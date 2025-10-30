#!/usr/bin/env python3
"""
ChromaDB 再初期化スクリプト
破損したChromaDBを修復・再初期化
"""

import os
import shutil
import sys
from datetime import datetime

# プロジェクトルートの絶対パス取得
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
DEFAULT_CHROMA_PERSIST_DIRECTORY = os.path.join(PROJECT_ROOT, 'db', 'chroma_store')

def reset_chromadb():
    """ChromaDBの完全リセット"""
    print("=" * 60)
    print("🔧 ChromaDB 再初期化スクリプト")
    print("=" * 60)

    chroma_paths = [
        DEFAULT_CHROMA_PERSIST_DIRECTORY,
        "chroma_store",
        "test_integration_chroma"
    ]

    for chroma_path in chroma_paths:
        if os.path.exists(chroma_path):
            print(f"🗑️ 既存のChromaDBを削除: {chroma_path}")
            try:
                shutil.rmtree(chroma_path)
                print(f"✅ 削除完了: {chroma_path}")
            except Exception as e:
                print(f"⚠️ 削除中にエラー: {chroma_path} - {e}")
        else:
            print(f"📂 存在しないディレクトリ: {chroma_path}")

    # 新しいChromaDBを初期化
    print("\n🚀 新しいChromaDBを初期化...")

    try:
        # 必要なモジュールをインポート
        from langchain_chroma import Chroma
        from langchain_huggingface import HuggingFaceEmbeddings

        # 埋め込みモデルを初期化
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        print("✅ 埋め込みモデル初期化完了")

        # 新しいChromaDBを作成
        vector_db = Chroma(
            persist_directory=DEFAULT_CHROMA_PERSIST_DIRECTORY,
            embedding_function=embedding_model
        )
        print("✅ 新しいChromaDB作成完了")

        # テストデータを追加
        test_documents = [
            "これはテスト用の文書です。",
            "システムの動作確認を行っています。",
            "ChromaDBが正常に動作することを確認します。",
            "馬三ソフトは素晴らしいチームです。",
            "練習は毎週火曜日と木曜日に行います。"
        ]

        test_metadata = [
            {"source": "test", "type": "system_check", "timestamp": datetime.now().isoformat()},
            {"source": "test", "type": "operation_check", "timestamp": datetime.now().isoformat()},
            {"source": "test", "type": "database_check", "timestamp": datetime.now().isoformat()},
            {"source": "test", "type": "team_info", "timestamp": datetime.now().isoformat()},
            {"source": "test", "type": "schedule_info", "timestamp": datetime.now().isoformat()}
        ]

        # テストデータを追加
        vector_db.add_texts(test_documents, metadatas=test_metadata)
        print(f"✅ テストデータ追加完了: {len(test_documents)}件")

        # 検索テスト
        results = vector_db.similarity_search("テスト", k=3)
        print(f"✅ 検索テスト成功: {len(results)}件の結果")

        for i, doc in enumerate(results, 1):
            print(f"   {i}. {doc.page_content[:50]}...")

        print("\n" + "=" * 60)
        print("🎉 ChromaDB 再初期化完了!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"❌ ChromaDB初期化中にエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chromadb_operations():
    """ChromaDBの基本操作テスト"""
    print("\n🧪 ChromaDB 基本操作テスト")
    print("-" * 40)

    try:
        from langchain_chroma import Chroma
        from langchain_huggingface import HuggingFaceEmbeddings

        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        vector_db = Chroma(
            persist_directory=DEFAULT_CHROMA_PERSIST_DIRECTORY,
            embedding_function=embedding_model
        )

        # 検索テスト
        search_queries = [
            "馬三ソフト",
            "練習",
            "チーム",
            "スケジュール"
        ]

        for query in search_queries:
            results = vector_db.similarity_search(query, k=2)
            print(f"'{query}' -> {len(results)}件の結果")

        print("✅ 全ての基本操作テストが成功しました")
        return True

    except Exception as e:
        print(f"❌ 基本操作テスト失敗: {e}")
        return False

if __name__ == "__main__":
    print(f"現在のディレクトリ: {os.getcwd()}")

    if reset_chromadb():
        if test_chromadb_operations():
            print("\n✨ ChromaDB再初期化と動作確認が正常に完了しました！")
        else:
            print("\n⚠️ 再初期化は成功しましたが、動作テストで問題がありました")
    else:
        print("\n❌ ChromaDB再初期化に失敗しました")
        sys.exit(1)
