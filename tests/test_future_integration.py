#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
未来日付フィルタリング統合テスト（簡易版）
"""

import os
import sys

sys.path.append(".")

# OpenAI API設定（環境変数から取得）
if "OPENAI_API_KEY" not in os.environ:
    print("⚠️  OPENAI_API_KEYの環境変数を設定してください")
    sys.exit(1)


def test_future_schedule_integration():
    """未来予定フィルタリングの統合テスト"""

    print("=" * 60)
    print("🚀 未来予定フィルタリング統合テスト")
    print("=" * 60)
    print()

    # システム初期化
    try:
        from langchain_chroma import Chroma
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_openai import ChatOpenAI
        from uma3 import format_message_for_mobile, split_long_message
        from uma3_chroma_improver import Uma3ChromaDBImprover

        print("✅ モジュール読み込み成功")

        # ChromaDB初期化
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        vector_db = Chroma(
            persist_directory="chroma_store", embedding_function=embedding_model
        )
        chroma_improver = Uma3ChromaDBImprover(vector_db)

        print("✅ ChromaDB初期化成功")

    except Exception as e:
        print(f"❌ 初期化失敗: {e}")
        return

    # テストクエリ
    test_query = "今後の予定を教えてください"
    print(f"🔍 テストクエリ: '{test_query}'")
    print()

    # 未来フィルタありの検索
    print("📋 未来フィルタありの検索結果:")
    print("-" * 40)

    try:
        future_results = chroma_improver.schedule_aware_search(
            test_query, k=6, score_threshold=0.5, future_only=True  # 明示的に未来のみ
        )

        print(f"📊 検索結果: {len(future_results)}件")

        if future_results:
            note_count = sum(
                1 for doc in future_results if "[ノート]" in doc.page_content
            )
            print(
                f"📝 [ノート]データ: {note_count}件 ({note_count/len(future_results)*100:.1f}%)"
            )

            print("\n検索結果詳細:")
            for i, doc in enumerate(future_results[:3], 1):
                content = doc.page_content.replace("\n", " ")[:100]
                print(f"{i}. {content}...")

        # LLM応答生成テスト
        print(f"\n📋 LLM応答生成テスト:")
        print("-" * 40)

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
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """あなたは優秀なアシスタントです。以下の関連する会話履歴を参考にして、ユーザーの質問に答えてください。

回答時は以下の点を心がけてください：
- スマートフォンで読みやすいように、適度に改行を入れる
- 重要な情報は箇条書きで整理する
- 予定や日程がある場合は、日付・時間・場所を明確に記載する
- 現在日時より未来の予定のみを提示する

---
{context}
---""",
                ),
                ("human", "{input}"),
            ]
        )

        if context:
            prompt = prompt_template.format(context=context, input=test_query)
        else:
            prompt = prompt_template.format(
                context="未来の予定情報が見つかりません。", input=test_query
            )

        # LLM応答生成
        response = llm.invoke(prompt)
        raw_answer = response.content

        print(f"✅ LLM応答生成成功 ({len(raw_answer)}文字)")

        # スマートフォン対応フォーマット
        formatted_answer = format_message_for_mobile(raw_answer)
        message_parts = split_long_message(formatted_answer, max_length=1000)

        print(f"📱 フォーマット完了 ({len(message_parts)}メッセージ)")

        # 最終的な返信内容を表示
        print(f"\n🤖 最終的な返信内容:")
        print("=" * 50)

        for i, part in enumerate(message_parts, 1):
            if len(message_parts) > 1:
                print(f"\n--- メッセージ{i} ---")
            print(part)
            if len(message_parts) > 1:
                print("--- 終了 ---")

        print("=" * 50)

    except Exception as e:
        print(f"❌ 統合テスト失敗: {e}")
        import traceback

        traceback.print_exc()
        return

    print(f"\n🎉 未来予定フィルタリング統合テスト完了!")
    print("=" * 60)


if __name__ == "__main__":
    test_future_schedule_integration()
