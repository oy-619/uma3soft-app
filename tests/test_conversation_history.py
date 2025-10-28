"""
会話履歴管理システムのテスト
conversation_history_manager.pyの動作確認とデバッグ
"""

import os
import sys
import sqlite3
from datetime import datetime

# パスの設定
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), "src")
sys.path.insert(0, src_dir)

from conversation_history_manager import ConversationHistoryManager, ConversationContextGenerator
from langchain_openai import ChatOpenAI


def test_database_creation():
    """データベース作成のテスト"""
    print("=" * 50)
    print("データベース作成テスト")
    print("=" * 50)

    db_path = "test_conversation_history.db"

    # 既存のテストDBを削除
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"既存のテストDB削除: {db_path}")

    # 履歴マネージャーの初期化
    history_manager = ConversationHistoryManager(db_path)
    print(f"✅ 履歴マネージャー初期化完了: {db_path}")

    # テーブル構造の確認
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"✅ 作成されたテーブル: {[table[0] for table in tables]}")

        # conversation_historyテーブルの構造確認
        cursor.execute("PRAGMA table_info(conversation_history);")
        columns = cursor.fetchall()
        print("✅ conversation_historyテーブル構造:")
        for column in columns:
            print(f"   - {column[1]} ({column[2]})")

    return history_manager


def test_conversation_saving(history_manager):
    """会話保存のテスト"""
    print("\n" + "=" * 50)
    print("会話保存テスト")
    print("=" * 50)

    test_user_id = "test_user_001"

    # テスト会話データ
    conversations = [
        ("こんにちは！", "こんにちは！お元気ですか？"),
        ("私は野球が好きです", "野球がお好きなんですね！どちらのチームを応援されていますか？"),
        ("読売ジャイアンツです", "ジャイアンツファンなんですね！今シーズンの調子はいかがですか？"),
        ("今日の試合結果を教えて", "申し訳ございませんが、リアルタイムの試合結果は取得できません。")
    ]

    for i, (human_msg, ai_msg) in enumerate(conversations):
        history_manager.save_conversation(test_user_id, human_msg, ai_msg)
        print(f"✅ 会話 {i+1} 保存完了: {human_msg[:20]}...")

    # 保存された会話の確認
    user_history = history_manager.get_user_history(test_user_id)
    messages = user_history.messages
    print(f"✅ 保存されたメッセージ数: {len(messages)}")

    for i, message in enumerate(messages):
        message_type = "👤" if message.__class__.__name__ == "HumanMessage" else "🤖"
        print(f"   {i+1}. {message_type} {message.content[:50]}...")

    return test_user_id


def test_user_profile(history_manager, user_id):
    """ユーザプロフィールのテスト"""
    print("\n" + "=" * 50)
    print("ユーザプロフィールテスト")
    print("=" * 50)

    # プロフィール取得
    profile = history_manager.get_user_profile(user_id)
    print(f"✅ ユーザプロフィール取得:")
    print(f"   - 会話回数: {profile['conversation_count']}")
    print(f"   - 興味・関心: {profile['interests']}")
    print(f"   - 最終対話: {profile['last_interaction']}")

    # 統計情報の確認
    stats = history_manager.get_conversation_statistics(user_id)
    print(f"✅ 会話統計:")
    print(f"   - 総メッセージ数: {stats['total_messages']}")
    print(f"   - ユーザメッセージ: {stats['human_messages']}")
    print(f"   - AIメッセージ: {stats['ai_messages']}")


def test_conversation_search(history_manager, user_id):
    """会話検索のテスト"""
    print("\n" + "=" * 50)
    print("会話検索テスト")
    print("=" * 50)

    # キーワード検索
    search_queries = ["野球", "ジャイアンツ", "試合"]

    for query in search_queries:
        results = history_manager.search_conversations(user_id, query)
        print(f"✅ '{query}' の検索結果: {len(results)}件")
        for result in results:
            message_type = "👤" if result["message_type"] == "human" else "🤖"
            print(f"   {message_type} {result['content'][:50]}...")

    # 最近の会話取得
    recent_conversations = history_manager.get_recent_conversations(user_id, limit=3)
    print(f"✅ 最近の会話: {len(recent_conversations)}件")
    for human_msg, ai_msg, timestamp in recent_conversations:
        time_str = timestamp.strftime("%m/%d %H:%M")
        print(f"   [{time_str}] 👤: {human_msg[:30]}...")
        print(f"   [{time_str}] 🤖: {ai_msg[:30]}...")


