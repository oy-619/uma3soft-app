"""
ChromaDB検索結果とLLM回答の評価システム
「今週末の練習予定と試合予定をしえてください。」クエリの詳細分析
"""

import sys
import os
import time
from datetime import datetime

sys.path.append(".")

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from uma3_chroma_improver import Uma3ChromaDBImprover


def evaluate_query_response():
    """指定クエリの検索結果とLLM回答を詳細評価"""
    print("=" * 80)
    print("🔍 ChromaDB検索結果とLLM回答の詳細評価")
    print("=" * 80)

    # 評価対象クエリ
    target_query = "今週末の練習予定と試合予定をしえてください。"
    test_user = "評価用ユーザー"

    print(f"📋 評価対象クエリ: '{target_query}'")
    print(f"🔍 実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"👤 テストユーザー: {test_user}")

    # 初期化
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vector_db = Chroma(
        persist_directory="../chroma_store",
        embedding_function=embedding_model
    )
    improver = Uma3ChromaDBImprover(vector_db)

    # OpenAI設定
    # 環境変数の読み込み
    from dotenv import load_dotenv
    load_dotenv()
    
    # OpenAI API設定を環境変数から取得
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    print("\n" + "=" * 60)
    print("📊 STEP 1: ChromaDB検索結果の詳細分析")
    print("=" * 60)

    # 1. 基本検索
    print("\n🔍 1-1. 基本検索結果")
    print("-" * 40)

    start_time = time.time()
    basic_results = vector_db.similarity_search_with_score(target_query, k=10)
    basic_time = time.time() - start_time

    print(f"検索時間: {basic_time:.3f}秒")
    print(f"結果件数: {len(basic_results)}件")

    if basic_results:
        print("\n📋 基本検索結果詳細:")
        for i, (doc, score) in enumerate(basic_results, 1):
            content_preview = doc.page_content[:60].replace('\n', ' ')
            user = doc.metadata.get('user', 'Unknown')
            timestamp = doc.metadata.get('timestamp', 'Unknown')
            print(f"  {i:2d}. スコア: {score:.4f} | ユーザー: {user}")
            print(f"      時系列: {timestamp}")
            print(f"      内容: {content_preview}...")
            print()

    # 2. スマート検索
    print("\n🧠 1-2. スマート検索結果（改善版）")
    print("-" * 40)

    start_time = time.time()
    smart_results = improver.smart_similarity_search(
        target_query,
        k=10,
        user_id=test_user,
        boost_recent=True,
        score_threshold=0.5
    )
    smart_time = time.time() - start_time

    print(f"検索時間: {smart_time:.3f}秒")
    print(f"結果件数: {len(smart_results)}件")
    print(f"速度比較: {((smart_time - basic_time) / basic_time) * 100:+.1f}%")

    if smart_results:
        print("\n📋 スマート検索結果詳細:")
        for i, doc in enumerate(smart_results, 1):
            content_preview = doc.page_content[:60].replace('\n', ' ')
            user = doc.metadata.get('user', 'Unknown')
            timestamp = doc.metadata.get('timestamp', 'Unknown')
            print(f"  {i:2d}. ユーザー: {user} | 時系列: {timestamp}")
            print(f"      内容: {content_preview}...")
            print()

    # 3. コンテキスト検索
    print("\n🎯 1-3. コンテキスト検索結果")
    print("-" * 40)

    start_time = time.time()
    context_results = improver.get_contextual_search(target_query, test_user, k=5)
    context_time = time.time() - start_time

    print(f"検索時間: {context_time:.3f}秒")
    print(f"結果件数: {len(context_results)}件")

    if context_results:
        print("\n📋 コンテキスト検索結果詳細:")
        for i, doc in enumerate(context_results, 1):
            content_preview = doc.page_content[:60].replace('\n', ' ')
            user = doc.metadata.get('user', 'Unknown')
            timestamp = doc.metadata.get('timestamp', 'Unknown')
            print(f"  {i:2d}. ユーザー: {user} | 時系列: {timestamp}")
            print(f"      内容: {content_preview}...")
            print()

    # 4. 検索結果の関連性評価
    print("\n📈 1-4. 検索結果の関連性評価")
    print("-" * 40)

    # キーワード分析
    target_keywords = ['練習', '予定', '試合', '今週末', '週末', 'スケジュール', '日程']

    def analyze_relevance(results, result_type):
        if not results:
            return {"relevance_score": 0, "keyword_matches": 0, "total_results": 0}

        total_keyword_matches = 0
        relevant_results = 0

        # 結果の形式に応じて処理
        docs = []
        if isinstance(results[0], tuple):  # (doc, score)の形式
            docs = [doc for doc, score in results]
        else:  # docのみの形式
            docs = results

        for doc in docs:
            content = doc.page_content.lower()
            keyword_matches = sum(1 for keyword in target_keywords if keyword in content)
            total_keyword_matches += keyword_matches

            if keyword_matches > 0:
                relevant_results += 1

        relevance_score = (relevant_results / len(docs)) * 100 if docs else 0
        avg_keyword_matches = total_keyword_matches / len(docs) if docs else 0

        print(f"{result_type}:")
        print(f"  関連性スコア: {relevance_score:.1f}% ({relevant_results}/{len(docs)}件)")
        print(f"  平均キーワード一致: {avg_keyword_matches:.1f}個/件")
        print(f"  総キーワード一致: {total_keyword_matches}個")

        return {
            "relevance_score": relevance_score,
            "keyword_matches": total_keyword_matches,
            "total_results": len(docs),
            "relevant_results": relevant_results
        }    # 各検索方法の関連性評価
    basic_analysis = analyze_relevance(
        [(doc, score) for doc, score in basic_results], "基本検索"
    )
    smart_analysis = analyze_relevance(smart_results, "スマート検索")
    context_analysis = analyze_relevance(context_results, "コンテキスト検索")

    print("\n" + "=" * 60)
    print("🤖 STEP 2: LLM回答生成と評価")
    print("=" * 60)

    # LLM初期化
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.3,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    # 各検索結果でLLM回答を生成
    def generate_llm_response(search_results, search_type):
        print(f"\n🧠 2-{search_type}. {search_type}結果を使用したLLM回答")
        print("-" * 40)

        if not search_results:
            print("検索結果なし - コンテキストなしで回答生成")
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", "あなたは優秀なアシスタントです。"),
                ("human", "{input}")
            ])
            prompt = prompt_template.format(input=target_query)
        else:
            # コンテキスト構築
            if isinstance(search_results[0], tuple):  # (doc, score) の場合
                context_parts = [doc.page_content for doc, score in search_results[:5]]
            else:  # doc のみの場合
                context_parts = [doc.page_content for doc in search_results[:5]]

            context = "\n".join(context_parts)

            prompt_template = ChatPromptTemplate.from_messages([
                ("system", "あなたは優秀なアシスタントです。以下の過去の会話履歴を参考にして、ユーザーの質問に答えてください。\n---\n{context}\n---"),
                ("human", "{input}")
            ])
            prompt = prompt_template.format(context=context, input=target_query)

        # LLM回答生成
        start_time = time.time()
        response = llm.invoke(prompt)
        generation_time = time.time() - start_time

        answer = response.content

        print(f"生成時間: {generation_time:.3f}秒")
        print(f"回答文字数: {len(answer)}文字")
        print(f"\n🤖 LLM回答:")
        print("-" * 30)
        print(answer)
        print("-" * 30)

        # 回答品質評価
        answer_lower = answer.lower()
        answer_keywords = sum(1 for keyword in target_keywords if keyword in answer_lower)

        # 具体性チェック
        specific_indicators = ['時間', '場所', '日時', '曜日', '月', '日', '時', '分']
        specificity_score = sum(1 for indicator in specific_indicators if indicator in answer)

        # 有用性評価
        helpful_phrases = ['予定', 'スケジュール', '確認', '詳細', '情報']
        helpfulness_score = sum(1 for phrase in helpful_phrases if phrase in answer)

        print(f"\n📊 回答品質評価:")
        print(f"  キーワード一致: {answer_keywords}/{len(target_keywords)} ({(answer_keywords/len(target_keywords))*100:.1f}%)")
        print(f"  具体性スコア: {specificity_score}/8 ({(specificity_score/8)*100:.1f}%)")
        print(f"  有用性スコア: {helpfulness_score}/5 ({(helpfulness_score/5)*100:.1f}%)")

        return {
            "answer": answer,
            "generation_time": generation_time,
            "answer_length": len(answer),
            "keyword_matches": answer_keywords,
            "specificity_score": specificity_score,
            "helpfulness_score": helpfulness_score
        }

    # 各検索方法でのLLM回答生成
    basic_llm = generate_llm_response(basic_results, "1: 基本検索")
    smart_llm = generate_llm_response(smart_results, "2: スマート検索")
    context_llm = generate_llm_response(context_results, "3: コンテキスト検索")

    print("\n" + "=" * 60)
    print("📈 STEP 3: 総合評価と比較分析")
    print("=" * 60)

    # 総合評価
    print("\n🏆 3-1. 検索方法別総合評価")
    print("-" * 40)

    methods = [
        ("基本検索", basic_analysis, basic_llm, basic_time),
        ("スマート検索", smart_analysis, smart_llm, smart_time),
        ("コンテキスト検索", context_analysis, context_llm, context_time)
    ]

    best_scores = {"relevance": 0, "keywords": 0, "specificity": 0, "helpfulness": 0}

    for method_name, search_analysis, llm_result, search_time in methods:
        print(f"\n{method_name}:")
        print(f"  🔍 検索性能:")
        print(f"    - 検索時間: {search_time:.3f}秒")
        print(f"    - 結果件数: {search_analysis['total_results']}件")
        print(f"    - 関連性: {search_analysis['relevance_score']:.1f}%")

        print(f"  🤖 LLM回答品質:")
        print(f"    - 生成時間: {llm_result['generation_time']:.3f}秒")
        print(f"    - キーワード一致: {llm_result['keyword_matches']}/{len(target_keywords)}")
        print(f"    - 具体性: {llm_result['specificity_score']}/8")
        print(f"    - 有用性: {llm_result['helpfulness_score']}/5")

        # ベストスコア更新
        if search_analysis['relevance_score'] > best_scores["relevance"]:
            best_scores["relevance"] = search_analysis['relevance_score']
        if llm_result['keyword_matches'] > best_scores["keywords"]:
            best_scores["keywords"] = llm_result['keyword_matches']
        if llm_result['specificity_score'] > best_scores["specificity"]:
            best_scores["specificity"] = llm_result['specificity_score']
        if llm_result['helpfulness_score'] > best_scores["helpfulness"]:
            best_scores["helpfulness"] = llm_result['helpfulness_score']

    # 推奨方法の決定
    print(f"\n🥇 3-2. 推奨方法と改善提案")
    print("-" * 40)

    # 総合スコア計算
    method_scores = []
    for method_name, search_analysis, llm_result, search_time in methods:
        # 正規化スコア計算（0-100）
        relevance_norm = (search_analysis['relevance_score'] / best_scores["relevance"]) * 100 if best_scores["relevance"] > 0 else 0
        keywords_norm = (llm_result['keyword_matches'] / best_scores["keywords"]) * 100 if best_scores["keywords"] > 0 else 0
        specificity_norm = (llm_result['specificity_score'] / best_scores["specificity"]) * 100 if best_scores["specificity"] > 0 else 0
        helpfulness_norm = (llm_result['helpfulness_score'] / best_scores["helpfulness"]) * 100 if best_scores["helpfulness"] > 0 else 0

        # 重み付き総合スコア
        total_score = (relevance_norm * 0.3 + keywords_norm * 0.25 +
                      specificity_norm * 0.25 + helpfulness_norm * 0.2)

        method_scores.append((method_name, total_score, {
            'relevance': relevance_norm,
            'keywords': keywords_norm,
            'specificity': specificity_norm,
            'helpfulness': helpfulness_norm
        }))

    # スコア順でソート
    method_scores.sort(key=lambda x: x[1], reverse=True)

    print("総合評価ランキング:")
    for i, (method_name, total_score, scores) in enumerate(method_scores, 1):
        print(f"  {i}位. {method_name}: {total_score:.1f}点")
        print(f"      関連性{scores['relevance']:.1f} + キーワード{scores['keywords']:.1f} + 具体性{scores['specificity']:.1f} + 有用性{scores['helpfulness']:.1f}")

    best_method = method_scores[0][0]
    print(f"\n🏆 推奨検索方法: {best_method}")

    # 改善提案
    print(f"\n💡 3-3. 改善提案")
    print("-" * 40)

    if best_scores["relevance"] < 50:
        print("⚠️  検索関連性が低い - データベースに関連情報が不足している可能性")
        print("   推奨: 練習・試合予定の関連データを追加")

    if best_scores["keywords"] < len(target_keywords) * 0.7:
        print("⚠️  キーワード一致率が低い - より関連性の高いコンテキスト検索が必要")
        print("   推奨: 検索アルゴリズムの改良")

    if best_scores["specificity"] < 4:
        print("⚠️  LLM回答の具体性が不足 - より詳細な情報提供が必要")
        print("   推奨: プロンプトテンプレートの改良")

    print(f"\n✅ 評価完了: {datetime.now().strftime('%H:%M:%S')}")

    print("\n" + "=" * 80)
    print("🎯 クエリ評価完了 - 検索精度とLLM回答品質の詳細分析結果")
    print("=" * 80)


if __name__ == "__main__":
    evaluate_query_response()
