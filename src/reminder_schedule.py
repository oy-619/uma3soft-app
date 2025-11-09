import json
import os
import re
from datetime import datetime, timedelta
from typing import Any, Dict

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# グループID
os.environ["TO_USER_ID"] = "C42ebf9338d5017559f0007dd0b52529c"

# 設定ファイルのパス（実行ディレクトリからの相対パス）
CONFIG_FILE = os.path.join("Lesson25", "uma3soft-app", "src", "reminder_config.json")

def clean_location_name_for_weather_api(raw_location: str) -> str:
    """
    場所名をクリーンアップして天気API用に最適化

    Args:
        raw_location (str): 生の場所名

    Returns:
        str: クリーンアップされた場所名
    """
    if not raw_location:
        return "東京都"

    # 都道府県名を抽出
    prefecture_patterns = [
        r'(東京都)',
        r'(神奈川県)',
        r'(千葉県)',
        r'(埼玉県)',
        r'(大阪府)',
        r'(愛知県)',
        r'(福岡県)',
        r'(北海道)',
        r'([^県都府道]+県)',
        r'([^県都府道]+府)',
        r'([^県都府道]+都)'
    ]

    for pattern in prefecture_patterns:
        match = re.search(pattern, raw_location)
        if match:
            return match.group(1)

    # 主要都市名を抽出
    city_patterns = [
        r'(横浜|川崎|相模原)',  # 神奈川
        r'(千葉|船橋|松戸)',    # 千葉
        r'(さいたま|川口|所沢)', # 埼玉
        r'(大阪|堺|東大阪)',    # 大阪
        r'(名古屋|豊田|岡崎)',  # 愛知
        r'(福岡|北九州|久留米)', # 福岡
        r'(札幌|函館|旭川)'     # 北海道
    ]

    for pattern in city_patterns:
        match = re.search(pattern, raw_location)
        if match:
            city = match.group(1)
            # 市名に対応する都道府県を返す
            if city in ['横浜', '川崎', '相模原']:
                return '神奈川県'
            elif city in ['千葉', '船橋', '松戸']:
                return '千葉県'
            elif city in ['さいたま', '川口', '所沢']:
                return '埼玉県'
            elif city in ['大阪', '堺', '東大阪']:
                return '大阪府'
            elif city in ['名古屋', '豊田', '岡崎']:
                return '愛知県'
            elif city in ['福岡', '北九州', '久留米']:
                return '福岡県'
            elif city in ['札幌', '函館', '旭川']:
                return '北海道'

    # デフォルトは東京都
    return "東京都"

# デフォルト設定
DEFAULT_CONFIG = {
    "target_ids": [],
    "fallback_user_id": None,
    "auto_discovery": True,
    "notification_times": [{"hour": 12, "minute": 0}, {"hour": 20, "minute": 0}],
}

app = Flask(__name__)

# ChromaDBの設定（chathistory2db.pyと同じパス構成を使用）
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_DIR = os.path.join(PROJECT_ROOT, "db")
PERSIST_DIRECTORY = os.path.join(DB_DIR, "chroma_store")

# ChromaDBの遅延初期化（必要時に初期化）
_embedding_model = None
_vector_db = None


def get_vector_db():
    """ChromaDBを必要時に初期化して返す"""
    global _embedding_model, _vector_db
    if _vector_db is None:
        _embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        _vector_db = Chroma(
            persist_directory=PERSIST_DIRECTORY, embedding_function=_embedding_model
        )
    return _vector_db


def load_config():
    """
    設定ファイルを読み込む

    Returns:
        dict: 設定データ
    """
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[CONFIG] Configuration file {CONFIG_FILE} not found. Using defaults.")
        return DEFAULT_CONFIG.copy()
    except json.JSONDecodeError:
        print(f"[CONFIG] Invalid JSON in {CONFIG_FILE}. Using defaults.")
        return DEFAULT_CONFIG.copy()


def save_config(config):
    """
    設定ファイルに保存する

    Args:
        config (dict): 設定データ
    """
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"[CONFIG] Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        print(f"[CONFIG] Failed to save configuration: {e}")


def get_target_ids():
    """
    送信先IDを取得する（複数の方法を試行・検証強化）

    Returns:
        list: 送信先IDのリスト
    """
    target_ids = []

    # 1. 環境変数から取得（uma3.pyで設定）
    env_id = os.getenv("TO_USER_ID")
    if env_id and env_id != "unknown":
        # 有効なIDかどうか基本的な検証
        if len(env_id) >= 10 and not env_id.startswith("C1234567890abcdef"):
            target_ids.append(env_id)
            print(f"[TARGET] Found valid target ID from environment: {env_id[:20]}...")
        else:
            print(f"[TARGET] Invalid environment ID ignored: {env_id}")

    # 2. 設定ファイルから取得
    config = load_config()
    config_ids = config.get("target_ids", [])
    for config_id in config_ids:
        if config_id and config_id not in target_ids:
            # 有効なIDかどうか基本的な検証
            if len(config_id) >= 10 and not config_id.startswith("C1234567890abcdef"):
                target_ids.append(config_id)
                print(f"[TARGET] Found valid target ID from config: {config_id[:20]}...")
            else:
                print(f"[TARGET] Invalid config ID ignored: {config_id}")

    # 3. フォールバックユーザーID
    fallback_id = config.get("fallback_user_id")
    if fallback_id and fallback_id not in target_ids:
        # 有効なIDかどうか基本的な検証
        if len(fallback_id) >= 10 and not fallback_id.startswith("C1234567890abcdef"):
            target_ids.append(fallback_id)
            print(f"[TARGET] Using valid fallback user ID: {fallback_id[:20]}...")
        else:
            print(f"[TARGET] Invalid fallback ID ignored: {fallback_id}")

    if not target_ids:
        print("[WARNING] No valid target IDs found. Please configure manually.")
        print("[INFO] ターゲットID取得方法:")
        print("  1. LINEグループでBotにメッセージ送信 → 自動設定")
        print("  2. reminder_config.json に手動追加")
        print("  3. 環境変数 TO_USER_ID を設定")
    else:
        print(f"[TARGET] Total valid targets: {len(target_ids)}")

    return target_ids


def add_target_id(new_id):
    """
    新しい送信先IDを設定に追加する

    Args:
        new_id (str): 新しい送信先ID
    """
    config = load_config()
    if new_id not in config.get("target_ids", []):
        config.setdefault("target_ids", []).append(new_id)
        save_config(config)
        print(f"[CONFIG] Added new target ID: {new_id}")


