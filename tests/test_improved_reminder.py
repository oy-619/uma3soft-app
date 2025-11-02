#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime, timedelta

def test_improved_reminder():
    """改善されたリマインダーテスト"""
    print("=" * 70)
    print("🔧 改善されたリマインダーテスト")
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
参加費：500円
集合時間：17:45

調整さんURL: https://chouseisan.com/s?h=xxxxx
↑必ずご入力ください！

連絡先：田中太郎（090-1234-5678）
何かご不明な点がございましたらお気軽にお声がけください。""",
            "date": datetime.now() + timedelta(days=1),
            "days_until": 1,
            "is_input_deadline": True
        }

        print("   ✅ テストノート準備完了")

        # 3. 改善されたリマインダー生成
        print("\n🎯 3. 改善されたリマインダー生成:")
        reminder_flex = customizer.customize_weather_flex_for_reminder(weather_flex, test_note)

        # 結果をファイルに保存
        with open('improved_reminder_test.json', 'w', encoding='utf-8') as f:
            json.dump(reminder_flex, f, ensure_ascii=False, indent=2)

        print("   ✅ リマインダー生成成功")
        print("   💾 保存ファイル: improved_reminder_test.json")

        # 4. 改善点の検証
        print("\n✅ 4. 改善点の検証:")

        # 調整さんURL検索
        def find_urls_recursive(obj):
            urls = []
            if isinstance(obj, dict):
                if 'text' in obj:
                    text = obj['text']
                    if 'chouseisan' in text or 'https://' in text or '調整さん' in text and 'URL' in text:
                        urls.append(text)
                for value in obj.values():
                    urls.extend(find_urls_recursive(value))
            elif isinstance(obj, list):
                for item in obj:
                    urls.extend(find_urls_recursive(item))
            return urls

        # 投稿者情報検索
        def find_author_info_recursive(obj):
            author_info = []
            if isinstance(obj, dict):
                if 'text' in obj:
                    text = obj['text']
                    if '田中' in text and ('詳細は個別に' in text or 'ご確認ください' in text):
                        author_info.append(text)
                for value in obj.values():
                    author_info.extend(find_author_info_recursive(value))
            elif isinstance(obj, list):
                for item in obj:
                    author_info.extend(find_author_info_recursive(item))
            return author_info

        # 全文表示確認
        def find_event_details_recursive(obj):
            details = []
            if isinstance(obj, dict):
                if 'text' in obj:
                    text = obj['text']
                    if ('持ち物' in text or '参加費' in text or '集合時間' in text) and 'chouseisan' not in text:
                        details.append(text)
                for value in obj.values():
                    details.extend(find_event_details_recursive(value))
            elif isinstance(obj, list):
                for item in obj:
                    details.extend(find_event_details_recursive(item))
            return details

        urls_found = find_urls_recursive(reminder_flex)
        author_info_found = find_author_info_recursive(reminder_flex)
        event_details_found = find_event_details_recursive(reminder_flex)

        # 結果表示
        if len(urls_found) == 0:
            print("   ✅ 調整さんURL: 上段からも完全に除外されています")
        else:
            print(f"   ❌ 調整さんURL: {len(urls_found)}個のURL関連テキストが見つかりました")
            for i, url in enumerate(urls_found):
                print(f"      {i+1}. {url[:50]}...")

        if len(author_info_found) > 0:
            print("   ✅ 投稿者情報: フッターに追加されました")
            for info in author_info_found:
                print(f"      → {info}")
        else:
            print("   ❌ 投稿者情報: フッターに追加されていません")

        if len(event_details_found) > 0:
            print("   ✅ ノート全文表示: 詳細情報が表示されています")
            for detail in event_details_found:
                print(f"      → {detail[:30]}...")
        else:
            print("   ❌ ノート全文表示: 詳細情報が見つかりません")

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
    test_improved_reminder()
