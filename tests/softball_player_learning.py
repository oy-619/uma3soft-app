"""
ソフトボール選手名学習システム
データベースからソフトボール関連の情報を抽出して選手名を学習
"""

import sqlite3
import re
import json
from datetime import datetime
from typing import List, Dict, Set
import os

class SoftballPlayerLearningSystem:
    """ソフトボール選手名学習システム"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.learned_names = set()

        # 有名なソフトボール選手名（日本）
        self.known_softball_players = {
            # 女子ソフトボール日本代表・プロ選手
            '上野由岐子', '峰幸代', '坂井寛子', '山田恵里', '藤田倭', '渥美万奈',
            '我妻悦子', '乾絵美', '三科真澄', '西山麗', '佐藤優花', '長崎望未',
            '市口侑果', '森さやか', '川畑瞳', '後藤希友', '清原奈侑', '藤原理恵',

            # 男子ソフトボール選手
            '松田光', '田中大貴', '中村亮太', '佐藤健太', '高橋直樹', '山本翔太',
            '鈴木一郎', '伊藤大輔', '小林雅英', '渡辺俊介', '加藤康介', '西田明央',

            # 大学・社会人ソフトボール
            '太田幸司', '宇津木妙子', '齋藤春香', '石川雅規', '杉内俊哉', '前田健太'
        }

        # ソフトボール関連用語
        self.softball_terms = {
            'ソフトボール', 'ソフト', '投手', 'ピッチャー', '捕手', 'キャッチャー',
            '内野手', '外野手', '打者', 'バッター', '走者', 'ランナー', 'コーチ',
            'プレイヤー', '選手', 'チーム', '試合', '大会', '甲子園', '全日本',
            'インカレ', '実業団', '社会人', '大学', '高校', '中学', '小学生',
            'リーグ', 'トーナメント', '決勝', '準決勝', '予選', '地区大会'
        }

        # ポジション関連
        self.positions = {
            '投手', 'ピッチャー', 'P', '捕手', 'キャッチャー', 'C',
            '一塁手', 'ファースト', '1B', '二塁手', 'セカンド', '2B',
            '三塁手', 'サード', '3B', '遊撃手', 'ショート', 'SS',
            '左翼手', 'レフト', 'LF', '中堅手', 'センター', 'CF',
            '右翼手', 'ライト', 'RF', '指名打者', 'DH'
        }

    def analyze_softball_database(self):
        """ソフトボール関連データベース分析"""
        print("🥎 ソフトボールデータベース分析開始")
        print("=" * 50)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # ソフトボール関連キーワードで検索
            softball_keywords = [
                'ソフトボール', 'ソフト', '投手', 'ピッチャー', '捕手', 'キャッチャー',
                '選手', 'プレイヤー', 'チーム', '試合', '大会', '練習', 'コーチ',
                '打者', 'バッター', 'ランナー', '走者', '内野', '外野', 'グローブ',
                'バット', 'ボール', 'ホームラン', 'ヒット', 'エラー', 'ストライク'
            ]

            all_conversations = []
            keyword_stats = {}

            for keyword in softball_keywords:
                cursor.execute("""
                    SELECT content, metadata, timestamp
                    FROM conversation_history
                    WHERE content LIKE ?
                    ORDER BY timestamp DESC
                """, (f'%{keyword}%',))

                keyword_conversations = cursor.fetchall()
                all_conversations.extend(keyword_conversations)
                keyword_stats[keyword] = len(keyword_conversations)

                if len(keyword_conversations) > 0:
                    print(f"   🔍 '{keyword}' で {len(keyword_conversations)} 件の会話を発見")

            # 重複除去
            unique_conversations = list(set(all_conversations))
            print(f"🎯 ユニークなソフトボール関連会話: {len(unique_conversations)} 件")

            # 選手名抽出
            extracted_names = self.extract_softball_player_names(unique_conversations)

            return {
                'softball_conversations': unique_conversations,
                'extracted_names': extracted_names,
                'keyword_stats': keyword_stats,
                'total_conversations': len(unique_conversations)
            }

        except Exception as e:
            print(f"❌ データベース分析エラー: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    def extract_softball_player_names(self, conversations: List[tuple]) -> Set[str]:
        """ソフトボール選手名抽出"""
        print("\n🥎 ソフトボール選手名抽出処理")
        print("-" * 30)

        extracted_names = set()

        # ソフトボール特化の名前パターン
        softball_patterns = [
            r'([一-龯]{2,4})\s*選手',                    # 名前 選手
            r'選手\s*[：:]\s*([一-龯]{2,4})',            # 選手: 名前
            r'([一-龯]{2,4})\s*投手',                    # 名前 投手
            r'投手\s*[：:]\s*([一-龯]{2,4})',            # 投手: 名前
            r'([一-龯]{2,4})\s*ピッチャー',              # 名前 ピッチャー
            r'ピッチャー\s*[：:]\s*([一-龯]{2,4})',      # ピッチャー: 名前
            r'([一-龯]{2,4})\s*キャッチャー',            # 名前 キャッチャー
            r'キャッチャー\s*[：:]\s*([一-龯]{2,4})',    # キャッチャー: 名前
            r'([一-龯]{2,4})\s*が\s*投げ',               # 名前 が投げ
            r'([一-龯]{2,4})\s*が\s*打っ',               # 名前 が打っ
            r'([一-龯]{2,4})\s*が\s*走っ',               # 名前 が走っ
            r'([一-龯]{2,4})\s*の\s*投球',               # 名前 の投球
            r'([一-龯]{2,4})\s*の\s*打撃',               # 名前 の打撃
            r'([一-龯]{2,4})\s*コーチ',                  # 名前 コーチ
            r'コーチ\s*[：:]\s*([一-龯]{2,4})',          # コーチ: 名前
            r'([一-龯]{2,4})\s*監督',                    # 名前 監督
            r'監督\s*[：:]\s*([一-龯]{2,4})',            # 監督: 名前
            r'([一-龯]{2,4})\s*さん',                    # 名前 さん
            r'([一-龯]{2,4})\s*君',                      # 名前 君
            r'([一-龯]{2,4})\s*ちゃん',                  # 名前 ちゃん
        ]

        for content, metadata, timestamp in conversations:
            text = content or ''

            # 既知のソフトボール選手名の直接検索（最優先）
            for player in self.known_softball_players:
                if player in text:
                    extracted_names.add(player)
                    print(f"   🏆 既知選手名検出: '{player}'")

            # パターンマッチング
            for pattern in softball_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    name = match.strip()

                    # フィルタリング条件
                    if (self.is_valid_softball_name(name) and
                        name not in self.softball_terms and
                        name not in self.positions):

                        extracted_names.add(name)
                        print(f"   📝 パターンマッチ: '{name}'")

        # 候補名の検証
        validated_names = self.validate_softball_names(extracted_names, conversations)

        print(f"\n📊 最終ソフトボール選手名: {len(validated_names)} 個")
        return validated_names

    def is_valid_softball_name(self, name: str) -> bool:
        """ソフトボール選手名として有効かチェック"""
        # 長さチェック
        if len(name) < 2 or len(name) > 5:
            return False

        # 除外する一般的な単語
        exclude_words = {
            'です', 'ます', 'した', 'する', 'ある', 'なる', 'いる', 'もの', 'こと',
            'とき', 'とか', 'など', 'まで', 'から', 'より', 'では', 'でも', 'その',
            'この', 'あの', 'どの', 'すべて', 'みんな', '全部', '一番', '最初', '最後',
            'ソフト', '選手', '投手', '打者', 'チーム', '試合', '練習', '大会', '監督'
        }

        if name in exclude_words:
            return False

        # 漢字の割合チェック（日本人名として妥当）
        kanji_count = len([c for c in name if '\u4e00' <= c <= '\u9faf'])
        if kanji_count == 0:  # 漢字が含まれていない
            return False

        # 一般的な日本の姓の文字が含まれているかチェック
        common_surname_chars = [
            '田', '中', '佐', '藤', '山', '木', '川', '井', '村', '島', '原', '本',
            '松', '林', '池', '橋', '石', '前', '後', '岡', '西', '東', '南', '北',
            '上', '下', '高', '小', '大', '長', '渡', '伊', '加', '近', '遠', '新'
        ]

        has_surname_char = any(char in name for char in common_surname_chars)

        return has_surname_char

    def validate_softball_names(self, names: Set[str], conversations: List[tuple]) -> Set[str]:
        """ソフトボール選手名の検証"""
        print("\n🔍 ソフトボール選手名検証")
        print("-" * 20)

        validated_names = set()

        for name in names:
            confidence_score = 0.0
            context_count = 0
            softball_context_count = 0

            # コンテキスト分析
            for content, metadata, timestamp in conversations:
                text = content or ''
                if name in text:
                    context_count += 1

                    # ソフトボール関連文脈の確認
                    softball_context_keywords = [
                        'ソフトボール', 'ソフト', '投手', 'ピッチャー', '捕手', 'キャッチャー',
                        '選手', '試合', '練習', 'チーム', '大会', '投球', '打撃', '守備',
                        'グローブ', 'バット', 'ボール', 'コーチ', '監督'
                    ]

                    context_score = sum(1 for keyword in softball_context_keywords if keyword in text)
                    if context_score > 0:
                        softball_context_count += 1
                        confidence_score += context_score * 0.1

            # 既知選手名は最高スコア
            if name in self.known_softball_players:
                confidence_score = 1.0

            # 出現頻度による信頼度調整
            if context_count > 1:
                confidence_score += 0.2

            # ソフトボール文脈での出現率
            if context_count > 0:
                softball_ratio = softball_context_count / context_count
                confidence_score += softball_ratio * 0.3

            # 名前の長さによる調整
            if 2 <= len(name) <= 4:
                confidence_score += 0.1

            # 最終判定
            if confidence_score >= 0.3:
                validated_names.add(name)
                print(f"   ✅ 検証OK: '{name}' (信頼度: {confidence_score:.2f}, 出現: {context_count}回, ソフト文脈: {softball_context_count}回)")
            else:
                print(f"   ❌ 検証NG: '{name}' (信頼度: {confidence_score:.2f}, 出現: {context_count}回)")

        return validated_names

    def create_softball_templates(self, validated_names: Set[str]) -> Dict[str, str]:
        """ソフトボール選手用テンプレート作成"""
        print("\n📝 ソフトボールテンプレート作成")
        print("-" * 30)

        templates = {}

        for name in validated_names:
            # 基本テンプレート
            templates[f'{name}について'] = f'{name}選手についてお話しします。どのようなことを知りたいですか？'
            templates[f'{name}選手'] = f'{name}選手のことですね。ソフトボールに関することでしたら何でもお聞きください。'

            # ポジション関連
            templates[f'{name}投手'] = f'{name}投手についてご案内します。投球スタイルや成績についてお知りになりたいですか？'
            templates[f'{name}の投球'] = f'{name}選手の投球についてお答えします。どのような詳細をお聞きになりたいですか？'
            templates[f'{name}の打撃'] = f'{name}選手の打撃についてお話しします。打率や特徴についてご質問ください。'
            templates[f'{name}の守備'] = f'{name}選手の守備についてご案内します。ポジションや守備力についてお聞きください。'

            # 試合・成績関連
            templates[f'{name}の成績'] = f'{name}選手の成績についてお答えします。どの期間や項目についてお知りになりたいですか？'
            templates[f'{name}の試合'] = f'{name}選手の試合についてお話しします。具体的にはどの試合についてお聞きになりたいですか？'

            # 既知選手の場合はより詳細なテンプレート
            if name in self.known_softball_players:
                templates[f'{name}の経歴'] = f'{name}選手の経歴についてご案内します。どの時期や所属チームについてお知りになりたいですか？'
                templates[f'{name}の代表歴'] = f'{name}選手の代表歴についてお答えします。日本代表での活躍についてお聞きください。'

        print(f"✅ 作成されたテンプレート数: {len(templates)}")
        return templates

    def save_softball_results(self, results: Dict, output_dir: str):
        """ソフトボール学習結果保存"""
        os.makedirs(output_dir, exist_ok=True)

        # 学習結果保存
        learning_results = {
            'timestamp': datetime.now().isoformat(),
            'sport': 'softball',
            'total_conversations_analyzed': results['total_conversations'],
            'extracted_names': list(results['extracted_names']),
            'known_players_found': list(results['extracted_names'] & self.known_softball_players),
            'new_names_discovered': list(results['extracted_names'] - self.known_softball_players),
            'keyword_statistics': results['keyword_stats'],
            'extraction_method': 'softball_specialized_pattern_matching'
        }

        # ファイル保存
        results_path = os.path.join(output_dir, 'softball_player_names.json')
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(learning_results, f, ensure_ascii=False, indent=2)

        templates = self.create_softball_templates(results['extracted_names'])
        templates_path = os.path.join(output_dir, 'softball_player_templates.json')
        with open(templates_path, 'w', encoding='utf-8') as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)

        print(f"\n💾 保存完了:")
        print(f"   📊 学習結果: {results_path}")
        print(f"   📝 テンプレート: {templates_path}")

        return learning_results, templates

def main():
    """メイン処理"""
    print("🥎 ソフトボール選手名学習システム")
    print(f"📅 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # データベースパス
    db_path = os.path.join('..', 'db', 'conversation_history.db')

    if not os.path.exists(db_path):
        print(f"❌ データベースが見つかりません: {db_path}")
        return

    # ソフトボール学習システム
    softball_system = SoftballPlayerLearningSystem(db_path)

    # 1. データベース分析
    analysis_results = softball_system.analyze_softball_database()

    if not analysis_results:
        print("❌ データベース分析に失敗しました")
        return

    # 2. 結果保存
    output_dir = '.'
    learning_results, templates = softball_system.save_softball_results(analysis_results, output_dir)

    # 3. 結果サマリー
    print(f"\n📊 ソフトボール学習結果サマリー")
    print("-" * 50)
    print(f"   🎯 分析した会話数: {analysis_results['total_conversations']}")
    print(f"   👤 抽出された選手名: {len(analysis_results['extracted_names'])}")
    print(f"   🏆 既知選手名発見: {len(learning_results['known_players_found'])}")
    print(f"   🆕 新発見選手名: {len(learning_results['new_names_discovered'])}")
    print(f"   📝 作成テンプレート: {len(templates)}")

    # 活用度の高いキーワード表示
    print(f"\n🔍 キーワード検索結果:")
    sorted_keywords = sorted(analysis_results['keyword_stats'].items(), key=lambda x: x[1], reverse=True)
    for keyword, count in sorted_keywords[:10]:
        if count > 0:
            print(f"      {keyword}: {count}件")

    # 発見された選手名を表示
    if learning_results['known_players_found']:
        print(f"\n🏆 発見された既知ソフトボール選手名:")
        for player in sorted(learning_results['known_players_found']):
            print(f"      ✅ {player}")

    if learning_results['new_names_discovered']:
        print(f"\n🆕 新発見のソフトボール選手名候補:")
        for name in sorted(learning_results['new_names_discovered']):
            print(f"      🔍 {name}")

    print(f"\n🎉 ソフトボール選手名学習完了！")

if __name__ == "__main__":
    main()
