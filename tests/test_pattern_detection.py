#!/usr/bin/env python3
"""
入力期限検出ロジックの単体テスト
"""

import re
from datetime import datetime, timedelta


def test_deadline_patterns():
    """入力期限パターンの検出テスト"""
    print("=== 入力期限パターン検出テスト ===")
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    # テストデータ
    test_notes = [
        "[ノート] 10月27日(日) ＊入力期限：10/24(木) 【5年以下】 26日(土)の都大会1回戦に ■勝った場合 都大会準決勝 @柴又野球場 6:00 馬三小北側集合(車移動) 10:20～...",
        "[ノート] テストイベント 日時：2025/10/27(月) 11:00～15:00（17:00まで利用可） 場所：XX小学校 集合：10:30開場 監督会議 会場設営 備考：",
        "[ノート] 11月2日(土) ＊入力期限：10/30(水) 【黒】【白】 練習 @馬三小(9:00～12:00) →ガス橋5号面(14:00～16:00) 8:30 馬三小集合 9:00...",
        "[ノート] 大森リーグ若草ジュニア杯（3年生以下） 日時：2025/11/03(月祝) 11:00～15:00（17:00まで利用可） 場所：徳持小学校 集合：10:30開場 監督会議 会場設営",
    ]

    # 入力期限パターン
    deadline_patterns = [
        r"入力期限[：:]\s*(\d{4})/(\d{1,2})/(\d{1,2})\([月火水木金土日]\)",  # 入力期限：2025/10/24(木)
        r"入力期限[：:]\s*(\d{4})/(\d{1,2})/(\d{1,2})",  # 入力期限：2025/10/24
        r"入力期限[：:]\s*(\d{1,2})/(\d{1,2})\([月火水木金土日]\)",  # 入力期限：10/24(木)
        r"入力期限[：:]\s*(\d{1,2})/(\d{1,2})",  # 入力期限：10/24
        r"入力期限[：:]\s*(\d{1,2})月(\d{1,2})日",  # 入力期限：10月24日
    ]

    # イベント日付パターン
    event_patterns = [
        r"(\d{4})/(\d{1,2})/(\d{1,2})\([月火水木金土日]\)",  # 2025/10/27(月)形式
        r"(\d{4})/(\d{1,2})/(\d{1,2})",  # 2024/12/25形式
        r"(\d{1,2})月(\d{1,2})日",  # 12月25日形式
        r"(\d{1,2})/(\d{1,2})",  # 12/25形式
    ]

    for i, content in enumerate(test_notes, 1):
        print(f"\n--- テストノート {i} ---")
        print(f"内容: {content[:100]}...")

        found_deadline_dates = []
        found_event_dates = []

        # 入力期限を検索
        for pattern in deadline_patterns:
            matches = re.findall(pattern, content)
            if matches:
                print(f"入力期限パターン '{pattern}' マッチ: {matches}")
                for match in matches:
                    try:
                        if len(match) == 3:  # 年/月/日形式
                            year, month, day = map(int, match)
                            deadline_date = datetime(year, month, day).date()
                        elif len(match) == 2:
                            if "月" in pattern:  # 月日形式
                                month, day = map(int, match)
                                year = today.year
                                if month < today.month or (
                                    month == today.month and day < today.day
                                ):
                                    year += 1
                            else:  # MM/DD形式
                                month, day = map(int, match)
                                year = today.year
                                if month < today.month or (
                                    month == today.month and day < today.day
                                ):
                                    year += 1
                            deadline_date = datetime(year, month, day).date()

                        found_deadline_dates.append(deadline_date)
                        print(f"  → 入力期限: {deadline_date}")
                    except ValueError as e:
                        print(f"  → 日付解析エラー: {e}")

        # 入力期限が見つからない場合はイベント日付を検索
        if not found_deadline_dates:
            print("入力期限なし、イベント日付を検索...")
            for pattern in event_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    print(f"イベント日付パターン '{pattern}' マッチ: {matches}")
                    for match in matches:
                        try:
                            if len(match) == 3:  # 年/月/日形式
                                year, month, day = map(int, match)
                                event_date = datetime(year, month, day).date()
                            elif len(match) == 2:
                                if "月" in pattern:  # 月日形式
                                    month, day = map(int, match)
                                    year = today.year
                                    if month < today.month or (
                                        month == today.month and day < today.day
                                    ):
                                        year += 1
                                else:  # MM/DD形式
                                    month, day = map(int, match)
                                    year = today.year
                                    if month < today.month or (
                                        month == today.month and day < today.day
                                    ):
                                        year += 1
                                event_date = datetime(year, month, day).date()

                            found_event_dates.append(event_date)
                            print(f"  → イベント日付: {event_date}")
                        except ValueError as e:
                            print(f"  → 日付解析エラー: {e}")

        # 結果の確認
        all_dates = found_deadline_dates + found_event_dates
        is_input_deadline = len(found_deadline_dates) > 0

        print(f"検出された期限: {all_dates}")
        print(f"入力期限フラグ: {is_input_deadline}")

        # 明日が期限かチェック
        if tomorrow in all_dates:
            print(f"🔔 明日({tomorrow})が期限です！")
            if is_input_deadline:
                print("   → 入力期限のリマインダーを送信")
            else:
                print("   → イベント日のリマインダーを送信")


if __name__ == "__main__":
    test_deadline_patterns()
    print("\n=== テスト完了 ===")
