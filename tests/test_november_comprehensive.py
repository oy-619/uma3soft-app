#!/usr/bin/env python3
"""
2025年11月1日（土）のノート情報をDBから検索してリマインドメッセージを作成するテスト（クリーン版）

このテストでは以下を実施：
1. 新しいデータベースファイルでクリーンな環境を作成
2. 2025年11月1日の模擬ノートデータを追加
3. 日付ベースの検索機能を実装
4. 検索されたノートからリマインドメッセージを作成
5. 天気情報統合の動作確認
6. Flex Messageカード形式のリマインダー作成
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
            message_text="プロジェクト打ち合わせのノートを作成しました。11月1日（土）15:00から会議室Aで開催します。場所：東京都渋谷区代々木公園"
        ),
        NoteInfo(
            note_id="test_note_002",
            note_url="https://line.me/R/note/group001/note002",
            group_id="group001",
            user_id="user002",
            user_name="佐藤花子",
            title="忘年会の日程調整 - 2025年11月1日締切",
            detected_at="2025-11-01T14:20:00",
            message_text="忘年会の日程調整です。https://chouseisan.com/s?h=abc123def456 こちらのURLから回答をお願いします。会場：新宿パークハイアット"
        ),
        NoteInfo(
            note_id="test_note_003",
            note_url="https://line.me/R/note/group002/note003",
            group_id="group002",
            user_id="user003",
            user_name="山田次郎",
            title="資料準備のお知らせ - 11月1日分",
            detected_at="2025-11-01T16:45:00",
            message_text="明日のプレゼン用資料を準備しました。確認をお願いします。場所：東京駅丸の内ビル"
        ),
        NoteInfo(
            note_id="test_note_004",
            note_url="https://line.me/R/note/group003/note004",
            group_id="group003",
            user_id="user004",
            user_name="鈴木一郎",
            title="【締切間近】報告書提出について",
            detected_at="2025-11-01T09:15:00",
            message_text="月次報告書の提出期限が近づいています。11月1日中の提出をお願いします。"
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

def create_comprehensive_reminder_message(notes: list, reminder_generator: EnhancedReminderMessageGenerator) -> dict:
    """
    検索されたノートから包括的なリマインドメッセージを作成

    Args:
        notes: ノート情報リスト
        reminder_generator: EnhancedReminderMessageGeneratorインスタンス

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
        "📅 **2025年11月1日（土）のノート情報**",
        f"📊 検索結果: **{len(notes)}件**のノートが見つかりました",
        ""
    ]

    # 緊急度別にノートを分類
    urgent_notes = []
    normal_notes = []
    schedule_notes = []

    for note in notes:
        if "【重要】" in note.title or "【緊急】" in note.title or "締切" in note.title:
            urgent_notes.append(note)
        elif "日程調整" in note.title or "chouseisan.com" in note.message_text:
            schedule_notes.append(note)
        else:
            normal_notes.append(note)

    # 緊急ノートの表示
    if urgent_notes:
        message_parts.append("🚨 **緊急・重要事項**")
        for i, note in enumerate(urgent_notes, 1):
            time_str = datetime.fromisoformat(note.detected_at).strftime("%H:%M")
            message_parts.append(f"  {i}. 【{time_str}】{note.title}")
            message_parts.append(f"     👤 {note.user_name}")
            if "場所：" in note.message_text:
                location = note.message_text.split("場所：")[1].split()[0] if "場所：" in note.message_text else ""
                if location:
                    message_parts.append(f"     📍 {location}")
        message_parts.append("")

    # 日程調整ノートの表示
    if schedule_notes:
        message_parts.append("📋 **日程調整・予定関連**")
        for i, note in enumerate(schedule_notes, 1):
            time_str = datetime.fromisoformat(note.detected_at).strftime("%H:%M")
            message_parts.append(f"  {i}. 【{time_str}】{note.title}")
            message_parts.append(f"     👤 {note.user_name}")
            if "chouseisan.com" in note.message_text:
                message_parts.append("     📋 日程調整URLが含まれています")
        message_parts.append("")

    # 一般ノートの表示
    if normal_notes:
        message_parts.append("📝 **一般情報**")
        for i, note in enumerate(normal_notes, 1):
            time_str = datetime.fromisoformat(note.detected_at).strftime("%H:%M")
            message_parts.append(f"  {i}. 【{time_str}】{note.title}")
            message_parts.append(f"     👤 {note.user_name}")
        message_parts.append("")

    # 天気情報を追加
    try:
        import sys; import os; sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'archive')); from openweather_service import get_weather_for_location
        weather_data = get_weather_for_location("東京都")
        if weather_data and 'temperature' in weather_data:
            message_parts.append("🌤️ **現在の天気情報（東京）**")
            message_parts.append(f"  🌡️ 気温: {weather_data.get('temperature', 'N/A')}°C（体感: {weather_data.get('feels_like', 'N/A')}°C）")
            message_parts.append(f"  ☁️ 天気: {weather_data.get('description', 'N/A')}")
            message_parts.append(f"  💧 湿度: {weather_data.get('humidity', 'N/A')}% / 気圧: {weather_data.get('pressure', 'N/A')}hPa")
            message_parts.append(f"  💨 風速: {weather_data.get('wind_speed', 'N/A')}km/h（風向: {weather_data.get('wind_direction', 'N/A')}°）")
            message_parts.append(f"  👁️ 視程: {weather_data.get('visibility', 'N/A')}km / 雲量: {weather_data.get('clouds', 'N/A')}%")
            message_parts.append("")
        else:
            message_parts.append("🌤️ 天気情報の取得に失敗しました")
            message_parts.append("")
    except Exception as e:
        message_parts.append(f"🌤️ 天気情報取得エラー: {e}")
        message_parts.append("")

    # フッター情報
    message_parts.append("---")
    message_parts.append("📊 データ統計:")
    message_parts.append(f"  • 緊急・重要: {len(urgent_notes)}件")
    message_parts.append(f"  • 日程調整: {len(schedule_notes)}件")
    message_parts.append(f"  • 一般情報: {len(normal_notes)}件")
    message_parts.append(f"  • 検索日時: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}")

    return {
        "type": "text",
        "text": "\n".join(message_parts)
    }

