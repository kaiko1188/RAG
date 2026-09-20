# -*- coding: utf-8 -*-
"""
ingest.py

data/ 配下のPDFを読み込み、
チャンク化 → メタデータ付与 → Embedding → Chroma保存
を行う。

使い方:
    python ingest.py

.env:
    EMBEDDING_BACKEND=local
    CHROMA_DIR=./chroma_db
    CHROMA_COLLECTION=nm_series
    DATA_DIR=./data
"""

from __future__ import annotations

import os
import shutil

import chromadb
from dotenv import load_dotenv

from backends import get_embeddings
from chunker import Chunk, build_chunks_for_all_documents


load_dotenv()


CHROMA_DIR = os.getenv(
    "CHROMA_DIR",
    "./chroma_db",
)

CHROMA_COLLECTION = os.getenv(
    "CHROMA_COLLECTION",
    "nm_series",
)

DATA_DIR = os.getenv(
    "DATA_DIR",
    "./data",
)


def _sanitize_metadata(meta: dict) -> dict:
    """
    Chromaのmetadataは
    str / int / float / bool
    を基本とするため、listなどを文字列化する。
    """

    out = {}

    for key, value in meta.items():

        if isinstance(value, list):
            out[key] = ",".join(
                str(x) for x in value
            )

        elif value is None:
            continue

        else:
            out[key] = value

    return out


def ingest(reset: bool = True) -> int:

    # -----------------------------------------------------------------------
    # 1. PDF → チャンク
    # -----------------------------------------------------------------------

    print(
        f"[ingest] チャンク化を開始します "
        f"(data_dir={DATA_DIR}) ..."
    )

    chunks: list[Chunk] = (
        build_chunks_for_all_documents(DATA_DIR)
    )

    print(
        f"[ingest] {len(chunks)} 件のチャンクを生成しました。"
    )

    if not chunks:
        raise RuntimeError(
            "チャンクが0件です。"
            "dataフォルダとPDFファイルを確認してください。"
        )


    # -----------------------------------------------------------------------
    # 2. 既存Chromaを削除
    # -----------------------------------------------------------------------

    if reset and os.path.exists(CHROMA_DIR):

        print(
            f"[ingest] 既存のChroma DBを削除します: "
            f"{CHROMA_DIR}"
        )

        shutil.rmtree(CHROMA_DIR)


    # -----------------------------------------------------------------------
    # 3. Chroma初期化
    # -----------------------------------------------------------------------

    client = chromadb.PersistentClient(
        path=CHROMA_DIR
    )

    try:
        client.delete_collection(
            CHROMA_COLLECTION
        )
    except Exception:
        pass

    collection = client.create_collection(
        CHROMA_COLLECTION,
        metadata={
            "hnsw:space": "cosine"
        },
    )


    # -----------------------------------------------------------------------
    # 4. Embeddingモデル読み込み
    # -----------------------------------------------------------------------

    embeddings = get_embeddings()

    texts = [
        chunk.text
        for chunk in chunks
    ]


    # -----------------------------------------------------------------------
    # 5. Embedding
    # -----------------------------------------------------------------------

    print(
        "[ingest] Embeddingを計算しています ..."
    )

    vectors = embeddings.embed_documents(
        texts
    )

    if len(vectors) != len(texts):
        raise RuntimeError(
            "Embeddingの件数とチャンク数が一致しません。"
        )


    # -----------------------------------------------------------------------
    # 6. Metadata
    # -----------------------------------------------------------------------

    ids = [
        f"chunk_{i:04d}"
        for i in range(len(chunks))
    ]

    metadatas = [
        _sanitize_metadata(chunk.metadata)
        for chunk in chunks
    ]


    # -----------------------------------------------------------------------
    # 7. Chroma保存
    # -----------------------------------------------------------------------

    collection.add(
        ids=ids,
        embeddings=vectors,
        documents=texts,
        metadatas=metadatas,
    )


    # -----------------------------------------------------------------------
    # 完了
    # -----------------------------------------------------------------------

    print(
        f"[ingest] Chromaへ "
        f"{len(chunks)} 件を保存しました。"
    )

    print(
        f"[ingest] DB: {CHROMA_DIR}"
    )

    print(
        f"[ingest] Collection: {CHROMA_COLLECTION}"
    )

    print(
        "[ingest] Embedding方式: "
        f"{os.getenv('EMBEDDING_BACKEND', 'local')}"
    )

    return len(chunks)


if __name__ == "__main__":
    ingest()