def get_line_group_info():
    """
    LINE APIを使用してBot参加中のグループ情報を取得する（参考用）
    注意: この機能は制限があり、実際には使用できない場合があります
    """
    LINE_ACCESS_TOKEN = (
        "fnNGsF7C1h861wsq/9lxqYZtdRdtFQpLnI6lCTcn9TPY7cNF+HaCvIqBZ8OlpW4k"
        "WGRKDWbeygz/UYAx7JbXJ3u+kxkOFSiLYCDPBSoc5WGJkUQRQbkM8/v4pv2mx+w2"
        "BblnaBi1h7ne3u1HHaKLHAdB04t89/1O/w1cDnyilFU="
    )

    headers = {
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        # Note: この API は実際には利用できない場合があります
        # LINE Bot API では基本的にグループ一覧を取得する API は提供されていません
        print(
            "[INFO] LINE API does not provide group list endpoint for security reasons"
        )
        print("[INFO] グループIDは以下の方法で取得してください：")
        print("  1. Botにメッセージを送信して自動取得")
        print("  2. LINE Developers Console でWebhookログを確認")
        print("  3. 手動で設定ファイルに追加")
        return []
    except Exception as e:
        print(f"[ERROR] Failed to get group info: {e}")
        return []


def get_upcoming_deadline_notes(days_ahead=7):
    """
    指定日数以内に入力期限が来るノートを検索する（入力期限ベース）

    Args:
        days_ahead (int): 何日先までの期限を検索するか

    Returns:
        list: 期限付きノートのリスト（入力期限順）
    """
    today = datetime.now().date()
    target_date_range = [(today + timedelta(days=i)) for i in range(1, days_ahead + 1)]

    print(
        f"[REMINDER] Searching for notes with input deadlines in next {days_ahead} days..."
    )

    # [ノート]データを検索
    vector_db = get_vector_db()
    print(f"[DEBUG] PERSIST_DIRECTORY: {PERSIST_DIRECTORY}")
    print(f"[DEBUG] ChromaDB exists: {os.path.exists(PERSIST_DIRECTORY)}")

    # 全データを取得してから文字列検索する（similarity_searchの代わり）
    all_docs = vector_db.get()
    all_notes = []
    for doc in all_docs["documents"]:
        if "[ノート]" in doc:
            all_notes.append(type("Document", (), {"page_content": doc})())

    # 制限を削除して全件検索
    notes = all_notes  # 全件検索
    print(f"[DEBUG] Found {len(notes)} notes with '[ノート]' search")

    upcoming_notes = []

    for i, note in enumerate(notes):
        content = note.page_content
        if "[ノート]" not in content:
            continue

        print(f"[DEBUG] Note {i+1}: {content[:100]}...")

        # 'テストイベント'を含むかチェック
        if "テストイベント" in content:
            print(f"[DEBUG] Found テストイベント in note {i+1}")
            print(f"[DEBUG] Full テストイベント content: {content}")

        # 入力期限パターンを優先的に検索
        deadline_patterns = [
            r"入力期限[：:]\s*(\d{4})/(\d{1,2})/(\d{1,2})\([月火水木金土日]\)",  # 入力期限：2025/10/24(木)
            r"入力期限[：:]\s*(\d{4})/(\d{1,2})/(\d{1,2})",  # 入力期限：2025/10/24
            r"入力期限[：:]\s*(\d{1,2})/(\d{1,2})\([月火水木金土日]\)",  # 入力期限：10/24(木)
            r"入力期限[：:]\s*(\d{1,2})/(\d{1,2})",  # 入力期限：10/24
            r"入力期限[：:]\s*(\d{1,2})月(\d{1,2})日",  # 入力期限：10月24日
        ]

        found_deadline_dates = []

        # まず入力期限を探す
        for pattern in deadline_patterns:
            matches = re.findall(pattern, content)
            if matches:
                print(f"[DEBUG] Deadline pattern '{pattern}' found matches: {matches}")
            for match in matches:
                try:
                    if len(match) == 3:  # 年/月/日形式（曜日付きも含む）
                        year, month, day = map(int, match)
                        deadline_date = datetime(year, month, day).date()
                        print(
                            f"[DEBUG] Parsed deadline date (year/month/day): {deadline_date}"
                        )
                    elif len(match) == 2:
                        if "月" in pattern:  # 月日形式
                            month, day = map(int, match)
                            year = today.year
                            # 過去の月の場合は翌年とする
                            if month < today.month or (
                                month == today.month and day < today.day
                            ):
                                year += 1
                            deadline_date = datetime(year, month, day).date()
                        else:  # MM/DD形式
                            month, day = map(int, match)
                            year = today.year
                            if month < today.month or (
                                month == today.month and day < today.day
                            ):
                                year += 1
                            deadline_date = datetime(year, month, day).date()

                    found_deadline_dates.append(deadline_date)
                except ValueError:
                    continue

        # 入力期限が見つからない場合は、従来のイベント日付を使用
        if not found_deadline_dates:
            print(f"[DEBUG] No input deadline found, searching for event dates...")
            date_patterns = [
                r"(\d{4})/(\d{1,2})/(\d{1,2})\([月火水木金土日]\)",  # 2025/10/27(月)形式
                r"(\d{4})/(\d{1,2})/(\d{1,2})",  # 2024/12/25形式
                r"(\d{1,2})月(\d{1,2})日",  # 12月25日形式
                r"(\d{1,2})/(\d{1,2})",  # 12/25形式
            ]

            for pattern in date_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    print(
                        f"[DEBUG] Event date pattern '{pattern}' found matches: {matches}"
                    )
                for match in matches:
                    try:
                        if len(match) == 3:  # 年/月/日形式（曜日付きも含む）
                            year, month, day = map(int, match)
                            event_date = datetime(year, month, day).date()
                            print(
                                f"[DEBUG] Parsed event date (year/month/day): {event_date}"
                            )
                            found_deadline_dates.append(event_date)
                        elif len(match) == 2:
                            if "月" in pattern:  # 月日形式
                                month, day = map(int, match)
                                year = today.year
                                if month < today.month or (
                                    month == today.month and day < today.day
                                ):
                                    year += 1
                                event_date = datetime(year, month, day).date()
                            else:  # MM/DD形式
                                month, day = map(int, match)
                                year = today.year
                                if month < today.month or (
                                    month == today.month and day < today.day
                                ):
                                    year += 1
                                event_date = datetime(year, month, day).date()
                            found_deadline_dates.append(event_date)
                    except ValueError:
                        continue

        # 期限内の日付があるかチェック
        print(f"[DEBUG] Found deadline dates for this note: {found_deadline_dates}")
        print(f"[DEBUG] Target date range: {target_date_range}")

        # 入力期限パターンが実際に見つかったかチェック
        has_input_deadline = any(
            re.search(pattern, content) for pattern in deadline_patterns
        )

        for deadline_date in found_deadline_dates:
            if deadline_date in target_date_range:
                print(f"[DEBUG] Deadline date {deadline_date} is in target range!")

                # 入力期限パターンが見つかった場合とそうでない場合を区別
                if has_input_deadline:
                    # 入力期限パターンが見つかった場合
                    print(f"[DEBUG] This is an input deadline note")
                    upcoming_notes.append(
                        {
                            "content": content,
                            "date": deadline_date,
                            "days_until": (deadline_date - today).days,
                            "is_input_deadline": True,
                            "reminder_type": "input_deadline",
                        }
                    )
                    break
                else:
                    # 入力期限パターンがない場合、イベント日として処理（前日・前々日通知）
                    print(f"[DEBUG] This is an event date note (no input deadline)")
                    upcoming_notes.append(
                        {
                            "content": content,
                            "date": deadline_date,
                            "days_until": (deadline_date - today).days,
                            "is_input_deadline": False,
                            "reminder_type": "event_date",
                        }
                    )
                    break

    # 日付順にソート
    upcoming_notes.sort(key=lambda x: x["date"])

    print(f"[REMINDER] Found {len(upcoming_notes)} upcoming deadline notes")
    return upcoming_notes


def get_reminders_for_tomorrow():
    """
    明日にリマインドすべきノートを取得する
    - 入力期限がある場合: 明日が入力期限のノート（前日通知）
    - 入力期限がない場合: 明日がイベント日のノート（当日通知）のみ

    Returns:
        list: 明日にリマインドすべき予定リスト
    """
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    print(f"[REMINDER] Looking for reminders to send tomorrow ({tomorrow})")
    print(f"[REMINDER] - Input deadlines for: {tomorrow}")
    print(f"[REMINDER] - Event dates (no deadline) for: {tomorrow} (same day)")

    # 2日先まで検索して詳細に分析
    upcoming_notes = get_upcoming_deadline_notes(days_ahead=2)
    reminders_for_tomorrow = []

    for note in upcoming_notes:
        note_date = note["date"]
        is_input_deadline = note.get("is_input_deadline", False)

        if is_input_deadline and note_date == tomorrow:
            # 入力期限が明日の場合（前日通知）
            print(f"[REMINDER] Found input deadline for tomorrow: {note_date}")
            reminders_for_tomorrow.append(note)
        elif not is_input_deadline and note_date == tomorrow:
            # 入力期限なしで明日がイベント日の場合（当日通知）
            print(
                f"[REMINDER] Found event (no deadline) for tomorrow (same day): {note_date}"
            )
            reminders_for_tomorrow.append(note)

    return reminders_for_tomorrow


def get_reminders_for_day_after_tomorrow():
    """
    明後日にリマインドすべきノートを取得する
    - 入力期限がない場合: 明後日がイベント日のノート（前日通知）

    Returns:
        list: 明後日にリマインドすべき予定リスト
    """
    today = datetime.now().date()
    day_after_tomorrow = today + timedelta(days=2)

    print(
        f"[REMINDER] Looking for reminders to send day after tomorrow (day before event)"
    )
    print(
        f"[REMINDER] - Event dates (no deadline) for: {day_after_tomorrow} (next day)"
    )

    # 2日先まで検索
    upcoming_notes = get_upcoming_deadline_notes(days_ahead=2)
    reminders_for_day_after = []

    print(
        f"[REMINDER] Debug: Found {len(upcoming_notes)} upcoming notes from get_upcoming_deadline_notes"
    )

    for note in upcoming_notes:
        note_date = note["date"]
        is_input_deadline = note.get("is_input_deadline", False)

        print(
            f"[REMINDER] Debug: Processing note with date {note_date}, is_input_deadline={is_input_deadline}"
        )
        print(
            f"[REMINDER] Debug: Comparing with day_after_tomorrow={day_after_tomorrow}"
        )

        if not is_input_deadline and note_date == day_after_tomorrow:
            # 入力期限なしで明後日がイベント日の場合（前日通知）
            print(
                f"[REMINDER] Found event (no deadline) for day after tomorrow (next day): {note_date}"
            )
            print(f"[REMINDER] Debug: Adding note: {note['content'][:50]}...")
            reminders_for_day_after.append(note)
        else:
            if is_input_deadline:
                print(f"[REMINDER] Debug: Skipping input deadline note for {note_date}")
            elif note_date != day_after_tomorrow:
                print(
                    f"[REMINDER] Debug: Skipping note - date mismatch ({note_date} != {day_after_tomorrow})"
                )

    print(
        f"[REMINDER] Total events found for day after tomorrow notification: {len(reminders_for_day_after)}"
    )

    # デバッグ: 返り値の詳細を確認
    if reminders_for_day_after:
        print(f"[REMINDER] Debug: Returning {len(reminders_for_day_after)} events")
        for i, reminder in enumerate(reminders_for_day_after, 1):
            print(
                f"[REMINDER] Debug: Event {i}: {reminder['date']} - {reminder['content'][:50]}..."
            )
    else:
        print("[REMINDER] Debug: No events to return")

    return reminders_for_day_after


def get_next_day_reminders():
    """
    明日が入力期限のノートを取得する（前日通知用）
    後方互換性のために残しておく

    Returns:
        list: 明日が入力期限の予定リスト
    """
    tomorrow = (datetime.now() + timedelta(days=1)).date()

    print(f"[REMINDER] Looking for tomorrow's input deadlines: {tomorrow}")

    # 明日が入力期限の予定を検索
    upcoming_notes = get_upcoming_deadline_notes(days_ahead=1)
    tomorrow_notes = [note for note in upcoming_notes if note["date"] == tomorrow]

    if not tomorrow_notes:
        # 明日の入力期限がない場合は、直近の入力期限を1件取得
        upcoming_notes = get_upcoming_deadline_notes(days_ahead=14)
        if upcoming_notes:
            print(
                f"[REMINDER] No tomorrow's input deadline found, using next upcoming: {upcoming_notes[0]['date']}"
            )
            return [upcoming_notes[0]]
    else:
        print(f"[REMINDER] Found {len(tomorrow_notes)} input deadline(s) for tomorrow")

    return tomorrow_notes


def get_weather_for_event(event_content, event_date):
    """
    イベント情報に基づいて天気情報を取得する

    Args:
        event_content (str): イベント内容
        event_date (datetime.date): イベント日付

    Returns:
        str: 天気情報（取得できない場合は空文字）
    """
    try:
        # WeatherContextToolをインポート
        from uma3_custom_tools import WeatherContextTool

        # 天気ツールのインスタンス作成
        weather_tool = WeatherContextTool()

        # イベント日付を文字列に変換
        event_date_str = event_date.strftime('%Y-%m-%d')

        # 天気情報を取得
        weather_info = weather_tool._run(
            query=event_content,
            location="",
            event_date=event_date_str
        )

        return weather_info

    except ImportError as e:
        print(f"[WEATHER] WeatherContextTool import error: {e}")
        return ""
    except Exception as e:
        print(f"[WEATHER] Error getting weather info: {e}")
        return ""


def generate_note_url(note_content):
    """
    ノート内容からアクセス用URLを生成する

    Args:
        note_content (str): ノートの内容

    Returns:
        str: ノート詳細用URL
    """
    try:
        import hashlib
        import urllib.parse

        # ノート内容からハッシュを生成してユニークIDとする
        note_hash = hashlib.md5(note_content.encode('utf-8')).hexdigest()[:16]

        # ノートのタイトルを抽出（最初の50文字程度）
        title_match = re.search(r'\[ノート\]([^\n]+)', note_content)
        if title_match:
            title = title_match.group(1).strip()[:50]
        else:
            title = note_content[:50].replace('\n', ' ').strip()

        # URLエンコード
        encoded_title = urllib.parse.quote(title)

        # ローカルサーバーのノート詳細URL（ngrokトンネル経由でアクセス可能）
        base_url = "http://localhost:5000"  # uma3アプリのベースURL
        note_url = f"{base_url}/note/{note_hash}?title={encoded_title}"

        return note_url

    except Exception as e:
        print(f"[URL] Error generating note URL: {e}")
        return ""


def find_related_detected_notes(reminder_content: str, event_date):
    """
    リマインダー内容に関連する検出済みノートを検索

    Args:
        reminder_content (str): リマインダー内容
        event_date: イベント日付

    Returns:
        list: 関連ノート情報のリスト
    """
    try:
        # ノート検出器を初期化
        from note_detector import NoteDetector
        detector = NoteDetector()

        # キーワード抽出（簡単な実装）
        keywords = []
        content_lower = reminder_content.lower()

        # 一般的なソフトボール関連キーワード
        softball_keywords = ["練習", "試合", "大会", "ソフトボール", "調整", "出欠", "参加", "集合"]
        for keyword in softball_keywords:
            if keyword in content_lower:
                keywords.append(keyword)

        # 日付関連
        if event_date:
            # 同日や近い日付のノートを優先
            date_str = event_date.strftime("%m/%d")
            keywords.append(date_str)

        # 関連ノートを検索
        related_notes = []
        if keywords:
            for keyword in keywords:
                notes = detector.search_notes_by_title(keyword)
                for note in notes[:2]:  # 最大2件
                    if note not in related_notes:
                        related_notes.append(note)

        # 最新ノートも含める（キーワードマッチがない場合）
        if not related_notes:
            recent_notes = detector.get_latest_notes(3)
            related_notes.extend(recent_notes)

        return related_notes[:3]  # 最大3件

    except Exception as e:
        print(f"[RELATED_NOTES] エラー: {e}")
        return []


def create_flex_reminder_message(note):
    """
    Flex Message形式のリマインダーメッセージを作成する（拡張版対応）

    Args:
        note (dict): ノート情報

    Returns:
        dict: Flex Message形式のメッセージデータ
    """
    try:
        # 天気情報Flex Messageテンプレートシステムとカスタマイザーを使用
        try:
            from src.weather_flex_template import WeatherFlexTemplate
            from src.reminder_flex_customizer import ReminderFlexCustomizer
        except ImportError:
            # 直接インポートを試行
            from weather_flex_template import WeatherFlexTemplate
            from reminder_flex_customizer import ReminderFlexCustomizer

        # 天気情報テンプレート生成器とカスタマイザーを初期化
        weather_template = WeatherFlexTemplate()
        flex_customizer = ReminderFlexCustomizer()

        # ノートからイベント情報を抽出
        event_content = note['content']
        event_date = note["date"]

        # days_untilが存在しない場合は計算する
        if "days_until" not in note:
            today = datetime.now().date()
            note_date = note["date"]
            if isinstance(note_date, str):
                note_date = datetime.strptime(note_date, "%Y-%m-%d").date()
            note["days_until"] = (note_date - today).days

        days_until = note["days_until"]
        is_input_deadline = note.get("is_input_deadline", False)

        # 場所情報を抽出（基本的には東京都を使用）
        location = "東京都"

        # ノート内容から場所を抽出する試行
        location_patterns = [
            r'@([^\s\n（）【】]+)',  # @記号の後の場所
            r'場所[：:]\s*([^\n]+)',
            r'会場[：:]\s*([^\n]+)',
            r'開催地[：:]\s*([^\n]+)',
            r'(平和島|萩中|ガス橋|馬三小|池雪小|糀谷中|北蒲広場)[^\n]*',
            r'(東京都|神奈川県|千葉県|埼玉県|大阪府|愛知県|福岡県)[^\n]*?[区市町村][^\n]*?球場',
            r'(東京都|神奈川県|千葉県|埼玉県|大阪府|愛知県|福岡県)[^\n]*?[区市町村]'
        ]

        for pattern in location_patterns:
            match = re.search(pattern, event_content)
            if match:
                if pattern.startswith('@'):
                    # @記号の場合は取得したものをそのまま使用
                    extracted_location = match.group(1).strip()
                    # 特定の場所名の場合は地域を追加
                    if any(place in extracted_location for place in ['平和島', '萩中', 'ガス橋']):
                        location = "東京都大田区"
                    elif any(place in extracted_location for place in ['馬三小', '池雪小']):
                        location = "東京都大田区"
                    elif '糀谷中' in extracted_location:
                        location = "東京都大田区"
                    else:
                        location = f"東京都{extracted_location[:10]}"  # 最大10文字
                elif pattern.startswith('場所') or pattern.startswith('会場') or pattern.startswith('開催地'):
                    extracted_location = match.group(1).strip()
                    # 場所情報が長すぎる場合は短縮
                    if len(extracted_location) > 30:
                        # 都道府県と区市町村程度に短縮
                        city_match = re.search(r'(東京都|神奈川県|千葉県|埼玉県|大阪府|愛知県|福岡県)[^\s]*[区市町]', extracted_location)
                        if city_match:
                            location = city_match.group(0)
                        else:
                            location = extracted_location[:15]  # 最大15文字
                    else:
                        location = extracted_location
                else:
                    location = match.group(0)[:15]  # 最大15文字
                break

        # 場所名をクリーンアップ（天気API用に最適化）
        location = clean_location_name_for_weather_api(location)

        # メッセージタイトルを生成
        if is_input_deadline:
            if days_until <= 1:
                title = f"⏰ 入力期限のご案内（{'本日' if days_until == 0 else '明日'}期限）"
            else:
                title = f"📅 入力期限のご案内（{days_until}日後期限）"
        else:
            if days_until <= 1:
                title = f"🎯 イベント開催のご案内（{'本日' if days_until == 0 else '明日'}開催）"
            else:
                title = f"📅 イベント開催のご案内（{days_until}日後開催）"

        # 日付文字列を生成
        if isinstance(event_date, str):
            date_str = event_date
        else:
            date_str = event_date.strftime('%Y-%m-%d')

        # 適切な天気Flex Messageテンプレートを選択
        if days_until == 0:
            # 当日の場合は現在の天気
            base_flex_message = weather_template.create_current_weather_flex(
                location=location,
                custom_title=title
            )
        else:
            # 未来の日付の場合は予報
            base_flex_message = weather_template.create_forecast_flex(
                location=location,
                target_date=date_str,
                custom_title=title
            )

        # リマインダー専用にカスタマイズ（イベント詳細と参加ボタンを追加）
        customized_flex_message = flex_customizer.customize_weather_flex_for_reminder(
            base_flex_message, note
        )

        return customized_flex_message

    except ImportError as e:
        print(f"[FLEX_MESSAGE] 天気Flexテンプレートのインポートエラー: {e}")
        return create_flex_reminder_message_basic(note)
    except Exception as e:
        print(f"[FLEX_MESSAGE] 天気Flexテンプレートエラー: {e}")
        return create_flex_reminder_message_basic(note)

def create_flex_reminder_message_basic(note):
    """
    Flex Message形式のリマインダーメッセージを作成する（基本版）

    Args:
        note (dict): ノート情報

    Returns:
        dict: Flex Message形式のメッセージデータ
    """
    # days_untilが存在しない場合は計算する
    if "days_until" not in note:
        today = datetime.now().date()
        note_date = note["date"]
        if isinstance(note_date, str):
            note_date = datetime.strptime(note_date, "%Y-%m-%d").date()
        note["days_until"] = (note_date - today).days

    days_until = note["days_until"]
    is_input_deadline = note.get("is_input_deadline", False)
    date_info = note["date"]

    # 日付を日本語形式でフォーマット
    formatted_date = date_info.strftime("%Y年%m月%d日")
    weekdays = ["月", "火", "水", "木", "金", "土", "日"]
    weekday = weekdays[date_info.weekday()]
    date_with_weekday = f"{formatted_date}({weekday})"

    # タイトルとカラーを決定
    if is_input_deadline:
        if days_until == 0:
            title = "⚠️ 入力期限（本日）"
            color = "#FF6B6B"  # 赤色
            urgency = "本日期限"
        elif days_until == 1:
            title = "⏰ 入力期限（明日）"
            color = "#FFA726"  # オレンジ色
            urgency = "明日期限"
        else:
            title = f"📅 入力期限（{days_until}日後）"
            color = "#42A5F5"  # 青色
            urgency = f"{days_until}日後期限"
    else:
        if days_until == 0:
            title = "🎯 イベント開催（本日）"
            color = "#FF6B6B"  # 赤色
            urgency = "本日開催"
        elif days_until == 1:
            title = "⏰ イベント開催（明日）"
            color = "#FFA726"  # オレンジ色
            urgency = "明日開催"
        elif days_until == 2:
            title = "📅 イベント開催（明後日）"
            color = "#66BB6A"  # 緑色
            urgency = "明後日開催"
        else:
            title = f"📅 イベント開催（{days_until}日後）"
            color = "#42A5F5"  # 青色
            urgency = f"{days_until}日後開催"

    # イベント内容を整理（最初の3行を取得）
    content_lines = note['content'].split('\n')
    main_content = content_lines[0] if content_lines else "詳細未定"
    sub_content = '\n'.join(content_lines[1:3]) if len(content_lines) > 1 else ""

    # Flex Message JSON構造
    flex_message = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": title,
                    "weight": "bold",
                    "size": "md",
                    "color": "#FFFFFF"
                }
            ],
            "backgroundColor": color,
            "paddingAll": "15px"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "📅 日時",
                            "size": "sm",
                            "color": "#666666",
                            "weight": "bold"
                        },
                        {
                            "type": "text",
                            "text": date_with_weekday,
                            "size": "lg",
                            "weight": "bold",
                            "color": color,
                            "margin": "xs"
                        }
                    ],
                    "margin": "none"
                },
                {
                    "type": "separator",
                    "margin": "md"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "📋 内容",
                            "size": "sm",
                            "color": "#666666",
                            "weight": "bold"
                        },
                        {
                            "type": "text",
                            "text": main_content,
                            "size": "md",
                            "wrap": True,
                            "margin": "xs"
                        }
                    ],
                    "margin": "md"
                }
            ],
            "paddingAll": "15px"
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": urgency,
                            "size": "sm",
                            "color": color,
                            "weight": "bold",
                            "flex": 1
                        },
                        {
                            "type": "text",
                            "text": "UMA3リマインダー",
                            "size": "xs",
                            "color": "#999999",
                            "align": "end",
                            "flex": 1
                        }
                    ]
                }
            ],
            "paddingAll": "10px"
        }
    }

    # サブコンテンツがある場合は追加
    if sub_content.strip():
        flex_message["body"]["contents"].append({
            "type": "text",
            "text": sub_content,
            "size": "sm",
            "color": "#666666",
            "wrap": True,
            "margin": "sm"
        })

    return flex_message


