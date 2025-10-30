#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Uma3 Software 機械学習システム運用管理ツール
日常運用・監視・メンテナンスを自動化するための統合管理システム
"""

import os
import sys
import json
import logging
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
import argparse
import psutil
import sqlite3

# プロジェクトルート設定
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / 'src'))

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(PROJECT_ROOT / 'logs' / 'operation_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Uma3OperationManager:
    """Uma3 機械学習システム運用管理クラス"""

    def __init__(self):
        # 正しいプロジェクトパス設定
        self.project_root = Path(r"C:\work\ws_python\GenerationAiCamp")
        self.venv_python = self.project_root / 'venv' / 'Scripts' / 'python.exe'
        self.ml_models_path = self.project_root / 'Lesson25' / 'uma3soft-app' / 'ml_models'
        self.logs_path = self.project_root / 'Lesson25' / 'uma3soft-app' / 'logs'
        self.src_path = self.project_root / 'Lesson25' / 'uma3soft-app' / 'src'

        # 運用メトリクス
        self.metrics = {
            'system_health': {},
            'performance': {},
            'errors': [],
            'maintenance_log': []
        }

    def check_system_health(self) -> dict:
        """システム健全性チェック"""
        print("🏥 システム健全性チェック実行中...")

        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'components': {}
        }

        try:
            # 1. Python環境チェック
            if self.venv_python.exists():
                health_status['components']['python_env'] = 'OK'
                print("  ✅ Python仮想環境: 正常")
            else:
                health_status['components']['python_env'] = 'ERROR'
                health_status['overall_status'] = 'unhealthy'
                print("  ❌ Python仮想環境: 見つかりません")

            # 2. 学習済みモデルチェック
            required_models = [
                'classification_model.pkl',
                'clustering_model.pkl',
                'vectorizer.pkl',
                'scaler.pkl'
            ]

            missing_models = []
            for model in required_models:
                model_path = self.ml_models_path / model
                if model_path.exists():
                    size_mb = model_path.stat().st_size / 1024 / 1024
                    print(f"  ✅ {model}: 正常 ({size_mb:.1f}MB)")
                else:
                    missing_models.append(model)
                    print(f"  ❌ {model}: 見つかりません")

            if missing_models:
                health_status['components']['ml_models'] = f'MISSING: {missing_models}'
                health_status['overall_status'] = 'unhealthy'
            else:
                health_status['components']['ml_models'] = 'OK'

            # 3. データベース接続チェック
            try:
                db_path = self.project_root / 'Lesson25' / 'uma3soft-app' / 'db' / 'chroma_store'
                if db_path.exists():
                    health_status['components']['database'] = 'OK'
                    print("  ✅ ChromaDB: 接続可能")
                else:
                    health_status['components']['database'] = 'WARNING'
                    print("  ⚠️ ChromaDB: パスが見つかりません")
            except Exception as e:
                health_status['components']['database'] = f'ERROR: {e}'
                print(f"  ❌ データベース: {e}")

            # 4. ディスク容量チェック
            try:
                disk_usage = psutil.disk_usage(str(self.project_root))
                free_gb = disk_usage.free / 1024 / 1024 / 1024

                if free_gb > 5.0:  # 5GB以上の空き容量
                    health_status['components']['disk_space'] = f'OK ({free_gb:.1f}GB free)'
                    print(f"  ✅ ディスク容量: {free_gb:.1f}GB 利用可能")
                else:
                    health_status['components']['disk_space'] = f'WARNING ({free_gb:.1f}GB free)'
                    health_status['overall_status'] = 'warning'
                    print(f"  ⚠️ ディスク容量: {free_gb:.1f}GB（容量不足の可能性）")

            except Exception as e:
                health_status['components']['disk_space'] = f'ERROR: {e}'
                print(f"  ❌ ディスク容量チェック: {e}")

            # 5. プロセス状態チェック
            python_processes = []
            ngrok_processes = []

            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'python' in proc.info['name'].lower():
                        if proc.info['cmdline'] and any('uma3' in cmd.lower() for cmd in proc.info['cmdline']):
                            python_processes.append(proc.info['pid'])

                    if proc.info['name'] and 'ngrok' in proc.info['name'].lower():
                        ngrok_processes.append(proc.info['pid'])

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            health_status['components']['processes'] = {
                'python_processes': len(python_processes),
                'ngrok_processes': len(ngrok_processes)
            }

            print(f"  📊 実行中プロセス: Python={len(python_processes)}, ngrok={len(ngrok_processes)}")

        except Exception as e:
            logger.error(f"システム健全性チェックエラー: {e}")
            health_status['overall_status'] = 'error'
            health_status['error'] = str(e)

        self.metrics['system_health'] = health_status
        return health_status

    def run_integration_test(self) -> dict:
        """統合テスト実行"""
        print("🧪 機械学習統合テスト実行中...")

        test_result = {
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'details': {}
        }

        try:
            # 統合テスト実行
            test_script = self.src_path / 'ml_integration_test.py'

            if not test_script.exists():
                test_result['error'] = 'Integration test script not found'
                print("  ❌ 統合テストスクリプトが見つかりません")
                return test_result

            cmd = [str(self.venv_python), str(test_script)]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5分タイムアウト
                cwd=str(self.project_root)
            )

            if result.returncode == 0:
                test_result['success'] = True
                print("  ✅ 統合テスト成功")

                # 出力から重要な指標を抽出
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if '🎯 成功テスト:' in line:
                        test_result['details']['success_rate'] = line.split(':')[1].strip()
                    elif '⚡ 分類精度:' in line:
                        test_result['details']['classification_accuracy'] = line.split(':')[1].strip()
                    elif '📊 処理スループット:' in line:
                        test_result['details']['throughput'] = line.split(':')[1].strip()

            else:
                test_result['success'] = False
                test_result['error'] = result.stderr
                print(f"  ❌ 統合テスト失敗: {result.stderr}")

            test_result['stdout'] = result.stdout
            test_result['stderr'] = result.stderr

        except subprocess.TimeoutExpired:
            test_result['error'] = 'Test execution timeout'
            print("  ⏰ 統合テストがタイムアウトしました")

        except Exception as e:
            test_result['error'] = str(e)
            logger.error(f"統合テスト実行エラー: {e}")
            print(f"  ❌ 統合テスト実行エラー: {e}")

        return test_result

    def monitor_performance(self) -> dict:
        """パフォーマンス監視"""
        print("📊 パフォーマンス監視実行中...")

        performance_data = {
            'timestamp': datetime.now().isoformat(),
            'cpu_usage': psutil.cpu_percent(interval=1),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_io': psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {},
            'network_io': psutil.net_io_counters()._asdict()
        }

        print(f"  📈 CPU使用率: {performance_data['cpu_usage']:.1f}%")
        print(f"  💾 メモリ使用率: {performance_data['memory_usage']:.1f}%")

        # パフォーマンス警告
        warnings = []
        if performance_data['cpu_usage'] > 80:
            warnings.append("CPU使用率が高い")
        if performance_data['memory_usage'] > 85:
            warnings.append("メモリ使用率が高い")

        if warnings:
            performance_data['warnings'] = warnings
            print("  ⚠️ 警告: " + ", ".join(warnings))
        else:
            print("  ✅ パフォーマンス正常")

        self.metrics['performance'] = performance_data
        return performance_data

    def retrain_models(self) -> dict:
        """モデル再訓練実行"""
        print("🔄 機械学習モデル再訓練実行中...")

        retrain_result = {
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'details': {}
        }

        try:
            # モデル再訓練スクリプト実行
            train_script = self.src_path / 'ml_training_system_offline.py'

            if not train_script.exists():
                retrain_result['error'] = 'Training script not found'
                print("  ❌ 訓練スクリプトが見つかりません")
                return retrain_result

            cmd = [str(self.venv_python), str(train_script)]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10分タイムアウト
                cwd=str(self.project_root)
            )

            if result.returncode == 0:
                retrain_result['success'] = True
                print("  ✅ モデル再訓練成功")

                # 訓練結果から精度を抽出
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if 'accuracy' in line.lower() or '精度' in line:
                        retrain_result['details']['accuracy'] = line.strip()
                        break

            else:
                retrain_result['success'] = False
                retrain_result['error'] = result.stderr
                print(f"  ❌ モデル再訓練失敗: {result.stderr}")

            retrain_result['stdout'] = result.stdout
            retrain_result['stderr'] = result.stderr

        except subprocess.TimeoutExpired:
            retrain_result['error'] = 'Training timeout'
            print("  ⏰ モデル訓練がタイムアウトしました")

        except Exception as e:
            retrain_result['error'] = str(e)
            logger.error(f"モデル再訓練エラー: {e}")
            print(f"  ❌ モデル再訓練エラー: {e}")

        return retrain_result

    def cleanup_logs(self, days_to_keep: int = 30) -> dict:
        """ログファイルクリーンアップ"""
        print(f"🧹 {days_to_keep}日以前のログファイルをクリーンアップ中...")

        cleanup_result = {
            'timestamp': datetime.now().isoformat(),
            'files_deleted': 0,
            'bytes_freed': 0,
            'errors': []
        }

        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)

            log_files = list(self.logs_path.glob('*.log*'))

            for log_file in log_files:
                try:
                    file_modified = datetime.fromtimestamp(log_file.stat().st_mtime)

                    if file_modified < cutoff_date:
                        file_size = log_file.stat().st_size
                        log_file.unlink()

                        cleanup_result['files_deleted'] += 1
                        cleanup_result['bytes_freed'] += file_size

                        print(f"  🗑️ 削除: {log_file.name} ({file_size} bytes)")

                except Exception as e:
                    cleanup_result['errors'].append(f"{log_file.name}: {e}")
                    print(f"  ❌ 削除エラー: {log_file.name} - {e}")

            freed_mb = cleanup_result['bytes_freed'] / 1024 / 1024
            print(f"  ✅ クリーンアップ完了: {cleanup_result['files_deleted']}ファイル, {freed_mb:.1f}MB解放")

        except Exception as e:
            cleanup_result['errors'].append(str(e))
            logger.error(f"ログクリーンアップエラー: {e}")
            print(f"  ❌ ログクリーンアップエラー: {e}")

        return cleanup_result

    def generate_status_report(self) -> dict:
        """システム状況レポート生成"""
        print("📋 システム状況レポート生成中...")

        # 各種チェック実行
        health_status = self.check_system_health()
        integration_test = self.run_integration_test()
        performance_data = self.monitor_performance()

        # 総合レポート作成
        report = {
            'report_timestamp': datetime.now().isoformat(),
            'system_health': health_status,
            'integration_test': integration_test,
            'performance': performance_data,
            'overall_status': self._determine_overall_status(health_status, integration_test, performance_data),
            'recommendations': self._generate_recommendations(health_status, integration_test, performance_data)
        }

        # レポートファイル保存
        report_filename = f"system_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = self.logs_path / report_filename

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"  💾 レポート保存: {report_path}")

        return report

    def _determine_overall_status(self, health, test, performance) -> str:
        """総合状態判定"""
        if health.get('overall_status') == 'error':
            return 'critical'
        elif not test.get('success', False):
            return 'degraded'
        elif health.get('overall_status') == 'unhealthy':
            return 'warning'
        elif performance.get('warnings'):
            return 'warning'
        else:
            return 'healthy'

    def _generate_recommendations(self, health, test, performance) -> list:
        """改善推奨事項生成"""
        recommendations = []

        # システム健全性に基づく推奨
        if health.get('overall_status') == 'unhealthy':
            recommendations.append("システムコンポーネントに問題があります - 詳細確認が必要")

        # テスト結果に基づく推奨
        if not test.get('success', False):
            recommendations.append("統合テストが失敗しています - モデル再訓練を検討してください")

        # パフォーマンスに基づく推奨
        if performance.get('warnings'):
            recommendations.append("システムリソースの使用率が高いです - 最適化を検討してください")

        if not recommendations:
            recommendations.append("システムは正常に稼働しています")

        return recommendations

def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description='Uma3 Software ML System Operation Manager')
    parser.add_argument('--action', choices=[
        'health-check', 'test', 'monitor', 'retrain', 'cleanup', 'report', 'full-maintenance'
    ], default='report', help='実行するアクション')
    parser.add_argument('--cleanup-days', type=int, default=30, help='ログクリーンアップ保持日数')

    args = parser.parse_args()

    manager = Uma3OperationManager()

    print("🚀 Uma3 Software 機械学習システム運用管理ツール")
    print("=" * 60)

    try:
        if args.action == 'health-check':
            result = manager.check_system_health()
            print(f"\n📊 システム状態: {result['overall_status']}")

        elif args.action == 'test':
            result = manager.run_integration_test()
            print(f"\n🧪 統合テスト結果: {'成功' if result['success'] else '失敗'}")

        elif args.action == 'monitor':
            result = manager.monitor_performance()
            warnings = result.get('warnings', [])
            print(f"\n📈 パフォーマンス: {'警告あり' if warnings else '正常'}")

        elif args.action == 'retrain':
            result = manager.retrain_models()
            print(f"\n🔄 モデル再訓練: {'成功' if result['success'] else '失敗'}")

        elif args.action == 'cleanup':
            result = manager.cleanup_logs(args.cleanup_days)
            print(f"\n🧹 ログクリーンアップ: {result['files_deleted']}ファイル削除")

        elif args.action == 'report':
            result = manager.generate_status_report()
            print(f"\n📋 システム状況: {result['overall_status']}")
            print("推奨事項:")
            for rec in result['recommendations']:
                print(f"  • {rec}")

        elif args.action == 'full-maintenance':
            print("\n🔧 フルメンテナンス実行中...")

            # 1. システム健全性チェック
            health = manager.check_system_health()

            # 2. 統合テスト
            test = manager.run_integration_test()

            # 3. モデル再訓練（テスト失敗時）
            if not test.get('success', False):
                print("\n🔄 テスト失敗のためモデル再訓練を実行...")
                retrain = manager.retrain_models()

                if retrain['success']:
                    # 再訓練後に再テスト
                    print("\n🧪 再訓練後の統合テスト実行...")
                    test = manager.run_integration_test()

            # 4. ログクリーンアップ
            cleanup = manager.cleanup_logs(args.cleanup_days)

            # 5. 最終レポート生成
            report = manager.generate_status_report()

            print(f"\n🎉 フルメンテナンス完了 - システム状況: {report['overall_status']}")

        print("\n✅ 運用管理ツール実行完了")
        return 0

    except Exception as e:
        logger.error(f"運用管理ツールエラー: {e}")
        print(f"\n❌ エラー: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
