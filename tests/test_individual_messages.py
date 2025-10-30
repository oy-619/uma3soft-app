#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
個別メッセージ送信のテスト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from src.reminder_schedule import format_reminder_message, format_single_reminder_message

def test_individual_messages():
    """個別メッセージ送信のテスト"""

    # テスト用のノートデータ
    today = datetime.now().date()

    test_notes = [
        {
            "date": today + timedelta(days=1),
            "days_until": 1,
            "content": "野球練習試合 vs Aチーム\n場所：公園グラウンド\n時間：13:00-17:00",
            "is_input_deadline": False
        },
        {
            "date": today + timedelta(days=2),
            "days_until": 2,
            "content": "出欠確認の締切\n来週の遠征について",
            "is_input_deadline": True
        },
        {
            "date": today,
            "days_until": 0,
            "content": "今日の試合 vs Bチーム\n場所：市営球場",
            "is_input_deadline": False
        }
    ]

    print("=" * 60)
    print("【個別メッセージ送信テスト】")
    print("=" * 60)

    # 1. 単一メッセージのテスト
    print("\n1. 単一メッセージのテスト:")
    single_message = format_single_reminder_message(test_notes[0])
    print(f"メッセージ長: {len(single_message)}文字")
    print("-" * 40)
    print(single_message)
    print("-" * 40)

    # 2. 複数メッセージのリスト生成テスト
    print("\n2. 複数メッセージのリスト生成テスト:")
    messages_list = format_reminder_message(test_notes)

    print(f"生成されたメッセージ数: {len(messages_list)}")

    for i, message in enumerate(messages_list, 1):
        print(f"\n--- メッセージ {i} ---")
        print(f"文字数: {len(message)}")
        print(message)
        print("-" * 40)

    # 3. 入力期限メッセージのテスト
    print("\n3. 入力期限メッセージのテスト:")
    input_deadline_message = format_single_reminder_message(test_notes[1])
    print(f"メッセージ長: {len(input_deadline_message)}文字")
    print("-" * 40)
    print(input_deadline_message)
    print("-" * 40)

    # 4. 当日メッセージのテスト
    print("\n4. 当日メッセージのテスト:")
    today_message = format_single_reminder_message(test_notes[2])
    print(f"メッセージ長: {len(today_message)}文字")
    print("-" * 40)
    print(today_message)
    print("-" * 40)

    print("\n✅ テスト完了")
    print("各リマインダーが個別メッセージとして生成されました")

if __name__ == "__main__":
    test_individual_messages()
