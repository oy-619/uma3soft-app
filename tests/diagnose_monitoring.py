"""
【監視機能診断スクリプト】
"""

import os
import sys
import traceback

# パス設定
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), 'src')
sys.path.insert(0, src_dir)

def diagnose_monitoring():
    print("🔍 監視機能診断開始")

    # 1. 基本インポートテスト
    print("\n1. 基本インポートテスト")
    try:
        import monitoring_historyfile
        print("✅ monitoring_historyfile インポート成功")
    except Exception as e:
        print(f"❌ monitoring_historyfile インポートエラー: {e}")
        traceback.print_exc()
        return

    # 2. 設定クラステスト
    print("\n2. 設定クラステスト")
    try:
        from monitoring_historyfile import MonitoringConfig
        config = MonitoringConfig()
        print("✅ MonitoringConfig作成成功")
        print(f"  監視ディレクトリ: {config.watch_directory}")
        print(f"  ChromaDBディレクトリ: {config.chroma_directory}")
    except Exception as e:
        print(f"❌ MonitoringConfig作成エラー: {e}")
        traceback.print_exc()
        return

    # 3. ハンドラー作成テスト（段階的）
    print("\n3. ハンドラー作成テスト")
    try:
        from monitoring_historyfile import ConversationFileHandler
        print("✅ ConversationFileHandler インポート成功")

        print("  ハンドラー初期化中...")
        handler = ConversationFileHandler(config)
        print("✅ ConversationFileHandler作成成功")

        print(f"  RAGエンジン存在: {handler.rag_engine is not None}")
        if handler.rag_engine:
            print(f"  RAGエンジンタイプ: {type(handler.rag_engine).__name__}")

    except Exception as e:
        print(f"❌ ConversationFileHandler作成エラー: {e}")
        traceback.print_exc()
        return

    # 4. 監視クラステスト
    print("\n4. 監視クラステスト")
    try:
        from monitoring_historyfile import ConversationMonitor
        monitor = ConversationMonitor(config)
        print("✅ ConversationMonitor作成成功")

    except Exception as e:
        print(f"❌ ConversationMonitor作成エラー: {e}")
        traceback.print_exc()
        return

    print("\n✅ 全ての診断テストが成功しました！")
    print("🎯 監視機能は正常に動作する状態です")

if __name__ == "__main__":
    diagnose_monitoring()
