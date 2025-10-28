"""
会話履歴管理システム
ユーザ別の会話履歴を蓄積・管理し、履歴ベースの自然応答Botを実現する

主な機能:
1. ユーザ別会話履歴の永続化（SQLite）
2. LangChainメモリー機能との統合
3. 会話コンテキストの動的取得
4. ユーザプロフィール学習機能
"""

import json
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI


class SQLiteChatMessageHistory(BaseChatMessageHistory):
    """SQLiteベースの会話履歴管理クラス"""

    def __init__(self, db_path: str, user_id: str, session_id: str = "default"):
        self.db_path = db_path
        self.user_id = user_id
        self.session_id = session_id
        self._init_db()

    def _init_db(self):
        """データベースの初期化"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_session
                ON conversation_history(user_id, session_id)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON conversation_history(timestamp)
            """)

            # ユーザプロフィールテーブル
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    profile_data TEXT,
                    interests TEXT,
                    conversation_count INTEGER DEFAULT 0,
                    last_interaction DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

    @property
    def messages(self) -> List[BaseMessage]:
        """会話履歴を取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT message_type, content, metadata, timestamp
                FROM conversation_history
                WHERE user_id = ? AND session_id = ?
                ORDER BY timestamp ASC
            """, (self.user_id, self.session_id))

            messages = []
            for row in cursor.fetchall():
                message_type, content, metadata_str, timestamp = row
                metadata = json.loads(metadata_str) if metadata_str else {}

                if message_type == "human":
                    messages.append(HumanMessage(content=content, additional_kwargs=metadata))
                elif message_type == "ai":
                    messages.append(AIMessage(content=content, additional_kwargs=metadata))

            return messages

    def add_message(self, message: BaseMessage) -> None:
        """メッセージを追加"""
        message_type = "human" if isinstance(message, HumanMessage) else "ai"
        metadata = json.dumps(getattr(message, 'additional_kwargs', {}))

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO conversation_history
                (user_id, session_id, message_type, content, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (self.user_id, self.session_id, message_type, message.content, metadata))

    def clear(self) -> None:
        """特定セッションの履歴をクリア"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                DELETE FROM conversation_history
                WHERE user_id = ? AND session_id = ?
            """, (self.user_id, self.session_id))


