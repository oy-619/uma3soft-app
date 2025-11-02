#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改善されたReminderFlexCustomizerのテスト
- location情報の改善（具体的な地名）
- イベント内容全文表示
- 天候予報の見やすい表示
- 当日リマインド時間設定
"""

import json
from datetime import datetime, timedelta

def test_improved_reminder_system():
    """改善されたリマインダーシステムのテスト"""
    print("=" * 80)
    print("🎯 改善されたReminderFlexCustomizerテスト")
    print("=" * 80)

    try:
        from reminder_flex_customizer import ReminderFlexCustomizer
        from weather_flex_template import WeatherFlexTemplate

        customizer = ReminderFlexCustomizer()
        weather_template = WeatherFlexTemplate()
        print("✅ モジュール初期化完了")

        # 改善テスト用のイベント内容
        test_content = """葛飾区柴又少年野球大会
場所：葛飾区柴又球場第一グラウンド
集合時間：17:45（試合開始18:00）
持ち物：グローブ、バット、飲み物、タオル、着替え
注意事項：雨天の場合は翌日同時刻に順延
参加費：500円（当日徴収）
駐車場：利用可能（1日300円）
連絡先：柴又太郎"""

        # テストシナリオ
        test_scenarios = [
            {
                "name": "当日開催（集合時間あり）",
                "content": test_content,
                "days_until": 0,
                "is_input_deadline": False,
                "description": "当日開催で集合時間とリマインド設定のテスト"
            },
            {
                "name": "明日期限（横浜会場）",
                "content": """横浜市青葉区春季大会
会場：横浜市青葉区総合運動場野球場
時間：午後2時開始
持参：ユニフォーム、スパイク
費用：1000円
連絡先：青葉花子""",
                "days_until": 1,
                "is_input_deadline": True,
                "description": "横浜の具体的な会場名と全文表示テスト"
            },
            {
                "name": "3日後開催（さいたま会場）",
                "content": """さいたま市大宮区秋季リーグ戦
開催地：さいたま市大宮区営球場A面
集合：午前10時30分
試合開始：午前11時
持ち物：ユニフォーム一式、グローブ、バット
雨天：中止（延期なし）
問い合わせ：大宮次郎""",
                "days_until": 3,
                "is_input_deadline": False,
                "description": "さいたま会場と午前集合時間のテスト"
            }
        ]

        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n🔧 シナリオ {i}: {scenario['name']}")
            print(f"📝 説明: {scenario['description']}")
            print("-" * 60)

            # ノート作成
            note = {
                "content": scenario["content"],
                "date": datetime.now() + timedelta(days=scenario["days_until"]),
                "days_until": scenario["days_until"],
                "is_input_deadline": scenario["is_input_deadline"]
            }

            # 天気情報生成
            try:
                weather_flex = weather_template.create_current_weather_flex("東京都")
                print("✅ 天気Flex生成完了")
            except Exception as e:
                print(f"⚠️ 天気Flex生成エラー、モック使用: {e}")
                weather_flex = create_mock_weather_flex()

            # リマインダーFlex生成
            reminder_flex = customizer.customize_weather_flex_for_reminder(weather_flex, note)

            # 改善点の確認
            print("\n📊 改善点の確認:")

            # 1. location情報の確認
            location_info = customizer._extract_location_info(scenario["content"])
            print(f"   🗺️  場所情報: {location_info or '検出されず'}")

            # 2. 集合時間の確認
            gathering_time = customizer._extract_gathering_time(scenario["content"])
            if gathering_time:
                reminder_time = customizer._calculate_reminder_time(gathering_time)
                print(f"   ⏰ 集合時間: {gathering_time}")
                print(f"   📱 リマインド時間: {reminder_time}")
            else:
                print("   ⏰ 集合時間: 検出されず")

            # 3. 全文表示の確認
            cleaned_content = customizer._clean_event_content_for_display(scenario["content"])
            print(f"   📋 表示内容: {len(cleaned_content)}文字")
            print(f"      → {cleaned_content[:50]}...")

            # 4. 天候情報の構造確認
            weather_info = customizer._extract_weather_info_from_base_flex(weather_flex)
            print(f"   🌤️ 天候情報: {len(weather_info)}項目")
            for key, value in weather_info.items():
                print(f"      → {key}: {value}")

            # ファイル保存
            filename = f"improved_test_{i}_{scenario['name'].replace('（', '_').replace('）', '')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(reminder_flex, f, ensure_ascii=False, indent=2)
            print(f"\n💾 保存完了: {filename}")

        print("\n" + "=" * 80)
        print("🎉 改善されたリマインダーシステムテスト完了！")
        print("=" * 80)

    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()

def create_mock_weather_flex():
    """モック天気Flexを作成"""
    return {
        "type": "flex",
        "altText": "東京都の天気情報",
        "contents": {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "📍 東京都",
                        "size": "lg",
                        "weight": "bold"
                    }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "🌡️ 気温",
                                        "size": "sm"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "22℃",
                                        "size": "sm",
                                        "weight": "bold"
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "💧 湿度",
                                        "size": "sm"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "65%",
                                        "size": "sm",
                                        "weight": "bold"
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "☔ 降水確率",
                                        "size": "sm"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "20%",
                                        "size": "sm",
                                        "weight": "bold"
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "text",
                        "text": "💡 過ごしやすい天候です。軽い上着があると良いでしょう。",
                        "size": "xs",
                        "wrap": True,
                        "margin": "md"
                    }
                ]
            }
        }
    }

if __name__ == "__main__":
    test_improved_reminder_system()
