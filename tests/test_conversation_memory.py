"""
会話履歴参照テスト
実際のLINE Botで会話履歴が使用されているかテスト
"""

import os
import sys
import sqlite3
from datetime import datetime

# パスの設定
sys.path.insert(0, 'Lesson25/uma3soft-app/src')

def test_conversation_history_usage():
    """会話履歴の使用状況をテスト"""
    print("=" * 60)
    print("会話履歴参照テスト")
    print("=" * 60)

    # データベースの確認
    db_path = 'Lesson25/uma3soft-app/db/conversation_history.db'
    if not os.path.exists(db_path):
        print(f"❌ データベースが見つかりません: {db_path}")
        return

    # 実際のユーザーIDを確認
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, COUNT(*) as message_count, MAX(timestamp) as last_message
        FROM conversation_history
        GROUP BY user_id
        ORDER BY message_count DESC
    """)

    users = cursor.fetchall()
    print(f"✅ データベース内のユーザー数: {len(users)}")

    for user_id, count, last_message in users[:3]:
        print(f"   - {user_id[:20]}...: {count}メッセージ, 最終: {last_message}")

    if not users:
        print("⚠️ 会話履歴が見つかりません")
        conn.close()
        return

    # 最もアクティブなユーザーをテスト対象に
    test_user_id = users[0][0]
    print(f"\n🎯 テスト対象ユーザー: {test_user_id[:20]}...")

    # そのユーザーの会話履歴を確認
    cursor.execute("""
        SELECT message_type, content, timestamp
        FROM conversation_history
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT 5
    """, (test_user_id,))

    recent_messages = cursor.fetchall()
    print(f"✅ 最近の会話履歴 ({len(recent_messages)}件):")

    for msg_type, content, timestamp in recent_messages:
        icon = "👤" if msg_type == "human" else "🤖"
        print(f"   {icon} [{timestamp}] {content[:60]}...")

    conn.close()

    # 統合システムのテスト
    print(f"\n📋 統合システムで履歴参照テスト")

    try:
        from integrated_conversation_system import IntegratedConversationSystem

        system = IntegratedConversationSystem(
            'Lesson25/uma3soft-app/db/chroma_store',
            'Lesson25/uma3soft-app/db/conversation_history.db'
        )

        # ユーザープロフィールの取得
        profile = system.history_manager.get_user_profile(test_user_id)
        print(f"✅ ユーザープロフィール:")
        print(f"   - 会話回数: {profile['conversation_count']}")
        print(f"   - 興味・関心: {profile['interests']}")
        print(f"   - 最終対話: {profile['last_interaction']}")

        # 最近の会話の取得
        recent_conversations = system.history_manager.get_recent_conversations(test_user_id, limit=3)
        print(f"✅ 最近の会話 ({len(recent_conversations)}件):")

        for human_msg, ai_msg, timestamp in recent_conversations:
            time_str = timestamp.strftime("%m/%d %H:%M")
            print(f"   [{time_str}] 👤: {human_msg[:40]}...")
            print(f"   [{time_str}] 🤖: {ai_msg[:40]}...")

        # 会話検索テスト
        search_results = system.search_user_conversations(test_user_id, "キャプテン", limit=3)
        print(f"✅ 'キャプテン'検索結果 ({len(search_results)}件):")

        for result in search_results:
            msg_type = "👤" if result["message_type"] == "human" else "🤖"
            print(f"   {msg_type} {result['content'][:50]}...")

        # コンテキスト生成テスト
        print(f"\n🧠 コンテキスト生成テスト")
        test_query = "前回の話を覚えてる？"

        context_prompt = system.context_generator.generate_contextual_response_prompt(
            test_user_id, test_query, max_history_items=3
        )

        print(f"✅ 生成されたプロンプト（一部）:")
        prompt_lines = context_prompt.split('\n')
        for line in prompt_lines[:10]:  # 最初の10行のみ表示
            print(f"   {line}")
        print("   ...")

        print(f"✅ プロンプト長: {len(context_prompt)}文字")

        # 実際にユーザーの会話履歴が含まれているかチェック
        if test_user_id[:10] in context_prompt or "会話回数" in context_prompt:
            print("✅ ユーザー固有の情報が含まれています")
        else:
            print("⚠️ ユーザー固有の情報が不足している可能性があります")

    except Exception as e:
        print(f"❌ 統合システムテストエラー: {e}")
        import traceback
        traceback.print_exc()


def test_uma3_integration():
    """uma3.pyでの統合会話システム使用確認"""
    print(f"\n📱 uma3.py統合確認")

    try:
        import uma3

        # 統合システムが初期化されているか確認
        if hasattr(uma3, 'integrated_conversation_system'):
            print("✅ 統合会話システムが初期化されています")

            system = uma3.integrated_conversation_system

            # データベースパスの確認
            print(f"✅ ChromaDBパス: {system.chroma_persist_directory}")
            print(f"✅ 会話履歴DBパス: {system.conversation_db_path}")

            # 実際のデータベースファイルが存在するか確認
            if os.path.exists(system.conversation_db_path):
                print("✅ 会話履歴データベースファイルが存在します")
            else:
                print("❌ 会話履歴データベースファイルが見つかりません")
        else:
            print("❌ 統合会話システムが初期化されていません")

    except Exception as e:
        print(f"❌ uma3.py統合確認エラー: {e}")


if __name__ == "__main__":
    print("🚀 会話履歴参照テスト開始")
    print(f"📅 テスト実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    test_conversation_history_usage()
    test_uma3_integration()

    print("\n🎉 テスト完了！")