class ConversationHistoryManager:
    """会話履歴管理の中央制御クラス"""

    def __init__(self, db_path: str = "conversation_history.db"):
        self.db_path = db_path
        self.history_cache = {}  # ユーザID別の履歴キャッシュ
        self._init_db()

    def _init_db(self):
        """データベースの初期化"""
        with sqlite3.connect(self.db_path) as conn:
            # 既存テーブルのチェックと作成はSQLiteChatMessageHistoryで実行される
            # 明示的に初期化を実行
            temp_history = SQLiteChatMessageHistory(self.db_path, "temp_init", "init")
            print(f"[DB_INIT] Database initialized: {self.db_path}")

    def get_user_history(self, user_id: str, session_id: str = "default") -> SQLiteChatMessageHistory:
        """ユーザの会話履歴を取得"""
        cache_key = f"{user_id}_{session_id}"
        if cache_key not in self.history_cache:
            self.history_cache[cache_key] = SQLiteChatMessageHistory(
                self.db_path, user_id, session_id
            )
        return self.history_cache[cache_key]

    def save_conversation(self, user_id: str, human_message: str, ai_message: str,
                         session_id: str = "default", metadata: Dict = None) -> None:
        """会話を保存"""
        history = self.get_user_history(user_id, session_id)

        # メタデータの準備
        base_metadata = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id
        }
        if metadata:
            base_metadata.update(metadata)

        # メッセージを追加
        history.add_message(HumanMessage(content=human_message, additional_kwargs=base_metadata))
        history.add_message(AIMessage(content=ai_message, additional_kwargs=base_metadata))

        # ユーザプロフィールを更新
        self._update_user_profile(user_id, human_message)

    def _update_user_profile(self, user_id: str, message: str) -> None:
        """ユーザプロフィールを更新"""
        with sqlite3.connect(self.db_path) as conn:
            # 現在のプロフィールを取得
            cursor = conn.cursor()
            cursor.execute("""
                SELECT profile_data, interests, conversation_count
                FROM user_profiles WHERE user_id = ?
            """, (user_id,))

            result = cursor.fetchone()
            if result:
                profile_data, interests, conversation_count = result
                profile_data = json.loads(profile_data) if profile_data else {}
                interests = json.loads(interests) if interests else []
                conversation_count += 1
            else:
                profile_data = {}
                interests = []
                conversation_count = 1

            # 興味・関心キーワードの抽出（改善版）
            interest_keywords = ["好き", "興味", "趣味", "楽しい", "面白い", "好む", "応援", "ファン"]
            for keyword in interest_keywords:
                if keyword in message:
                    # キーワード前後の文脈を抽出
                    words = message.replace("。", " ").replace("、", " ").split()
                    for i, word in enumerate(words):
                        if keyword in word:
                            # 前後2-3語を含む文脈を抽出
                            start_idx = max(0, i-2)
                            end_idx = min(len(words), i+3)
                            interest_context = " ".join(words[start_idx:end_idx])

                            # 既存の興味リストにない場合追加
                            if interest_context not in interests and len(interest_context) > 3:
                                interests.append(interest_context)
                                # 最大10個まで保持
                                if len(interests) > 10:
                                    interests = interests[-10:]

            # プロフィールを保存
            conn.execute("""
                INSERT OR REPLACE INTO user_profiles
                (user_id, profile_data, interests, conversation_count, last_interaction, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                json.dumps(profile_data),
                json.dumps(interests),
                conversation_count,
                datetime.now(),
                datetime.now()
            ))

    def get_recent_conversations(self, user_id: str, limit: int = 10,
                               days: int = 7) -> List[Tuple[str, str, datetime]]:
        """最近の会話を取得"""
        cutoff_date = datetime.now() - timedelta(days=days)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT content, message_type, timestamp
                FROM conversation_history
                WHERE user_id = ? AND timestamp > ?
                ORDER BY timestamp DESC
            """, (user_id, cutoff_date.isoformat()))

            conversations = []
            messages = cursor.fetchall()

            # メッセージをペアに整理
            human_messages = [msg for msg in messages if msg[1] == "human"]
            ai_messages = [msg for msg in messages if msg[1] == "ai"]

            # 時系列順にペアを作成
            for human_msg in human_messages[:limit]:
                # 同時期のAI応答を検索
                human_time = datetime.fromisoformat(human_msg[2])
                for ai_msg in ai_messages:
                    ai_time = datetime.fromisoformat(ai_msg[2])
                    # 時間差が1分以内のペアを探す
                    if abs((ai_time - human_time).total_seconds()) < 60:
                        conversations.append((human_msg[0], ai_msg[0], human_time))
                        break

            return conversations[:limit]

    def get_user_profile(self, user_id: str) -> Dict:
        """ユーザプロフィールを取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT profile_data, interests, conversation_count, last_interaction
                FROM user_profiles WHERE user_id = ?
            """, (user_id,))

            result = cursor.fetchone()
            if result:
                profile_data, interests, conversation_count, last_interaction = result
                return {
                    "profile_data": json.loads(profile_data) if profile_data else {},
                    "interests": json.loads(interests) if interests else [],
                    "conversation_count": conversation_count,
                    "last_interaction": last_interaction
                }
            else:
                return {
                    "profile_data": {},
                    "interests": [],
                    "conversation_count": 0,
                    "last_interaction": None
                }

    def search_conversations(self, user_id: str, query: str, limit: int = 5) -> List[Dict]:
        """会話履歴の検索"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT content, message_type, timestamp, metadata
                FROM conversation_history
                WHERE user_id = ? AND content LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, f"%{query}%", limit))

            results = []
            for row in cursor.fetchall():
                content, message_type, timestamp, metadata_str = row
                metadata = json.loads(metadata_str) if metadata_str else {}

                results.append({
                    "content": content,
                    "message_type": message_type,
                    "timestamp": timestamp,
                    "metadata": metadata
                })

            return results

    def get_conversation_statistics(self, user_id: str) -> Dict:
        """会話統計を取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 基本統計
            cursor.execute("""
                SELECT COUNT(*) as total_messages,
                       COUNT(CASE WHEN message_type = 'human' THEN 1 END) as human_messages,
                       COUNT(CASE WHEN message_type = 'ai' THEN 1 END) as ai_messages,
                       MIN(timestamp) as first_interaction,
                       MAX(timestamp) as last_interaction
                FROM conversation_history
                WHERE user_id = ?
            """, (user_id,))

            stats = cursor.fetchone()

            # 日別統計（過去30日）
            cursor.execute("""
                SELECT DATE(timestamp) as date, COUNT(*) as message_count
                FROM conversation_history
                WHERE user_id = ? AND timestamp > date('now', '-30 days')
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
            """, (user_id,))

            daily_stats = cursor.fetchall()

            return {
                "total_messages": stats[0] if stats else 0,
                "human_messages": stats[1] if stats else 0,
                "ai_messages": stats[2] if stats else 0,
                "first_interaction": stats[3] if stats else None,
                "last_interaction": stats[4] if stats else None,
                "daily_activity": dict(daily_stats)
            }


