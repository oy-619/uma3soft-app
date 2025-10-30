#!/usr/bin/env python3
"""
ChromaDBファイルアクセス確認テスト
"""

import os

def test_chromadb_file_access():
    """ChromaDBファイルへのアクセステスト"""
    chroma_file = r"C:\work\ws_python\GenerationAiCamp\Lesson25\uma3soft-app\db\chroma_store\chroma.sqlite3"

    print("=" * 50)
    print("🔍 ChromaDBファイルアクセステスト")
    print("=" * 50)

    print(f"📁 テスト対象ファイル: {chroma_file}")
    print(f"📂 ファイル存在: {'✅' if os.path.exists(chroma_file) else '❌'}")

    if os.path.exists(chroma_file):
        print(f"📊 ファイルサイズ: {os.path.getsize(chroma_file)} bytes")

        # ファイルアクセステスト
        try:
            with open(chroma_file, 'r+b') as f:
                print("✅ ファイルアクセス: 成功（ロックなし）")
            return True
        except (IOError, PermissionError) as e:
            print(f"⚠️ ファイルアクセス: 失敗（ロック中） - {e}")
            return False
    else:
        print("ℹ️ ChromaDBファイルが存在しません")
        return True

def test_psutil_availability():
    """psutilの可用性テスト"""
    print("\n🔍 psutil可用性テスト")
    print("=" * 50)

    try:
        import psutil
        print("✅ psutil利用可能")
        print(f"📊 現在のプロセス: PID {os.getpid()}")

        # Python関連プロセス数をカウント
        python_processes = 0
        for proc in psutil.process_iter(['name']):
            try:
                if 'python' in proc.info['name'].lower():
                    python_processes += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        print(f"🐍 Python関連プロセス: {python_processes}個")
        return True

    except ImportError:
        print("❌ psutil利用不可")
        return False

def main():
    """メインテスト実行"""
    print("ChromaDBファイルアクセス確認テスト")

    results = [
        test_chromadb_file_access(),
        test_psutil_availability()
    ]

    passed = sum(results)
    total = len(results)

    print("\n" + "=" * 50)
    print("📊 テスト結果")
    print("=" * 50)

    if passed == total:
        print(f"🎉 全テスト成功! ({passed}/{total})")
        print("✅ ファイルアクセスとpsutil機能が正常です")
    else:
        print(f"⚠️  一部テスト失敗 ({passed}/{total})")

    return passed == total

if __name__ == "__main__":
    main()
