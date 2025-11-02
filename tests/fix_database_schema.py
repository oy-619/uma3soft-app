#!/usr/bin/env python3
"""
データベーススキーマ修正スクリプト
conversation_history.dbのスキーマを最新版に更新
"""

import os
import sqlite3
import sys
from datetime import datetime

# パスの設定
db_path = "db/conversation_history.db"

def check_and_fix_database():
    """データベースのスキーマを確認・修正"""
    print("=" * 60)
    print("🔧 データベーススキーマ修正スクリプト")
    print("=" * 60)

    try:
        # データベースファイルの存在確認
        if not os.path.exists(db_path):
            print(f"❌ データベースファイルが見つかりません: {db_path}")
            return False

        print(f"✅ データベースファイル確認: {db_path}")

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # 現在のテーブル構造を確認
            print("\n📊 現在のテーブル構造:")

            # conversations テーブルの確認
            cursor.execute("PRAGMA table_info(conversations)")
            conversations_columns = cursor.fetchall()
            print("conversations テーブル:")
            for col in conversations_columns:
                print(f"  - {col[1]} ({col[2]})")

            # user_profiles テーブルの確認
            try:
                cursor.execute("PRAGMA table_info(user_profiles)")
                user_profiles_columns = cursor.fetchall()
                if user_profiles_columns:
                    print("user_profiles テーブル:")
                    for col in user_profiles_columns:
                        print(f"  - {col[1]} ({col[2]})")
                else:
                    print("user_profiles テーブル: 存在しません")
            except sqlite3.OperationalError:
                print("user_profiles テーブル: 存在しません")
                user_profiles_columns = []

            # user_profiles テーブルが存在しない場合は作成
            if not user_profiles_columns:
                print("\n🔨 user_profiles テーブルを作成しています...")
                cursor.execute("""
                    CREATE TABLE user_profiles (
                        user_id TEXT PRIMARY KEY,
                        interests TEXT DEFAULT '[]',
                        preferences TEXT DEFAULT '{}',
                        conversation_count INTEGER DEFAULT 0,
                        last_active DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
                print("✅ user_profiles テーブルを作成しました")
            else:
                # 既存のテーブルにpreferencesカラムがあるかチェック
                column_names = [col[1] for col in user_profiles_columns]

                if 'preferences' not in column_names:
                    print("\n🔨 preferences カラムを追加しています...")
                    cursor.execute("ALTER TABLE user_profiles ADD COLUMN preferences TEXT DEFAULT '{}'")
                    conn.commit()
                    print("✅ preferences カラムを追加しました")

                if 'interests' not in column_names:
                    print("\n🔨 interests カラムを追加しています...")
                    cursor.execute("ALTER TABLE user_profiles ADD COLUMN interests TEXT DEFAULT '[]'")
                    conn.commit()
                    print("✅ interests カラムを追加しました")

                if 'conversation_count' not in column_names:
                    print("\n🔨 conversation_count カラムを追加しています...")
                    cursor.execute("ALTER TABLE user_profiles ADD COLUMN conversation_count INTEGER DEFAULT 0")
                    conn.commit()
                    print("✅ conversation_count カラムを追加しました")

                if 'last_active' not in column_names:
                    print("\n🔨 last_active カラムを追加しています...")
                    cursor.execute("ALTER TABLE user_profiles ADD COLUMN last_active DATETIME")
                    conn.commit()
                    print("✅ last_active カラムを追加しました")

                if 'created_at' not in column_names:
                    print("\n🔨 created_at カラムを追加しています...")
                    cursor.execute("ALTER TABLE user_profiles ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
                    conn.commit()
                    print("✅ created_at カラムを追加しました")

                if 'updated_at' not in column_names:
                    print("\n🔨 updated_at カラムを追加しています...")
                    cursor.execute("ALTER TABLE user_profiles ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP")
                    conn.commit()
                    print("✅ updated_at カラムを追加しました")

            # 最終的なテーブル構造を確認
            print("\n📊 修正後のテーブル構造:")

            cursor.execute("PRAGMA table_info(conversations)")
            conversations_columns = cursor.fetchall()
            print("conversations テーブル:")
            for col in conversations_columns:
                print(f"  - {col[1]} ({col[2]})")

            cursor.execute("PRAGMA table_info(user_profiles)")
            user_profiles_columns = cursor.fetchall()
            print("user_profiles テーブル:")
            for col in user_profiles_columns:
                print(f"  - {col[1]} ({col[2]})")

            # データ件数の確認
            cursor.execute("SELECT COUNT(*) FROM conversations")
            conv_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM user_profiles")
            profile_count = cursor.fetchone()[0]

            print(f"\n📈 データ件数:")
            print(f"  - conversations: {conv_count}件")
            print(f"  - user_profiles: {profile_count}件")

            # テスト用のユーザープロファイルを作成（存在しない場合）
            test_user_id = "test_user"
            cursor.execute("SELECT COUNT(*) FROM user_profiles WHERE user_id = ?", (test_user_id,))
            if cursor.fetchone()[0] == 0:
                print(f"\n🧪 テスト用ユーザープロファイルを作成: {test_user_id}")
                cursor.execute("""
                    INSERT INTO user_profiles (user_id, interests, preferences, conversation_count)
                    VALUES (?, ?, ?, ?)
                """, (test_user_id, '["テスト", "開発"]', '{"theme": "default"}', 1))
                conn.commit()
                print("✅ テスト用プロファイルを作成しました")

            print("\n" + "=" * 60)
            print("🎉 データベーススキーマ修正完了!")
            print("=" * 60)

            return True

    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_user_profile_access():
    """ユーザープロファイルアクセステスト"""
    print("\n🧪 ユーザープロファイルアクセステスト")
    print("-" * 40)

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # テスト用ユーザーでプロファイル取得テスト
            test_user_id = "test_user_profile"

            # プロファイル取得（存在しない場合は作成）
            cursor.execute("""
                SELECT interests, preferences, conversation_count, last_active, created_at
                FROM user_profiles WHERE user_id = ?
            """, (test_user_id,))

            result = cursor.fetchone()
            if result:
                print(f"✅ 既存プロファイル取得成功: {test_user_id}")
                print(f"   - interests: {result[0]}")
                print(f"   - preferences: {result[1]}")
                print(f"   - conversation_count: {result[2]}")
            else:
                print(f"➕ 新規プロファイル作成: {test_user_id}")
                cursor.execute("""
                    INSERT INTO user_profiles (user_id, interests, preferences, conversation_count)
                    VALUES (?, ?, ?, ?)
                """, (test_user_id, '["profile_test"]', '{"test": true}', 0))
                conn.commit()
                print("✅ 新規プロファイル作成成功")

    except Exception as e:
        print(f"❌ テスト失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print(f"現在のディレクトリ: {os.getcwd()}")
    print(f"対象データベース: {db_path}")

    if check_and_fix_database():
        test_user_profile_access()
        print("\n✨ スキーマ修正とテストが正常に完了しました！")
    else:
        print("\n❌ スキーマ修正に失敗しました")
        sys.exit(1)
