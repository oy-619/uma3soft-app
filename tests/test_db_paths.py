#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# reminder_schedule.pyと同じパス構成
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_DIR = os.path.join(PROJECT_ROOT, "db")
PERSIST_DIRECTORY = os.path.join(DB_DIR, "chroma_store")

print(f"[テスト] PROJECT_ROOT: {PROJECT_ROOT}")
print(f"[テスト] DB_DIR: {DB_DIR}")
print(f"[テスト] PERSIST_DIRECTORY: {PERSIST_DIRECTORY}")
print(f"[テスト] ChromaDBディレクトリ存在: {os.path.exists(PERSIST_DIRECTORY)}")

# embeddings_model初期化
embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

try:
    # ChromaDB接続
    vector_db = Chroma(
        persist_directory=PERSIST_DIRECTORY, embedding_function=embeddings_model
    )

    print(f"[テスト] ChromaDB接続成功")

    # 全件取得
    all_docs = vector_db.get()
    print(f"[テスト] 全ドキュメント数: {len(all_docs['documents'])}")

    # "テストイベント"を含むドキュメント検索
    test_docs = [doc for doc in all_docs["documents"] if "テストイベント" in doc]
    print(f"[テスト] 'テストイベント'を含むドキュメント数: {len(test_docs)}")

    for i, doc in enumerate(test_docs):
        print(f"[テスト] ドキュメント{i+1}: {doc[:200]}...")

    # similarity_searchテスト
    search_results = vector_db.similarity_search("[ノート]", k=50)
    print(f"[テスト] similarity_search('[ノート]', k=50) 結果数: {len(search_results)}")

    # "テストイベント"を含む結果
    test_search_results = [
        doc for doc in search_results if "テストイベント" in doc.page_content
    ]
    print(
        f"[テスト] similarity_search結果で'テストイベント'を含む数: {len(test_search_results)}"
    )

    for i, doc in enumerate(test_search_results):
        print(f"[テスト] 検索結果{i+1}: {doc.page_content[:200]}...")

except Exception as e:
    print(f"[エラー] ChromaDB接続失敗: {e}")
    sys.exit(1)
