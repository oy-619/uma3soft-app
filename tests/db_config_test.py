#!/usr/bin/env python3
"""
DB設定確認テスト - 指定されたディレクトリ設定の確認
"""

import sys
import os

# パスを設定
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

def test_db_paths():
    """DB設定パスの確認"""
    print("🔍 DB設定パス確認テスト")
    print("=" * 50)

    try:
        from src.monitoring_historyfile import MonitoringConfig
        config = MonitoringConfig()

        print(f"📁 監視設定:")
        print(f"   - 監視対象フォルダ: {config.watch_directory}")
        print(f"   - ChromaDBディレクトリ: {config.chroma_directory}")
        print(f"   - 会話DBファイル: {config.conversation_db}")

        # パスの絶対パス確認
        print(f"\n🔗 絶対パス:")
        print(f"   - ChromaDB絶対パス: {os.path.abspath(config.chroma_directory)}")
        print(f"   - 会話DB絶対パス: {os.path.abspath(config.conversation_db)}")

        # ディレクトリ存在確認
        print(f"\n📂 ディレクトリ存在確認:")
        db_base_dir = os.path.dirname(config.chroma_directory)
        print(f"   - DB基盤ディレクトリ ({db_base_dir}): {'✅存在' if os.path.exists(db_base_dir) else '❌不存在'}")
        print(f"   - ChromaDBディレクトリ ({config.chroma_directory}): {'✅存在' if os.path.exists(config.chroma_directory) else '❌不存在'}")

        return True
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

def test_rag_engine_paths():
    """RAGエンジンの設定パス確認"""
    print("\n🔍 RAGエンジン設定パス確認テスト")
    print("=" * 50)

    try:
        from src.uma3_rag_engine import Uma3RAGEngine

        # デフォルト設定でRAGエンジンを作成
        rag_engine = Uma3RAGEngine()

        print(f"📁 RAGエンジン設定:")
        print(f"   - persist_directory: {rag_engine.persist_directory}")
        print(f"   - 絶対パス: {os.path.abspath(rag_engine.persist_directory)}")

        return True
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

def test_chathistory_db_paths():
    """チャット履歴DB設定の確認"""
    print("\n🔍 チャット履歴DB設定確認テスト")
    print("=" * 50)

    try:
        from src.chathistory2db import PERSIST_DIRECTORY, DB_DIR

        print(f"📁 チャット履歴DB設定:")
        print(f"   - DB_DIR: {DB_DIR}")
        print(f"   - PERSIST_DIRECTORY: {PERSIST_DIRECTORY}")
        print(f"   - 絶対パスDB_DIR: {os.path.abspath(DB_DIR)}")
        print(f"   - 絶対パスPERSIST: {os.path.abspath(PERSIST_DIRECTORY)}")

        # ディレクトリ存在確認
        print(f"\n📂 ディレクトリ存在確認:")
        print(f"   - DB_DIR ({DB_DIR}): {'✅存在' if os.path.exists(DB_DIR) else '❌不存在'}")
        print(f"   - PERSIST_DIRECTORY ({PERSIST_DIRECTORY}): {'✅存在' if os.path.exists(PERSIST_DIRECTORY) else '❌不存在'}")

        return True
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

def main():
    """メインテスト実行"""
    print("=" * 60)
    print("🔧 DB設定確認テスト")
    print("指定ディレクトリ: C:\\work\\ws_python\\GenerationAiCamp\\Lesson25\\uma3soft-app\\db\\chroma_store")
    print("=" * 60)

    tests = [
        test_db_paths,
        test_rag_engine_paths,
        test_chathistory_db_paths
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 60)
    print("📊 DB設定確認結果サマリー")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"🎉 全設定確認成功! ({passed}/{total})")
        print("✅ 指定されたDBディレクトリ設定が完了しました")
    else:
        print(f"⚠️  一部設定に問題あり ({passed}/{total})")
        print("❌ 設定の再確認が必要です")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
