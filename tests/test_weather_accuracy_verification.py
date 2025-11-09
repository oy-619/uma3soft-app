#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天気情報の正確性と表示内容の検証テスト
"""

import sys
import os
import json
from datetime import datetime, timedelta

# プロジェクトのパスを追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

def test_weather_accuracy_and_display():
    """天気情報の正確性と表示内容をテスト"""
    print("🌤️ 天気情報正確性・表示内容検証テスト")
    print("=" * 60)

    try:
        from enhanced_reminder_messages import generate_weather_flex_card
        import sys; import os; sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'archive')); from openweather_service import get_weather_for_location

        # 2025年11月1日のテストイベント
        test_event = {
            "content": "[ノート] 11月1日(金) 重要会議\n会場: 代々木公園管理事務所\n時間: 14:00-16:00\n資料準備必要",
            "date": datetime(2025, 11, 1).date(),
            "days_until": 2,
            "is_input_deadline": False
        }

        print("📋 テスト対象イベント:")
        print(f"  📅 日付: {test_event['date']}")
        content_lines = test_event['content'].split('\n')
        print(f"  📍 内容: {content_lines[0]}")
        print(f"  🏢 会場: 代々木公園管理事務所")

        print("\n--- 1. 直接天気API呼び出しテスト ---")
        weather_data = get_weather_for_location("東京都", "代々木公園管理事務所", 2)

        if weather_data:
            print("✅ 天気データ取得成功")
            print(f"  🌡️ 気温: {weather_data.get('temperature', 'N/A')}°C")
            print(f"  💧 湿度: {weather_data.get('humidity', 'N/A')}%")
            print(f"  ☔ 降水確率: {weather_data.get('rain_probability', 'N/A')}%")
            print(f"  💨 風速: {weather_data.get('wind_speed', 'N/A')}km/h")
            print(f"  ☁️ 天気: {weather_data.get('description', 'N/A')}")
            print(f"  📊 データソース: {weather_data.get('data_source', 'OpenWeatherMap API')}")

            if weather_data.get('is_mock_data', False):
                print("  ⚠️ 注意: これはテスト用のモックデータです")
            else:
                print("  ✅ 実際のAPIデータです")
        else:
            print("❌ 天気データ取得失敗")

        print("\n--- 2. Flex Message天気カード生成テスト ---")
        weather_flex = generate_weather_flex_card(test_event)

        if weather_flex:
            print("✅ Flex Message生成成功")

            # 表示内容の確認
            contents = weather_flex.get("contents", {})
            body = contents.get("body", {})
            body_contents = body.get("contents", [])
            footer = contents.get("footer", {})
            footer_contents = footer.get("contents", [])

            print("\n📱 Flex Message表示内容:")
            print(f"  Alt Text: {weather_flex.get('altText', '不明')}")

            # ヘッダー確認
            header = contents.get("header", {})
            if header:
                header_contents = header.get("contents", [])
                if len(header_contents) > 1:
                    location_text = header_contents[1].get("text", "")
                    print(f"  📍 ヘッダー地域: {location_text}")

            # ボディ内容確認
            for content in body_contents:
                if content.get("type") == "text":
                    text = content.get("text", "")
                    if "開催場所" in text:
                        print(f"  🏢 {text}")
                    elif "対象地域" in text:
                        print(f"  🗺️ {text}")

            # フッター確認
            print("\n📄 フッター情報:")
            for content in footer_contents:
                if content.get("type") == "text":
                    text = content.get("text", "")
                    print(f"    {text}")

            # JSONファイル保存
            output_file = "weather_accuracy_test_result.json"
            output_path = os.path.join(project_root, "tests", output_file)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump({
                    "test_date": datetime.now().isoformat(),
                    "event_info": test_event,
                    "weather_data": weather_data,
                    "flex_message": weather_flex
                }, f, ensure_ascii=False, indent=2, default=str)

            print(f"\n💾 詳細結果保存: {output_file}")

        else:
            print("❌ Flex Message生成失敗")

        print("\n--- 3. 天気情報の信頼性について ---")
        print("📊 現在の状況:")

        # API キー設定確認
        import sys; import os; sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'archive')); from openweather_service import OpenWeatherMapService
        service = OpenWeatherMapService()

        if service.api_key == "your_api_key_here":
            print("  ⚠️ OpenWeatherMap API キーが未設定")
            print("  📝 現在はテスト用のシミュレーションデータを使用")
            print("  🎯 季節感のある現実的なデータを生成")
            print("  ❌ 実際の気象観測データではありません")
        else:
            print("  ✅ OpenWeatherMap API キーが設定済み")
            print("  🌐 実際の気象観測データを取得")
            print("  📡 リアルタイム天気情報")

        print("\n💡 改善方法:")
        print("  1. OpenWeatherMap APIキーを環境変数に設定")
        print("     export OPENWEATHERMAP_API_KEY='your_actual_api_key'")
        print("  2. または openweather_service.py の api_key を直接設定")
        print("  3. 気象庁APIやJMA XMLなどの公式データソースとの併用")

        print("\n🔗 引用元情報:")
        print("  • OpenWeatherMap: https://openweathermap.org/")
        print("  • 気象庁: https://www.jma.go.jp/")
        print("  • 現在のデータソース: テスト用シミュレーション")

    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()

def show_weather_data_comparison():
    """異なる地域での天気データ比較"""
    print("\\n" + "=" * 60)
    print("🗾 地域別天気データ比較テスト")
    print("=" * 60)

    try:
        import sys; import os; sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'archive')); from openweather_service import get_weather_for_location

        test_locations = [
            ("東京都", "代々木公園"),
            ("大阪府", "大阪城公園"),
            ("北海道", "札幌駅"),
            ("沖縄県", "那覇空港")
        ]

        for location, venue in test_locations:
            print(f"\n📍 {location} - {venue}")
            weather = get_weather_for_location(location, venue, 1)  # 明日の天気

            if weather:
                temp = weather.get('average_temperature') or weather.get('temperature', 'N/A')
                humidity = weather.get('humidity', 'N/A')
                rain_prob = weather.get('rain_probability', 'N/A')
                wind = weather.get('wind_speed', 'N/A')
                desc = weather.get('description', 'N/A')

                print(f"  🌡️ 気温: {temp}°C")
                print(f"  💧 湿度: {humidity}%")
                print(f"  ☔ 降水確率: {rain_prob}%")
                print(f"  💨 風速: {wind}km/h")
                print(f"  ☁️ 天気: {desc}")

                # データの妥当性チェック
                temp_num = temp if isinstance(temp, (int, float)) else 0
                humidity_num = humidity if isinstance(humidity, (int, float)) else 0
                rain_prob_num = rain_prob if isinstance(rain_prob, (int, float)) else 0

                validity_notes = []
                if temp_num < -20 or temp_num > 45:
                    validity_notes.append("⚠️ 極端な気温")
                if humidity_num < 0 or humidity_num > 100:
                    validity_notes.append("⚠️ 湿度範囲外")
                if rain_prob_num < 0 or rain_prob_num > 100:
                    validity_notes.append("⚠️ 降水確率範囲外")

                if validity_notes:
                    print(f"  📊 妥当性: {', '.join(validity_notes)}")
                else:
                    print("  ✅ データ妥当性: 正常範囲")
            else:
                print("  ❌ データ取得失敗")

    except Exception as e:
        print(f"❌ 比較テストエラー: {e}")

if __name__ == "__main__":
    test_weather_accuracy_and_display()
    show_weather_data_comparison()

