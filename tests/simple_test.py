#!/usr/bin/env python3
"""
簡単なノート関連付け機能テスト
"""

import sys
import os
from datetime import datetime, timedelta

# パスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_note_detector_basic():
    """基本的なノート検出のテスト"""
    print("🔍 基本ノート検出テスト")
    print("=" * 40)

    try:
        from src.note_detector import NoteDetector
        detector = NoteDetector()

        # データ形式を確認
        latest_notes = detector.get_latest_notes(2)
        print(f"最新ノート数: {len(latest_notes)}")

        for i, note in enumerate(latest_notes, 1):
            print(f"{i}. タイプ: {type(note)}")
            if isinstance(note, dict):
                print(f"   タイトル: {note.get('title', 'N/A')}")
                print(f"   URL: {note.get('note_url', 'N/A')}")
            else:
                print(f"   タイトル: {getattr(note, 'title', 'N/A')}")
                print(f"   URL: {getattr(note, 'note_url', 'N/A')}")

        print("✅ 基本テスト完了")

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

def test_search_function():
    """検索機能のテスト"""
    print("\n🔍 検索機能テスト")
    print("=" * 40)

    try:
        from src.note_detector import NoteDetector
        detector = NoteDetector()

        # キーワード検索
        results = detector.search_notes_by_title("練習")
        print(f"「練習」の検索結果: {len(results)}件")

        for result in results:
            print(f"結果タイプ: {type(result)}")
            if isinstance(result, dict):
                print(f"  - {result.get('title', 'N/A')}")

        print("✅ 検索テスト完了")

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_note_detector_basic()
    test_search_function()
