#!/usr/bin/env python3
"""
ChromaDB PermissionError 修正テスト
プロセス競合とファイルロックの問題を解決
"""

import os
import sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def cleanup_existing_processes():
    """既存のChromaDBプロセスをクリーンアップ"""
    print("=" * 60)
    print("🔧 ChromaDB プロセスクリーンアップ")
    print("=" * 60)

    try:
        import psutil
        current_pid = os.getpid()
        terminated_count = 0

        print(f"   Current PID: {current_pid}")

        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'open_files']):
            try:
                # uma3.pyを実行している他のプロセスを検索
                if (proc.info['name'] == 'python.exe' and
                    proc.info['pid'] != current_pid and
                    proc.info['cmdline']):

                    cmdline_str = ' '.join(proc.info['cmdline'])
                    if 'uma3.py' in cmdline_str:
                        print(f"   Found uma3.py process: PID {proc.info['pid']}")
                        proc.terminate()
                        terminated_count += 1
                        print(f"   ✅ Terminated PID {proc.info['pid']}")

                # ChromaDBファイルを開いているプロセスを検索
                if proc.info['open_files']:
                    for file_info in proc.info['open_files']:
                        if 'chroma' in file_info.path.lower():
                            print(f"   Found ChromaDB file user: PID {proc.info['pid']}")
                            proc.terminate()
                            terminated_count += 1
                            print(f"   ✅ Terminated PID {proc.info['pid']}")
                            break

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if terminated_count > 0:
            print(f"   💀 Terminated {terminated_count} processes")
            print("   ⏳ Waiting for cleanup...")
            time.sleep(3)
        else:
            print("   ✅ No conflicting processes found")

    except ImportError:
        print("   ⚠️ psutil not available, using Windows taskkill")
        import subprocess
        try:
            result = subprocess.run(
                ['taskkill', '/F', '/IM', 'python.exe'],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                print("   ✅ Python processes terminated")
                time.sleep(2)
            else:
                print("   ℹ️ No Python processes to terminate")
        except Exception as e:
            print(f"   ❌ Process cleanup failed: {e}")

def test_chromadb_safety():
    """ChromaDBの安全な初期化をテスト"""
    print("\n=" * 60)
    print("🧪 ChromaDB安全初期化テスト")
    print("=" * 60)

    # 既存プロセスのクリーンアップ
    cleanup_existing_processes()

    try:
        # 環境設定
        from dotenv import load_dotenv
        load_dotenv()

        persist_directory = "db/chroma_store"
        print(f"\n   Target directory: {persist_directory}")
        print(f"   Directory exists: {os.path.exists(persist_directory)}")

        # ファイルロック状況の確認
        if os.path.exists(persist_directory):
            chroma_db_file = os.path.join(persist_directory, "chroma.sqlite3")
            if os.path.exists(chroma_db_file):
                print(f"   SQLite file exists: {chroma_db_file}")
                try:
                    # ファイルアクセステスト
                    with open(chroma_db_file, 'r+b') as f:
                        print("   ✅ SQLite file is accessible")
                except PermissionError:
                    print("   ❌ SQLite file is locked")
                except Exception as e:
                    print(f"   ⚠️ SQLite file access error: {e}")

        # 埋め込みモデルの初期化
        print("\n1️⃣ 埋め込みモデル初期化")
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            embedding_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            print("   ✅ HuggingFaceEmbeddings initialized")
        except Exception as e:
            print(f"   ❌ Embedding initialization failed: {e}")
            return

        # ChromaDBの安全な初期化テスト
        print("\n2️⃣ ChromaDB安全初期化")
        from langchain_chroma import Chroma

        vector_db = None
        for attempt in range(3):
            try:
                print(f"   Attempt {attempt + 1}/3...")

                vector_db = Chroma(
                    persist_directory=persist_directory,
                    embedding_function=embedding_model
                )

                # 接続テスト
                vector_db._collection.count()
                print(f"   ✅ ChromaDB initialized successfully (attempt {attempt + 1})")
                break

            except Exception as e:
                print(f"   ❌ Attempt {attempt + 1} failed: {e}")

                if attempt == 0:
                    # ディレクトリのリネーム
                    if os.path.exists(persist_directory):
                        import uuid
                        backup_name = f"{persist_directory}_backup_{uuid.uuid4().hex[:8]}"
                        try:
                            os.rename(persist_directory, backup_name)
                            print(f"   🔄 Moved locked directory to: {backup_name}")
                        except Exception:
                            print("   ⚠️ Cannot move directory")

                    os.makedirs(persist_directory, exist_ok=True)

                elif attempt == 1:
                    # 一時ディレクトリを使用
                    import tempfile
                    persist_directory = tempfile.mkdtemp(prefix="uma3_test_")
                    print(f"   🔄 Using temporary directory: {persist_directory}")

        if vector_db:
            print("\n3️⃣ ChromaDB動作テスト")
            try:
                # テストデータの追加
                test_texts = ["テストドキュメント1", "テストドキュメント2"]
                vector_db.add_texts(test_texts)
                print("   ✅ Test documents added")

                # 検索テスト
                results = vector_db.similarity_search("テスト", k=1)
                print(f"   ✅ Search test successful: {len(results)} results")

            except Exception as e:
                print(f"   ❌ ChromaDB operation failed: {e}")
        else:
            print("   ❌ ChromaDB initialization completely failed")

        print("\n=" * 60)
        print("🎉 ChromaDB安全性テスト完了")
        print("=" * 60)

    except Exception as e:
        print(f"❌ テスト中にエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chromadb_safety()
