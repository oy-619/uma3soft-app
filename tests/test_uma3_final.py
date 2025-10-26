#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from dotenv import load_dotenv

sys.path.append(".")

# 環境変数の読み込み
load_dotenv()

# OpenAI API設定を環境変数から取得
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable is not set")

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from uma3_chroma_improver import Uma3ChromaDBImprover


def test_uma3_improved():
    """改善されたUma3システムのテスト"""

    print("=" * 60)
    print("🤖 Uma3改善版システムテスト")
    print("=" * 60)

    # 初期化（uma3.pyと同じ設定）
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vector_db = Chroma(
        persist_directory="chroma_store",
        embedding_function=embedding_model
    )

    # ChromaDB精度向上機能の初期化
    chroma_improver = Uma3ChromaDBImprover(vector_db)

    # OpenAI LLM初期化
    llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")

    # テストクエリ
    test_query = "今後の予定を教えてください"
    user_id = "test_user"

    print(f"🔍 テストクエリ: '{test_query}'")
    print(f"👤 ユーザーID: {user_id}")
    print()

    # ステップ1: 改善された検索実行
    print("📋 ステップ1: 改善検索実行")
    print("-" * 30)

    results = chroma_improver.schedule_aware_search(
        test_query,
        k=6,
        score_threshold=0.5
    )

    print(f"✅ 検索結果: {len(results)}件")

    if len(results) > 0:
        note_count = sum(1 for doc in results if "[ノート]" in doc.page_content)
        print(f"📝 [ノート]データ: {note_count}件 ({note_count/len(results)*100:.1f}%)")

    # 正解データ確認
    targets_found = []
    target_keywords = [
        "第52回東京都小学生男子ソフトボール秋季大会",
        "羽村ライオンズさんとの練習試合",
        "大森リーグ若草ジュニア杯"
    ]

    if len(results) > 0:
        for doc in results:
            for target in target_keywords:
                if target[:20] in doc.page_content:
                    targets_found.append(target)
                    break

    print(f"🎯 正解データ発見: {len(targets_found)}/{len(target_keywords)}件")
    for target in targets_found:
        print(f"   ✅ {target}")

    # ステップ2: コンテキスト構築
    print("\n📋 ステップ2: コンテキスト構築")
    print("-" * 30)

    if results:
        context_parts = []
        for i, doc in enumerate(results, 1):
            user = doc.metadata.get('user', 'Unknown')
            timestamp = doc.metadata.get('timestamp', 'Unknown')
            content = doc.page_content
            context_parts.append(f"{i}. [{user}] {timestamp}: {content}")

        context = "\n".join(context_parts)
        print(f"📄 コンテキスト長: {len(context)}文字")

        # ステップ3: LLM応答生成
        print(f"\n📋 ステップ3: LLM応答生成")
        print("-" * 30)

        user_match_count = sum(1 for doc in results if doc.metadata.get('user') == user_id)
        context_quality = (user_match_count / len(results)) * 100

        if context_quality > 30:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "あなたは優秀なアシスタントです。以下の過去の会話履歴（特にユーザーの過去の発言）を参考にして、ユーザーの質問に自然で親しみやすく答えてください。\n---\n{context}\n---"),
                ("user", "{query}")
            ])
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "あなたは優秀なアシスタントです。以下の関連する会話履歴を参考にして、ユーザーの質問に答えてください。\n---\n{context}\n---"),
                ("user", "{query}")
            ])

        chain = prompt | llm

        try:
            response = chain.invoke({
                "context": context,
                "query": test_query
            })

            reply_text = response.content

            print("🤖 Uma3回答:")
            print("="*50)
            print(reply_text)
            print("="*50)

        except Exception as e:
            print(f"❌ LLM呼び出しエラー: {e}")

    else:
        print("❌ 検索結果が見つかりませんでした")


if __name__ == "__main__":
    test_uma3_improved()
