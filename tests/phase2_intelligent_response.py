"""
Phase 2: インテリジェント応答生成システム
拡張されたメタデータを活用した応答精度向上システム

Phase 1で構築されたメタデータ：
- 意図分析（greeting, information, question）
- トピック分類（personal, technology）
- 複雑度レベル（1-5）
- ユーザー行動パターン

これらを活用してパーソナライズされた高精度応答を生成
"""

import os
import sys
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# パス設定
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), 'src')
sys.path.insert(0, src_dir)

@dataclass
class ResponseContext:
    """応答生成のためのコンテキスト情報"""
    user_id: str
    current_message: str
    intent: str
    topic_category: str
    complexity_level: int
    user_behavior_patterns: Dict
    conversation_history: List[Tuple[str, str]]
    relevant_conversations: List[Dict]
    chroma_results: List = None

class IntelligentResponseGenerator:
    """インテリジェント応答生成システム"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.setup_response_templates()

    def setup_response_templates(self):
        """意図とトピック別応答テンプレートの設定"""
        self.response_templates = {
            # 挨拶への応答
            'greeting': {
                'personal': {
                    'new_user': "はじめまして！{user_name}さんですね。よろしくお願いします。何かお手伝いできることがあれば、お気軽にお声かけください。",
                    'returning_user': "こんにちは、{user_name}さん！お久しぶりです。{last_topic}の件はいかがでしょうか？"
                },
                'general': "こんにちは！今日はどのようなことをお手伝いできますか？"
            },

            # 質問への応答
            'question': {
                'technology': {
                    'simple': "技術的なご質問ですね。{relevant_context}に基づいてお答えします。",
                    'complex': "少し複雑な技術的な内容ですね。詳しく説明させていただきます。{detailed_context}",
                    'personal_context': "{user_name}さんの{user_interests}の経験を踏まえると、"
                },
                'personal': {
                    'simple': "個人的なことについてのご質問ですね。",
                    'complex': "詳しくお聞かせください。{conversation_context}を参考に、"
                }
            },

            # 情報提供への応答
            'information': {
                'technology': {
                    'acknowledge': "技術的な情報をありがとうございます。{topic}について理解しました。",
                    'followup': "とても興味深い{topic}の話ですね。もう少し詳しく教えていただけますか？"
                },
                'personal': {
                    'acknowledge': "お教えいただき、ありがとうございます。{user_name}さんのことがよく分かりました。",
                    'remember': "覚えておきますね。{topic}について、また何かあればお聞かせください。"
                }
            }
        }

    def get_user_context(self, user_id: str) -> Dict:
        """ユーザーのコンテキスト情報を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        context = {
            'user_name': None,
            'interests': [],
            'conversation_count': 0,
            'last_topic': None,
            'behavior_patterns': {},
            'preferred_topics': []
        }

        # ユーザープロフィール取得
        cursor.execute("""
            SELECT profile_data, interests, conversation_count
            FROM user_profiles
            WHERE user_id = ?
        """, (user_id,))

        profile_result = cursor.fetchone()
        if profile_result:
            profile_data, interests, conv_count = profile_result
            context['conversation_count'] = conv_count

            if interests:
                try:
                    context['interests'] = json.loads(interests)
                except:
                    context['interests'] = [interests] if interests else []

        # 行動パターン取得
        cursor.execute("""
            SELECT behavior_type, pattern_data
            FROM user_behavior_patterns
            WHERE user_id = ?
        """, (user_id,))

        for behavior_type, pattern_data in cursor.fetchall():
            try:
                context['behavior_patterns'][behavior_type] = json.loads(pattern_data)
            except:
                continue

        # 最近のトピック取得
        cursor.execute("""
            SELECT cm.topic_category, COUNT(*) as count
            FROM conversation_metadata cm
            JOIN conversation_history ch ON cm.conversation_id = ch.id
            WHERE ch.user_id = ?
            GROUP BY cm.topic_category
            ORDER BY count DESC
            LIMIT 3
        """, (user_id,))

        context['preferred_topics'] = [row[0] for row in cursor.fetchall()]

        # ユーザー名の推測（過去の会話から）
        cursor.execute("""
            SELECT content
            FROM conversation_history
            WHERE user_id = ? AND message_type = 'human'
            AND (content LIKE '%私の名前は%' OR content LIKE '%私は%です')
            ORDER BY timestamp DESC
            LIMIT 1
        """, (user_id,))

        name_result = cursor.fetchone()
        if name_result:
            content = name_result[0]
            # 簡易的な名前抽出
            if '私の名前は' in content:
                name_part = content.split('私の名前は')[1].split('です')[0].strip()
                context['user_name'] = name_part
            elif '私は' in content and 'です' in content:
                name_part = content.split('私は')[1].split('です')[0].strip()
                if len(name_part) < 10:  # 名前っぽい長さ
                    context['user_name'] = name_part

        conn.close()
        return context

    def analyze_current_message(self, user_id: str, message: str) -> Dict:
        """現在のメッセージを分析"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 一時的な分析（本来は既存の分析システムを使用）
        from phase1_enhanced_learning import EnhancedConversationAnalyzer
        analyzer = EnhancedConversationAnalyzer(self.db_path)

        analysis = {
            'intent': analyzer.analyze_conversation_intent(message),
            'sentiment': analyzer.analyze_sentiment(message),
            'topic_category': analyzer.categorize_topic(message),
            'complexity_level': analyzer.calculate_complexity_level(message),
            'keywords': analyzer.extract_keywords(message)
        }

        conn.close()
        return analysis

    def get_relevant_conversation_context(self, user_id: str, current_analysis: Dict, limit: int = 3) -> List[Dict]:
        """関連する過去の会話コンテキストを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 同じトピックカテゴリの過去の会話
        cursor.execute("""
            SELECT ch.content, ch.message_type, ch.timestamp, cm.intent, cm.topic_category
            FROM conversation_history ch
            JOIN conversation_metadata cm ON ch.id = cm.conversation_id
            WHERE ch.user_id = ? AND cm.topic_category = ?
            ORDER BY ch.timestamp DESC
            LIMIT ?
        """, (user_id, current_analysis['topic_category'], limit * 2))

        relevant_conversations = []
        for content, msg_type, timestamp, intent, topic in cursor.fetchall():
            relevant_conversations.append({
                'content': content,
                'message_type': msg_type,
                'timestamp': timestamp,
                'intent': intent,
                'topic_category': topic
            })

        conn.close()
        return relevant_conversations[:limit]

    def generate_personalized_response(self, user_id: str, message: str) -> Dict:
        """パーソナライズされた応答を生成"""

        # 1. 現在のメッセージを分析
        current_analysis = self.analyze_current_message(user_id, message)

        # 2. ユーザーコンテキストを取得
        user_context = self.get_user_context(user_id)

        # 3. 関連する会話コンテキストを取得
        relevant_context = self.get_relevant_conversation_context(user_id, current_analysis)

        # 4. 応答生成
        response_parts = []

        # 基本応答の選択
        intent = current_analysis['intent']
        topic = current_analysis['topic_category']
        complexity = current_analysis['complexity_level']

        # パーソナライゼーション要素
        personalization = {}

        # ユーザー名の活用
        if user_context['user_name']:
            personalization['user_name'] = user_context['user_name']

        # 興味・関心の活用
        if user_context['interests']:
            personalization['user_interests'] = '、'.join(user_context['interests'])

        # 過去の会話の参照
        if relevant_context:
            last_topic = relevant_context[0]['topic_category']
            personalization['last_topic'] = last_topic

        # テンプレート選択と応答生成
        response_type = 'standard'

        if intent in self.response_templates:
            template_group = self.response_templates[intent]

            if topic in template_group:
                if isinstance(template_group[topic], dict):
                    # 複雑さやユーザーコンテキストに基づく選択
                    if user_context['conversation_count'] == 0:
                        template_key = 'new_user'
                    elif user_context['conversation_count'] > 5:
                        template_key = 'returning_user'
                    elif complexity > 3:
                        template_key = 'complex'
                    else:
                        template_key = 'simple'

                    template = template_group[topic].get(template_key, list(template_group[topic].values())[0])
                else:
                    template = template_group[topic]

                # テンプレートに値を埋め込み
                try:
                    response = template.format(**personalization)
                    response_type = 'personalized'
                except KeyError:
                    response = template
                    response_type = 'template'

                response_parts.append(response)

        # コンテキスト情報を追加
        context_info = []

        # 過去の会話を参照
        if relevant_context and len(relevant_context) > 0:
            recent_topics = [ctx['topic_category'] for ctx in relevant_context]
            if recent_topics.count(topic) > 1:
                context_info.append(f"以前も{topic}について話しましたね。")

        # 応答の組み立て
        if not response_parts:
            # フォールバック応答
            response_parts.append(f"ありがとうございます。{topic}について、理解しました。")

        if context_info:
            response_parts.extend(context_info)

        final_response = " ".join(response_parts)

        # 応答品質の評価
        quality_score = self.evaluate_response_quality(final_response, current_analysis, user_context)

        return {
            'response': final_response,
            'response_type': response_type,
            'quality_score': quality_score,
            'personalization_used': personalization,
            'context_analysis': current_analysis,
            'user_context': user_context,
            'relevant_context_count': len(relevant_context)
        }

    def evaluate_response_quality(self, response: str, analysis: Dict, user_context: Dict) -> float:
        """応答品質の評価"""
        score = 0.0
        max_score = 5.0

        # 基本的な応答の存在
        if response and len(response.strip()) > 0:
            score += 1.0

        # パーソナライゼーションの活用
        if user_context['user_name'] and user_context['user_name'] in response:
            score += 1.0

        # トピックの一致
        if analysis['topic_category'] in ['technology', 'personal']:
            topic_keywords = {
                'technology': ['技術', 'プログラミング', 'システム', 'データ'],
                'personal': ['あなた', 'お聞かせ', '理解', '覚えて']
            }

            if any(keyword in response for keyword in topic_keywords.get(analysis['topic_category'], [])):
                score += 1.0

        # 応答の長さ（適切な情報量）
        if 20 <= len(response) <= 200:
            score += 1.0
        elif len(response) > 10:
            score += 0.5

        # 意図に対する適切性
        intent_appropriateness = {
            'greeting': ['こんにちは', 'はじめまして', 'よろしく'],
            'question': ['お答え', 'について', '説明'],
            'information': ['ありがとう', '理解', '覚えて']
        }

        if any(phrase in response for phrase in intent_appropriateness.get(analysis['intent'], [])):
            score += 1.0

        return min(score, max_score)

