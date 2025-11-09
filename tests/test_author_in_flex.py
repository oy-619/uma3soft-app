#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投稿者情報がFlexメッセージに正確に表示されているかの最終確認テスト
"""

import json
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from reminder_flex_customizer import ReminderFlexCustomizer

def test_author_in_flex_message():
    """Flexメッセージ内の投稿者情報確認テスト"""
    print("=" * 80)
    print("👤 Flexメッセージ内投稿者情報確認テスト")
    print("=" * 80)

    customizer = ReminderFlexCustomizer()

    # 実際のFlexメッセージを生成するテストケース
    test_cases = [
        {
            "name": "柴又太郎のイベント",
            "content": """葛飾区柴又少年野球大会
場所：葛飾区柴又球場第一グラウンド
集合時間：17:45（試合開始18:00）
持ち物：グローブ、バット、飲み物、タオル、着替え
注意事項：雨天の場合は翌日同時刻に順延
参加費：500円（当日徴収）
駐車場：利用可能（1日300円）
連絡先：柴又太郎""",
            "expected_author": "柴又太郎"
        },
        {
            "name": "青葉花子の大会",
            "content": """横浜市青葉区春季大会
会場：横浜市青葉区総合運動場野球場
時間：午後2時開始
持参：ユニフォーム、スパイク
費用：1000円
担当：青葉花子""",
            "expected_author": "青葉花子"
        }
    ]

    # モック天気情報
    mock_weather_flex = {
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
                        "type": "text",
                        "text": "🌡️ 気温: 22℃",
                        "size": "sm"
                    }
                ]
            }
        }
    }

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 テスト {i}: {test_case['name']}")
        print("-" * 60)

        # ノート情報作成
        note = {
            "content": test_case["content"],
            "date": datetime.now(),
            "days_until": 0,
            "is_input_deadline": False
        }

        # Flexメッセージ生成
        flex_message = customizer.customize_weather_flex_for_reminder(mock_weather_flex, note)

        # フッター部分から投稿者情報を抽出
        footer_contents = flex_message.get("contents", {}).get("footer", {}).get("contents", [])

        author_found = None
        for content in footer_contents:
            if content.get("type") == "text":
                text = content.get("text", "")
                if "詳細は個別にご確認ください" in text:
                    # 括弧内の投稿者名を抽出
                    import re
                    match = re.search(r'（([^）]+)）', text)
                    if match:
                        author_found = match.group(1)
                    break

        print(f"📝 イベント内容: {test_case['content'][:50]}...")
        print(f"🎯 期待する投稿者: {test_case['expected_author']}")
        print(f"📤 Flex内投稿者: {author_found}")

        # 判定
        if author_found == test_case["expected_author"]:
            print("✅ Flexメッセージ内投稿者情報：正確に表示")
        else:
            print("❌ Flexメッセージ内投稿者情報：表示エラー")

        # JSONファイルとして保存して詳細確認
        filename = f"author_test_{i}_{test_case['name'].replace('の', '_')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(flex_message, f, ensure_ascii=False, indent=2)
        print(f"💾 詳細確認用ファイル保存: {filename}")

    print("\n" + "=" * 80)
    print("🎉 Flexメッセージ内投稿者情報確認テスト完了")
    print("=" * 80)

if __name__ == "__main__":
    test_author_in_flex_message()
