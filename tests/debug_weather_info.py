#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天気情報抽出とアドバイス生成のデバッグテスト
"""

from reminder_flex_customizer import ReminderFlexCustomizer

def debug_weather_extraction():
    """天気情報抽出のデバッグ"""
    print("=" * 80)
    print("🔍 天気情報抽出デバッグテスト")
    print("=" * 80)

    customizer = ReminderFlexCustomizer()

    # テスト用天気Flex
    test_weather_flex = {
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
                                        "text": "33.2°C",
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
                                        "text": "78%",
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
                                        "text": "5%",
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

    # 1. 天気情報抽出テスト
    print("🔧 ステップ1: 天気情報抽出")
    weather_info = customizer._extract_weather_info_from_base_flex(test_weather_flex)
    print(f"抽出された天気情報: {weather_info}")

    # 2. 直接アドバイス生成テスト
    print("\n🔧 ステップ2: 直接アドバイス生成")
    direct_advice = customizer._generate_sports_weather_advice(
        "33.2°C", "78%", "5%", "元のアドバイス"
    )
    print(f"直接生成されたアドバイス: {direct_advice}")

    # 3. 抽出した情報でアドバイス生成
    print("\n🔧 ステップ3: 抽出情報からアドバイス生成")
    extracted_advice = customizer._generate_sports_weather_advice(
        weather_info.get("temperature", "情報なし"),
        weather_info.get("humidity", "情報なし"),
        weather_info.get("precipitation", "情報なし"),
        weather_info.get("advice", "元のアドバイス")
    )
    print(f"抽出情報からのアドバイス: {extracted_advice}")

if __name__ == "__main__":
    debug_weather_extraction()
