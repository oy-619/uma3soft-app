#!/usr/bin/env python3
"""
簡単なChromaDB状況確認
"""

import sqlite3
import os

def check_chromadb():
    db_path = r"C:\work\ws_python\GenerationAiCamp\Lesson25\uma3soft-app\db\chroma_store\chroma.sqlite3"

    print("=" * 50)
    print("🔍 ChromaDB状況確認")
    print("=" * 50)

    if not os.path.exists(db_path):
        print("❌ ChromaDBファイルが存在しません")
        return

    print(f"📁 ファイルパス: {db_path}")
    print(f"📊 ファイルサイズ: {os.path.getsize(db_path)} bytes")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # テーブル一覧
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📋 テーブル数: {len(tables)}")

        for table in tables:
            table_name = table[0]
            print(f"   - {table_name}")

            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"     レコード数: {count}")

                # 最新のレコードを少し見る
                if count > 0:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                    sample = cursor.fetchone()
                    print(f"     列数: {len(sample) if sample else 0}")

            except Exception as e:
                print(f"     エラー: {e}")

        conn.close()

    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    check_chromadb()
