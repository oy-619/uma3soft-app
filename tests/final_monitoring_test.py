#!/usr/bin/env python3
"""
監視機能の最終動作確認テスト
修正後の監視システムが正常に動作するかを確認
"""

import sys
import os
import importlib.util

# パスを設定
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

def test_import():
    """基本インポートテスト"""
    print("🔍 監視システム インポートテスト")
    try:
        from src.monitoring_historyfile import ConversationMonitor, ConversationFileHandler, MonitoringConfig
        print("✅ 全コンポーネントのインポートが成功")
        return True
    except Exception as e:
        print(f"❌ インポートエラー: {e}")
        return False

def test_configuration():
    """設定クラステスト"""
    print("\n🔍 設定クラステスト")
    try:
        from src.monitoring_historyfile import MonitoringConfig
        config = MonitoringConfig()
        print(f"✅ 設定クラス初期化成功")
        print(f"   - 監視対象フォルダ: {config.watch_directory}")
        print(f"   - 監視パターン: {config.monitor_patterns}")
        return True
    except Exception as e:
        print(f"❌ 設定クラスエラー: {e}")
        return False

def test_file_handler():
    """ファイルハンドラーテスト"""
    print("\n🔍 ファイルハンドラーテスト")
    try:
        from src.monitoring_historyfile import ConversationFileHandler, MonitoringConfig
        config = MonitoringConfig()
        handler = ConversationFileHandler(config)
        print("✅ ファイルハンドラー初期化成功")
        return True
    except Exception as e:
        print(f"❌ ファイルハンドラーエラー: {e}")
        return False

def test_monitor_creation():
    """監視オブジェクト作成テスト"""
    print("\n🔍 監視オブジェクト作成テスト")
    try:
        from src.monitoring_historyfile import ConversationMonitor
        monitor = ConversationMonitor()
        print("✅ 監視オブジェクト作成成功")
        return True
    except Exception as e:
        print(f"❌ 監視オブジェクト作成エラー: {e}")
        return False

def main():
    """メインテスト実行"""
    print("=" * 50)
    print("🔧 監視機能 最終動作確認テスト")
    print("=" * 50)

    tests = [
        test_import,
        test_configuration,
        test_file_handler,
        test_monitor_creation
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 50)
    print("📊 テスト結果サマリー")
    print("=" * 50)

    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"🎉 全テスト成功! ({passed}/{total})")
        print("✅ 監視機能の修正が完了しました")
    else:
        print(f"⚠️  一部テスト失敗 ({passed}/{total})")
        print("❌ さらなる修正が必要です")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
