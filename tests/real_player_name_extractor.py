"""
データベース全体から実際の人名データを探索するシステム
"""

import sqlite3
import re
import json
from datetime import datetime
from typing import List, Dict, Set
import os

class RealPlayerNameExtractor:
    """実際の選手名抽出システム"""

    def __init__(self, db_path: str):
        self.db_path = db_path

        # 明確な人名パターン（より厳密）
        self.name_patterns = [
            r'([一-龯]{2,4})\s*選手',        # 漢字 + 選手
            r'([一-龯]{2,4})\s*君',          # 漢字 + 君
            r'([一-龯]{2,4})\s*さん',        # 漢字 + さん
            r'([一-龯]{2,4})\s*ちゃん',      # 漢字 + ちゃん
            r'([一-龯]{2,4})\s*監督',        # 漢字 + 監督
            r'([一-龯]{2,4})\s*コーチ',      # 漢字 + コーチ
        ]

        # 明確に除外すべき一般語彙
        self.excluded_words = {
            '小学生', '中学生', '高校生', '大学生', '社会人',
            '選手', 'チーム', '試合', '練習', '大会', '監督', 'コーチ',
            '投手', '捕手', '内野手', '外野手', 'ピッチャー', 'キャッチャー',
            '今日', '明日', '昨日', '今年', '来年', '去年',
            '結果', '勝敗', '試合', '成績', '記録', '成果',
            '実力', '能力', '技術', '経験', '才能', '素質',
            '馬三', 'ソフト', '情報', '具体', '一般', '詳細',
            '現在', '以前', '今後', '将来', '過去', '最近'
        }

        # 既知の実在選手名（例）
        self.known_real_players = {
            '田中', '佐藤', '鈴木', '高橋', '渡辺', '伊藤', '山田', '中村',
            '小林', '加藤', '吉田', '山本', '松本', '井上', '木村', '林',
            '清水', '山崎', '森', '池田', '橋本', '阿部', '石川', '前田'
        }

    def explore_database_schema(self):
        """データベーススキーマの探索"""
        print("🔍 データベーススキーマ探索")
        print("=" * 40)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # テーブル一覧取得
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            print(f"📊 テーブル一覧:")
            for table in tables:
                table_name = table[0]
                print(f"   📋 {table_name}")

                # テーブル構造取得
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()

                for col in columns:
                    print(f"      🔹 {col[1]} ({col[2]})")

                # レコード数確認
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"      📈 レコード数: {count}")
                print()

            return tables

        except Exception as e:
            print(f"❌ スキーマ探索エラー: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    def search_for_player_names_in_all_columns(self):
        """全カラムから選手名候補を検索"""
        print("🔍 全カラム選手名検索")
        print("=" * 30)

        potential_players = set()
        search_results = {}

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # conversation_historyテーブルの全カラムを検索
            columns_to_search = ['content', 'metadata']

            for column in columns_to_search:
                print(f"🔍 検索カラム: {column}")

                cursor.execute(f"SELECT DISTINCT {column} FROM conversation_history WHERE {column} IS NOT NULL AND {column} != ''")
                rows = cursor.fetchall()

                column_players = set()

                for row in rows:
                    text = row[0] if row[0] else ''

                    # 各パターンで検索
                    for pattern in self.name_patterns:
                        matches = re.findall(pattern, text)
                        for match in matches:
                            if self.is_likely_player_name(match):
                                column_players.add(match)
                                potential_players.add(match)

                search_results[column] = column_players
                print(f"   📊 {column}から抽出: {len(column_players)} 個")

                if column_players:
                    print(f"   🔍 候補例: {', '.join(list(column_players)[:5])}")
                print()

            return potential_players, search_results

        except Exception as e:
            print(f"❌ 選手名検索エラー: {e}")
            return set(), {}
        finally:
            if 'conn' in locals():
                conn.close()

    def is_likely_player_name(self, name: str) -> bool:
        """選手名らしさの判定"""
        # 除外語彙チェック
        if name in self.excluded_words:
            return False

        # 長さチェック（2-4文字の漢字）
        if len(name) < 2 or len(name) > 4:
            return False

        # 漢字のみかチェック
        if not all('\u4e00' <= c <= '\u9fff' for c in name):
            return False

        # 一般的な語尾を含むかチェック
        invalid_endings = ['的', '性', '者', '物', '事', '中', '内', '外', '上', '下', '前', '後', '間']
        if any(name.endswith(ending) for ending in invalid_endings):
            return False

        # 既知の実在選手姓をチェック
        if any(name.startswith(surname) for surname in self.known_real_players):
            return True

        # その他の人名らしさチェック（人名によく使われる漢字）
        common_name_chars = set('田中佐藤鈴木高橋渡辺伊藤山田中村小林加藤吉田山本松本井上木村林清水山崎森池田橋本阿部石川前田')
        if any(char in common_name_chars for char in name):
            return True

        return False

    def analyze_metadata_for_names(self):
        """メタデータから名前情報を分析"""
        print("🔍 メタデータ分析")
        print("=" * 20)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT metadata FROM conversation_history WHERE metadata IS NOT NULL AND metadata != ''")
            metadata_rows = cursor.fetchall()

            print(f"📊 メタデータレコード数: {len(metadata_rows)}")

            # メタデータの構造分析
            sample_metadata = []
            for row in metadata_rows[:10]:  # 最初の10件をサンプル
                try:
                    metadata = json.loads(row[0])
                    sample_metadata.append(metadata)
                except json.JSONDecodeError:
                    continue

            print(f"📝 メタデータサンプル:")
            for i, metadata in enumerate(sample_metadata[:3], 1):
                print(f"   {i}. {json.dumps(metadata, ensure_ascii=False, indent=2)[:200]}...")
                print()

            # メタデータ内のキーを調査
            all_keys = set()
            for metadata in sample_metadata:
                if isinstance(metadata, dict):
                    all_keys.update(metadata.keys())

            print(f"🗝️ メタデータキー一覧: {sorted(all_keys)}")

            return sample_metadata

        except Exception as e:
            print(f"❌ メタデータ分析エラー: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()

    def search_user_related_names(self):
        """ユーザー関連の名前を検索"""
        print("🔍 ユーザー関連名前検索")
        print("=" * 25)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # user_idの一覧取得
            cursor.execute("SELECT DISTINCT user_id FROM conversation_history WHERE user_id IS NOT NULL")
            user_ids = cursor.fetchall()

            print(f"👥 ユニークユーザー数: {len(user_ids)}")

            # 各ユーザーの会話パターン分析
            user_names = {}
            for user_id_tuple in user_ids[:10]:  # 最初の10ユーザー
                user_id = user_id_tuple[0]

                cursor.execute("""
                    SELECT content, metadata
                    FROM conversation_history
                    WHERE user_id = ? AND content IS NOT NULL
                    ORDER BY timestamp DESC
                    LIMIT 20
                """, (user_id,))

                user_conversations = cursor.fetchall()

                # このユーザーの会話から名前を抽出
                user_potential_names = set()
                for content, metadata in user_conversations:
                    if content:
                        for pattern in self.name_patterns:
                            matches = re.findall(pattern, content)
                            for match in matches:
                                if self.is_likely_player_name(match):
                                    user_potential_names.add(match)

                if user_potential_names:
                    user_names[user_id] = user_potential_names
                    print(f"   👤 ユーザー {user_id}: {user_potential_names}")

            return user_names

        except Exception as e:
            print(f"❌ ユーザー名検索エラー: {e}")
            return {}
        finally:
            if 'conn' in locals():
                conn.close()

    def create_comprehensive_report(self, all_players: Set[str], search_results: Dict):
        """包括的レポート作成"""
        print("📊 包括的レポート作成")
        print("=" * 25)

        report = {
            'timestamp': datetime.now().isoformat(),
            'total_potential_players': len(all_players),
            'players_by_column': {k: list(v) for k, v in search_results.items()},
            'all_players_list': sorted(list(all_players)),
            'confidence_analysis': {},
            'recommendations': []
        }

        # 信頼度分析
        for player in all_players:
            confidence_score = 0
            reasons = []

            # 既知の姓が含まれているか
            if any(player.startswith(surname) for surname in self.known_real_players):
                confidence_score += 50
                reasons.append('既知の姓を含む')

            # 文字数が適切か
            if 2 <= len(player) <= 3:
                confidence_score += 30
                reasons.append('適切な文字数')

            # 人名用漢字が含まれているか
            common_chars = set('田中佐藤鈴木高橋渡辺伊藤山田中村小林加藤吉田山本松本井上木村林清水山崎森池田橋本阿部石川前田')
            if any(char in common_chars for char in player):
                confidence_score += 20
                reasons.append('人名用漢字を含む')

            report['confidence_analysis'][player] = {
                'score': confidence_score,
                'reasons': reasons
            }

        # 推奨事項
        if not all_players:
            report['recommendations'].extend([
                'データベースに具体的な選手名が記録されていない可能性があります',
                'ユーザーとの会話で選手名を直接聞いてみることをお勧めします',
                '会話履歴の蓄積と共に学習精度が向上します'
            ])
        else:
            report['recommendations'].extend([
                f'{len(all_players)}個の選手名候補が見つかりました',
                '信頼度の高い候補から学習テンプレートを作成できます',
                'より多くの会話データが蓄積されることで精度が向上します'
            ])

        # レポート保存
        report_path = 'comprehensive_player_analysis.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"💾 包括的レポート保存: {report_path}")
        print(f"📊 最終結果: {len(all_players)} 個の選手名候補")

        if all_players:
            print(f"🏆 高信頼度候補:")
            high_confidence = [(name, data['score']) for name, data in report['confidence_analysis'].items() if data['score'] >= 50]
            high_confidence.sort(key=lambda x: x[1], reverse=True)

            for name, score in high_confidence[:10]:
                reasons = ', '.join(report['confidence_analysis'][name]['reasons'])
                print(f"   ✨ {name} (信頼度: {score}点) - {reasons}")

        return report

def main():
    """メイン処理"""
    print("🔍 実選手名探索システム")
    print(f"📅 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # データベースパス
    db_path = os.path.join('..', 'db', 'conversation_history.db')

    if not os.path.exists(db_path):
        print(f"❌ データベースが見つかりません: {db_path}")
        return

    # 実選手名抽出システム
    extractor = RealPlayerNameExtractor(db_path)

    # 1. データベーススキーマ探索
    tables = extractor.explore_database_schema()

    # 2. 全カラムから選手名検索
    all_players, search_results = extractor.search_for_player_names_in_all_columns()

    # 3. メタデータ分析
    metadata_analysis = extractor.analyze_metadata_for_names()

    # 4. ユーザー関連名前検索
    user_names = extractor.search_user_related_names()

    # 5. 包括的レポート作成
    report = extractor.create_comprehensive_report(all_players, search_results)

    print(f"\n🎉 実選手名探索完了！")
    print(f"📊 発見された選手名候補: {len(all_players)} 個")

    if all_players:
        print(f"📝 選手名一覧: {', '.join(sorted(all_players))}")

if __name__ == "__main__":
    main()
