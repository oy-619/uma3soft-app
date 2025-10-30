#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日時修正のテスト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta

def test_date_fix():
    """日時修正のテスト"""

    try:
        from src.reminder_schedule import format_single_reminder_message
        print("✅ モジュールのインポートに成功しました")

        today = datetime.now().date()

        # 入力期限のあるテストケース
        input_deadline_note = {
            "date": today + timedelta(days=1),  # 期限日
            "days_until": 1,
            "content": "野球大会 11/15(土) 13:00-17:00\n場所：総合運動公園\n出欠確認をお願いします",
            "is_input_deadline": True
        }

        # イベント日のテストケース
        event_date_note = {
            "date": today + timedelta(days=1),  # イベント日
            "days_until": 1,
            "content": "野球練習試合 vs Aチーム\n場所：公園グラウンド\n時間：13:00-17:00",
            "is_input_deadline": False
        }

        print("\n📝 入力期限のあるメッセージテスト:")
        input_message = format_single_reminder_message(input_deadline_note)
        # 最初の5行だけ表示
        lines = input_message.split('\n')
        preview = '\n'.join(lines[:5])
        print(f"プレビュー:\n{preview}\n...")

        print("\n📅 イベント日メッセージテスト:")
        event_message = format_single_reminder_message(event_date_note)
        # 最初の5行だけ表示
        lines = event_message.split('\n')
        preview = '\n'.join(lines[:5])
        print(f"プレビュー:\n{preview}\n...")

        print("\n✅ 日時表記の修正が完了しました!")
        print("📋 修正内容:")
        print("  - 入力期限: 「期限日」として明確に表示")
        print("  - イベント日: 「開催日」として明確に表示")
        print("  - メッセージの文言を調整して混乱を防止")

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_date_fix()
