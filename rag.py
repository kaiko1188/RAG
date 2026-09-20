
Rag · PY
# -*- coding: utf-8 -*-
"""
rag.py
 
質問を受け取り、
 
    質問
      ↓
    Embedding
      ↓
    Chroma検索
      ↓
    メタデータによる補完
      ↓
    資料タイプの優先順位付け
      ↓
    Ollama等のLLM
      ↓
    根拠付き回答
 
を行う。
 
使い方:
 
    python rag.py
 
または
 
    python rag.py "R-104でE-204が再発した場合どうすればいい？"
"""
 
from __future__ import annotations
 
import os
import sys
from dataclasses import dataclass
 
import chromadb
from dotenv import load_dotenv
 
from backends import get_embeddings, get_llm
from chunker import extract_domain_metadata
 
 
load_dotenv()
 
 
# ---------------------------------------------------------------------------
# 設定
# ---------------------------------------------------------------------------
 
CHROMA_DIR = os.getenv(
    "CHROMA_DIR",
    "./chroma_db",
)
 
CHROMA_COLLECTION = os.getenv(
    "CHROMA_COLLECTION",
    "nm_series",
)
 
TOP_K = int(
    os.getenv(
        "TOP_K",
        "6",
    )
)
 
 
# ---------------------------------------------------------------------------
# 資料タイプの優先順位
# ---------------------------------------------------------------------------
 
DOC_TYPE_PRIORITY = {
 
    # 最新の正式な指示を最優先
    "service_bulletin": 3,
 
    # 一般的な保守手順
    "maintenance_guide": 2,
 
    # 機体の事実情報
    "asset_ledger": 2,
 
    # 過去事例は参考情報
    "case_history": 1,
 
    "ops_record_other": 1,
}
 
 
# ---------------------------------------------------------------------------
# LLM System Prompt
# ---------------------------------------------------------------------------
 
SYSTEM_PROMPT = """
あなたはNMシリーズ自律走行ロボットの
保守サポートを行うアシスタントです。
 
以下のルールを必ず守ってください。
 
1.
回答は「参考資料」として提示されたチャンクの内容だけを
根拠にしてください。
資料に存在しない情報を推測・創作しないでください。
 
2.
複数の資料にまたがる情報については、
必要に応じて複数の資料を組み合わせて回答してください。
 
3.
同じ事象について複数の資料に異なる記載がある場合は、
以下の優先順位に従ってください。
 
対象条件に一致するサービス速報
(service_bulletin)
>
保守技術ガイド
(maintenance_guide)
>
障害事例
(case_history)
 
障害事例は参考情報であり、
正式な手順を置き換えるものではありません。
 
4.
サービス速報の対象条件が質問対象に一致する場合は、
一般的な保守手順や過去事例よりも
サービス速報を優先してください。
 
5.
参考資料から質問に対する情報を判断できない場合は、
必ず
「提供された資料からは判断できません」
という趣旨で回答してください。
 
推測で回答しないでください。
 
6.
回答は日本語で簡潔かつ具体的にしてください。
 
7.
回答本文の中に
「出典：」「p.◯に記載」のような
出典・ページ番号の表記を書かないでください。
 
出典は回答本文とは別に、
システム側が検索結果のメタデータから
自動的に表示します。
あなたが自分で出典を作文すると、
実際には存在しないページ番号を
書いてしまう可能性があるため禁止します。
 
8.
参考資料に書かれている内容を超えて
一般知識から補足しないでください。
"""
 
 
# ---------------------------------------------------------------------------
# User Prompt
# ---------------------------------------------------------------------------
 
USER_PROMPT_TEMPLATE = """
# 参考資料
 
{context}
 
# 質問
 
{question}
 
# 回答指示
 
上記の参考資料だけを根拠に回答してください。
 
資料から判断できない場合は、
「提供された資料からは判断できません」
と回答してください。
 
回答本文には「出典：」やページ番号などの
出典表記を含めないでください。
出典はシステム側が別途表示します。
"""
 
 
# ---------------------------------------------------------------------------
# Retrieved Chunk
# ---------------------------------------------------------------------------
 