def format_single_reminder_message(note, notification_type="standard"):
    """
    単一リマインダーメッセージを整形する（拡張版対応）

    Args:
        note (dict): 単一のノート情報
        notification_type (str): 通知タイプ

    Returns:
        str: 整形されたメッセージ
    """
    try:
        # 天気情報テンプレートシステムを使用してテキストメッセージを生成
        from weather_flex_template import WeatherFlexTemplate

        weather_template = WeatherFlexTemplate()

        # ノート情報を取得
        event_content = note['content']
        event_date = note["date"]
        days_until = note["days_until"]
        is_input_deadline = note.get("is_input_deadline", False)

        # 場所情報を抽出
        location = "東京都"
        location_patterns = [
            r'@([^\s\n（）【】]+)',  # @記号の後の場所
            r'場所[：:]\s*([^\n]+)',
            r'会場[：:]\s*([^\n]+)',
            r'開催地[：:]\s*([^\n]+)',
            r'(平和島|萩中|ガス橋|馬三小|池雪小|糀谷中|北蒲広場)[^\n]*',
            r'(東京都|神奈川県|千葉県|埼玉県|大阪府|愛知県|福岡県)[^\n]*?[区市町村][^\n]*?球場',
            r'(東京都|神奈川県|千葉県|埼玉県|大阪府|愛知県|福岡県)[^\n]*?[区市町村]'
        ]

        for pattern in location_patterns:
            match = re.search(pattern, event_content)
            if match:
                if pattern.startswith('@'):
                    # @記号の場合は取得したものをそのまま使用
                    extracted_location = match.group(1).strip()
                    # 特定の場所名の場合は地域を追加
                    if any(place in extracted_location for place in ['平和島', '萩中', 'ガス橋']):
                        location = "東京都大田区"
                    elif any(place in extracted_location for place in ['馬三小', '池雪小']):
                        location = "東京都大田区"
                    elif '糀谷中' in extracted_location:
                        location = "東京都大田区"
                    else:
                        location = f"東京都{extracted_location[:10]}"  # 最大10文字
                elif pattern.startswith('場所') or pattern.startswith('会場') or pattern.startswith('開催地'):
                    extracted_location = match.group(1).strip()
                    # 場所情報が長すぎる場合は短縮
                    if len(extracted_location) > 30:
                        # 都道府県と区市町村程度に短縮
                        city_match = re.search(r'(東京都|神奈川県|千葉県|埼玉県|大阪府|愛知県|福岡県)[^\s]*[区市町]', extracted_location)
                        if city_match:
                            location = city_match.group(0)
                        else:
                            location = extracted_location[:15]  # 最大15文字
                    else:
                        location = extracted_location
                else:
                    location = match.group(0)[:15]  # 最大15文字
                break        # 基本的な挨拶とメッセージ開始
        current_hour = datetime.now().hour
        if current_hour < 10:
            greeting = "おはようございます。"
        elif current_hour < 18:
            greeting = "お疲れ様です。"
        else:
            greeting = "お疲れ様です。"

        # 日付フォーマット
        formatted_date = event_date.strftime("%Y年%m月%d日")
        weekdays = ["月", "火", "水", "木", "金", "土", "日"]
        weekday = weekdays[event_date.weekday()]
        date_with_weekday = f"{formatted_date}({weekday})"

        # メッセージタイプに応じた内容
        if is_input_deadline:
            if days_until == 1:
                message_header = f"⏰ 【入力期限のご案内（明日期限）】\n\n{greeting}\n入力期限が明日{date_with_weekday}となっているイベントがございます。\nお忙しい中恐れ入りますが、ご都合の確認とご入力をお願いいたします。"
            elif days_until == 0:
                message_header = f"⚠️ 【入力期限のご案内（本日期限）】\n\n{greeting}\n入力期限が本日{date_with_weekday}となっているイベントがございます。\nお忙しい中恐れ入りますが、まだご入力いただいていない方は、お早めのご入力をお願いいたします。"
            else:
                message_header = f"📅 【入力期限のご案内（{days_until}日後期限）】\n\n{greeting}\n入力期限が{days_until}日後の{date_with_weekday}となっている予定がございます。\nご都合のご確認をお願いいたします。"
        else:
            if days_until == 2:
                message_header = f"⏰ 【イベントのご案内（明後日開催）】\n\n{greeting}\n{date_with_weekday}にイベントが開催されます。\n改めてご確認いただき、ご準備のほどよろしくお願いいたします。"
            elif days_until == 1:
                message_header = f"⏰ 【イベントのご案内（明日開催）】\n\n{greeting}\n{date_with_weekday}にイベントが開催されます。\nお気をつけてお越しください。よろしくお願いいたします。"
            elif days_until == 0:
                message_header = f"⚠️ 【イベント開催のご案内（本日開催）】\n\n{greeting}\n{date_with_weekday}にイベントが開催されます。\nお気をつけてお越しください。"
            else:
                message_header = f"📅 【イベントのご案内（{days_until}日後開催）】\n\n{greeting}\n{date_with_weekday}にイベントが開催されます。\nご都合のご確認をお願いいたします。"

        # 天気情報を取得
        try:
            if days_until == 0:
                weather_data = weather_template.get_current_weather(location)
            else:
                date_str = event_date.strftime('%Y-%m-%d')
                forecast_list = weather_template.get_forecast_by_date(location, date_str)
                weather_data = forecast_list[0] if forecast_list else None

            weather_text = ""
            if weather_data:
                # 天気情報をテキスト形式で整形
                temp = weather_data.get('temperature', weather_data.get('temp', 'N/A'))
                weather_desc = weather_data.get('description', weather_data.get('weather', 'N/A'))
                humidity = weather_data.get('humidity', 'N/A')
                wind_speed = weather_data.get('wind_speed', 'N/A')

                weather_text = f"\n\n🌤️ **天気情報（{location}）**\n"
                weather_text += f"🌡️ 気温: {temp}℃\n"
                weather_text += f"☁️ 天気: {weather_desc}\n"
                weather_text += f"💧 湿度: {humidity}%\n"
                weather_text += f"💨 風速: {wind_speed}m/s\n"

                # 天気アドバイスを追加
                advice = weather_template._get_weather_advice(weather_data, [weather_data] if isinstance(weather_data, dict) else weather_data)
                if advice:
                    weather_text += f"\n💡 天気アドバイス: {advice}"
            else:
                weather_text = f"\n\n🌤️ **天気情報**: 当日の天気予報をご確認いただき、適切な服装でお越しください"

        except Exception as e:
            print(f"[WEATHER] 天気情報取得エラー: {e}")
            weather_text = f"\n\n🌤️ **天気情報**: 当日の天気予報をご確認いただき、適切な服装でお越しください"

        # メッセージを組み立て
        enhanced_message = f"{message_header}\n\n📋 **イベント詳細**\n{event_content}{weather_text}"

        # 関連ノートがある場合は追加
        related_notes = find_related_detected_notes(event_content, event_date)
        if related_notes:
            enhanced_message += f"\n\n{'='*50}\n\n📋 **関連情報のご参考**\n以下の関連情報もご確認いただけますと幸いです。\n"
            for i, related_note in enumerate(related_notes, 1):
                note_title = related_note.get('title', '不明なノート')
                if len(note_title) > 30:
                    note_title = note_title[:30] + "..."
                enhanced_message += f"\n{i}. 📝 {note_title}\n"

        # 締めの挨拶を追加
        enhanced_message += f"\n{'='*50}\n\nご不明な点がございましたら、お気軽にお声かけください。\nよろしくお願いいたします。"

        return enhanced_message

    except ImportError as e:
        print(f"[FORMAT_MESSAGE] 天気テンプレートのインポートエラー: {e}")
        return format_single_reminder_message_basic(note, notification_type)
    except Exception as e:
        print(f"[FORMAT_MESSAGE] 天気テンプレート処理エラー: {e}")
        return format_single_reminder_message_basic(note, notification_type)

