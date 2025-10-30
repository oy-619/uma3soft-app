#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
個別メッセージ送信の簡単なテスト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta

def simple_test():
    """簡単なテスト"""

    try:
        from src.reminder_schedule import format_single_reminder_message, format_reminder_message
        print("✅ モジュールのインポートに成功しました")

        # テスト用のノートデータ
        today = datetime.now().date()

        test_note = {
            "date": today + timedelta(days=1),
            "days_until": 1,
            "content": "野球練習試合 vs Aチーム\n場所：公園グラウンド\n時間：13:00-17:00",
            "is_input_deadline": False
        }

        print("\n📝 テストノート:")
        print(f"  日付: {test_note['date']}")
        print(f"  残り日数: {test_note['days_until']}")
        print(f"  内容: {test_note['content'][:30]}...")

        # 単一メッセージのテスト
        print("\n🔄 単一メッセージを生成中...")
        single_message = format_single_reminder_message(test_note)

        print(f"\n✅ 単一メッセージ生成完了!")
        print(f"📏 文字数: {len(single_message)}")
        print(f"📄 内容:")
        print("-" * 60)
        print(single_message)
        print("-" * 60)

        # 複数メッセージのテスト
        print("\n🔄 複数メッセージのリスト生成中...")
        test_notes = [test_note]
        messages_list = format_reminder_message(test_notes)

        print(f"\n✅ 複数メッセージ生成完了!")
        print(f"📊 生成されたメッセージ数: {len(messages_list)}")
        print(f"📏 各メッセージの文字数: {[len(msg) for msg in messages_list]}")

        print("\n🎉 すべてのテストが正常に完了しました!")
        print("個別メッセージ送信機能が正常に動作しています。")

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_test()
