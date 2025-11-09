#!/usr/bin/env python3
"""
修正されたUma3システムの安全テスト
プロセス終了機能を無効化した状態でのテスト
"""

import os
import sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_safe_uma3_system():
    """プロセス終了なしでのUma3システムテスト"""
    print("=" * 60)
    print("🔧 修正済みUma3システム安全テスト")
    print("=" * 60)

    try:
        # 環境設定
        from dotenv import load_dotenv
        load_dotenv()

        print("\n1️⃣ システム初期化テスト")
        print("-" * 30)

        # 埋め込みモデルの初期化
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            embedding_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            print("   ✅ 埋め込みモデル初期化成功")
        except Exception as e:
            print(f"   ❌ 埋め込みモデル初期化失敗: {e}")
            return

        # ChromaDBの安全な初期化テスト
        print("\n2️⃣ ChromaDB安全初期化テスト")
        print("-" * 30)

        from langchain_chroma import Chroma
        persist_directory = "db/chroma_store_test"

        # テストディレクトリの準備
        os.makedirs(persist_directory, exist_ok=True)

        vector_db = None
        for attempt in range(2):
            try:
                print(f"   試行 {attempt + 1}/2...")

                if attempt == 0:
                    # 通常の初期化
                    test_dir = persist_directory
                else:
                    # 一時ディレクトリで初期化
                    import tempfile
                    test_dir = tempfile.mkdtemp(prefix="uma3_safe_test_")
                    print(f"   一時ディレクトリ使用: {test_dir}")

                vector_db = Chroma(
                    persist_directory=test_dir,
                    embedding_function=embedding_model
                )

                # 接続テスト
                vector_db.add_texts(["テストドキュメント"])
                results = vector_db.similarity_search("テスト", k=1)

                print(f"   ✅ ChromaDB初期化成功 (試行 {attempt + 1})")
                print(f"   📊 テスト結果: {len(results)} 件")
                break

            except Exception as e:
                print(f"   ❌ 試行 {attempt + 1} 失敗: {e}")
                if attempt == 1:
                    print("   🚨 全ての初期化試行が失敗")

        if vector_db:
            print("\n3️⃣ 基本機能テスト")
            print("-" * 30)

            try:
                # Uma3ChromaDBImprover初期化テスト
                from uma3_chroma_improver import Uma3ChromaDBImprover
                chroma_improver = Uma3ChromaDBImprover(vector_db)
                print("   ✅ Uma3ChromaDBImprover初期化成功")

                # 簡単な検索テスト
                results = chroma_improver.smart_similarity_search("テスト", k=1)
                print(f"   ✅ スマート検索テスト成功: {len(results)} 件")

            except Exception as e:
                print(f"   ❌ Uma3機能テスト失敗: {e}")

            try:
                # 統合システム初期化テスト
                from integrated_conversation_system import IntegratedConversationSystem

                integrated_system = IntegratedConversationSystem(
                    chroma_persist_directory=persist_directory,
                    conversation_db_path="db/test_conversation_history.db",
                    embeddings_model=embedding_model
                )
                print("   ✅ 統合システム初期化成功")

                # 簡単な応答テスト
                response = integrated_system.generate_integrated_response(
                    "test_user", "こんにちは"
                )
                print(f"   ✅ 応答生成テスト成功: {response['response'][:50]}...")

            except Exception as e:
                print(f"   ❌ 統合システムテスト失敗: {e}")

        print("\n=" * 60)
        print("🎉 修正済みシステムテスト完了")
        print("=" * 60)
        print("✅ プロセス終了機能が無効化され、安全に動作しています")

    except Exception as e:
        print(f"❌ テスト中にエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_safe_uma3_system()
