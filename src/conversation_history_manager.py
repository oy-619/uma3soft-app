# -*- coding: utf-8 -*-
"""
Conversation History Manager - Clean Implementation

SQLite-based conversation history management system.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


class ConversationHistoryManager:
    """Simple conversation history manager"""

    def __init__(self, db_path: str = "conversation_history.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT DEFAULT 'default'
                )
            """)
            conn.commit()

    def save_conversation(self, user_id: str, user_message: str, ai_response: str,
                         session_id: str = "default"):
        """Save conversation to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO conversations (user_id, message_type, content, session_id)
                VALUES (?, ?, ?, ?)
            """, (user_id, "human", user_message, session_id))

            conn.execute("""
                INSERT INTO conversations (user_id, message_type, content, session_id)
                VALUES (?, ?, ?, ?)
            """, (user_id, "ai", ai_response, session_id))

            conn.commit()

    def get_recent_conversations(self, user_id: str, limit: int = 5) -> List[Tuple]:
        """Get recent conversations"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT content, message_type, timestamp
                FROM conversations
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, limit * 2))

            results = cursor.fetchall()
            conversations = []

            for i in range(0, len(results), 2):
                if i + 1 < len(results):
                    conversations.append((results[i+1][0], results[i][0], results[i][2]))

            return conversations[:limit]

    def get_user_history(self, user_id: str, session_id: str = "default"):
        """Get user history object for compatibility"""
        class SimpleHistory:
            def __init__(self, manager, user_id, session_id):
                self.manager = manager
                self.user_id = user_id
                self.session_id = session_id

            def clear(self):
                with sqlite3.connect(self.manager.db_path) as conn:
                    conn.execute("""
                        DELETE FROM conversations
                        WHERE user_id = ? AND session_id = ?
                    """, (self.user_id, self.session_id))
                    conn.commit()

        return SimpleHistory(self, user_id, session_id)

    def get_user_profile(self, user_id: str) -> Dict:
        """Get user profile information"""
        # Create user_profiles table if it doesn't exist
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    interests TEXT,
                    preferences TEXT,
                    conversation_count INTEGER DEFAULT 0,
                    last_active DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor = conn.execute("""
                SELECT interests, preferences, conversation_count, last_active, created_at
                FROM user_profiles WHERE user_id = ?
            """, (user_id,))

            result = cursor.fetchone()
            if result:
                interests = json.loads(result[0]) if result[0] else []
                preferences = json.loads(result[1]) if result[1] else {}
                return {
                    "user_id": user_id,
                    "interests": interests,
                    "preferences": preferences,
                    "conversation_count": result[2] or 0,
                    "last_active": result[3],
                    "created_at": result[4]
                }
            else:
                # Create default profile
                conn.execute("""
                    INSERT INTO user_profiles (user_id, interests, preferences, conversation_count)
                    VALUES (?, ?, ?, ?)
                """, (user_id, "[]", "{}", 0))
                conn.commit()

                return {
                    "user_id": user_id,
                    "interests": [],
                    "preferences": {},
                    "conversation_count": 0,
                    "last_active": None,
                    "created_at": datetime.now().isoformat()
                }

    def search_conversations(self, user_id: str, query: str, limit: int = 10) -> List[Dict]:
        """Search conversations by content"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT content, message_type, timestamp, session_id
                FROM conversations
                WHERE user_id = ? AND content LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, f"%{query}%", limit))

            results = []
            for row in cursor.fetchall():
                results.append({
                    "content": row[0],
                    "message_type": row[1],
                    "timestamp": row[2],
                    "session_id": row[3],
                    "metadata": {}
                })

            return results

    def get_conversation_statistics(self, user_id: str) -> Dict:
        """Get conversation statistics for user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT
                    COUNT(*) as total_messages,
                    COUNT(CASE WHEN message_type = 'human' THEN 1 END) as user_messages,
                    COUNT(CASE WHEN message_type = 'ai' THEN 1 END) as ai_messages,
                    MIN(timestamp) as first_conversation,
                    MAX(timestamp) as last_conversation
                FROM conversations
                WHERE user_id = ?
            """, (user_id,))

            result = cursor.fetchone()
            if result:
                return {
                    "total_messages": result[0] or 0,
                    "user_messages": result[1] or 0,
                    "ai_messages": result[2] or 0,
                    "first_conversation": result[3],
                    "last_conversation": result[4]
                }
            else:
                return {
                    "total_messages": 0,
                    "user_messages": 0,
                    "ai_messages": 0,
                    "first_conversation": None,
                    "last_conversation": None
                }

    def update_user_profile(self, user_id: str, interests: List[str] = None,
                           preferences: Dict = None):
        """Update user profile information"""
        with sqlite3.connect(self.db_path) as conn:
            updates = []
            params = []

            if interests is not None:
                updates.append("interests = ?")
                params.append(json.dumps(interests))

            if preferences is not None:
                updates.append("preferences = ?")
                params.append(json.dumps(preferences))

            if updates:
                updates.append("updated_at = ?")
                params.append(datetime.now().isoformat())
                params.append(user_id)

                query = f"""
                    UPDATE user_profiles
                    SET {', '.join(updates)}
                    WHERE user_id = ?
                """
                conn.execute(query, params)
                conn.commit()


class ConversationContextGenerator:
    """Simple context generator for compatibility"""

    def __init__(self, history_manager: ConversationHistoryManager):
        self.history_manager = history_manager

    def generate_contextual_response_prompt(self, user_id: str, current_message: str,
                                          max_history_items: int = 5) -> str:
        """Generate simple contextual prompt"""
        recent = self.history_manager.get_recent_conversations(user_id, limit=3)

        context_parts = []
        if recent:
            context_parts.append("Recent conversation:")
            for human_msg, ai_msg, timestamp in recent:
                context_parts.append(f"User: {human_msg[:100]}...")
                context_parts.append(f"Bot: {ai_msg[:100]}...")

        context_text = "\n".join(context_parts)

        return f"""Previous context:
{context_text}

Current question: {current_message}

Please provide a helpful response."""


if __name__ == "__main__":
    # Test the system
    manager = ConversationHistoryManager("test.db")
    manager.save_conversation("user1", "Hello", "Hi there!")
    recent = manager.get_recent_conversations("user1")
    print(f"Recent conversations: {recent}")
