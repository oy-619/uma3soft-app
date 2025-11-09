FROM python:3.12-slim

# システム依存パッケージをインストール
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係ファイルをコピー
COPY requirements.railway.txt /app/

# 依存関係をインストール
RUN pip install --no-cache-dir -r requirements.railway.txt

# アプリケーションファイルをコピー
COPY . /app/

# ポートを公開
EXPOSE 8080

# アプリケーションを起動
CMD ["python", "src/uma3.py"]
