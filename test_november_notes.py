#!/usr/bin/env python3
"""
2025年11月1日（土）のノート情報をDBから検索してリマインドメッセージを作成するテスト

このテストでは以下を実施：
1. note_detector.pyを使用してデータベースを初期化
2. 2025年11月1日の模擬ノートデータを追加
3. 日付ベースの検索機能を実装
4. 検索されたノートからリマインドメッセージを作成
5. 天気情報統合の動作確認
"""

import sys
import os
from datetime import datetime, date

# プロジェクトのsrcディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from note_detector import NoteDetector, NoteInfo
from enhanced_reminder_messages import EnhancedReminderMessageGenerator

def create_test_notes_for_november():
    """2025年11月1日のテストノートデータを作成"""
    test_notes = [
        NoteInfo(
            note_id="test_note_001",
            note_url="https://line.me/R/note/group001/note001",
            group_id="group001",
            user_id="user001",
            user_name="田中太郎",
            title="【重要】プロジェクト打ち合わせ - 11月1日（土）15:00〜",
            detected_at="2025-11-01T10:30:00",
            message_text="プロジェクト打ち合わせのノートを作成しました。11月1日（土）15:00から会議室Aで開催します。"
        ),
        NoteInfo(
            note_id="test_note_002",
            note_url="https://line.me/R/note/group001/note002",
            group_id="group001",
            user_id="user002",
            user_name="佐藤花子",
            title="忘年会の日程調整 - 2025年11月1日締切",
            detected_at="2025-11-01T14:20:00",
            message_text="忘年会の日程調整です。https://chouseisan.com/s?h=abc123def456 こちらのURLから回答をお願いします。"
        ),
        NoteInfo(
            note_id="test_note_003",
            note_url="https://line.me/R/note/group002/note003",
            group_id="group002",
            user_id="user003",
            user_name="山田次郎",
            title="資料準備のお知らせ - 11月1日分",
            detected_at="2025-11-01T16:45:00",
            message_text="明日のプレゼン用資料を準備しました。確認をお願いします。"
        )
    ]
    return test_notes

def search_notes_by_date(note_detector: NoteDetector, target_date: str) -> list:
    """
    指定された日付のノートを検索する

    Args:
        note_detector: NoteDetectorインスタンス
        target_date: 検索対象日付 (YYYY-MM-DD形式)

    Returns:
        list: 該当するノート情報のリスト
    """
    results = []

    for note in note_detector.notes_db:
        try:
            # detected_atから日付部分を抽出
            note_date = datetime.fromisoformat(note.detected_at).date()
            target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()

            if note_date == target_date_obj:
                results.append(note)
        except Exception as e:
            print(f"日付解析エラー: {note.detected_at} - {e}")
            continue

    # 時刻順でソート
    results.sort(key=lambda x: x.detected_at)
    return results

def create_reminder_message_from_notes(notes: list, reminder_system: EnhancedReminderMessageGenerator) -> dict:
    """
    検索されたノートからリマインドメッセージを作成

    Args:
        notes: ノート情報リスト
        reminder_system: EnhancedReminderSystemインスタンス

    Returns:
        dict: 作成されたリマインドメッセージ
    """
    if not notes:
        return {
            "type": "text",
            "text": "📝 2025年11月1日のノート情報は見つかりませんでした。"
        }

    # メッセージ内容を構築
    message_parts = [
        "📅 2025年11月1日（土）のノート情報",
        f"📊 検索結果: {len(notes)}件のノートが見つかりました\n"
    ]

    for i, note in enumerate(notes, 1):
        time_str = datetime.fromisoformat(note.detected_at).strftime("%H:%M")
        message_parts.append(f"{i}. 【{time_str}】{note.title}")
        message_parts.append(f"   👤 {note.user_name}")

        # 調整さんURLが含まれている場合
        if "chouseisan.com" in note.message_text:
            message_parts.append("   📋 日程調整URLが含まれています")

        message_parts.append("")  # 空行

    # 天気情報を追加（東京の天気を例として）
    try:
        # openweather_serviceを直接インポートして使用
        from openweather_service import get_weather_for_location
        weather_data = get_weather_for_location("東京都")
        if weather_data and 'temperature' in weather_data:
            message_parts.append("🌤️ 現在の天気情報（東京）")
            message_parts.append(f"気温: {weather_data.get('temperature', 'N/A')}°C")
            message_parts.append(f"天気: {weather_data.get('description', 'N/A')}")
            message_parts.append(f"湿度: {weather_data.get('humidity', 'N/A')}%")
            message_parts.append(f"風速: {weather_data.get('wind_speed', 'N/A')}km/h")
        else:
            message_parts.append("🌤️ 天気情報の取得に失敗しました")
    except Exception as e:
        message_parts.append(f"🌤️ 天気情報取得エラー: {e}")

    return {
        "type": "text",
        "text": "\n".join(message_parts)
    }

