"""
Phase 1: データ基盤強化 - 会話履歴メタデータ拡張の実装

現在の分析結果：
- 1ユーザー、10メッセージの少ないデータ
- 平均メッセージ長: 18文字（短い）
- 興味・関心: プログラミング関連が学習済み

最優先改善ポイント：
1. 会話の質的情報を増やす
2. ユーザープロフィールの詳細化
3. 検索精度の向上
"""

import os
import sys
import sqlite3
import json
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional

# パス設定
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), 'src')
sys.path.insert(0, src_dir)

@dataclass
class ConversationMetadata:
    """拡張された会話メタデータ"""
    user_id: str
    content: str
    message_type: str
    timestamp: str

    # 新しい質的情報
    intent: Optional[str] = None  # 質問、雑談、情報提供など
    sentiment: Optional[str] = None  # positive, neutral, negative
    topic_category: Optional[str] = None  # 技術、個人、業務など
    complexity_level: Optional[int] = None  # 1-5の複雑さレベル
    response_quality: Optional[int] = None  # 1-5の応答品質
    user_satisfaction: Optional[int] = None  # 1-5のユーザー満足度
    context_used: Optional[Dict] = None  # 使用されたコンテキスト情報
    keywords: Optional[List[str]] = None  # 抽出されたキーワード

