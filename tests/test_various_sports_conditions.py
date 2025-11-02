#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
様々な天候条件でのスポーツ向けアドバイス統合テスト
"""

import json
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from reminder_flex_customizer import ReminderFlexCustomizer

def test_various_weather_sports_advice():
    """様々な天候条件でのスポーツアドバイステスト"""
    print("=" * 80)
    print("🌦️ 様々な天候条件でのスポーツ向けアドバイステスト")
    print("=" * 80)

    customizer = ReminderFlexCustomizer()

    # 様々な天候条件のモックFlex作成
    weather_conditions = [
        {
            "name": "高温多湿（猛暑日）",
            "weather_flex": create_mock_weather_flex("東京都", "33.2°C", "78%", "5%"),
            "expected_advice": "熱中症対策必須"
        },
        {
            "name": "適温（スポーツ日和）",
            "weather_flex": create_mock_weather_flex("神奈川県", "22°C", "55%", "10%"),
            "expected_advice": "運動に最適"
        },
        {
            "name": "雨天（屋内推奨）",
            "weather_flex": create_mock_weather_flex("千葉県", "18°C", "85%", "75%"),
            "expected_advice": "雨天のため室内"
        },
        {
            "name": "寒い日（防寒必要）",
            "weather_flex": create_mock_weather_flex("埼玉県", "8°C", "60%", "20%"),
            "expected_advice": "防寒対策"
        }
    ]

    # 基本イベント情報
    base_event_content = """秋季野球大会
場所：地域運動場野球場
集合時間：10:00（試合開始10:30）
持ち物：ユニフォーム、グローブ、バット、飲み物
連絡先：大会太郎"""

    for i, condition in enumerate(weather_conditions, 1):
        print(f"\n🧪 テスト {i}: {condition['name']}")
        print("-" * 60)

        # ノート作成
        note = {
            "content": base_event_content,
            "date": datetime.now(),
            "days_until": 0,
            "is_input_deadline": False
        }

        # リマインダーFlex生成
        reminder_flex = customizer.customize_weather_flex_for_reminder(
            condition["weather_flex"], note
        )

        # アドバイス部分を抽出
        advice_text = extract_advice_from_flex(reminder_flex)

        print(f"🌤️ 天候条件: {condition['name']}")
        print(f"💡 スポーツアドバイス: {advice_text}")

        # ファイル保存
        filename = f"sports_advice_test_{i}_{condition['name'].replace('（', '_').replace('）', '')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(reminder_flex, f, ensure_ascii=False, indent=2)
        print(f"💾 保存完了: {filename}")

        # 期待する内容が含まれているかチェック
        if condition["expected_advice"] in advice_text:
            print("✅ 期待するアドバイス内容が含まれています")
        else:
            print("⚠️ 期待するアドバイス内容が見つかりません")

    print("\n" + "=" * 80)
    print("🎉 様々な天候条件でのスポーツアドバイステスト完了")
    print("=" * 80)

def create_mock_weather_flex(venue, temperature, humidity, precipitation):
    """指定した条件のモック天気Flexを作成"""
    return {
        "type": "flex",
        "altText": f"{venue}の天気情報",
        "contents": {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"📍 {venue}",
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
                                        "text": temperature,
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
                                        "text": humidity,
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
                                        "text": precipitation,
                                        "size": "sm",
                                        "weight": "bold"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
    }

def extract_advice_from_flex(flex_message):
    """Flexメッセージからアドバイス文を抽出"""
    try:
        body_contents = flex_message.get("contents", {}).get("body", {}).get("contents", [])

        for section in body_contents:
            if section.get("type") == "box":
                section_contents = section.get("contents", [])
                for item in section_contents:
                    if item.get("type") == "box" and item.get("layout") == "horizontal":
                        horizontal_contents = item.get("contents", [])
                        if len(horizontal_contents) >= 2:
                            first_box = horizontal_contents[0]
                            second_box = horizontal_contents[1]

                            # 💡アイコンをチェック
                            if (first_box.get("type") == "text" and
                                first_box.get("text") == "💡"):
                                # アドバイステキスト取得
                                if (second_box.get("type") == "text"):
                                    return second_box.get("text", "")

        return "アドバイスが見つかりません"
    except Exception as e:
        return f"抽出エラー: {e}"

if __name__ == "__main__":
    test_various_weather_sports_advice()
