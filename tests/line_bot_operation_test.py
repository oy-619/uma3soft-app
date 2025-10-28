"""
改善されたuma3.py LINE Botシステムの運用テスト
"""

import os
import sys
import time
from datetime import datetime

def pre_flight_check():
    """運用テスト前の事前チェック"""
    print("🔍 LINE Bot運用テスト事前チェック")
    print("=" * 60)

    checks = []

    # 1. 必要なファイルの存在確認
    required_files = [
        '../src/uma3.py',
        '../db/conversation_history.db',
        'improved_response_system.py',
        '../.env'
    ]

    for file_path in required_files:
        if os.path.exists(file_path):
            checks.append((f"✅ {file_path}", True))
        else:
            checks.append((f"❌ {file_path}", False))

    # 2. 環境変数チェック
    from dotenv import load_dotenv
    env_path = '../.env'
    if os.path.exists(env_path):
        load_dotenv(env_path)

        env_vars = [
            'LINE_CHANNEL_ACCESS_TOKEN',
            'LINE_CHANNEL_SECRET',
            'OPENAI_API_KEY'
        ]

        for var in env_vars:
            if os.getenv(var):
                checks.append((f"✅ {var} 設定済み", True))
            else:
                checks.append((f"❌ {var} 未設定", False))

    # 3. Pythonモジュール動作チェック
    try:
        sys.path.insert(0, '.')
        from improved_response_system import ImprovedResponseGenerator
        generator = ImprovedResponseGenerator('../db/conversation_history.db')
        test_result = generator.generate_improved_response('TEST_USER', 'こんにちは')
        checks.append((f"✅ ImprovedResponseGenerator動作確認", True))
        checks.append((f"   テスト応答: '{test_result['response'][:30]}...'", True))
        checks.append((f"   品質スコア: {test_result['quality_score']:.1f}/5.0", True))
    except Exception as e:
        checks.append((f"❌ ImprovedResponseGenerator: {e}", False))

    # 結果表示
    print("\n📋 チェック結果:")
    all_passed = True
    for check, passed in checks:
        print(f"   {check}")
        if not passed:
            all_passed = False

    print(f"\n🎯 総合結果: {'✅ 全てOK' if all_passed else '❌ 問題あり'}")
    return all_passed

def create_line_bot_test_scenarios():
    """LINE Bot運用テストシナリオを作成"""

    scenarios = [
        {
            "id": 1,
            "name": "初回挨拶・自己紹介テスト",
            "user_inputs": [
                "こんにちは！初めまして。",
                "私の名前は山田太郎です。よろしくお願いします。"
            ],
            "expected_improvements": [
                "自然な挨拶応答",
                "ユーザー名の認識と記憶",
                "親しみやすい口調"
            ]
        },
        {
            "id": 2,
            "name": "感謝・お礼表現テスト",
            "user_inputs": [
                "ありがとうございました！",
                "助かりました。感謝します。"
            ],
            "expected_improvements": [
                "適切な感謝応答",
                "継続的関係性の示唆",
                "温かみのある返答"
            ]
        },
        {
            "id": 3,
            "name": "技術質問・専門的内容テスト",
            "user_inputs": [
                "Pythonプログラミングについて教えてください",
                "データ分析の方法を知りたいです"
            ],
            "expected_improvements": [
                "技術的トピックの理解",
                "適切な情報提供",
                "ユーザーレベルに応じた説明"
            ]
        },
        {
            "id": 4,
            "name": "継続的会話・記憶テスト",
            "user_inputs": [
                "前回話したプログラミングの件、覚えてる？",
                "山田のことを覚えていますか？"
            ],
            "expected_improvements": [
                "過去の会話内容の参照",
                "ユーザー情報の記憶",
                "一貫した対話体験"
            ]
        },
        {
            "id": 5,
            "name": "エラー・フォールバックテスト",
            "user_inputs": [
                "あいうえおかきくけこ",  # 意味不明な入力
                "１２３４５６７８９０"   # 数字のみ
            ],
            "expected_improvements": [
                "適切なエラーハンドリング",
                "ユーザーフレンドリーな応答",
                "システムの安定性"
            ]
        }
    ]

    return scenarios

def generate_ngrok_test_guide():
    """ngrokを使用したLINE Bot運用テストガイド"""

    guide = """
🚀 LINE Bot運用テスト実行手順

1. 🔧 ngrok起動
   VS Code ターミナルで以下を実行：
   > Clean Start ngrok (Lesson25) タスクを実行
   または
   > cd Lesson25/uma3soft-app && ngrok http 5000 --region=jp

2. 🌐 ngrok URL確認
   ngrok起動後に表示されるHTTPS URLをコピー
   例: https://abc123.ngrok-free.app

3. 📱 LINE Developers設定更新
   - LINE Developers Console にアクセス
   - Webhook URL を更新: https://abc123.ngrok-free.app/callback
   - Webhook の使用をオンに設定

4. 🤖 uma3.py起動
   新しいターミナルで：
   > cd Lesson25/uma3soft-app/src && python uma3.py

5. 📱 LINE アプリでテスト実行
   各テストシナリオを順番に実行

6. 📊 ログ監視
   uma3.pyの実行ログで以下を確認：
   - [ENHANCED] 改善システムの動作
   - [QUALITY] 品質スコアの表示
   - [TEMPLATE] テンプレート使用状況
   - [FALLBACK] フォールバック発生状況

7. 📈 結果記録
   各シナリオの実行結果を記録
   - 応答の自然さ
   - ユーザー名の認識
   - 記憶機能の動作
   - 品質向上の確認
"""

    return guide

def start_operation_test():
    """運用テスト開始"""
    print("🎯 LINE Bot改善システム運用テスト開始")
    print(f"📅 開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # 事前チェック
    if not pre_flight_check():
        print("\n❌ 事前チェックに失敗しました。問題を解決してから再実行してください。")
        return False

    print("\n" + "="*70)

    # テストシナリオ表示
    scenarios = create_line_bot_test_scenarios()
    print("\n📝 運用テストシナリオ:")
    for scenario in scenarios:
        print(f"\n{scenario['id']}. {scenario['name']}")
        print("   入力例:")
        for inp in scenario['user_inputs']:
            print(f"     📱 '{inp}'")
        print("   期待する改善:")
        for exp in scenario['expected_improvements']:
            print(f"     ✅ {exp}")

    # 実行手順表示
    print("\n" + "="*70)
    guide = generate_ngrok_test_guide()
    print(guide)

    print("\n🎉 運用テスト準備完了！")
    print("上記手順に従ってLINE Botの運用テストを実行してください。")
    print("\n💡 テスト中のポイント:")
    print("   - 改善システムの品質スコア3.0以上の応答に注目")
    print("   - ユーザー名のパーソナライズ動作確認")
    print("   - 自然な日本語応答の確認")
    print("   - エラー時のフォールバック動作確認")

    return True

def main():
    """メイン処理"""
    success = start_operation_test()

    if success:
        print(f"\n✅ 運用テスト準備完了")
        print("🚀 LINE Botで実際にテストを開始してください！")
    else:
        print(f"\n❌ 運用テスト準備に問題があります")

if __name__ == "__main__":
    main()
