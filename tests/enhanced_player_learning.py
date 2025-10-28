"""
改良版：より精密な選手名学習システム
"""

import sqlite3
import re
import json
from datetime import datetime
from typing import List, Dict, Set
import os

class EnhancedPlayerNameLearningSystem:
    """改良版選手名学習システム"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.learned_names = set()

        # 実際の競馬騎手名データベース
        self.known_jockeys = {
            '武豊', '福永祐一', '川田将雅', '戸崎圭太', '岩田康誠', '池添謙一', '和田竜二',
            '藤岡康太', '松山弘平', '鮫島克駿', '丸山元気', '横山典弘', '蛯名正義', '内田博幸',
            '田辺裕信', '石橋脩', '北村友一', '幸英明', '藤岡佑介', '吉田隼人', '柴山雄一',
            '三浦皇成', '大野拓弥', '松田大作', '菱田裕二', '野中悠太郎', '永島まなみ',
            '古川吉洋', '藤田菜七子', '今村聖奈', '菅原明良', '永野猛蔵', '坂井瑠星'
        }

        # 一般的な競馬用語（除外用）
        self.racing_terms = {
            '競馬', '競走', '騎乗', '調教', '厩舎', '馬主', '生産', '血統', '配合',
            'レース', 'コース', '芝', 'ダート', '距離', '重賞', 'G1', 'G2', 'G3',
            '勝利', '優勝', '入着', '着順', '馬券', '単勝', '複勝', '馬連', '馬単',
            '三連複', '三連単', 'ワイド', '枠連', '枠単', 'WIN5'
        }

    def analyze_enhanced_database(self):
        """強化されたデータベース分析"""
        print("🔍 強化データベース分析開始")
        print("=" * 50)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # より広範囲な競馬関連キーワードで検索
            racing_keywords = [
                '競馬', '騎手', '騎乗', '勝利', 'レース', '競走', '調教', '厩舎',
                '配車', '選手', 'ドライバー', '武豊', '福永', '川田', '戸崎',
                'G1', 'G2', 'G3', '重賞', '馬券', '単勝', '複勝'
            ]

            all_conversations = []

            for keyword in racing_keywords:
                cursor.execute("""
                    SELECT content, metadata, timestamp
                    FROM conversation_history
                    WHERE content LIKE ?
                    ORDER BY timestamp DESC
                """, (f'%{keyword}%',))

                keyword_conversations = cursor.fetchall()
                all_conversations.extend(keyword_conversations)
                print(f"   🔍 '{keyword}' で {len(keyword_conversations)} 件の会話を発見")

            # 重複除去
            unique_conversations = list(set(all_conversations))
            print(f"🎯 ユニークな競馬関連会話: {len(unique_conversations)} 件")

            # 選手名抽出
            extracted_names = self.enhanced_name_extraction(unique_conversations)

            return {
                'racing_conversations': unique_conversations,
                'extracted_names': extracted_names,
                'total_conversations': len(unique_conversations)
            }

        except Exception as e:
            print(f"❌ データベース分析エラー: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    def enhanced_name_extraction(self, conversations: List[tuple]) -> Set[str]:
        """強化された名前抽出"""
        print("\n🏇 強化選手名抽出処理")
        print("-" * 30)

        extracted_names = set()

        # より精密な名前パターン
        precise_patterns = [
            r'騎手\s*[：:]\s*([一-龯]{2,4})',           # 騎手: 名前
            r'([一-龯]{2,4})\s*騎手',                   # 名前 騎手
            r'([一-龯]{2,4})\s*選手',                   # 名前 選手
            r'([一-龯]{2,4})\s*ジョッキー',             # 名前 ジョッキー
            r'([一-龯]{2,4})\s*が\s*騎乗',              # 名前 が騎乗
            r'([一-龯]{2,4})\s*が\s*勝利',              # 名前 が勝利
            r'([一-龯]{2,4})\s*が\s*優勝',              # 名前 が優勝
            r'([一-龯]{2,4})\s*の\s*騎乗',              # 名前 の騎乗
            r'([一-龯]{2,4})\s*による\s*勝利',          # 名前 による勝利
        ]

        for content, metadata, timestamp in conversations:
            text = content or ''

            # 既知の騎手名の直接検索（最優先）
            for jockey in self.known_jockeys:
                if jockey in text:
                    extracted_names.add(jockey)
                    print(f"   🏆 既知騎手名検出: '{jockey}'")

            # 精密パターンマッチング
            for pattern in precise_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    name = match.strip()

                    # フィルタリング条件
                    if (len(name) >= 2 and len(name) <= 4 and
                        name not in self.racing_terms and
                        not any(term in name for term in ['です', 'ます', 'する', 'した', 'ある', 'なる']) and
                        self.is_likely_person_name(name)):

                        extracted_names.add(name)
                        print(f"   📝 パターンマッチ: '{name}' (パターン: {pattern})")

        # 候補名の信頼度評価
        validated_names = self.validate_extracted_names(extracted_names, conversations)

        print(f"\n📊 最終選手名: {len(validated_names)} 個")
        return validated_names

    def is_likely_person_name(self, name: str) -> bool:
        """人名らしさの判定"""
        # 一般的な日本の姓の一部
        common_surname_chars = ['田', '中', '佐', '藤', '山', '木', '川', '井', '村', '島', '原', '本', '松', '林', '池', '橋', '石', '前', '後', '岡']

        # 姓の文字が含まれているか
        has_surname_char = any(char in name for char in common_surname_chars)

        # ひらがな・カタカナが多すぎないか
        hiragana_katakana_count = len([c for c in name if 'ぁ' <= c <= 'ん' or 'ァ' <= c <= 'ン'])

        return has_surname_char or hiragana_katakana_count <= 1

    def validate_extracted_names(self, names: Set[str], conversations: List[tuple]) -> Set[str]:
        """抽出された名前の検証"""
        print("\n🔍 名前候補検証")
        print("-" * 20)

        validated_names = set()

        for name in names:
            confidence_score = 0.0
            context_count = 0

            # コンテキスト分析
            for content, metadata, timestamp in conversations:
                text = content or ''
                if name in text:
                    context_count += 1

                    # 競馬関連文脈の確認
                    racing_context_keywords = ['騎手', '騎乗', '勝利', '優勝', 'レース', '競走', '競馬']
                    context_score = sum(1 for keyword in racing_context_keywords if keyword in text)
                    confidence_score += context_score * 0.1

            # 既知騎手名は最高スコア
            if name in self.known_jockeys:
                confidence_score = 1.0

            # 出現頻度による信頼度調整
            if context_count > 1:
                confidence_score += 0.2

            # 名前の長さによる調整
            if 2 <= len(name) <= 4:
                confidence_score += 0.1

            # 最終判定
            if confidence_score >= 0.3:  # 閾値を下げて幅広く学習
                validated_names.add(name)
                print(f"   ✅ 検証OK: '{name}' (信頼度: {confidence_score:.2f}, 出現: {context_count}回)")
            else:
                print(f"   ❌ 検証NG: '{name}' (信頼度: {confidence_score:.2f}, 出現: {context_count}回)")

        return validated_names

    def create_enhanced_templates(self, validated_names: Set[str]) -> Dict[str, str]:
        """強化されたテンプレート作成"""
        print("\n📝 強化テンプレート作成")
        print("-" * 30)

        templates = {}

        for name in validated_names:
            # 基本テンプレート
            templates[f'{name}について'] = f'{name}についてお話しします。どのようなことを知りたいですか？'
            templates[f'{name}選手'] = f'{name}選手のことですね。競馬に関することでしたら何でもお聞きください。'
            templates[f'{name}騎手'] = f'{name}騎手につ���てご案内します。騎乗成績や最近のレース結果など、お知りになりたいことはありますか？'

            # 既知騎手の場合はより詳細なテンプレート
            if name in self.known_jockeys:
                templates[f'{name}の成績'] = f'{name}騎手の成績についてお答えします。具体的にはどの期間や内容をお知りになりたいですか？'
                templates[f'{name}の騎乗'] = f'{name}騎手の騎乗についてご案内します。どのレースや馬についてお聞きになりたいですか？'
                templates[f'{name}の勝利'] = f'{name}騎手の勝利についてお話しします。重賞勝利や最近の活躍についてお知りになりたいですか？'

        print(f"✅ 作成されたテンプレート数: {len(templates)}")
        return templates

    def save_enhanced_results(self, results: Dict, output_dir: str):
        """強化された結果保存"""
        os.makedirs(output_dir, exist_ok=True)

        # 学習結果保存
        learning_results = {
            'timestamp': datetime.now().isoformat(),
            'total_conversations_analyzed': results['total_conversations'],
            'extracted_names': list(results['extracted_names']),
            'known_jockeys_found': list(results['extracted_names'] & self.known_jockeys),
            'new_names_discovered': list(results['extracted_names'] - self.known_jockeys),
            'extraction_method': 'enhanced_pattern_matching_with_validation'
        }

        # ファイル保存
        results_path = os.path.join(output_dir, 'enhanced_player_names.json')
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(learning_results, f, ensure_ascii=False, indent=2)

        templates = self.create_enhanced_templates(results['extracted_names'])
        templates_path = os.path.join(output_dir, 'enhanced_player_templates.json')
        with open(templates_path, 'w', encoding='utf-8') as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)

        print(f"\n💾 保存完了:")
        print(f"   📊 学習結果: {results_path}")
        print(f"   📝 テンプレート: {templates_path}")

        return learning_results, templates

def main():
    """メイン処理"""
    print("🏇 強化版選手名学習システム")
    print(f"📅 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # データベースパス
    db_path = os.path.join('..', 'db', 'conversation_history.db')

    if not os.path.exists(db_path):
        print(f"❌ データベースが見つかりません: {db_path}")
        return

    # 強化学習システム
    enhanced_system = EnhancedPlayerNameLearningSystem(db_path)

    # 1. 強化データベース分析
    analysis_results = enhanced_system.analyze_enhanced_database()

    if not analysis_results:
        print("❌ データベース分析に失敗しました")
        return

    # 2. 結果保存
    output_dir = '.'
    learning_results, templates = enhanced_system.save_enhanced_results(analysis_results, output_dir)

    # 3. 結果サマリー
    print(f"\n📊 強化学習結果サマリー")
    print("-" * 50)
    print(f"   🎯 分析した会話数: {analysis_results['total_conversations']}")
    print(f"   👤 抽出された選手名: {len(analysis_results['extracted_names'])}")
    print(f"   🏆 既知騎手名発見: {len(learning_results['known_jockeys_found'])}")
    print(f"   🆕 新発見選手名: {len(learning_results['new_names_discovered'])}")
    print(f"   📝 作成テンプレート: {len(templates)}")

    # 発見された騎手名を表示
    if learning_results['known_jockeys_found']:
        print(f"\n🏆 発見された既知騎手名:")
        for jockey in sorted(learning_results['known_jockeys_found']):
            print(f"      ✅ {jockey}")

    if learning_results['new_names_discovered']:
        print(f"\n🆕 新発見の選手名候補:")
        for name in sorted(learning_results['new_names_discovered']):
            print(f"      🔍 {name}")

    print(f"\n🎉 強化版選手名学習完了！")

if __name__ == "__main__":
    main()
