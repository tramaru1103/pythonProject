FROM python:3.9

WORKDIR /app

# 依存関係のインストール
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ソースコードのコピー
COPY . .

# 実行コマンド
CMD ["python", "main.py"]
