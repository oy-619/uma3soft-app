#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from reminder_flex_customizer import ReminderFlexCustomizer

def test_reminder_flex_system():
    """調整さん確認を主体とするリマインダーFlexシステムのテスト"""
    print("=" * 60)
    print("調整さん確認リマインダーFlexシステムのテスト開始")
    print("=" * 60)

    try:
        customizer = ReminderFlexCustomizer()
        print("✅ ReminderFlexCustomizer初期化成功")

        # テスト用ノートデータ（入力期限）
        test_note_deadline = {
            "content": """【大会情報】
場所：平和島公園野球場
時間：9:00集合、9:30試合開始
持ち物：グローブ、スパイク、帽子、水筒
費用：参加費500円
連絡：雨天の場合は前日夜に連絡します""",
            "date": datetime.now() + timedelta(days=2),
            "days_until": 2,
            "is_input_deadline": True
        }

        # テスト用ノートデータ（イベント開催日）
        test_note_event = {
            "content": """【練習試合】
会場：萩中公園野球場
集合時間：13:00
試合開始：13:30
注意事項：雨天中止の場合あり""",
            "date": datetime.now() + timedelta(days=1),
            "days_until": 1,
            "is_input_deadline": False
        }

        # モック天気Flex Message
        mock_weather_flex = {
            "type": "bubble",
            "contents": {
                "body": {
                    "contents": [
                        {
                            "type": "box",
                            "contents": [
                                {
                                    "type": "box",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "晴れ"
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "22.5℃"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        }

        # 入力期限リマインダーテスト
        print("\n📝 入力期限リマインダーテスト:")
        deadline_flex = customizer.customize_weather_flex_for_reminder(mock_weather_flex, test_note_deadline)
        print("✅ 入力期限リマインダーFlex生成成功")
        print(f"   タイトル: {deadline_flex['altText']}")
        print(f"   Type: {deadline_flex['contents']['type']}")

        # イベント開催日リマインダーテスト
        print("\n🎯 イベント開催日リマインダーテスト:")
        event_flex = customizer.customize_weather_flex_for_reminder(mock_weather_flex, test_note_event)
        print("✅ イベント開催日リマインダーFlex生成成功")
        print(f"   タイトル: {event_flex['altText']}")
        print(f"   Type: {event_flex['contents']['type']}")

        # 構造確認
        print(f"\n📊 構造確認:")
        print(f"   Header: {deadline_flex['contents'].get('header', {}).get('contents', [{}])[0].get('text', 'なし')}")
        print(f"   Footer: {'あり' if 'footer' in deadline_flex['contents'] else 'なし'}")

        # JSONファイルとして保存（確認用）
        with open('test_deadline_reminder.json', 'w', encoding='utf-8') as f:
            json.dump(deadline_flex, f, ensure_ascii=False, indent=2)

        with open('test_event_reminder.json', 'w', encoding='utf-8') as f:
            json.dump(event_flex, f, ensure_ascii=False, indent=2)

        print("\n" + "=" * 60)
        print("🎉 調整さん主体のリマインダーFlexシステムテスト完了！")
        print("主要コンテンツ：調整さんの確認と入力依頼")
        print("付属情報：天候情報（簡潔に表示）")
        print(f"生成ファイル: test_deadline_reminder.json, test_event_reminder.json")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_reminder_flex_system()
