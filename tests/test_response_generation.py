"""
実際の応答生成テスト
統合システムで実際にどのような応答が生成されるかテスト
"""

import os
import sys
from datetime import datetime

# パスを追加
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), 'src')
sys.path.insert(0, src_dir)

def test_actual_response_generation():
    """実際の応答生成をテスト"""
    print("=" * 60)
    print("実際の応答生成テスト")
    print("=" * 60)

    # OpenAI APIキーの確認
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ OPENAI_API_KEYが設定されていません。")
        print("⚠️ 実際の応答生成はテストできませんが、プロンプト生成をテストします。")
        test_without_llm = True
    else:
        print("✅ OPENAI_API_KEYが設定されています。")
        test_without_llm = False

    try:
        from integrated_conversation_system import IntegratedConversationSystem
        from langchain_openai import ChatOpenAI

        # システム初期化
        system = IntegratedConversationSystem(
            'Lesson25/uma3soft-app/db/chroma_store',
            'Lesson25/uma3soft-app/db/conversation_history.db'
        )

        # 実際のユーザーIDを使用
        test_user_id = "U2b1bb2a638b714727085c7317a3b54a0"

        # テストケース
        test_cases = [
            "前回の話を覚えてる？",
            "キャプテンの件、どうだったっけ？",
            "なおまさんの話、覚えてる？",
            "今度は違う質問だけど、今日の天気は？"
        ]

        if not test_without_llm:
            llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.3,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )

        for i, test_message in enumerate(test_cases, 1):
            print(f"\n{i}. テストケース: '{test_message}'")
            print("-" * 50)

            try:
                if test_without_llm:
                    # プロンプト生成のみテスト
                    context_prompt = system.context_generator.generate_contextual_response_prompt(
                        test_user_id, test_message, max_history_items=3
                    )

                    print("📝 生成されたプロンプト:")
                    print(context_prompt[:500] + "..." if len(context_prompt) > 500 else context_prompt)
                    print(f"プロンプト全体の長さ: {len(context_prompt)}文字")

                    # 履歴参照の確認
                    if "会話回数" in context_prompt:
                        print("✅ 会話回数情報が含まれています")
                    if "最近の会話履歴" in context_prompt:
                        print("✅ 最近の会話履歴が含まれています")
                    if "キャプテン" in context_prompt:
                        print("✅ 過去の会話内容（キャプテン）が参照されています")
                    if "なおま" in context_prompt:
                        print("✅ 過去の会話内容（なおま）が参照されています")
                else:
                    # 実際に応答生成
                    result = system.generate_integrated_response(
                        test_user_id, test_message, llm
                    )

                    if "error" in result:
                        print(f"❌ エラー: {result.get('error_message', 'Unknown error')}")
                    else:
                        response = result["response"]
                        context_info = result.get("context_used", {})

                        print(f"🤖 応答: {response}")
                        print(f"📊 コンテキスト情報:")
                        print(f"   - ChromaDB検索結果: {context_info.get('chroma_results', 0)}件")
                        print(f"   - 会話履歴: {context_info.get('conversation_history', 0)}件")
                        print(f"   - 関連会話: {context_info.get('relevant_conversations', 0)}件")

                        # 履歴参照の確認
                        if "キャプテン" in response or "なおま" in response:
                            print("✅ 過去の会話内容が応答に反映されています")
                        else:
                            print("⚠️ 過去の会話内容が応答に十分反映されていない可能性があります")

                        user_profile = context_info.get('user_profile', {})
                        if user_profile and user_profile.get('conversation_count', 0) > 0:
                            print(f"✅ ユーザープロフィールが活用されています（会話数: {user_profile['conversation_count']}）")

            except Exception as e:
                print(f"❌ テストケース{i}でエラー: {e}")
                import traceback
                traceback.print_exc()

    except Exception as e:
        print(f"❌ 応答生成テストでエラー: {e}")
        import traceback
        traceback.print_exc()


def test_context_quality():
    """コンテキストの質をテスト"""
    print(f"\n🔍 コンテキスト品質分析")

    try:
        from integrated_conversation_system import IntegratedConversationSystem

        system = IntegratedConversationSystem(
            'Lesson25/uma3soft-app/db/chroma_store',
            'Lesson25/uma3soft-app/db/conversation_history.db'
        )

        test_user_id = "U2b1bb2a638b714727085c7317a3b54a0"
        test_query = "前回の話、覚えてる？"

        # 個別のコンポーネントをテスト
        print("1. ユーザープロフィール:")
        profile = system.history_manager.get_user_profile(test_user_id)
        print(f"   会話回数: {profile['conversation_count']}")
        print(f"   興味・関心: {profile['interests']}")

        print("\n2. 最近の会話:")
        recent = system.history_manager.get_recent_conversations(test_user_id, limit=3)
        for i, (human, ai, timestamp) in enumerate(recent):
            print(f"   {i+1}. [{timestamp.strftime('%m/%d %H:%M')}]")
            print(f"      👤: {human[:60]}...")
            print(f"      🤖: {ai[:60]}...")

        print("\n3. 関連会話検索:")
        relevant = system.history_manager.search_conversations(test_user_id, test_query, limit=3)
        for i, conv in enumerate(relevant):
            msg_type = "👤" if conv["message_type"] == "human" else "🤖"
            print(f"   {i+1}. {msg_type} {conv['content'][:60]}...")

        print("\n4. ChromaDB検索:")
        chroma_results = system.chroma_improver.schedule_aware_search(test_query, k=3)
        for i, doc in enumerate(chroma_results):
            print(f"   {i+1}. {doc.page_content[:60]}...")

        print(f"\n📊 総合評価:")
        print(f"   - ユーザープロフィール: {'✅' if profile['conversation_count'] > 0 else '❌'}")
        print(f"   - 最近の会話: {'✅' if len(recent) > 0 else '❌'}")
        print(f"   - 関連会話: {'✅' if len(relevant) > 0 else '❌'}")
        print(f"   - ChromaDB検索: {'✅' if len(chroma_results) > 0 else '❌'}")

    except Exception as e:
        print(f"❌ コンテキスト品質分析エラー: {e}")


if __name__ == "__main__":
    print("🚀 実際の応答生成テスト開始")
    print(f"📅 テスト実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    test_actual_response_generation()
    test_context_quality()

    print("\n🎉 テスト完了！")
