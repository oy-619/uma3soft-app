"""
ChromaDBと統合した会話履歴ベース応答システム
既存のuma3_chroma_improverと新しい会話履歴管理を統合
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

from conversation_history_manager import ConversationHistoryManager, ConversationContextGenerator
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from uma3_chroma_improver import Uma3ChromaDBImprover


class IntegratedConversationSystem:
    """ChromaDBと会話履歴を統合した応答システム"""

    def __init__(self,
                 chroma_persist_directory: str,
                 conversation_db_path: str = "conversation_history.db",
                 embeddings_model: HuggingFaceEmbeddings = None):

        self.chroma_persist_directory = chroma_persist_directory
        self.conversation_db_path = conversation_db_path

        # 埋め込みモデルの初期化
        self.embedding_model = embeddings_model or HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # ChromaDBベクトルデータベースの初期化
        self.vector_db = Chroma(
            persist_directory=chroma_persist_directory,
            embedding_function=self.embedding_model
        )

        # ChromaDB精度向上機能の初期化
        self.chroma_improver = Uma3ChromaDBImprover(self.vector_db)

        # 会話履歴管理の初期化
        self.history_manager = ConversationHistoryManager(conversation_db_path)
        self.context_generator = ConversationContextGenerator(self.history_manager)

        print(f"[INIT] Integrated conversation system initialized")
        print(f"[INIT] ChromaDB: {chroma_persist_directory}")
        print(f"[INIT] ConversationDB: {conversation_db_path}")

    def generate_integrated_response(self, user_id: str, message: str,
                                   llm: ChatOpenAI = None) -> Dict:
        """統合された応答生成

        Args:
            user_id: ユーザID
            message: ユーザからのメッセージ
            llm: 使用するLLMモデル

        Returns:
            Dict: 応答情報（応答テキスト、使用されたコンテキスト、統計など）
        """
        if llm is None:
            llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)

        # 1. ChromaDBから関連情報を検索
        chroma_results = self.chroma_improver.schedule_aware_search(
            message, k=5, score_threshold=0.5
        )

        # 2. 会話履歴から関連情報を取得
        user_profile = self.history_manager.get_user_profile(user_id)
        recent_conversations = self.history_manager.get_recent_conversations(
            user_id, limit=3
        )
        relevant_conversations = self.history_manager.search_conversations(
            user_id, message, limit=2
        )

        # 3. 統合プロンプトの構築
        context_parts = []

        # ChromaDBからの情報
        if chroma_results:
            context_parts.append("**データベースから関連情報:**")
            for i, doc in enumerate(chroma_results[:3]):
                context_parts.append(f"{i+1}. {doc.page_content[:200]}...")

        # ユーザプロフィール情報
        if user_profile["interests"]:
            interests_text = "、".join(user_profile["interests"][:3])
            context_parts.append(f"\n**{user_id}さんの興味・関心:** {interests_text}")

        if user_profile["conversation_count"] > 0:
            context_parts.append(f"**これまでの会話回数:** {user_profile['conversation_count']}回")

        # 最近の会話履歴
        if recent_conversations:
            context_parts.append("\n**最近の会話履歴:**")
            for human_msg, ai_msg, timestamp in recent_conversations[:2]:
                time_str = timestamp.strftime("%m/%d %H:%M")
                context_parts.append(f"[{time_str}] {user_id}: {human_msg[:80]}...")
                context_parts.append(f"[{time_str}] Bot: {ai_msg[:80]}...")

        # 関連する過去の会話
        if relevant_conversations:
            context_parts.append("\n**関連する過去の会話:**")
            for conv in relevant_conversations:
                if conv["message_type"] == "human":
                    context_parts.append(f"過去の質問: {conv['content'][:100]}...")

        # 統合プロンプトテンプレート
        context_text = "\n".join(context_parts)

        # 今週の予定に関する質問かチェック
        is_weekly_schedule_query = any(
            keyword in message for keyword in ["今週", "週", "今週の予定", "週の予定", "スケジュール"]
        )

        if is_weekly_schedule_query:
            current_time = datetime.now()
            current_date_str = current_time.strftime("%Y年%m月%d日 %H:%M")

            prompt_template = ChatPromptTemplate.from_messages([
                (
                    "system",
                    f"""あなたは優秀なスケジュール管理アシスタントです。
                    現在時刻は{current_date_str}です。

                    以下の情報を参考にして、ユーザの質問に個人的で親しみやすい応答をしてください：

                    {context_text}

                    回答時の注意点:
                    - ユーザの過去の会話や興味を踏まえた個人的な応答
                    - 長期的な関係性を意識した自然な会話継続
                    - スマートフォンで読みやすいよう適度に改行
                    - 必要に応じて過去の会話を参照した発言
                    - 予定がある場合は日付・時間・場所を明確に記載"""
                ),
                ("human", "{input}")
            ])
        else:
            prompt_template = ChatPromptTemplate.from_messages([
                (
                    "system",
                    f"""あなたは優秀なAIアシスタントです。

                    以下の情報を参考にして、ユーザの質問に個人的で親しみやすい応答をしてください：

                    {context_text}

                    回答時の注意点:
                    - ユーザの過去の発言や興味を踏まえた個人的な応答
                    - 長期的な関係性を意識した自然な会話継続
                    - スマートフォンで読みやすいよう適度に改行
                    - 必要に応じて過去の会話を参照した発言
                    - 重要な情報は箇条書きで整理"""
                ),
                ("human", "{input}")
            ])

        # 応答生成
        try:
            formatted_prompt = prompt_template.format_messages(input=message)
            response = llm.invoke(formatted_prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)

            # 応答を会話履歴に保存
            self.history_manager.save_conversation(
                user_id, message, response_text,
                metadata={
                    "chroma_results_count": len(chroma_results),
                    "context_quality": "high" if len(context_parts) > 3 else "medium",
                    "response_type": "weekly_schedule" if is_weekly_schedule_query else "general"
                }
            )

            # 応答情報を返す
            return {
                "response": response_text,
                "context_used": {
                    "chroma_results": len(chroma_results),
                    "conversation_history": len(recent_conversations),
                    "relevant_conversations": len(relevant_conversations),
                    "user_profile": user_profile
                },
                "prompt_length": len(context_text),
                "response_type": "weekly_schedule" if is_weekly_schedule_query else "general"
            }

        except Exception as e:
            error_response = f"申し訳ございません。応答の生成中にエラーが発生しました: {str(e)}"
            print(f"[ERROR] Response generation failed: {e}")

            # エラーも履歴に保存
            self.history_manager.save_conversation(
                user_id, message, error_response,
                metadata={"error": True, "error_message": str(e)}
            )

            return {
                "response": error_response,
                "context_used": {},
                "error": True,
                "error_message": str(e)
            }

    def get_user_conversation_summary(self, user_id: str) -> Dict:
        """ユーザの会話サマリーを取得"""
        profile = self.history_manager.get_user_profile(user_id)
        stats = self.history_manager.get_conversation_statistics(user_id)
        recent_conversations = self.history_manager.get_recent_conversations(user_id, limit=5)

        return {
            "user_id": user_id,
            "profile": profile,
            "statistics": stats,
            "recent_conversations": recent_conversations,
            "summary_generated_at": datetime.now().isoformat()
        }

    def search_user_conversations(self, user_id: str, query: str, limit: int = 10) -> List[Dict]:
        """ユーザの会話履歴を検索"""
        return self.history_manager.search_conversations(user_id, query, limit)

    def clear_user_history(self, user_id: str, session_id: str = "default") -> bool:
        """ユーザの会話履歴をクリア"""
        try:
            user_history = self.history_manager.get_user_history(user_id, session_id)
            user_history.clear()
            print(f"[CLEAR] Cleared conversation history for user: {user_id}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to clear history for user {user_id}: {e}")
            return False

    def export_user_conversations(self, user_id: str, output_file: str) -> bool:
        """ユーザの会話履歴をエクスポート"""
        try:
            import json

            summary = self.get_user_conversation_summary(user_id)
            all_conversations = self.history_manager.search_conversations(user_id, "", limit=1000)

            export_data = {
                "user_summary": summary,
                "all_conversations": all_conversations,
                "export_timestamp": datetime.now().isoformat()
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            print(f"[EXPORT] User conversations exported to: {output_file}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to export conversations for user {user_id}: {e}")
            return False


# 使用例とテスト
if __name__ == "__main__":
    # 設定
    chroma_persist_dir = "Lesson25/uma3soft-app/db/chroma_store"
    conversation_db_path = "conversation_history.db"

    # 統合システムの初期化
    integrated_system = IntegratedConversationSystem(
        chroma_persist_directory=chroma_persist_dir,
        conversation_db_path=conversation_db_path
    )

    # テストユーザ
    test_user_id = "integration_test_user"

    # LLMの初期化（OpenAI APIキーが設定されている場合）
    if os.getenv("OPENAI_API_KEY"):
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)

        # テストメッセージ
        test_messages = [
            "こんにちは、野球に興味があります",
            "今週の予定を教えて",
            "ジャイアンツの試合はいつですか？"
        ]

        print("=" * 50)
        print("統合システムテスト")
        print("=" * 50)

        for i, message in enumerate(test_messages, 1):
            print(f"\n{i}. テストメッセージ: {message}")

            result = integrated_system.generate_integrated_response(
                test_user_id, message, llm
            )

            print(f"応答: {result['response'][:150]}...")
            print(f"コンテキスト: {result['context_used']}")
            print("-" * 30)

        # ユーザサマリーの確認
        summary = integrated_system.get_user_conversation_summary(test_user_id)
        print(f"\nユーザサマリー:")
        print(f"会話回数: {summary['statistics']['total_messages']}")
        print(f"興味: {summary['profile']['interests']}")

    else:
        print("OPENAI_API_KEYが設定されていません。統合システムのテストをスキップします。")
