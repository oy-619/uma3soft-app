#!/usr/bin/env python3
"""
LINE Bot起動スクリプト
"""
import os
import subprocess
import sys
import time


def start_line_bot():
    """LINE Botを起動"""
    print("🤖 LINE Bot稼働開始!")
    print("=" * 50)

    # 環境確認
    env_check = subprocess.run(
        [
            sys.executable,
            "-c",
            "import os; from dotenv import load_dotenv; load_dotenv(); "
            "print('✅ OpenAI API:', '設定済み' if os.getenv('OPENAI_API_KEY') else '❌未設定'); "
            "print('✅ LINE Token:', '設定済み' if os.getenv('LINE_ACCESS_TOKEN') else '❌未設定'); "
            "print('✅ LINE Secret:', '設定済み' if os.getenv('LINE_CHANNEL_SECRET') else '❌未設定')",
        ],
        capture_output=True,
        text=True,
    )

    print("🔧 環境設定確認:")
    print(env_check.stdout)

    if env_check.returncode != 0:
        print("❌ 環境設定に問題があります")
        return False

    print("\n🚀 Flask サーバー起動中...")
    print("📱 LINE Webhook URL: http://localhost:5000/callback")
    print("⚠️  ngrokなどでHTTPS公開が必要です")
    print("🛑 停止するには Ctrl+C を押してください")
    print("=" * 50)

    # Flask アプリケーション起動
    try:
        os.chdir("src")
        subprocess.run(
            [
                sys.executable,
                "-c",
                "import uma3; uma3.app.run(host='0.0.0.0', port=5000, debug=True)",
            ]
        )
    except KeyboardInterrupt:
        print("\n🛑 LINE Bot 停止")
        return True
    except Exception as e:
        print(f"❌ 起動エラー: {e}")
        return False


if __name__ == "__main__":
    success = start_line_bot()
    sys.exit(0 if success else 1)
