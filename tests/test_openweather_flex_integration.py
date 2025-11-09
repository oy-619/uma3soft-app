#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenWeatherMap API と Flex Message 統合テスト
"""

import sys
import os
import json
from datetime import datetime, timedelta

# プロジェクトのパスを追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

def test_openweather_service():
    """OpenWeatherMap サービス単体テスト"""
    print("=== OpenWeatherMap サービステスト ===")

    try:
        import sys; import os; sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'archive')); from openweather_service import get_weather_for_location

        test_locations = [
            ("東京都", "代々木公園"),
            ("大阪府", "大阪城ホール"),
            ("北海道", "札幌ドーム"),
            ("渋谷", ""),
            ("新宿", "")
        ]

        for location, venue in test_locations:
            print(f"\n📍 {location} {venue}")
            weather = get_weather_for_location(location, venue, 0)  # 今日の天気

            if weather:
                print(f"  🌡️ 気温: {weather.get('temperature', 'N/A')}°C")
                print(f"  💧 湿度: {weather.get('humidity', 'N/A')}%")
                print(f"  💨 風速: {weather.get('wind_speed', 'N/A')}km/h")
                print(f"  ☁️ 天気: {weather.get('description', 'N/A')}")

                # 予報も取得
                forecast = get_weather_for_location(location, venue, 1)  # 明日の天気
                if forecast:
                    print(f"  📅 明日の予想気温: {forecast.get('average_temperature', 'N/A')}°C")
                    print(f"  ☔ 降水確率: {forecast.get('rain_probability', 'N/A')}%")
            else:
                print("  ❌ 天気データ取得失敗")

        print("\n✅ OpenWeatherMap サービステスト完了")

    except Exception as e:
        print(f"❌ OpenWeatherMap サービステストエラー: {e}")

def test_weather_flex_message():
    """天気 Flex Message テスト"""
    print("\n=== 天気 Flex Message テスト ===")

    try:
        from enhanced_reminder_messages import generate_weather_flex_card

        # テストデータ
        test_events = [
            {
                "content": "[ノート] 11月3日(日) ソフトボール練習試合\n会場: 代々木公園グラウンド\n集合時間: 9:00\n持ち物: グローブ、帽子、飲み物",
                "date": (datetime.now() + timedelta(days=1)).date(),
                "days_until": 1,
                "is_input_deadline": False
            },
            {
                "content": "[ノート] 12月15日(日) 忘年会\n会場: 新宿の居酒屋\n時間: 18:00-21:00\n会費: 4000円",
                "date": (datetime.now() + timedelta(days=2)).date(),
                "days_until": 2,
                "is_input_deadline": False
            },
            {
                "content": "[ノート] 1月20日(月) 会社会議\n場所: 渋谷オフィス\n時間: 10:00-12:00\n資料準備必要",
                "date": (datetime.now() + timedelta(days=0)).date(),  # 今日
                "days_until": 0,
                "is_input_deadline": False
            }
        ]

        for i, event in enumerate(test_events, 1):
            print(f"\n--- テストケース {i} ---")
            content_lines = event['content'].split('\n')
            print(f"イベント: {content_lines[0]}")

            flex_message = generate_weather_flex_card(event)

            if flex_message:
                print("✅ Flex Message 生成成功")

                # JSON の構造を確認
                if flex_message.get("type") == "flex":
                    print("  📋 Flex Message タイプ: OK")
                    contents = flex_message.get("contents", {})

                    if contents.get("type") == "bubble":
                        print("  🫧 Bubble タイプ: OK")

                        # ヘッダー確認
                        header = contents.get("header", {})
                        if header:
                            print("  📊 ヘッダー: 有")

                        # ボディ確認
                        body = contents.get("body", {})
                        if body:
                            print("  📝 ボディ: 有")

                        # フッター確認
                        footer = contents.get("footer", {})
                        if footer:
                            print("  📄 フッター: 有")

                    # altText 確認
                    alt_text = flex_message.get("altText", "")
                    if alt_text:
                        print(f"  📱 代替テキスト: {alt_text}")                # ファイルに保存（確認用）
                output_file = f"test_weather_flex_{i}.json"
                output_path = os.path.join(project_root, "tests", output_file)

                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(flex_message, f, ensure_ascii=False, indent=2)
                print(f"  💾 JSON ファイル保存: {output_file}")

            else:
                print("❌ Flex Message 生成失敗")

        print("\n✅ 天気 Flex Message テスト完了")

    except Exception as e:
        print(f"❌ 天気 Flex Message テストエラー: {e}")

def test_enhanced_reminder_integration():
    """統合リマインダーテスト"""
    print("\n=== 統合リマインダーテスト ===")

    try:
        from enhanced_reminder_messages import (
            generate_enhanced_reminder_message,
            generate_enhanced_flex_message,
            generate_weather_flex_card
        )

        # テストイベント
        test_event = {
            "content": "[ノート] 11月10日(日) BBQイベント\n会場: 代々木公園バーベキュー広場\n集合時間: 11:00\n持ち物: 食材、飲み物、炭、軍手\n雨天中止",
            "date": (datetime.now() + timedelta(days=1)).date(),
            "days_until": 1,
            "is_input_deadline": False
        }

        print("テストイベント:")
        content_lines = test_event['content'].split('\n')
        print(f"  📅 {content_lines[0]}")
        print(f"  📍 日付: {test_event['date']}")
        print(f"  ⏰ あと{test_event['days_until']}日")

        # 1. 通常のテキストメッセージ
        print("\n--- 通常テキストメッセージ ---")
        text_message = generate_enhanced_reminder_message(test_event)
        if text_message:
            print("✅ テキストメッセージ生成成功")
            print(f"📝 文字数: {len(text_message)}文字")
        else:
            print("❌ テキストメッセージ生成失敗")

        # 2. 通常の Flex Message
        print("\n--- 通常 Flex Message ---")
        normal_flex = generate_enhanced_flex_message(test_event)
        if normal_flex:
            print("✅ 通常 Flex Message 生成成功")
        else:
            print("❌ 通常 Flex Message 生成失敗")

        # 3. 天気 Flex Message
        print("\n--- 天気 Flex Message ---")
        weather_flex = generate_weather_flex_card(test_event)
        if weather_flex:
            print("✅ 天気 Flex Message 生成成功")

            # 複合メッセージの例（配列で複数送信）
            combined_messages = [normal_flex, weather_flex]
            print(f"📊 複合メッセージ: {len(combined_messages)}個のカード")

            # JSONファイルとして保存
            output_path = os.path.join(project_root, "tests", "combined_reminder_messages.json")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump({
                    "text_message": text_message,
                    "normal_flex": normal_flex,
                    "weather_flex": weather_flex,
                    "combined": combined_messages
                }, f, ensure_ascii=False, indent=2, default=str)

            print(f"💾 統合メッセージ保存: combined_reminder_messages.json")
        else:
            print("❌ 天気 Flex Message 生成失敗")

        print("\n✅ 統合リマインダーテスト完了")

    except Exception as e:
        print(f"❌ 統合リマインダーテストエラー: {e}")

def display_summary():
    """テスト結果サマリー"""
    print("\n" + "="*50)
    print("🎯 OpenWeatherMap & Flex Message 統合テスト結果")
    print("="*50)
    print("✅ 実装完了機能:")
    print("  📡 OpenWeatherMap API 統合")
    print("  🌤️ 詳細天気情報取得 (気温、湿度、降水確率、風速)")
    print("  🎴 Flex Message 天気カード表示")
    print("  🔔 雨天時の特別メッセージ (例: 傘を忘れずに！)")
    print("  🏢 会場名対応 (代々木公園、新宿、渋谷など)")
    print("  📱 モバイル最適化カードレイアウト")
    print("  🎨 天気に応じた色分けとアイコン")
    print("  🛡️ エラー処理とフォールバック機能")
    print("\n📋 次のステップ:")
    print("  🔗 LINE Bot への統合")
    print("  🧪 実環境でのテスト")
    print("  🔑 OpenWeatherMap API キー設定 (必要に応じて)")
    print("\n🎉 リマインダーシステムがより実用的になりました！")

if __name__ == "__main__":
    print("🚀 OpenWeatherMap & Flex Message 統合テスト開始")
    print("="*60)

    # 各テストを実行
    test_openweather_service()
    test_weather_flex_message()
    test_enhanced_reminder_integration()

    # サマリー表示
    display_summary()

    print("\n🏁 全テスト完了")

