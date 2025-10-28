#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3

# ChromaDBのSQLiteファイルパス
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_DIR = os.path.join(PROJECT_ROOT, "db")
CHROMA_DB_PATH = os.path.join(DB_DIR, "chroma_store", "chroma.sqlite3")

print(f"ChromaDB SQLiteファイル: {CHROMA_DB_PATH}")
print(f"ファイル存在: {os.path.exists(CHROMA_DB_PATH)}")

try:
    # SQLiteファイルに直接接続
    conn = sqlite3.connect(CHROMA_DB_PATH)
    cursor = conn.cursor()

    # テーブル一覧を取得
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"テーブル一覧: {tables}")

    # embeddings_queueテーブルの内容を確認
    cursor.execute("SELECT * FROM embeddings_queue LIMIT 5;")
    rows = cursor.fetchall()
    print(f"embeddings_queue最初の5行: {rows}")

    # ドキュメント数をカウント
    cursor.execute("SELECT COUNT(*) FROM embeddings_queue;")
    count = cursor.fetchone()[0]
    print(f"総ドキュメント数: {count}")

    # テストイベントを含むドキュメントを検索
    cursor.execute(
        "SELECT document FROM embeddings_queue WHERE document LIKE '%テストイベント%';"
    )
    test_docs = cursor.fetchall()
    print(f"テストイベントを含むドキュメント数: {len(test_docs)}")

    for i, doc in enumerate(test_docs[:3]):  # 最初の3件表示
        print(f"ドキュメント{i+1}: {doc[0][:200]}...")

    conn.close()

except Exception as e:
    print(f"SQLite接続エラー: {e}")
    import traceback

    traceback.print_exc()
