"""
LangChain Agent フレームワーク
ReAct パターン（推論→行動→観察）を使用した高度なAgent システム
"""

import os
import re
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

try:
    from langchain.agents import AgentExecutor, create_react_agent
    from langchain.memory import ConversationBufferWindowMemory
    from langchain.tools import BaseTool, tool
    from langchain_core.callbacks import BaseCallbackHandler
    from langchain_core.messages import AIMessage, HumanMessage
    from langchain_core.prompts import PromptTemplate
    from langchain_openai import ChatOpenAI
    from pydantic import BaseModel, Field
except ImportError as e:
    print(f"⚠️ LangChain import error: {e}")
    print("Please install: pip install langchain langchain-openai")
    import sys

    sys.exit(1)

from uma3_rag_engine import Uma3RAGEngine


class Uma3Agent:
    """
    LangChain Agent システム

    機能:
    - ReAct パターンによる推論・行動・観察サイクル
    - カスタムツール統合
    - 会話メモリ管理
    - 動的プロンプト生成
    """

    def __init__(
        self,
        rag_engine: Uma3RAGEngine,
        openai_api_key: Optional[str] = None,
        model_name: str = "gpt-3.5-turbo",
        memory_k: int = 10,
        max_iterations: int = 5,
        verbose: bool = True,
    ):
        """
        Agent の初期化

        Args:
            rag_engine: RAG エンジンのインスタンス
            openai_api_key: OpenAI APIキー
            model_name: LLMモデル名
            memory_k: 会話履歴の保持数
            max_iterations: 最大推論ループ回数
            verbose: 詳細ログ出力
        """
        self.rag_engine = rag_engine
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.verbose = verbose

        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")

        # LLM初期化
        self.llm = ChatOpenAI(
            model=model_name, api_key=self.openai_api_key, temperature=0.3
        )

        # メモリ初期化
        self.memory = ConversationBufferWindowMemory(
            k=memory_k, return_messages=True, memory_key="chat_history"
        )

        # ツール初期化
        self.tools = self._create_tools()

        # ReAct プロンプトテンプレート
        self.react_prompt = self._create_react_prompt()

        # Agent 作成
        self.agent = create_react_agent(
            llm=self.llm, tools=self.tools, prompt=self.react_prompt
        )

        # Agent executor 作成
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            max_iterations=max_iterations,
            verbose=verbose,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )

        print(f"✅ Uma3Agent initialized with {len(self.tools)} tools")

    def _create_tools(self) -> List[BaseTool]:
        """カスタムツールの作成"""
        tools = []

        # RAG検索ツール
        @tool
        def search_conversation_history(query: str) -> str:
            """
            過去の会話履歴を検索します。
            スケジュール、予定、過去の発言などを調べる際に使用してください。

            Args:
                query: 検索したい内容のクエリ

            Returns:
                検索結果のテキスト
            """
            try:
                results = self.rag_engine.hybrid_search(query, k=5)
                if not results:
                    return "関連する会話履歴が見つかりませんでした。"

                context_parts = []
                for i, doc in enumerate(results, 1):
                    metadata_info = ""
                    if doc.metadata:
                        user = doc.metadata.get("user", "不明")
                        timestamp = doc.metadata.get("timestamp", "日時不明")
                        metadata_info = f" (発言者: {user}, 日時: {timestamp})"

                    context_parts.append(f"{i}. {doc.text[:200]}...{metadata_info}")

                return "\\n\\n".join(context_parts)

            except Exception as e:
                return f"検索中にエラーが発生しました: {e}"

        # スケジュール検索ツール
        @tool
        def search_schedule(query: str) -> str:
            """
            スケジュールや予定に特化した検索を行います。
            大会、練習、試合などの予定を調べる際に使用してください。

            Args:
                query: スケジュール検索クエリ

            Returns:
                スケジュール情報
            """
            try:
                results = self.rag_engine.hybrid_search(
                    query, k=3, include_schedule_data=True
                )

                if not results:
                    return "該当するスケジュールが見つかりませんでした。"

                schedule_info = []
                for doc in results:
                    if "[ノート]" in doc.text:
                        # 日付情報を抽出
                        date_matches = re.findall(r"(\\d{1,2})月(\\d{1,2})日", doc.text)
                        dates = [f"{m[0]}月{m[1]}日" for m in date_matches]

                        schedule_text = doc.text.replace("[ノート]", "").strip()
                        if dates:
                            schedule_info.append(
                                f"📅 {', '.join(dates)}: {schedule_text}"
                            )
                        else:
                            schedule_info.append(f"📋 {schedule_text}")
                    else:
                        schedule_info.append(doc.text[:150])

                return "\\n\\n".join(schedule_info)

            except Exception as e:
                return f"スケジュール検索中にエラーが発生しました: {e}"

        # 今日・明日の予定ツール
        @tool
        def get_today_tomorrow_schedule() -> str:
            """
            今日と明日の予定を取得します。

            Returns:
                今日・明日の予定情報
            """
            try:
                today = datetime.now()
                tomorrow = today + timedelta(days=1)

                today_str = f"{today.month}月{today.day}日"
                tomorrow_str = f"{tomorrow.month}月{tomorrow.day}日"

                query = f"{today_str} {tomorrow_str} 予定 スケジュール"
                results = self.rag_engine.hybrid_search(query, k=5)

                today_events = []
                tomorrow_events = []

                for doc in results:
                    if today_str in doc.text:
                        today_events.append(doc.text)
                    elif tomorrow_str in doc.text:
                        tomorrow_events.append(doc.text)

                response = []
                if today_events:
                    response.append(
                        f"📅 今日({today_str})の予定:\\n" + "\\n".join(today_events)
                    )
                else:
                    response.append(f"📅 今日({today_str})の予定: 特に予定はありません")

                if tomorrow_events:
                    response.append(
                        f"📅 明日({tomorrow_str})の予定:\\n"
                        + "\\n".join(tomorrow_events)
                    )
                else:
                    response.append(
                        f"📅 明日({tomorrow_str})の予定: 特に予定はありません"
                    )

                return "\\n\\n".join(response)

            except Exception as e:
                return f"予定取得中にエラーが発生しました: {e}"

        # 時間計算ツール
        @tool
        def calculate_time_difference(target_date: str) -> str:
            """
            指定された日付までの時間差を計算します。

            Args:
                target_date: 対象日付（例: "11月3日", "2024/11/03"）

            Returns:
                時間差の情報
            """
            try:
                today = datetime.now()

                # 日付パースの試行
                target_dt = None

                # MM月DD日 形式
                month_day_match = re.match(r"(\\d{1,2})月(\\d{1,2})日", target_date)
                if month_day_match:
                    month = int(month_day_match.group(1))
                    day = int(month_day_match.group(2))
                    year = today.year

                    # 過去の日付の場合は来年を想定
                    target_dt = datetime(year, month, day)
                    if target_dt < today:
                        target_dt = datetime(year + 1, month, day)

                if target_dt:
                    diff = target_dt - today
                    days = diff.days

                    if days == 0:
                        return f"{target_date}は今日です！"
                    elif days == 1:
                        return f"{target_date}は明日です！"
                    elif days > 0:
                        weeks = days // 7
                        remaining_days = days % 7

                        if weeks > 0:
                            return f"{target_date}まであと{weeks}週間{remaining_days}日（{days}日）です"
                        else:
                            return f"{target_date}まであと{days}日です"
                    else:
                        return f"{target_date}は{abs(days)}日前でした"
                else:
                    return f"日付の解析ができませんでした: {target_date}"

            except Exception as e:
                return f"時間計算中にエラーが発生しました: {e}"

        # ツールリストに追加
        tools.extend(
            [
                search_conversation_history,
                search_schedule,
                get_today_tomorrow_schedule,
                calculate_time_difference,
            ]
        )

        return tools

    def _create_react_prompt(self) -> PromptTemplate:
        """ReAct プロンプトテンプレートの作成"""
        template = """
あなたは優秀なアシスタントです。ユーザーの質問に対して、利用可能なツールを使って情報を収集し、的確な回答を提供してください。

以下のツールが利用できます:
{tools}

次の形式で思考してください:

Question: 回答すべき質問
Thought: 何をすべきか考えてください
Action: 実行するアクション（ツール名）
Action Input: アクションへの入力
Observation: アクションの結果
... (必要に応じてThought/Action/Action Input/Observationを繰り返し)
Thought: 最終的な答えがわかりました
Final Answer: ユーザーへの最終回答

重要な点:
- スケジュールや予定に関する質問では、search_scheduleツールを優先的に使用してください
- 過去の会話や発言に関する質問では、search_conversation_historyツールを使用してください
- 今日・明日の予定については、get_today_tomorrow_scheduleツールを使用してください
- 日付の計算が必要な場合は、calculate_time_differenceツールを使用してください
- 複数のツールを組み合わせて、より包括的な情報を提供してください
- 回答は読みやすく、スマートフォンでも見やすい形式で提供してください

{agent_scratchpad}

Question: {input}
"""

        return PromptTemplate(
            template=template,
            input_variables=["input", "agent_scratchpad"],
            partial_variables={
                "tools": "\\n".join(
                    [f"{tool.name}: {tool.description}" for tool in self.tools]
                ),
                "tool_names": ", ".join([tool.name for tool in self.tools]),
            },
        )

    def process_query(self, query: str, user_id: str = "unknown") -> Dict[str, Any]:
        """
        クエリを処理して回答を生成

        Args:
            query: ユーザーのクエリ
            user_id: ユーザーID

        Returns:
            処理結果の辞書
        """
        try:
            print(f"[AGENT] Processing query: '{query}' from user: {user_id}")

            # Agentでクエリを実行
            result = self.agent_executor.invoke(
                {"input": query, "chat_history": self.memory.chat_memory.messages}
            )

            # 結果の処理
            answer = result.get(
                "output", "申し訳ありませんが、回答を生成できませんでした。"
            )
            intermediate_steps = result.get("intermediate_steps", [])

            # メモリに会話を追加
            self.memory.chat_memory.add_user_message(query)
            self.memory.chat_memory.add_ai_message(answer)

            # ログ出力
            if self.verbose:
                print(f"[AGENT] Generated answer: {answer[:100]}...")
                print(f"[AGENT] Used {len(intermediate_steps)} intermediate steps")

            return {
                "answer": answer,
                "intermediate_steps": intermediate_steps,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "success": True,
            }

        except Exception as e:
            error_msg = f"Agent処理中にエラーが発生しました: {e}"
            print(f"[ERROR] {error_msg}")

            return {
                "answer": error_msg,
                "intermediate_steps": [],
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e),
            }

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """会話履歴の取得"""
        history = []
        for message in self.memory.chat_memory.messages:
            if isinstance(message, HumanMessage):
                history.append({"type": "human", "content": message.content})
            elif isinstance(message, AIMessage):
                history.append({"type": "ai", "content": message.content})
        return history

    def clear_memory(self):
        """メモリのクリア"""
        self.memory.clear()
        print("[AGENT] Memory cleared")

    def add_custom_tool(self, tool: BaseTool):
        """カスタムツールの追加"""
        self.tools.append(tool)

        # Agent を再作成
        self.agent = create_react_agent(
            llm=self.llm, tools=self.tools, prompt=self.react_prompt
        )

        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=self.verbose,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )

        print(f"[AGENT] Added custom tool: {tool.name}")

    def get_analytics(self) -> Dict[str, Any]:
        """Agent 分析情報の取得"""
        return {
            "tools_count": len(self.tools),
            "memory_messages": len(self.memory.chat_memory.messages),
            "available_tools": [tool.name for tool in self.tools],
            "model": (
                self.llm.model_name if hasattr(self.llm, "model_name") else "unknown"
            ),
        }


def test_agent_system():
    """Agent システムのテスト"""
    try:
        print("🧪 Testing Uma3Agent...")

        # RAG エンジン初期化
        rag_engine = Uma3RAGEngine()

        # Agent 初期化
        agent = Uma3Agent(rag_engine, verbose=True)

        # テストクエリ
        test_queries = [
            "今週の予定を教えて",
            "羽村ライオンズの練習はいつですか？",
            "明日は何かありますか？",
        ]

        for query in test_queries:
            print(f"\\n📝 Testing query: '{query}'")
            result = agent.process_query(query, user_id="test_user")

            print(f"Success: {result['success']}")
            print(f"Answer: {result['answer'][:200]}...")
            if result["intermediate_steps"]:
                print(f"Steps: {len(result['intermediate_steps'])}")

        print("\\n📊 Agent Analytics:")
        analytics = agent.get_analytics()
        for key, value in analytics.items():
            print(f"  {key}: {value}")

        print("✅ Agent system test completed")

    except Exception as e:
        print(f"❌ Agent system test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_agent_system()
