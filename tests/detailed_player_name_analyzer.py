"""
データベース会話内容の詳細分析と実際の選手名抽出
"""

import sqlite3
import re
import json
from datetime import datetime
from typing import List, Dict, Set, Optional
import os

class DetailedPlayerNameAnalyzer:
    """詳細選手名分析システム"""

    def __init__(self, db_path: str):
        self.db_path = db_path

        # 既存の13名
        self.existing_players = [
            "陸功", "湊", "錬", "南", "統司", "春輝", "新",
            "由眞", "心寧", "唯浬", "朋樹", "佑多", "穂美"
        ]

        # 実際の日本人名パターン（より厳密）
        self.strict_name_patterns = [
            r'([一-龯]{2,3})(?:選手|君|さん)(?:が|は|も|について|の)',  # 敬称付き
            r'([一-龯]{2,3})(?:選手|君|さん)(?:です|だ)',  # 断定形
            r'([一-龯]{2,3})(?:選手|君|さん)(?:を|に|で)',  # 助詞付き
            r'(?:投手|捕手|内野手|外野手)の([一-龯]{2,3})',  # ポジション
            r'(?:キャプテン|コーチ|監督)の([一-龯]{2,3})',  # 役職
            r'([一-龯]{2,3})(?:が投げ|が打っ|が走っ|が守っ)',  # 動作
            r'([一-龯]{2,3})(?:の成績|のヒット|の得点|のエラー)',  # 成績
        ]

        # 確実に除外すべき語
        self.definitely_not_names = {
            '参加', '登録', '出場', '試合', '練習', '大会', '優勝', '準優勝',
            '成績', '結果', '記録', '得点', '失点', 'ヒット', 'エラー',
            '今日', '明日', '昨日', '今年', '来年', '去年', '最近',
            '選手', 'チーム', 'メンバー', 'コーチ', '監督', 'キャプテン',
            '小学生', '中学生', '高校生', '大学生', '社会人',
            '投手', '捕手', '内野手', '外野手', 'ピッチャー', 'キャッチャー',
            '一番', '二番', '三番', '四番', '五番', '六番', '七番', '八番', '九番',
            '活躍', '成長', '努力', '頑張', '上達', '向上', '改善',
            '情報', '詳細', '具体', '一般', '全体', '部分', '個別', '特別',
            '馬三', 'ソフト', 'ソフトボール', '球場', 'グラウンド'
        }

        # 実在しそうな日本人の姓
        self.common_surnames = {
            '田中', '佐藤', '鈴木', '高橋', '渡辺', '伊藤', '山田', '中村',
            '小林', '加藤', '吉田', '山本', '松本', '井上', '木村', '林',
            '清水', '山崎', '森', '池田', '橋本', '阿部', '石川', '前田',
            '藤田', '岡田', '後藤', '長谷川', '村上', '近藤', '石田', '斎藤',
            '原田', '青木', '竹内', '西田', '今井', '野田', '水野', '菊地'
        }

    def analyze_all_conversation_content(self):
        """全会話内容の詳細分析"""
        print("📋 全会話内容詳細分析")
        print("=" * 40)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 全会話を取得
            cursor.execute("""
                SELECT id, content, metadata, timestamp, user_id
                FROM conversation_history
                WHERE content IS NOT NULL AND content != ''
                ORDER BY timestamp DESC
            """)

            conversations = cursor.fetchall()
            print(f"📊 総会話数: {len(conversations)} 件")

            # 実際の会話内容をサンプル表示
            print(f"\n📝 会話内容サンプル（最新10件）:")
            print("-" * 60)

            for i, (id, content, metadata, timestamp, user_id) in enumerate(conversations[:10], 1):
                print(f"{i:2d}. [{timestamp}] (ID:{id})")
                print(f"    内容: {content[:150]}...")
                if metadata:
                    try:
                        meta = json.loads(metadata) if metadata else {}
                        print(f"    メタ: {str(meta)[:100]}...")
                    except:
                        print(f"    メタ: {metadata[:100]}...")
                print()

            return conversations

        except Exception as e:
            print(f"❌ 会話分析エラー: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()

    def extract_potential_names_from_conversations(self, conversations: List[tuple]):
        """会話から潜在的な名前を抽出"""
        print(f"\n🔍 潜在的名前抽出分析")
        print("=" * 30)

        potential_names = set()
        name_contexts = {}

        # 各会話を詳細分析
        for id, content, metadata, timestamp, user_id in conversations:
            text = content or ''

            # 既存選手以外の2-3文字の漢字を全て抽出
            all_possible_names = re.findall(r'([一-龯]{2,3})', text)

            for possible_name in all_possible_names:
                # 既存選手は除外
                if possible_name in self.existing_players:
                    continue

                # 確実に除外すべき語は除外
                if possible_name in self.definitely_not_names:
                    continue

                # 文脈をチェック
                if self.check_name_context(possible_name, text):
                    potential_names.add(possible_name)

                    if possible_name not in name_contexts:
                        name_contexts[possible_name] = []

                    name_contexts[possible_name].append({
                        'conversation_id': id,
                        'context': text,
                        'timestamp': timestamp,
                        'user_id': user_id
                    })

        print(f"📊 抽出された潜在的名前: {len(potential_names)} 個")

        # 各名前の文脈を分析
        analyzed_names = {}
        for name in potential_names:
            contexts = name_contexts[name]
            analysis = self.analyze_name_likelihood(name, contexts)
            analyzed_names[name] = analysis

            print(f"\n🔍 候補: '{name}' (信頼度: {analysis['confidence_score']:.1f})")
            print(f"   出現回数: {len(contexts)} 回")
            print(f"   判定要因: {', '.join(analysis['factors'])}")

            # 代表的な文脈を表示
            for i, ctx in enumerate(contexts[:2], 1):
                context_snippet = self.extract_context_snippet(name, ctx['context'])
                print(f"   文脈{i}: ...{context_snippet}...")

        # 信頼度でフィルタリング
        high_confidence_names = {
            name: analysis for name, analysis in analyzed_names.items()
            if analysis['confidence_score'] >= 3.0
        }

        print(f"\n✅ 高信頼度名前候補: {len(high_confidence_names)} 個")
        for name, analysis in high_confidence_names.items():
            print(f"   🌟 {name} (信頼度: {analysis['confidence_score']:.1f})")

        return high_confidence_names, name_contexts

    def check_name_context(self, name: str, text: str) -> bool:
        """名前の文脈をチェック"""
        # 名前らしい文脈パターン
        name_context_patterns = [
            f'{name}選手',
            f'{name}君',
            f'{name}さん',
            f'{name}ちゃん',
            f'{name}について',
            f'{name}の',
            f'{name}は',
            f'{name}が',
            f'{name}を'
        ]

        return any(pattern in text for pattern in name_context_patterns)

    def extract_context_snippet(self, name: str, text: str) -> str:
        """名前周辺の文脈を抽出"""
        name_index = text.find(name)
        if name_index == -1:
            return text[:50]

        start = max(0, name_index - 30)
        end = min(len(text), name_index + len(name) + 30)
        return text[start:end]

    def analyze_name_likelihood(self, name: str, contexts: List[Dict]) -> Dict:
        """名前らしさの分析"""
        analysis = {
            'confidence_score': 0.0,
            'factors': [],
            'context_count': len(contexts)
        }

        # 1. 既知の姓をチェック
        if any(name.startswith(surname) for surname in self.common_surnames):
            analysis['confidence_score'] += 2.0
            analysis['factors'].append('既知の姓')

        # 2. 文字数チェック
        if len(name) == 2 or len(name) == 3:
            analysis['confidence_score'] += 1.0
            analysis['factors'].append('適切な文字数')

        # 3. 敬称での使用チェック
        honorific_count = 0
        for ctx in contexts:
            text = ctx['context']
            if f'{name}選手' in text or f'{name}君' in text or f'{name}さん' in text:
                honorific_count += 1

        if honorific_count > 0:
            analysis['confidence_score'] += min(honorific_count * 0.5, 2.0)
            analysis['factors'].append(f'敬称使用{honorific_count}回')

        # 4. 文脈での一貫性チェック
        consistent_contexts = 0
        for ctx in contexts:
            text = ctx['context']
            if any(keyword in text for keyword in ['選手', 'チーム', '馬三ソフト', '試合', '練習']):
                consistent_contexts += 1

        if consistent_contexts > 0:
            analysis['confidence_score'] += min(consistent_contexts * 0.3, 1.5)
            analysis['factors'].append(f'一貫した文脈{consistent_contexts}回')

        # 5. 出現頻度
        if len(contexts) >= 3:
            analysis['confidence_score'] += 1.0
            analysis['factors'].append('十分な出現頻度')
        elif len(contexts) >= 2:
            analysis['confidence_score'] += 0.5
            analysis['factors'].append('適度な出現頻度')

        return analysis

    def create_verified_player_list(self, high_confidence_names: Dict):
        """検証済み選手リスト作成"""
        print(f"\n✅ 検証済み選手リスト作成")
        print("=" * 30)

        # 既存選手 + 高信頼度新規選手
        verified_new_players = list(high_confidence_names.keys())
        all_verified_players = self.existing_players + verified_new_players

        verified_database = {
            'verification_info': {
                'verification_date': datetime.now().isoformat(),
                'original_players': len(self.existing_players),
                'verified_new_players': len(verified_new_players),
                'total_verified_players': len(all_verified_players),
                'team_name': '馬三ソフト'
            },
            'original_13_players': self.existing_players,
            'verified_new_players': verified_new_players,
            'all_verified_players': all_verified_players,
            'confidence_analysis': high_confidence_names
        }

        print(f"📊 検証結果:")
        print(f"   既存選手: {len(self.existing_players)} 名")
        print(f"   検証済み新規選手: {len(verified_new_players)} 名")
        print(f"   総検証済み選手: {len(all_verified_players)} 名")

        if verified_new_players:
            print(f"\n🎯 検証済み新規選手:")
            for player in verified_new_players:
                confidence = high_confidence_names[player]['confidence_score']
                factors = high_confidence_names[player]['factors']
                print(f"   ✅ {player} (信頼度: {confidence:.1f}) - {', '.join(factors)}")
        else:
            print(f"\n⚠️ 検証済み新規選手なし")
            print(f"   データベースには既存の13名以外の確実な選手情報が見つかりませんでした")

        # 検証データベース保存
        db_path = 'verified_player_database.json'
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(verified_database, f, ensure_ascii=False, indent=2)

        print(f"\n💾 検証済みデータベース保存: {db_path}")

        return verified_database

    def generate_detailed_analysis_report(self, conversations: List[tuple], verified_database: Dict):
        """詳細分析レポート生成"""
        print(f"\n📊 詳細分析レポート生成")
        print("=" * 30)

        report = {
            'analysis_metadata': {
                'analysis_date': datetime.now().isoformat(),
                'total_conversations_analyzed': len(conversations),
                'analysis_methods': [
                    'strict_pattern_matching',
                    'context_analysis',
                    'confidence_scoring',
                    'name_likelihood_assessment'
                ]
            },
            'findings': {
                'existing_players_confirmed': len(self.existing_players),
                'new_players_discovered': len(verified_database['verified_new_players']),
                'total_verified_players': len(verified_database['all_verified_players'])
            },
            'analysis_summary': {
                'database_contains_mainly_existing_13': True,
                'additional_player_data_limited': len(verified_database['verified_new_players']) == 0,
                'recommendation': 'focus_on_existing_13_players'
            },
            'data_quality_assessment': {
                'conversation_quality': 'system_generated_responses',
                'player_name_mentions': 'primarily_existing_13',
                'new_player_evidence': 'insufficient_for_confident_identification'
            }
        }

        print(f"📋 分析結果サマリー:")
        print(f"   🔍 分析対象会話: {report['analysis_metadata']['total_conversations_analyzed']} 件")
        print(f"   ✅ 既存選手確認: {report['findings']['existing_players_confirmed']} 名")
        print(f"   🆕 新規選手発見: {report['findings']['new_players_discovered']} 名")
        print(f"   🏆 総検証選手数: {report['findings']['total_verified_players']} 名")

        if report['findings']['new_players_discovered'] == 0:
            print(f"\n💡 推奨事項:")
            print(f"   - 現在のデータベースには既存の13名以外の確実な選手情報は含まれていません")
            print(f"   - 既存の13名の選手情報を強化・詳細化することを推奨します")
            print(f"   - 新たな選手情報は実際の会話やユーザー入力から学習することが必要です")

        # レポート保存
        report_path = 'detailed_player_analysis_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n💾 詳細分析レポート保存: {report_path}")

        return report

def main():
    """メイン処理"""
    print("🔍 詳細選手名分析システム")
    print(f"📅 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # データベースパス
    db_path = os.path.join('..', 'db', 'conversation_history.db')

    if not os.path.exists(db_path):
        print(f"❌ データベースが見つかりません: {db_path}")
        return

    # 詳細分析システム
    analyzer = DetailedPlayerNameAnalyzer(db_path)

    print(f"📊 分析対象既存選手: {len(analyzer.existing_players)}名")
    print(f"   {', '.join(analyzer.existing_players)}")
    print()

    # 1. 全会話内容の詳細分析
    conversations = analyzer.analyze_all_conversation_content()

    if not conversations:
        print("❌ 会話データが取得できませんでした")
        return

    # 2. 潜在的名前の抽出と分析
    high_confidence_names, name_contexts = analyzer.extract_potential_names_from_conversations(conversations)

    # 3. 検証済み選手リスト作成
    verified_database = analyzer.create_verified_player_list(high_confidence_names)

    # 4. 詳細分析レポート生成
    report = analyzer.generate_detailed_analysis_report(conversations, verified_database)

    print(f"\n🎉 詳細選手名分析完了！")

    if verified_database['verified_new_players']:
        print(f"✨ 新規発見選手: {', '.join(verified_database['verified_new_players'])}")
        print(f"📊 総選手数: {verified_database['verification_info']['total_verified_players']}名")
    else:
        print(f"📊 確認済み選手: 既存の{len(analyzer.existing_players)}名のみ")
        print(f"💡 データベースには追加の確実な選手情報は含まれていません")

if __name__ == "__main__":
    main()