def create_weather_flex_message() -> dict:
    """天気情報のFlex Messageを作成"""
    try:
        from enhanced_reminder_messages import create_weather_flex_message
        flex_message = create_weather_flex_message("東京都", "代々木公園")
        return flex_message
    except Exception as e:
        print(f"Flex Message作成エラー: {e}")
        return None

def main():
    """メイン処理"""
    print("=" * 80)
    print("🔍 2025年11月1日（土）ノート検索・リマインドメッセージ作成テスト【包括版】")
    print("=" * 80)

    # テスト用データベースファイル名
    test_db_file = "clean_november_test_notes.json"

    # 既存のテストファイルを削除（クリーンスタート）
    if os.path.exists(test_db_file):
        os.remove(test_db_file)
        print("✅ 既存のテストデータベースをクリア")

    # 1. NoteDetectorを初期化
    print("\n1️⃣ NoteDetectorを初期化中...")
    note_detector = NoteDetector(storage_file=test_db_file)

    # 2. テストデータを追加
    print("\n2️⃣ 2025年11月1日のテストノートデータを追加中...")
    test_notes = create_test_notes_for_november()

    for note in test_notes:
        note_detector.notes_db.append(note)

    note_detector.save_notes_db()
    print(f"   ✅ 追加完了: {len(test_notes)}件のテストノートを追加")

    # 3. 日付ベース検索を実行
    print("\n3️⃣ 2025年11月1日のノートを検索中...")
    target_date = "2025-11-01"
    found_notes = search_notes_by_date(note_detector, target_date)

    print(f"   ✅ 検索結果: {len(found_notes)}件のノートが見つかりました")

    # 検索結果の詳細表示
    for i, note in enumerate(found_notes, 1):
        time_str = datetime.fromisoformat(note.detected_at).strftime("%H:%M")
        urgency = "🚨" if ("重要" in note.title or "緊急" in note.title or "締切" in note.title) else "📝"
        print(f"   {urgency} {i}. [{time_str}] {note.title} (投稿者: {note.user_name})")

    # 4. EnhancedReminderMessageGeneratorを初期化
    print("\n4️⃣ EnhancedReminderMessageGeneratorを初期化中...")
    reminder_generator = EnhancedReminderMessageGenerator()

    # 5. 包括的なリマインドメッセージを作成
    print("\n5️⃣ 包括的なリマインドメッセージを作成中...")
    comprehensive_message = create_comprehensive_reminder_message(found_notes, reminder_generator)

    # 6. 結果表示
    print("\n6️⃣ 作成されたリマインドメッセージ:")
    print("=" * 60)
    print(comprehensive_message['text'])
    print("=" * 60)

    # 7. 天気情報のFlex Message作成テスト
    print("\n7️⃣ 天気情報Flex Messageカード作成テスト:")
    flex_message = create_weather_flex_message()
    if flex_message:
        print("   ✅ Flex Message作成成功")
        print(f"   📱 カードタイプ: {flex_message.get('type', 'N/A')}")
        if 'altText' in flex_message:
            print(f"   📝 代替テキスト: {flex_message['altText']}")
    else:
        print("   ❌ Flex Message作成失敗")

    # 8. データ分析結果
    print("\n8️⃣ データ分析結果:")
    urgent_count = len([n for n in found_notes if "重要" in n.title or "緊急" in n.title or "締切" in n.title])
    schedule_count = len([n for n in found_notes if "日程調整" in n.title or "chouseisan.com" in n.message_text])
    normal_count = len(found_notes) - urgent_count - schedule_count

    print(f"   📊 緊急・重要事項: {urgent_count}件")
    print(f"   📋 日程調整関連: {schedule_count}件")
    print(f"   📝 一般情報: {normal_count}件")
    print(f"   🕐 最早投稿: {datetime.fromisoformat(min(found_notes, key=lambda x: x.detected_at).detected_at).strftime('%H:%M')}")
    print(f"   🕓 最遅投稿: {datetime.fromisoformat(max(found_notes, key=lambda x: x.detected_at).detected_at).strftime('%H:%M')}")

    # 9. テスト環境のクリーンアップ
    print("\n9️⃣ テスト環境のクリーンアップ:")
    try:
        os.remove(test_db_file)
        print("   ✅ テスト用データベースファイルを削除")
    except Exception as e:
        print(f"   ⚠️ クリーンアップエラー: {e}")

    print("\n" + "=" * 80)
    print("✅ 2025年11月1日ノート検索・リマインドメッセージ作成テスト 完了")
    print("=" * 80)

if __name__ == "__main__":
    main()

