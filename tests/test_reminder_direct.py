#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime

# reminder_schedule.pyがあるディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(__file__))

print("=== リマインダー機能直接テスト ===")
print(f"テスト実行時刻: {datetime.now()}")

try:
    # reminder_schedule.pyから関数をインポート
    from reminder_schedule import get_upcoming_deadline_notes, reminder_job

    print("✅ 関数のインポート成功")

    # 明日の期限を取得
    print("\n--- 明日の期限を検索 ---")
    results = get_upcoming_deadline_notes(days_ahead=1)

    print(f"見つかった期限付きノート数: {len(results)}")

    for i, note in enumerate(results):
        print(f"\n📅 ノート {i+1}:")
        print(f"  日付: {note['date']}")
        print(f"  残り日数: {note['days_until']}日")
        print(f"  内容: {note['content'][:150]}...")

    if results:
        print("\n--- リマインダージョブ実行 ---")
        # reminder_job()を直接実行
        reminder_job()
        print("✅ リマインダージョブ実行完了")
    else:
        print(
            "❌ 期限付きノートが見つからないため、リマインダージョブはスキップされます"
        )

except ImportError as e:
    print(f"❌ インポートエラー: {e}")
except Exception as e:
    print(f"❌ 実行エラー: {e}")
    import traceback

    traceback.print_exc()

print("\n=== テスト完了 ===")
