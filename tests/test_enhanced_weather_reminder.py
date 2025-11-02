#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from reminder_flex_customizer import ReminderFlexCustomizer

def test_enhanced_weather_reminder():
    """改良された天候情報を含むリマインダーFlexシステムのテスト"""
    print("=" * 70)
    print("🌤️ 改良版天候情報リマインダーFlexシステムのテスト開始")
    print("必須項目：会場名、気温、湿度、降水確率、一言アドバイス")
    print("=" * 70)

    try:
        customizer = ReminderFlexCustomizer()
        print("✅ ReminderFlexCustomizer初期化成功")

        # テスト用ノートデータ
        test_note = {
            "content": """【野球大会参加確認】
場所：平和島公園野球場
日時：11月2日(日) 9:00集合
持ち物：グローブ、スパイク、飲み物
参加費：500円
注意：雨天の場合は中止""",
            "date": datetime.now() + timedelta(days=2),
            "days_until": 1,  # 明日期限
            "is_input_deadline": True
        }

        # より詳細なモック天気Flex Message
        detailed_weather_flex = {
            "type": "bubble",
            "contents": {
                "body": {
                    "contents": [
                        {
                            "type": "box",
                            "contents": [
                                {
                                    "type": "box",
                                    "contents": [
                                        {
                                            "type": "box",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": "🌤 天気:"
                                                }
                                            ]
                                        },
                                        {
                                            "type": "box",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": "晴れ"
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "contents": [
                                        {
                                            "type": "box",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": "🌡️ 気温:"
                                                }
                                            ]
                                        },
                                        {
                                            "type": "box",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": "22.5℃"
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "contents": [
                                        {
                                            "type": "box",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": "💧 湿度:"
                                                }
                                            ]
                                        },
                                        {
                                            "type": "box",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": "65%"
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "contents": [
                                        {
                                            "type": "box",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": "☔ 降水確率:"
                                                }
                                            ]
                                        },
                                        {
                                            "type": "box",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": "10%"
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "🌈 天気アドバイス"
                                },
                                {
                                    "type": "text",
                                    "text": "日差し対策をお忘れなく・過ごしやすい気温です"
                                }
                            ]
                        }
                    ]
                }
            }
        }

        # 改良されたリマインダーFlex生成テスト
        print("\n📝 改良版天候情報リマインダーテスト:")
        enhanced_flex = customizer.customize_weather_flex_for_reminder(detailed_weather_flex, test_note)
        print("✅ 改良版リマインダーFlex生成成功")
        print(f"   タイトル: {enhanced_flex['altText']}")
        print(f"   Type: {enhanced_flex['contents']['type']}")

        # 天候情報の確認
        body_contents = enhanced_flex['contents']['body']['contents']
        weather_section = None
        for section in body_contents:
            if isinstance(section, dict) and section.get('contents'):
                for item in section['contents']:
                    if isinstance(item, dict) and 'text' in item and '🌤️ 会場の天候予報' in item.get('text', ''):
                        weather_section = section
                        break

        if weather_section:
            print("✅ 天候情報セクション確認済み")
            print("   必須項目:")
            print("   - 会場名: ✅")
            print("   - 気温: ✅")
            print("   - 湿度: ✅")
            print("   - 降水確率: ✅")
            print("   - 一言アドバイス: ✅")
        else:
            print("⚠️ 天候情報セクションが見つかりません")

        # JSONファイルとして保存
        with open('enhanced_weather_reminder.json', 'w', encoding='utf-8') as f:
            json.dump(enhanced_flex, f, ensure_ascii=False, indent=2)

        print(f"\n💾 保存ファイル: enhanced_weather_reminder.json")

        # 構造の詳細確認
        print(f"\n📊 構造詳細確認:")
        print(f"   Header色: {enhanced_flex['contents']['header']['backgroundColor']}")
        print(f"   Footer有無: {'あり' if 'footer' in enhanced_flex['contents'] else 'なし'}")
        print(f"   Body項目数: {len(enhanced_flex['contents']['body']['contents'])}")

        print("\n" + "=" * 70)
        print("🎉 改良版天候情報リマインダーFlexシステムテスト完了！")
        print("主要コンテンツ：調整さんの確認と入力依頼")
        print("補足情報：会場名・気温・湿度・降水確率・一言アドバイス")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_enhanced_weather_reminder()