def test_intelligent_response_system():
    """インテリジェント応答システムのテスト"""
    print("🧠 Phase 2: インテリジェント応答生成システムテスト")
    print("=" * 70)

    db_path = 'Lesson25/uma3soft-app/db/conversation_history.db'

    if not os.path.exists(db_path):
        print(f"❌ データベースファイルが見つかりません: {db_path}")
        return

    # システム初期化
    generator = IntelligentResponseGenerator(db_path)

    # テストユーザー
    test_user_id = "TEST_U12345_CONVERSATION_FIX"

    # テストケース
    test_messages = [
        "こんにちは！今日もよろしくお願いします",
        "前回話したプログラミングについて、もう少し詳しく教えてください",
        "私の名前、覚えていますか？",
        "新しいPythonプロジェクトを始めました",
        "ありがとうございました"
    ]

    print(f"\n👤 テストユーザー: {test_user_id[:20]}...")
    print(f"🧪 テストケース: {len(test_messages)}件")
    print("-" * 50)

    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. 入力メッセージ: '{message}'")
        print("-" * 30)

        try:
            result = generator.generate_personalized_response(test_user_id, message)

            print(f"🤖 生成応答: {result['response']}")
            print(f"📊 応答タイプ: {result['response_type']}")
            print(f"⭐ 品質スコア: {result['quality_score']:.1f}/5.0")

            # 分析情報
            analysis = result['context_analysis']
            print(f"🔍 分析結果:")
            print(f"   意図: {analysis['intent']}")
            print(f"   トピック: {analysis['topic_category']}")
            print(f"   複雑度: {analysis['complexity_level']}/5")

            # パーソナライゼーション情報
            personalization = result['personalization_used']
            if personalization:
                print(f"👤 パーソナライゼーション:")
                for key, value in personalization.items():
                    print(f"   {key}: {value}")

            # ユーザーコンテキスト
            user_context = result['user_context']
            print(f"📚 ユーザーコンテキスト:")
            print(f"   会話回数: {user_context['conversation_count']}")
            print(f"   興味・関心: {user_context['interests']}")
            print(f"   関連コンテキスト: {result['relevant_context_count']}件")

        except Exception as e:
            print(f"❌ エラー: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n🎉 インテリジェント応答システムテスト完了！")

    # 応答品質の統計
    print(f"\n📊 システム性能評価")
    print("-" * 50)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # メタデータ統計の再確認
    cursor.execute("SELECT COUNT(*) FROM conversation_metadata;")
    metadata_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM user_behavior_patterns;")
    pattern_count = cursor.fetchone()[0]

    print(f"✅ 分析済み会話メタデータ: {metadata_count}件")
    print(f"✅ ユーザー行動パターン: {pattern_count}件")
    print(f"✅ パーソナライゼーション機能: 有効")
    print(f"✅ コンテキスト参照機能: 有効")

    conn.close()

    print(f"\n💡 次のステップ:")
    print("   1. この応答生成システムを統合会話システムに組み込み")
    print("   2. 実際のLINE Botでの運用テスト")
    print("   3. ユーザーフィードバックの収集と品質改善")

if __name__ == "__main__":
    print(f"📅 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    test_intelligent_response_system()
