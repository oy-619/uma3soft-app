#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# srcディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from reminder_schedule import get_reminders_for_tomorrow


def main():
    print("=== 明日のリマインダーテスト ===")

    # 明日のリマインダーを取得
    tomorrow_reminders = get_reminders_for_tomorrow()
    print(f"明日のリマインダー数: {len(tomorrow_reminders)}")

    for i, reminder in enumerate(tomorrow_reminders, 1):
        print(f"\n--- リマインダー {i} ---")
        print(f"内容: {reminder[:100]}...")


if __name__ == "__main__":
    main()
