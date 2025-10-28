#!/usr/bin/env python3
"""
デュアル通知システムのテスト
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# パスを追加
sys.path.append(str(Path(__file__).parent))

# reminder_schedule.pyから関数をインポート
from reminder_schedule import (
    format_reminder_message,
    get_reminders_for_day_after_tomorrow,
    get_reminders_for_tomorrow,
)


def test_dual_reminder_system():
    """デュアル通知システムのテスト"""
    print("=" * 60)
    print("🔍 デュアル通知システムのテスト")
    print("=" * 60)

    # 明日の通知をテスト
    print("\n1. 明日の通知テスト（入力期限 + イベント前日）")
    print("-" * 40)

    try:
        tomorrow_notes = get_reminders_for_tomorrow()
        print(f"✅ 明日の通知対象: {len(tomorrow_notes)}件")

        if tomorrow_notes:
            print("\n📝 明日の通知詳細:")
            for i, note in enumerate(tomorrow_notes, 1):
                is_input_deadline = note.get("is_input_deadline", False)
                deadline_type = "入力期限" if is_input_deadline else "イベント日"
                print(
                    f"  {i}. {deadline_type}: {note['date']} ({note['content'][:50]}...)"
                )

            # メッセージ形式テスト
            print("\n📨 通知メッセージ:")
            message = format_reminder_message(tomorrow_notes, "day_before")
            print(message)
        else:
            print("📭 明日の通知対象はありません")

    except Exception as e:
        print(f"❌ 明日の通知テストでエラー: {e}")
        import traceback

        traceback.print_exc()

    # 明後日の通知をテスト
    print("\n2. 明後日の通知テスト（イベント前々日）")
    print("-" * 40)

    try:
        day_after_tomorrow_notes = get_reminders_for_day_after_tomorrow()
        print(f"✅ 明後日の通知対象: {len(day_after_tomorrow_notes)}件")

        if day_after_tomorrow_notes:
            print("\n📝 明後日の通知詳細:")
            for i, note in enumerate(day_after_tomorrow_notes, 1):
                is_input_deadline = note.get("is_input_deadline", False)
                deadline_type = "入力期限" if is_input_deadline else "イベント日"
                print(
                    f"  {i}. {deadline_type}: {note['date']} ({note['content'][:50]}...)"
                )

            # メッセージ形式テスト
            print("\n📨 通知メッセージ:")
            message = format_reminder_message(
                day_after_tomorrow_notes, "two_days_before"
            )
            print(message)
        else:
            print("📭 明後日の通知対象はありません")

    except Exception as e:
        print(f"❌ 明後日の通知テストでエラー: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 60)
    print("🎯 デュアル通知システムテスト完了")
    print("=" * 60)


if __name__ == "__main__":
    test_dual_reminder_system()
