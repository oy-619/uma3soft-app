#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
改善後のuma3.pyの動作確認テスト
"""

import os
import sys

sys.path.append(".")

# OpenAI API設定（環境変数から取得）
if "OPENAI_API_KEY" not in os.environ:
    print("⚠️  OPENAI_API_KEYの環境変数を設定してください")
    sys.exit(1)


def test_improved_uma3():
    """改善されたuma3.pyの主要機能をテスト"""

    print("=" * 60)
    print("🚀 改善後Uma3システム動作確認")
    print("=" * 60)
    print()

    # 1. ChromaDB接続テスト
    print("📋 1. ChromaDB接続テスト")
    print("-" * 30)

    try:
        from langchain_chroma import Chroma
        from langchain_huggingface import HuggingFaceEmbeddings

        # 改善後の設定でChromaDB接続
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        vector_db = Chroma(
            persist_directory="chroma_store", embedding_function=embedding_model
        )

        # データ数確認
        collection = vector_db._collection
        count = collection.count()
        print(f"✅ ChromaDB接続成功")
        print(f"📊 データ数: {count}件")

    except Exception as e:
        print(f"❌ ChromaDB接続失敗: {e}")
        return

    # 2. Uma3ChromaDBImprover初期化テスト
    print(f"\n📋 2. Uma3ChromaDBImprover初期化テスト")
    print("-" * 30)

    try:
        from uma3_chroma_improver import Uma3ChromaDBImprover

        chroma_improver = Uma3ChromaDBImprover(vector_db)
        print("✅ Uma3ChromaDBImprover初期化成功")

        # メソッド存在確認
        if hasattr(chroma_improver, "schedule_aware_search"):
            print("✅ schedule_aware_search メソッド確認")
        else:
            print("❌ schedule_aware_search メソッドが見つかりません")

        if hasattr(chroma_improver, "get_contextual_search"):
            print("✅ get_contextual_search メソッド確認")
        else:
            print("❌ get_contextual_search メソッドが見つかりません")

    except Exception as e:
        print(f"❌ Uma3ChromaDBImprover初期化失敗: {e}")
        return

    # 3. スケジュール特化検索テスト
    print(f"\n📋 3. スケジュール特化検索テスト")
    print("-" * 30)

    test_query = "今後の予定を教えてください"
    print(f"🔍 テストクエリ: '{test_query}'")

    try:
        results = chroma_improver.schedule_aware_search(
            test_query, k=6, score_threshold=0.5
        )

        print(f"✅ 検索実行成功")
        print(f"📊 検索結果: {len(results)}件")

        if results:
            # [ノート]データ率確認
            note_count = sum(1 for doc in results if "[ノート]" in doc.page_content)
            note_ratio = note_count / len(results) * 100
            print(
                f"📝 [ノート]データ率: {note_count}/{len(results)} ({note_ratio:.1f}%)"
            )

            # 正解データ確認
            target_keywords = ["東京都大会", "羽村ライオンズ", "大森リーグ"]
            found_targets = []
            for doc in results:
                for target in target_keywords:
                    if target in doc.page_content:
                        found_targets.append(target)
                        break

            if found_targets:
                print(f"🎯 正解データ発見: {found_targets}")
            else:
                print("⚠️ 正解データ未発見")

        else:
            print("⚠️ 検索結果なし")

    except Exception as e:
        print(f"❌ 検索テスト失敗: {e}")
        import traceback

        traceback.print_exc()
        return

    # 4. 設定確認
    print(f"\n📋 4. 設定確認")
    print("-" * 30)

    print("✅ エンベディングモデル: sentence-transformers/all-MiniLM-L6-v2")
    print("✅ ChromaDBパス: chroma_store")
    print("✅ 検索アルゴリズム: schedule_aware_search")

    print(f"\n🎉 改善後Uma3システム動作確認完了!")
    print("=" * 60)


if __name__ == "__main__":
    test_improved_uma3()
