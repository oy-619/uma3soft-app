#!/usr/bin/env python3
"""
天気情報統合機能のテスト
"""

import os
import sys
from datetime import datetime

# パスの追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_weather_integration():
    """天気情報統合機能のテスト"""
    print("=" * 60)
    print("🌤️ 天気情報統合機能テスト")
    print("=" * 60)

    try:
        # 1. カスタムツールのテスト
        print("\n1️⃣ WeatherContextTool単体テスト")
        print("-" * 40)

        from uma3_custom_tools import WeatherContextTool

        weather_tool = WeatherContextTool()

        # テストクエリ
        test_queries = [
            "今日の天気を教えて",
            "東京の天気はどうですか？",
            "大阪の気温を知りたい",
            "明日は雨が降りますか？"
        ]

        for i, query in enumerate(test_queries, 1):
            print(f"   {i}. クエリ: '{query}'")
            try:
                result = weather_tool._run(query)
                print(f"      結果: {result[:100]}...")
                print()
            except Exception as e:
                print(f"      エラー: {e}")
                print()

        # 2. 統合システムでのテスト
        print("\n2️⃣ 統合システムでの天気機能テスト")
        print("-" * 40)

        from integrated_conversation_system import IntegratedConversationSystem

        # システム初期化
        chroma_persist_dir = "db/chroma_store"
        conversation_db_path = "db/conversation_history.db"

        integrated_system = IntegratedConversationSystem(
            chroma_persist_directory=chroma_persist_dir,
            conversation_db_path=conversation_db_path
        )

        print("✅ 統合システム初期化完了")

        # 天気質問のテスト
        test_user = "weather_test_user"
        weather_questions = [
            "今日の天気はどうですか？",
            "東京の気温を教えて",
            "明日の天気予報が知りたい",
            "雨は降りそうですか？",
            "週間天気予報を見たい"
        ]

        for i, question in enumerate(weather_questions, 1):
            print(f"\n   {i}. 質問: '{question}'")

            try:
                response = integrated_system.generate_integrated_response(
                    test_user, question
                )

                print(f"      応答タイプ: {response.get('response_type', 'normal')}")
                print(f"      応答内容: {response['response'][:200]}...")
                print(f"      コンテキスト: {response['context_used']}")

            except Exception as e:
                print(f"      エラー: {e}")

        # 3. 天気以外の質問との比較
        print("\n3️⃣ 天気以外の質問との比較テスト")
        print("-" * 40)

        non_weather_questions = [
            "こんにちは",
            "今週の予定を教えて",
            "野球について教えて"
        ]

        for i, question in enumerate(non_weather_questions, 1):
            print(f"\n   {i}. 質問: '{question}'")

            try:
                response = integrated_system.generate_integrated_response(
                    test_user, question
                )

                print(f"      応答タイプ: {response.get('response_type', 'normal')}")
                print(f"      天気判定: {'Yes' if response.get('response_type') == 'weather_info' else 'No'}")

            except Exception as e:
                print(f"      エラー: {e}")

        print("\n=" * 60)
        print("✅ 天気情報統合機能テスト完了")
        print("=" * 60)

    except Exception as e:
        print(f"❌ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_weather_integration()
