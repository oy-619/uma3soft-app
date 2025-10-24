#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
スマートフォン対応の改善をテストする統合テスト
"""

import os
import re
import sys

sys.path.append(".")

# OpenAI API設定（環境変数から取得）
if "OPENAI_API_KEY" not in os.environ:
    print("⚠️  OPENAI_API_KEYの環境変数を設定してください")
    sys.exit(1)


def test_complete_mobile_system():
    """完全なスマートフォン対応システムのテスト"""

    print("=" * 70)
    print("📱🤖 スマートフォン対応Uma3システム統合テスト")
    print("=" * 70)
    print()

    # 1. 基本機能のテスト
    print("📋 1. 基本機能テスト")
    print("-" * 40)

    try:
        from langchain_chroma import Chroma
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_openai import ChatOpenAI
        from uma3 import format_message_for_mobile, split_long_message
        from uma3_chroma_improver import Uma3ChromaDBImprover

        print("✅ 全モジュールのインポート成功")

    except Exception as e:
        print(f"❌ モジュールインポートエラー: {e}")
        return

    # 2. ChromaDB + 改善検索テスト
    print("\n📋 2. ChromaDB + 改善検索テスト")
    print("-" * 40)

    try:
        # ChromaDB初期化
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        vector_db = Chroma(
            persist_directory="chroma_store", embedding_function=embedding_model
        )
        chroma_improver = Uma3ChromaDBImprover(vector_db)

        print("✅ ChromaDB + Uma3ChromaDBImprover初期化成功")

        # 検索テスト
        test_query = "今後の予定を教えてください"
        results = chroma_improver.schedule_aware_search(
            test_query, k=6, score_threshold=0.5
        )

        print(f"✅ 検索実行成功: {len(results)}件")

        if results:
            note_count = sum(1 for doc in results if "[ノート]" in doc.page_content)
            print(
                f"📝 [ノート]データ率: {note_count}/{len(results)} ({note_count/len(results)*100:.1f}%)"
            )

    except Exception as e:
        print(f"❌ ChromaDB検索エラー: {e}")
        return

    # 3. LLM応答生成 + スマートフォンフォーマットテスト
    print("\n📋 3. LLM応答生成 + スマートフォンフォーマットテスト")
    print("-" * 40)

    try:
        # LLM初期化
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )

        # コンテキスト構築
        if results:
            context_parts = []
            for doc in results:
                context_parts.append(doc.page_content)
            context = "\n".join(context_parts)
        else:
            context = ""

        # プロンプト作成（スマートフォン対応版）
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """あなたは優秀なアシスタントです。以下の関連する会話履歴を参考にして、ユーザーの質問に答えてください。

回答時は以下の点を心がけてください：
- スマートフォンで読みやすいように、適度に改行を入れる
- 重要な情報は箇条書きで整理する
- 予定や日程がある場合は、日付・時間・場所を明確に記載する

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
                context="関連する情報がありません。", input=test_query
            )

        # LLM応答生成
        response = llm.invoke(prompt)
        raw_answer = response.content

        print("✅ LLM応答生成成功")
        print(f"📄 生成回答長: {len(raw_answer)}文字")

        # スマートフォン用フォーマット
        formatted_answer = format_message_for_mobile(raw_answer)
        print(f"📱 フォーマット後長: {len(formatted_answer)}文字")

        # メッセージ分割
        message_parts = split_long_message(formatted_answer, max_length=1000)
        print(f"✂️ 分割メッセージ数: {len(message_parts)}")

        # 結果表示
        print("\n🤖 最終的なLINE送信メッセージ:")
        print("=" * 50)

        for i, part in enumerate(message_parts, 1):
            print(f"\n--- メッセージ{i} ({len(part)}文字) ---")
            print(part)
            print("--- 終了 ---")

        print("=" * 50)

    except Exception as e:
        print(f"❌ LLM応答生成エラー: {e}")
        import traceback

        traceback.print_exc()
        return

    # 4. LINE API制限チェック
    print("\n📋 4. LINE API制限チェック")
    print("-" * 40)

    # LINE APIの制限
    MAX_MESSAGES_PER_REPLY = 5
    MAX_CHARS_PER_MESSAGE = 5000

    if len(message_parts) <= MAX_MESSAGES_PER_REPLY:
        print(f"✅ メッセージ数制限: {len(message_parts)}/{MAX_MESSAGES_PER_REPLY}")
    else:
        print(f"⚠️ メッセージ数制限超過: {len(message_parts)}/{MAX_MESSAGES_PER_REPLY}")

    for i, part in enumerate(message_parts, 1):
        if len(part) <= MAX_CHARS_PER_MESSAGE:
            print(f"✅ メッセージ{i}文字数制限: {len(part)}/{MAX_CHARS_PER_MESSAGE}")
        else:
            print(
                f"❌ メッセージ{i}文字数制限超過: {len(part)}/{MAX_CHARS_PER_MESSAGE}"
            )

    # 5. スマートフォン表示品質評価
    print("\n📋 5. スマートフォン表示品質評価")
    print("-" * 40)

    quality_score = 0
    total_checks = 0

    for part in message_parts:
        # 改行の適切性チェック
        total_checks += 1
        if "\n\n" in part:
            quality_score += 1
            print("✅ 段落区切りあり")
        else:
            print("⚠️ 段落区切りなし")

        # 箇条書きの存在チェック
        total_checks += 1
        if re.search(r"^\s*[-•・]\s+", part, re.MULTILINE):
            quality_score += 1
            print("✅ 箇条書き形式あり")
        else:
            print("⚠️ 箇条書き形式なし")

        # 絵文字の存在チェック（予定関連の場合）
        if "予定" in test_query:
            total_checks += 1
            if part.startswith("📅"):
                quality_score += 1
                print("✅ 予定絵文字あり")
            else:
                print("⚠️ 予定絵文字なし")

    quality_percentage = (quality_score / total_checks) * 100
    print(
        f"\n📊 スマートフォン表示品質: {quality_score}/{total_checks} ({quality_percentage:.1f}%)"
    )

    print(f"\n🎉 スマートフォン対応Uma3システム統合テスト完了!")
    print("=" * 70)


if __name__ == "__main__":
    test_complete_mobile_system()