@dataclass
class RetrievedChunk:
 
    text: str
    metadata: dict
    score: float
    source: str
 
 
# ---------------------------------------------------------------------------
# Priority
# ---------------------------------------------------------------------------
 
def _priority_of(meta: dict) -> int:
 
    return DOC_TYPE_PRIORITY.get(
        meta.get(
            "document_type",
            "",
        ),
        0,
    )
 
 
# ---------------------------------------------------------------------------
# Metadata Filter
# ---------------------------------------------------------------------------
 
def _build_filter_from_query(
    query: str,
) -> dict | None:
    """
    質問文から機体ID、エラーコード、
    速報番号などを抽出してChroma検索用の
    filter条件を作成する。
    """
 
    q_meta = extract_domain_metadata(
        query
    )
 
    conditions = []
 
    for key in (
        "machine_id",
        "error_code",
        "bulletin_id",
        "model",
        "part_number",
        "case_id",
    ):
 
        value = q_meta.get(key)
 
        if not value:
            continue
 
        # 単一値
        conditions.append(
            {
                key: {
                    "$eq": value
                }
            }
        )
 
        # 複数値をカンマ区切りで保存しているmetadata
        conditions.append(
            {
                f"{key}s": {
                    "$eq": value
                }
            }
        )
 
    if not conditions:
        return None
 
    if len(conditions) == 1:
        return conditions[0]
 
    return {
        "$or": conditions
    }
 
 
# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------
 
def retrieve(
    collection,
    embeddings,
    question: str,
    top_k: int = TOP_K,
) -> list[RetrievedChunk]:
 
    # -----------------------------------------------------------------------
    # 1. Vector Search
    # -----------------------------------------------------------------------
 
    query_vec = embeddings.embed_query(
        question
    )
 
    vector_res = collection.query(
        query_embeddings=[query_vec],
        n_results=top_k,
    )
 
    results: dict[str, RetrievedChunk] = {}
 
    ids = vector_res.get(
        "ids",
        [[]],
    )[0]
 
    docs = vector_res.get(
        "documents",
        [[]],
    )[0]
 
    metas = vector_res.get(
        "metadatas",
        [[]],
    )[0]
 
    dists = vector_res.get(
        "distances",
        [[]],
    )[0]
 
 
    # -----------------------------------------------------------------------
    # Vector結果を登録
    # -----------------------------------------------------------------------
 
    for (
        _id,
        text,
        meta,
        dist,
    ) in zip(
        ids,
        docs,
        metas,
        dists,
    ):
 
        # Chroma cosine distance
        # 小さいほど類似
        score = 1.0 - float(dist)
 
        results[_id] = RetrievedChunk(
            text=text,
            metadata=meta,
            score=score,
            source="vector",
        )
 
 
    # -----------------------------------------------------------------------
    # 2. Metadata完全一致による補完検索
    # -----------------------------------------------------------------------
 
    q_meta = extract_domain_metadata(
        question
    )
 
    if q_meta:
 
        all_data = collection.get()
 
        all_ids = all_data.get(
            "ids",
            [],
        )
 
        all_docs = all_data.get(
            "documents",
            [],
        )
 
        all_metas = all_data.get(
            "metadatas",
            [],
        )
 
        for (
            _id,
            text,
            meta,
        ) in zip(
            all_ids,
            all_docs,
            all_metas,
        ):
 
            if _id in results:
                continue
 
            matched = False
 
            for key in (
                "machine_id",
                "error_code",
                "bulletin_id",
                "model",
                "part_number",
                "case_id",
            ):
 
                query_value = q_meta.get(
                    key
                )
 
                if not query_value:
                    continue
 
                single_value = meta.get(
                    key,
                    "",
                )
 
                plural_value = str(
                    meta.get(
                        f"{key}s",
                        "",
                    )
                )
 
                if (
                    query_value == single_value
                    or query_value in plural_value.split(",")
                ):
                    matched = True
                    break
 
            if matched:
 
                results[_id] = RetrievedChunk(
                    text=text,
                    metadata=meta,
                    score=0.5,
                    source="metadata_filter",
                )
 
 
    # -----------------------------------------------------------------------
    # 3. 資料タイプ優先順位 + 類似度
    # -----------------------------------------------------------------------
 
    ranked = sorted(
        results.values(),
        key=lambda r: (
            _priority_of(r.metadata),
            r.score,
        ),
        reverse=True,
    )
 
 
    # top_k以上の候補をLLMへ渡す
    return ranked[
        : max(
            top_k,
            8,
        )
    ]
 
 
