#!/usr/bin/env python3
"""
デバッグ実行時のパス動作テスト
"""
import os
import sys

print("=== デバッグ実行時のパス動作テスト ===")
print(f"現在のワーキングディレクトリ: {os.getcwd()}")
print(f"スクリプトのパス: {__file__}")
print(f"sys.path: {sys.path[:3]}...")

# srcディレクトリに移動（F5デバッグ実行時の状況を再現）
src_dir = os.path.join(os.path.dirname(__file__), "src")
os.chdir(src_dir)
print(f"\nsrcディレクトリに移動後:")
print(f"現在のワーキングディレクトリ: {os.getcwd()}")

# chathistory2dbをインポート
sys.path.insert(0, ".")
try:
    from chathistory2db import PERSIST_DIRECTORY, PROJECT_ROOT, SCRIPT_DIR

    print(f"\n=== chathistory2db.pyのパス設定 ===")
    print(f"SCRIPT_DIR: {SCRIPT_DIR}")
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"PERSIST_DIRECTORY: {PERSIST_DIRECTORY}")
    print(f"PERSIST_DIRECTORYが存在するか: {os.path.exists(PERSIST_DIRECTORY)}")

    # 実際にChromaを初期化してみる
    print(f"\n=== Chroma初期化テスト ===")
    from langchain_chroma import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings

    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vector_db = Chroma(
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=embedding_model,
    )
    print(f"Chroma初期化成功: {vector_db}")
    print(f"実際のディレクトリ確認: {os.path.exists(PERSIST_DIRECTORY)}")

except Exception as e:
    print(f"エラー: {e}")
    import traceback

    traceback.print_exc()