def format_single_reminder_message_basic(note, notification_type="standard"):
    """
    単一リマインダーメッセージを整形する（基本版）

    Args:
        note (dict): 単一のノート情報
        notification_type (str): 通知タイプ

    Returns:
        str: 整形されたメッセージ
    """
    days_until = note["days_until"]
    is_input_deadline = note.get("is_input_deadline", False)
    reminder_type = note.get("reminder_type", "standard")
    date_info = note["date"]  # 期限日またはイベント日

    # 日付を日本語形式でフォーマット
    formatted_date = date_info.strftime("%Y年%m月%d日")
    weekdays = ["月", "火", "水", "木", "金", "土", "日"]
    weekday = weekdays[date_info.weekday()]
    date_with_weekday = f"{formatted_date}({weekday})"

    # 通知タイプに応じてメッセージを調整（期限日とイベント日を明確に区別）
    if is_input_deadline:
        # 入力期限がある場合（date_infoは期限日）
        if days_until == 1:
            prefix = f"⏰ 【入力期限のご案内（明日期限）】\n\nいつもお疲れ様です。\n入力期限が明日{date_with_weekday}となっているイベントがございます。\nお忙しい中恐れ入りますが、ご都合の確認とご入力をお願いいたします。\n"
        elif days_until == 0:
            prefix = f"⚠️ 【入力期限のご案内（本日期限）】\n\nいつもお疲れ様です。\n入力期限が本日{date_with_weekday}となっているイベントがございます。\nお忙しい中恐れ入りますが、まだご入力いただいていない方は、お早めのご入力をお願いいたします。\n"
        else:
            prefix = f"📅 【入力期限のご案内（{days_until}日後期限）】\n\nいつもお疲れ様です。\n入力期限が{days_until}日後の{date_with_weekday}となっている予定がございます。\nご都合のご確認をお願いいたします。\n"
    else:
        # 入力期限がない場合（date_infoはイベント日）
        if days_until == 2:
            prefix = f"⏰ 【イベントのご案内（明後日開催）】\n\nいつもお疲れ様です。\n{date_with_weekday}にイベントが開催されます。\n改めてご確認いただき、ご準備のほどよろしくお願いいたします。\n"
        elif days_until == 1:
            prefix = f"⏰ 【イベントのご案内（明日開催）】\n\nいつもお疲れ様です。\n{date_with_weekday}にイベントが開催されます。\nお気をつけてお越しください。よろしくお願いいたします。\n"
        elif days_until == 0:
            prefix = f"⚠️ 【イベント開催のご案内（本日開催）】\n\nいつもお疲れ様です。\n{date_with_weekday}にイベントが開催されます。\nお気をつけてお越しください。\n"
        else:
            prefix = f"📅 【イベントのご案内（{days_until}日後開催）】\n\nいつもお疲れ様です。\n{date_with_weekday}にイベントが開催されます。\nご都合のご確認をお願いいたします。\n"

    # 天気情報を取得（実際のイベント日または期限日を使用）
    weather_info = get_weather_for_event(note['content'], date_info)

    # 関連ノートを検索
    related_notes = find_related_detected_notes(note['content'], date_info)

    # メッセージを組み立て
    message = f"{prefix}\n\n📋 **イベント詳細**\n{note['content']}\n"

    if weather_info:
        message += f"\n{'='*50}\n\n{weather_info}\n"
    else:
        message += f"\n🌤️ **天気情報のご案内**: 当日の天気予報をご確認いただき、適切な服装でお越しください\n"

    # 関連ノートを追加（URL削除版）
    if related_notes:
        message += f"\n{'='*50}\n\n📋 **関連情報のご参考**\n以下の関連情報もご確認いただけますと幸いです。\n"
        for i, related_note in enumerate(related_notes, 1):
            # 辞書形式でアクセス
            note_title = related_note.get('title', '不明なノート')

            if len(note_title) > 30:
                note_title = note_title[:30] + "..."

            message += f"\n{i}. 📝 {note_title}\n"

    # 締めの挨拶を追加
    message += f"\n{'='*50}\n\nご不明な点がございましたら、お気軽にお声かけください。\nよろしくお願いいたします。"

    return message


