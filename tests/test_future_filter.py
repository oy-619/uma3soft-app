#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
未来日付フィルタリング機能のテスト
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.append(".")

# 環境変数の読み込み
from dotenv import load_dotenv
load_dotenv()

# OpenAI API設定を環境変数から取得
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable is not set")


def test_future_date_filtering():
    """未来日付フィルタリング機能のテスト"""

    print("=" * 70)
    print("📅 未来日付フィルタリング機能テスト")
    print("=" * 70)
    print()

    # 1. Uma3ChromaDBImproverの初期化
    print("📋 1. 初期化テスト")
    print("-" * 40)

    try:
        from langchain_chroma import Chroma
        from langchain_huggingface import HuggingFaceEmbeddings
        from uma3_chroma_improver import Uma3ChromaDBImprover

        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        vector_db = Chroma(
            persist_directory="chroma_store",
            embedding_function=embedding_model
        )
        chroma_improver = Uma3ChromaDBImprover(vector_db)

        print("✅ ChromaDB + Uma3ChromaDBImprover初期化成功")

    except Exception as e:
        print(f"❌ 初期化失敗: {e}")
        return

    # 2. 日付抽出機能テスト
    print("\n📋 2. 日付抽出機能テスト")
    print("-" * 40)

    # 現在日時を取得
    current_time = datetime.now()
    print(f"現在日時: {current_time.strftime('%Y年%m月%d日 %H:%M')}")

    # テストケース
    test_cases = [
        # 未来の日付（今年）
        f"{current_time.month + 1}月15日（土）の練習試合",
        f"{current_time.month + 2}月10日の大会",
        "12月25日のクリスマス試合",

        # 過去の日付
        f"{current_time.month - 1}月10日の試合結果",
        "4月1日の結果",

        # 未来を示すキーワード
        "今後の予定について",
        "これからの練習について",
        "将来の大会について",
        "次回の試合について",

        # 日付なし
        "今日はいい天気ですね",
        "ありがとうございます",
    ]

    print("テストケース結果:")
    for i, test_text in enumerate(test_cases, 1):
        is_future = chroma_improver._extract_future_dates(test_text, current_time)
        status = "✅ 未来" if is_future else "❌ 過去/無関係"
        print(f"{i:2d}. {status} | {test_text}")

    # 3. 「今後の予定を教えてください」での検索テスト
    print("\n📋 3. 未来日付フィルタリング検索テスト")
    print("-" * 40)

    test_query = "今後の予定を教えてください"
    print(f"テストクエリ: '{test_query}'")

    try:
        # 未来フィルタありの検索
        future_results = chroma_improver.schedule_aware_search(
            test_query,
            k=10,
            score_threshold=0.5,
            future_only=True
        )

        print(f"\n🔮 未来フィルタあり: {len(future_results)}件")

        if future_results:
            print("検索結果:")
            for i, doc in enumerate(future_results, 1):
                content = doc.page_content[:100].replace('\n', ' ')
                is_future = chroma_improver._extract_future_dates(doc.page_content, current_time)
                future_mark = "🔮" if is_future else "⏰"
                print(f"{i:2d}. {future_mark} {content}...")

        # 未来フィルタなしの検索（比較用）
        all_results = chroma_improver.schedule_aware_search(
            test_query,
            k=10,
            score_threshold=0.5,
            future_only=False
        )

        print(f"\n📄 未来フィルタなし: {len(all_results)}件")

        # 効果の評価
        future_ratio = len(future_results) / len(all_results) * 100 if all_results else 0
        print(f"📊 未来フィルタ効果: {len(future_results)}/{len(all_results)} ({future_ratio:.1f}%)")

    except Exception as e:
        print(f"❌ 検索テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return

    # 4. 実際の予定データでの検証
    print("\n📋 4. 実際の予定データでの検証")
    print("-" * 40)

    try:
        # ChromaDBから全データを取得して分析
        collection = vector_db._collection
        all_data = collection.get()

        total_docs = len(all_data['documents'])
        print(f"📊 総データ数: {total_docs}件")

        # [ノート]データの分析
        note_docs = [doc for doc in all_data['documents'] if "[ノート]" in doc]
        print(f"📝 [ノート]データ: {len(note_docs)}件")

        # 未来の日付を含むデータの分析
        future_docs = []
        for doc in note_docs:
            if chroma_improver._extract_future_dates(doc, current_time):
                future_docs.append(doc)

        print(f"🔮 未来予定データ: {len(future_docs)}件")

        if future_docs:
            print("\n未来の予定データ例:")
            for i, doc in enumerate(future_docs[:3], 1):
                content = doc[:100].replace('\n', ' ')
                print(f"{i}. {content}...")

    except Exception as e:
        print(f"⚠️ データ分析中にエラー: {e}")

    print(f"\n🎉 未来日付フィルタリング機能テスト完了!")
    print("=" * 70)


if __name__ == "__main__":
    test_future_date_filtering()
