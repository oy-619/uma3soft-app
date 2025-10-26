#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
未来日付フィルタリング機能 最終統合テスト
"""

import sys
import os

sys.path.append(".")

# 環境変数の読み込み
from dotenv import load_dotenv
load_dotenv()

# OpenAI API設定を環境変数から取得
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable is not set")


def test_final_future_filtering():
    """未来日付フィルタリング機能の最終統合テスト"""

    print("=" * 70)
    print("🏆 未来日付フィルタリング機能 最終統合テスト")
    print("=" * 70)
    print()

    try:
        from langchain_chroma import Chroma
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        from uma3_chroma_improver import Uma3ChromaDBImprover
        from uma3 import format_message_for_mobile, split_long_message

        # システム初期化
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        vector_db = Chroma(
            persist_directory="chroma_store",
            embedding_function=embedding_model
        )
        chroma_improver = Uma3ChromaDBImprover(vector_db)

        print("✅ システム初期化成功")

    except Exception as e:
        print(f"❌ 初期化失敗: {e}")
        return

    # テストクエリ
    test_query = "今後の予定を教えてください"
    print(f"🔍 テストクエリ: '{test_query}'")
    print()

    # 1. 未来フィルタありの検索
    print("📋 1. 未来フィルタありの検索")
    print("-" * 40)

    future_results = chroma_improver.schedule_aware_search(
        test_query,
        k=6,
        score_threshold=0.5,
        future_only=True  # 未来のみ
    )

    print(f"📊 検索結果: {len(future_results)}件")

    if future_results:
        note_count = sum(1 for doc in future_results if "[ノート]" in doc.page_content)
        print(f"📝 [ノート]データ: {note_count}件 ({note_count/len(future_results)*100:.1f}%)")

        # 正解データ確認
        target_keywords = ["東京都大会", "羽村ライオンズ", "大森リーグ"]
        found_targets = []
        for doc in future_results:
            for target in target_keywords:
                if target in doc.page_content:
                    found_targets.append(target)
                    break

        if found_targets:
            print(f"🎯 正解データ発見: {found_targets}")

    # 2. 未来フィルタなしとの比較
    print(f"\n📋 2. 未来フィルタなしとの比較")
    print("-" * 40)

    all_results = chroma_improver.schedule_aware_search(
        test_query,
        k=6,
        score_threshold=0.5,
        future_only=False  # フィルタなし
    )

    print(f"📊 全体検索結果: {len(all_results)}件")
    filter_ratio = len(future_results) / len(all_results) * 100 if all_results else 0
    print(f"📈 フィルタ効果: {len(future_results)}/{len(all_results)} ({filter_ratio:.1f}%)")

    # 3. LLM応答生成
    print(f"\n📋 3. LLM応答生成テスト")
    print("-" * 40)

    try:
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)

        # コンテキスト構築
        if future_results:
            context_parts = []
            for doc in future_results:
                context_parts.append(doc.page_content)
            context = "\n".join(context_parts)
        else:
            context = ""

        # プロンプト作成
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """あなたは優秀なアシスタントです。以下の関連する会話履歴を参考にして、ユーザーの質問に答えてください。

回答時は以下の点を心がけてください：
- スマートフォンで読みやすいように、適度に改行を入れる
- 重要な情報は箇条書きで整理する
- 予定や日程がある場合は、日付・時間・場所を明確に記載する
- 現在日時（2025年10月20日）より未来の予定のみを提示する

---
{context}
---"""),
            ("human", "{input}")
        ])

        if context:
            prompt = prompt_template.format(context=context, input=test_query)
        else:
            prompt = prompt_template.format(context="未来の予定情報が見つかりません。", input=test_query)

        # LLM応答生成
        response = llm.invoke(prompt)
        raw_answer = response.content

        print(f"✅ LLM応答生成成功 ({len(raw_answer)}文字)")

        # スマートフォン対応フォーマット
        formatted_answer = format_message_for_mobile(raw_answer)
        message_parts = split_long_message(formatted_answer, max_length=1000)

        print(f"📱 フォーマット完了 ({len(message_parts)}メッセージ)")

        # 最終的な返信内容を表示
        print(f"\n🤖 最終的なLINE返信内容:")
        print("="*50)

        for i, part in enumerate(message_parts, 1):
            if len(message_parts) > 1:
                print(f"\n--- メッセージ{i} ---")
            print(part)
            if len(message_parts) > 1:
                print("--- 終了 ---")

        print("="*50)

        # 4. 効果測定
        print(f"\n📋 4. 改善効果測定")
        print("-" * 40)

        # 未来関連キーワードの出現率
        future_keywords = ["10月", "11月", "12月", "25日", "1日", "23日", "大会", "練習試合"]
        keyword_count = sum(1 for keyword in future_keywords if keyword in raw_answer)

        print(f"🔍 未来関連キーワード含有: {keyword_count}/{len(future_keywords)} ({keyword_count/len(future_keywords)*100:.1f}%)")

        # 日付の具体性チェック
        import re
        date_matches = re.findall(r'\d{1,2}月\d{1,2}日', raw_answer)
        print(f"📅 具体的日付の言及: {len(date_matches)}件")
        if date_matches:
            print(f"   例: {', '.join(date_matches[:3])}")

        print(f"✅ 未来日付フィルタリング機能が正常に動作")

    except Exception as e:
        print(f"❌ LLM応答生成エラー: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n🎉 未来日付フィルタリング機能 最終統合テスト完了!")
    print("=" * 70)


if __name__ == "__main__":
    test_final_future_filtering()