def format_reminder_message(notes, notification_type="standard"):
    """
    リマインダーメッセージを整形する（1件ずつ個別メッセージ対応）

    Args:
        notes (list): ノートリスト
        notification_type (str): 通知タイプ ("standard", "day_before", "two_days_before")

    Returns:
        list または str: 複数件の場合はメッセージのリスト、1件の場合は文字列
    """
    if not notes:
        return ["⏰ 直近の入力期限は見つかりませんでした。"]

    # 1件ずつ個別メッセージを生成
    messages = []
    for note in notes:
        single_message = format_single_reminder_message(note, notification_type)
        messages.append(single_message)

    # 複数件の場合はリストで返す
    return messages




def _extract_weather_summary(weather_info):
    """
    天気情報から要約を抽出

    Args:
        weather_info (str): 詳細天気情報

    Returns:
        str: 要約された天気情報
    """
    try:
        lines = weather_info.split('\n')
        summary_parts = []

        for line in lines:
            if '現在の気温' in line:
                summary_parts.append(line.replace('**', '').replace('🌡️', '').strip())
            elif '降水確率' in line:
                summary_parts.append(line.replace('**', '').replace('☔', '').strip())
            elif '天気' in line and len(line) < 50:
                summary_parts.append(line.replace('**', '').replace('☁️', '').strip())

        if summary_parts:
            return ' / '.join(summary_parts[:3])  # 最大3項目
        else:
            return "天気情報をご確認ください"

    except Exception:
        return "天気情報をご確認ください"


