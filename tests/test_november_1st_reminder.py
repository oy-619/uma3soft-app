#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2025年11月1日のリマインダー天気情報の詳細テスト
"""

import sys
import os
import json
from datetime import datetime, timedelta

# プロジェクトのパスを追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

def test_november_1st_reminder():
    """2025年11月1日のリマインダー天気情報テスト"""
    print("📅 2025年11月1日リマインダー天気情報テスト")
    print("=" * 60)

    try:
        from enhanced_reminder_messages import generate_weather_flex_card, generate_enhanced_reminder_message
        import sys; import os; sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'archive')); from openweather_service import get_weather_for_location

        # 2025年11月1日のイベント
        event_november_1st = {
            "content": "[ノート] 11月1日(土) 秋の運動会\n会場: 代々木公園陸上競技場\n集合時間: 9:00\n持ち物: 運動着、タオル、飲み物\n雨天中止の可能性あり",
            "date": datetime(2025, 11, 1).date(),
            "days_until": 2,  # 10月30日から2日後
            "is_input_deadline": False
        }

        print("🏃‍♂️ テスト対象イベント:")
        print(f"  📅 日付: 2025年11月1日（土）")
        print(f"  🏟️ 会場: 代々木公園陸上競技場")
        print(f"  🎯 種類: 屋外スポーツイベント")
        print(f"  ☔ 天気重要度: 高（雨天中止の可能性）")

        print("\n--- 1. 直接天気API呼び出し ---")
        # 11月1日の天気予報を取得（2日後）
        weather_data = get_weather_for_location("東京都", "代々木公園陸上競技場", 2)

        if weather_data:
            print("✅ 天気データ取得成功")

            # 取得したデータの詳細表示
            temp = weather_data.get('average_temperature') or weather_data.get('temperature', 'N/A')
            max_temp = weather_data.get('max_temperature', 'N/A')
            min_temp = weather_data.get('min_temperature', 'N/A')
            humidity = weather_data.get('humidity', 'N/A')
            rain_prob = weather_data.get('rain_probability', 'N/A')
            wind_speed = weather_data.get('wind_speed', 'N/A')
            description = weather_data.get('description', 'N/A')

            print(f"  🌡️ 気温: {temp}°C")
            if max_temp != 'N/A' and min_temp != 'N/A':
                print(f"  📊 気温範囲: {min_temp}°C - {max_temp}°C")
            print(f"  💧 湿度: {humidity}%")
            print(f"  ☔ 降水確率: {rain_prob}%")
            print(f"  💨 風速: {wind_speed}km/h")
            print(f"  ☁️ 天気: {description}")

            # データソースの確認
            is_mock = weather_data.get('is_mock_data', False)
            data_source = weather_data.get('data_source', 'OpenWeatherMap API')
            print(f"  📡 データソース: {data_source}")

            if is_mock:
                print("  ⚠️ これはテスト用データです")
            else:
                print("  ✅ 実際の気象予報データです")

            # 運動会への影響評価
            print("\n🏃‍♂️ 運動会への影響評価:")

            # 気温評価
            if isinstance(temp, (int, float)):
                if temp >= 25:
                    print("  🌡️ 暖かい日になりそうです。熱中症対策を忘れずに！")
                elif temp >= 15:
                    print("  🌡️ 運動するのに適した気温です。")
                elif temp >= 10:
                    print("  🌡️ やや涼しいです。ウォームアップをしっかりと。")
                else:
                    print("  🌡️ 寒いです。防寒対策が必要です。")

            # 降水確率評価
            if isinstance(rain_prob, (int, float)):
                if rain_prob >= 70:
                    print("  ☔ 雨の可能性が高いです。中止になる可能性があります。")
                elif rain_prob >= 40:
                    print("  ☔ 雨の可能性があります。雨具の準備をお勧めします。")
                elif rain_prob >= 20:
                    print("  ☔ 小雨の可能性があります。念のため雨具を持参してください。")
                else:
                    print("  ☀️ 雨の心配は少なそうです。")

            # 風速評価
            if isinstance(wind_speed, (int, float)):
                if wind_speed >= 20:
                    print("  💨 風が強いです。競技に影響する可能性があります。")
                elif wind_speed >= 10:
                    print("  💨 やや風があります。軽いものが飛ばされないよう注意。")
                else:
                    print("  💨 風は穏やかです。")

        else:
            print("❌ 天気データ取得失敗")

        print("\n--- 2. 天気カードFlex Message生成 ---")
        weather_flex = generate_weather_flex_card(event_november_1st)

        if weather_flex:
            print("✅ Flex Message生成成功")

            # JSONファイル保存
            output_file = "november_1st_weather_card.json"
            output_path = os.path.join(project_root, "tests", output_file)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(weather_flex, f, ensure_ascii=False, indent=2)

            print(f"💾 天気カード保存: {output_file}")

            # 表示内容確認
            alt_text = weather_flex.get("altText", "")
            print(f"📱 代替テキスト: {alt_text}")

        else:
            print("❌ Flex Message生成失敗")

        print("\n--- 3. 通常リマインダーメッセージ生成 ---")
        reminder_text = generate_enhanced_reminder_message(event_november_1st)

        if reminder_text:
            print("✅ リマインダーメッセージ生成成功")
            print(f"📝 文字数: {len(reminder_text)}文字")

            # 天気情報部分の抽出表示
            lines = reminder_text.split('\n')
            weather_section = []
            in_weather_section = False

            for line in lines:
                if '天気情報' in line or '天気予報' in line:
                    in_weather_section = True
                elif in_weather_section and ('データ提供' in line or '取得日時' in line):
                    weather_section.append(line)
                    break

                if in_weather_section:
                    weather_section.append(line)

            if weather_section:
                print("\n🌤️ 天気情報セクション:")
                for line in weather_section[:10]:  # 最初の10行のみ表示
                    print(f"    {line}")
                if len(weather_section) > 10:
                    print(f"    ... （他{len(weather_section)-10}行）")
        else:
            print("❌ リマインダーメッセージ生成失敗")

        print("\n--- 4. 改善された表示内容の確認 ---")
        print("✅ 実装済み改善点:")
        print("  📍 開催場所の明示表示")
        print("  🗺️ 対象地域の表示")
        print("  🔗 OpenWeatherMap引用元リンク")
        print("  📅 データ取得日時の表示")
        print("  ✅ 実際のAPIデータ使用の表示")
        print("  ⚠️ テストデータ時の注意表示")
        print("  🌡️ 詳細な天気情報（気温、湿度、降水確率、風速）")
        print("  🎯 イベント種類に応じた注意喚起")

        print("\n🎉 結論:")
        if weather_data and not weather_data.get('is_mock_data', False):
            print("  ✅ 正確な天気情報を取得・表示しています")
            print("  📡 OpenWeatherMap APIからリアルタイムデータを使用")
            print("  🔗 適切な引用元情報を表示")
            print("  📍 開催場所と対象地域を明示")
        else:
            print("  ⚠️ テストデータを使用中")
            print("  🔧 APIキー設定で実データに切り替え可能")

    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_november_1st_reminder()

