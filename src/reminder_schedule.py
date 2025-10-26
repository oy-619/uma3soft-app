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

# ChromaDBの設定（実行ディレクトリからの相対パス - dbディレクトリを使用）
PERSIST_DIRECTORY = os.path.join("Lesson25", "uma3soft-app", "db")

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
    送信先IDを取得する（複数の方法を試行）

    Returns:
        list: 送信先IDのリスト
    """
    target_ids = []

    # 1. 環境変数から取得（uma3.pyで設定）
    env_id = os.getenv("TO_USER_ID")
    if env_id:
        target_ids.append(env_id)
        print(f"[TARGET] Found target ID from environment: {env_id}")

    # 2. 設定ファイルから取得
    config = load_config()
    config_ids = config.get("target_ids", [])
    for config_id in config_ids:
        if config_id not in target_ids:
            target_ids.append(config_id)
            print(f"[TARGET] Found target ID from config: {config_id}")

    # 3. フォールバックユーザーID
    fallback_id = config.get("fallback_user_id")
    if fallback_id and fallback_id not in target_ids:
        target_ids.append(fallback_id)
        print(f"[TARGET] Using fallback user ID: {fallback_id}")

    if not target_ids:
        print("[WARNING] No target IDs found. Please configure manually.")

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
    指定日数以内に期限が来るノートを検索する

    Args:
        days_ahead (int): 何日先までの期限を検索するか

    Returns:
        list: 期限付きノートのリスト（日付順）
    """
    today = datetime.now().date()
    target_date_range = [(today + timedelta(days=i)) for i in range(1, days_ahead + 1)]

    print(f"[REMINDER] Searching for notes with deadlines in next {days_ahead} days...")

    # [ノート]データを検索
    vector_db = get_vector_db()
    notes = vector_db.similarity_search("[ノート]", k=50)
    upcoming_notes = []

    for note in notes:
        content = note.page_content
        if "[ノート]" not in content:
            continue

        # 日付パターンを検索
        date_patterns = [
            r"(\d{4})/(\d{1,2})/(\d{1,2})",  # 2024/12/25形式
            r"(\d{1,2})月(\d{1,2})日",  # 12月25日形式
            r"(\d{1,2})/(\d{1,2})",  # 12/25形式
        ]

        found_dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                try:
                    if len(match) == 3:  # 年/月/日
                        year, month, day = map(int, match)
                        note_date = datetime(year, month, day).date()
                    elif len(match) == 2:
                        if "月" in pattern:  # 月日形式
                            month, day = map(int, match)
                            year = today.year
                            # 過去の月の場合は翌年とする
                            if month < today.month or (
                                month == today.month and day < today.day
                            ):
                                year += 1
                            note_date = datetime(year, month, day).date()
                        else:  # MM/DD形式
                            month, day = map(int, match)
                            year = today.year
                            if month < today.month or (
                                month == today.month and day < today.day
                            ):
                                year += 1
                            note_date = datetime(year, month, day).date()

                    found_dates.append(note_date)
                except ValueError:
                    continue

        # 期限内の日付があるかチェック
        for note_date in found_dates:
            if note_date in target_date_range:
                upcoming_notes.append(
                    {
                        "content": content,
                        "date": note_date,
                        "days_until": (note_date - today).days,
                    }
                )
                break

    # 日付順にソート
    upcoming_notes.sort(key=lambda x: x["date"])

    print(f"[REMINDER] Found {len(upcoming_notes)} upcoming deadline notes")
    return upcoming_notes


def get_next_day_reminders():
    """
    明日の予定/期限のノートを取得する（前日通知用）

    Returns:
        list: 明日の予定リスト
    """
    tomorrow = (datetime.now() + timedelta(days=1)).date()

    print(f"[REMINDER] Looking for tomorrow's schedule: {tomorrow}")

    # 明日の予定を検索
    upcoming_notes = get_upcoming_deadline_notes(days_ahead=1)
    tomorrow_notes = [note for note in upcoming_notes if note["date"] == tomorrow]

    if not tomorrow_notes:
        # 明日の予定がない場合は、直近の予定を1件取得
        upcoming_notes = get_upcoming_deadline_notes(days_ahead=14)
        if upcoming_notes:
            print(
                f"[REMINDER] No tomorrow's schedule found, using next upcoming: {upcoming_notes[0]['date']}"
            )
            return [upcoming_notes[0]]
    else:
        print(f"[REMINDER] Found {len(tomorrow_notes)} schedule(s) for tomorrow")

    return tomorrow_notes


