"""
uma3.pyに改善された応答システムを統合するための実際の修正パッチ
"""

# uma3.pyのhandle_message関数内の統合システム呼び出し部分を以下のように置き換えてください：

IMPROVED_INTEGRATION_PATCH = '''
                # 統合システムで応答生成（改善版）
                print(f"[ENHANCED] Trying improved response system first...")

                # 1. 改善されたテンプレートシステムを試行
                enhanced_response = None
                try:
                    # ImprovedResponseGeneratorを初期化（必要時のみ）
                    if not hasattr(handle_message, 'improved_generator'):
                        from tests.improved_response_system import ImprovedResponseGenerator
                        db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'conversation_history.db')
                        handle_message.improved_generator = ImprovedResponseGenerator(db_path)
                        print("[ENHANCED] Improved response generator initialized")

                    # 改善された応答生成
                    improved_result = handle_message.improved_generator.generate_improved_response(user_id, text)

                    # 高品質な応答が生成された場合は使用
                    if improved_result.get('quality_score', 0) >= 3.0:
                        enhanced_response = improved_result['response']
                        print(f"[ENHANCED] ✅ High quality response (score: {improved_result['quality_score']:.1f})")

                        # 統合システムの会話履歴に保存
                        try:
                            integrated_conversation_system.history_manager.save_conversation(
                                user_id, text, enhanced_response,
                                metadata={
                                    "source": "enhanced_template",
                                    "quality_score": improved_result['quality_score'],
                                    "template_type": improved_result.get('template_type', 'unknown')
                                }
                            )
                            print(f"[ENHANCED] ✅ Saved enhanced conversation to history")
                        except Exception as save_error:
                            print(f"[WARNING] ❌ Failed to save enhanced conversation: {save_error}")

                    else:
                        print(f"[ENHANCED] ⚠️ Low quality response, trying integrated system (score: {improved_result['quality_score']:.1f})")

                except Exception as e:
                    print(f"[WARNING] Enhanced response generation failed: {e}")

                # 2. 改善システムで高品質な応答が得られた場合はそれを使用
                if enhanced_response:
                    ai_msg = {"answer": enhanced_response}
                    print(f"[ENHANCED] Using enhanced template response")

                else:
                    # 3. 既存の統合システムにフォールバック
                    response_result = integrated_conversation_system.generate_integrated_response(
                        user_id, text, llm
                    )

                    if "error" in response_result:
                        # エラーが発生した場合のフォールバック処理
                        print(f"[ERROR] Integrated system error: {response_result.get('error_message', 'Unknown error')}")

                        # ChromaDB検索フォールバック
                        results = chroma_improver.schedule_aware_search(
                            text, k=6, score_threshold=0.5
                        )

                        if results:
                            context = "\\n".join([doc.page_content for doc in results])

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
                                context=context, input=text
                            )
                            response = llm.invoke(formatted_prompt)
                            ai_msg = {"answer": response.content}
                        else:
                            ai_msg = {"answer": "申し訳ございません。関連する情報が見つかりませんでした。"}
                    else:
                        # 正常応答の場合
                        ai_msg = {"answer": response_result["response"]}

                        # 応答情報をログ出力
                        context_info = response_result.get("context_used", {})
                        print(f"[INTEGRATED] Response generated successfully")
                        print(f"[INTEGRATED] ChromaDB results: {context_info.get('chroma_results', 0)}")
                        print(f"[INTEGRATED] Conversation history: {context_info.get('conversation_history', 0)}")
                        print(f"[INTEGRATED] Response type: {response_result.get('response_type', 'unknown')}")

                        # ユーザプロフィール情報をログ出力
                        user_profile = context_info.get('user_profile', {})
                        if user_profile:
                            print(f"[PROFILE] User conversation count: {user_profile.get('conversation_count', 0)}")
                            if user_profile.get('interests'):
                                print(f"[PROFILE] User interests: {user_profile['interests'][:3]}")

                        # 統合システムで生成した会話を履歴に保存（改善システムでない場合のみ）
                        if not enhanced_response:
                            try:
                                integrated_conversation_system.history_manager.save_conversation(
                                    user_id, text, ai_msg["answer"],
                                    metadata={"source": "line_mention", "response_type": response_result.get('response_type', 'integrated')}
                                )
                                print(f"[HISTORY] ✅ Saved conversation to history (user: {user_id[:10]}...)")
                            except Exception as save_error:
                                print(f"[WARNING] ❌ Failed to save conversation to history: {save_error}")
                                traceback.print_exc()
'''

def apply_enhanced_integration():
    """uma3.pyに改善システムを統合する手順を表示"""

    print("🔧 uma3.py 改善システム統合手順")
    print("=" * 60)

    print("📋 修正が必要な箇所:")
    print("1. handle_message関数内の統合システム呼び出し部分")
    print("   (約468行目～540行目付近)")
    print()

    print("🔍 置き換え対象コード:")
    print("   # 統合システムで応答生成")
    print("   response_result = integrated_conversation_system.generate_integrated_response(")
    print("       user_id, text, llm")
    print("   )")
    print()

    print("🆕 新しいコード:")
    print("   上記のIMPROVED_INTEGRATION_PATCHの内容で置き換え")
    print()

    print("✅ 期待される改善:")
    print("   - 高品質テンプレート応答の優先使用")
    print("   - 自然な日本語応答")
    print("   - ユーザー名のパーソナライズ")
    print("   - 品質スコア3.0以上の応答優先")
    print("   - 既存システムへの安全なフォールバック")

    return IMPROVED_INTEGRATION_PATCH

def main():
    """統合パッチの表示"""
    patch_code = apply_enhanced_integration()

    print("\n" + "="*80)
    print("📄 INTEGRATION PATCH CODE:")
    print("="*80)
    print(patch_code)
    print("="*80)

if __name__ == "__main__":
    main()