class ConversationContextGenerator:
    """会話コンテキスト生成クラス"""

    def __init__(self, history_manager: ConversationHistoryManager,
                 embeddings_model: HuggingFaceEmbeddings = None):
        self.history_manager = history_manager
        self.embeddings_model = embeddings_model or HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    def generate_contextual_response_prompt(self, user_id: str, current_message: str,
                                          max_history_items: int = 5) -> str:
        """履歴ベースの応答プロンプトを生成"""

        # ユーザプロフィールを取得
        profile = self.history_manager.get_user_profile(user_id)

        # 最近の会話を取得
        recent_conversations = self.history_manager.get_recent_conversations(
            user_id, limit=max_history_items
        )

        # 関連する過去の会話を検索
        relevant_conversations = self.history_manager.search_conversations(
            user_id, current_message, limit=3
        )

        # プロンプト構築
        context_parts = []

        # ユーザプロフィール情報
        if profile["interests"]:
            interests_text = "、".join(profile["interests"][:5])
            context_parts.append(f"ユーザの興味・関心: {interests_text}")

        if profile["conversation_count"] > 0:
            context_parts.append(f"これまでの会話回数: {profile['conversation_count']}回")

        # 最近の会話履歴
        if recent_conversations:
            context_parts.append("\n**最近の会話履歴:**")
            for i, (human_msg, ai_msg, timestamp) in enumerate(recent_conversations[:3]):
                time_str = timestamp.strftime("%m/%d %H:%M")
                context_parts.append(f"[{time_str}] ユーザ: {human_msg[:100]}...")
                context_parts.append(f"[{time_str}] Bot: {ai_msg[:100]}...")

        # 関連する過去の会話
        if relevant_conversations:
            context_parts.append("\n**関連する過去の会話:**")
            for conv in relevant_conversations[:2]:
                if conv["message_type"] == "human":
                    context_parts.append(f"過去の質問: {conv['content'][:150]}...")

        # 最終プロンプト
        context_text = "\n".join(context_parts)

        prompt_template = f"""あなたは優秀なAIアシスタントです。以下のユーザ情報と会話履歴を参考にして、自然で親しみやすい応答を生成してください。

{context_text}

**現在の質問:** {current_message}

回答時の注意点:
- ユーザの過去の発言や興味を踏まえた個人的な応答を心がける
- 長期的な関係性を意識した会話を継続する
- スマートフォンで読みやすいよう適度に改行を入れる
- 必要に応じて過去の会話を参照した発言をする

応答:"""

        return prompt_template

    def generate_response_with_history(self, user_id: str, message: str,
                                     llm: ChatOpenAI = None) -> str:
        """履歴を考慮した応答を生成"""
        if llm is None:
            llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)

        prompt = self.generate_contextual_response_prompt(user_id, message)

        try:
            # ChatPromptTemplateを使用してプロンプトを整形
            formatted_prompt = ChatPromptTemplate.from_messages([
                ("user", prompt)
            ])

            response = llm.invoke(formatted_prompt.format_messages())
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            print(f"[ERROR] Response generation failed: {e}")
            return "申し訳ございません。現在応答の生成に問題が発生しています。"
# 使用例
if __name__ == "__main__":
    # 初期化
    history_manager = ConversationHistoryManager("conversation_history.db")
    context_generator = ConversationContextGenerator(history_manager)

    # テストユーザとの会話をシミュレート
    test_user_id = "test_user_123"

    # 過去の会話を保存
    history_manager.save_conversation(
        test_user_id,
        "こんにちは！私は野球が好きです。",
        "こんにちは！野球がお好きなんですね。どちらのチームを応援されていますか？"
    )

    history_manager.save_conversation(
        test_user_id,
        "読売ジャイアンツのファンです。",
        "ジャイアンツファンなんですね！今シーズンの調子はいかがですか？"
    )

    # 新しい質問に対する履歴ベース応答
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
    response = context_generator.generate_response_with_history(
        test_user_id,
        "今日の試合結果を教えて",
        llm
    )

    print(f"履歴ベース応答: {response}")

    # 統計情報の表示
    stats = history_manager.get_conversation_statistics(test_user_id)
    print(f"会話統計: {stats}")
