#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Uma3 Software 機械学習統合システム クイックスタート
LINE Bot + ML統合システムを一括で起動・停止するためのユーティリティ
"""

import os
import sys
import subprocess
import time
import json
import requests
from pathlib import Path
import argparse
import signal
import psutil

# プロジェクトルート設定
PROJECT_ROOT = Path(r"C:\work\ws_python\GenerationAiCamp")
VENV_PYTHON = PROJECT_ROOT / 'venv' / 'Scripts' / 'python.exe'
SRC_PATH = PROJECT_ROOT / 'Lesson25' / 'uma3soft-app' / 'src'

class Uma3QuickStart:
    """Uma3システム一括管理クラス"""

    def __init__(self):
        self.processes = {}
        self.ngrok_url = None

    def check_prerequisites(self) -> bool:
        """前提条件チェック"""
        print("🔍 前提条件チェック中...")

        # Python環境確認
        if not VENV_PYTHON.exists():
            print(f"  ❌ Python仮想環境が見つかりません: {VENV_PYTHON}")
            return False
        print("  ✅ Python仮想環境: OK")

        # MLモデル確認
        models_path = PROJECT_ROOT / 'Lesson25' / 'uma3soft-app' / 'ml_models'
        required_models = [
            'classification_model.pkl',
            'clustering_model.pkl',
            'vectorizer.pkl',
            'scaler.pkl'
        ]

        missing_models = []
        for model in required_models:
            if not (models_path / model).exists():
                missing_models.append(model)

        if missing_models:
            print(f"  ⚠️ 不足しているモデル: {missing_models}")
            print("  💡 モデル訓練を実行してください: python src/ml_training_system_offline.py")
            return False
        print("  ✅ 機械学習モデル: OK")

        # ngrokの確認
        try:
            subprocess.run(['ngrok', 'version'], capture_output=True, check=True)
            print("  ✅ ngrok: OK")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("  ❌ ngrokが見つかりません")
            print("  💡 ngrokをインストールしてください: https://ngrok.com/download")
            return False

        return True

    def start_ngrok(self) -> str:
        """ngrokトンネル開始"""
        print("🌐 ngrokトンネル開始中...")

        # 既存のngrokプロセスを停止
        self.stop_process('ngrok')

        # ngrok起動
        ngrok_cmd = ['ngrok', 'http', '5000', '--log=stdout', '--region=jp']

        try:
            # ngrokをバックグラウンドで起動
            process = subprocess.Popen(
                ngrok_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(SRC_PATH)
            )

            self.processes['ngrok'] = process

            # ngrokの起動を待機
            print("  ⏳ ngrok起動を待機中...")
            time.sleep(5)

            # ngrok URLを取得
            try:
                response = requests.get('http://localhost:4040/api/tunnels', timeout=10)
                if response.status_code == 200:
                    tunnels = response.json()['tunnels']
                    if tunnels:
                        self.ngrok_url = tunnels[0]['public_url']
                        print(f"  ✅ ngrok URL: {self.ngrok_url}")
                        return self.ngrok_url
                    else:
                        print("  ⚠️ ngrokトンネルが見つかりません")
                else:
                    print(f"  ⚠️ ngrok API応答エラー: {response.status_code}")
            except requests.RequestException as e:
                print(f"  ⚠️ ngrok URL取得エラー: {e}")

            return "ngrok起動中（URL取得は手動で確認してください）"

        except Exception as e:
            print(f"  ❌ ngrok起動エラー: {e}")
            return None

    def start_linebot_with_ml(self) -> bool:
        """LINE Bot + ML統合システム起動"""
        print("🤖 LINE Bot + ML統合システム起動中...")

        try:
            # uma3.pyを起動
            uma3_script = SRC_PATH / 'uma3.py'

            if not uma3_script.exists():
                print(f"  ❌ uma3.pyが見つかりません: {uma3_script}")
                return False

            cmd = [str(VENV_PYTHON), str(uma3_script)]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(PROJECT_ROOT)
            )

            self.processes['linebot'] = process

            print("  ✅ LINE Bot起動完了")
            print(f"  📱 Webhook URL: {self.ngrok_url}/callback")
            return True

        except Exception as e:
            print(f"  ❌ LINE Bot起動エラー: {e}")
            return False

    def run_system_check(self) -> bool:
        """システム動作確認"""
        print("🧪 システム動作確認中...")

        try:
            # 統合テスト実行
            test_script = SRC_PATH / 'ml_integration_test.py'

            if not test_script.exists():
                print("  ⚠️ 統合テストスクリプトが見つかりません")
                return True  # テストがなくても続行

            cmd = [str(VENV_PYTHON), str(test_script)]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(PROJECT_ROOT)
            )

            if result.returncode == 0:
                print("  ✅ システム動作確認: 正常")

                # テスト結果から重要情報を抽出
                lines = result.stdout.split('\n')
                for line in lines:
                    if '🎯 成功テスト:' in line:
                        print(f"  📊 {line.strip()}")
                    elif '⚡ 分類精度:' in line:
                        print(f"  📊 {line.strip()}")
                    elif '📊 処理スループット:' in line:
                        print(f"  📊 {line.strip()}")

                return True
            else:
                print("  ⚠️ システム動作確認: 一部問題あり")
                print(f"  💡 詳細: {result.stderr[:200]}...")
                return False

        except subprocess.TimeoutExpired:
            print("  ⏰ システム動作確認: タイムアウト")
            return False
        except Exception as e:
            print(f"  ❌ システム動作確認エラー: {e}")
            return False

    def stop_process(self, process_name: str):
        """指定プロセス停止"""
        print(f"🛑 {process_name}プロセス停止中...")

        # 管理下のプロセス停止
        if process_name in self.processes:
            process = self.processes[process_name]
            try:
                process.terminate()
                process.wait(timeout=10)
                print(f"  ✅ {process_name}プロセス停止完了")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"  🔥 {process_name}プロセス強制終了")
            except Exception as e:
                print(f"  ⚠️ {process_name}プロセス停止エラー: {e}")

            del self.processes[process_name]

        # システム全体の同名プロセス停止
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                        proc.terminate()
                        print(f"  🛑 {process_name} PID {proc.info['pid']} 停止")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"  ⚠️ システムプロセス停止エラー: {e}")

    def stop_all(self):
        """全プロセス停止"""
        print("🛑 全システム停止中...")

        self.stop_process('python')
        self.stop_process('ngrok')

        print("  ✅ 全システム停止完了")

    def show_status(self):
        """システム状態表示"""
        print("📊 システム状態:")

        # プロセス状態
        python_procs = []
        ngrok_procs = []

        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name']:
                    if 'python' in proc.info['name'].lower():
                        if proc.info['cmdline'] and any('uma3' in str(cmd).lower() for cmd in proc.info['cmdline']):
                            python_procs.append(f"PID {proc.info['pid']}")
                    elif 'ngrok' in proc.info['name'].lower():
                        ngrok_procs.append(f"PID {proc.info['pid']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        print(f"  🐍 Python (uma3): {len(python_procs)}個 {python_procs}")
        print(f"  🌐 ngrok: {len(ngrok_procs)}個 {ngrok_procs}")

        # ngrok URL確認
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
            if response.status_code == 200:
                tunnels = response.json()['tunnels']
                if tunnels:
                    print(f"  🔗 Webhook URL: {tunnels[0]['public_url']}/callback")
                else:
                    print("  ⚠️ ngrokトンネルなし")
            else:
                print("  ⚠️ ngrok API接続不可")
        except:
            print("  ⚠️ ngrok状態確認不可")

    def start_complete_system(self):
        """完全システム起動"""
        print("🚀 Uma3 Machine Learning統合システム起動")
        print("=" * 50)

        # 1. 前提条件チェック
        if not self.check_prerequisites():
            print("❌ 前提条件が満たされていません")
            return False

        # 2. ngrok起動
        ngrok_url = self.start_ngrok()
        if not ngrok_url:
            print("❌ ngrok起動に失敗しました")
            return False

        # 3. システム動作確認
        if not self.run_system_check():
            print("⚠️ システム動作確認で問題が検出されましたが続行します")

        # 4. LINE Bot起動
        if not self.start_linebot_with_ml():
            print("❌ LINE Bot起動に失敗しました")
            self.stop_all()
            return False

        print("\n🎉 Sistema起動完了!")
        print("=" * 50)
        print(f"📱 LINE Bot Webhook URL: {ngrok_url}/callback")
        print("🌐 ngrok Web UI: http://localhost:4040")
        print("🤖 システムは機械学習統合モードで動作中です")
        print("\n💡 停止するには Ctrl+C を押すか、--stop オプションを使用してください")

        return True

def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description='Uma3 Software ML System Quick Start')
    parser.add_argument('--action', choices=[
        'start', 'stop', 'restart', 'status', 'check'
    ], default='start', help='実行するアクション')

    args = parser.parse_args()

    manager = Uma3QuickStart()

    try:
        if args.action == 'start':
            success = manager.start_complete_system()
            if success:
                # システム起動後は待機
                try:
                    while True:
                        time.sleep(10)
                        # プロセス生存確認
                        alive_count = 0
                        for name, proc in manager.processes.items():
                            if proc.poll() is None:  # プロセスが生きている
                                alive_count += 1
                            else:
                                print(f"⚠️ {name}プロセスが終了しました")

                        if alive_count == 0:
                            print("❌ 全プロセスが終了しました")
                            break

                except KeyboardInterrupt:
                    print("\n🛑 終了要求を受信しました")
                    manager.stop_all()

        elif args.action == 'stop':
            manager.stop_all()

        elif args.action == 'restart':
            manager.stop_all()
            time.sleep(3)
            manager.start_complete_system()

        elif args.action == 'status':
            manager.show_status()

        elif args.action == 'check':
            if manager.check_prerequisites():
                print("✅ 前提条件チェック完了")
                manager.run_system_check()
            else:
                print("❌ 前提条件チェック失敗")

        return 0

    except Exception as e:
        print(f"❌ エラー: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
