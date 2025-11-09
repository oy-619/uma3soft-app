"""
【天気情報付きリマインダーテストスクリプト】
天気情報統合機能の動作確認用
"""

import sys
import os
from datetime import datetime, timedelta

# パスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_weather_reminder():
    """天気情報付きリマインダー機能のテスト"""
    print("🧪 天気情報付きリマインダー機能のテスト開始")

    try:
        # WeatherContextToolのテスト
        print("\n1. WeatherContextTool 単体テスト")
        from uma3_custom_tools import WeatherContextTool

        weather_tool = WeatherContextTool()

        # テストケース1: 基本的な天気情報取得
        test_query1 = "東京の明日の天気"
        result1 = weather_tool._run(query=test_query1)
        print(f"✅ 基本テスト結果: {result1[:100]}...")

        # テストケース2: イベント情報から場所・日時抽出
        test_query2 = """
        [ノート] 2025/10/30(火) 馬三ソフト 東京都大会
        会場：代々木体育館
        練習試合のため、屋外グラウンドでの開催
        """
        result2 = weather_tool._run(query=test_query2, event_date="2025-10-30")
        print(f"✅ イベント情報テスト結果: {result2[:200]}...")

    except Exception as e:
        print(f"❌ WeatherContextTool テストエラー: {e}")

    try:
        # リマインダースケジュール機能のテスト
        print("\n2. リマインダー天気情報統合テスト")
        from reminder_schedule import get_weather_for_event, format_reminder_message

        # テストイベント
        test_event_content = """
        [ノート] 馬三ソフト 東京都大会
        会場：代々木体育館
        日時：2025/10/30(火) 10:00〜
        屋外での練習試合
        """

        test_event_date = datetime(2025, 10, 30).date()

        # 天気情報取得テスト
        weather_info = get_weather_for_event(test_event_content, test_event_date)
        print(f"✅ イベント天気情報: {weather_info[:150]}...")

        # リマインダーメッセージフォーマットテスト
        test_notes = [{
            'content': test_event_content,
            'date': test_event_date,
            'days_until': 1,
            'is_input_deadline': False,
            'reminder_type': 'event_date'
        }]

        formatted_message = format_reminder_message(test_notes, "day_before")
        print(f"✅ フォーマット済みメッセージ:\n{formatted_message[:300]}...")

    except Exception as e:
        print(f"❌ リマインダー統合テストエラー: {e}")
        import traceback
        traceback.print_exc()

    try:
        # イベント情報抽出機能のテスト
        print("\n3. イベント情報抽出テスト")
        from uma3_custom_tools import WeatherContextTool

        weather_tool = WeatherContextTool()

        test_event_texts = [
            """
            [ノート] 大阪府大会
            会場：大阪城ホール
            日時：2025/11/15(土) 9:00〜17:00
            屋外競技場での開催
            """,
            """
            [ノート] 名古屋練習試合
            場所：名古屋ドーム近くのグラウンド
            2025/12/01(日) 13:00キックオフ
            雨天決行
            """,
            """
            [ノート] 福岡遠征
            開催地：福岡県北九州市
            12月20日 午前10時開始
            屋外フィールドでの試合
            """
        ]

        for i, test_text in enumerate(test_event_texts, 1):
            print(f"\n📋 テストケース {i}:")
            event_info = weather_tool._extract_event_info(test_text)
            print(f"  場所: {event_info.get('location', 'なし')}")
            print(f"  会場: {event_info.get('venue', 'なし')}")
            print(f"  日付: {event_info.get('date', 'なし')}")
            print(f"  イベント名: {event_info.get('event_name', 'なし')}")

    except Exception as e:
        print(f"❌ イベント情報抽出テストエラー: {e}")
        import traceback
        traceback.print_exc()

    print("\n✅ 天気情報付きリマインダー機能テスト完了")


def test_weather_patterns():
    """天気情報取得パターンのテスト"""
    print("\n🌤️ 天気情報取得パターンテスト")

    try:
        from uma3_custom_tools import WeatherContextTool

        weather_tool = WeatherContextTool()

        # 各地域の天気情報取得テスト
        test_locations = ["東京", "大阪", "名古屋", "福岡", "札幌"]

        for location in test_locations:
            print(f"\n📍 {location}の天気情報テスト:")
            try:
                result = weather_tool._run(query=f"{location}の天気", location=location)
                print(f"  ✅ 取得成功: {len(result)}文字")

                # 主要情報の確認
                if "気温" in result:
                    print("  🌡️ 気温情報: あり")
                if "降水確率" in result:
                    print("  ☔ 降水確率: あり")
                if "湿度" in result:
                    print("  💧 湿度情報: あり")
                if "風" in result:
                    print("  💨 風情報: あり")

            except Exception as e:
                print(f"  ❌ エラー: {e}")

    except Exception as e:
        print(f"❌ 天気パターンテストエラー: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("🌤️ 天気情報付きリマインダー統合テストスクリプト")
    print("=" * 60)

    test_weather_reminder()
    test_weather_patterns()

    print("\n" + "=" * 60)
    print("🎯 テスト完了 - 実際のLINE Botでの動作確認をお試しください")
    print("=" * 60)