# ---------------------------------------------------------------------------
# Context
# ---------------------------------------------------------------------------
 
def format_context(
    chunks: list[RetrievedChunk],
) -> str:
 
    blocks = []
 
    for chunk in chunks:
 
        metadata = chunk.metadata
 
        document = metadata.get(
            "document",
            "不明",
        )
 
        page = metadata.get(
            "page",
            "不明",
        )
 
        document_type = metadata.get(
            "document_type",
            "",
        )
 
        blocks.append(
            f"[出典候補: "
            f"{document} "
            f"p.{page} "
            f"/ document_type={document_type}]\n"
            f"{chunk.text}"
        )
 
    return "\n\n---\n\n".join(
        blocks
    )
 
 
# ---------------------------------------------------------------------------
# Citation（出典表示）
# ---------------------------------------------------------------------------
#
# 出典はLLMに書かせず、検索結果(chunks)のmetadataから
# プログラム側で機械的に生成する。
#
# 理由:
#   - LLMに出典を書かせると、書く場合と書かない場合が混在する
#     （小型モデルほど指示に従いきれない）
#   - LLMが実在しないページ番号を作文してしまうリスクがある
#
# そのため「回答できた/できなかった」に関わらず、
# 検索してLLMに渡したchunk一覧から必ず同じロジックで
# 出典ブロックを組み立てる。
 
UNANSWERABLE_PHRASES = (
    "判断できません",
    "判断できない",
)
 
 
def _is_unanswerable(text: str) -> bool:
 
    return any(
        phrase in text
        for phrase in UNANSWERABLE_PHRASES
    )
 
 
def _strip_llm_written_citations(text: str) -> str:
    """
    指示を守らずLLMが自分で末尾に書いてしまった
    「出典：...」「【出典】...」のような行を取り除く。
 
    あくまで末尾の行を対象にした簡易対策であり、
    本文中に埋め込まれた「p.4に記載されています」等の
    自然文までは除去しない（過剰な本文改変を避けるため）。
    """
 
    lines = text.rstrip().split("\n")
 
    citation_prefixes = (
        "出典",
        "【出典】",
        "【根拠】",
        "【確認した資料】",
    )
 
    while lines and lines[-1].strip().startswith(citation_prefixes):
        lines.pop()
 
    while lines and not lines[-1].strip():
        lines.pop()
 
    return "\n".join(lines)
 
 
def build_citation_block(
    chunks: list[RetrievedChunk],
    answer_text: str,
) -> str:
    """
    検索結果chunksのmetadataから、出典ブロックを組み立てる。
 
    「判断できません」という回答の場合は、
    根拠ではなく「確認した資料」として提示する
    （＝正式な根拠ではないが、何を見た上で
      判断できないと結論付けたかを分かるようにする）。
    """
 
    if not chunks:
        return ""
 
    seen: set[tuple[str, str]] = set()
    entries: list[str] = []
 
    for chunk in chunks:
 
        metadata = chunk.metadata
 
        document = metadata.get("document", "不明")
        page = metadata.get("page", "不明")
 
        key = (document, str(page))
 
        if key in seen:
            continue
 
        seen.add(key)
 
        entries.append(f"・{document} p.{page}")
 
    if not entries:
        return ""
 
    label = (
        "確認した資料"
        if _is_unanswerable(answer_text)
        else "出典"
    )
 
    return (
        f"\n\n【{label}】\n"
        + "\n".join(entries)
    )
 
 
