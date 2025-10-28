"""
DBの配車情報から選手の名前を学習するシステム
"""

import sqlite3
import re
import json
from datetime import datetime
from typing import List, Dict, Set
import os

class PlayerNameLearningSystem:
    """配車情報から選手名を学習するシステム"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.learned_names = set()
        self.name_patterns = []

    def analyze_conversation_database(self):
        """会話データベースを分析して配車情報を抽出"""
        print("🔍 データベース分析開始")
        print("=" * 50)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # テーブル構造確認
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"📊 利用可能なテーブル: {[table[0] for table in tables]}")

            # 会話履歴テーブルの確認
            if ('conversation_history',) in tables:
                cursor.execute("PRAGMA table_info(conversation_history)")
                columns = cursor.fetchall()
                print(f"📋 conversation_historyカラム: {[col[1] for col in columns]}")

                # 配車関連の会話を検索（実際のDBスキーマに合わせて修正）
                cursor.execute("""
                    SELECT content, metadata, timestamp
                    FROM conversation_history
                    WHERE content LIKE '%配車%'
                       OR content LIKE '%選手%'
                       OR content LIKE '%騎手%'
                       OR content LIKE '%名前%'
                       OR content LIKE '%ドライバー%'
                       OR content LIKE '%競馬%'
                    ORDER BY timestamp DESC
                    LIMIT 100
                """)

                dispatching_conversations = cursor.fetchall()
                print(f"🚗 配車関連会話数: {len(dispatching_conversations)}")

                # 選手名抽出
                extracted_names = self.extract_player_names_from_conversations(dispatching_conversations)

                return {
                    'dispatching_conversations': dispatching_conversations,
                    'extracted_names': extracted_names,
                    'total_conversations': len(dispatching_conversations)
                }

        except Exception as e:
            print(f"❌ データベース分析エラー: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    def extract_player_names_from_conversations(self, conversations: List[tuple]) -> Set[str]:
        """会話から選手名を抽出（DB構造に合わせて修正）"""
        print("\n🏇 選手名抽出処理")
        print("-" * 30)

        extracted_names = set()

        # 日本の一般的な姓のパターン
        common_surnames = [
            '田中', '佐藤', '鈴木', '高橋', '渡辺', '伊藤', '山田', '中村', '小林', '加藤',
            '吉田', '山本', '斎藤', '松本', '井上', '木村', '林', '清水', '山崎', '池田',
            '橋本', '石田', '中島', '前田', '藤田', '後藤', '岡田', '長谷川', '石川', '近藤'
        ]

        # 競馬関連の有名騎手名（例）
        famous_jockeys = [
            '武豊', '福永祐一', '川田将雅', '戸崎圭太', '岩田康誠', '池添謙一', '和田竜二',
            '藤岡康太', '松山弘平', '鮫島克駿', '丸山元気', '横山典弘', '蛯名正義', '内田博幸'
        ]

        # 名前パターンの定義
        name_patterns = [
            r'選手[：:]\s*([一-龯ぁ-んァ-ン\s]{2,8})',  # 選手: 名前
            r'([一-龯ぁ-んァ-ン]{2,4})\s*選手',          # 名前 選手
            r'騎手[：:]\s*([一-龯ぁ-んァ-ン\s]{2,8})',    # 騎手: 名前
            r'([一-龯ぁ-んァ-ン]{2,4})\s*騎手',          # 名前 騎手
            r'配車[：:]\s*([一-龯ぁ-んァ-ン\s]{2,8})',    # 配車: 名前
            r'ドライバー[：:]\s*([一-龯ぁ-んァ-ン\s]{2,8})', # ドライバー: 名前
            r'([一-龯ぁ-んァ-ン]{2,4})\s*さん',           # 名前 さん
            r'([一-龯ぁ-んァ-ン]{2,4})\s*君',             # 名前 君
        ]

        # 有名騎手名の直接検索
        all_known_names = set(famous_jockeys)

        for content, metadata, timestamp in conversations:
            text_content = content or ''

            # パターンマッチングで抽出
            for pattern in name_patterns:
                matches = re.findall(pattern, text_content)
                for match in matches:
                    name = match.strip()
                    if len(name) >= 2 and len(name) <= 8:
                        extracted_names.add(name)
                        print(f"   📝 パターンから抽出: '{name}'")

            # 有名騎手名の直接検索
            for jockey in famous_jockeys:
                if jockey in text_content:
                    extracted_names.add(jockey)
                    print(f"   🏆 有名騎手名検出: '{jockey}'")

            # 一般的な姓を含む名前の特別処理
            for surname in common_surnames:
                # 姓 + 名のパターンを検索
                pattern = f'{surname}[一-龯ぁ-んァ-ン]{{1,3}}'
                matches = re.findall(pattern, text_content)
                for match in matches:
                    if len(match) >= 3 and len(match) <= 6:
                        extracted_names.add(match)
                        print(f"   👤 姓名パターンから抽出: '{match}'")

        print(f"\n📊 抽出された選手名総数: {len(extracted_names)}")
        return extracted_names

    def learn_player_names(self, extracted_names: Set[str]) -> Dict:
        """抽出された選手名を学習"""
        print("\n🧠 選手名学習処理")
        print("-" * 30)

        learning_results = {
            'learned_names': list(extracted_names),
            'name_categories': {
                'jockey_names': [],      # 騎手名
                'driver_names': [],      # ドライバー名
                'general_names': []      # 一般的な名前
            },
            'name_patterns': [],
            'confidence_scores': {}
        }

        # 名前の分類と信頼度スコア計算
        for name in extracted_names:
            confidence = self.calculate_name_confidence(name)
            learning_results['confidence_scores'][name] = confidence

            # 高い信頼度の名前を分類
            if confidence >= 0.7:
                learning_results['name_categories']['general_names'].append(name)
                print(f"   ✅ 学習完了: '{name}' (信頼度: {confidence:.2f})")
            else:
                print(f"   ⚠️ 低信頼度: '{name}' (信頼度: {confidence:.2f})")

        # 名前パターンの生成
        learning_results['name_patterns'] = self.generate_name_patterns(extracted_names)

        return learning_results

    def calculate_name_confidence(self, name: str) -> float:
        """名前の信頼度を計算"""
        confidence = 0.5  # 基本信頼度

        # 長さによる調整
        if 2 <= len(name) <= 4:
            confidence += 0.3
        elif len(name) == 5:
            confidence += 0.1
        else:
            confidence -= 0.2

        # 漢字の割合
        kanji_count = len([c for c in name if '\u4e00' <= c <= '\u9faf'])
        if kanji_count >= len(name) * 0.5:
            confidence += 0.2

        # 一般的でない文字の検出
        if any(c in name for c in ['車', '配', '選手', '騎手', 'ドライバー']):
            confidence -= 0.4

        return max(0.0, min(1.0, confidence))

    def generate_name_patterns(self, names: Set[str]) -> List[str]:
        """名前パターンを生成"""
        patterns = []

        for name in names:
            # 名前の直前・直後のコンテキストパターン
            patterns.extend([
                f'{name}選手',
                f'{name}騎手',
                f'{name}さん',
                f'選手{name}',
                f'騎手{name}',
                f'{name}の配車',
                f'{name}について'
            ])

        return list(set(patterns))

    def save_learned_names(self, learning_results: Dict, output_path: str):
        """学習結果を保存"""
        print(f"\n💾 学習結果保存: {output_path}")

        # タイムスタンプ追加
        learning_results['learning_timestamp'] = datetime.now().isoformat()
        learning_results['total_learned_names'] = len(learning_results['learned_names'])

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(learning_results, f, ensure_ascii=False, indent=2)

        print(f"✅ 保存完了: {len(learning_results['learned_names'])}個の選手名を学習")

    def integrate_with_response_system(self, learning_results: Dict):
        """改善システムとの統合"""
        print(f"\n🔗 応答システム統合")
        print("-" * 30)

        try:
            # 改善システムのインポート
            import sys
            tests_path = os.path.join(os.path.dirname(__file__), '..', 'tests')
            sys.path.insert(0, tests_path)

            from improved_response_system import ImprovedResponseGenerator

            # 選手名を使ったテンプレート拡張
            player_templates = {}

            for name in learning_results['learned_names']:
                if learning_results['confidence_scores'].get(name, 0) >= 0.7:
                    player_templates[f'{name}について'] = f'{name}選手についてお話しします。何か具体的に知りたいことはありますか？'
                    player_templates[f'{name}の配車'] = f'{name}選手の配車についてご案内します。'
                    player_templates[f'{name}選手'] = f'{name}選手のことですね。どのようなことをお聞きになりたいですか？'

            print(f"📝 作成されたテンプレート数: {len(player_templates)}")

            # テンプレート保存
            template_path = os.path.join(os.path.dirname(__file__), '..', 'tests', 'player_name_templates.json')
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(player_templates, f, ensure_ascii=False, indent=2)

            print(f"✅ 選手名テンプレート保存: {template_path}")

            return player_templates

        except Exception as e:
            print(f"❌ 統合エラー: {e}")
            return {}

def main():
    """メイン処理"""
    print("🏇 配車情報選手名学習システム")
    print(f"📅 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # データベースパス
    db_path = os.path.join('..', 'db', 'conversation_history.db')

    if not os.path.exists(db_path):
        print(f"❌ データベースが見つかりません: {db_path}")
        return

    # 学習システム初期化
    learning_system = PlayerNameLearningSystem(db_path)

    # 1. データベース分析
    analysis_result = learning_system.analyze_conversation_database()

    if not analysis_result:
        print("❌ データベース分析に失敗しました")
        return

    # 2. 選手名学習
    learning_results = learning_system.learn_player_names(analysis_result['extracted_names'])

    # 3. 学習結果保存
    output_path = os.path.join('..', 'tests', 'learned_player_names.json')
    learning_system.save_learned_names(learning_results, output_path)

    # 4. 応答システム統合
    player_templates = learning_system.integrate_with_response_system(learning_results)

    # 5. 結果サマリー
    print(f"\n📊 学習結果サマリー")
    print("-" * 40)
    print(f"   🎯 分析した会話数: {analysis_result['total_conversations']}")
    print(f"   👤 抽出された選手名: {len(analysis_result['extracted_names'])}")
    print(f"   📚 学習した選手名: {len(learning_results['learned_names'])}")
    print(f"   ✅ 高信頼度選手名: {len([n for n, c in learning_results['confidence_scores'].items() if c >= 0.7])}")
    print(f"   📝 作成テンプレート: {len(player_templates)}")

    # 高信頼度の選手名を表示
    high_confidence_names = [
        name for name, confidence in learning_results['confidence_scores'].items()
        if confidence >= 0.7
    ]

    if high_confidence_names:
        print(f"\n🏆 高信頼度選手名:")
        for name in sorted(high_confidence_names):
            confidence = learning_results['confidence_scores'][name]
            print(f"      {name} (信頼度: {confidence:.2f})")

    print(f"\n🎉 選手名学習完了！")

if __name__ == "__main__":
    main()
