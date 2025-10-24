#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
metadataベースの未来日付フィルタリングテスト
"""

import os
import sys
from datetime import datetime

sys.path.append(".")

# OpenAI API設定（環境変数から取得）
if "OPENAI_API_KEY" not in os.environ:
    print("⚠️  OPENAI_API_KEYの環境変数を設定してください")
    sys.exit(1)


def test_metadata_timestamp_parsing():
    """metadataのtimestamp解析機能をテスト"""

    print("=" * 60)
    print("📅 metadataベース未来日付フィルタリングテスト")
    print("=" * 60)
    print()

    # 初期化
    try:
        from langchain_chroma import Chroma
        from langchain_huggingface import HuggingFaceEmbeddings
        from uma3_chroma_improver import Uma3ChromaDBImprover

        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        vector_db = Chroma(
            persist_directory="chroma_store", embedding_function=embedding_model
        )
        chroma_improver = Uma3ChromaDBImprover(vector_db)

        print("✅ 初期化成功")

    except Exception as e:
        print(f"❌ 初期化失敗: {e}")
        return

    # 1. timestamp解析テスト
    print("\n📋 1. timestamp解析テスト")
    print("-" * 40)

    current_time = datetime.now()
    print(f"現在日時: {current_time.strftime('%Y年%m月%d日 %H:%M')}")

    # テストケース
    test_timestamps = [
        "R5/10/22(日) 14:30",  # 過去（2023年10月22日）
        "R6/4/5(土) 09:00",  # 過去（2024年4月5日）
        "R7/10/25(土) 10:00",  # 未来？（2025年10月25日）
        "R7/11/1(土) 11:00",  # 未来（2025年11月1日）
        "R7/12/23(日) 09:00",  # 未来（2025年12月23日）
        "R8/3/15(月) 08:30",  # 未来（2026年3月15日）
    ]

    print("timestamp解析結果:")
    for timestamp_str in test_timestamps:
        parsed_dt = chroma_improver._parse_timestamp_metadata(timestamp_str)
        if parsed_dt:
            is_future = parsed_dt.date() > current_time.date()
            status = "🔮 未来" if is_future else "⏰ 過去"
            print(
                f"{status} | {timestamp_str} → {parsed_dt.strftime('%Y年%m月%d日 %H:%M')}"
            )
        else:
            print(f"❌ 解析失敗 | {timestamp_str}")

    # 2. 実際のChromaDBデータでのテスト
    print("\n📋 2. 実際のChromaDBデータでのテスト")
    print("-" * 40)

    try:
        # 「今後の予定」で検索
        test_query = "今後の予定を教えてください"
        print(f"テストクエリ: '{test_query}'")

        # 未来フィルタありで検索
        future_results = chroma_improver.schedule_aware_search(
            test_query, k=10, score_threshold=0.5, future_only=True
        )

        print(f"\n検索結果: {len(future_results)}件")

        if future_results:
            print("\n詳細分析:")
            metadata_future_count = 0
            content_future_count = 0

            for i, doc in enumerate(future_results[:5], 1):
                timestamp = doc.metadata.get("timestamp", "Unknown")
                content = doc.page_content[:100].replace("\n", " ")

                # metadata判定
                is_future_meta = chroma_improver._is_future_by_metadata(
                    doc, current_time
                )
                # content判定
                is_future_content = chroma_improver._extract_future_dates(
                    doc.page_content, current_time
                )

                if is_future_meta:
                    metadata_future_count += 1
                if is_future_content:
                    content_future_count += 1

                meta_mark = "📅" if is_future_meta else "⏰"
                content_mark = "📝" if is_future_content else "📄"

                print(f"\n{i}. {meta_mark}{content_mark} | {timestamp}")
                print(f"   内容: {content}...")

            print(f"\n📊 判定結果統計:")
            print(f"   metadataによる未来判定: {metadata_future_count}件")
            print(f"   contentによる未来判定: {content_future_count}件")

        # 3. 実データのtimestamp分布確認
        print(f"\n📋 3. 実データのtimestamp分布確認")
        print("-" * 40)

        # ChromaDBから一部データを取得して分析
        collection = vector_db._collection
        sample_data = collection.get(limit=100)

        if sample_data and "metadatas" in sample_data:
            timestamp_analysis = {}

            for metadata in sample_data["metadatas"]:
                if metadata and "timestamp" in metadata:
                    timestamp_str = metadata["timestamp"]
                    parsed_dt = chroma_improver._parse_timestamp_metadata(timestamp_str)

                    if parsed_dt:
                        year_month = f"{parsed_dt.year}年{parsed_dt.month}月"
                        timestamp_analysis[year_month] = (
                            timestamp_analysis.get(year_month, 0) + 1
                        )

            print("timestamp分布（サンプル100件）:")
            for year_month, count in sorted(timestamp_analysis.items()):
                print(f"   {year_month}: {count}件")

    except Exception as e:
        print(f"❌ テスト失敗: {e}")
        import traceback

        traceback.print_exc()

    print(f"\n🎉 metadataベース未来日付フィルタリングテスト完了!")
    print("=" * 60)


if __name__ == "__main__":
    test_metadata_timestamp_parsing()
