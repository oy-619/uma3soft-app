#!/usr/bin/env python3
"""
詳細なノート検索デバッグテスト
"""

import sys
import os

# パスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def debug_search():
    """検索機能の詳細デバッグ"""
    print("🔍 詳細検索デバッグ")

    try:
        from src.note_detector import NoteDetector
        from dataclasses import asdict

        detector = NoteDetector()

        # 直接search_notes_by_titleメソッドを呼び出し
        print("直接メソッド呼び出し:")
        results = detector.search_notes_by_title("練習")
        print(f"結果の数: {len(results)}")

        for i, result in enumerate(results):
            print(f"結果 {i+1}:")
            print(f"  タイプ: {type(result)}")
            print(f"  内容: {result}")

            if hasattr(result, 'title'):
                print(f"  title属性: {result.title}")
            if isinstance(result, dict):
                print(f"  辞書のtitle: {result.get('title')}")

        # notes_dbの中身も確認
        print(f"\nnotes_dbの中身: {len(detector.notes_db)}件")
        for i, note in enumerate(detector.notes_db[:2]):
            print(f"ノート {i+1}: {type(note)} - {note.title}")

            # asdictで変換テスト
            dict_note = asdict(note)
            print(f"  asdict結果: {type(dict_note)} - {dict_note.get('title')}")

    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_search()
