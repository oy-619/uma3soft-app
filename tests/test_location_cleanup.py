#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime, timedelta

def test_location_cleanup():
    """場所名クリーンアップテスト"""
    print("=" * 70)
    print("🔧 場所名クリーンアップテスト")
    print("=" * 70)

    try:
        from weather_flex_template import WeatherFlexTemplate
        from reminder_flex_customizer import ReminderFlexCustomizer

        # テンプレート生成
        weather_template = WeatherFlexTemplate()
        customizer = ReminderFlexCustomizer()

        # 1. 場所名クリーンアップのテスト
        print("📊 1. 場所名クリーンアップテスト:")

        test_locations = [
            "東京都小学生男子ソフトボール秋",
            "神奈川県横浜市青葉区美しが丘小学校",
            "千葉県船橋市中央公園野球場",
            "埼玉県さいたま市浦和区駒場運動公園",
            "大阪府大阪市住吉区住吉公園",
            "不明な場所名12345",
            ""
        ]

        for location in test_locations:
            cleaned = customizer._clean_location_name(location)
            print(f"   元: '{location[:30]}{'...' if len(location) > 30 else ''}'")
            print(f"   → '{cleaned}'")
            print()

        # 2. 実際の天気取得テスト
        print("🌤️ 2. 天気取得テスト:")

        for i, location in enumerate(["東京都", "神奈川県", "千葉県"]):
            print(f"   {i+1}. {location}の天気取得...")
            try:
                weather_data = weather_template.get_current_weather(location)
                if weather_data:
                    temp = weather_data.get('temperature', '不明')
                    desc = weather_data.get('description', '不明')
                    print(f"      ✅ 成功: {temp}°C, {desc}")
                else:
                    print(f"      ❌ 失敗: データなし")
            except Exception as e:
                print(f"      ❌ エラー: {e}")

        # 3. 問題のあった場所名でのテスト
        print("\n🚨 3. 問題のあった場所名でのテスト:")
        problematic_location = "東京都小学生男子ソフトボール秋"
        cleaned_location = customizer._clean_location_name(problematic_location)

        print(f"   問題のあった場所名: '{problematic_location}'")
        print(f"   クリーンアップ後: '{cleaned_location}'")

        try:
            weather_data = weather_template.get_current_weather(cleaned_location)
            if weather_data:
                print(f"   ✅ 天気取得成功: {weather_data.get('temperature', '不明')}°C")
            else:
                print(f"   ❌ 天気取得失敗: データなし")
        except Exception as e:
            print(f"   ❌ 天気取得エラー: {e}")

        # 4. リマインダー生成テスト（問題のあった場所名で）
        print("\n📝 4. リマインダー生成テスト:")
        test_note = {
            "content": f"""【野球練習試合】
場所：{problematic_location}
日時：11月1日(金) 18:00～21:00
持ち物：グローブ、バット、飲み物""",
            "date": datetime.now() + timedelta(days=1),
            "days_until": 1,
            "is_input_deadline": True
        }

        # 天気Flex生成（クリーンアップされた場所名で）
        weather_flex = weather_template.create_current_weather_flex(cleaned_location)

        # リマインダー生成
        reminder_flex = customizer.customize_weather_flex_for_reminder(weather_flex, test_note)

        # 結果をファイルに保存
        with open('location_cleanup_test.json', 'w', encoding='utf-8') as f:
            json.dump(reminder_flex, f, ensure_ascii=False, indent=2)

        print("   ✅ リマインダー生成成功")
        print("   💾 保存ファイル: location_cleanup_test.json")

        print("\n" + "=" * 70)
        print("🎉 テスト完了！")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_location_cleanup()
