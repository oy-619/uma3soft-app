#!/usr/bin/env python3
"""
軽量なファイルロック対応テスト - 高速版
"""

import sys
import os
import time

# パスを設定
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

def test_file_access_simple():
    """シンプルなファイルアクセステスト"""
    print("🔍 シンプルなファイルアクセステスト")
    print("=" * 50)

    try:
        from src.chathistory2db import PERSIST_DIRECTORY
        chroma_file = os.path.join(PERSIST_DIRECTORY, "chroma.sqlite3")

        print(f"📁 テスト対象ファイル: {chroma_file}")
        print(f"📂 ファイル存在: {'✅' if os.path.exists(chroma_file) else '❌'}")

        if os.path.exists(chroma_file):
            # ファイルアクセステスト
            try:
                with open(chroma_file, 'r+b') as f:
                    print("✅ ファイルアクセス: 成功（ロックなし）")
                return True
            except (IOError, PermissionError) as e:
                print(f"⚠️ ファイルアクセス: 失敗（ロック中） - {e}")
                return False
        else:
            print("ℹ️ ChromaDBファイルが存在しないため、アクセステストをスキップ")
            return True

    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

def test_chromadb_initialization_with_recovery():
    """ChromaDB初期化とリカバリ機能のテスト"""
    print("\n🔍 ChromaDB初期化・リカバリテスト")
    print("=" * 50)

    try:
        from src.chathistory2db import load_chathistory_to_chromadb

        # テスト用の小さなチャット履歴ファイルを作成
        test_chat_file = os.path.join(os.path.dirname(__file__), "test_simple_chat.txt")
        with open(test_chat_file, "w", encoding="utf-8") as f:
            f.write("2025/01/01(水)\n")
            f.write("12:00 テストユーザー\n")
            f.write("シンプルテスト\n")

        print(f"📁 テストファイル作成: {test_chat_file}")

        print("🔧 ChromaDB初期化テスト実行中...")

        result = load_chathistory_to_chromadb(
            chathistory_path=test_chat_file,
            verbose=False  # 詳細ログは無効
        )

        print(f"✅ 初期化結果: {'成功' if result else '失敗'}")

        # テストファイル削除
        if os.path.exists(test_chat_file):
            os.remove(test_chat_file)

        return result

    except Exception as e:
        print(f"❌ エラー: {e}")
        if "KeyError: '_type'" in str(e):
            print("⚠️ '_type' KeyError が発生しました - リカバリ機能をテスト中")
        if "PermissionError" in str(e) or "WinError 32" in str(e):
            print("⚠️ ファイルロックエラーが発生しました - リカバリ機能が動作中")
        return False

def test_process_detection():
    """プロセス検出機能のテスト"""
    print("\n🔍 プロセス検出機能テスト")
    print("=" * 50)

    try:
        from src.chathistory2db import get_chromadb_process_locks, PERSIST_DIRECTORY

        print("🔧 プロセス検出実行中...")
        processes = get_chromadb_process_locks(PERSIST_DIRECTORY)

        print(f"📊 検出されたプロセス数: {len(processes)}")

        for i, proc in enumerate(processes[:3]):  # 最初の3つのプロセスのみ表示
            print(f"   {i+1}. PID: {proc['pid']}, 名前: {proc['name']}")

        if len(processes) > 3:
            print(f"   ... その他 {len(processes) - 3} プロセス")

        return True

    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

def main():
    """メインテスト実行"""
    print("=" * 60)
    print("🔧 軽量なファイルロック対応テスト")
    print("高速版 - プロセス競合・アクセス権限問題の修正確認")
    print("=" * 60)

    tests = [
        test_file_access_simple,
        test_process_detection,
        test_chromadb_initialization_with_recovery
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 60)
    print("📊 テスト結果サマリー")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"🎉 全テスト成功! ({passed}/{total})")
        print("✅ ファイルロック対応が正常に動作しています")
    else:
        print(f"⚠️  一部テスト失敗 ({passed}/{total})")
        print("❌ さらなる修正が必要です")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
