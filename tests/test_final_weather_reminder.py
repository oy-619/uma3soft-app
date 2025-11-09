#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime, timedelta

def test_final_weather_reminder():
    """最終的な天気情報付きリマインダーテスト"""
    print("=" * 70)
    print("🔧 最終 天気情報付きリマインダーテスト")
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

        # 生成されたFlex構造をファイルに保存（デバッグ用）
        with open('test_weather_flex.json', 'w', encoding='utf-8') as f:
            json.dump(weather_flex, f, ensure_ascii=False, indent=2)
        print("   💾 天気Flex保存: test_weather_flex.json")

        # 2. 天気情報を抽出
        print("\n🔍 2. 天気情報抽出:")
        weather_info = customizer._extract_weather_info_from_base_flex(weather_flex)

        print("   抽出結果:")
        for key, value in weather_info.items():
            status = "✅" if value != "情報なし" else "❌"
            print(f"     {status} {key}: {value}")

        # 3. ノート情報を準備
        print("\n📝 3. テストノート準備:")
        test_note = {
            "content": """【重要】調整さん入力をお忘れなく！

【野球練習試合】
場所：東京ドーム
日時：11月1日(金) 18:00～21:00
持ち物：グローブ、バット、飲み物

調整さんURL: https://chouseisan.com/s?h=xxxxx
↑必ずご入力ください！""",
            "date": datetime.now() + timedelta(days=1),
            "days_until": 1,
            "is_input_deadline": True
        }

        print("   ✅ テストノート準備完了")

        # 4. リマインダー生成
        print("\n🎯 4. リマインダー生成:")
        reminder_flex = customizer.customize_weather_flex_for_reminder(weather_flex, test_note)

        # 最終結果をファイルに保存
        with open('final_weather_reminder_test.json', 'w', encoding='utf-8') as f:
            json.dump(reminder_flex, f, ensure_ascii=False, indent=2)

        print("   ✅ リマインダー生成成功")
        print("   💾 保存ファイル: final_weather_reminder_test.json")

        # 5. 結果検証
        print("\n✅ 5. 結果検証:")

        # ヘッダータイトル確認
        header_title = reminder_flex.get('contents', {}).get('header', {}).get('contents', [{}])[0].get('text', '')
        if '📅 スケジュール確認' in header_title:
            print("   ✅ ヘッダー: スケジュール確認が優先されています")
        else:
            print(f"   ⚠️ ヘッダー: {header_title}")

        # ボタン確認（再帰的に検索）
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

        # 天候情報セクション確認（再帰的に検索）
        def find_weather_section_recursive(obj):
            if isinstance(obj, dict):
                if 'text' in obj and '🌤️ 会場の天候予報' in obj.get('text', ''):
                    return True
                for value in obj.values():
                    if find_weather_section_recursive(value):
                        return True
            elif isinstance(obj, list):
                for item in obj:
                    if find_weather_section_recursive(item):
                        return True
            return False

        buttons_found = find_buttons_recursive(reminder_flex)
        weather_section_found = find_weather_section_recursive(reminder_flex)

        if len(buttons_found) > 0:
            print(f"   ✅ ボタン: {len(buttons_found)}個の調整さん入力ボタンが設置されています")
        else:
            print("   ❌ ボタン: 調整さん入力ボタンが見つかりません")

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
    test_final_weather_reminder()
