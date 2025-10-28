"""
Uma3 RAG + Agent統合システム
LangChain + LlamaIndex を組み合わせたRAG + Agent型AI
既存のuma3.pyとの統合インターフェース
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from uma3_agent import Uma3Agent
from uma3_custom_tools import (
    calculate_days_until_event,
    create_custom_tools,
    format_schedule_response,
)

# 新しいRAG + Agentシステムのインポート
from uma3_rag_engine import Uma3RAGEngine


class Uma3IntegratedSystem:
    """
    统合RAG + Agent システム
    既存システムとの互換性を保ちながら、新機能を提供
    """

    def __init__(
        self,
        persist_directory: str = "Lesson25/uma3soft-app/db/chroma_store",
        openai_api_key: Optional[str] = None,
        enable_agent: bool = True,
        verbose: bool = True,
    ):
        """
        統合システムの初期化

        Args:
            persist_directory: ChromaDBの保存ディレクトリ
            openai_api_key: OpenAI APIキー
            enable_agent: Agent機能を有効にするか
            verbose: 詳細ログ出力
        """
        self.persist_directory = persist_directory
        self.enable_agent = enable_agent
        self.verbose = verbose

        print("🚀 Initializing Uma3 Integrated RAG + Agent System...")

        try:
            # RAG エンジン初期化
            self.rag_engine = Uma3RAGEngine(
                persist_directory=persist_directory, openai_api_key=openai_api_key
            )
            print("✅ RAG Engine initialized")

            # Agent システム初期化
            if enable_agent:
                self.agent = Uma3Agent(
                    rag_engine=self.rag_engine,
                    openai_api_key=openai_api_key,
                    verbose=verbose,
                )

                # カスタムツール追加
                custom_tools = create_custom_tools(self.rag_engine)
                for tool in custom_tools:
                    self.agent.add_custom_tool(tool)

                # 関数型ツール追加
                self.agent.add_custom_tool(format_schedule_response)
                self.agent.add_custom_tool(calculate_days_until_event)

                print("✅ Agent System initialized with custom tools")
            else:
                self.agent = None
                print("⚠️ Agent System disabled")

            self.initialized = True

        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            self.initialized = False
            raise

    def process_message(
        self, message: str, user_id: str = "unknown", use_agent: bool = True
    ) -> Dict[str, Any]:
        """
        メッセージ処理のメイン関数
        既存システムとの互換性を保持

        Args:
            message: ユーザーメッセージ
            user_id: ユーザーID
            use_agent: Agent機能を使用するか

        Returns:
            処理結果の辞書
        """
        if not self.initialized:
            return {
                "answer": "システムが初期化されていません。",
                "success": False,
                "method": "error",
            }

        try:
            print(f"[INTEGRATED] Processing message: '{message}' from user: {user_id}")

            # Agent機能が有効かつ使用を指定された場合
            if self.enable_agent and use_agent and self.agent:
                print("[INTEGRATED] Using Agent System")
                result = self.agent.process_query(message, user_id)
                result["method"] = "agent"
                return result

            # フォールバック: 従来のRAG検索
            else:
                print("[INTEGRATED] Using fallback RAG search")
                return self._fallback_rag_search(message, user_id)

        except Exception as e:
            print(f"[ERROR] Message processing failed: {e}")
            return {
                "answer": f"メッセージ処理中にエラーが発生しました: {e}",
                "success": False,
                "method": "error",
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
            }

    def _fallback_rag_search(self, message: str, user_id: str) -> Dict[str, Any]:
        """
        フォールバック用のRAG検索
        従来システムとの互換性を保持
        """
        try:
            # ハイブリッド検索実行
            results = self.rag_engine.hybrid_search(
                message, k=5, score_threshold=0.3, include_schedule_data=True
            )

            if results:
                # コンテキスト構築
                context_parts = []
                for i, doc in enumerate(results, 1):
                    metadata_info = ""
                    if doc.metadata:
                        user = doc.metadata.get("user", "不明")
                        timestamp = doc.metadata.get("timestamp", "日時不明")
                        metadata_info = f" (発言者: {user}, 日時: {timestamp})"

                    context_parts.append(f"{doc.text[:200]}{metadata_info}")

                context = "\\n\\n".join(context_parts)

                # 簡易応答生成（LLMを使用せず）
                answer = self._generate_simple_response(message, context)

                return {
                    "answer": answer,
                    "context": context,
                    "results_count": len(results),
                    "success": True,
                    "method": "rag_fallback",
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                return {
                    "answer": "関連する情報が見つかりませんでした。",
                    "context": "",
                    "results_count": 0,
                    "success": True,
                    "method": "rag_fallback",
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            return {
                "answer": f"検索中にエラーが発生しました: {e}",
                "success": False,
                "method": "rag_fallback",
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
            }

    def _generate_simple_response(self, query: str, context: str) -> str:
        """
        簡易応答生成（LLMを使用しない場合）
        """
        if not context:
            return "申し訳ありませんが、関連する情報が見つかりませんでした。"

        # キーワードベースの簡易応答
        query_lower = query.lower()

        if any(keyword in query_lower for keyword in ["予定", "スケジュール", "いつ"]):
            return f"📅 スケジュール情報をお調べしました:\\n\\n{context}"
        elif any(keyword in query_lower for keyword in ["練習", "大会", "試合"]):
            return f"🏃‍♂️ 関連する活動情報:\\n\\n{context}"
        elif any(keyword in query_lower for keyword in ["メンバー", "選手", "チーム"]):
            return f"👥 チーム関連情報:\\n\\n{context}"
        else:
            return f"💬 関連する会話履歴:\\n\\n{context}"

    def get_system_status(self) -> Dict[str, Any]:
        """システム状態の取得"""
        status = {
            "initialized": self.initialized,
            "rag_engine_available": self.rag_engine is not None,
            "agent_enabled": self.enable_agent,
            "agent_available": self.agent is not None,
            "persist_directory": self.persist_directory,
        }

        if self.rag_engine:
            status["rag_analytics"] = self.rag_engine.get_analytics("system_status")

        if self.agent:
            status["agent_analytics"] = self.agent.get_analytics()

        return status

    def search_hybrid(self, query: str, **kwargs) -> List[Any]:
        """
        ハイブリッド検索の直接実行
        既存システムとの互換性
        """
        if not self.rag_engine:
            return []

        return self.rag_engine.hybrid_search(query, **kwargs)

    def add_message_to_memory(self, user_message: str, ai_response: str):
        """
        会話履歴への追加
        """
        if self.agent:
            self.agent.memory.chat_memory.add_user_message(user_message)
            self.agent.memory.chat_memory.add_ai_message(ai_response)

    def clear_conversation_memory(self):
        """会話履歴のクリア"""
        if self.agent:
            self.agent.clear_memory()

    def is_agent_available(self) -> bool:
        """Agent機能の利用可否チェック"""
        return self.enable_agent and self.agent is not None and self.initialized


def create_integrated_system(
    persist_directory: str = "Lesson25/uma3soft-app/db/chroma_store",
    enable_agent: bool = True,
    verbose: bool = True,
) -> Uma3IntegratedSystem:
    """
    統合システムの作成
    既存システムから簡単に呼び出せるファクトリ関数
    """
    try:
        return Uma3IntegratedSystem(
            persist_directory=persist_directory,
            enable_agent=enable_agent,
            verbose=verbose,
        )
    except Exception as e:
        print(f"❌ Failed to create integrated system: {e}")
        raise


def test_integrated_system():
    """統合システムのテスト"""
    try:
        print("🧪 Testing Uma3 Integrated System...")

        # システム初期化
        system = create_integrated_system(verbose=True)

        # システム状態確認
        status = system.get_system_status()
        print(f"\\n📊 System Status:")
        for key, value in status.items():
            if not key.endswith("_analytics"):
                print(f"  {key}: {value}")

        # テストクエリ
        test_queries = [
            "今週の予定を教えて",
            "羽村ライオンズの練習はいつですか？",
            "チームメンバーは誰ですか？",
            "11月3日まで何日ありますか？",
        ]

        for i, query in enumerate(test_queries, 1):
            print(f"\\n📝 Test {i}: '{query}'")

            # Agent使用
            result_agent = system.process_message(
                query, f"test_user_{i}", use_agent=True
            )
            print(
                f"  Agent: {result_agent['success']} - {result_agent['answer'][:100]}..."
            )

            # RAGフォールバック
            result_rag = system.process_message(
                query, f"test_user_{i}", use_agent=False
            )
            print(f"  RAG: {result_rag['success']} - {result_rag['answer'][:100]}...")

        print("\\n✅ Integrated system test completed")

    except Exception as e:
        print(f"❌ Integrated system test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_integrated_system()
