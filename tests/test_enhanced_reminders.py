#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拡張リマインダーメッセージのテスト
"""

import os
import sys
import json
from datetime import datetime, timedelta

# プロジェクトルート設定
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))

def test_enhanced_reminder_messages():
    """拡張リマインダーメッセージのテスト"""

    print("=" * 80)
    print("🧪 拡張リマインダーメッセージ機能テスト")
    print("=" * 80)

    # テストケース1: 明日のソフトボール練習（屋外イベント）
    test_case_1 = {
        "content": "[ノート] 11月15日(金) ソフトボール練習試合\n会場: 代々木公園グラウンド\n集合時間: 午前9:00\n持ち物: グローブ、帽子、飲み物\n雨天中止の場合は当日朝7:00にLINEでお知らせします",
        "date": datetime.now().date() + timedelta(days=1),  # 明日
        "days_until": 1,
        "is_input_deadline": False
    }

    # テストケース2: 本日期限の入力依頼
    test_case_2 = {
        "content": "[入力期限] 12月忘年会の出席確認\n日時: 12月20日(金) 18:00-21:00\n会場: 〇〇ホテル 宴会場\n会費: 5,000円\n締切: 11月15日(金)まで",
        "date": datetime.now().date(),  # 本日
        "days_until": 0,
        "is_input_deadline": True
    }

    # テストケース3: 2日後の屋内会議
    test_case_3 = {
        "content": "[会議] 月次定例会議\n日時: 11月17日(日) 13:00-15:00\n場所: 会議室A\n議題: 来月の活動計画について\n参加者: 役員および希望者",
        "date": datetime.now().date() + timedelta(days=2),  # 2日後
        "days_until": 2,
        "is_input_deadline": False
    }

    test_cases = [
        ("明日のソフトボール練習（屋外）", test_case_1),
        ("本日期限の入力依頼", test_case_2),
        ("2日後の屋内会議", test_case_3)
    ]

    for case_name, note_info in test_cases:
        print(f"\n🔍 テストケース: {case_name}")
        print("-" * 60)

        try:
            # 拡張リマインダーメッセージのテスト
            from enhanced_reminder_messages import generate_enhanced_reminder_message, generate_enhanced_flex_message

            print("\n📝 拡張リマインダーメッセージ:")
            print("-" * 30)
            enhanced_message = generate_enhanced_reminder_message(note_info)
            print(enhanced_message)

            print("\n📱 Flex Message JSON:")
            print("-" * 30)
            flex_data = generate_enhanced_flex_message(note_info)
            print(json.dumps(flex_data, ensure_ascii=False, indent=2)[:500] + "..." if len(json.dumps(flex_data, ensure_ascii=False, indent=2)) > 500 else json.dumps(flex_data, ensure_ascii=False, indent=2))

        except Exception as e:
            print(f"❌ エラー: {e}")
            import traceback
            traceback.print_exc()

        print("\n" + "=" * 60)

    # 統合テスト: reminder_schedule.pyとの連携
    print("\n🔗 統合テスト: reminder_schedule.pyとの連携")
    print("-" * 60)

    try:
        from reminder_schedule import format_single_reminder_message, create_flex_reminder_message

        test_note = {
            'content': test_case_1["content"],
            'date': test_case_1["date"],
            'days_until': test_case_1["days_until"],
            'is_input_deadline': test_case_1["is_input_deadline"]
        }

        print("\n📝 統合メッセージ:")
        print("-" * 30)
        integrated_message = format_single_reminder_message(test_note)
        print(integrated_message[:800] + "..." if len(integrated_message) > 800 else integrated_message)

        print("\n📱 統合Flex Message:")
        print("-" * 30)
        integrated_flex = create_flex_reminder_message(test_note)
        print("Flex Message構造が正常に生成されました")
        print(f"Type: {integrated_flex.get('type')}")
        print(f"Header: {integrated_flex.get('header', {}).get('contents', [{}])[0].get('text', 'N/A')}")

    except Exception as e:
        print(f"❌ 統合テストエラー: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("✅ テスト完了")
    print("=" * 80)

if __name__ == "__main__":
    test_enhanced_reminder_messages()