def main():
    """メイン処理"""
    print("=" * 60)
    print("2025年11月1日（土）ノート検索・リマインドメッセージ作成テスト")
    print("=" * 60)

    # 1. NoteDetectorを初期化
    print("\n1. NoteDetectorを初期化中...")
    note_detector = NoteDetector(storage_file="test_november_notes.json")

    # 2. テストデータを追加
    print("\n2. 2025年11月1日のテストノートデータを追加中...")
    test_notes = create_test_notes_for_november()

    for note in test_notes:
        note_detector.notes_db.append(note)

    note_detector.save_notes_db()
    print(f"   追加完了: {len(test_notes)}件のテストノートを追加")

    # 3. 日付ベース検索を実行
    print("\n3. 2025年11月1日のノートを検索中...")
    target_date = "2025-11-01"
    found_notes = search_notes_by_date(note_detector, target_date)

    print(f"   検索結果: {len(found_notes)}件のノートが見つかりました")

    # 検索結果の詳細表示
    for i, note in enumerate(found_notes, 1):
        time_str = datetime.fromisoformat(note.detected_at).strftime("%H:%M")
        print(f"   {i}. [{time_str}] {note.title} (投稿者: {note.user_name})")

    # 4. EnhancedReminderMessageGeneratorを初期化
    print("\n4. EnhancedReminderMessageGeneratorを初期化中...")
    reminder_system = EnhancedReminderMessageGenerator()

    # 5. リマインドメッセージを作成
    print("\n5. リマインドメッセージを作成中...")
    reminder_message = create_reminder_message_from_notes(found_notes, reminder_system)

    # 6. 結果表示
    print("\n6. 作成されたリマインドメッセージ:")
    print("-" * 50)
    print(reminder_message['text'])
    print("-" * 50)

    # 7. 天気情報統合の個別テスト
    print("\n7. 天気情報統合の個別テスト:")
    try:
        from openweather_service import get_weather_for_location
        weather_data = get_weather_for_location("東京都")
        if weather_data and 'temperature' in weather_data:
            print("   ✅ 天気情報の取得成功")
            print(f"   📍 場所: {weather_data.get('location', 'N/A')}")
            print(f"   🌡️ 気温: {weather_data.get('temperature', 'N/A')}°C")
            print(f"   ☁️ 天気: {weather_data.get('description', 'N/A')}")
            print(f"   💧 湿度: {weather_data.get('humidity', 'N/A')}%")
            print(f"   💨 風速: {weather_data.get('wind_speed', 'N/A')}km/h")
            print(f"   ☁️ 雲量: {weather_data.get('clouds', 'N/A')}%")
        else:
            print("   ❌ 天気情報の取得失敗")
            print(f"   取得データ: {weather_data}")
    except Exception as e:
        print(f"   ❌ 天気情報取得エラー: {e}")

    print("\n" + "=" * 60)
    print("テスト完了")
    print("=" * 60)

if __name__ == "__main__":
    main()
