"""
統合会話システムのテスト
uma3.pyでの動作確認とデバッグ
"""

import os
import sys
from datetime import datetime

# パスの設定
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), "src")
sys.path.insert(0, src_dir)

from integrated_conversation_system import IntegratedConversationSystem
from langchain_openai import ChatOpenAI


def test_integrated_system():
    """統合システムの基本テスト"""
    print("=" * 60)
    print("統合会話システムテスト")
    print("=" * 60)

    # 設定
    chroma_persist_dir = "Lesson25/uma3soft-app/db/chroma_store"
    conversation_db_path = "Lesson25/uma3soft-app/db/test_conversation_history.db"

    # 既存のテストDBを削除
    if os.path.exists(conversation_db_path):
        os.remove(conversation_db_path)
        print(f"✅ 既存のテストDB削除: {conversation_db_path}")

    try:
        # 統合システムの初期化
        integrated_system = IntegratedConversationSystem(
            chroma_persist_directory=chroma_persist_dir,
            conversation_db_path=conversation_db_path
        )
        print("✅ 統合システム初期化完了")

        # OpenAI APIキーの確認
        if not os.getenv("OPENAI_API_KEY"):
            print("⚠️ OPENAI_API_KEYが設定されていません。応答生成テストをスキップします。")
            return

        # LLMの初期化
        try:
            llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.3,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
            print("✅ LLM初期化完了")
        except Exception as e:
            print(f"⚠️ LLM初期化エラー: {e}")
            print("⚠️ 応答生成テストをスキップします。")
            return

        # テストユーザ
        test_user_id = "line_user_test_001"

        # テストシナリオ：会話履歴の蓄積
        test_conversations = [
            ("こんにちは、私は野球が大好きです", "初回会話"),
            ("読売ジャイアンツのファンです", "興味の蓄積"),
            ("今週の予定を教えて", "スケジュール問い合わせ"),
            ("野球の試合はありますか？", "過去の興味を踏まえた質問"),
        ]

        print("\n" + "=" * 40)
        print("会話履歴テストシナリオ")
        print("=" * 40)

        for i, (message, description) in enumerate(test_conversations, 1):
            print(f"\n{i}. {description}")
            print(f"   入力: {message}")

            try:
                # 統合システムで応答生成
                result = integrated_system.generate_integrated_response(
                    test_user_id, message, llm
                )

                if "error" in result:
                    print(f"   ❌ エラー: {result.get('error_message', 'Unknown error')}")
                else:
                    response = result["response"]
                    context_info = result.get("context_used", {})

                    print(f"   🤖 応答: {response[:150]}...")
                    print(f"   📊 コンテキスト情報:")
                    print(f"      - ChromaDB検索結果: {context_info.get('chroma_results', 0)}件")
                    print(f"      - 会話履歴: {context_info.get('conversation_history', 0)}件")
                    print(f"      - 関連会話: {context_info.get('relevant_conversations', 0)}件")

                    # ユーザプロフィール情報
                    user_profile = context_info.get('user_profile', {})
                    if user_profile:
                        print(f"      - 総会話数: {user_profile.get('conversation_count', 0)}")
                        if user_profile.get('interests'):
                            interests = user_profile['interests'][:2]
                            print(f"      - 興味: {interests}")

            except Exception as e:
                print(f"   ❌ 応答生成エラー: {e}")
                import traceback
                traceback.print_exc()

            print("-" * 30)

        # 蓄積された会話履歴の確認
        print("\n" + "=" * 40)
        print("会話履歴蓄積確認")
        print("=" * 40)

        # ユーザサマリーの取得
        summary = integrated_system.get_user_conversation_summary(test_user_id)

        print(f"✅ ユーザID: {summary['user_id']}")
        print(f"✅ 総会話数: {summary['statistics']['total_messages']}")
        print(f"✅ ユーザメッセージ: {summary['statistics']['human_messages']}")
        print(f"✅ AIメッセージ: {summary['statistics']['ai_messages']}")

        # 興味・関心の確認
        interests = summary['profile']['interests']
        if interests:
            print(f"✅ 学習された興味・関心: {interests}")
        else:
            print("ℹ️ 興味・関心はまだ学習されていません")

        # 最近の会話履歴
        recent_conversations = summary['recent_conversations']
        if recent_conversations:
            print(f"✅ 最近の会話: {len(recent_conversations)}件")
            for human_msg, ai_msg, timestamp in recent_conversations[:2]:
                time_str = timestamp.strftime("%H:%M")
                print(f"   [{time_str}] 👤: {human_msg[:50]}...")
                print(f"   [{time_str}] 🤖: {ai_msg[:50]}...")

        # 会話検索テスト
        print("\n" + "=" * 40)
        print("会話検索テスト")
        print("=" * 40)

        search_queries = ["野球", "ジャイアンツ", "予定"]
        for query in search_queries:
            search_results = integrated_system.search_user_conversations(
                test_user_id, query, limit=3
            )
            print(f"✅ '{query}' の検索結果: {len(search_results)}件")
            for result in search_results:
                message_type = "👤" if result["message_type"] == "human" else "🤖"
                print(f"   {message_type} {result['content'][:60]}...")

        print("\n🎉 統合システムテスト完了！")

        # 継続性テスト：同じユーザとの追加会話
        print("\n" + "=" * 40)
        print("継続性テスト")
        print("=" * 40)

        follow_up_message = "前に話した野球の件、覚えていますか？"
        print(f"継続質問: {follow_up_message}")

        try:
            result = integrated_system.generate_integrated_response(
                test_user_id, follow_up_message, llm
            )

            if "error" not in result:
                response = result["response"]
                context_info = result.get("context_used", {})

                print(f"🤖 応答: {response}")
                print(f"📊 この応答でのコンテキスト活用:")
                print(f"   - 関連会話: {context_info.get('relevant_conversations', 0)}件")
                print(f"   - 会話履歴活用: {context_info.get('conversation_history', 0)}件")

                # 過去の会話が参照されているかチェック
                if "野球" in response or "ジャイアンツ" in response:
                    print("✅ 過去の会話内容が適切に参照されています")
                else:
                    print("⚠️ 過去の会話内容の参照が不十分です")
            else:
                print(f"❌ 継続性テストでエラー: {result.get('error_message')}")

        except Exception as e:
            print(f"❌ 継続性テストエラー: {e}")

    except Exception as e:
        print(f"❌ 統合システムテスト中にエラー: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # クリーンアップ確認
        print("\n" + "=" * 40)
        print("テスト後の状態確認")
        print("=" * 40)

        if os.path.exists(conversation_db_path):
            file_size = os.path.getsize(conversation_db_path)
            print(f"📊 会話履歴DB サイズ: {file_size} bytes")

            keep_db = input("\nテスト用会話履歴DBを保持しますか？ (y/N): ").lower().strip()
            if keep_db != 'y':
                os.remove(conversation_db_path)
                print(f"✅ テスト用DBを削除しました: {conversation_db_path}")
            else:
                print(f"✅ テスト用DBを保持しました: {conversation_db_path}")


def test_line_bot_integration():
    """LINE Bot統合の簡易テスト"""
    print("\n" + "=" * 60)
    print("LINE Bot統合テスト (簡易版)")
    print("=" * 60)

    # uma3.pyのimportテスト
    try:
        import uma3
        print("✅ uma3.py import成功")

        # 統合システムが初期化されているかチェック
        if hasattr(uma3, 'integrated_conversation_system'):
            print("✅ 統合会話システムが初期化されています")

            # 簡単な機能テスト
            test_user = "test_line_user"
            system = uma3.integrated_conversation_system

            # ユーザプロフィール取得テスト
            profile = system.history_manager.get_user_profile(test_user)
            print(f"✅ ユーザプロフィール取得: 会話数={profile['conversation_count']}")

        else:
            print("⚠️ 統合会話システムが見つかりません")

    except ImportError as e:
        print(f"❌ uma3.py import失敗: {e}")
    except Exception as e:
        print(f"❌ LINE Bot統合テストエラー: {e}")


if __name__ == "__main__":
    print("🚀 統合会話システム包括テスト開始")
    print(f"📅 テスト実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. 統合システム基本テスト
    test_integrated_system()

    # 2. LINE Bot統合テスト
    test_line_bot_integration()

    print("\n🎉 全テスト完了！")
