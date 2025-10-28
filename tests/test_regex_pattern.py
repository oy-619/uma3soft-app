#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from datetime import datetime, timedelta

# 正規表現パターンのテスト
test_content = """
[ノート]
テストイベント: 2025/10/27(月) 15:00 - 重要なミーティング
"""

print("=== 正規表現パターンテスト ===")
print(f"テスト対象テキスト: {test_content}")

date_patterns = [
    r"(\d{4})/(\d{1,2})/(\d{1,2})",  # 2024/12/25形式
    r"(\d{4})/(\d{1,2})/(\d{1,2})\([月火水木金土日]\)",  # 2025/10/27(月)形式
    r"(\d{1,2})月(\d{1,2})日",  # 12月25日形式
    r"(\d{1,2})/(\d{1,2})",  # 12/25形式
]

for i, pattern in enumerate(date_patterns):
    print(f"\nパターン {i+1}: {pattern}")
    matches = re.findall(pattern, test_content)
    print(f"マッチ結果: {matches}")

    for match in matches:
        try:
            if len(match) == 3 and all(match):  # 年/月/日（または曜日付き形式）
                year, month, day = map(int, match)
                note_date = datetime(year, month, day).date()
                print(f"  パース成功: {note_date}")
        except Exception as e:
            print(f"  パースエラー: {e}")

# 日付範囲テスト
today = datetime.now().date()
target_date_range = [(today + timedelta(days=i)) for i in range(1, 2)]  # days_ahead=1
print(f"\n今日: {today}")
print(f"対象日付範囲: {target_date_range}")

test_date = datetime(2025, 10, 27).date()
print(f"テスト日付 {test_date} が範囲内か: {test_date in target_date_range}")
