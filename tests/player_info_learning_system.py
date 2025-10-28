"""
具体的な選手情報から学習するシステム
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Set
import os

class PlayerInfoLearningSystem:
    """選手情報学習システム"""

    def __init__(self, db_path: str):
        self.db_path = db_path

        # 提供された選手情報
        self.player_list = [
            "陸功", "湊", "錬", "南", "統司", "春輝", "新",
            "由眞", "心寧", "唯浬", "朋樹", "佑多", "穂美"
        ]

        self.total_players = 13

        print(f"🏆 学習対象選手情報:")
        print(f"   参加選手数: {self.total_players}名")
        print(f"   選手一覧: {', '.join(self.player_list)}")
        print()

    def analyze_player_names(self):
        """選手名の詳細分析"""
        print("🔍 選手名詳細分析")
        print("=" * 30)

        analysis = {
            'total_count': len(self.player_list),
            'name_lengths': {},
            'character_analysis': {},
            'name_patterns': {},
            'reading_suggestions': {}
        }

        # 文字数分析
        for player in self.player_list:
            length = len(player)
            if length not in analysis['name_lengths']:
                analysis['name_lengths'][length] = []
            analysis['name_lengths'][length].append(player)

        print("📊 文字数別分析:")
        for length, names in sorted(analysis['name_lengths'].items()):
            print(f"   {length}文字: {len(names)}名 - {', '.join(names)}")

        # 使用漢字分析
        all_chars = set()
        char_count = {}
        for player in self.player_list:
            for char in player:
                all_chars.add(char)
                char_count[char] = char_count.get(char, 0) + 1

        print(f"\n📝 使用漢字数: {len(all_chars)}文字")
        print("   頻出漢字:")
        sorted_chars = sorted(char_count.items(), key=lambda x: x[1], reverse=True)
        for char, count in sorted_chars[:10]:
            if count > 1:
                print(f"      '{char}': {count}回")

        analysis['character_analysis'] = char_count

        return analysis

    def create_player_database(self):
        """選手データベース作成"""
        print("\n💾 選手データベース作成")
        print("=" * 25)

        player_database = {
            'team_info': {
                'total_players': self.total_players,
                'team_name': '馬三ソフト',
                'last_updated': datetime.now().isoformat()
            },
            'players': []
        }

        # 各選手の詳細情報作成
        for i, player in enumerate(self.player_list, 1):
            player_info = {
                'id': i,
                'name': player,
                'name_length': len(player),
                'position_number': i,
                'characters': list(player),
                'possible_readings': self.generate_reading_suggestions(player),
                'search_patterns': self.generate_search_patterns(player)
            }
            player_database['players'].append(player_info)

        # データベース保存
        db_path = 'learned_player_database.json'
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(player_database, f, ensure_ascii=False, indent=2)

        print(f"✅ 選手データベース保存: {db_path}")
        print(f"📊 登録選手数: {len(player_database['players'])}名")

        return player_database

    def generate_reading_suggestions(self, name: str) -> List[str]:
        """選手名の読み方候補生成"""
        # 簡単な読み方パターン（実際の読み方は推測）
        reading_patterns = []

        # 一般的な漢字の読み方マッピング（例）
        reading_map = {
            '陸': ['りく', 'ろく'],
            '功': ['こう', 'いさお'],
            '湊': ['みなと', 'そう'],
            '錬': ['れん'],
            '南': ['みなみ', 'なん'],
            '統': ['とう'],
            '司': ['し', 'つかさ'],
            '春': ['はる', 'しゅん'],
            '輝': ['き', 'てる'],
            '新': ['しん', 'あらた'],
            '由': ['ゆ', 'よし'],
            '眞': ['ま', 'しん'],
            '心': ['こころ', 'しん'],
            '寧': ['ねい', 'やす'],
            '唯': ['ゆい', 'ただ'],
            '浬': ['り'],
            '朋': ['とも', 'ほう'],
            '樹': ['き', 'じゅ'],
            '佑': ['ゆう', 'すけ'],
            '多': ['た', 'おお'],
            '穂': ['ほ'],
            '美': ['み', 'よし']
        }

        # 各文字の読み方を組み合わせ
        char_readings = []
        for char in name:
            if char in reading_map:
                char_readings.append(reading_map[char])
            else:
                char_readings.append([char])  # 読み方が不明な場合は文字をそのまま

        # 組み合わせ生成（最初の候補のみ）
        if char_readings:
            reading_patterns.append(''.join(readings[0] for readings in char_readings))

        return reading_patterns

    def generate_search_patterns(self, name: str) -> List[str]:
        """検索パターン生成"""
        patterns = []

        # 基本パターン
        patterns.extend([
            name,
            f"{name}選手",
            f"{name}君",
            f"{name}さん",
            f"{name}について",
            f"{name}の",
            f"{name}は",
            f"{name}が"
        ])

        return patterns

    def create_response_templates(self, player_database: Dict):
        """選手用応答テンプレート作成"""
        print("\n📝 応答テンプレート作成")
        print("=" * 25)

        templates = {}

        # チーム全体のテンプレート
        templates['team_overview'] = f"馬三ソフトには{self.total_players}名の選手が参加しています。選手一覧: {', '.join(self.player_list)}。どの選手について詳しく知りたいですか？"

        templates['player_count'] = f"馬三ソフトの参加選手は{self.total_players}名です。"

        templates['player_list'] = f"参加選手一覧: {', '.join(self.player_list)}"

        # 各選手用のテンプレート
        for player_info in player_database['players']:
            name = player_info['name']
            position = player_info['position_number']
            readings = player_info['possible_readings']

            # 基本テンプレート
            templates[f'{name}_basic'] = f"{name}選手についてお答えします。{name}選手は馬三ソフトの{position}番目に登録された選手です。"

            # 詳細テンプレート
            templates[f'{name}_detail'] = f"{name}選手（{position}番）は馬三ソフトの大切なメンバーです。"

            if readings:
                templates[f'{name}_reading'] = f"{name}選手の読み方は「{readings[0]}」と思われます。"

            # 質問テンプレート
            templates[f'{name}_question'] = f"{name}選手について何をお知りになりたいですか？"

        # 検索関連テンプレート
        templates['player_search'] = "どの選手について知りたいですか？以下の選手が参加しています: " + ', '.join(self.player_list)

        templates['unknown_player'] = f"申し訳ございませんが、その選手は馬三ソフトの参加選手リストにはいません。参加選手は: {', '.join(self.player_list)} です。"

        # テンプレート保存
        template_path = 'player_response_templates.json'
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)

        print(f"✅ 応答テンプレート保存: {template_path}")
        print(f"📊 作成テンプレート数: {len(templates)}")

        return templates

    def save_to_conversation_history(self):
        """学習データを会話履歴DBに保存"""
        print("\n💾 会話履歴データベースに学習データ保存")
        print("=" * 40)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 学習データとして会話履歴に保存
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            learning_entries = [
                {
                    'user_id': 'system_learning',
                    'session_id': f'player_learning_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                    'message_type': 'system',
                    'content': f'馬三ソフト参加選手{self.total_players}名: {", ".join(self.player_list)}',
                    'metadata': json.dumps({
                        'learning_type': 'player_info',
                        'total_players': self.total_players,
                        'players': self.player_list,
                        'source': 'manual_input'
                    }, ensure_ascii=False),
                    'timestamp': timestamp
                }
            ]

            # 各選手の個別エントリー
            for i, player in enumerate(self.player_list, 1):
                learning_entries.append({
                    'user_id': 'system_learning',
                    'session_id': f'player_learning_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                    'message_type': 'system',
                    'content': f'{player}選手は馬三ソフトの参加選手です。',
                    'metadata': json.dumps({
                        'learning_type': 'individual_player',
                        'player_name': player,
                        'player_number': i,
                        'team': '馬三ソフト'
                    }, ensure_ascii=False),
                    'timestamp': timestamp
                })

            # データベースに挿入
            for entry in learning_entries:
                cursor.execute("""
                    INSERT INTO conversation_history
                    (user_id, session_id, message_type, content, metadata, timestamp, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry['user_id'],
                    entry['session_id'],
                    entry['message_type'],
                    entry['content'],
                    entry['metadata'],
                    entry['timestamp'],
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))

            conn.commit()
            print(f"✅ 学習データ保存完了: {len(learning_entries)}件")

        except Exception as e:
            print(f"❌ データベース保存エラー: {e}")
        finally:
            if 'conn' in locals():
                conn.close()

    def create_player_search_system(self, templates: Dict):
        """選手検索システム作成"""
        print("\n🔍 選手検索システム作成")
        print("=" * 25)

        search_system = {
            'player_mapping': {},
            'search_patterns': {},
            'response_templates': templates,
            'fuzzy_search': {}
        }

        # 選手名マッピング
        for player in self.player_list:
            search_system['player_mapping'][player] = {
                'full_name': player,
                'search_keys': [
                    player,
                    f'{player}選手',
                    f'{player}君',
                    f'{player}さん'
                ]
            }

        # ファジー検索用（一文字違いなど）
        for player in self.player_list:
            for other_player in self.player_list:
                if player != other_player:
                    # 一文字共通している場合
                    common_chars = set(player) & set(other_player)
                    if common_chars:
                        if player not in search_system['fuzzy_search']:
                            search_system['fuzzy_search'][player] = []
                        search_system['fuzzy_search'][player].append({
                            'similar_to': other_player,
                            'common_chars': list(common_chars)
                        })

        # 検索システム保存
        search_path = 'player_search_system.json'
        with open(search_path, 'w', encoding='utf-8') as f:
            json.dump(search_system, f, ensure_ascii=False, indent=2)

        print(f"✅ 検索システム保存: {search_path}")

        return search_system

    def generate_learning_summary(self):
        """学習サマリー生成"""
        print("\n📊 学習サマリー")
        print("=" * 20)

        summary = {
            'learning_date': datetime.now().isoformat(),
            'total_players_learned': len(self.player_list),
            'team_name': '馬三ソフト',
            'players_by_length': {},
            'unique_characters': len(set(''.join(self.player_list))),
            'learning_files_created': [
                'learned_player_database.json',
                'player_response_templates.json',
                'player_search_system.json'
            ]
        }

        # 文字数別集計
        for player in self.player_list:
            length = len(player)
            if length not in summary['players_by_length']:
                summary['players_by_length'][length] = 0
            summary['players_by_length'][length] += 1

        print(f"📅 学習実行日時: {summary['learning_date']}")
        print(f"👥 学習選手数: {summary['total_players_learned']}名")
        print(f"🏆 チーム名: {summary['team_name']}")
        print(f"📝 使用文字数: {summary['unique_characters']}文字")
        print(f"📁 作成ファイル数: {len(summary['learning_files_created'])}個")

        # サマリー保存
        summary_path = 'player_learning_summary.json'
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"💾 学習サマリー保存: {summary_path}")

        return summary

def main():
    """メイン処理"""
    print("🏆 選手情報学習システム")
    print(f"📅 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # データベースパス
    db_path = os.path.join('..', 'db', 'conversation_history.db')

    # 学習システム初期化
    learning_system = PlayerInfoLearningSystem(db_path)

    # 1. 選手名分析
    analysis = learning_system.analyze_player_names()

    # 2. 選手データベース作成
    player_database = learning_system.create_player_database()

    # 3. 応答テンプレート作成
    templates = learning_system.create_response_templates(player_database)

    # 4. 会話履歴に学習データ保存
    if os.path.exists(db_path):
        learning_system.save_to_conversation_history()
    else:
        print(f"⚠️ データベースが見つかりません: {db_path}")

    # 5. 検索システム作成
    search_system = learning_system.create_player_search_system(templates)

    # 6. 学習サマリー生成
    summary = learning_system.generate_learning_summary()

    print(f"\n🎉 選手情報学習完了！")
    print(f"✅ 学習済み選手: {', '.join(learning_system.player_list)}")
    print(f"📊 総学習データ: {len(learning_system.player_list)}名")

if __name__ == "__main__":
    main()
