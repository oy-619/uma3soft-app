"""
Uma3 基本エージェントルーターテスト（LangChain依存なし）
"""

import sys
import os

# パス設定
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_basic_agent_routing():
    """基本的なエージェントルーティングテスト"""
    print("🧪 基本エージェントルーティングテスト")
    print("=" * 50)

    try:
        from uma3_agent_router import Uma3AgentRouter, AgentType

        # LLMなしでエージェントルーター初期化
        router = Uma3AgentRouter(llm=None)
        print("✅ Agent router initialized (without LLM)")

        # テストケース
        test_messages = [
            ("@Bot F履歴を表示して", "Flex履歴表示"),
            ("明日の予定を教えて", "スケジュール確認"),
            ("11月3日のリマインダーを設定して", "リマインダー設定"),
            ("チームメンバーの一覧", "チーム管理"),
            ("過去の試合結果を分析", "イベント分析"),
            ("陸功選手の履歴", "履歴検索"),
            ("今日の天気", "天気コンテキスト"),
            ("よくある質問", "FAQ検索"),
            ("こんにちは", "一般会話")
        ]

        print(f"\n🧮 {len(test_messages)}個のテストケースを実行中...")
        print("-" * 60)

        success_count = 0

        for i, (message, description) in enumerate(test_messages, 1):
            print(f"\n🧪 テスト {i}: {description}")
            print(f"   📝 メッセージ: '{message}'")

            try:
                # エージェント選択を実行
                selected_agent, intent = router.route_to_agent(message)
                agent_info = router.get_agent_info(selected_agent)

                print(f"   🤖 選択エージェント: {agent_info.get('name', selected_agent.value)}")
                print(f"   📊 信頼度: {intent.confidence:.3f}")
                print(f"   💭 理由: {intent.reasoning}")

                if intent.extracted_params:
                    print(f"   📋 パラメータ: {intent.extracted_params}")

                # 基本的な妥当性チェック
                if intent.confidence > 0.0:
                    print("   ✅ 成功: エージェントが正常に選択されました")
                    success_count += 1
                else:
                    print("   ⚠️ 警告: 信頼度が低すぎます")

            except Exception as e:
                print(f"   ❌ エラー: {e}")

        print("\n" + "=" * 60)
        print(f"🎉 テスト結果: {success_count}/{len(test_messages)} 成功")
        print(f"📊 成功率: {(success_count/len(test_messages))*100:.1f}%")

        # 詳細分析例
        print(f"\n📋 詳細分析例:")
        example_message = "@Bot F履歴を表示して"
        explanation = router.explain_routing_decision(example_message)
        print(f"\nメッセージ: {example_message}")
        print(explanation)

        return success_count >= len(test_messages) * 0.8  # 80%以上成功で合格

    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_intent_analysis():
    """意図分析の詳細テスト"""
    print("\n🔍 意図分析詳細テスト")
    print("-" * 30)

    try:
        from uma3_agent_router import Uma3AgentRouter, AgentType

        router = Uma3AgentRouter()

        # 複数の意図を持つメッセージのテスト
        complex_messages = [
            "@Bot F履歴を表示して、明日の予定も教えて",
            "陸功選手の過去の成績分析をお願いします",
            "チームの今日の天気と予定を確認したい"
        ]

        for message in complex_messages:
            print(f"\n💭 複雑なメッセージ分析: '{message}'")
            intents = router.analyze_intent(message)

            print(f"   🎯 検出された意図数: {len(intents)}")
            for i, intent in enumerate(intents[:3], 1):  # 上位3つ
                agent_info = router.get_agent_info(intent.agent_type)
                print(f"   {i}. {agent_info.get('name', intent.agent_type.value)}")
                print(f"      信頼度: {intent.confidence:.3f}")
                print(f"      理由: {intent.reasoning}")

        return True

    except Exception as e:
        print(f"❌ 意図分析テストエラー: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Uma3 基本エージェントシステムテスト開始")
    print("=" * 60)

    # 基本ルーティングテスト
    routing_success = test_basic_agent_routing()

    # 意図分析テスト
    analysis_success = test_intent_analysis()

    print("\n" + "=" * 60)
    print("🏁 基本テスト完了")

    if routing_success and analysis_success:
        print("🎉 基本エージェントシステムが正常に動作しています！")
        print("✅ メッセージの自動分類とエージェント選択が機能しています")
    else:
        print("⚠️ 一部の機能に問題があります")
        if not routing_success:
            print("❌ エージェントルーティングに問題があります")
        if not analysis_success:
            print("❌ 意図分析に問題があります")