def format_reminder_message(notes):
    """
    リマインダーメッセージを整形する

    Args:
        notes (list): ノートリスト

    Returns:
        str: 整形されたメッセージ
    """
    if not notes:
        return "⏰ 直近の予定は見つかりませんでした。"

    if len(notes) == 1:
        note = notes[0]
        days_until = note["days_until"]

        if days_until == 1:
            prefix = "⏰ 明日の予定リマインダー"
        elif days_until == 0:
            prefix = "⚠️ 本日の予定"
        else:
            prefix = f"📅 {days_until}日後の予定"

        return f"{prefix}\n\n{note['content']}"

    # 複数の予定がある場合
    message = "⏰ 今後の予定リマインダー\n\n"
    for i, note in enumerate(notes[:3], 1):  # 最大3件
        days_until = note["days_until"]
        if days_until == 1:
            date_info = "明日"
        elif days_until == 0:
            date_info = "本日"
        else:
            date_info = f"{days_until}日後"

        message += f"{i}. {date_info}\n{note['content']}\n\n"

    return message.strip()


def send_reminder_via_line(note_text):
    """
    LINE経由でリマインダーを送信する（複数の送信先に対応）

    Args:
        note_text (str): 送信するメッセージ
    """
    LINE_ACCESS_TOKEN = (
        "fnNGsF7C1h861wsq/9lxqYZtdRdtFQpLnI6lCTcn9TPY7cNF+HaCvIqBZ8OlpW4k"
        "WGRKDWbeygz/UYAx7JbXJ3u+kxkOFSiLYCDPBSoc5WGJkUQRQbkM8/v4pv2mx+w2"
        "BblnaBi1h7ne3u1HHaKLHAdB04t89/1O/w1cDnyilFU="
    )

    target_ids = get_target_ids()

    if not target_ids:
        print("[ERROR] No target IDs configured. Cannot send reminder.")
        return False

    headers = {
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    success_count = 0

    for target_id in target_ids:
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
            response = requests.post(
                "https://api.line.me/v2/bot/message/push",
                headers=headers,
                json=data,
                timeout=10,
            )

            if response.status_code == 200:
                print(f"[SUCCESS] Reminder sent to {target_id}: {note_text[:50]}...")
                success_count += 1
            else:
                print(
                    f"[ERROR] Failed to send to {target_id}: {response.status_code} - {response.text}"
                )

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Request failed for {target_id}: {e}")

    return success_count > 0


def reminder_job():
    """
    定期実行されるリマインダージョブ（前日通知）
    複数のソースからターゲットIDを取得
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
        # 明日の予定を取得（前日通知）
        tomorrow_notes = get_next_day_reminders()

        if tomorrow_notes:
            message = format_reminder_message(tomorrow_notes)
            success = send_reminder_via_line(message)
            if success:
                print(
                    f"[REMINDER] Successfully sent reminder for {len(tomorrow_notes)} note(s)"
                )
            else:
                print("[REMINDER] Failed to send reminders")
        else:
            print("[REMINDER] No upcoming notes found")

    except Exception as e:
        print(f"[ERROR] Error in reminder job: {e}")
        import traceback

        traceback.print_exc()


# スケジューラー設定（前日通知：毎日12:00と20:00）
scheduler = BackgroundScheduler()

# 毎日12:00にリマインダーを送信（明日の予定を前日通知）
scheduler.add_job(
    reminder_job,
    "cron",
    hour=9,
    minute=20,
    id="reminder_noon",
    name="Daily Reminder at Noon (Previous Day Notification)",
)

# 毎日20:00にリマインダーを送信（明日の予定を前日通知）
scheduler.add_job(
    reminder_job,
    "cron",
    hour=20,
    minute=0,
    id="reminder_evening",
    name="Daily Reminder at Evening (Previous Day Notification)",
)

# テスト用：1分毎に実行（開発時のみ使用）
# scheduler.add_job(
#     reminder_job,
#     "interval",
#     minutes=1,
#     id="test_reminder",
#     name="Test Reminder (Every Minute)"
# )

print("[SCHEDULER] Starting reminder scheduler...")
scheduler.start()
print("[SCHEDULER] Reminder jobs scheduled for previous day notification:")
print("  - Daily at 12:00 (noon) - notifies about tomorrow's schedule")
print("  - Daily at 20:00 (evening) - notifies about tomorrow's schedule")
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


if __name__ == "__main__":
    print("🤖 LINEリマインダーサービスが起動しました。")
    print("📅 期限付きノートの自動リマインダー機能（前日通知）")
    print("⏰ 送信時刻: 毎日12:00と20:00（明日の予定を前日に通知）")
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
