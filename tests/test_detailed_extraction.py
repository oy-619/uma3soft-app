#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime, timedelta

def test_weather_extraction_detailed():
    """詳細な天気情報抽出デバッグテスト"""
    print("=" * 70)
    print("🔍 詳細天気情報抽出デバッグテスト")
    print("=" * 70)

    try:
        from weather_flex_template import WeatherFlexTemplate
        from reminder_flex_customizer import ReminderFlexCustomizer

        # 天気テンプレート生成
        weather_template = WeatherFlexTemplate()
        customizer = ReminderFlexCustomizer()

        # モック天気Flexを生成
        print("📊 モック天気Flex Message生成:")
        weather_flex = weather_template.create_current_weather_flex("東京都")

        # Flex構造から直接データを手動で抽出して確認
        print("\n🔍 手動でFlex構造から情報抽出:")
        body_contents = weather_flex["contents"]["body"]["contents"]

        for i, section in enumerate(body_contents):
            if isinstance(section, dict) and section.get("type") == "box":
                if section.get("layout") == "horizontal" and "contents" in section:
                    horizontal_contents = section["contents"]
                    if len(horizontal_contents) >= 2:
                        label_box = horizontal_contents[0]
                        value_box = horizontal_contents[1]

                        # ラベル抽出
                        label_text = ""
                        if "contents" in label_box:
                            for item in label_box["contents"]:
                                if item.get("type") == "text":
                                    label_text = item.get("text", "")
                                    break

                        # 値抽出
                        value_text = ""
                        if "contents" in value_box:
                            for item in value_box["contents"]:
                                if item.get("type") == "text":
                                    value_text = item.get("text", "")
                                    break

                        if label_text and value_text:
                            print(f"  [{i}] {label_text.strip()} → {value_text.strip()}")

        # 正式な抽出メソッドをテスト
        print("\n🔍 正式な抽出メソッドテスト:")
        weather_info = customizer._extract_weather_info_from_base_flex(weather_flex)

        print("抽出結果:")
        for key, value in weather_info.items():
            status = "✅" if value != "情報なし" else "❌"
            print(f"  {status} {key}: {value}")

        # 実際のリマインダーを生成してテスト
        print("\n📝 実際のリマインダー生成テスト:")
        test_note = {
            "content": """【野球練習】
場所：東京ドーム
日時：11月1日(金) 18:00～
持ち物：グローブ、バット""",
            "date": datetime.now() + timedelta(days=1),
            "days_until": 1,
            "is_input_deadline": True
        }

        reminder_flex = customizer.customize_weather_flex_for_reminder(weather_flex, test_note)

        # 最終的なリマインダーをファイルに保存
        with open('final_detailed_reminder.json', 'w', encoding='utf-8') as f:
            json.dump(reminder_flex, f, ensure_ascii=False, indent=2)

        print("✅ 最終リマインダー生成成功")
        print("💾 保存ファイル: final_detailed_reminder.json")

        # リマインダー内の天候情報を確認
        body_contents = reminder_flex['contents']['body']['contents']
        weather_section_found = False
        for section in body_contents:
            if isinstance(section, dict) and 'contents' in section:
                for item in section['contents']:
                    if isinstance(item, dict) and 'text' in item:
                        if '🌤️ 会場の天候予報' in item.get('text', ''):
                            weather_section_found = True
                            print("✅ 天候情報セクション確認")
                            break

        if not weather_section_found:
            print("⚠️ 天候情報セクションが見つかりません")

        return True

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_weather_extraction_detailed()
