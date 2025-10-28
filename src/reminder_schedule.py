import json
import os
import re
from datetime import datetime, timedelta

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# グループID
os.environ["TO_USER_ID"] = "C42ebf9338d5017559f0007dd0b52529c"

# 設定ファイルのパス（実行ディレクトリからの相対パス）
CONFIG_FILE = os.path.join("Lesson25", "uma3soft-app", "src", "reminder_config.json")

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


def format_reminder_message(notes, notification_type="standard"):
    """
    リマインダーメッセージを整形する（入力期限・前日・前々日通知対応）

    Args:
        notes (list): ノートリスト
        notification_type (str): 通知タイプ ("standard", "day_before", "two_days_before")

    Returns:
        str: 整形されたメッセージ
    """
    if not notes:
        return "⏰ 直近の入力期限は見つかりませんでした。"

    if len(notes) == 1:
        note = notes[0]
        days_until = note["days_until"]
        is_input_deadline = note.get("is_input_deadline", False)
        reminder_type = note.get("reminder_type", "standard")
        event_date = note["date"]  # イベントの日付を取得

        # 日付を日本語形式でフォーマット
        formatted_date = event_date.strftime("%Y年%m月%d日")
        weekdays = ["月", "火", "水", "木", "金", "土", "日"]
        weekday = weekdays[event_date.weekday()]
        date_with_weekday = f"{formatted_date}({weekday})"

        # 通知タイプに応じてメッセージを調整
        if is_input_deadline:
            # 入力期限がある場合
            if days_until == 1:
                prefix = f"⏰ 【リマインダー（前日）】\n\n{date_with_weekday}のイベントの入力期限です。\nご確認ください。\n"
            elif days_until == 0:
                prefix = f"⚠️ 【リマインダー（前日）】\n\n{date_with_weekday}のイベントの入力期限(本日)です。\nよろしくお願いします。\n"
            else:
                prefix = f"📅 【リマインダー（{days_until}日後）】\n\n{date_with_weekday}の予定です。\nご確認ください。\n"
        else:
            # 入力期限がない場合（イベント日）
            if days_until == 2:
                prefix = f"⏰ 【リマインダー（前々日通知）】\n\n{date_with_weekday}のイベントです。\nご確認ください。\n"
            elif days_until == 1:
                prefix = f"⏰ 【リマインダー（前日通知）】\n\n{date_with_weekday}のイベントです。\nよろしくお願いします。\n"
            elif days_until == 0:
                prefix = f"⚠️ 【リマインダー（当日）】\n\n{date_with_weekday}（本日）のイベントです。\nご注意ください。\n"
            else:
                prefix = f"📅 【リマインダー（{days_until}日後）】\n\n{date_with_weekday}のイベントです。\nご確認ください。\n"

        return f"{prefix}\n\n{note['content']}"

    # 複数の予定がある場合
    has_input_deadlines = any(note.get("is_input_deadline", False) for note in notes)
    has_events = any(not note.get("is_input_deadline", False) for note in notes)

    if has_input_deadlines and has_events:
        message = "⏰ 今後の予定リマインダー\n\n"
    elif has_input_deadlines:
        message = "⏰ 入力期限リマインダー\n\n"
    else:
        message = "⏰ イベント予定リマインダー\n\n"

    for i, note in enumerate(notes[:3], 1):  # 最大3件
        days_until = note["days_until"]
        is_input_deadline = note.get("is_input_deadline", False)
        event_date = note["date"]  # イベントの日付を取得

        # 日付を日本語形式でフォーマット
        formatted_date = event_date.strftime("%Y年%m月%d日")
        weekdays = ["月", "火", "水", "木", "金", "土", "日"]
        weekday = weekdays[event_date.weekday()]
        date_with_weekday = f"{formatted_date}({weekday})"

        if is_input_deadline:
            if days_until == 1:
                date_info = f"明日が入力期限【{date_with_weekday}】"
            elif days_until == 0:
                date_info = f"本日が入力期限【{date_with_weekday}】"
            else:
                date_info = f"{days_until}日後が入力期限【{date_with_weekday}】"
        else:
            if days_until == 2:
                date_info = f"明後日の予定（前々日通知）【{date_with_weekday}】"
            elif days_until == 1:
                date_info = f"明日の予定（前日通知）【{date_with_weekday}】"
            elif days_until == 0:
                date_info = f"本日の予定【{date_with_weekday}】"
            else:
                date_info = f"{days_until}日後の予定【{date_with_weekday}】"

        message += f"{i}. {date_info}\n{note['content']}\n\n"

    return message.strip()


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

        # 明日の通知
        if tomorrow_notes:
            message = format_reminder_message(tomorrow_notes, "day_before")
            success = send_reminder_via_line(message)
            if success:
                print(
                    f"[REMINDER] Successfully sent tomorrow reminder for {len(tomorrow_notes)} note(s)"
                )
                total_reminders_sent += len(tomorrow_notes)
            else:
                print("[REMINDER] Failed to send tomorrow reminders")

        # 明後日の通知（前日通知）
        if day_after_tomorrow_notes:
            message = format_reminder_message(day_after_tomorrow_notes, "day_before")
            success = send_reminder_via_line(message)
            if success:
                print(
                    f"[REMINDER] Successfully sent day-after-tomorrow reminder for {len(day_after_tomorrow_notes)} note(s)"
                )
                total_reminders_sent += len(day_after_tomorrow_notes)
            else:
                print("[REMINDER] Failed to send day-after-tomorrow reminders")

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
    ヘルスチェック用エンドポイント
    """
    target_ids = get_target_ids()
    return {
        "status": "LINE Reminder Service is running!",
        "configured_targets": len(target_ids),
        "target_ids": target_ids,
        "config_file": CONFIG_FILE,
    }


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