class EnhancedConversationAnalyzer:
    """拡張された会話分析システム"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.setup_enhanced_schema()

    def setup_enhanced_schema(self):
        """拡張されたデータベーススキーマのセットアップ"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 新しいテーブル: conversation_metadata
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                intent TEXT,
                sentiment TEXT,
                topic_category TEXT,
                complexity_level INTEGER,
                response_quality INTEGER,
                user_satisfaction INTEGER,
                context_used TEXT,  -- JSON形式
                keywords TEXT,      -- JSON形式
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversation_history (id)
            );
        """)

        # 新しいテーブル: user_behavior_patterns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_behavior_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                behavior_type TEXT,  -- 'time_pattern', 'topic_preference', 'communication_style'
                pattern_data TEXT,   -- JSON形式
                confidence_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 新しいテーブル: conversation_quality_metrics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_quality_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                date TEXT,
                total_conversations INTEGER,
                avg_response_quality REAL,
                avg_user_satisfaction REAL,
                topic_diversity_score REAL,
                engagement_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.commit()
        conn.close()
        print("✅ 拡張データベーススキーマを設定しました")

    def analyze_conversation_intent(self, content: str) -> str:
        """会話の意図を分析（簡易版）"""
        content_lower = content.lower()

        # 質問パターン
        question_patterns = ['？', '?', 'どう', 'なに', 'なん', 'いつ', 'どこ', 'だれ', 'なぜ', 'どのように']
        if any(pattern in content for pattern in question_patterns):
            return 'question'

        # 挨拶パターン
        greeting_patterns = ['こんにちは', 'おはよう', 'こんばんは', 'はじめまして', 'よろしく']
        if any(pattern in content for pattern in greeting_patterns):
            return 'greeting'

        # 情報提供パターン
        info_patterns = ['です', 'ます', '～している', '～した', '～します']
        if any(pattern in content for pattern in info_patterns):
            return 'information'

        # 依頼パターン
        request_patterns = ['してください', 'お願い', 'help', 'ヘルプ']
        if any(pattern in content for pattern in request_patterns):
            return 'request'

        return 'chat'  # その他は雑談として分類

    def analyze_sentiment(self, content: str) -> str:
        """感情分析（簡易版）"""
        # ポジティブキーワード
        positive_words = ['ありがとう', '嬉しい', '良い', '素晴らしい', '楽しい', '好き', '素敵']
        # ネガティブキーワード
        negative_words = ['残念', '悲しい', '困った', '問題', 'エラー', '嫌い', 'だめ']

        positive_count = sum(1 for word in positive_words if word in content)
        negative_count = sum(1 for word in negative_words if word in content)

        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'

    def categorize_topic(self, content: str) -> str:
        """トピックのカテゴリ分類"""
        # 技術関連
        tech_keywords = ['プログラミング', 'Python', 'コード', '開発', 'システム', 'アプリ', 'データベース']
        if any(keyword in content for keyword in tech_keywords):
            return 'technology'

        # 個人関連
        personal_keywords = ['名前', '住んで', '趣味', '好き', '家族', '仕事', '年齢']
        if any(keyword in content for keyword in personal_keywords):
            return 'personal'

        # 業務関連
        work_keywords = ['会議', 'スケジュール', '予定', '仕事', '会社', 'プロジェクト']
        if any(keyword in content for keyword in work_keywords):
            return 'work'

        # 時間関連
        time_keywords = ['今日', '明日', '昨日', '来週', '先週', '時間', '日時']
        if any(keyword in content for keyword in time_keywords):
            return 'time'

        return 'general'

    def calculate_complexity_level(self, content: str) -> int:
        """会話の複雑さレベルを計算"""
        # 文字数ベースの基本スコア
        length_score = min(len(content) // 20, 3)

        # 専門用語や複雑な表現の存在
        complex_patterns = ['について', 'に関して', '具体的に', '詳しく', 'システム', 'データベース']
        complexity_bonus = sum(1 for pattern in complex_patterns if pattern in content)

        # 疑問詞の数（複雑な質問ほど多い）
        question_words = ['なぜ', 'どのように', 'どうして', 'いかに']
        question_bonus = sum(1 for word in question_words if word in content)

        total_score = length_score + complexity_bonus + question_bonus
        return min(max(total_score, 1), 5)  # 1-5の範囲に制限

    def extract_keywords(self, content: str) -> List[str]:
        """キーワード抽出"""
        import re

        # カタカナ、漢字、英単語を抽出
        keywords = []

        # カタカナ（2文字以上）
        katakana_words = re.findall(r'[ァ-ヶー]{2,}', content)
        keywords.extend(katakana_words)

        # 漢字（1文字以上）
        kanji_words = re.findall(r'[一-龯]+', content)
        keywords.extend([word for word in kanji_words if len(word) >= 1])

        # 英単語（2文字以上）
        english_words = re.findall(r'[a-zA-Z]{2,}', content)
        keywords.extend(english_words)

        # 重複除去と長さフィルタ
        unique_keywords = list(set(keywords))
        return [kw for kw in unique_keywords if len(kw) >= 2]

    def enhance_existing_conversations(self):
        """既存の会話データに拡張メタデータを追加"""
        print("\n🔧 既存会話データの拡張処理開始")
        print("-" * 50)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 既存の会話データを取得
        cursor.execute("SELECT id, user_id, content, message_type, timestamp FROM conversation_history;")
        conversations = cursor.fetchall()

        enhanced_count = 0

        for conv_id, user_id, content, msg_type, timestamp in conversations:
            if msg_type == 'human' and content.strip():  # 人間のメッセージのみ処理
                # 各種分析を実行
                intent = self.analyze_conversation_intent(content)
                sentiment = self.analyze_sentiment(content)
                topic_category = self.categorize_topic(content)
                complexity_level = self.calculate_complexity_level(content)
                keywords = self.extract_keywords(content)

                # メタデータをデータベースに保存
                cursor.execute("""
                    INSERT INTO conversation_metadata
                    (conversation_id, intent, sentiment, topic_category, complexity_level, keywords)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    conv_id, intent, sentiment, topic_category,
                    complexity_level, json.dumps(keywords, ensure_ascii=False)
                ))

                enhanced_count += 1
                print(f"   ✅ 会話ID {conv_id}: {intent}/{topic_category} (複雑度:{complexity_level})")

        conn.commit()
        conn.close()

        print(f"\n📊 拡張完了: {enhanced_count}件の会話を処理しました")

    def generate_user_behavior_patterns(self, user_id: str):
        """ユーザーの行動パターンを生成"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 会話時間パターンの分析
        cursor.execute("""
            SELECT timestamp FROM conversation_history
            WHERE user_id = ? AND message_type = 'human'
            ORDER BY timestamp
        """, (user_id,))

        timestamps = [row[0] for row in cursor.fetchall()]

        if timestamps:
            # 時間帯パターンの分析
            hours = []
            for ts in timestamps:
                try:
                    dt = datetime.fromisoformat(ts)
                    hours.append(dt.hour)
                except:
                    continue

            if hours:
                time_pattern = {
                    'active_hours': hours,
                    'most_active_hour': max(set(hours), key=hours.count),
                    'conversation_frequency': len(hours)
                }

                # データベースに保存
                cursor.execute("""
                    INSERT OR REPLACE INTO user_behavior_patterns
                    (user_id, behavior_type, pattern_data, confidence_score)
                    VALUES (?, ?, ?, ?)
                """, (
                    user_id, 'time_pattern',
                    json.dumps(time_pattern, ensure_ascii=False),
                    min(len(hours) / 10.0, 1.0)  # 会話数に基づく信頼度
                ))

        # トピック嗜好パターンの分析
        cursor.execute("""
            SELECT cm.topic_category, COUNT(*) as count
            FROM conversation_metadata cm
            JOIN conversation_history ch ON cm.conversation_id = ch.id
            WHERE ch.user_id = ?
            GROUP BY cm.topic_category
            ORDER BY count DESC
        """, (user_id,))

        topic_preferences = dict(cursor.fetchall())

        if topic_preferences:
            cursor.execute("""
                INSERT OR REPLACE INTO user_behavior_patterns
                (user_id, behavior_type, pattern_data, confidence_score)
                VALUES (?, ?, ?, ?)
            """, (
                user_id, 'topic_preference',
                json.dumps(topic_preferences, ensure_ascii=False),
                min(sum(topic_preferences.values()) / 20.0, 1.0)
            ))

        conn.commit()
        conn.close()

        print(f"✅ ユーザー {user_id[:20]}... の行動パターンを生成しました")

    def generate_quality_report(self) -> Dict:
        """会話品質レポートを生成"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        report = {}

        # 基本統計
        cursor.execute("SELECT COUNT(*) FROM conversation_history WHERE message_type = 'human';")
        total_human_messages = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM conversation_history;")
        total_users = cursor.fetchone()[0]

        # メタデータ統計
        cursor.execute("""
            SELECT intent, COUNT(*)
            FROM conversation_metadata
            GROUP BY intent
        """)
        intent_distribution = dict(cursor.fetchall())

        cursor.execute("""
            SELECT topic_category, COUNT(*)
            FROM conversation_metadata
            GROUP BY topic_category
        """)
        topic_distribution = dict(cursor.fetchall())

        cursor.execute("""
            SELECT AVG(complexity_level)
            FROM conversation_metadata
        """)
        avg_complexity = cursor.fetchone()[0] or 0

        report = {
            'basic_stats': {
                'total_human_messages': total_human_messages,
                'total_users': total_users,
                'avg_messages_per_user': total_human_messages / max(total_users, 1)
            },
            'intent_distribution': intent_distribution,
            'topic_distribution': topic_distribution,
            'avg_complexity': round(avg_complexity, 2)
        }

        conn.close()
        return report

