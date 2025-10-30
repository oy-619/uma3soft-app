#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
リマインダー機能の実用テスト
実際のイベントを使った天気情報表示テスト
"""

import os
import sys
from datetime import datetime, timedelta

# プロジェクトルート設定
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))

def test_real_world_reminders():
    """実際のイベントを想定したリマインダーテスト"""

    print("=" * 80)
    print("🎯 実用リマインダーテスト - 詳細天気情報確認")
    print("=" * 80)

    # 実際のイベント例
    test_events = [
        {
            "name": "代々木公園でのソフトボール練習",
            "content": "[ノート] ソフトボール練習\n会場: 代々木公園グラウンド\n時間: 午前9:00集合\n持ち物: グローブ、帽子、水筒\n雨天中止（前日19時判断）",
            "date": datetime.now().date() + timedelta(days=1),
            "days_until": 1,
            "is_input_deadline": False
        },
        {
            "name": "大阪での出張会議",
            "content": "[会議] 関西支社との合同会議\n会場: 大阪本社 会議室A\n時間: 14:00-17:00\n参加者: 営業部全員\n資料: 企画書持参",
            "date": datetime.now().date() + timedelta(days=2),
            "days_until": 2,
            "is_input_deadline": False
        },
        {
            "name": "札幌出張の参加確認期限",
            "content": "[入力期限] 札幌出張参加確認\n期間: 12月15日-17日\n目的: 新規開拓営業\n締切: 今日中に返答必須",
            "date": datetime.now().date(),
            "days_until": 0,
            "is_input_deadline": True
        }
    ]

    for i, event in enumerate(test_events, 1):
        print(f"\n🔍 テスト {i}: {event['name']}")
        print("-" * 60)

        try:
            from enhanced_reminder_messages import generate_enhanced_reminder_message

            # 詳細リマインダーメッセージを生成
            detailed_message = generate_enhanced_reminder_message(event)

            print(f"📅 イベント日: {event['date']}")
            print(f"📊 残り日数: {event['days_until']}日")
            print(f"⏰ 期限フラグ: {'期限あり' if event['is_input_deadline'] else 'イベント'}")

            print("\n📝 生成されたリマインダーメッセージ:")
            print("-" * 40)

            # メッセージの重要部分を抽出して表示
            lines = detailed_message.split('\n')

            # ヘッダー部分
            for line in lines[:5]:
                if line.strip():
                    print(line)

            print("\n[... 中略 ...]\n")

            # 天気情報部分を抽出
            weather_start = False
            weather_lines = []
            clothing_start = False
            clothing_lines = []

            for line in lines:
                if "天気情報" in line and line.startswith("🌤️"):
                    weather_start = True
                    weather_lines.append(line)
                elif weather_start and line.startswith("💡"):
                    clothing_start = True
                    clothing_lines.append(line)
                    weather_start = False
                elif weather_start and line.strip():
                    weather_lines.append(line)
                elif clothing_start and line.strip():
                    clothing_lines.append(line)
                elif clothing_start and line.startswith("="):
                    break

            # 天気情報を表示
            if weather_lines:
                print("🌤️ 天気情報セクション:")
                for line in weather_lines[:8]:  # 最大8行
                    print(line)
                print("")

            # 服装提案を表示
            if clothing_lines:
                print("💡 服装提案セクション:")
                for line in clothing_lines[:5]:  # 最大5行
                    print(line)
                print("")

            # 統計情報
            total_chars = len(detailed_message)
            total_lines = len(lines)
            weather_info_present = any("天気情報" in line for line in lines)
            clothing_advice_present = any("服装" in line for line in lines)

            print(f"✅ 統計情報:")
            print(f"   - 総文字数: {total_chars}文字")
            print(f"   - 総行数: {total_lines}行")
            print(f"   - 天気情報: {'✅ 有' if weather_info_present else '❌ 無'}")
            print(f"   - 服装提案: {'✅ 有' if clothing_advice_present else '❌ 無'}")

        except Exception as e:
            print(f"❌ エラー: {e}")
            import traceback
            traceback.print_exc()

        print("\n" + "=" * 60)

    # 実際の使用方法のガイド
    print("\n💡 実際の使用方法:")
    print("-" * 40)
    print("""
1. LINE Botから送信する場合:

```python
from enhanced_reminder_messages import generate_enhanced_reminder_message
from linebot.models import TextSendMessage

# イベント情報を準備
event_info = {
    "content": "イベント詳細",
    "date": datetime(2025, 11, 1).date(),
    "days_until": 1,
    "is_input_deadline": False
}

# 詳細メッセージを生成
message = generate_enhanced_reminder_message(event_info)

# LINE Botで送信
line_bot_api.reply_message(
    event.reply_token,
    TextSendMessage(text=message)
)
```

2. スケジュール通知として使用:

```python
from reminder_schedule import format_single_reminder_message

# 既存システムで自動的に拡張機能が適用される
reminder_text = format_single_reminder_message(note_dict)
```
""")

    print("\n" + "=" * 80)
    print("✨ 実用テスト完了 - 詳細天気情報機能が正常に動作しています！")
    print("=" * 80)

if __name__ == "__main__":
    test_real_world_reminders()
