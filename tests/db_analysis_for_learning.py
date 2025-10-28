"""
データベース分析による回答精度向上のための学習方法提案

このスクリプトは以下の分析を行います：
1. 会話履歴データの量的・質的分析
2. ユーザープロフィールの学習パターン分析
3. ChromaDBの検索精度分析
4. 回答品質向上のための学習方法提案
"""

import os
import sys
import sqlite3
import json
from datetime import datetime, timedelta
from collections import Counter
import re

# パス設定
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), 'src')
sys.path.insert(0, src_dir)

def analyze_conversation_database():
    """会話データベースの詳細分析"""
    print("=" * 70)
    print("🔍 会話データベース分析 - 回答精度向上のための学習方法提案")
    print("=" * 70)

    db_path = 'Lesson25/uma3soft-app/db/conversation_history.db'

    if not os.path.exists(db_path):
        print(f"❌ データベースファイルが見つかりません: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. 基本統計情報
    print("\n📊 1. 基本統計情報")
    print("-" * 50)

    # ユーザー数とメッセージ数
    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM conversation_history;")
    user_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM conversation_history;")
    message_count = cursor.fetchone()[0]

    print(f"   👥 総ユーザー数: {user_count}")
    print(f"   💬 総メッセージ数: {message_count}")

    if user_count > 0:
        avg_messages = message_count / user_count
        print(f"   📈 ユーザーあたり平均メッセージ数: {avg_messages:.1f}")

    # 2. ユーザー別会話分析
    print(f"\n👤 2. ユーザー別会話分析")
    print("-" * 50)

    cursor.execute("""
        SELECT user_id, COUNT(*) as msg_count,
               MIN(timestamp) as first_msg,
               MAX(timestamp) as last_msg
        FROM conversation_history
        GROUP BY user_id
        ORDER BY msg_count DESC
        LIMIT 10;
    """)

    user_stats = cursor.fetchall()

    for i, (user_id, msg_count, first_msg, last_msg) in enumerate(user_stats, 1):
        print(f"   {i}. ユーザー: {user_id[:20]}...")
        print(f"      メッセージ数: {msg_count}")
        print(f"      期間: {first_msg} ～ {last_msg}")

        # 会話の継続性分析
        try:
            first_dt = datetime.fromisoformat(first_msg)
            last_dt = datetime.fromisoformat(last_msg)
            duration = last_dt - first_dt
            print(f"      会話期間: {duration.days}日")
        except:
            print(f"      会話期間: 計算不可")
        print()

    # 3. メッセージタイプ分析
    print(f"\n💭 3. メッセージタイプ分析")
    print("-" * 50)

    cursor.execute("""
        SELECT message_type, COUNT(*) as count
        FROM conversation_history
        GROUP BY message_type;
    """)

    message_types = cursor.fetchall()
    for msg_type, count in message_types:
        percentage = (count / message_count) * 100 if message_count > 0 else 0
        print(f"   {msg_type}: {count}件 ({percentage:.1f}%)")

    # 4. 会話内容の質的分析
    print(f"\n📝 4. 会話内容の質的分析")
    print("-" * 50)

    # 人間のメッセージを分析
    cursor.execute("""
        SELECT content FROM conversation_history
        WHERE message_type = 'human' AND content != ''
        ORDER BY timestamp DESC
        LIMIT 50;
    """)

    human_messages = [row[0] for row in cursor.fetchall()]

    # メッセージ長の統計
    if human_messages:
        message_lengths = [len(msg) for msg in human_messages]
        avg_length = sum(message_lengths) / len(message_lengths)
        max_length = max(message_lengths)
        min_length = min(message_lengths)

        print(f"   📏 メッセージ長統計（最新50件）:")
        print(f"      平均長: {avg_length:.1f}文字")
        print(f"      最大長: {max_length}文字")
        print(f"      最小長: {min_length}文字")

    # 5. キーワード分析
    print(f"\n🔤 5. よく使われるキーワード")
    print("-" * 50)

    # すべての人間のメッセージからキーワードを抽出
    cursor.execute("""
        SELECT content FROM conversation_history
        WHERE message_type = 'human' AND content != '';
    """)

    all_human_content = [row[0] for row in cursor.fetchall()]

    # 日本語キーワードの抽出（簡易版）
    keywords = []
    for content in all_human_content:
        # カタカナ、ひらがな、漢字の単語を抽出
        words = re.findall(r'[ァ-ヶー]+|[あ-んー]+|[一-龯]+', content)
        # 2文字以上の単語のみ
        keywords.extend([word for word in words if len(word) >= 2])

    if keywords:
        keyword_freq = Counter(keywords)
        print(f"   頻出キーワード（上位10位）:")
        for keyword, freq in keyword_freq.most_common(10):
            print(f"      {keyword}: {freq}回")
    else:
        print("   キーワードが見つかりませんでした")

    # 6. ユーザープロフィール分析
    print(f"\n👥 6. ユーザープロフィール学習状況")
    print("-" * 50)

    try:
        cursor.execute("SELECT * FROM user_profiles;")
        profiles = cursor.fetchall()

        if profiles:
            print(f"   登録プロフィール数: {len(profiles)}")
            for profile in profiles[:5]:  # 最初の5件を表示
                user_id, profile_data, interests, conv_count, last_interaction, created_at, updated_at = profile
                print(f"   ユーザー: {user_id[:20]}...")
                print(f"      会話回数: {conv_count}")
                print(f"      興味・関心: {interests}")
                print(f"      最終更新: {updated_at}")
                print()
        else:
            print("   プロフィールデータがありません")
    except Exception as e:
        print(f"   プロフィール分析エラー: {e}")

    conn.close()

def analyze_chromadb_performance():
    """ChromaDBの検索性能分析"""
    print(f"\n🗄️ 7. ChromaDB検索性能分析")
    print("-" * 50)

    try:
        from uma3_chroma_improver import Uma3ChromaImprover

        chroma_path = 'Lesson25/uma3soft-app/db/chroma_store'
        improver = Uma3ChromaImprover(chroma_path)

        # テスト用クエリ
        test_queries = [
            "プログラミング",
            "Python",
            "会議",
            "スケジュール",
            "明日",
            "今日の予定",
            "技術的な質問",
            "個人的な話"
        ]

        print(f"   テストクエリによる検索性能:")

        for query in test_queries:
            try:
                results = improver.schedule_aware_search(query, k=3, score_threshold=0.5)
                print(f"      '{query}': {len(results)}件の結果")

                if results:
                    # 最初の結果のスコア（もしあれば）
                    first_result = results[0]
                    content_preview = first_result.page_content[:50] + "..." if len(first_result.page_content) > 50 else first_result.page_content
                    print(f"         例: {content_preview}")

            except Exception as e:
                print(f"      '{query}': エラー - {e}")

    except Exception as e:
        print(f"   ChromaDB分析エラー: {e}")

def propose_learning_improvements():
    """回答精度向上のための学習方法提案"""
    print(f"\n🚀 8. 回答精度向上のための学習方法提案")
    print("=" * 70)

    proposals = [
        {
            "title": "📚 会話履歴の質的向上",
            "methods": [
                "会話のコンテキスト情報を充実させる",
                "メタデータに感情や意図の情報を追加",
                "会話の成功/失敗フラグを記録",
                "ユーザー満足度のフィードバック収集"
            ]
        },
        {
            "title": "🧠 ユーザープロフィールの強化",
            "methods": [
                "興味・関心の自動カテゴリ分類",
                "会話パターンの学習と予測",
                "時間帯別の行動パターン分析",
                "専門用語や業界特有の言葉の学習"
            ]
        },
        {
            "title": "🔍 検索精度の向上",
            "methods": [
                "セマンティック検索の精度調整",
                "ユーザー固有の語彙重み付け",
                "会話履歴とChromaDBの統合重み調整",
                "クエリの意図理解の改善"
            ]
        },
        {
            "title": "💡 応答生成の改善",
            "methods": [
                "プロンプトテンプレートの最適化",
                "会話の文脈継続性の向上",
                "パーソナライゼーションの強化",
                "応答の一貫性チェック機能"
            ]
        },
        {
            "title": "📊 継続的学習システム",
            "methods": [
                "A/Bテストによる応答品質評価",
                "ユーザーフィードバックの自動分析",
                "応答品質メトリクスの定義と測定",
                "定期的なモデル性能評価"
            ]
        }
    ]

    for i, proposal in enumerate(proposals, 1):
        print(f"\n{i}. {proposal['title']}")
        print("-" * 50)
        for method in proposal['methods']:
            print(f"   ✅ {method}")

def generate_implementation_roadmap():
    """実装ロードマップの生成"""
    print(f"\n🗺️ 9. 実装ロードマップ")
    print("=" * 70)

    phases = [
        {
            "phase": "Phase 1: データ基盤強化（1-2週間）",
            "tasks": [
                "会話履歴のメタデータ拡張",
                "ユーザープロフィールのスキーマ改善",
                "データ品質チェック機能の追加",
                "バックアップとリストア機能"
            ]
        },
        {
            "phase": "Phase 2: 検索・マッチング改善（2-3週間）",
            "tasks": [
                "ChromaDBの埋め込みモデル調整",
                "ユーザー固有の検索重み付け",
                "会話コンテキストの改善",
                "検索結果の品質メトリクス"
            ]
        },
        {
            "phase": "Phase 3: 応答生成最適化（2-3週間）",
            "tasks": [
                "プロンプトエンジニアリングの改善",
                "パーソナライゼーション機能",
                "応答の多様性向上",
                "一貫性チェック機能"
            ]
        },
        {
            "phase": "Phase 4: 学習・評価システム（3-4週間）",
            "tasks": [
                "フィードバック収集システム",
                "応答品質評価指標",
                "自動学習パイプライン",
                "ダッシュボードと監視"
            ]
        }
    ]

    for phase_info in phases:
        print(f"\n📅 {phase_info['phase']}")
        print("-" * 50)
        for task in phase_info['tasks']:
            print(f"   🔧 {task}")

if __name__ == "__main__":
    print("🚀 データベース分析による学習方法提案システム")
    print(f"📅 分析実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        analyze_conversation_database()
        analyze_chromadb_performance()
        propose_learning_improvements()
        generate_implementation_roadmap()

        print(f"\n🎉 分析完了！")
        print("💡 提案された学習方法を参考に、段階的に実装することをお勧めします。")

    except Exception as e:
        print(f"❌ 分析中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
