"""
uma3.pyに改善された応答システムを統合するためのアップグレードモジュール
"""

import os
import sys
from datetime import datetime

# パス設定
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), 'src')
sys.path.insert(0, src_dir)

class Uma3ResponseUpgrader:
    """uma3.pyの応答システムをアップグレード"""

    def __init__(self):
        self.uma3_path = os.path.join(src_dir, 'uma3.py')
        print(f"[UPGRADER] uma3.py path: {self.uma3_path}")

    def backup_uma3(self):
        """現在のuma3.pyをバックアップ"""
        backup_path = self.uma3_path + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        try:
            import shutil
            shutil.copy2(self.uma3_path, backup_path)
            print(f"[BACKUP] ✅ Backup created: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"[ERROR] Failed to create backup: {e}")
            return None

    def create_enhanced_uma3_integration(self):
        """拡張された応答システム統合コードを生成"""

        integration_code = '''
# === 改善された応答システム統合 ===
# improved_response_systemからImprovedResponseGeneratorをインポート
import sys
import os
tests_path = os.path.join(os.path.dirname(__file__), '..', 'tests')
sys.path.insert(0, tests_path)

try:
    from improved_response_system import ImprovedResponseGenerator
    improved_response_generator = ImprovedResponseGenerator(
        os.path.join(os.path.dirname(__file__), '..', 'db', 'conversation_history.db')
    )
    print("[ENHANCED] Improved response generator loaded successfully")
except Exception as e:
    print(f"[WARNING] Could not load improved response generator: {e}")
    improved_response_generator = None

def generate_enhanced_line_response(user_id: str, user_message: str, llm) -> Dict:
    """LINE Bot用の拡張応答生成"""

    # 1. 改善された応答システムを試行
    if improved_response_generator:
        try:
            improved_result = improved_response_generator.generate_improved_response(user_id, user_message)

            # 高品質な応答が生成された場合
            if improved_result.get('quality_score', 0) >= 3.0:
                print(f"[ENHANCED] High quality response generated (score: {improved_result['quality_score']:.1f})")
                return {
                    'response': improved_result['response'],
                    'response_type': 'enhanced_template',
                    'quality_score': improved_result['quality_score'],
                    'source': 'improved_system'
                }
            else:
                print(f"[ENHANCED] Low quality response, trying integrated system (score: {improved_result['quality_score']:.1f})")

        except Exception as e:
            print(f"[WARNING] Improved response generation failed: {e}")

    # 2. 統合システムへのフォールバック
    try:
        integrated_result = integrated_conversation_system.generate_integrated_response(
            user_id, user_message, llm
        )

        if "error" not in integrated_result:
            return {
                'response': integrated_result['response'],
                'response_type': 'integrated_system',
                'context_used': integrated_result.get('context_used', {}),
                'source': 'integrated_system'
            }
        else:
            print(f"[WARNING] Integrated system error: {integrated_result.get('error_message', 'Unknown')}")

    except Exception as e:
        print(f"[WARNING] Integrated system failed: {e}")

    # 3. 基本ChromaDB検索へのフォールバック
    try:
        results = chroma_improver.schedule_aware_search(user_message, k=6, score_threshold=0.5)

        if results:
            context = "\\n".join([doc.page_content for doc in results])

            prompt_template = ChatPromptTemplate.from_messages([
                (
                    "system",
                    """あなたは優秀なアシスタントです。以下の関連情報を参考にして、
                    ユーザーの質問に自然で親しみやすく答えてください。
                    回答時はスマートフォンで読みやすいように、適度に改行を入れてください。

                    ---
                    {context}
                    ---""",
                ),
                ("human", "{input}"),
            ])

            formatted_prompt = prompt_template.format_messages(
                context=context, input=user_message
            )
            response = llm.invoke(formatted_prompt)

            return {
                'response': response.content,
                'response_type': 'chroma_fallback',
                'source': 'chroma_search'
            }
    except Exception as e:
        print(f"[WARNING] ChromaDB fallback failed: {e}")

    # 4. 最終フォールバック
    return {
        'response': "申し訳ございません。少し時間をおいて、もう一度お試しください。",
        'response_type': 'final_fallback',
        'source': 'fallback'
    }
'''

        return integration_code

    def create_backup_and_plan(self):
        """バックアップとアップグレード計画を作成"""
        print("🚀 uma3.py アップグレード計画")
        print("=" * 60)

        # バックアップ作成
        backup_path = self.backup_uma3()

        if not backup_path:
            print("❌ バックアップ作成に失敗しました。手動でバックアップを作成してください。")
            return

        print(f"\n📋 アップグレード手順:")
        print("1. ✅ バックアップ作成完了")
        print("2. 🔧 handle_message関数の修正が必要")
        print("3. 📝 統合コードの追加")
        print("4. 🧪 動作テスト")
        print("5. 🚀 LINE Bot運用テスト")

        print(f"\n💡 推奨される修正方法:")
        print("手動での慎重な統合を推奨します。以下の理由から：")
        print("   - uma3.pyは複雑な本番システム")
        print("   - 既存の動作を維持する必要がある")
        print("   - 段階的なテストが必要")

        # 統合コードの生成
        integration_code = self.create_enhanced_uma3_integration()

        integration_file = os.path.join(current_dir, 'uma3_enhancement_integration.py')
        with open(integration_file, 'w', encoding='utf-8') as f:
            f.write(f'''"""
uma3.py enhancement integration code
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This file contains the integration code to enhance uma3.py with improved response system.
Copy the relevant parts to uma3.py manually after careful review.
"""

{integration_code}
''')

        print(f"\n📄 統合コードを生成しました: {integration_file}")

        return {
            'backup_path': backup_path,
            'integration_file': integration_file,
            'status': 'ready_for_manual_integration'
        }

def create_test_scenario_for_line_bot():
    """LINE Bot運用テスト用のシナリオを作成"""

    scenarios = [
        {
            "scenario_name": "初回挨拶テスト",
            "user_input": "こんにちは！初めまして。",
            "expected_behavior": [
                "自然な挨拶応答",
                "ユーザー名の取得試行",
                "会話履歴への保存"
            ]
        },
        {
            "scenario_name": "自己紹介テスト",
            "user_input": "私の名前は田中です。プログラミングが好きです。",
            "expected_behavior": [
                "名前の認識と記憶",
                "興味・関心の学習",
                "パーソナライズされた応答"
            ]
        },
        {
            "scenario_name": "記憶テスト",
            "user_input": "前回話したプログラミングの件、覚えてる？",
            "expected_behavior": [
                "過去の会話内容を参照",
                "記憶していることを示す応答",
                "関連する情報の提供"
            ]
        },
        {
            "scenario_name": "技術質問テスト",
            "user_input": "Pythonでデータ分析をしていますが、どう思いますか？",
            "expected_behavior": [
                "技術的なトピックの認識",
                "ユーザーの興味に応じた応答",
                "建設的なフィードバック"
            ]
        },
        {
            "scenario_name": "感謝表現テスト",
            "user_input": "ありがとうございました！",
            "expected_behavior": [
                "感謝表現の認識",
                "適切な返答",
                "継続的な関係性の示唆"
            ]
        }
    ]

    return scenarios

def test_integration_locally():
    """ローカルでの統合テスト"""
    print("\n🧪 ローカル統合テスト")
    print("-" * 40)

    try:
        # 改善されたシステムをテスト
        from improved_response_system import ImprovedResponseGenerator

        db_path = os.path.join(os.path.dirname(current_dir), 'db', 'conversation_history.db')
        print(f"[TEST] Database path: {db_path}")
        generator = ImprovedResponseGenerator(db_path)

        test_user_id = "INTEGRATION_TEST_USER"
        test_messages = [
            "こんにちは！",
            "ありがとうございました"
        ]

        for i, message in enumerate(test_messages, 1):
            result = generator.generate_improved_response(test_user_id, message)
            print(f"{i}. '{message}' → '{result['response']}'")
            print(f"   品質スコア: {result['quality_score']:.1f}/5.0")

        print("✅ ローカル統合テスト成功")
        return True

    except Exception as e:
        print(f"❌ ローカル統合テスト失敗: {e}")
        return False

def main():
    """メイン処理"""
    print("🎯 uma3.py 改善システム統合プロセス")
    print(f"📅 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # 1. アップグレード計画作成
    upgrader = Uma3ResponseUpgrader()
    upgrade_result = upgrader.create_backup_and_plan()

    # 2. テストシナリオ生成
    print(f"\n📝 LINE Bot運用テストシナリオ")
    print("-" * 40)

    scenarios = create_test_scenario_for_line_bot()

    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['scenario_name']}")
        print(f"   入力: '{scenario['user_input']}'")
        print(f"   期待: {', '.join(scenario['expected_behavior'])}")
        print()

    # 3. ローカル統合テスト
    local_test_success = test_integration_locally()

    # 4. 次のステップ
    print(f"\n🚀 次のステップ")
    print("-" * 40)

    if local_test_success and upgrade_result:
        print("✅ 統合準備完了！以下の手順で進めてください：")
        print()
        print("1. 📄 統合コードの確認")
        print(f"   {upgrade_result['integration_file']}")
        print()
        print("2. 🔧 uma3.pyの手動統合")
        print("   - handle_message関数に拡張システム呼び出しを追加")
        print("   - 既存の動作を維持しながら段階的に統合")
        print()
        print("3. 🧪 開発環境でのテスト")
        print("   - ngrok起動")
        print("   - LINE Botでの動作確認")
        print("   - 各テストシナリオの実行")
        print()
        print("4. 🚀 本番環境へのデプロイ")
        print("   - 慎重な段階的リリース")
        print("   - ユーザーフィードバックの収集")
    else:
        print("❌ 統合準備に問題があります。ログを確認してください。")

    print(f"\n🎉 統合プロセス完了！")

if __name__ == "__main__":
    main()
