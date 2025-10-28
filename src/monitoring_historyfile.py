import os
import subprocess
import time
from datetime import datetime
from threading import Thread

from flask import Flask, jsonify

# Python環境でUTF-8を強制設定（Windows対応）
os.environ["PYTHONIOENCODING"] = "utf-8"

# 監視するディレクトリのパスを指定
WATCH_DIR = (
    r"C:\Users\o_you\iCloudDrive\3L68KQB4HG~com~readdle~CommonDocuments\chat_history"
)
# 監視の間隔（秒単位）
INTERVAL_SEC = 10  # 監視間隔（秒）

app = Flask(__name__)
monitoring_active = False


def get_current_time():
    """現在時刻を文字列で返す"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def watch_directory(path):
    """常時監視してファイル追加時にchathistory2db.pyを呼び出す"""
    global monitoring_active
    monitoring_active = True

    print(f"[{get_current_time()}] 監視開始: {path}")

    # 初回はディレクトリの存在確認
    if not os.path.exists(path):
        print(
            f"[{get_current_time()}] エラー: 監視対象ディレクトリが存在しません: {path}"
        )
        monitoring_active = False
        return

    # 初期ファイルリストを取得
    try:
        prev_files = set(os.listdir(path))
        print(f"[{get_current_time()}] 初期ファイル数: {len(prev_files)}")
        if prev_files:
            print(
                f"[{get_current_time()}] 既存ファイル: {', '.join(list(prev_files)[:3])}{'...' if len(prev_files) > 3 else ''}"
            )
    except Exception as e:
        print(f"[{get_current_time()}] 初期ファイルリスト取得エラー: {e}")
        monitoring_active = False
        return

    cycle_count = 0
    while monitoring_active:
        cycle_count += 1
        time.sleep(INTERVAL_SEC)

        try:
            current_files = set(os.listdir(path))
            added = current_files - prev_files

            # print(
            #     f"[{get_current_time()}] 監視サイクル #{cycle_count} - ファイル数: {len(current_files)}"
            # )

            if added:
                print(f"[{get_current_time()}] 🆕 新規ファイル検出: {', '.join(added)}")
                try:
                    script_path = os.path.join(
                        os.path.dirname(__file__), "chathistory2db.py"
                    )
                    print(f"[{get_current_time()}] chathistory2db.py実行中...")
                    result = subprocess.run(
                        ["python", script_path],
                        capture_output=True,
                        text=True,
                        check=True,
                        encoding="utf-8",
                        errors="replace",
                    )
                    print(f"[{get_current_time()}] ✅ chathistory2db.py実行完了")
                    if result.stdout:
                        print(f"[{get_current_time()}] 出力: {result.stdout.strip()}")
                except UnicodeDecodeError as e:
                    print(f"[{get_current_time()}] ❌ 文字エンコーディングエラー: {e}")
                    print(f"[{get_current_time()}] UTF-8への変換に失敗しました")
                except subprocess.CalledProcessError as e:
                    print(f"[{get_current_time()}] ❌ chathistory2db.py実行エラー: {e}")
                    if e.stderr:
                        print(f"[{get_current_time()}] エラー詳細: {e.stderr}")
                except Exception as e:
                    print(f"[{get_current_time()}] ❌ 予期しないエラー: {e}")
                    print(f"[{get_current_time()}] エラータイプ: {type(e).__name__}")
                except Exception as e:
                    print(f"[{get_current_time()}] ❌ 予期しないエラー: {e}")
            # else:
            # print(f"[{get_current_time()}] 新しいファイルはありませんでした。")

            prev_files = current_files  # 状態を更新

        except Exception as e:
            print(f"[{get_current_time()}] 監視中にエラー: {e}")

    print(f"[{get_current_time()}] 監視を停止しました。")


@app.route("/")
def status():
    """監視状況の確認"""
    return jsonify(
        {
            "status": "File Monitoring Service",
            "monitoring_active": monitoring_active,
            "watch_directory": WATCH_DIR,
            "interval_seconds": INTERVAL_SEC,
            "current_time": get_current_time(),
        }
    )


@app.route("/start")
def start_monitoring():
    """監視を手動で開始"""
    global monitoring_active
    if monitoring_active:
        return jsonify(
            {"status": "already_running", "message": "監視は既に実行中です。"}
        )

    t = Thread(target=watch_directory, args=(WATCH_DIR,), daemon=True)
    t.start()
    return jsonify(
        {"status": "started", "message": "常時監視をバックグラウンドで開始しました。"}
    )


@app.route("/stop")
def stop_monitoring():
    """監視を停止"""
    global monitoring_active
    monitoring_active = False
    return jsonify({"status": "stopped", "message": "監視を停止しました。"})


@app.route("/force-check")
def force_check():
    """手動でchathistory2db.pyを実行"""
    try:
        script_path = os.path.join(os.path.dirname(__file__), "chathistory2db.py")
        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        )
        return jsonify(
            {
                "status": "success",
                "message": "chathistory2db.py実行完了",
                "output": result.stdout,
            }
        )
    except UnicodeDecodeError as e:
        return jsonify(
            {
                "status": "error",
                "message": f"文字エンコーディングエラー: {e}",
                "error_type": "UnicodeDecodeError",
            }
        )
    except subprocess.CalledProcessError as e:
        return jsonify(
            {"status": "error", "message": f"実行エラー: {e}", "stderr": e.stderr}
        )
    except Exception as e:
        return jsonify(
            {
                "status": "error",
                "message": f"予期しないエラー: {e}",
                "error_type": type(e).__name__,
            }
        )


def auto_start_monitoring():
    """アプリケーション起動時に自動で監視開始"""
    print(f"[{get_current_time()}] 自動監視を開始します...")
    t = Thread(target=watch_directory, args=(WATCH_DIR,), daemon=True)
    t.start()


if __name__ == "__main__":
    print(f"[{get_current_time()}] File Monitoring Service starting...")
    auto_start_monitoring()  # 自動で監視開始
    app.run(host="0.0.0.0", port=5003, debug=False, use_reloader=False)
