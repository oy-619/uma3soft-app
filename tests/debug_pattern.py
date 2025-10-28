import re
import sys

sys.path.append(".")
from datetime import datetime, timedelta

from reminder_schedule import get_vector_db

print("=== Debug: Manual Date Pattern Testing ===")

# テストイベントデータを直接検索
vector_db = get_vector_db()
notes = vector_db.similarity_search("テストイベント", k=10)

print(f'Found {len(notes)} notes containing "テストイベント"')
for note in notes:
    content = note.page_content
    if "テストイベント" in content:
        print(f"Content: {content}")
        print()

        # 日付パターンテスト
        date_patterns = [
            r"(\d{4})/(\d{1,2})/(\d{1,2})",  # 2024/12/25形式
            r"(\d{4})/(\d{1,2})/(\d{1,2})\([月火水木金土日]\)",  # 2025/10/27(月)形式
            r"(\d{1,2})月(\d{1,2})日",  # 12月25日形式
            r"(\d{1,2})/(\d{1,2})",  # 12/25形式
        ]

        for i, pattern in enumerate(date_patterns):
            matches = re.findall(pattern, content)
            print(f"Pattern {i+1} ({pattern}): {matches}")

        print("---")