def send_flex_reminder_via_line(flex_message_data):
    """
    Flex Message形式でリマインダーを送信する

    Args:
        flex_message_data (dict): Flex Messageのデータ構造

    Returns:
        bool: 送信成功の場合True
    """
    # 環境変数からアクセストークンを取得
    LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")

    # フォールバック: ファイル内のトークンを使用（デバッグ用）
    if not LINE_ACCESS_TOKEN:
        LINE_ACCESS_TOKEN = (
            "fnNGsF7C1h861wsq/9lxqYZtdRdtFQpLnI6lCTcn9TPY7cNF+HaCvIqBZ8OlpW4k"
            "WGRKDWbeygz/UYAx7JbXJ3u+kxkOFSiLYCDPBSoc5WGJkUQRQbkM8/v4pv2mx+w2"
            "BblnaBi1h7ne3u1HHaKLHAdB04t89/1O/w1cDnyilFU="
        )
        print("[WARNING] Using fallback LINE_ACCESS_TOKEN from code")
    else:
        print(f"[INFO] Using LINE_ACCESS_TOKEN from environment (length: {len(LINE_ACCESS_TOKEN)})")

    target_ids = get_target_ids()

    if not target_ids:
        print("[ERROR] No target IDs configured. Cannot send reminder.")
        return False

    headers = {
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    success_count = 0

    print(f"[FLEX_REMINDER] Attempting to send Flex Message to {len(target_ids)} target(s)")

    for target_id in target_ids:
        # ターゲットIDの検証
        if not target_id or len(target_id) < 10:
            print(f"[ERROR] Invalid target ID format: {target_id}")
            continue

        # サンプルIDかどうかチェック
        if target_id.startswith("C1234567890abcdef") or target_id == "unknown":
            print(f"[ERROR] Sample/invalid target ID detected: {target_id}")
            continue

        # flex_message_dataが既に完全なFlex Messageの場合
        if isinstance(flex_message_data, dict) and flex_message_data.get("type") == "flex":
            # そのまま使用
            data = {
                "to": target_id,
                "messages": [flex_message_data],
            }
        else:
            # contentsとして使用
            data = {
                "to": target_id,
                "messages": [
                    {
                        "type": "flex",
                        "altText": "リマインダー通知",
                        "contents": flex_message_data
                    }
                ],
            }

        try:
            print(f"[SEND] Sending Flex Message to {target_id[:20]}...")

            response = requests.post(
                "https://api.line.me/v2/bot/message/push",
                headers=headers,
                json=data,
                timeout=10,
            )

            print(f"[RESPONSE] Status: {response.status_code}")

            if response.status_code == 200:
                print(f"[SUCCESS] Flex reminder sent to {target_id}")
                success_count += 1
            else:
                try:
                    error_data = response.json()
                    print(f"[ERROR] Failed to send Flex Message to {target_id}: {response.status_code}")
                    print(f"[ERROR] Response: {error_data}")
                except:
                    print(f"[ERROR] Failed to send Flex Message to {target_id}: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Request failed for {target_id}: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected error for {target_id}: {e}")
            import traceback
            traceback.print_exc()

    print(f"[SUMMARY] Successfully sent Flex Messages to {success_count}/{len(target_ids)} targets")
    return success_count > 0


def send_reminder_via_line(note_text):
    """
    LINE経由でリマインダーを送信する（複数の送信先に対応・エラー処理強化）

    Args:
        note_text (str): 送信するメッセージ
    """
    # 環境変数からアクセストークンを取得（フォールバック付き）
    LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")

    # フォールバック: ファイル内のトークンを使用（デバッグ用）
    if not LINE_ACCESS_TOKEN:
        LINE_ACCESS_TOKEN = (
            "fnNGsF7C1h861wsq/9lxqYZtdRdtFQpLnI6lCTcn9TPY7cNF+HaCvIqBZ8OlpW4k"
            "WGRKDWbeygz/UYAx7JbXJ3u+kxkOFSiLYCDPBSoc5WGJkUQRQbkM8/v4pv2mx+w2"
            "BblnaBi1h7ne3u1HHaKLHAdB04t89/1O/w1cDnyilFU="
        )
        print("[WARNING] Using fallback LINE_ACCESS_TOKEN from code")
    else:
        print(f"[INFO] Using LINE_ACCESS_TOKEN from environment (length: {len(LINE_ACCESS_TOKEN)})")

    target_ids = get_target_ids()

    if not target_ids:
        print("[ERROR] No target IDs configured. Cannot send reminder.")
        return False

    # メッセージ長の検証
    if len(note_text) > 5000:
        print(f"[WARNING] Message too long ({len(note_text)} chars), truncating...")
        note_text = note_text[:4900] + "...\n（メッセージが長いため省略されました）"

    headers = {
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    success_count = 0

    print(f"[REMINDER] Attempting to send to {len(target_ids)} target(s)")

    for target_id in target_ids:
        # ターゲットIDの検証
        if not target_id or len(target_id) < 10:
            print(f"[ERROR] Invalid target ID format: {target_id}")
            continue

        # サンプルIDかどうかチェック
        if target_id.startswith("C1234567890abcdef") or target_id == "unknown":
            print(f"[ERROR] Sample/invalid target ID detected: {target_id}")
            continue

        data = {
            "to": target_id,
            "messages": [
                {
                    "type": "text",
                    "text": note_text,
                }
            ],
        }

        try:
            print(f"[SEND] Sending to {target_id[:20]}... (length: {len(target_id)})")

            response = requests.post(
                "https://api.line.me/v2/bot/message/push",
                headers=headers,
                json=data,
                timeout=10,
            )

            print(f"[RESPONSE] Status: {response.status_code}")

            if response.status_code == 200:
                print(f"[SUCCESS] Reminder sent to {target_id}: {note_text[:50]}...")
                success_count += 1
            else:
                # 詳細なエラー情報を出力
                try:
                    error_data = response.json()
                    print(f"[ERROR] Failed to send to {target_id}: {response.status_code}")
                    print(f"[ERROR] Response: {error_data}")

                    # 特定のエラーコードに対する対処法を提示
                    if response.status_code == 400:
                        print("[ERROR] Bad Request - チェック項目:")
                        print("  - ターゲットID形式が正しいか")
                        print("  - メッセージ内容に問題はないか")
                        print("  - Bot がそのチャット/グループに参加しているか")
                    elif response.status_code == 401:
                        print("[ERROR] Unauthorized - アクセストークンを確認してください")
                    elif response.status_code == 403:
                        print("[ERROR] Forbidden - Bot の権限を確認してください")

                except:
                    print(f"[ERROR] Failed to send to {target_id}: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Request failed for {target_id}: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected error for {target_id}: {e}")
            import traceback
            traceback.print_exc()

    print(f"[SUMMARY] Successfully sent to {success_count}/{len(target_ids)} targets")
    return success_count > 0


def reminder_job():
    """
    定期実行されるリマインダージョブ（デュアル通知システム）
    - 入力期限がある場合：前日通知
    - 入力期限がない場合：イベント日の前日・前々日通知
    """
    print(f"[REMINDER] Running reminder job at {datetime.now()}")

    # 複数のソースからターゲットIDを取得
    target_ids = get_target_ids()

    if not target_ids:
        print(
            "[WARNING] No target IDs found. Please configure using one of these methods:"
        )
        print("  1. Send a message to the bot in LINE group (auto-discovery)")
        print("  2. Add ID to reminder_config.json manually")
        print("  3. Set fallback_user_id in config for individual notifications")
        return

    print(f"[REMINDER] Target IDs: {target_ids}")

    try:
        # 明日の通知を取得（入力期限 + イベント前日）
        tomorrow_notes = get_reminders_for_tomorrow()

        # 明後日のイベント通知を取得（イベント前日）
        day_after_tomorrow_notes = get_reminders_for_day_after_tomorrow()

        total_reminders_sent = 0

        # 明日の通知（Flex Message個別送信）
        if tomorrow_notes:
            success_count = 0
            for note in tomorrow_notes:
                # Flex Messageを作成
                flex_message_data = create_flex_reminder_message(note)
                if send_flex_reminder_via_line(flex_message_data):
                    success_count += 1

            print(f"[FLEX_REMINDER] Successfully sent {success_count}/{len(tomorrow_notes)} tomorrow Flex reminders")
            total_reminders_sent += success_count

        # 明後日の通知（Flex Message個別送信）
        if day_after_tomorrow_notes:
            success_count = 0
            for note in day_after_tomorrow_notes:
                # Flex Messageを作成
                flex_message_data = create_flex_reminder_message(note)
                if send_flex_reminder_via_line(flex_message_data):
                    success_count += 1

            print(f"[FLEX_REMINDER] Successfully sent {success_count}/{len(day_after_tomorrow_notes)} day-after-tomorrow Flex reminders")
            total_reminders_sent += success_count

        if total_reminders_sent == 0:
            print("[REMINDER] No upcoming deadlines or events found")

    except Exception as e:
        print(f"[ERROR] Error in reminder job: {e}")
        import traceback

        traceback.print_exc()


# 動的スケジューラー設定（設定ファイルのnotification_timesを使用）
def setup_scheduler():
    """
    設定ファイルのnotification_timesに基づいてスケジューラーを設定する
    """
    scheduler = BackgroundScheduler()
    config = load_config()
    notification_times = config.get(
        "notification_times", DEFAULT_CONFIG["notification_times"]
    )

    print(
        f"[SCHEDULER] Loading {len(notification_times)} notification times from config..."
    )

    for i, time_config in enumerate(notification_times):
        hour = time_config.get("hour", 12)
        minute = time_config.get("minute", 0)

        job_id = f"reminder_{hour:02d}_{minute:02d}"
        job_name = f"Daily Reminder at {hour:02d}:{minute:02d}"

        scheduler.add_job(
            reminder_job,
            "cron",
            hour=hour,
            minute=minute,
            id=job_id,
            name=job_name,
        )

        print(
            f"  - Daily at {hour:02d}:{minute:02d} - notifies about tomorrow's input deadlines"
        )

    return scheduler


print("[SCHEDULER] Starting reminder scheduler...")
scheduler = setup_scheduler()
scheduler.start()
print("[SCHEDULER] TO_USER_ID will be set by uma3.py when messages are received")


@app.route("/")
def home():
    """
    ヘルスチェック用エンドポイント（HTML版）
    """
    from flask import render_template_string

    target_ids = get_target_ids()
    jobs = scheduler.get_jobs()

    template = """
    <html>
    <head>
        <title>LINEリマインダーサービス</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; border-bottom: 3px solid #4CAF50; padding-bottom: 20px; margin-bottom: 30px; }
            .status { background: #d4edda; padding: 15px; border-radius: 5px; margin-bottom: 20px; border-left: 5px solid #28a745; }
            .info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .info-card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; }
            .info-card h3 { margin-top: 0; color: #333; }
            .btn { display: inline-block; background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px; }
            .btn:hover { background: #45a049; }
            .btn-info { background: #17a2b8; }
            .btn-info:hover { background: #138496; }
            .btn-warning { background: #ffc107; color: #212529; }
            .btn-warning:hover { background: #e0a800; }
            .code { font-family: monospace; background: #e9ecef; padding: 2px 6px; border-radius: 3px; }
            .feature-list { list-style-type: none; padding: 0; }
            .feature-list li { margin: 10px 0; padding: 8px; background: #fff; border-left: 3px solid #28a745; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 LINEリマインダーサービス</h1>
                <p>ソフトボールチーム向けノート・リマインダーシステム</p>
            </div>

            <div class="status">
                <strong>✅ サービス稼働中</strong> - {{ current_time }}
            </div>

            <div class="info-grid">
                <div class="info-card">
                    <h3>📊 設定状況</h3>
                    <p><strong>設定済みターゲット:</strong> {{ target_count }}件</p>
                    <p><strong>スケジュール数:</strong> {{ job_count }}件</p>
                    <p><strong>設定ファイル:</strong> <span class="code">{{ config_file }}</span></p>
                </div>

                <div class="info-card">
                    <h3>⏰ リマインダー機能</h3>
                    <ul class="feature-list">
                        <li>📅 入力期限の前日通知</li>
                        <li>🎉 イベント前日通知</li>
                        <li>🌤️ 天気情報統合</li>
                        <li>🔗 ノート詳細URL付き</li>
                    </ul>
                </div>

                <div class="info-card">
                    <h3>🔗 ノートURL機能</h3>
                    <p>リマインダーメッセージにノート詳細へのURLが自動添付されます</p>
                    <p><strong>URL形式:</strong></p>
                    <p class="code">http://localhost:5000/note/{ハッシュID}</p>
                    <p>👆 クリックでノート全文を確認可能</p>
                </div>
            </div>

            <div style="text-align: center; margin-top: 30px;">
                <a href="/config" class="btn btn-info">⚙️ 設定確認</a>
                <a href="/status" class="btn btn-info">📊 ステータス</a>
                <a href="/test-reminder" class="btn btn-warning">🧪 テスト実行</a>
            </div>

            <div style="margin-top: 40px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                <h3>🚀 管理機能</h3>
                <p><strong>設定確認:</strong> <a href="/config">/config</a></p>
                <p><strong>リマインダーテスト:</strong> <a href="/test-reminder">/test-reminder</a></p>
                <p><strong>スケジュール再読込:</strong> <a href="/reload-schedule">/reload-schedule</a></p>
                <p><strong>ターゲットID追加:</strong> /add-target/{新しいID}</p>
            </div>
        </div>
    </body>
    </html>
    """

    return render_template_string(
        template,
        current_time=datetime.now().strftime("%Y年%m月%d日 %H:%M:%S"),
        target_count=len(target_ids),
        job_count=len(jobs),
        config_file=CONFIG_FILE
    )


@app.route("/add-target/<target_id>")
def add_target_endpoint(target_id):
    """
    新しいターゲットIDを追加するエンドポイント
    """
    try:
        add_target_id(target_id)
        return {"status": "success", "message": f"Added target ID: {target_id}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.route("/config")
def get_config():
    """
    現在の設定を表示するエンドポイント
    """
    config = load_config()
    target_ids = get_target_ids()
    return {
        "config": config,
        "active_targets": target_ids,
        "env_target": os.getenv("TO_USER_ID"),
    }


@app.route("/test-reminder")
def test_reminder():
    """
    リマインダーのテスト実行用エンドポイント
    """
    try:
        reminder_job()
        return "Test reminder executed successfully!"
    except Exception as e:
        return f"Test reminder failed: {str(e)}"


@app.route("/debug-tomorrow")
def debug_tomorrow():
    """
    明日の期限検索をデバッグ用エンドポイント
    """
    try:
        notes = get_upcoming_deadline_notes(days_ahead=1)
        return {
            "debug": "tomorrow_deadline_search",
            "count": len(notes),
            "notes": notes,
            "target_date": str((datetime.now().date() + timedelta(days=1))),
        }
    except Exception as e:
        import traceback

        return {"error": str(e), "traceback": traceback.format_exc()}


@app.route("/status")
def status():
    """
    スケジューラーの状態確認用エンドポイント
    """
    jobs = scheduler.get_jobs()
    job_info = []

    for job in jobs:
        next_run = (
            job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")
            if job.next_run_time
            else "Not scheduled"
        )
        job_info.append({"id": job.id, "name": job.name, "next_run": next_run})

    return {
        "scheduler_running": scheduler.running,
        "jobs": job_info,
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


@app.route("/reload-schedule")
def reload_schedule():
    """
    設定ファイルを再読み込みしてスケジューラーを再起動する
    """
    global scheduler

    try:
        print("[SCHEDULER] Stopping current scheduler...")
        scheduler.shutdown(wait=False)

        print("[SCHEDULER] Reloading configuration and restarting scheduler...")
        scheduler = setup_scheduler()
        scheduler.start()

        return {
            "status": "success",
            "message": "Scheduler reloaded successfully",
            "jobs": [{"id": job.id, "name": job.name} for job in scheduler.get_jobs()],
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to reload scheduler: {str(e)}"}


@app.route("/note/<note_id>")
def view_note_detail(note_id):
    """
    ノートの詳細情報を表示する

    Args:
        note_id (str): ノートのハッシュID

    Returns:
        HTML: ノート詳細ページ
    """
    try:
        from flask import request, render_template_string

        # ノートタイトルを取得（URL パラメータから）
        note_title = request.args.get('title', 'ノート詳細')

        # ChromaDBからノートを検索
        vector_db = get_vector_db()
        all_docs = vector_db.get()

        found_note = None
        for doc in all_docs["documents"]:
            if "[ノート]" in doc:
                import hashlib
                doc_hash = hashlib.md5(doc.encode('utf-8')).hexdigest()[:16]
                if doc_hash == note_id:
                    found_note = doc
                    break

        if not found_note:
            return f"""
            <html>
            <head><title>ノートが見つかりません</title></head>
            <body>
                <h1>❌ ノートが見つかりません</h1>
                <p>指定されたノート（ID: {note_id}）は見つかりませんでした。</p>
                <a href="/">トップページに戻る</a>
            </body>
            </html>
            """, 404

        # HTMLテンプレート
        template = """
        <html>
        <head>
            <title>{{ title }}</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background-color: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { border-bottom: 3px solid #4CAF50; padding-bottom: 20px; margin-bottom: 30px; }
                .header h1 { color: #333; margin: 0; }
                .meta-info { background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
                .content { line-height: 1.6; white-space: pre-wrap; font-size: 16px; }
                .btn { display: inline-block; background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 20px; }
                .btn:hover { background: #45a049; }
                .note-id { font-family: monospace; background: #e9ecef; padding: 2px 6px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📝 {{ title }}</h1>
                </div>

                <div class="meta-info">
                    <strong>ノートID:</strong> <span class="note-id">{{ note_id }}</span><br>
                    <strong>データソース:</strong> ChromaDB<br>
                    <strong>生成時刻:</strong> {{ current_time }}
                </div>

                <div class="content">{{ content }}</div>

                <a href="/" class="btn">🏠 トップページに戻る</a>
                <a href="/config" class="btn">⚙️ 設定確認</a>
            </div>
        </body>
        </html>
        """

        return render_template_string(
            template,
            title=note_title,
            note_id=note_id,
            content=found_note,
            current_time=datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
        )

    except Exception as e:
        return f"""
        <html>
        <head><title>エラー</title></head>
        <body>
            <h1>❌ エラーが発生しました</h1>
            <p>ノート詳細の取得中にエラーが発生しました: {str(e)}</p>
            <a href="/">トップページに戻る</a>
        </body>
        </html>
        """, 500


@app.route("/debug-send/<target_id>")
def debug_send_message(target_id):
    """
    特定のターゲットIDにテストメッセージを送信する（デバッグ用）
    """
    test_message = "🔧 テストメッセージ\nこれはデバッグ用の送信テストです。"

    # 環境変数からアクセストークンを取得
    LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
    if not LINE_ACCESS_TOKEN:
        # フォールバック
        LINE_ACCESS_TOKEN = (
            "fnNGsF7C1h861wsq/9lxqYZtdRdtFQpLnI6lCTcn9TPY7cNF+HaCvIqBZ8OlpW4k"
            "WGRKDWbeygz/UYAx7JbXJ3u+kxkOFSiLYCDPBSoc5WGJkUQRQbkM8/v4pv2mx+w2"
            "BblnaBi1h7ne3u1HHaKLHAdB04t89/1O/w1cDnyilFU="
        )

    headers = {
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    data = {
        "to": target_id,
        "messages": [
            {
                "type": "text",
                "text": test_message,
            }
        ],
    }

    try:
        response = requests.post(
            "https://api.line.me/v2/bot/message/push",
            headers=headers,
            json=data,
            timeout=10,
        )

        result = {
            "target_id": target_id,
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "message": test_message,
        }

        if response.status_code == 200:
            result["response"] = "Message sent successfully"
        else:
            try:
                result["error"] = response.json()
            except:
                result["error"] = response.text

        return result

    except Exception as e:
        return {
            "target_id": target_id,
            "error": str(e),
            "success": False
        }


if __name__ == "__main__":
    print("🤖 LINEリマインダーサービスが起動しました。")
    print("📅 ノートの入力期限リマインダー機能（入力期限の前日通知）")
    print("⏰ 送信時刻: 毎日12:00と20:00（明日が入力期限のノートを前日に通知）")
    print()
    print("� グループID取得方法:")
    print("  1. Botにメッセージ送信 → uma3.py が自動設定")
    print("  2. 手動設定 → reminder_config.json に追加")
    print("  3. URL追加 → http://localhost:5001/add-target/YOUR_GROUP_ID")
    print("  4. 設定確認 → http://localhost:5001/config")
    print()
    print("🌐 管理エンドポイント:")
    print("  - ホーム: http://localhost:5001/")
    print("  - 設定確認: http://localhost:5001/config")
    print("  - テスト実行: http://localhost:5001/test-reminder")
    print("  - 状態確認: http://localhost:5001/status")
    print("  - ID追加: http://localhost:5001/add-target/<ID>")
    print()

    # 初期設定の確認
    target_ids = get_target_ids()
    if target_ids:
        print(f"✅ 設定済みターゲット: {target_ids}")
    else:
        print("⚠️  ターゲットIDが未設定です。上記の方法で設定してください。")

    # フラスクアプリを別ポートで起動（uma3.pyと競合を避ける）
    app.run(host="0.0.0.0", port=5001, debug=False)
