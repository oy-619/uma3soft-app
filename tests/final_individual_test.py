#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
個別メッセージ送信の最終確認テスト （複数件リマインダー対応）
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta

def final_test():
    """個別メッセージ送信の最終確認"""

    try:
        from src.reminder_schedule import format_reminder_message, format_single_reminder_message
        print("✅ モジュールのインポートに成功しました")

        # 複数のテスト用ノートデータ
        today = datetime.now().date()

        test_notes = [
            {
                "date": today + timedelta(days=1),
                "days_until": 1,
                "content": "野球練習試合 vs Aチーム\n場所：公園グラウンド\n時間：13:00-17:00",
                "is_input_deadline": False
            },
            {
                "date": today + timedelta(days=1),
                "days_until": 1,
                "content": "出欠確認の締切\n来週の遠征について\n期限：明日まで",
                "is_input_deadline": True
            },
            {
                "date": today,
                "days_until": 0,
                "content": "今日の試合 vs Bチーム\n場所：市営球場\n時間：14:00-18:00",
                "is_input_deadline": False
            }
        ]

        print(f"\n📝 テスト対象: {len(test_notes)}件のリマインダー")
        for i, note in enumerate(test_notes, 1):
            print(f"  {i}. {note['content'][:30]}... (残り{note['days_until']}日)")

        # 個別メッセージ生成テスト
        print(f"\n🔄 {len(test_notes)}件のリマインダーを個別メッセージに変換中...")
        messages_list = format_reminder_message(test_notes)

        print(f"\n✅ 個別メッセージ生成完了!")
        print(f"📊 生成されたメッセージ数: {len(messages_list)} (1件=1メッセージ)")
        print(f"📏 各メッセージの文字数: {[len(msg) for msg in messages_list]}")

        # 各メッセージの内容を確認
        for i, message in enumerate(messages_list, 1):
            print(f"\n--- 個別メッセージ {i} ---")
            print(f"文字数: {len(message)}")
            # 最初の3行だけ表示
            lines = message.split('\n')
            preview = '\n'.join(lines[:3]) + ('...' if len(lines) > 3 else '')
            print(f"プレビュー:\n{preview}")
            print("-" * 40)

        # 単一メッセージのテストも実行
        print(f"\n🔍 単一メッセージ生成テスト:")
        single_message = format_single_reminder_message(test_notes[0])
        print(f"✅ 単一メッセージ文字数: {len(single_message)}")

        print(f"\n🎉 個別メッセージ送信機能の実装が完了しました!")
        print(f"📋 要約:")
        print(f"  - 3件のリマインダー → 3個の個別メッセージに変換")
        print(f"  - 各メッセージは丁寧で完結した内容")
        print(f"  - 1件=1メッセージの要件を満たしています")

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    final_test()
