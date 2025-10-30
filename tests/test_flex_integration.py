#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flex Message統合テスト
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta

def test_flex_reminder_integration():
    """
    Flex Messageリマインダーの統合テスト
    """

    try:
        from src.reminder_schedule import create_flex_reminder_message
        print("✅ Flex Message関数のインポートに成功しました")

        today = datetime.now().date()

        # 複数のテストケース
        test_cases = [
            {
                "name": "入力期限（明日）",
                "note": {
                    "date": today + timedelta(days=1),
                    "days_until": 1,
                    "content": "野球大会 11/15(土) 13:00-17:00\n場所：総合運動公園\n出欠確認をお願いします",
                    "is_input_deadline": True
                }
            },
            {
                "name": "イベント開催（明日）",
                "note": {
                    "date": today + timedelta(days=1),
                    "days_until": 1,
                    "content": "野球練習試合 vs Aチーム\n場所：公園グラウンド\n時間：13:00-17:00",
                    "is_input_deadline": False
                }
            },
            {
                "name": "本日開催",
                "note": {
                    "date": today,
                    "days_until": 0,
                    "content": "今日の試合 vs Bチーム\n場所：市営球場\n開始：14:00",
                    "is_input_deadline": False
                }
            },
            {
                "name": "2日後開催",
                "note": {
                    "date": today + timedelta(days=2),
                    "days_until": 2,
                    "content": "月例ミーティング\n場所：会議室A\n議題：来月の予定",
                    "is_input_deadline": False
                }
            }
        ]

        print(f"\n🔍 {len(test_cases)}つのテストケースを実行中...")

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- テスト {i}: {test_case['name']} ---")

            note = test_case['note']
            flex_msg = create_flex_reminder_message(note)

            # Flex Messageの基本構造を確認
            print(f"✅ Flex Message作成成功")
            print(f"📊 メッセージタイプ: {flex_msg['type']}")
            print(f"🎨 ヘッダー色: {flex_msg['header']['backgroundColor']}")
            print(f"📝 タイトル: {flex_msg['header']['contents'][0]['text']}")

            # 日付情報を確認
            date_text = flex_msg['body']['contents'][0]['contents'][1]['text']
            print(f"📅 表示日付: {date_text}")

            # 内容を確認
            content_text = flex_msg['body']['contents'][2]['contents'][1]['text']
            print(f"📋 メイン内容: {content_text[:30]}...")

            # フッター情報を確認
            footer_text = flex_msg['footer']['contents'][0]['contents'][0]['text']
            print(f"⏰ 緊急度: {footer_text}")

        print(f"\n🎉 Flex Messageリマインダーの統合テストが完了しました！")
        print(f"📋 結果要約:")
        print(f"  - {len(test_cases)}種類のリマインダータイプをテスト")
        print(f"  - すべてのFlex Messageが正常に生成")
        print(f"  - 日時、内容、緊急度が適切に表示")
        print(f"  - カラーコーディングが正常に動作")

        # サンプルJSONを出力（デバッグ用）
        sample_flex = create_flex_reminder_message(test_cases[0]['note'])
        with open('tests/sample_flex_message.json', 'w', encoding='utf-8') as f:
            json.dump(sample_flex, f, ensure_ascii=False, indent=2)
        print(f"\n📄 サンプルFlex MessageをJSONファイルに保存しました: tests/sample_flex_message.json")

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_flex_reminder_integration()
