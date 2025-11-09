#!/usr/bin/env python3
"""
ノート関連付け機能の個別テスト（スケジューラーなし）
"""

import sys
import os
from datetime import datetime, timedelta

# パスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_find_related_notes():
    """関連ノート検索機能の単体テスト"""
    print("🔍 関連ノート検索テスト")
    print("=" * 40)

    try:
        # reminder_schedule.pyのfind_related_detected_notes関数のみをテスト
        from src.reminder_schedule import find_related_detected_notes

        # テスト用の日付
        test_date = datetime.now().date() + timedelta(days=2)

        # テスト用のリマインダー内容
        test_contents = [
            "来週の練習は午前9時からです。グラウンドに集合してください。",
            "ソフトボール大会の参加者募集中です。調整さんで出欠確認をお願いします。",
            "次回の試合について確認をお願いします。"
        ]

        for i, content in enumerate(test_contents, 1):
            print(f"\n--- テスト {i} ---")
            print(f"内容: {content[:30]}...")

            # 関連ノート検索
            related_notes = find_related_detected_notes(content, test_date)

            print(f"検出された関連ノート数: {len(related_notes)}")
            for j, note in enumerate(related_notes, 1):
                title = note.get('title', '不明') if isinstance(note, dict) else getattr(note, 'title', '不明')
                url = note.get('note_url', '') if isinstance(note, dict) else getattr(note, 'note_url', '')
                print(f"  {j}. {title}")
                if url:
                    print(f"     🔗 {url}")

        print("\n✅ 関連ノート検索テスト完了")

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

def test_note_detector_only():
    """ノート検出器のみのテスト"""
    print("\n🔍 ノート検出器単体テスト")
    print("=" * 40)

    try:
        from src.note_detector import NoteDetector

        detector = NoteDetector()

        # 最新ノート取得テスト
        latest_notes = detector.get_latest_notes(3)
        print(f"最新ノート数: {len(latest_notes)}")

        for i, note in enumerate(latest_notes, 1):
            print(f"{i}. {note.get('title', 'N/A')} (タイプ: {type(note).__name__})")

        # キーワード検索テスト
        search_results = detector.search_notes_by_title("練習")
        print(f"\n「練習」検索結果: {len(search_results)}件")

        for result in search_results:
            print(f"  - {result.get('title', 'N/A')} (タイプ: {type(result).__name__})")

        print("\n✅ ノート検出器テスト完了")

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_note_detector_only()
    test_find_related_notes()
