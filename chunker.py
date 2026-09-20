# -*- coding: utf-8 -*-
"""
chunker.py
PDFを「検索単位として意味が成立する範囲」でチャンク化するモジュール。

設計方針:
  1. 表はPyMuPDFのfind_tables()で検出し、1表=1チャンクとして丸ごと保持する。
     - find_tables()は罫線のない表で右端カラムを取りこぼすことがあるため
       (実データで確認済み: 「交換部品と互換条件」表の「状態」列が欠落する)、
       検出済み表の右側に本来あるはずの単語が残っていないかを走査し、
       列を自動補修する(repair_table)。
  2. 表以外の本文は、見出し行(「1.1 情報の読み方」「3.1 E-204 ...」
     「サービス速報 SB-2026-014」等の番号付き見出し/固有の見出しパターン)で
     セクションに分割し、1セクション=1チャンクを基本とする。
     短すぎるセクション(見出しのみ等)は前後のチャンクと統合する。
  3. 各チャンクから正規表現でドメイン固有のメタデータ
     (機種・機体ID・ロット・FW・エラーコード・部品番号・速報番号)を抽出する。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF


# ---------------------------------------------------------------------------
# データ構造
# ---------------------------------------------------------------------------

@dataclass
class Chunk:
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# メタデータ抽出(正規表現)
# ---------------------------------------------------------------------------

# 機種: NM-100S は NM-100 の部分文字列を含むため、長いパターンを先に試す
_MODEL_PATTERNS = ["NM-100S", "NM-200", "NM-100"]

# 機体ID: 資産管理でつかわれる接頭辞(R/H/M/P) + ハイフン + 3桁。
# エラーコード(E-xxx / W-xxx)と衝突しないよう接頭辞を限定する。
_MACHINE_ID_RE = re.compile(r"\b[RHMP]-\d{3}\b")

# エラー/警告コード: E-xxx, W-xxx
_ERROR_CODE_RE = re.compile(r"\b[EW]-\d{3}\b")

# ロット: L2301 のような英数字、範囲表記 L2406〜L2410 にも対応
_LOT_RE = re.compile(r"\bL\d{4}(?:[〜~]L?\d{4})?(?:以降|以前)?\b")
# H2501 のような重量機ロット表記もある
_LOT_RE2 = re.compile(r"\bH\d{4}(?:以降|以前)?\b")

# FWバージョン: 3.1.4 / 3.2.0以降 / 3.1.x以前 / 3.1.0〜3.1.6
_FW_RE = re.compile(r"\d\.\d(?:\.\d|\.x)(?:[〜~]\d\.\d\.\d)?(?:以降|以前)?")

# 部品番号: DRV-42A, LDS-10Y, ADP-L10, JIG-L2 等
_PART_RE = re.compile(r"\b(?:DRV|LDS|ADP|JIG)-[A-Z0-9]+\b")

# サービス速報番号: SB-2026-014
_BULLETIN_RE = re.compile(r"\bSB-\d{4}-\d{3}\b")

# 事例番号: CASE-017
_CASE_RE = re.compile(r"\bCASE-\d{3}\b")


def _first(pattern_list_or_re, text: str):
    if isinstance(pattern_list_or_re, list):
        for p in pattern_list_or_re:
            if p in text:
                return p
        return None
    m = pattern_list_or_re.search(text)
    return m.group(0) if m else None


def _all(pattern: re.Pattern, text: str) -> list[str]:
    seen = []
    for m in pattern.findall(text):
        if m not in seen:
            seen.append(m)
    return seen


def extract_domain_metadata(text: str) -> dict[str, Any]:
    """チャンク本文からドメイン固有メタデータを抽出する。"""
    models = [m for m in _MODEL_PATTERNS if m in text]
    # NM-100S を含む場合、単純一致の "NM-100" は誤検出なので除外する
    if "NM-100S" in models and "NM-100" in models:
        # "NM-100" 単独出現がNM-100Sの一部でない箇所にも実在するかは判別しないため
        # 両方残す(検索フィルタでは前方一致的に扱う想定)。
        pass

    meta: dict[str, Any] = {}
    if models:
        meta["model"] = models[0]
        meta["models"] = models
    machine_ids = _all(_MACHINE_ID_RE, text)
    if machine_ids:
        meta["machine_id"] = machine_ids[0]
        meta["machine_ids"] = machine_ids
    error_codes = _all(_ERROR_CODE_RE, text)
    if error_codes:
        meta["error_code"] = error_codes[0]
        meta["error_codes"] = error_codes
    lots = _all(_LOT_RE, text) + _all(_LOT_RE2, text)
    if lots:
        meta["lot"] = lots[0]
        meta["lots"] = lots
    fws = _all(_FW_RE, text)
    if fws:
        meta["firmware"] = fws[0]
        meta["firmwares"] = fws
    parts = _all(_PART_RE, text)
    if parts:
        meta["part_number"] = parts[0]
        meta["part_numbers"] = parts
    bulletins = _all(_BULLETIN_RE, text)
    if bulletins:
        meta["bulletin_id"] = bulletins[0]
        meta["bulletin_ids"] = bulletins
    cases = _all(_CASE_RE, text)
    if cases:
        meta["case_id"] = cases[0]
        meta["case_ids"] = cases
    return meta


# ---------------------------------------------------------------------------
# 表の抽出・補修
# ---------------------------------------------------------------------------

def repair_table(page: "fitz.Page", table) -> list[list[str]]:
    """find_tables()が右端の列を検出し損ねた場合に、単語座標から列を復元する。

    PyMuPDFの罫線なし表検出は、右端カラムの区切りを見つけられず
    そのカラムを丸ごと欠落させることがある(実データで確認済み)。
    表の右端より右にある単語を行の高さ範囲(y-band)ごとに走査し、
    見つかった分だけ新しい列として追加する。
    """
    rows = [[(c if c is not None else "") for c in r] for r in table.extract()]
    row_count = table.row_count
    # cellsは列優先(column-major)で並んでいるため、先頭row_count個が
    # 第1列の各行のセル座標 = 各行のy範囲として利用できる
    col0_cells = table.cells[0:row_count]
    row_bands = [(c[1], c[3]) for c in col0_cells]

    words = page.get_text("words")  # (x0, y0, x1, y1, text, block, line, word)
    cur_x1 = table.bbox[2]

    for _ in range(3):  # 最大3列まで復元を試みる(通常は1列で十分)
        col_vals = []
        any_found = False
        for (y0, y1) in row_bands:
            seg = [
                w for w in words
                if w[0] >= cur_x1 - 1 and w[1] >= y0 - 1 and w[3] <= y1 + 1
            ]
            seg.sort(key=lambda w: w[0])
            text = "".join(w[4] for w in seg)
            col_vals.append(text)
            if text:
                any_found = True
        if not any_found:
            break
        for i, v in enumerate(col_vals):
            if i < len(rows):
                rows[i].append(v)
        max_x1 = cur_x1
        for (y0, y1) in row_bands:
            for w in words:
                if w[0] >= cur_x1 - 1 and w[1] >= y0 - 1 and w[3] <= y1 + 1:
                    max_x1 = max(max_x1, w[2])
        if max_x1 <= cur_x1:
            break
        cur_x1 = max_x1
    return rows


def table_to_text(rows: list[list[str]], caption: str = "") -> str:
    """表をMarkdown風のテキストに変換する(1表=1チャンクとして保持するため)。"""
    if not rows:
        return ""
    header, *body = rows
    lines = []
    if caption:
        lines.append(f"【表】{caption}")
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "|".join(["---"] * len(header)) + "|")
    for r in body:
        r = r + [""] * (len(header) - len(r))  # 列数を揃える
        lines.append("| " + " | ".join(r[: len(header)]) + " |")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 見出し検出(本文のセクション分割用)
# ---------------------------------------------------------------------------

# 例: "1.1 情報の優先順位" "3.1 E-204 左駆動系過負荷" "5.2 交換手順 1〜5"
_HEADING_NUM_RE = re.compile(r"^\d+(?:\.\d+)*\s+\S.{0,40}$")
# 例: "サービス速報 SB-2026-014"
_HEADING_BULLETIN_RE = re.compile(r"^サービス速報\s*SB-\d{4}-\d{3}")
# 例: "1. 導入機器台帳" のような大見出し
_HEADING_MAJOR_RE = re.compile(r"^\d+\．\S")


def is_heading(line: str) -> bool:
    line = line.strip()
    if not line or len(line) > 50:
        return False
    if _HEADING_BULLETIN_RE.match(line):
        return True
    if _HEADING_MAJOR_RE.match(line):
        return True
    if _HEADING_NUM_RE.match(line):
        return True
    return False


# ---------------------------------------------------------------------------
# メイン処理: PDF -> チャンクのリスト
# ---------------------------------------------------------------------------

def _table_region_mask(page_height: float, tables) -> list[tuple[float, float]]:
    return [(t.bbox[1], t.bbox[3]) for t in tables]


def _line_in_tables(y0: float, y1: float, regions: list[tuple[float, float]]) -> bool:
    for (ry0, ry1) in regions:
        if y0 >= ry0 - 2 and y1 <= ry1 + 2:
            return True
    return False


def process_pdf(pdf_path: str, document_name: str, document_type_default: str) -> list[Chunk]:
    """PDFを読み込み、表チャンク + 本文セクションチャンクのリストを返す。"""
    doc = fitz.open(pdf_path)
    chunks: list[Chunk] = []

    for page_index in range(len(doc)):
        page = doc[page_index]
        page_no = page_index + 1

        # ページ内の見出し行とそのy座標を集めておく(表がどの見出しの配下にあるか判定するため)
        heading_positions: list[tuple[float, str]] = []
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                line_text = "".join(span["text"] for span in line["spans"]).strip()
                if line_text and is_heading(line_text):
                    y0 = line["bbox"][1]
                    heading_positions.append((y0, line_text))
        heading_positions.sort(key=lambda x: x[0])

        def heading_before(y: float) -> str:
            current = ""
            for hy, htext in heading_positions:
                if hy <= y + 2:
                    current = htext
                else:
                    break
            return current

        # --- 1. 表を検出して1表=1チャンクにする ---
        found = page.find_tables()
        table_regions = _table_region_mask(page.rect.height, found.tables)
        for t in found.tables:
            rows = repair_table(page, t)
            if not rows or len(rows) < 2:
                continue
            table_text = table_to_text(rows)
            nearest_heading = heading_before(t.bbox[1])
            meta = {
                "document": document_name,
                "page": page_no,
                "section": nearest_heading,
                "document_type": document_type_default,
                "content_kind": "table",
            }
            meta.update(extract_domain_metadata(table_text))
            chunks.append(Chunk(text=table_text, metadata=meta))

        # --- 2. 表以外の本文をセクション単位に分割 ---
        raw = page.get_text("text")
        lines = [l for l in raw.split("\n")]

        # 表領域に含まれる行を除外するため、単語座標ベースで行ごとのy範囲を推定する
        words = page.get_text("words")
        # 簡易的に: 表本文に含まれるテキストトークンを除去する
        table_token_set = set()
        for t in found.tables:
            for row in repair_table(page, t):
                for cell in row:
                    cell = cell.strip()
                    if not cell:
                        continue
                    # セル全体を1行として除外(PDF抽出では1セル=1行になることが多い)
                    table_token_set.add(cell)
                    # セル内が改行を含む場合はその各行も除外
                    for sub in cell.split("\n"):
                        sub = sub.strip()
                        if sub:
                            table_token_set.add(sub)
                    # 念のため空白区切りトークンも除外対象に加える
                    for tok in re.split(r"\s+", cell):
                        if tok:
                            table_token_set.add(tok)

        body_lines = []
        for l in lines:
            stripped = l.strip()
            if not stripped:
                continue
            if stripped in table_token_set:
                continue
            body_lines.append(stripped)

        # ヘッダ/フッタ(資料名・発行日・ページ番号の定型行)を除去
        body_lines = [
            l for l in body_lines
            if not re.match(r"^\d+\s*/\s*\d+$", l)
            and "ネクスモーション株式会社" not in l
            and not l.startswith("NXM-")
            and l != document_name  # 各ページ冒頭に繰り返される資料名(ランニングヘッダ)を除去
        ]

        # セクション分割: 見出し行で区切る
        sections: list[list[str]] = []
        current: list[str] = []
        for l in body_lines:
            if is_heading(l) and current:
                sections.append(current)
                current = [l]
            else:
                current.append(l)
        if current:
            sections.append(current)

        # 短すぎる断片(見出しのみ等)は次のセクションに統合
        merged_sections: list[list[str]] = []
        buffer: list[str] = []
        for sec in sections:
            buffer.extend(sec)
            joined = "\n".join(buffer)
            if len(joined) >= 40:
                merged_sections.append(buffer)
                buffer = []
        if buffer:
            if merged_sections:
                merged_sections[-1].extend(buffer)
            else:
                merged_sections.append(buffer)

        for sec_lines in merged_sections:
            text = "\n".join(sec_lines).strip()
            if not text:
                continue
            heading = sec_lines[0] if is_heading(sec_lines[0]) else ""
            meta = {
                "document": document_name,
                "page": page_no,
                "section": heading,
                "document_type": document_type_default,
                "content_kind": "text",
            }
            meta.update(extract_domain_metadata(text))
            chunks.append(Chunk(text=text, metadata=meta))

    return chunks


# ---------------------------------------------------------------------------
# 資料タイプ別の後処理: 運用記録PDFは複数の性質が混ざるため再分類する
# ---------------------------------------------------------------------------

def refine_document_type(chunk: Chunk) -> None:
    """運用記録・サービス速報PDFは、本文中身に応じてdocument_typeを再分類する。

    - 「サービス速報」を含む/bulletin_idを持つ -> service_bulletin (優先度: 最高)
    - 「導入機器台帳」を含む/machine_idを複数持つ表 -> asset_ledger
    - 「CASE-0」を含む -> case_history (参考情報・優先度: 低)
    """
    text = chunk.text
    meta = chunk.metadata
    if meta.get("document_type") != "ops_record":
        return

    heading = meta.get("section", "") or ""
    is_bulletin_heading = bool(_HEADING_BULLETIN_RE.match(heading)) or "サービス速報 SB-" in text

    if "bulletin_id" in meta or is_bulletin_heading:
        meta["document_type"] = "service_bulletin"
        meta["priority"] = 3
    elif "case_id" in meta or re.search(r"CASE-\d{3}", text) or "類似症状" in text:
        meta["document_type"] = "case_history"
        meta["priority"] = 1
    elif "導入機器台帳" in text or "機体ID" in text or meta.get("content_kind") == "table":
        meta["document_type"] = "asset_ledger"
        meta["priority"] = 2
    else:
        meta["document_type"] = "ops_record_other"
        meta["priority"] = 1


PRIORITY_BY_DOC_TYPE = {
    "service_bulletin": 3,   # 最優先: 対象条件に一致すれば一般手順より優先
    "maintenance_guide": 2,  # 一般手順
    "asset_ledger": 2,       # 事実情報(機種・ロット・FW)
    "case_history": 1,       # 参考情報のみ・正式手順を置き換えない
    "ops_record_other": 1,
}


def build_chunks_for_all_documents(data_dir: str) -> list[Chunk]:
    data_dir_path = Path(data_dir)
    all_chunks: list[Chunk] = []

    maint_pdf = data_dir_path / "01_NMシリーズ保守技術ガイド.pdf"
    ops_pdf = data_dir_path / "02_NMシリーズ運用記録サービス速報.pdf"

    maint_chunks = process_pdf(
        str(maint_pdf), document_name="NMシリーズ 保守技術ガイド",
        document_type_default="maintenance_guide",
    )
    for c in maint_chunks:
        c.metadata["priority"] = PRIORITY_BY_DOC_TYPE["maintenance_guide"]
    all_chunks.extend(maint_chunks)

    ops_chunks = process_pdf(
        str(ops_pdf), document_name="NMシリーズ 運用記録・サービス速報",
        document_type_default="ops_record",
    )
    for c in ops_chunks:
        refine_document_type(c)
        c.metadata.setdefault(
            "priority", PRIORITY_BY_DOC_TYPE.get(c.metadata["document_type"], 1)
        )
    all_chunks.extend(ops_chunks)

    return all_chunks


if __name__ == "__main__":
    chunks = build_chunks_for_all_documents("data")
    print(f"total chunks: {len(chunks)}")
    for c in chunks:
        print("=" * 80)
        print(c.metadata)
        print(c.text[:200])
