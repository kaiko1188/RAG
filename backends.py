# -*- coding: utf-8 -*-
"""
backends.py

Embedding / LLM の呼び出しをバックエンドごとに切り替えるための薄いラッパー。

今回の課題では、OpenAI APIを使用せず、
ローカル環境だけでEmbeddingとLLMを動作させる。

.env:
    EMBEDDING_BACKEND=local
    LLM_BACKEND=local

ローカル:
    Embedding : Sentence Transformers
    LLM       : Ollama

OpenAIを使用する場合:
    EMBEDDING_BACKEND=openai
    LLM_BACKEND=openai
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# Backend設定
# ---------------------------------------------------------------------------

EMBEDDING_BACKEND = os.getenv(
    "EMBEDDING_BACKEND",
    "local",
).lower()

LLM_BACKEND = os.getenv(
    "LLM_BACKEND",
    "local",
).lower()


# ---------------------------------------------------------------------------
# OpenAI設定
# ---------------------------------------------------------------------------

OPENAI_EMBEDDING_MODEL = os.getenv(
    "OPENAI_EMBEDDING_MODEL",
    "text-embedding-3-small",
)

OPENAI_CHAT_MODEL = os.getenv(
    "OPENAI_CHAT_MODEL",
    "gpt-4o-mini",
)


# ---------------------------------------------------------------------------
# Local Embedding設定
# ---------------------------------------------------------------------------

# 日本語を含む多言語文章に対応したEmbeddingモデル
LOCAL_EMBEDDING_MODEL = os.getenv(
    "LOCAL_EMBEDDING_MODEL",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)

LOCAL_EMBEDDING_DEVICE = os.getenv(
    "LOCAL_EMBEDDING_DEVICE",
    "auto",
).lower()


# ---------------------------------------------------------------------------
# Ollama設定
# ---------------------------------------------------------------------------

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen3:8b",
)

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
)


# ===========================================================================
# Local Embedding
# ===========================================================================

class LocalSentenceTransformerEmbeddings:
    """
    Sentence Transformersを利用したローカルEmbedding。

    LangChainのEmbeddingsと同様に、
        embed_documents()
        embed_query()
    を提供する。

    Chromaに保存したEmbeddingと、質問時のEmbeddingで
    同じモデルを使用する。
    """

    def __init__(self, model_name: str | None = None):

        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as e:
            raise ImportError(
                "sentence-transformers がインストールされていません。\n"
                "以下を実行してください:\n"
                "pip install sentence-transformers"
            ) from e

        self.model_name = model_name or LOCAL_EMBEDDING_MODEL

        import torch

        if LOCAL_EMBEDDING_DEVICE == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            device = LOCAL_EMBEDDING_DEVICE

        print(
            f"[Embedding] Sentence Transformersを読み込みます: "
            f"{self.model_name} (device={device})"
        )

        self.model = SentenceTransformer(
            self.model_name,
            device=device,
        )

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        文書チャンクをEmbeddingする。
        """

        if not texts:
            return []

        vectors = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        return vectors.tolist()

    def embed_query(
        self,
        text: str,
    ) -> list[float]:
        """
        質問文をEmbeddingする。
        """

        if not text:
            return []

        vector = self.model.encode(
            [text],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )[0]

        return vector.tolist()


# ===========================================================================
# Embedding Factory
# ===========================================================================

def get_embeddings():
    """
    .envのEMBEDDING_BACKENDに応じてEmbeddingを返す。
    """

    if EMBEDDING_BACKEND == "local":

        return LocalSentenceTransformerEmbeddings()

    if EMBEDDING_BACKEND == "openai":

        try:
            from langchain_openai import OpenAIEmbeddings
        except ImportError as e:
            raise ImportError(
                "langchain-openai がインストールされていません。\n"
                "pip install langchain-openai"
            ) from e

        return OpenAIEmbeddings(
            model=OPENAI_EMBEDDING_MODEL,
        )

    raise ValueError(
        f"未対応のEMBEDDING_BACKENDです: {EMBEDDING_BACKEND}\n"
        "local または openai を指定してください。"
    )


# ===========================================================================
# LLM Factory
# ===========================================================================

def get_llm():
    """
    .envのLLM_BACKENDに応じてLLMを返す。

    local:
        Ollama

    openai:
        OpenAI Chat Model
    """

    if LLM_BACKEND == "local":

        try:
            from langchain_ollama import ChatOllama
        except ImportError as e:
            raise ImportError(
                "langchain-ollama がインストールされていません。\n"
                "pip install langchain-ollama"
            ) from e

        print(
            f"[LLM] Ollamaモデルを使用します: {OLLAMA_MODEL}"
        )

        return ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0,
        )

    if LLM_BACKEND == "openai":

        try:
            from langchain_openai import ChatOpenAI
        except ImportError as e:
            raise ImportError(
                "langchain-openai がインストールされていません。\n"
                "pip install langchain-openai"
            ) from e

        return ChatOpenAI(
            model=OPENAI_CHAT_MODEL,
            temperature=0,
        )

    raise ValueError(
        f"未対応のLLM_BACKENDです: {LLM_BACKEND}\n"
        "local または openai を指定してください。"
    )