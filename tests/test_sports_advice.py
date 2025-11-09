#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
スポーツ向け天候アドバイス機能のテスト
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from reminder_flex_customizer import ReminderFlexCustomizer

def test_sports_weather_advice():
    """スポーツ向け天候アドバイステスト"""
    print("=" * 80)
    print("⚽ スポーツ向け天候アドバイステスト")
    print("=" * 80)

    customizer = ReminderFlexCustomizer()

    # テストケース：様々な天候条件
    test_cases = [
        {
            "name": "高温多湿（熱中症注意）",
            "temperature": "32.5℃",
            "humidity": "75%",
            "precipitation": "10%",
            "original_advice": "暑いです"
        },
        {
            "name": "高温乾燥（日差し注意）",
            "temperature": "29℃",
            "humidity": "45%",
            "precipitation": "5%",
            "original_advice": "晴れです"
        },
        {
            "name": "適温（スポーツ日和）",
            "temperature": "22℃",
            "humidity": "55%",
            "precipitation": "0%",
            "original_advice": "過ごしやすいです"
        },
        {
            "name": "肌寒い日（ウォーミングアップ重要）",
            "temperature": "12℃",
            "humidity": "60%",
            "precipitation": "15%",
            "original_advice": "寒いです"
        },
        {
            "name": "雨天（雨具必要）",
            "temperature": "18℃",
            "humidity": "85%",
            "precipitation": "80%",
            "original_advice": "雨が降りそうです"
        },
        {
            "name": "雨の可能性（念のため準備）",
            "temperature": "20℃",
            "humidity": "70%",
            "precipitation": "45%",
            "original_advice": "曇りです"
        },
        {
            "name": "蒸し暑い日（汗対策）",
            "temperature": "27℃",
            "humidity": "80%",
            "precipitation": "20%",
            "original_advice": "湿度が高いです"
        }
    ]

    print(f"{'No.':<3} {'条件':<20} {'気温':<8} {'湿度':<6} {'降水':<6} {'アドバイス'}")
    print("-" * 100)

    for i, test_case in enumerate(test_cases, 1):
        # スポーツアドバイス生成
        advice = customizer._generate_sports_weather_advice(
            test_case["temperature"],
            test_case["humidity"],
            test_case["precipitation"],
            test_case["original_advice"]
        )

        print(f"{i:<3} {test_case['name']:<20} {test_case['temperature']:<8} {test_case['humidity']:<6} {test_case['precipitation']:<6} {advice}")

    print("\n" + "=" * 80)
    print("⚽ スポーツ向け天候アドバイステスト完了")
    print("=" * 80)

if __name__ == "__main__":
    test_sports_weather_advice()
