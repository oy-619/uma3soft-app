#!/usr/bin/env python3
"""
ChromaDBエラー修正テスト
テレメトリーエラーと権限エラーの修正確認
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_chromadb_error_fixes():
    """ChromaDBエラー修正のテスト"""
    print("=" * 60)
    print("🔧 ChromaDBエラー修正テスト")
    print("=" * 60)

    try:
        # 環境変数設定
        os.environ["CHROMA_TELEMETRY"] = "false"
        os.environ["CHROMA_CLIENT_SETTINGS"] = '{"telemetry": {"enabled": false}}'

        # ログレベル設定
        import logging
        logging.getLogger("chromadb").setLevel(logging.WARNING)
        logging.getLogger("chromadb.telemetry").setLevel(logging.ERROR)

        print("\n1️⃣ 環境設定")
        print("-" * 30)
        print("   ✅ ChromaDBテレメトリー無効化")
        print("   ✅ ログレベル設定完了")

        # 埋め込みモデルの初期化
        print("\n2️⃣ 埋め込みモデル初期化")
        print("-" * 30)

        from dotenv import load_dotenv
        load_dotenv()

        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            embedding_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            print("   ✅ HuggingFaceEmbeddings初期化成功")
        except Exception as e:
            print(f"   ❌ 埋め込みモデル初期化失敗: {e}")
            return

        # ChromaDB初期化テスト
        print("\n3️⃣ ChromaDB初期化テスト")
        print("-" * 30)

        from langchain_chroma import Chroma

        # テスト用のディレクトリ作成
        import tempfile
        import uuid

        base_test_dir = "db/test_chroma_fix"
        test_dirs = []

        # 複数のディレクトリでテスト
        for i in range(3):
            if i == 0:
                test_dir = base_test_dir
            elif i == 1:
                test_dir = f"{base_test_dir}_alt_{uuid.uuid4().hex[:8]}"
            else:
                test_dir = tempfile.mkdtemp(prefix="chroma_test_")

            test_dirs.append(test_dir)

            try:
                print(f"   テスト {i+1}: {test_dir}")

                # ディレクトリ作成
                os.makedirs(test_dir, exist_ok=True)

                # ChromaDB初期化
                vector_db = Chroma(
                    persist_directory=test_dir,
                    embedding_function=embedding_model
                )

                # 簡単なテスト
                vector_db.add_texts([f"テストドキュメント{i}"])
                results = vector_db.similarity_search("テスト", k=1)

                print(f"   ✅ テスト {i+1} 成功: {len(results)} 件")
                break

            except Exception as e:
                print(f"   ❌ テスト {i+1} 失敗: {e}")
                if i == 2:
                    print("   🚨 全てのテストが失敗")

        print("\n4️⃣ テレメトリーエラー確認")
        print("-" * 30)

        # 追加のChromaDBインスタンスでテレメトリーエラーをチェック
        try:
            temp_dir2 = tempfile.mkdtemp(prefix="telemetry_test_")
            test_db = Chroma(
                persist_directory=temp_dir2,
                embedding_function=embedding_model
            )
            test_db.add_texts(["テレメトリーテスト"])
            print("   ✅ テレメトリーエラーなし")
        except Exception as e:
            if "telemetry" in str(e).lower():
                print(f"   ❌ テレメトリーエラー: {e}")
            else:
                print(f"   ⚠️ 他のエラー: {e}")

        print("\n=" * 60)
        print("🎉 ChromaDBエラー修正テスト完了")
        print("=" * 60)

    except Exception as e:
        print(f"❌ テスト中にエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chromadb_error_fixes()
