#!/usr/bin/env python3
"""
ChromaDB初期化テスト - '_type' KeyErrorの修正確認
"""

import sys
import os

# パスを設定
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

def test_chromadb_initialization():
    """ChromaDBの初期化テスト"""
    print("🔍 ChromaDB初期化テスト")
    print("=" * 50)

    try:
        from src.chathistory2db import check_chromadb_integrity, PERSIST_DIRECTORY

        print(f"📁 テスト対象ディレクトリ: {PERSIST_DIRECTORY}")

        # 整合性チェック
        integrity_ok = check_chromadb_integrity(PERSIST_DIRECTORY)
        print(f"🔍 整合性チェック結果: {'✅ OK' if integrity_ok else '⚠️ 問題あり'}")

        # ChromaDBの基本初期化テスト
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_chroma import Chroma

        print("🔧 埋め込みモデル初期化中...")
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        print("🔧 ChromaDB初期化中...")
        vector_db = Chroma(
            persist_directory=PERSIST_DIRECTORY,
            embedding_function=embedding_model,
        )

        print("✅ ChromaDB初期化成功!")

        # 基本操作テスト
        print("🔧 基本操作テスト中...")
        test_docs = ["テストメッセージ1", "テストメッセージ2"]
        test_metadatas = [{"user": "テスト", "timestamp": "2025-01-01"}, {"user": "テスト", "timestamp": "2025-01-02"}]

        result = vector_db.add_texts(test_docs, metadatas=test_metadatas)
        print(f"✅ テストデータ追加成功: {len(result) if result else 0}件")

        return True

    except Exception as e:
        print(f"❌ エラー: {e}")
        print(f"❌ エラータイプ: {type(e).__name__}")

        if "_type" in str(e):
            print("⚠️ '_type' KeyError が検出されました")
            print("🔧 リカバリ処理が必要です")

        return False

def test_chathistory_function():
    """チャット履歴読み込み関数のテスト"""
    print("\n🔍 チャット履歴読み込み関数テスト")
    print("=" * 50)

    try:
        from src.chathistory2db import load_chathistory_to_chromadb

        # テスト用の空のチャット履歴ファイルを作成
        test_chat_file = os.path.join(os.path.dirname(__file__), "test_chat.txt")
        with open(test_chat_file, "w", encoding="utf-8") as f:
            f.write("2025/01/01(水)\n")
            f.write("12:00 テストユーザー\n")
            f.write("テストメッセージです\n")

        print(f"📁 テストファイル作成: {test_chat_file}")

        print("🔧 チャット履歴読み込み実行中...")
        result = load_chathistory_to_chromadb(
            chathistory_path=test_chat_file,
            verbose=True
        )

        print(f"✅ チャット履歴読み込み結果: {'成功' if result else '失敗'}")

        # テストファイル削除
        if os.path.exists(test_chat_file):
            os.remove(test_chat_file)

        return result

    except Exception as e:
        print(f"❌ エラー: {e}")
        print(f"❌ エラータイプ: {type(e).__name__}")
        return False

def main():
    """メインテスト実行"""
    print("=" * 60)
    print("🔧 ChromaDB '_type' KeyError 修正テスト")
    print("=" * 60)

    tests = [
        test_chromadb_initialization,
        test_chathistory_function
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
        print("✅ '_type' KeyError問題が修正されました")
    else:
        print(f"⚠️  一部テスト失敗 ({passed}/{total})")
        print("❌ さらなる修正が必要です")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
