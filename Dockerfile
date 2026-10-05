# 1. ベースイメージの指定
FROM python:3.11-slim

# 2. 作業ディレクトリの設定
WORKDIR /app

# 3. 環境変数の設定
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 4. OSレベルの必要な依存パッケージのインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 5. pipの更新と requirements.txt のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cu128 \
    torch==2.11.0+cu128 && \
    pip install --no-cache-dir -r requirements.txt

# 6. ソースコードのコピー
COPY . .

# 7. 実行するコマンド（ingest完了後に自動でragを実行）
CMD python ingest.py && python rag.py