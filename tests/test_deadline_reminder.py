#!/usr/bin/env python3
"""
入力期限ベースのリマインダー機能をテストするスクリプト
"""

import os
import sys
from datetime import datetime, timedelta

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from reminder_schedule import (
    format_reminder_message,
    get_next_day_reminders,
    get_upcoming_deadline_notes,
)


def test_deadline_reminder():
    """入力期限ベースのリマインダー機能をテスト"""
    print("=== 入力期限ベースのリマインダーテスト ===")
    print(f"現在日時: {datetime.now()}")
    print(f"明日の日付: {(datetime.now() + timedelta(days=1)).date()}")
    print()

    # 1. 明日が入力期限のノートを検索
    print("1. 明日が入力期限のノート検索:")
    try:
        tomorrow_notes = get_next_day_reminders()
        print(f"見つかったノート数: {len(tomorrow_notes)}")

        for i, note in enumerate(tomorrow_notes, 1):
            print(f"\n--- ノート {i} ---")
            print(f"日付: {note['date']}")
            print(f"日数: {note['days_until']}日後")
            print(f"入力期限: {note.get('is_input_deadline', False)}")
            print(f"内容: {note['content'][:200]}...")

        if tomorrow_notes:
            print(f"\n2. メッセージ整形テスト:")
            message = format_reminder_message(tomorrow_notes)
            print("--- 整形されたメッセージ ---")
            print(message)
        else:
            print("\n⚠️ 明日が入力期限のノートは見つかりませんでした")

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback

        traceback.print_exc()

    # 3. 今後7日間の入力期限を確認
    print(f"\n3. 今後7日間の入力期限:")
    try:
        upcoming_notes = get_upcoming_deadline_notes(days_ahead=7)
        print(f"見つかったノート数: {len(upcoming_notes)}")

        for i, note in enumerate(upcoming_notes, 1):
            deadline_type = (
                "入力期限" if note.get("is_input_deadline", False) else "イベント日"
            )
            print(f"{i}. {note['date']} ({note['days_until']}日後) [{deadline_type}]")
            print(f"   {note['content'][:100]}...")

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_deadline_reminder()
    print("\n=== テスト完了 ===")
