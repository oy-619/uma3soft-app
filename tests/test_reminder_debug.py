#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# reminder_schedule.pyの関数をインポートして実行
sys.path.append(os.path.dirname(__file__))
from reminder_schedule import get_upcoming_deadline_notes

print("=== デバッグテスト: get_upcoming_deadline_notes() ===")
print("明日までの期限を検索...")

try:
    results = get_upcoming_deadline_notes(days_ahead=1)
    print(f"\n=== 結果 ===")
    print(f"見つかった期限付きノート数: {len(results)}")

    for i, note in enumerate(results):
        print(f"\nノート {i+1}:")
        print(f"  日付: {note['date']}")
        print(f"  残り日数: {note['days_until']}日")
        print(f"  内容: {note['content'][:200]}...")

except Exception as e:
    print(f"エラーが発生しました: {e}")
    import traceback

    traceback.print_exc()
