#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

try:
    print("=== ChromaDB基本テスト開始 ===")

    # パス設定
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    DB_DIR = os.path.join(PROJECT_ROOT, "db")
    PERSIST_DIRECTORY = os.path.join(DB_DIR, "chroma_store")

    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"DB_DIR: {DB_DIR}")
    print(f"PERSIST_DIRECTORY: {PERSIST_DIRECTORY}")
    print(f"ChromaDB exists: {os.path.exists(PERSIST_DIRECTORY)}")

    # モジュールインポートテスト
    print("\n=== モジュールインポートテスト ===")
    from langchain_chroma import Chroma

    print("langchain_chroma.Chroma: OK")

    from langchain_huggingface import HuggingFaceEmbeddings

    print("langchain_huggingface.HuggingFaceEmbeddings: OK")

    # embedding初期化テスト
    print("\n=== embedding初期化テスト ===")
    embeddings_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    print("HuggingFaceEmbeddings初期化: OK")

    # ChromaDB接続テスト
    print("\n=== ChromaDB接続テスト ===")
    vector_db = Chroma(
        persist_directory=PERSIST_DIRECTORY, embedding_function=embeddings_model
    )
    print("ChromaDB接続: OK")

    # 基本データ取得テスト
    print("\n=== 基本データ取得テスト ===")
    all_docs = vector_db.get()
    print(f"全ドキュメント数: {len(all_docs['documents'])}")

    # テストイベント検索
    print("\n=== テストイベント検索 ===")
    test_count = 0
    for doc in all_docs["documents"]:
        if "テストイベント" in doc:
            test_count += 1
            print(f"見つかりました: {doc[:100]}...")

    print(f"テストイベントを含むドキュメント数: {test_count}")

    print("\n=== テスト完了 ===")

except Exception as e:
    print(f"エラー発生: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
