import os
import subprocess
import time

from flask import Flask, jsonify

# 監視するディレクトリのパスを指定
WATCH_DIR = (
    r"C:\Users\o_you\iCloudDrive\3L68KQB4HG~com~readdle~CommonDocuments\chat_history"
)
# 監視の間隔（秒単位）
INTERVAL_SEC = 10  # 監視間隔（秒）

app = Flask(__name__)


def watch_directory(path):
    """常時監視してファイル追加時にchathistory2db.pyを呼び出す"""
    print(f"監視開始: {path}")
    prev_files = set(os.listdir(path))
    while True:
        time.sleep(INTERVAL_SEC)
        current_files = set(os.listdir(path))
        added = current_files - prev_files

        if added:
            print(f"[追加] {', '.join(added)}")
            try:
                script_path = os.path.join(
                    os.path.dirname(__file__), "chathistory2db.py"
                )
                subprocess.run(["python", script_path], check=True)
                print("chathistory2db.pyを実行しました。")
            except Exception as e:
                print(f"chathistory2db.pyの実行中にエラー: {e}")
        else:
            print("新しいファイルはありませんでした。")

        prev_files = current_files  # 状態を更新


@app.route("/")
def trigger_watch():
    """ルートURLアクセス時に監視をバックグラウンドで開始"""
    from threading import Thread

    t = Thread(target=watch_directory, args=(WATCH_DIR,), daemon=True)
    t.start()
    return jsonify({"status": "常時監視をバックグラウンドで開始しました。"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True, use_reloader=False)
