#!/usr/bin/env python3
"""
明日の通知対象詳細確認スクリプト
"""

import os
import sys
from pathlib import Path

# パスを追加
sys.path.append(str(Path(__file__).parent))

from reminder_schedule import format_reminder_message, get_reminders_for_tomorrow


def main():
    print("=== 明日の通知対象詳細確認 ===")
    tomorrow_notes = get_reminders_for_tomorrow()
    print(f"検出件数: {len(tomorrow_notes)}件")

    for i, note in enumerate(tomorrow_notes, 1):
        print(f"\n{i}. 通知対象ノート:")
        print(f'   日付: {note["date"]}')
        print(f'   入力期限あり: {note.get("is_input_deadline", False)}')
        print(f'   リマインドタイプ: {note.get("reminder_type", "不明")}')
        print(f'   内容: {note["content"][:100]}...')

    if tomorrow_notes:
        print("\n=== 通知メッセージ ===")
        message = format_reminder_message(tomorrow_notes, "day_before")
        print(message)

        print("\n=== LINE通知が送信される内容 ===")
        print(f"対象ID数: 複数のLINEターゲットに送信")
        print(f"メッセージ長: {len(message)}文字")
    else:
        print("\n❌ 通知対象が見つかりません")


if __name__ == "__main__":
    main()
