# ペルソナベースAIエージェント - Docker環境
# Python 3.11 + Node.js 18 + 全依存関係を含む統合環境

FROM python:3.11-slim

# システムの更新と必要なシステムライブラリのインストール
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Node.js 18のインストール
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# 作業ディレクトリの設定
WORKDIR /app

# Python依存関係ファイルをコピー
COPY requirements-basic.txt .

# Python依存関係のインストール（基本版）
RUN pip install --no-cache-dir -r requirements-basic.txt

# Node.js依存関係ファイルをコピー
COPY package.json package-lock.json* ./

# Node.js依存関係のインストール
RUN npm install

# プロジェクトファイルをコピー
COPY . .

# 必要なディレクトリを作成
RUN mkdir -p agents/persona/outputs \
    && mkdir -p products/persona \
    && mkdir -p common/knowledge/customer-support \
    && mkdir -p common/knowledge/industry

# 環境変数の設定
ENV PYTHONPATH=/app
ENV NODE_PATH=/app/node_modules

# ポート露出（必要に応じて）
EXPOSE 8000 3000

# デフォルトコマンド（bash開始）
CMD ["/bin/bash"] 