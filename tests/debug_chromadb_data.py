#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime, timedelta

# ChromaDBに直接アクセスしてテストイベントを検索
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_DIR = os.path.join(PROJECT_ROOT, "db")
PERSIST_DIRECTORY = os.path.join(DB_DIR, "chroma_store")

print(f"=== ChromaDBデータ検索テスト ===")
print(f"PERSIST_DIRECTORY: {PERSIST_DIRECTORY}")
print(f"ChromaDB存在確認: {os.path.exists(PERSIST_DIRECTORY)}")

try:
    from langchain_chroma import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings

    embeddings_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_db = Chroma(
        persist_directory=PERSIST_DIRECTORY, embedding_function=embeddings_model
    )

    print("ChromaDB接続成功")

    # 全データを取得
    all_docs = vector_db.get()
    print(f"全ドキュメント数: {len(all_docs['documents'])}")

    # テストイベントを含むドキュメントを検索
    test_docs = []
    for i, doc in enumerate(all_docs["documents"]):
        if "テストイベント" in doc and "[ノート]" in doc:
            test_docs.append(doc)
            print(f"\n=== 見つかったテストイベント {len(test_docs)} ===")
            print(doc)
            print("=" * 50)

    print(f"\nテストイベントを含む[ノート]の数: {len(test_docs)}")

    # 日付パターンのテスト
    if test_docs:
        import re

        for doc in test_docs:
            print(f"\n--- 日付パターン検索 ---")
            patterns = [
                r"(\d{4})/(\d{1,2})/(\d{1,2})\([月火水木金土日]\)",
                r"(\d{4})/(\d{1,2})/(\d{1,2})",
            ]

            for pattern in patterns:
                matches = re.findall(pattern, doc)
                if matches:
                    print(f"パターン '{pattern}' マッチ: {matches}")
                    for match in matches:
                        if len(match) == 3:
                            year, month, day = map(int, match)
                            date_obj = datetime(year, month, day).date()
                            print(f"  パース結果: {date_obj}")

                            # 明日かどうか確認
                            tomorrow = datetime.now().date() + timedelta(days=1)
                            print(f"  明日({tomorrow})と一致: {date_obj == tomorrow}")

except Exception as e:
    print(f"エラー: {e}")
    import traceback

    traceback.print_exc()