def implement_enhanced_learning_system():
    """拡張学習システムの実装"""
    print("🚀 Phase 1: データ基盤強化 - 拡張学習システム実装")
    print("=" * 70)

    db_path = 'Lesson25/uma3soft-app/db/conversation_history.db'

    if not os.path.exists(db_path):
        print(f"❌ データベースファイルが見つかりません: {db_path}")
        return

    # 拡張分析システムの初期化
    analyzer = EnhancedConversationAnalyzer(db_path)

    # 既存データの拡張
    analyzer.enhance_existing_conversations()

    # ユーザー別行動パターンの生成
    print(f"\n🧠 ユーザー行動パターン生成")
    print("-" * 50)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT user_id FROM conversation_history;")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()

    for user_id in users:
        analyzer.generate_user_behavior_patterns(user_id)

    # 品質レポートの生成
    print(f"\n📊 会話品質レポート")
    print("-" * 50)

    report = analyzer.generate_quality_report()

    print(f"基本統計:")
    for key, value in report['basic_stats'].items():
        print(f"   {key}: {value}")

    print(f"\n意図分布:")
    for intent, count in report['intent_distribution'].items():
        print(f"   {intent}: {count}件")

    print(f"\nトピック分布:")
    for topic, count in report['topic_distribution'].items():
        print(f"   {topic}: {count}件")

    print(f"\n平均複雑度: {report['avg_complexity']}/5.0")

    print(f"\n🎉 Phase 1 完了！拡張データ基盤が構築されました。")
    print("💡 次のステップ: この拡張されたメタデータを活用した応答生成システムの改善")

if __name__ == "__main__":
    print(f"📅 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    implement_enhanced_learning_system()
