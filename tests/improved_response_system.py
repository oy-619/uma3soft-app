"""
改善された応答テンプレートシステム
Phase 2で発見された問題を修正し、自然で魅力的な応答を生成
"""

import os
import sys
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import re

# パス設定
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), 'src')
sys.path.insert(0, src_dir)

class ImprovedResponseGenerator:
    """改善された応答生成システム"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.setup_improved_templates()

    def setup_improved_templates(self):
        """改善された自然な応答テンプレート"""
        self.response_templates = {
            # 挨拶への応答
            'greeting': {
                'personal': {
                    'new_user': [
                        "はじめまして！よろしくお願いします。何かお手伝いできることがあれば、お気軽にお声かけください😊",
                        "こんにちは！お会いできて嬉しいです。どのようなことでお困りでしょうか？",
                        "はじめまして！どんなことでもお気軽にご相談ください。"
                    ],
                    'returning_user': [
                        "こんにちは！また会えて嬉しいです😊",
                        "お疲れ様です！今日はどのようなことをお手伝いできますか？",
                        "こんにちは！元気でしたか？何かお困りのことがあれば教えてください。"
                    ],
                    'with_name': [
                        "こんにちは、{user_name}さん！今日もよろしくお願いします😊",
                        "{user_name}さん、こんにちは！今日はどのようなことでお手伝いできますか？",
                        "お疲れ様です、{user_name}さん！何かお困りのことがあればお聞かせください。"
                    ]
                },
                'general': [
                    "こんにちは！今日はどのようなことをお手伝いできますか？😊",
                    "お疲れ様です！何かご質問はありますか？",
                    "こんにちは！お気軽に何でもお聞きください。"
                ]
            },

            # 質問への応答
            'question': {
                'technology': {
                    'simple': [
                        "技術的なご質問ですね！お答えしますので、少々お待ちください。",
                        "{user_name}さんのご質問にお答えします。",
                        "良いご質問ですね！詳しく説明させていただきます。"
                    ],
                    'complex': [
                        "とても興味深い技術的なご質問ですね。詳しく説明させていただきます。",
                        "少し複雑な内容ですが、分かりやすく説明しますね。",
                        "素晴らしいご質問です！{user_name}さんの技術への関心がよく伝わります。"
                    ],
                    'personal_context': [
                        "{user_name}さんが{user_interests}に興味をお持ちということを踏まえてお答えします。",
                        "{user_name}さんの技術的なバックグラウンドを考慮してご説明しますね。"
                    ]
                },
                'personal': {
                    'simple': [
                        "個人的なことについてのご質問ですね。お答えします。",
                        "プライベートなことですね。お聞かせください。",
                        "{user_name}さんのことについてですね。"
                    ],
                    'complex': [
                        "詳しく教えてください。{user_name}さんのお話を聞かせていただけると嬉しいです。",
                        "もう少し詳しくお聞かせください。"
                    ]
                },
                'memory_test': [
                    "もちろん覚えています！{user_name}さんとお話した{previous_topic}のことですね😊",
                    "はい、{previous_topic}についてお話しましたね。覚えていますよ！",
                    "{user_name}さんの{previous_topic}への関心、しっかり覚えています。"
                ]
            },

            # 情報提供への応答
            'information': {
                'technology': {
                    'acknowledge': [
                        "技術的な情報をありがとうございます！{topic}について勉強になりました。",
                        "{user_name}さんの{topic}の知識、素晴らしいですね！",
                        "とても参考になります。{topic}について教えていただき、ありがとうございます。"
                    ],
                    'followup': [
                        "とても興味深い{topic}のお話ですね！もう少し詳しく教えていただけますか？",
                        "{topic}について、さらに詳しく知りたいです。",
                        "{user_name}さんの{topic}の経験、もっとお聞かせください。"
                    ],
                    'new_project': [
                        "新しい{topic}プロジェクト、とても楽しそうですね！",
                        "{topic}のプロジェクト開始、おめでとうございます！どのような内容ですか？",
                        "素晴らしい！{user_name}さんの新しい{topic}への挑戦、応援しています。"
                    ]
                },
                'personal': {
                    'acknowledge': [
                        "お教えいただき、ありがとうございます。{user_name}さんのことがよく分かりました😊",
                        "{user_name}さんのお話、とても興味深いです。",
                        "貴重なお話をありがとうございます。"
                    ],
                    'remember': [
                        "しっかり覚えさせていただきますね。{user_name}さんのことをもっと知ることができて嬉しいです。",
                        "覚えておきます！また{topic}のことでお話しできると嬉しいです。",
                        "{user_name}さんの{topic}について、今度また詳しくお聞かせください。"
                    ]
                }
            },

            # 感謝・お礼への応答
            'thanks': [
                "どういたしまして！お役に立てて嬉しいです😊",
                "{user_name}さんのお役に立てたようで良かったです。",
                "こちらこそ、いつもありがとうございます！",
                "また何かあれば、いつでもお声かけください。"
            ],

            # チャット・雑談への応答
            'chat': {
                'technology': [
                    "{user_name}さんの技術的なお話、いつも勉強になります。",
                    "技術の話題、とても興味深いです。",
                    "{user_name}さんの技術への情熱が伝わってきます。"
                ],
                'general': [
                    "{user_name}さんとお話しできて楽しいです😊",
                    "そうですね。{user_name}さんはどう思われますか？",
                    "面白いお話ですね。"
                ]
            }
        }

    def get_user_context(self, user_id: str) -> Dict:
        """ユーザーコンテキストの取得（改善版）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        context = {
            'user_name': None,
            'interests': [],
            'conversation_count': 0,
            'last_topic': None,
            'recent_topics': [],
            'behavior_patterns': {}
        }

        try:
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
                        interests_list = json.loads(interests) if isinstance(interests, str) else [interests]
                        context['interests'] = interests_list
                    except:
                        context['interests'] = [interests] if interests else []

            # ユーザー名の推測（より精密に）
            cursor.execute("""
                SELECT content
                FROM conversation_history
                WHERE user_id = ? AND message_type = 'human'
                AND content LIKE '%名前%'
                ORDER BY timestamp DESC
                LIMIT 3
            """, (user_id,))

            name_messages = cursor.fetchall()
            for msg in name_messages:
                content = msg[0]
                # より柔軟な名前抽出
                name = self.extract_user_name(content)
                if name:
                    context['user_name'] = name
                    break

            # 最近のトピック取得（改善版）
            cursor.execute("""
                SELECT cm.topic_category, ch.content, ch.timestamp
                FROM conversation_metadata cm
                JOIN conversation_history ch ON cm.conversation_id = ch.id
                WHERE ch.user_id = ? AND ch.message_type = 'human'
                ORDER BY ch.timestamp DESC
                LIMIT 5
            """, (user_id,))

            recent_data = cursor.fetchall()
            context['recent_topics'] = [row[0] for row in recent_data]

            if recent_data:
                context['last_topic'] = recent_data[0][0]

        except Exception as e:
            print(f"[WARNING] Error getting user context: {e}")

        finally:
            conn.close()

        return context

    def extract_user_name(self, content: str) -> Optional[str]:
        """より精密なユーザー名抽出"""
        patterns = [
            r'私の名前は(.+?)です',
            r'私は(.+?)です',
            r'名前は(.+?)です',
            r'(.+?)と申します',
            r'(.+?)といいます'
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                name = match.group(1).strip()
                # 名前っぽいかチェック（短くて、変な文字が含まれていない）
                if 1 <= len(name) <= 10 and not any(char in name for char in ['？', '?', '何', 'どこ', 'いつ']):
                    return name

        return None

    def analyze_message_advanced(self, content: str) -> Dict:
        """高度なメッセージ分析"""
        analysis = {
            'intent': 'chat',
            'topic_category': 'general',
            'is_memory_test': False,
            'is_gratitude': False,
            'complexity_level': 1,
            'keywords': []
        }

        content_lower = content.lower()

        # 記憶テストの検出
        memory_patterns = ['覚えて', '記憶', '前回', '以前', '話した', '言った']
        if any(pattern in content for pattern in memory_patterns):
            analysis['is_memory_test'] = True
            analysis['intent'] = 'question'

        # 感謝表現の検出
        thanks_patterns = ['ありがとう', 'ありがとうございます', '感謝', 'お礼']
        if any(pattern in content for pattern in thanks_patterns):
            analysis['is_gratitude'] = True
            analysis['intent'] = 'thanks'

        # 挨拶の検出
        greeting_patterns = ['こんにちは', 'おはよう', 'こんばんは', 'はじめまして', 'よろしく']
        if any(pattern in content for pattern in greeting_patterns):
            analysis['intent'] = 'greeting'

        # 質問の検出
        question_patterns = ['？', '?', 'どう', 'なに', 'なん', 'いつ', 'どこ', 'だれ', 'なぜ', 'どのように', 'ですか', 'ますか']
        if any(pattern in content for pattern in question_patterns):
            analysis['intent'] = 'question'

        # 情報提供の検出
        info_patterns = ['です', 'ます', 'している', 'した', 'します', 'になりました', 'です。']
        if any(pattern in content for pattern in info_patterns) and analysis['intent'] == 'chat':
            analysis['intent'] = 'information'

        # トピック分類
        tech_keywords = ['プログラミング', 'Python', 'コード', '開発', 'システム', 'アプリ', 'データベース', '機械学習', 'AI', 'データ分析']
        if any(keyword in content for keyword in tech_keywords):
            analysis['topic_category'] = 'technology'

            # 新プロジェクトの検出
            if '新しい' in content or '始め' in content or 'プロジェクト' in content:
                analysis['intent'] = 'information'
                analysis['is_new_project'] = True

        # 個人情報の検出
        personal_keywords = ['名前', '住んで', '趣味', '好き', '家族', '年齢', '出身']
        if any(keyword in content for keyword in personal_keywords):
            analysis['topic_category'] = 'personal'

        # 複雑度計算
        analysis['complexity_level'] = min(len(content) // 15 + 1, 5)

        return analysis

    def select_best_template(self, intent: str, topic: str, user_context: Dict, message_analysis: Dict) -> str:
        """最適なテンプレートを選択"""
        templates = self.response_templates

        # 記憶テスト特別処理
        if message_analysis.get('is_memory_test', False):
            if 'question' in templates and 'memory_test' in templates['question']:
                return self.random_choice(templates['question']['memory_test'])

        # 感謝表現特別処理
        if message_analysis.get('is_gratitude', False):
            return self.random_choice(templates['thanks'])

        # 通常の処理
        if intent in templates:
            intent_templates = templates[intent]

            if isinstance(intent_templates, list):
                return self.random_choice(intent_templates)

            if topic in intent_templates:
                topic_templates = intent_templates[topic]

                if isinstance(topic_templates, list):
                    return self.random_choice(topic_templates)

                if isinstance(topic_templates, dict):
                    # コンテキストに基づく選択
                    if user_context.get('user_name') and 'with_name' in topic_templates:
                        return self.random_choice(topic_templates['with_name'])
                    elif user_context.get('conversation_count', 0) == 0 and 'new_user' in topic_templates:
                        return self.random_choice(topic_templates['new_user'])
                    elif user_context.get('conversation_count', 0) > 0 and 'returning_user' in topic_templates:
                        return self.random_choice(topic_templates['returning_user'])
                    elif message_analysis.get('complexity_level', 1) > 3 and 'complex' in topic_templates:
                        return self.random_choice(topic_templates['complex'])
                    elif message_analysis.get('is_new_project', False) and 'new_project' in topic_templates:
                        return self.random_choice(topic_templates['new_project'])
                    elif 'simple' in topic_templates:
                        return self.random_choice(topic_templates['simple'])
                    elif 'acknowledge' in topic_templates:
                        return self.random_choice(topic_templates['acknowledge'])
                    else:
                        # フォールバック：最初のテンプレートを使用
                        first_key = list(topic_templates.keys())[0]
                        return self.random_choice(topic_templates[first_key])

        # フォールバック応答
        fallback_responses = [
            "ありがとうございます。お話しいただき、嬉しいです😊",
            "なるほど、そうですね。もう少し詳しく教えていただけますか？",
            "面白いお話ですね。続きをお聞かせください。"
        ]

        return self.random_choice(fallback_responses)

    def random_choice(self, templates):
        """テンプレートからランダム選択（時間ベースシード）"""
        import random
        # 秒単位でシードを変える（同じ秒内では同じ選択）
        seed = int(datetime.now().timestamp()) % 1000
        random.seed(seed)
        return random.choice(templates)

    def format_template(self, template: str, user_context: Dict, message_analysis: Dict, original_message: str) -> str:
        """テンプレートに値を埋め込み"""
        formatted = template

        # ユーザー名の埋め込み
        if user_context.get('user_name'):
            formatted = formatted.replace('{user_name}', user_context['user_name'])
        else:
            # ユーザー名がない場合のフォールバック
            formatted = formatted.replace('{user_name}さん', 'あなた')
            formatted = formatted.replace('{user_name}', '')

        # 興味・関心の埋め込み
        if user_context.get('interests'):
            interests_text = '、'.join(user_context['interests'][:2])  # 最初の2つまで
            formatted = formatted.replace('{user_interests}', interests_text)
        else:
            formatted = formatted.replace('{user_interests}', '技術')

        # トピックの埋め込み
        topic_mapping = {
            'technology': '技術',
            'personal': '個人的なこと',
            'general': '一般的なこと',
            'work': '仕事',
            'time': '時間'
        }

        topic_ja = topic_mapping.get(message_analysis['topic_category'], message_analysis['topic_category'])
        formatted = formatted.replace('{topic}', topic_ja)

        # 前回のトピックを埋め込み
        if user_context.get('last_topic'):
            last_topic_ja = topic_mapping.get(user_context['last_topic'], user_context['last_topic'])
            formatted = formatted.replace('{previous_topic}', last_topic_ja)

        # 残った未置換変数をクリーンアップ
        formatted = re.sub(r'\{[^}]+\}', '', formatted)

        # 余分な空白を削除
        formatted = re.sub(r'\s+', ' ', formatted).strip()

        return formatted

    def generate_improved_response(self, user_id: str, message: str) -> Dict:
        """改善された応答生成"""
        try:
            # 1. ユーザーコンテキスト取得
            user_context = self.get_user_context(user_id)

            # 2. メッセージ分析
            message_analysis = self.analyze_message_advanced(message)

            # 3. 最適なテンプレート選択
            template = self.select_best_template(
                message_analysis['intent'],
                message_analysis['topic_category'],
                user_context,
                message_analysis
            )

            # 4. テンプレートの埋め込み
            final_response = self.format_template(template, user_context, message_analysis, message)

            # 5. 品質評価
            quality_score = self.evaluate_response_quality(final_response, message_analysis, user_context)

            return {
                'response': final_response,
                'response_type': 'improved_template',
                'quality_score': quality_score,
                'user_context': user_context,
                'message_analysis': message_analysis,
                'template_used': template
            }

        except Exception as e:
            print(f"[ERROR] Improved response generation failed: {e}")
            return {
                'response': "申し訳ございません。少し時間をおいて、もう一度お試しください。",
                'response_type': 'error_fallback',
                'error': str(e)
            }

    def evaluate_response_quality(self, response: str, analysis: Dict, user_context: Dict) -> float:
        """応答品質の評価（改善版）"""
        score = 0.0
        max_score = 5.0

        # 基本的な応答の存在
        if response and len(response.strip()) > 0:
            score += 1.0

        # 自然な長さ
        if 10 <= len(response) <= 150:
            score += 1.0
        elif 5 <= len(response) <= 200:
            score += 0.5

        # パーソナライゼーション
        if user_context.get('user_name') and user_context['user_name'] in response:
            score += 1.0
        elif 'あなた' in response or 'さん' in response:
            score += 0.5

        # 感情表現・絵文字
        if '😊' in response or '！' in response or 'ですね' in response:
            score += 0.5

        # 意図との適合性
        intent_keywords = {
            'greeting': ['こんにちは', 'はじめまして', 'よろしく'],
            'question': ['お答え', 'ご質問', '説明'],
            'information': ['ありがとう', '教えて', '興味深い'],
            'thanks': ['どういたしまして', 'お役に立て']
        }

        if analysis['intent'] in intent_keywords:
            if any(keyword in response for keyword in intent_keywords[analysis['intent']]):
                score += 1.0

        # コンテキストの活用
        if user_context.get('interests') and any(interest in response for interest in user_context['interests']):
            score += 0.5

        return min(score, max_score)

def test_improved_response_system():
    """改善された応答システムのテスト"""
    print("🎯 改善された応答テンプレートシステムテスト")
    print("=" * 60)

    db_path = 'Lesson25/uma3soft-app/db/conversation_history.db'

    if not os.path.exists(db_path):
        print(f"❌ データベースファイルが見つかりません: {db_path}")
        return

    # システム初期化
    generator = ImprovedResponseGenerator(db_path)

    # テストユーザー
    test_user_id = "TEST_IMPROVED_USER_001"

    # まず、テスト用ユーザー情報を設定
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # テスト用の会話履歴を作成
    test_conversations = [
        ("私の名前は佐藤太郎です。", "human"),
        ("はじめまして、佐藤太郎さん！", "ai"),
        ("プログラミングに興味があります。", "human"),
        ("素晴らしいご興味ですね！", "ai")
    ]

    cursor.execute("DELETE FROM conversation_history WHERE user_id = ?", (test_user_id,))
    cursor.execute("DELETE FROM user_profiles WHERE user_id = ?", (test_user_id,))

    for i, (content, msg_type) in enumerate(test_conversations):
        cursor.execute("""
            INSERT INTO conversation_history (user_id, content, message_type, timestamp, session_id)
            VALUES (?, ?, ?, ?, ?)
        """, (test_user_id, content, msg_type, datetime.now().isoformat(), f"test_session_{i}"))

    # ユーザープロフィール作成
    cursor.execute("""
        INSERT INTO user_profiles (user_id, interests, conversation_count)
        VALUES (?, ?, ?)
    """, (test_user_id, json.dumps(["プログラミング", "Python"], ensure_ascii=False), 2))

    conn.commit()
    conn.close()

    # テストメッセージ
    test_messages = [
        "こんにちは！今日もよろしくお願いします",
        "前回話したプログラミングの件、覚えてる？",
        "私の名前、覚えていますか？",
        "新しいPythonプロジェクトを始めました",
        "ありがとうございました",
        "機械学習について教えてください",
        "データ分析の勉強をしています"
    ]

    print(f"\n👤 テストユーザー: {test_user_id}")
    print(f"🧪 改善されたテンプレートシステムのテスト")
    print("-" * 60)

    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. ユーザー入力: '{message}'")
        print("-" * 40)

        try:
            result = generator.generate_improved_response(test_user_id, message)

            print(f"🤖 改善応答: {result['response']}")
            print(f"📊 応答タイプ: {result['response_type']}")
            print(f"⭐ 品質スコア: {result['quality_score']:.1f}/5.0")

            # 分析情報
            analysis = result['message_analysis']
            print(f"🔍 分析:")
            print(f"   意図: {analysis['intent']}")
            print(f"   トピック: {analysis['topic_category']}")
            print(f"   記憶テスト: {analysis.get('is_memory_test', False)}")
            print(f"   感謝表現: {analysis.get('is_gratitude', False)}")

            # ユーザーコンテキスト
            user_context = result['user_context']
            print(f"👤 コンテキスト:")
            print(f"   名前: {user_context.get('user_name', 'なし')}")
            print(f"   会話回数: {user_context.get('conversation_count', 0)}")
            print(f"   興味: {user_context.get('interests', [])}")

        except Exception as e:
            print(f"❌ エラー: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n🎉 改善されたテンプレートシステムテスト完了！")
    print("📈 品質向上のポイント:")
    print("   ✅ 自然な日本語応答")
    print("   ✅ パーソナライゼーション")
    print("   ✅ コンテキスト活用")
    print("   ✅ 感情表現・絵文字")
    print("   ✅ 意図に応じた応答選択")

if __name__ == "__main__":
    print(f"📅 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    test_improved_response_system()
