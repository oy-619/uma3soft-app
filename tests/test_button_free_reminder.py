#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime, timedelta

def test_button_free_reminder():
    """ボタンなしリマインダーテスト"""
    print("=" * 70)
    print("🔧 ボタンなしリマインダーテスト")
    print("=" * 70)

    try:
        from weather_flex_template import WeatherFlexTemplate
        from reminder_flex_customizer import ReminderFlexCustomizer

        # テンプレート生成
        weather_template = WeatherFlexTemplate()
        customizer = ReminderFlexCustomizer()

        # 1. 天気Flexメッセージを生成
        print("📊 1. 天気Flexメッセージ生成:")
        weather_flex = weather_template.create_current_weather_flex("東京都")
        print("   ✅ 天気Flex生成完了")

        # 2. テストノート（調整さんURL含む）
        print("\n📝 2. テストノート準備:")
        test_note = {
            "content": """【重要】調整さん入力をお忘れなく！

【野球練習試合】
場所：東京ドーム
日時：11月1日(金) 18:00～21:00
持ち物：グローブ、バット、飲み物
注意：雨天時は体育館に変更

調整さんURL: https://chouseisan.com/s?h=xxxxx
↑必ずご入力ください！

連絡先：田中（090-1234-5678）""",
            "date": datetime.now() + timedelta(days=1),
            "days_until": 1,
            "is_input_deadline": True
        }

        print("   ✅ テストノート準備完了")

        # 3. リマインダー生成
        print("\n🎯 3. ボタンなしリマインダー生成:")
        reminder_flex = customizer.customize_weather_flex_for_reminder(weather_flex, test_note)

        # 結果をファイルに保存
        with open('button_free_reminder_test.json', 'w', encoding='utf-8') as f:
            json.dump(reminder_flex, f, ensure_ascii=False, indent=2)

        print("   ✅ リマインダー生成成功")
        print("   💾 保存ファイル: button_free_reminder_test.json")

        # 4. 結果検証
        print("\n✅ 4. 結果検証:")

        # ボタン検索（再帰的）
        def find_buttons_recursive(obj):
            buttons = []
            if isinstance(obj, dict):
                if obj.get('type') == 'button':
                    buttons.append(obj)
                for value in obj.values():
                    buttons.extend(find_buttons_recursive(value))
            elif isinstance(obj, list):
                for item in obj:
                    buttons.extend(find_buttons_recursive(item))
            return buttons

        # 調整さんURL検索（再帰的）
        def find_urls_recursive(obj):
            urls = []
            if isinstance(obj, dict):
                if 'text' in obj:
                    text = obj['text']
                    if 'chouseisan' in text or 'https://' in text or '調整さんURL' in text:
                        urls.append(text)
                for value in obj.values():
                    urls.extend(find_urls_recursive(value))
            elif isinstance(obj, list):
                for item in obj:
                    urls.extend(find_urls_recursive(item))
            return urls

        buttons_found = find_buttons_recursive(reminder_flex)
        urls_found = find_urls_recursive(reminder_flex)

        # 天候情報検索
        def find_weather_info_recursive(obj):
            if isinstance(obj, dict):
                if 'text' in obj and '🌤️ 会場の天候予報' in obj.get('text', ''):
                    return True
                for value in obj.values():
                    if find_weather_info_recursive(value):
                        return True
            elif isinstance(obj, list):
                for item in obj:
                    if find_weather_info_recursive(item):
                        return True
            return False

        weather_section_found = find_weather_info_recursive(reminder_flex)

        # 結果表示
        if len(buttons_found) == 0:
            print("   ✅ ボタン: すべてのボタンが削除されています")
        else:
            print(f"   ❌ ボタン: {len(buttons_found)}個のボタンが見つかりました")
            for i, button in enumerate(buttons_found):
                print(f"      {i+1}. {button.get('action', {}).get('label', 'ラベルなし')}")

        if len(urls_found) == 0:
            print("   ✅ URL: 調整さんURLが除外されています")
        else:
            print(f"   ❌ URL: {len(urls_found)}個のURLが見つかりました")
            for i, url in enumerate(urls_found):
                print(f"      {i+1}. {url[:50]}...")

        if weather_section_found:
            print("   ✅ 天候情報: 補足情報として適切に表示されています")
        else:
            print("   ❌ 天候情報: セクションが見つかりません")

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
    test_button_free_reminder()
