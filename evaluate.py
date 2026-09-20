# -*- coding: utf-8 -*-
"""
evaluate.py
設計書(RAG技術課題の実装手順)にある評価用質問10問を実行し、
「検索精度(狙った資料・ページ・タグを引けているか)」と「回答内容」を
まとめてMarkdownレポートとして出力する。

使い方:
    python evaluate.py

出力:
    eval_report.md
"""
from __future__ import annotations

import chromadb

from backends import get_llm
from rag import CHROMA_COLLECTION, CHROMA_DIR, _load_embeddings, answer

# 各質問について、検索で拾えていて欲しい正解シグナル(document_type / 主要メタデータ)を
# 事前に資料を精読した上で定義しておく(検索精度の自動チェック用)。
# expect_unanswerable=True の質問は「資料からは判断できない」という回答が期待値。
EVAL_QUESTIONS = [
    {
        "id": "Q1",
        "question": "E-204とは何か？",
        "expect_doc_types": {"maintenance_guide"},
        "expect_any_metadata": [{"error_code": "E-204"}],
    },
    {
        "id": "Q2",
        "question": "NM-100SのE-204の基本的な確認項目は？",
        "expect_doc_types": {"maintenance_guide"},
        "expect_any_metadata": [{"error_code": "E-204"}],
    },
    {
        "id": "Q3",
        "question": "R-104の機種・ロット・FWは？",
        "expect_doc_types": {"asset_ledger"},
        "expect_any_metadata": [{"machine_id": "R-104"}],
    },
    {
        "id": "Q4",
        "question": "R-104はSB-2026-014の対象か？",
        "expect_doc_types": {"service_bulletin", "asset_ledger"},
        "expect_any_metadata": [{"bulletin_id": "SB-2026-014"}, {"machine_id": "R-104"}],
    },
    {
        "id": "Q5",
        "question": "R-104でE-204が再発した場合、最初に何をするべきか？",
        "expect_doc_types": {"service_bulletin"},
        "expect_any_metadata": [{"bulletin_id": "SB-2026-014"}],
    },
    {
        "id": "Q6",
        "question": "R-104にDRV-42Aを取り付けてよいか？",
        "expect_doc_types": {"service_bulletin", "maintenance_guide"},
        "expect_any_metadata": [{"part_number": "DRV-42A"}],
    },
    {
        "id": "Q7",
        "question": "NM-100Sの適合部品は何か？",
        "expect_doc_types": {"maintenance_guide"},
        "expect_any_metadata": [{"model": "NM-100S"}],
    },
    {
        "id": "Q8",
        "question": "CASE-017と同じ対応をR-104に行ってよいか？",
        "expect_doc_types": {"case_history", "service_bulletin"},
        "expect_any_metadata": [{"case_id": "CASE-017"}],
    },
    {
        "id": "Q9",
        "question": "NM-100Sの基板交換後の無負荷電流基準は？",
        "expect_doc_types": {"maintenance_guide"},
        "expect_any_metadata": [{"model": "NM-100S"}],
    },
    {
        "id": "Q10",
        "question": "R-104のバッテリー交換履歴は？",
        "expect_doc_types": set(),
        "expect_any_metadata": [],
        "expect_unanswerable": True,
    },
]


def check_metadata_match(chunks, expect_any_metadata) -> bool:
    if not expect_any_metadata:
        return True
    for cond in expect_any_metadata:
        for c in chunks:
            ok = True
            for k, v in cond.items():
                meta_val = c.metadata.get(k, "")
                meta_plural = str(c.metadata.get(f"{k}s", ""))
                if v != meta_val and v not in meta_plural.split(","):
                    ok = False
                    break
            if ok:
                return True
    return False


def run():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection(CHROMA_COLLECTION)
    embeddings = _load_embeddings()
    llm = get_llm()

    report_lines = ["# RAG評価レポート", ""]
    n_retrieval_ok = 0

    for item in EVAL_QUESTIONS:
        text, chunks = answer(item["question"], collection=collection, embeddings=embeddings, llm=llm)

        retrieved_doc_types = {c.metadata.get("document_type") for c in chunks}
        doc_type_ok = (
            not item["expect_doc_types"] or bool(retrieved_doc_types & item["expect_doc_types"])
        )
        meta_ok = check_metadata_match(chunks, item.get("expect_any_metadata", []))
        retrieval_ok = doc_type_ok and meta_ok
        if item.get("expect_unanswerable"):
            # Q10はそもそも該当情報が存在しないため、検索結果の妥当性ではなく
            # 回答が「判断できない」という趣旨になっているかを目視確認する
            retrieval_ok = True
        if retrieval_ok:
            n_retrieval_ok += 1

        report_lines.append(f"## {item['id']}: {item['question']}")
        report_lines.append("")
        report_lines.append(f"- 検索精度チェック: {'OK' if retrieval_ok else 'NG'}")
        report_lines.append(
            f"- 取得チャンクのdocument_type: {sorted(retrieved_doc_types)}"
        )
        report_lines.append("- 取得チャンク出典:")
        for c in chunks:
            m = c.metadata
            report_lines.append(
                f"  - {m['document']} p.{m['page']} "
                f"(document_type={m.get('document_type')}, source={c.source}, score={c.score:.3f})"
            )
        report_lines.append("")
        report_lines.append("**回答:**")
        report_lines.append("")
        report_lines.append(text)
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")

    summary = (
        f"検索精度チェック OK: {n_retrieval_ok} / {len(EVAL_QUESTIONS)} 問"
    )
    report_lines.insert(1, summary)
    report_lines.insert(2, "")

    with open("eval_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(summary)
    print("詳細は eval_report.md を参照してください。")


if __name__ == "__main__":
    run()
