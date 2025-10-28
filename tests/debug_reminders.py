#!/usr/bin/env python3
"""
リマインダー機能の詳細デバッグ用スクリプト
"""

import os
import sys
from datetime import datetime, timedelta

# パス設定
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

# カスタムモジュールをインポート
from reminder_schedule import (
    get_reminders_for_day_after_tomorrow,
    get_reminders_for_tomorrow,
)


def main():
    print("=== リマインダー機能詳細デバッグ ===")
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    day_after_tomorrow = today + timedelta(days=2)

    print(f"今日: {today}")
    print(f"明日: {tomorrow}")
    print(f"明後日: {day_after_tomorrow}")
    print()

    # 明日のリマインダーをチェック
    print("=== 明日のリマインダー ===")
    tomorrow_reminders = get_reminders_for_tomorrow()
    print(f"明日のリマインダー数: {len(tomorrow_reminders)}")

    for i, reminder in enumerate(tomorrow_reminders, 1):
        print(f"[{i}] 日付: {reminder['date']}")
        print(
            f"    タイプ: {'入力期限' if reminder.get('is_input_deadline', False) else 'イベント日'}"
        )
        print(f"    内容: {reminder['content'][:100]}...")
        print()

    # 明後日のリマインダーをチェック
    print("=== 明後日のリマインダー ===")
    day_after_reminders = get_reminders_for_day_after_tomorrow()
    print(f"明後日のリマインダー数: {len(day_after_reminders)}")

    for i, reminder in enumerate(day_after_reminders, 1):
        print(f"[{i}] 日付: {reminder['date']}")
        print(
            f"    タイプ: {'入力期限' if reminder.get('is_input_deadline', False) else 'イベント日'}"
        )
        print(f"    内容: {reminder['content'][:100]}...")
        print()


if __name__ == "__main__":
    main()
