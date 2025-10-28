"""
データベース内容の直接確認
"""

import sqlite3
import os

db_path = 'Lesson25/uma3soft-app/db/conversation_history.db'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("🔍 データベース内のユーザーID一覧:")
    cursor.execute("SELECT DISTINCT user_id, COUNT(*) as msg_count FROM conversation_history GROUP BY user_id;")
    users = cursor.fetchall()

    for user_id, count in users:
        print(f"   ユーザー: {user_id}")
        print(f"   メッセージ数: {count}")

        # 最新の会話をいくつか表示
        cursor.execute("""
            SELECT message_type, content, timestamp
            FROM conversation_history
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT 3
        """, (user_id,))

        recent_msgs = cursor.fetchall()
        print(f"   最新の会話:")
        for msg_type, content, timestamp in recent_msgs:
            icon = "👤" if msg_type == "human" else "🤖"
            print(f"     {icon} [{timestamp}] {content[:50]}...")
        print()

    # user_profiles テーブルも確認
    print("📊 ユーザープロフィール:")
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_profiles';")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(user_profiles);")
            columns = cursor.fetchall()
            print("   テーブル構造:", [col[1] for col in columns])

            cursor.execute("SELECT * FROM user_profiles;")
            profiles = cursor.fetchall()

            for profile in profiles:
                print(f"   プロフィール: {profile}")
        else:
            print("   user_profiles テーブルが存在しません")
    except Exception as e:
        print(f"   プロフィール確認エラー: {e}")

    # テーブル一覧も表示
    print("\n🗃️ 全テーブル一覧:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        print(f"   テーブル: {table[0]}")

    conn.close()
else:
    print(f"❌ データベースファイルが見つかりません: {db_path}")
