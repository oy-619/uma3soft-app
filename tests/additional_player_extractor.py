"""
データベースから追加選手情報を抽出・学習するシステム
"""

import sqlite3
import re
import json
from datetime import datetime
from typing import List, Dict, Set, Optional
import os

class AdditionalPlayerExtractor:
    """追加選手抽出システム"""

    def __init__(self, db_path: str):
        self.db_path = db_path

        # 既存の13名
        self.existing_players = [
            "陸功", "湊", "錬", "南", "統司", "春輝", "新",
            "由眞", "心寧", "唯浬", "朋樹", "佑多", "穂美"
        ]

        # 新たに発見された選手
        self.new_players = set()

        # より厳密な人名パターン
        self.name_patterns = [
            r'([一-龯]{2,4})(?:選手|君|さん|ちゃん)',  # 漢字 + 敬称
            r'([一-龯]{2,4})(?:が|は|も|の|を|に|で|と)\s*(?:参加|出場|登録|メンバー)',  # 参加関連
            r'([一-龯]{2,4})(?:が|は|も|の|を|に|で|と)\s*(?:投げ|打っ|走っ|守っ)',  # 動作関連
            r'([一-龯]{2,4})(?:が|は|も|の|を|に|で|と)\s*(?:得点|ヒット|エラー)',  # 成績関連
            r'([一-龯]{2,4})(?:番|位|年|組)',  # 番号・学年関連
            r'(?:コーチ|監督|キャプテン)の([一-龯]{2,4})',  # 役職関連
        ]

        # 除外する一般語彙（拡張版）
        self.excluded_words = {
            # 基本除外語
            '小学生', '中学生', '高校生', '大学生', '社会人', '子供', '大人',
            '選手', 'チーム', '試合', '練習', '大会', '監督', 'コーチ', 'キャプテン',
            '投手', '捕手', '内野手', '外野手', 'ピッチャー', 'キャッチャー',

            # 時間・期間関連
            '今日', '明日', '昨日', '今年', '来年', '去年', '最近', '今度', '今回', '前回',
            '今月', '先月', '来月', '今週', '先週', '来週', '当日', '翌日', '前日',

            # 成績・結果関連
            '結果', '勝敗', '成績', '記録', '成果', '得点', '失点', 'ヒット', 'エラー',
            '勝利', '敗北', '引分', '優勝', '準優勝', '入賞', '表彰', '受賞',

            # 場所・施設関連
            '球場', 'グラウンド', '体育館', '運動場', '野球場', 'ソフトボール場',
            '学校', '小学校', '中学校', '高校', '大学', '会社', '職場',

            # 一般名詞
            '情報', '詳細', '具体', '一般', '全体', '部分', '個別', '特別',
            '内容', '話題', '問題', '課題', '目標', '予定', '計画', 'スケジュール',

            # 馬三ソフト関連の一般語
            '馬三', 'ソフト', 'ソフトボール', 'ソフトウェア', 'ソフトクリーム',

            # よくある誤抽出語
            '活躍', '成長', '努力', '頑張', '上達', '向上', '改善', '発達',
            '経験', '体験', '練習', '訓練', '指導', '教育', '学習', '勉強'
        }

        # 人名によく使われる漢字
        self.common_name_chars = {
            # 姓によく使われる漢字
            '田', '中', '佐', '藤', '鈴', '木', '高', '橋', '渡', '辺', '伊', '山', '村',
            '小', '林', '加', '吉', '松', '本', '井', '上', '森', '池', '石', '川',
            '前', '後', '西', '東', '南', '北', '大', '小', '新', '古', '長', '短',

            # 名によく使われる漢字
            '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
            '太', '郎', '次', '雄', '男', '夫', '子', '美', '恵', '香', '花',
            '愛', '優', '希', '光', '輝', '明', '清', '正', '良', '和', '平',
            '真', '誠', '純', '健', '強', '勇', '智', '賢', '聡', '優', '秀'
        }

    def search_database_for_additional_players(self):
        """データベースから追加選手を検索"""
        print("🔍 データベース追加選手検索")
        print("=" * 40)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 全会話データを取得
            cursor.execute("""
                SELECT content, metadata, timestamp, user_id
                FROM conversation_history
                WHERE content IS NOT NULL AND content != ''
                ORDER BY timestamp DESC
                LIMIT 1000
            """)

            conversations = cursor.fetchall()
            print(f"📊 分析対象会話数: {len(conversations)} 件")

            # 各パターンで名前候補を抽出
            all_candidates = set()
            pattern_results = {}

            for pattern in self.name_patterns:
                pattern_candidates = set()

                for content, metadata, timestamp, user_id in conversations:
                    text = content or ''
                    matches = re.findall(pattern, text)

                    for match in matches:
                        if self.is_valid_player_name(match):
                            pattern_candidates.add(match)
                            all_candidates.add(match)

                pattern_results[pattern] = pattern_candidates
                print(f"   パターン '{pattern[:30]}...': {len(pattern_candidates)} 個")
                if pattern_candidates:
                    print(f"      例: {', '.join(list(pattern_candidates)[:5])}")

            # 既存選手を除外して新規選手を特定
            for candidate in all_candidates:
                if candidate not in self.existing_players:
                    self.new_players.add(candidate)

            print(f"\n📊 抽出結果:")
            print(f"   全候補: {len(all_candidates)} 個")
            print(f"   既存選手: {len(self.existing_players)} 名")
            print(f"   新規選手: {len(self.new_players)} 名")

            if self.new_players:
                print(f"\n🆕 発見された新規選手:")
                for player in sorted(self.new_players):
                    print(f"      ✨ {player}")

            return all_candidates, pattern_results, conversations

        except Exception as e:
            print(f"❌ データベース検索エラー: {e}")
            return set(), {}, []
        finally:
            if 'conn' in locals():
                conn.close()

    def is_valid_player_name(self, name: str) -> bool:
        """有効な選手名かどうかの判定"""
        # 除外語彙チェック
        if name in self.excluded_words:
            return False

        # 長さチェック（2-4文字）
        if len(name) < 2 or len(name) > 4:
            return False

        # 漢字のみかチェック
        if not all('\u4e00' <= c <= '\u9fff' for c in name):
            return False

        # 一般的でない語尾をチェック
        invalid_endings = ['的', '性', '者', '物', '事', '中', '内', '外', '上', '下', '前', '後', '間', '時', '日', '月', '年']
        if any(name.endswith(ending) for ending in invalid_endings):
            return False

        # 人名らしい漢字が含まれているかチェック
        if any(char in self.common_name_chars for char in name):
            return True

        # その他の判定基準
        # 3文字以上で複雑な漢字の組み合わせの場合は人名の可能性が高い
        if len(name) >= 3:
            return True

        return False

    def analyze_new_players_context(self, conversations: List[tuple]):
        """新規選手の文脈分析"""
        print(f"\n🔍 新規選手文脈分析")
        print("=" * 25)

        player_contexts = {}

        for player in self.new_players:
            contexts = []

            for content, metadata, timestamp, user_id in conversations:
                text = content or ''

                if player in text:
                    # 該当部分の前後のテキストを取得
                    player_index = text.find(player)
                    start = max(0, player_index - 50)
                    end = min(len(text), player_index + len(player) + 50)
                    context = text[start:end]

                    contexts.append({
                        'context': context,
                        'timestamp': timestamp,
                        'user_id': user_id,
                        'full_text': text
                    })

            player_contexts[player] = contexts
            print(f"📝 {player}: {len(contexts)} 件の文脈")

            # 代表的な文脈を表示
            for i, ctx in enumerate(contexts[:3], 1):
                print(f"   {i}. ...{ctx['context']}...")

        return player_contexts

    def create_expanded_player_database(self, player_contexts: Dict):
        """拡張選手データベース作成"""
        print(f"\n💾 拡張選手データベース作成")
        print("=" * 30)

        # 既存の13名と新規選手を統合
        all_players = self.existing_players + sorted(list(self.new_players))

        expanded_database = {
            'team_info': {
                'total_players': len(all_players),
                'original_players': len(self.existing_players),
                'new_players_found': len(self.new_players),
                'team_name': '馬三ソフト',
                'last_updated': datetime.now().isoformat()
            },
            'all_players': all_players,
            'original_13_players': self.existing_players,
            'newly_discovered_players': sorted(list(self.new_players)),
            'player_details': []
        }

        # 各選手の詳細情報
        for i, player in enumerate(all_players, 1):
            player_info = {
                'id': i,
                'name': player,
                'status': 'original' if player in self.existing_players else 'newly_discovered',
                'name_length': len(player),
                'characters': list(player),
                'contexts_found': len(player_contexts.get(player, [])),
                'search_patterns': self.generate_search_patterns(player)
            }

            # 新規選手の場合は発見された文脈情報も含める
            if player in self.new_players and player in player_contexts:
                player_info['discovery_contexts'] = [
                    ctx['context'] for ctx in player_contexts[player][:5]  # 最初の5件
                ]

            expanded_database['player_details'].append(player_info)

        # データベース保存
        db_path = 'expanded_player_database.json'
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(expanded_database, f, ensure_ascii=False, indent=2)

        print(f"✅ 拡張データベース保存: {db_path}")
        print(f"📊 統合選手数: {len(all_players)}名")
        print(f"   - 既存: {len(self.existing_players)}名")
        print(f"   - 新規: {len(self.new_players)}名")

        return expanded_database

    def generate_search_patterns(self, player_name: str) -> List[str]:
        """検索パターン生成"""
        patterns = []

        # 基本パターン
        patterns.extend([
            player_name,
            f"{player_name}選手",
            f"{player_name}君",
            f"{player_name}さん",
            f"{player_name}ちゃん",
            f"{player_name}について",
            f"{player_name}の",
            f"{player_name}は",
            f"{player_name}が",
            f"{player_name}を",
            f"{player_name}に"
        ])

        return patterns

    def create_expanded_response_templates(self, expanded_database: Dict):
        """拡張応答テンプレート作成"""
        print(f"\n📝 拡張応答テンプレート作成")
        print("=" * 30)

        templates = {}
        all_players = expanded_database['all_players']
        total_players = len(all_players)
        new_players = expanded_database['newly_discovered_players']

        # チーム全体のテンプレート（更新）
        templates['team_overview'] = f"馬三ソフトには{total_players}名の選手が参加しています。選手一覧: {', '.join(all_players)}。どの選手について詳しく知りたいですか？"

        templates['player_count'] = f"馬三ソフトの参加選手は{total_players}名です。"

        templates['player_list'] = f"参加選手一覧: {', '.join(all_players)}"

        # 新規発見選手の特別テンプレート
        if new_players:
            templates['new_players_announcement'] = f"新たに{len(new_players)}名の選手を発見しました: {', '.join(new_players)}"
            templates['discovery_summary'] = f"データベース分析により、既存の13名に加えて{len(new_players)}名の追加選手を発見し、合計{total_players}名の選手情報を学習しました。"

        # 各選手用のテンプレート
        for player_info in expanded_database['player_details']:
            name = player_info['name']
            position = player_info['id']
            status = player_info['status']

            if status == 'newly_discovered':
                templates[f'{name}_basic'] = f"{name}選手についてお答えします。{name}選手は新たに発見された馬三ソフトのメンバーです。"
                templates[f'{name}_discovery'] = f"{name}選手は会話データの分析により新たに発見された選手です。"
            else:
                templates[f'{name}_basic'] = f"{name}選手についてお答えします。{name}選手は馬三ソフトの{position}番目に登録された選手です。"

            templates[f'{name}_detail'] = f"{name}選手は馬三ソフトの大切なメンバーです。"
            templates[f'{name}_question'] = f"{name}選手について何をお知りになりたいですか？"

        # 統計テンプレート
        templates['statistics'] = f"馬三ソフトの選手統計: 総選手数{total_players}名（既存{len(expanded_database['original_13_players'])}名 + 新規発見{len(new_players)}名）"

        # テンプレート保存
        template_path = 'expanded_response_templates.json'
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)

        print(f"✅ 拡張テンプレート保存: {template_path}")
        print(f"📊 作成テンプレート数: {len(templates)}")

        return templates

    def update_conversation_history(self, expanded_database: Dict):
        """会話履歴に拡張データを保存"""
        print(f"\n💾 会話履歴拡張更新")
        print("=" * 25)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            session_id = f'expanded_learning_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

            # 拡張学習の記録
            learning_entries = [
                {
                    'user_id': 'system_expansion',
                    'session_id': session_id,
                    'message_type': 'system',
                    'content': f'選手データベース拡張: 総選手数{expanded_database["team_info"]["total_players"]}名（新規発見{len(self.new_players)}名追加）',
                    'metadata': json.dumps({
                        'learning_type': 'database_expansion',
                        'total_players': expanded_database["team_info"]["total_players"],
                        'original_players': len(self.existing_players),
                        'new_players': len(self.new_players),
                        'new_player_names': sorted(list(self.new_players)),
                        'source': 'database_analysis'
                    }, ensure_ascii=False),
                    'timestamp': timestamp
                }
            ]

            # 新規発見選手の個別エントリー
            for player in self.new_players:
                learning_entries.append({
                    'user_id': 'system_expansion',
                    'session_id': session_id,
                    'message_type': 'system',
                    'content': f'新規発見選手: {player}選手が馬三ソフトのメンバーとして特定されました。',
                    'metadata': json.dumps({
                        'learning_type': 'new_player_discovery',
                        'player_name': player,
                        'team': '馬三ソフト',
                        'discovery_method': 'database_pattern_analysis'
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
            print(f"✅ 拡張学習データ保存完了: {len(learning_entries)}件")

        except Exception as e:
            print(f"❌ データベース保存エラー: {e}")
        finally:
            if 'conn' in locals():
                conn.close()

    def generate_expansion_summary(self, expanded_database: Dict):
        """拡張サマリー生成"""
        print(f"\n📊 拡張学習サマリー")
        print("=" * 25)

        summary = {
            'expansion_date': datetime.now().isoformat(),
            'original_players': len(self.existing_players),
            'newly_discovered_players': len(self.new_players),
            'total_players_after_expansion': expanded_database['team_info']['total_players'],
            'new_player_names': sorted(list(self.new_players)),
            'expansion_files_created': [
                'expanded_player_database.json',
                'expanded_response_templates.json',
                'player_expansion_summary.json'
            ],
            'discovery_methods': [
                'pattern_matching_analysis',
                'conversation_context_analysis',
                'database_text_mining'
            ]
        }

        print(f"📅 拡張実行日時: {summary['expansion_date']}")
        print(f"📊 既存選手数: {summary['original_players']}名")
        print(f"🆕 新規発見選手数: {summary['newly_discovered_players']}名")
        print(f"🏆 拡張後総選手数: {summary['total_players_after_expansion']}名")

        if self.new_players:
            print(f"\n🌟 新規発見選手一覧:")
            for i, player in enumerate(sorted(self.new_players), 1):
                print(f"   {i:2d}. {player}")

        # サマリー保存
        summary_path = 'player_expansion_summary.json'
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"\n💾 拡張サマリー保存: {summary_path}")

        return summary

def main():
    """メイン処理"""
    print("🔍 追加選手抽出・学習システム")
    print(f"📅 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # データベースパス
    db_path = os.path.join('..', 'db', 'conversation_history.db')

    if not os.path.exists(db_path):
        print(f"❌ データベースが見つかりません: {db_path}")
        return

    # 追加選手抽出システム
    extractor = AdditionalPlayerExtractor(db_path)

    print(f"📊 既存選手: {len(extractor.existing_players)}名")
    print(f"   {', '.join(extractor.existing_players)}")
    print()

    # 1. データベースから追加選手を検索
    all_candidates, pattern_results, conversations = extractor.search_database_for_additional_players()

    if not extractor.new_players:
        print("\n⚠️ 新規選手が見つかりませんでした。")
        print("   - データベースに追加の選手情報が記録されていない可能性があります")
        print("   - 既存の13名以外の選手情報がない可能性があります")
        return

    # 2. 新規選手の文脈分析
    player_contexts = extractor.analyze_new_players_context(conversations)

    # 3. 拡張選手データベース作成
    expanded_database = extractor.create_expanded_player_database(player_contexts)

    # 4. 拡張応答テンプレート作成
    templates = extractor.create_expanded_response_templates(expanded_database)

    # 5. 会話履歴に拡張データ保存
    extractor.update_conversation_history(expanded_database)

    # 6. 拡張サマリー生成
    summary = extractor.generate_expansion_summary(expanded_database)

    print(f"\n🎉 追加選手抽出・学習完了！")
    if extractor.new_players:
        print(f"✨ 新規発見選手: {', '.join(sorted(extractor.new_players))}")
        print(f"📊 拡張後総選手数: {len(extractor.existing_players) + len(extractor.new_players)}名")
    else:
        print(f"📊 既存選手のみ: {len(extractor.existing_players)}名")

if __name__ == "__main__":
    main()