# ---------------------------------------------------------------------------
# Embedding
# ---------------------------------------------------------------------------
 
def _load_embeddings():
    """
    Embeddingモデルを読み込む。
 
    以前のTF-IDF版ではpickleを読み込んでいたが、
    Sentence Transformersでは同じモデルを毎回ロードすれば
    ingest時と同じベクトル空間を使用できるため、
    pickle保存は不要。
    """
 
    return get_embeddings()
 
 
# ---------------------------------------------------------------------------
# Answer
# ---------------------------------------------------------------------------
 
def answer(
    question: str,
    collection=None,
    embeddings=None,
    llm=None,
    top_k: int = TOP_K,
):
 
    # -----------------------------------------------------------------------
    # Chroma
    # -----------------------------------------------------------------------
 
    client = chromadb.PersistentClient(
        path=CHROMA_DIR
    )
 
    collection = (
        collection
        or client.get_collection(
            CHROMA_COLLECTION
        )
    )
 
 
    # -----------------------------------------------------------------------
    # Backend
    # -----------------------------------------------------------------------
 
    embeddings = (
        embeddings
        or _load_embeddings()
    )
 
    llm = (
        llm
        or get_llm()
    )
 
 
    # -----------------------------------------------------------------------
    # Retrieval
    # -----------------------------------------------------------------------
 
    chunks = retrieve(
        collection,
        embeddings,
        question,
        top_k=top_k,
    )
 
 
    # -----------------------------------------------------------------------
    # 検索結果なし
    # -----------------------------------------------------------------------
 
    if not chunks:
 
        return (
            "提供された資料からは判断できません。"
            "（検索結果0件）",
            [],
        )
 
 
    # -----------------------------------------------------------------------
    # LLM
    # -----------------------------------------------------------------------
 
    context = format_context(
        chunks
    )
 
    prompt = USER_PROMPT_TEMPLATE.format(
        context=context,
        question=question,
    )
 
 
    from langchain_core.messages import (
        HumanMessage,
        SystemMessage,
    )
 
 
    response = llm.invoke(
        [
            SystemMessage(
                content=SYSTEM_PROMPT
            ),
            HumanMessage(
                content=prompt
            ),
        ]
    )
 
 
    # -----------------------------------------------------------------------
    # Response
    # -----------------------------------------------------------------------
 
    if hasattr(
        response,
        "content",
    ):
        text = response.content
    else:
        text = str(response)
 
 
    # -----------------------------------------------------------------------
    # 出典（毎回・同じロジックで付与する）
    # -----------------------------------------------------------------------
    #
    # LLMが指示を無視して末尾に自作の出典を書いてしまった場合に備えて
    # まず末尾の出典らしき行を取り除いてから、
    # 検索結果metadataベースの出典ブロックを必ず追加する。
    # これにより「出典が出るときと出ないとき」の差をなくす。
 
    text = _strip_llm_written_citations(text)
    text = text + build_citation_block(chunks, text)
 
 
    return text, chunks
 
 
# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
 
def main():
 
    if len(sys.argv) > 1:
 
        question = " ".join(
            sys.argv[1:]
        )
 
        text, chunks = answer(
            question
        )
 
        print()
        print(text)
 
        return
 
 
    print(
        "NMシリーズ保守RAG"
    )
 
    print(
        "終了するには exit と入力してください。"
    )
 
 
    while True:
 
        try:
 
            question = input(
                "\n質問> "
            ).strip()
 
        except (
            EOFError,
            KeyboardInterrupt,
        ):
 
            break
 
 
        if (
            not question
            or question.lower()
            in (
                "exit",
                "quit",
            )
        ):
 
            break
 
 
        try:
 
            text, chunks = answer(
                question
            )
 
            print()
            print(text)
 
        except Exception as e:
 
            print()
            print(
                "エラーが発生しました:"
            )
            print(e)
 
 
# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
 
if __name__ == "__main__":
    main()





























