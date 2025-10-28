"""
uma3.py enhancement integration code
Generated on: 2025-10-28 00:43:11

This file contains the integration code to enhance uma3.py with improved response system.
Copy the relevant parts to uma3.py manually after careful review.
"""


# === 改善された応答システム統合 ===
# improved_response_systemからImprovedResponseGeneratorをインポート
import sys
import os
tests_path = os.path.join(os.path.dirname(__file__), '..', 'tests')
sys.path.insert(0, tests_path)

try:
    from improved_response_system import ImprovedResponseGenerator
    improved_response_generator = ImprovedResponseGenerator(
        os.path.join(os.path.dirname(__file__), '..', 'db', 'conversation_history.db')
    )
    print("[ENHANCED] Improved response generator loaded successfully")
except Exception as e:
    print(f"[WARNING] Could not load improved response generator: {e}")
    improved_response_generator = None

def generate_enhanced_line_response(user_id: str, user_message: str, llm) -> Dict:
    """LINE Bot用の拡張応答生成"""

    # 1. 改善された応答システムを試行
    if improved_response_generator:
        try:
            improved_result = improved_response_generator.generate_improved_response(user_id, user_message)

            # 高品質な応答が生成された場合
            if improved_result.get('quality_score', 0) >= 3.0:
                print(f"[ENHANCED] High quality response generated (score: {improved_result['quality_score']:.1f})")
                return {
                    'response': improved_result['response'],
                    'response_type': 'enhanced_template',
                    'quality_score': improved_result['quality_score'],
                    'source': 'improved_system'
                }
            else:
                print(f"[ENHANCED] Low quality response, trying integrated system (score: {improved_result['quality_score']:.1f})")

        except Exception as e:
            print(f"[WARNING] Improved response generation failed: {e}")

    # 2. 統合システムへのフォールバック
    try:
        integrated_result = integrated_conversation_system.generate_integrated_response(
            user_id, user_message, llm
        )

        if "error" not in integrated_result:
            return {
                'response': integrated_result['response'],
                'response_type': 'integrated_system',
                'context_used': integrated_result.get('context_used', {}),
                'source': 'integrated_system'
            }
        else:
            print(f"[WARNING] Integrated system error: {integrated_result.get('error_message', 'Unknown')}")

    except Exception as e:
        print(f"[WARNING] Integrated system failed: {e}")

    # 3. 基本ChromaDB検索へのフォールバック
    try:
        results = chroma_improver.schedule_aware_search(user_message, k=6, score_threshold=0.5)

        if results:
            context = "\n".join([doc.page_content for doc in results])

            prompt_template = ChatPromptTemplate.from_messages([
                (
                    "system",
                    """あなたは優秀なアシスタントです。以下の関連情報を参考にして、
                    ユーザーの質問に自然で親しみやすく答えてください。
                    回答時はスマートフォンで読みやすいように、適度に改行を入れてください。

                    ---
                    {context}
                    ---""",
                ),
                ("human", "{input}"),
            ])

            formatted_prompt = prompt_template.format_messages(
                context=context, input=user_message
            )
            response = llm.invoke(formatted_prompt)

            return {
                'response': response.content,
                'response_type': 'chroma_fallback',
                'source': 'chroma_search'
            }
    except Exception as e:
        print(f"[WARNING] ChromaDB fallback failed: {e}")

    # 4. 最終フォールバック
    return {
        'response': "申し訳ございません。少し時間をおいて、もう一度お試しください。",
        'response_type': 'final_fallback',
        'source': 'fallback'
    }

