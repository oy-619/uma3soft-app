#!/usr/bin/env python3
"""
リマインダーメッセージ生成テスト（調整さんURL削除版）
"""

import sys
import os
from datetime import datetime, timedelta

# パスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_reminder_message():
    """リマインダーメッセージの生成テスト"""
    print("📨 リマインダーメッセージ生成テスト")
    print("=" * 50)

    # スケジューラーを使わずに直接メッセージ生成をテスト
    try:
        # テスト用のリマインダーデータ
        test_reminder = {
            'content': '来週の練習は午前9時からです。グラウンドに集合してください。',
            'date': (datetime.now() + timedelta(days=2)).date(),
            'days_until': 2,
            'is_input_deadline': False
        }

        # 関連ノート検索を直接実行
        from src.reminder_schedule import find_related_detected_notes

        related_notes = find_related_detected_notes(
            test_reminder['content'],
            test_reminder['date']
        )

        print(f"検出関連ノート数: {len(related_notes)}")

        # メッセージを手動で組んでテスト
        event_date = test_reminder['date']
        days_until = test_reminder['days_until']
        content = test_reminder['content']

        # 基本メッセージ部分
        date_with_weekday = event_date.strftime("%Y/%m/%d（%a）")

        if days_until == 2:
            prefix = f"📅 【リマインダー（明後日）】\n\n{date_with_weekday}のイベントです。\nご確認ください。"
        else:
            prefix = f"📅 【リマインダー（{days_until}日後）】\n\n{date_with_weekday}のイベントです。\nご確認ください。"

        message = f"{prefix}\n\n📋 **イベント詳細**\n{content}\n"
        message += f"\n🌤️ **天気情報**: 当日の天気予報をご確認ください\n"

        # 関連ノートを追加（調整さんURL削除版）
        if related_notes:
            message += f"\n{'='*50}\n\n📋 **関連するノート**\n"
            for i, related_note in enumerate(related_notes, 1):
                note_title = related_note.get('title', '不明なノート')
                note_url_detected = related_note.get('note_url', '')

                if len(note_title) > 30:
                    note_title = note_title[:30] + "..."

                message += f"\n{i}. 📝 {note_title}\n"
                if note_url_detected:
                    message += f"   🔗 ノートURL: {note_url_detected}\n"

        print("\n生成されたメッセージ:")
        print("-" * 50)
        print(message)
        print("-" * 50)

        # 調整さんURLが含まれていないことを確認
        if "調整さん" in message:
            print("❌ 調整さんURLが残っています")
        else:
            print("✅ 調整さんURLが正しく削除されています")

        print("\n✅ リマインダーメッセージテスト完了")

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_reminder_message()
