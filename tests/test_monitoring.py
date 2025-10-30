"""
【監視機能テストスクリプト】
トーク履歴ファイル監視機能の動作確認用
"""

import os
import sys
import time
import json
from datetime import datetime

# パスを追加
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), 'src')
sys.path.insert(0, src_dir)

def test_monitoring_setup():
    """監視機能のセットアップテスト"""
    print("🧪 監視機能セットアップテスト開始")

    try:
        from monitoring_historyfile import MonitoringConfig, ConversationMonitor

        # 設定テスト
        config = MonitoringConfig()
        print(f"✅ 設定作成成功")
        print(f"  監視ディレクトリ: {config.watch_directory}")
        print(f"  ChromaDBディレクトリ: {config.chroma_directory}")
        print(f"  ポーリング間隔: {config.polling_interval}秒")
        print(f"  監視パターン: {config.monitor_patterns}")

        # ディレクトリ確認
        if os.path.exists(config.watch_directory):
            print(f"✅ 監視ディレクトリ存在確認: {config.watch_directory}")

            # ディレクトリ内容確認
            files = os.listdir(config.watch_directory)
            print(f"  ディレクトリ内ファイル数: {len(files)}")

            # 関連ファイルの検索
            relevant_files = []
            for file in files:
                for pattern in config.monitor_patterns:
                    if pattern.replace("*", "") in file:
                        relevant_files.append(file)
                        break

            print(f"  監視対象ファイル数: {len(relevant_files)}")
            for file in relevant_files[:5]:  # 最大5件表示
                print(f"    - {file}")

        else:
            print(f"⚠️ 監視ディレクトリが存在しません: {config.watch_directory}")
            os.makedirs(config.watch_directory, exist_ok=True)
            print(f"✅ 監視ディレクトリを作成しました")

        return config

    except Exception as e:
        print(f"❌ セットアップテストエラー: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_file_processing():
    """ファイル処理機能テスト"""
    print("\n📁 ファイル処理機能テスト")

    try:
        from monitoring_historyfile import ConversationFileHandler, MonitoringConfig

        config = MonitoringConfig()
        handler = ConversationFileHandler(config)

        # テストファイル作成
        test_file_path = os.path.join(config.watch_directory, "test_conversation.log")
        test_content = """
[2025-10-29 10:00:00] User: こんにちは
[2025-10-29 10:00:05] Bot: こんにちは！馬三ソフトのサポートです。
[2025-10-29 10:00:10] User: 明日の天気を教えて
[2025-10-29 10:00:15] Bot: 明日の東京の天気は晴れ時々曇りです。
        """

        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)

        print(f"✅ テストファイル作成: {test_file_path}")

        # ファイル処理テスト
        handler._process_conversation_file(test_file_path)
        print("✅ ファイル処理テスト完了")

        # テストファイル削除
        os.remove(test_file_path)
        print("✅ テストファイル削除完了")

    except Exception as e:
        print(f"❌ ファイル処理テストエラー: {e}")
        import traceback
        traceback.print_exc()


def test_rag_integration():
    """RAG統合テスト"""
    print("\n🧠 RAG統合テスト")

    try:
        from monitoring_historyfile import ConversationFileHandler, MonitoringConfig

        config = MonitoringConfig()
        handler = ConversationFileHandler(config)

        if handler.rag_engine:
            print("✅ RAGエンジン利用可能")
            print(f"  エンジンタイプ: {type(handler.rag_engine).__name__}")

            # RAGエンジンのメソッド確認
            available_methods = []
            for method in ['add_documents', 'add_texts', 'search_similar', 'smart_similarity_search']:
                if hasattr(handler.rag_engine, method):
                    available_methods.append(method)

            print(f"  利用可能メソッド: {available_methods}")

        else:
            print("⚠️ RAGエンジンが利用できません")

    except Exception as e:
        print(f"❌ RAG統合テストエラー: {e}")
        import traceback
        traceback.print_exc()


def test_real_monitoring():
    """実際の監視機能テスト（短時間）"""
    print("\n⏰ 実際の監視機能テスト（10秒間）")

    try:
        from monitoring_historyfile import ConversationMonitor, MonitoringConfig

        config = MonitoringConfig()
        config.polling_interval = 2  # 2秒間隔

        monitor = ConversationMonitor(config)

        print("✅ 監視開始...")

        # バックグラウンドで監視開始（簡略版）
        import threading

        def monitoring_thread():
            try:
                monitor._start_polling_monitoring_test()
            except Exception as e:
                print(f"監視スレッドエラー: {e}")

        # 監視機能を少し修正してテスト用に作成
        def _start_polling_monitoring_test():
            """テスト用ポーリング監視"""
            print("[MONITOR] テスト用ポーリング監視開始")
            processed_files = set()

            for i in range(5):  # 5回だけ実行
                try:
                    from pathlib import Path
                    watch_path = Path(config.watch_directory)
                    if watch_path.exists():
                        for file_path in watch_path.rglob("*"):
                            if file_path.is_file():
                                file_str = str(file_path)
                                if (file_str not in processed_files and
                                    monitor._should_process_file(file_str)):
                                    print(f"[MONITOR] 検出: {file_str}")
                                    processed_files.add(file_str)

                    time.sleep(2)

                except Exception as e:
                    print(f"[ERROR] ポーリングエラー: {e}")
                    break

        # テスト実行
        monitor._start_polling_monitoring_test = _start_polling_monitoring_test

        thread = threading.Thread(target=monitoring_thread)
        thread.daemon = True
        thread.start()

        # テストファイル作成（監視中）
        time.sleep(1)
        test_file = os.path.join(config.watch_directory, f"test_realtime_{int(time.time())}.log")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(f"テスト監視ファイル - {datetime.now()}")

        print(f"✅ テストファイル作成: {os.path.basename(test_file)}")

        # 監視結果待機
        thread.join(timeout=12)

        # テストファイル削除
        if os.path.exists(test_file):
            os.remove(test_file)

        print("✅ 実際の監視テスト完了")

    except Exception as e:
        print(f"❌ 実際の監視テストエラー: {e}")
        import traceback
        traceback.print_exc()


def main():
    """メイン実行関数"""
    print("=" * 60)
    print("🔍 トーク履歴ファイル監視機能テストスクリプト")
    print("=" * 60)

    # 1. セットアップテスト
    config = test_monitoring_setup()

    if config:
        # 2. ファイル処理テスト
        test_file_processing()

        # 3. RAG統合テスト
        test_rag_integration()

        # 4. 実際の監視テスト
        test_real_monitoring()

    print("\n" + "=" * 60)
    print("🎯 監視機能テスト完了")
    print("=" * 60)


if __name__ == "__main__":
    main()