def test_context_generation(history_manager, user_id):
    """コンテキスト生成のテスト"""
    print("\n" + "=" * 50)
    print("コンテキスト生成テスト")
    print("=" * 50)

    context_generator = ConversationContextGenerator(history_manager)

    # テストクエリ
    test_queries = [
        "今日の調子はどう？",
        "ジャイアンツの最新情報は？",
        "野球以外の趣味はある？"
    ]

    for query in test_queries:
        prompt = context_generator.generate_contextual_response_prompt(user_id, query)
        print(f"✅ クエリ: {query}")
        print(f"📝 生成されたプロンプト:")
        print(prompt[:300] + "..." if len(prompt) > 300 else prompt)
        print("-" * 30)


def test_llm_response(history_manager, user_id):
    """LLM応答生成のテスト（OpenAI APIキーが設定されている場合）"""
    print("\n" + "=" * 50)
    print("LLM応答生成テスト")
    print("=" * 50)

    # OpenAI APIキーの確認
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ OPENAI_API_KEYが設定されていません。LLM応答テストをスキップします。")
        return

    try:
        context_generator = ConversationContextGenerator(history_manager)
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)

        test_message = "今度の週末は何をしようかな？"

        print(f"📝 テストメッセージ: {test_message}")

        response = context_generator.generate_response_with_history(
            user_id, test_message, llm
        )

        print(f"🤖 履歴ベース応答:")
        print(response)

        # 応答を履歴に保存
        history_manager.save_conversation(user_id, test_message, response)
        print("✅ 応答を履歴に保存しました")

    except Exception as e:
        print(f"❌ LLM応答生成エラー: {e}")


def test_multiple_users(history_manager):
    """複数ユーザーのテスト"""
    print("\n" + "=" * 50)
    print("複数ユーザーテスト")
    print("=" * 50)

    users_data = [
        ("user_002", "サッカーが好きです", "サッカーがお好きなんですね！"),
        ("user_003", "料理に興味があります", "料理に興味がおありなんですね！"),
        ("user_004", "映画をよく見ます", "映画がお好きなんですね！")
    ]

    for user_id, human_msg, ai_msg in users_data:
        history_manager.save_conversation(user_id, human_msg, ai_msg)
        profile = history_manager.get_user_profile(user_id)
        print(f"✅ {user_id}: 会話数={profile['conversation_count']}, 興味={profile['interests']}")


def test_cleanup(db_path):
    """テスト後のクリーンアップ"""
    print("\n" + "=" * 50)
    print("クリーンアップ")
    print("=" * 50)

    if os.path.exists(db_path):
        # ファイルサイズの確認
        file_size = os.path.getsize(db_path)
        print(f"📊 テストDB サイズ: {file_size} bytes")

        # テーブル内のレコード数確認
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM conversation_history")
            conversation_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM user_profiles")
            profile_count = cursor.fetchone()[0]

            print(f"📊 会話レコード数: {conversation_count}")
            print(f"📊 ユーザプロファイル数: {profile_count}")

        # テストDBを保持するかユーザーに確認
        keep_db = input("\nテストDBを保持しますか？ (y/N): ").lower().strip()
        if keep_db != 'y':
            os.remove(db_path)
            print(f"✅ テストDBを削除しました: {db_path}")
        else:
            print(f"✅ テストDBを保持しました: {db_path}")


def main():
    """メインテスト実行関数"""
    print("🚀 会話履歴管理システム テスト開始")
    print(f"📅 テスト実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # 1. データベース作成テスト
        history_manager = test_database_creation()

        # 2. 会話保存テスト
        test_user_id = test_conversation_saving(history_manager)

        # 3. ユーザプロフィールテスト
        test_user_profile(history_manager, test_user_id)

        # 4. 会話検索テスト
        test_conversation_search(history_manager, test_user_id)

        # 5. コンテキスト生成テスト
        test_context_generation(history_manager, test_user_id)

        # 6. LLM応答生成テスト
        test_llm_response(history_manager, test_user_id)

        # 7. 複数ユーザーテスト
        test_multiple_users(history_manager)

        print("\n🎉 全テスト完了！")

    except Exception as e:
        print(f"\n❌ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 8. クリーンアップ
        test_cleanup("test_conversation_history.db")


if __name__ == "__main__":
    main()
