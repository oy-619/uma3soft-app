"""
【簡単な監視機能テスト】
"""

import os
import sys

# パス設定
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), 'src')
sys.path.insert(0, src_dir)

def quick_test():
    print("🔍 監視機能クイックテスト")

    # 1. インポートテスト
    try:
        from monitoring_historyfile import MonitoringConfig
        print("✅ MonitoringConfig インポート成功")

        config = MonitoringConfig()
        print(f"✅ 設定作成成功")
        print(f"  監視ディレクトリ: {config.watch_directory}")
        print(f"  存在確認: {os.path.exists(config.watch_directory)}")

    except Exception as e:
        print(f"❌ インポートエラー: {e}")
        return

    # 2. RAGエンジンテスト
    try:
        from monitoring_historyfile import ConversationFileHandler

        handler = ConversationFileHandler(config)
        print(f"✅ ConversationFileHandler作成成功")
        print(f"  RAGエンジン: {handler.rag_engine is not None}")

        if handler.rag_engine:
            print(f"  RAGエンジンタイプ: {type(handler.rag_engine).__name__}")

    except Exception as e:
        print(f"❌ ハンドラー作成エラー: {e}")
        import traceback
        traceback.print_exc()
        return

    # 3. ファイル監視テスト
    try:
        # テストファイル作成
        test_file = os.path.join(config.watch_directory, "monitoring_test.log")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("テスト監視ファイル\n2025-10-29 09:00:00 - テストメッセージ")

        print(f"✅ テストファイル作成: {test_file}")

        # ファイル処理テスト
        handler._process_conversation_file(test_file)
        print("✅ ファイル処理完了")

        # テストファイル削除
        os.remove(test_file)
        print("✅ テストファイル削除完了")

    except Exception as e:
        print(f"❌ ファイル処理エラー: {e}")
        import traceback
        traceback.print_exc()

    print("🎯 クイックテスト完了")

if __name__ == "__main__":
    quick_test()
