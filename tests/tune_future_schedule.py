"""
「今後の予定を教えてください。」クエリのチューニング
正解回答内容への最適化
"""

import os
import sys
import time
from datetime import datetime

sys.path.append(".")

from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from uma3_chroma_improver import Uma3ChromaDBImprover


def tune_future_schedule_query():
    """「今後の予定を教えてください。」クエリのチューニング"""
    print("=" * 80)
    print("🔧 「今後の予定を教えてください。」クエリチューニング")
    print("=" * 80)

    # クエリと正解回答の設定
    target_query = "今後の予定を教えてください。"
    correct_answers = [
        "[ノート] 第52回東京都小学生男子ソフトボール秋季大会　【大会日程】10月25日（土）／26日（日）／予備日・11月1日（土）／2日（日）",
        "[ノート] 羽村ライオンズさんとの練習試合",
        "[ノート] 大森リーグ若草ジュニア杯（3年生以下）日時：2025/11/03(月祝)11:00～15:00（17:00まで利用可）",
    ]

    print(f"📋 チューニング対象クエリ: '{target_query}'")
    print(f"🎯 正解回答数: {len(correct_answers)}件")
    print(f"⏰ 実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 初期化
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vector_db = Chroma(
        persist_directory="chroma_store", embedding_function=embedding_model
    )
    improver = Uma3ChromaDBImprover(vector_db)

    # OpenAI設定（環境変数から取得）
    if "OPENAI_API_KEY" not in os.environ:
        print("⚠️  OPENAI_API_KEYの環境変数を設定してください")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("📊 STEP 1: 現在の検索結果分析")
    print("=" * 60)

    # 現在の検索結果を確認
    def analyze_search_results(search_results, search_type):
        print(f"\n🔍 {search_type}検索結果分析")
        print("-" * 40)

        if not search_results:
            print("❌ 検索結果なし")
            return {"score": 0, "matches": [], "coverage": 0}

        # 正解回答との一致度チェック
        matches = []
        for i, doc in enumerate(search_results, 1):
            content = doc.page_content
            for j, correct in enumerate(correct_answers):
                # 部分的一致をチェック
                if any(
                    keyword in content
                    for keyword in ["東京都小学生", "秋季大会", "10月25日", "10月26日"]
                ):
                    matches.append(
                        {
                            "result_idx": i,
                            "correct_idx": j,
                            "type": "秋季大会",
                            "content": content[:60],
                        }
                    )
                elif any(
                    keyword in content for keyword in ["羽村ライオンズ", "練習試合"]
                ):
                    matches.append(
                        {
                            "result_idx": i,
                            "correct_idx": j,
                            "type": "練習試合",
                            "content": content[:60],
                        }
                    )
                elif any(
                    keyword in content
                    for keyword in ["若草ジュニア杯", "2025/11/03", "大森リーグ"]
                ):
                    matches.append(
                        {
                            "result_idx": i,
                            "correct_idx": j,
                            "type": "ジュニア杯",
                            "content": content[:60],
                        }
                    )

        print(f"検索結果数: {len(search_results)}件")
        print(f"正解一致数: {len(matches)}件")

        if matches:
            print("一致内容:")
            for match in matches:
                print(
                    f"  {match['result_idx']}位: {match['type']} - {match['content']}..."
                )

        coverage = (len(matches) / len(correct_answers)) * 100
        score = (len(matches) / len(search_results)) * 100 if search_results else 0

        print(f"正解カバー率: {coverage:.1f}% ({len(matches)}/{len(correct_answers)})")
        print(f"精度スコア: {score:.1f}%")

        return {"score": score, "matches": matches, "coverage": coverage}

    # 各検索方法でテスト
    print("\n🔍 1-1. 基本検索")
    basic_results = vector_db.similarity_search(target_query, k=10)
    basic_analysis = analyze_search_results(basic_results, "基本")

    print("\n🧠 1-2. スマート検索（現在設定）")
    smart_results = improver.smart_similarity_search(
        target_query, k=10, score_threshold=0.5, boost_recent=True
    )
    smart_analysis = analyze_search_results(smart_results, "スマート")

    # 改良版検索パラメータのテスト
    print("\n" + "=" * 60)
    print("🔧 STEP 2: チューニングパラメータのテスト")
    print("=" * 60)

    # 異なるパラメータでのテスト
    tuning_params = [
        {"threshold": 0.3, "k": 15, "desc": "閾値緩和・件数増加"},
        {"threshold": 0.4, "k": 12, "desc": "中間設定"},
        {"threshold": 0.6, "k": 8, "desc": "厳格設定"},
        {"threshold": 0.5, "k": 20, "desc": "大量取得"},
    ]

    best_params = None
    best_score = 0

    for i, params in enumerate(tuning_params, 1):
        print(f"\n🧪 2-{i}. テスト: {params['desc']}")
        print(f"   パラメータ: 閾値={params['threshold']}, 件数={params['k']}")

        tuned_results = improver.smart_similarity_search(
            target_query,
            k=params["k"],
            score_threshold=params["threshold"],
            boost_recent=True,
        )

        analysis = analyze_search_results(tuned_results, f"チューニング{i}")

        if analysis["coverage"] > best_score:
            best_score = analysis["coverage"]
            best_params = params
            best_params["results"] = tuned_results

    print(f"\n🏆 最適パラメータ: {best_params['desc']}")
    print(f"   設定: 閾値={best_params['threshold']}, 件数={best_params['k']}")
    print(f"   カバー率: {best_score:.1f}%")

    # 検索キーワード拡張テスト
    print("\n" + "=" * 60)
    print("🎯 STEP 3: 検索キーワード拡張テスト")
    print("=" * 60)

    # より具体的なクエリでのテスト
    expanded_queries = [
        "秋季大会 10月 ソフトボール",
        "練習試合 羽村ライオンズ",
        "若草ジュニア杯 11月 大森リーグ",
        "今後の大会予定 試合スケジュール",
        "2025年 11月 予定",
    ]

    all_expanded_results = []

    for i, expanded_query in enumerate(expanded_queries, 1):
        print(f"\n🔍 3-{i}. 拡張クエリ: '{expanded_query}'")

        expanded_results = improver.smart_similarity_search(
            expanded_query, k=best_params["k"], score_threshold=best_params["threshold"]
        )

        analysis = analyze_search_results(expanded_results, f"拡張{i}")
        all_expanded_results.extend(expanded_results)

    # 重複除去して統合
    unique_expanded = []
    seen_content = set()
    for doc in all_expanded_results:
        content_key = doc.page_content[:50]
        if content_key not in seen_content:
            seen_content.add(content_key)
            unique_expanded.append(doc)

    print(f"\n📊 拡張検索統合結果")
    print("-" * 40)
    expanded_analysis = analyze_search_results(unique_expanded[:15], "統合拡張")

    # LLM回答生成とテスト
    print("\n" + "=" * 60)
    print("🤖 STEP 4: LLM回答生成とチューニング")
    print("=" * 60)

    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.3,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )

    def generate_tuned_response(search_results, prompt_type):
        if not search_results:
            return "関連する予定情報が見つかりませんでした。"

        # コンテキスト構築
        context_parts = []
        for doc in search_results[:10]:
            content = doc.page_content
            # 予定関連の情報を優先
            if any(
                keyword in content
                for keyword in ["ノート", "日時", "場所", "大会", "試合", "予定"]
            ):
                context_parts.append(content)

        context = "\n".join(context_parts)

        if prompt_type == "基本":
            prompt_template = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "あなたは優秀なアシスタントです。以下の過去の会話履歴を参考にして、ユーザーの質問に答えてください。\n---\n{context}\n---",
                    ),
                    ("human", "{input}"),
                ]
            )
        elif prompt_type == "予定特化":
            prompt_template = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "あなたは予定管理の専門アシスタントです。以下の情報から今後の予定（大会、練習試合、イベント）を整理して、日時順に回答してください。[ノート]で始まる情報を優先してください。\n---\n{context}\n---",
                    ),
                    ("human", "{input}"),
                ]
            )
        elif prompt_type == "構造化":
            prompt_template = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "以下の情報から今後の予定を抽出し、以下の形式で回答してください：\n1. 大会・試合名\n2. 日時\n3. 場所（あれば）\n\n情報：\n---\n{context}\n---",
                    ),
                    ("human", "{input}"),
                ]
            )

        prompt = prompt_template.format(context=context, input=target_query)
        response = llm.invoke(prompt)
        return response.content

    # 各手法でLLM回答を生成
    test_results = [
        {"name": "現在設定", "results": smart_results, "prompt": "基本"},
        {"name": "最適パラメータ", "results": best_params["results"], "prompt": "基本"},
        {"name": "拡張検索", "results": unique_expanded[:10], "prompt": "基本"},
        {
            "name": "予定特化プロンプト",
            "results": best_params["results"],
            "prompt": "予定特化",
        },
        {
            "name": "構造化プロンプト",
            "results": best_params["results"],
            "prompt": "構造化",
        },
    ]

    best_response = None
    best_match_score = 0

    for i, test in enumerate(test_results, 1):
        print(f"\n🤖 4-{i}. {test['name']}での回答生成")
        print("-" * 40)

        response = generate_tuned_response(test["results"], test["prompt"])
        print(f"回答内容:")
        print(response)

        # 正解回答との一致度評価
        match_count = 0
        for correct in correct_answers:
            key_terms = []
            if "東京都小学生" in correct or "秋季大会" in correct:
                key_terms = ["東京都小学生", "秋季大会", "10月25日", "10月26日"]
            elif "羽村ライオンズ" in correct:
                key_terms = ["羽村ライオンズ", "練習試合"]
            elif "若草ジュニア杯" in correct:
                key_terms = ["若草ジュニア杯", "大森リーグ", "2025/11/03", "11月"]

            if any(term in response for term in key_terms):
                match_count += 1

        match_score = (match_count / len(correct_answers)) * 100
        print(f"正解一致率: {match_score:.1f}% ({match_count}/{len(correct_answers)})")

        if match_score > best_match_score:
            best_match_score = match_score
            best_response = {
                "name": test["name"],
                "response": response,
                "score": match_score,
            }

    # 最終チューニング結果
    print("\n" + "=" * 60)
    print("🎯 STEP 5: 最終チューニング結果")
    print("=" * 60)

    print(f"🏆 最適手法: {best_response['name']}")
    print(f"📊 正解一致率: {best_response['score']:.1f}%")
    print(f"🎯 推奨設定:")
    print(f"   検索閾値: {best_params['threshold']}")
    print(f"   検索件数: {best_params['k']}")
    print(f"   プロンプト: 予定特化型")

    print(f"\n📝 最適回答例:")
    print("-" * 40)
    print(best_response["response"])

    # チューニング適用
    print("\n" + "=" * 60)
    print("⚙️ STEP 6: チューニング設定適用")
    print("=" * 60)

    return {
        "optimal_threshold": best_params["threshold"],
        "optimal_k": best_params["k"],
        "best_method": best_response["name"],
        "match_score": best_response["score"],
    }


if __name__ == "__main__":
    results = tune_future_schedule_query()
    print(f"\n✅ チューニング完了")
    print(f"最適設定: 閾値={results['optimal_threshold']}, 件数={results['optimal_k']}")
    print(f"最適手法: {results['best_method']}")
    print(f"達成率: {results['match_score']:.1f}%")
