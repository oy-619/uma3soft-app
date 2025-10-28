"""
Phase 3: 統合会話システムの改善
既存のintegrated_conversation_systemにインテリジェント応答生成を統合

改善ポイント：
1. パーソナライズされた応答生成
2. 会話品質の向上
3. ユーザーコンテキストの活用
4. 継続的学習機能
"""

import os
import sys
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# パス設定
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), 'src')
sys.path.insert(0, src_dir)

class EnhancedIntegratedConversationSystem:
    """拡張統合会話システム"""

    def __init__(self, chroma_path: str, conversation_db_path: str):
        # 既存のコンポーネントを初期化
        try:
            from integrated_conversation_system import IntegratedConversationSystem
            self.base_system = IntegratedConversationSystem(chroma_path, conversation_db_path)
            print("[ENHANCED] Base integrated system loaded")
        except Exception as e:
            print(f"[WARNING] Could not load base system: {e}")
            self.base_system = None

        # 拡張機能を初期化
        self.db_path = conversation_db_path
        self.setup_enhanced_features()

    def setup_enhanced_features(self):
        """拡張機能のセットアップ"""
        # Phase 1 & 2のクラスをインポート
        try:
            sys.path.append(os.path.dirname(__file__))
            from phase1_enhanced_learning import EnhancedConversationAnalyzer
            from phase2_intelligent_response import IntelligentResponseGenerator

            self.analyzer = EnhancedConversationAnalyzer(self.db_path)
            self.response_generator = IntelligentResponseGenerator(self.db_path)
            print("[ENHANCED] Advanced analysis and response generation loaded")
        except Exception as e:
            print(f"[WARNING] Could not load enhanced features: {e}")
            self.analyzer = None
            self.response_generator = None

    def generate_enhanced_response(self, user_id: str, user_message: str, llm=None) -> Dict:
        """拡張された応答生成"""

        try:
            # 1. 基本的な統合システムでの応答生成（既存機能）
            base_result = None
            if self.base_system and llm:
                try:
                    base_result = self.base_system.generate_integrated_response(user_id, user_message, llm)
                    print("[ENHANCED] Base system response generated")
                except Exception as e:
                    print(f"[WARNING] Base system failed: {e}")

            # 2. 拡張された分析と応答生成
            enhanced_result = None
            if self.response_generator:
                try:
                    enhanced_result = self.response_generator.generate_personalized_response(user_id, user_message)
                    print("[ENHANCED] Personalized response generated")
                except Exception as e:
                    print(f"[WARNING] Enhanced response generation failed: {e}")

            # 3. 最適な応答の選択と組み合わせ
            final_response = self.combine_responses(base_result, enhanced_result, user_message)

            # 4. 会話履歴の保存（拡張メタデータ付き）
            self.save_enhanced_conversation(user_id, user_message, final_response)

            return final_response

        except Exception as e:
            print(f"[ERROR] Enhanced response generation failed: {e}")
            # フォールバック: シンプルな応答
            return {
                'response': "申し訳ございません。一時的に応答生成に問題が発生しています。もう一度お試しください。",
                'response_type': 'fallback',
                'error': str(e)
            }

    def combine_responses(self, base_result: Optional[Dict], enhanced_result: Optional[Dict], user_message: str) -> Dict:
        """基本応答と拡張応答を組み合わせ"""

        # 両方の結果がある場合
        if base_result and enhanced_result and 'error' not in base_result:
            base_response = base_result.get('response', '')
            enhanced_response = enhanced_result.get('response', '')

            # 拡張応答の品質スコアを確認
            quality_score = enhanced_result.get('quality_score', 0)

            if quality_score >= 3.0:
                # 高品質な拡張応答がある場合、それをメインに使用
                # 基本応答から有用な情報があれば追加
                combined_response = enhanced_response

                # ChromaDBからの情報を追加
                context_info = base_result.get('context_used', {})
                chroma_results = context_info.get('chroma_results', 0)

                if chroma_results > 0 and len(base_response) > len(enhanced_response) * 1.5:
                    # 基本応答に豊富な情報がある場合は組み合わせ
                    combined_response = f"{enhanced_response}\n\n{base_response}"

                return {
                    'response': combined_response,
                    'response_type': 'enhanced_with_chroma',
                    'quality_score': quality_score,
                    'context_used': context_info,
                    'personalization_used': enhanced_result.get('personalization_used', {}),
                    'chroma_enhanced': chroma_results > 0
                }
            else:
                # 拡張応答の品質が低い場合は基本応答を使用
                return {
                    'response': base_response,
                    'response_type': 'base_system',
                    'context_used': base_result.get('context_used', {}),
                    'fallback_reason': 'low_quality_enhanced_response'
                }

        # 拡張応答のみがある場合
        elif enhanced_result:
            return {
                'response': enhanced_result['response'],
                'response_type': 'enhanced_only',
                'quality_score': enhanced_result.get('quality_score', 0),
                'personalization_used': enhanced_result.get('personalization_used', {})
            }

        # 基本応答のみがある場合
        elif base_result and 'error' not in base_result:
            return {
                'response': base_result['response'],
                'response_type': 'base_only',
                'context_used': base_result.get('context_used', {})
            }

        # フォールバック
        else:
            return {
                'response': f"ご質問ありがとうございます。「{user_message}」について、もう少し詳しく教えていただけますか？",
                'response_type': 'simple_fallback'
            }

    def save_enhanced_conversation(self, user_id: str, user_message: str, response_result: Dict):
        """拡張メタデータ付きで会話を保存"""
        try:
            if self.base_system and hasattr(self.base_system, 'history_manager'):
                # 基本的な会話履歴保存
                ai_response = response_result.get('response', '')

                metadata = {
                    'source': 'enhanced_system',
                    'response_type': response_result.get('response_type', 'unknown'),
                    'quality_score': response_result.get('quality_score', 0)
                }

                # パーソナライゼーション情報も保存
                personalization = response_result.get('personalization_used', {})
                if personalization:
                    metadata['personalization'] = json.dumps(personalization, ensure_ascii=False)

                self.base_system.history_manager.save_conversation(
                    user_id, user_message, ai_response, metadata=metadata
                )
                print("[ENHANCED] Conversation saved with enhanced metadata")

            # 拡張メタデータの保存
            if self.analyzer:
                self.save_conversation_analysis(user_id, user_message, response_result)

        except Exception as e:
            print(f"[WARNING] Failed to save enhanced conversation: {e}")

    def save_conversation_analysis(self, user_id: str, user_message: str, response_result: Dict):
        """会話分析結果の保存"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 最新の会話IDを取得
            cursor.execute("""
                SELECT id FROM conversation_history
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (user_id,))

            result = cursor.fetchone()
            if result:
                conversation_id = result[0]

                # メタデータを保存
                intent = self.analyzer.analyze_conversation_intent(user_message)
                sentiment = self.analyzer.analyze_sentiment(user_message)
                topic_category = self.analyzer.categorize_topic(user_message)
                complexity_level = self.analyzer.calculate_complexity_level(user_message)
                keywords = self.analyzer.extract_keywords(user_message)

                cursor.execute("""
                    INSERT OR REPLACE INTO conversation_metadata
                    (conversation_id, intent, sentiment, topic_category, complexity_level,
                     response_quality, keywords)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    conversation_id, intent, sentiment, topic_category,
                    complexity_level, response_result.get('quality_score', 0),
                    json.dumps(keywords, ensure_ascii=False)
                ))

                conn.commit()
                print("[ENHANCED] Conversation analysis saved")

            conn.close()

        except Exception as e:
            print(f"[WARNING] Failed to save conversation analysis: {e}")

    def get_conversation_insights(self, user_id: str) -> Dict:
        """ユーザーの会話インサイトを取得"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            insights = {}

            # 基本統計
            cursor.execute("""
                SELECT COUNT(*)
                FROM conversation_history
                WHERE user_id = ? AND message_type = 'human'
            """, (user_id,))
            total_messages = cursor.fetchone()[0]

            # 意図別統計
            cursor.execute("""
                SELECT cm.intent, COUNT(*)
                FROM conversation_metadata cm
                JOIN conversation_history ch ON cm.conversation_id = ch.id
                WHERE ch.user_id = ?
                GROUP BY cm.intent
            """, (user_id,))
            intent_stats = dict(cursor.fetchall())

            # トピック別統計
            cursor.execute("""
                SELECT cm.topic_category, COUNT(*)
                FROM conversation_metadata cm
                JOIN conversation_history ch ON cm.conversation_id = ch.id
                WHERE ch.user_id = ?
                GROUP BY cm.topic_category
            """, (user_id,))
            topic_stats = dict(cursor.fetchall())

            # 平均応答品質
            cursor.execute("""
                SELECT AVG(cm.response_quality)
                FROM conversation_metadata cm
                JOIN conversation_history ch ON cm.conversation_id = ch.id
                WHERE ch.user_id = ? AND cm.response_quality > 0
            """, (user_id,))
            avg_quality = cursor.fetchone()[0] or 0

            insights = {
                'total_messages': total_messages,
                'intent_distribution': intent_stats,
                'topic_distribution': topic_stats,
                'average_response_quality': round(avg_quality, 2),
                'user_id': user_id[:20] + '...'
            }

            conn.close()
            return insights

        except Exception as e:
            print(f"[WARNING] Failed to get conversation insights: {e}")
            return {}

def test_enhanced_integrated_system():
    """拡張統合システムのテスト"""
    print("🚀 Phase 3: 拡張統合会話システムテスト")
    print("=" * 70)

    chroma_path = 'Lesson25/uma3soft-app/db/chroma_store'
    db_path = 'Lesson25/uma3soft-app/db/conversation_history.db'

    # システム初期化
    enhanced_system = EnhancedIntegratedConversationSystem(chroma_path, db_path)

    # テストユーザー
    test_user_id = "TEST_ENHANCED_USER_001"

    # テストメッセージ
    test_messages = [
        "こんにちは！私の名前は山田太郎です。",
        "機械学習について教えてください",
        "前回話したことを覚えていますか？",
        "Pythonでのデータ分析に興味があります",
        "ありがとうございました"
    ]

    print(f"\n👤 テストユーザー: {test_user_id}")
    print(f"🧪 テストケース数: {len(test_messages)}")
    print("-" * 50)

    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. ユーザー入力: '{message}'")
        print("-" * 40)

        try:
            # 拡張応答生成（LLMなしでテスト）
            result = enhanced_system.generate_enhanced_response(test_user_id, message)

            print(f"🤖 システム応答: {result['response']}")
            print(f"📊 応答タイプ: {result['response_type']}")

            if 'quality_score' in result:
                print(f"⭐ 品質スコア: {result['quality_score']:.1f}/5.0")

            if 'personalization_used' in result:
                personalization = result['personalization_used']
                if personalization:
                    print("👤 パーソナライゼーション:")
                    for key, value in personalization.items():
                        print(f"   {key}: {value}")

            if 'context_used' in result:
                context = result['context_used']
                if context:
                    print(f"📚 コンテキスト: ChromaDB {context.get('chroma_results', 0)}件")

        except Exception as e:
            print(f"❌ エラー: {e}")
            import traceback
            traceback.print_exc()

    # 会話インサイトの表示
    print(f"\n📊 会話インサイト分析")
    print("-" * 50)

    insights = enhanced_system.get_conversation_insights(test_user_id)

    if insights:
        print(f"💬 総メッセージ数: {insights['total_messages']}")
        print(f"📈 平均応答品質: {insights['average_response_quality']}/5.0")

        if insights['intent_distribution']:
            print("🎯 意図分布:")
            for intent, count in insights['intent_distribution'].items():
                print(f"   {intent}: {count}回")

        if insights['topic_distribution']:
            print("🏷️ トピック分布:")
            for topic, count in insights['topic_distribution'].items():
                print(f"   {topic}: {count}回")

    print(f"\n🎉 拡張統合システムテスト完了！")
    print(f"💡 このシステムは実際のLINE Botに統合可能です。")

if __name__ == "__main__":
    print(f"📅 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    test_enhanced_integrated_system()
