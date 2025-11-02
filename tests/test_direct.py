#!/usr/bin/env python3
"""
関連ノート検索機能の直接テスト
"""

import sys
import os
from datetime import datetime, timedelta

# パスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def direct_test():
    """関連ノート検索を直接実装してテスト"""
    print("🔍 関連ノート検索直接テスト")
    print("=" * 40)

    try:
        from src.note_detector import NoteDetector

        # ノート検出器を初期化
        detector = NoteDetector()

        # テスト用のリマインダー内容
        reminder_content = "来週の練習は午前9時からです。グラウンドに集合してください。"
        event_date = (datetime.now() + timedelta(days=2)).date()

        print(f"テスト内容: {reminder_content[:30]}...")
        print(f"イベント日: {event_date}")

        # キーワード抽出（find_related_detected_notes関数の一部を再現）
        keywords = []
        content_lower = reminder_content.lower()

        # ソフトボール関連キーワード
        softball_keywords = ["練習", "試合", "大会", "ソフトボール", "調整", "出欠", "参加", "集合"]
        for keyword in softball_keywords:
            if keyword in content_lower:
                keywords.append(keyword)

        print(f"抽出されたキーワード: {keywords}")

        # 各キーワードで検索
        related_notes = []
        for keyword in keywords:
            print(f"\nキーワード「{keyword}」で検索...")
            notes = detector.search_notes_by_title(keyword)
            print(f"  検索結果: {len(notes)}件")

            for note in notes[:2]:  # 最大2件
                if note not in related_notes:
                    related_notes.append(note)
                    print(f"  追加: {note.get('title', 'N/A')}")

        print(f"\n最終結果: {len(related_notes)}件の関連ノート")
        for i, note in enumerate(related_notes, 1):
            print(f"{i}. {note.get('title', 'N/A')}")
            print(f"   URL: {note.get('note_url', 'N/A')}")

        print("\n✅ 直接テスト完了")

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    direct_test()
