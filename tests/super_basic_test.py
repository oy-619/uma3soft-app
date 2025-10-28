import os

print("=== 超基本テスト ===")

# パス設定
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_DIR = os.path.join(PROJECT_ROOT, "db")
PERSIST_DIRECTORY = os.path.join(DB_DIR, "chroma_store")

print(f"PERSIST_DIRECTORY: {PERSIST_DIRECTORY}")
print(f"ChromaDB exists: {os.path.exists(PERSIST_DIRECTORY)}")

# ディレクトリ内容確認
if os.path.exists(PERSIST_DIRECTORY):
    import os

    files = os.listdir(PERSIST_DIRECTORY)
    print(f"ChromaDBディレクトリ内容: {files}")

print("テスト完了")
