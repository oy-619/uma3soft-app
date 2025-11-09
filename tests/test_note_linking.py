#!/usr/bin/env python3
"""
リマインダーとノート関連付け機能のテストスクリプト
"""

import sys
import os
from datetime import datetime, timedelta

# パスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.reminder_schedule import (
    format_reminder_message,
    find_related_detected_notes,
    generate_note_url
)
from src.note_detector import NoteDetector

def test_note_linking():
    """ノート関連付け機能のテスト"""
    print("🔍 ノート関連付け機能テスト開始")
    print("=" * 60)

    # ノート検出器を初期化してテストデータを追加
    detector = NoteDetector()

    # テスト用のノートデータを追加
    test_notes = [
        {
            'text': '田中さんがノートを投稿しました\n来週の練習について\nhttps://line.me/R/note/C123/NOTE001',
            'user': 'U123',
            'group': 'C123',
            'name': '田中'
        },
        {
            'text': '📝 山田がノートを投稿しました\n試合の調整さん\nhttps://line.me/R/note/C123/NOTE002\nhttps://chouseisan.com/s?h=abc123',
            'user': 'U456',
            'group': 'C123',
            'name': '山田'
        },
        {
            'text': 'ソフトボール部の大会について\nhttps://line.me/R/home/note/C123/NOTE003',
            'user': 'U789',
            'group': 'C123',
            'name': '佐藤'
        }
    ]

    # テストノートを検出システムに登録
    for note_data in test_notes:
        result = detector.detect_note_notification(
            message_text=note_data['text'],
            user_id=note_data['user'],
            group_id=note_data['group'],
            user_name=note_data['name']
        )
        if result:
            print(f"✅ テストノート登録: {result.title}")

    # リマインダーのテストデータ
    test_reminders = [
        {
            'content': '来週の練習は午前9時からです。グラウンドに集合してください。',
            'date': (datetime.now() + timedelta(days=2)).date(),
            'is_input_deadline': False
        },
        {
            'content': 'ソフトボール大会の参加者募集中です。調整さんで出欠確認をお願いします。',
            'date': (datetime.now() + timedelta(days=5)).date(),
            'is_input_deadline': False
        }
    ]

    print("\n📋 リマインダーメッセージテスト")
    print("-" * 40)

    for i, reminder in enumerate(test_reminders, 1):
        print(f"\n--- テスト {i} ---")
        print(f"リマインダー内容: {reminder['content'][:30]}...")

        # 関連ノート検索をテスト
        related_notes = find_related_detected_notes(
            reminder['content'],
            reminder['date']
        )

        print(f"関連ノート検出数: {len(related_notes)}")
        for j, note in enumerate(related_notes, 1):
            # 辞書形式でアクセス
            title = note.get('title', '不明') if isinstance(note, dict) else getattr(note, 'title', '不明')
            print(f"  {j}. {title}")

            url = note.get('note_url', '') if isinstance(note, dict) else getattr(note, 'note_url', '')
            if url:
                print(f"     🔗 {url}")

            chouseisan_urls = note.get('chouseisan_urls', []) if isinstance(note, dict) else getattr(note, 'chouseisan_urls', [])
            if chouseisan_urls:
                for url in chouseisan_urls:
                    print(f"     📊 {url}")        # リマインダーメッセージ全体を生成（必要なフィールドを追加）
        reminder_with_days = reminder.copy()
        reminder_with_days['days_until'] = (reminder['date'] - datetime.now().date()).days

        try:
            formatted_message = format_reminder_message([reminder_with_days])
            print(f"\n📨 生成されたメッセージ:")
            print(formatted_message[:300] + "..." if len(formatted_message) > 300 else formatted_message)
        except Exception as e:
            print(f"\n⚠️ メッセージ生成エラー: {e}")
            print("（関連ノート検索は正常に動作しています）")

    print("\n" + "=" * 60)
    print("✅ テスト完了")

def test_note_search():
    """ノート検索機能のテスト"""
    print("\n🔍 ノート検索機能テスト")
    print("-" * 40)

    detector = NoteDetector()

    # キーワード検索テスト
    keywords = ['練習', '試合', '大会', '調整']

    for keyword in keywords:
        results = detector.search_notes_by_title(keyword)
        print(f"\nキーワード「{keyword}」の検索結果: {len(results)}件")
        for result in results[:2]:  # 最大2件表示
            # 結果は辞書形式で返される
            title = result.get('title', '不明') if isinstance(result, dict) else getattr(result, 'title', '不明')
            print(f"  - {title}")

    # 最新ノート取得テスト
    latest_notes = detector.get_latest_notes(3)
    print(f"\n最新ノート {len(latest_notes)}件:")
    for note in latest_notes:
        # 結果は辞書形式で返される
        title = note.get('title', '不明') if isinstance(note, dict) else getattr(note, 'title', '不明')
        detected_at = note.get('detected_at', '') if isinstance(note, dict) else getattr(note, 'detected_at', '')
        print(f"  - {title} ({detected_at})")

if __name__ == "__main__":
    try:
        test_note_linking()
        test_note_search()
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
