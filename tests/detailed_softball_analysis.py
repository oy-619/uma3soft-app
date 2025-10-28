"""
ソフトボール関連データの詳細分析と選手名学習強化システム
"""

import sqlite3
import re
import json
from datetime import datetime
from typing import List, Dict, Set
import os

class DetailedSoftballAnalysis:
    """詳細ソフトボール分析システム"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def analyze_softball_conversations_detail(self):
        """ソフトボール会話の詳細分析"""
        print("🔍 ソフトボール会話詳細分析")
        print("=" * 50)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # ソフト関連の会話を詳細取得
            cursor.execute("""
                SELECT content, metadata, timestamp
                FROM conversation_history
                WHERE content LIKE '%ソフト%'
                ORDER BY timestamp DESC
                LIMIT 50
            """)

            softball_conversations = cursor.fetchall()
            print(f"📊 'ソフト'を含む会話: {len(softball_conversations)} 件")

            print("\n📝 実際の会話内容サンプル:")
            print("-" * 40)

            for i, (content, metadata, timestamp) in enumerate(softball_conversations[:10], 1):
                print(f"{i}. [{timestamp}] {content[:100]}...")
                if metadata:
                    print(f"   メタデータ: {metadata[:50]}...")
                print()

            # パターン分析
            self.analyze_name_patterns(softball_conversations)

            # 学習データ生成
            self.generate_learning_data(softball_conversations)

            return softball_conversations

        except Exception as e:
            print(f"❌ 詳細分析エラー: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    def analyze_name_patterns(self, conversations: List[tuple]):
        """名前パターンの詳細分析"""
        print("\n🔍 名前パターン詳細分析")
        print("-" * 30)

        # より緩い条件での名前候補抽出
        loose_patterns = [
            r'([一-龯ぁ-んァ-ン]{2,6})\s*さん',          # 名前 さん
            r'([一-龯ぁ-んァ-ン]{2,6})\s*君',            # 名前 君
            r'([一-龯ぁ-んァ-ン]{2,6})\s*ちゃん',        # 名前 ちゃん
            r'([一-龯ぁ-んァ-ン]{2,6})\s*選手',          # 名前 選手
            r'([一-龯ぁ-んァ-ン]{2,6})\s*が',            # 名前 が
            r'([一-龯ぁ-んァ-ン]{2,6})\s*は',            # 名前 は
            r'([一-龯ぁ-んァ-ン]{2,6})\s*も',            # 名前 も
            r'([一-龯ぁ-んァ-ン]{2,6})\s*の',            # 名前 の
            r'([一-龯ぁ-んァ-ン]{2,6})\s*で',            # 名前 で
            r'([一-龯ぁ-んァ-ン]{2,6})\s*と',            # 名前 と
        ]

        potential_names = set()
        pattern_stats = {}

        for content, metadata, timestamp in conversations:
            text = content or ''

            for pattern in loose_patterns:
                matches = re.findall(pattern, text)
                if matches:
                    if pattern not in pattern_stats:
                        pattern_stats[pattern] = []

                    pattern_stats[pattern].extend(matches)
                    potential_names.update(matches)

        print(f"📊 潜在的な名前候補: {len(potential_names)} 個")

        # パターン別統計
        for pattern, matches in pattern_stats.items():
            if matches:
                print(f"   パターン {pattern}: {len(set(matches))} 個のユニーク名前")
                unique_matches = list(set(matches))[:5]  # 最初の5個を表示
                print(f"      例: {', '.join(unique_matches)}")

        # フィルタリングして人名っぽいものを抽出
        filtered_names = self.filter_potential_names(potential_names, conversations)

        return filtered_names

    def filter_potential_names(self, names: Set[str], conversations: List[tuple]) -> Set[str]:
        """人名候補のフィルタリング"""
        print(f"\n🔍 人名候補フィルタリング")
        print("-" * 20)

        filtered_names = set()

        # 除外する一般的な単語（拡張版）
        exclude_words = {
            'ソフト', 'ソフトウェア', 'ソフトボール', 'ソフトバンク', 'ソフトクリーム',
            'チーム', '選手', '試合', '練習', '大会', 'コーチ', '監督', '先生',
            'です', 'ます', 'した', 'する', 'ある', 'なる', 'いる', 'もの', 'こと',
            'とき', 'ところ', 'ため', 'はず', 'わけ', 'つもり', 'ほう', 'まま',
            '小学生', '中学生', '高校生', '大学生', '社会人', '子供', '大人',
            '今日', '明日', '昨日', '今年', '来年', '去年', '最近', '今度',
            '一番', '二番', '三番', '最初', '最後', '全部', 'みんな', 'だれ',
            'なに', 'どこ', 'いつ', 'どう', 'なぜ', 'どの', 'その', 'この', 'あの'
        }

        for name in names:
            # 除外チェック
            if name in exclude_words:
                continue

            # 長さチェック
            if len(name) < 2 or len(name) > 5:
                continue

            # ひらがな・カタカナのみは除外（人名は通常漢字を含む）
            if all('ぁ' <= c <= 'ん' or 'ァ' <= c <= 'ン' for c in name):
                continue

            # 数字や記号が含まれている場合は除外
            if any(c.isdigit() or not c.isalnum() for c in name if c not in 'ぁ-んァ-ン一-龯'):
                continue

            # 文脈での使用回数をチェック
            usage_count = sum(1 for content, _, _ in conversations if name in (content or ''))

            if usage_count >= 1:  # 1回以上使用されている
                filtered_names.add(name)
                print(f"   ✅ 候補採用: '{name}' (使用回数: {usage_count})")

        print(f"\n📊 フィルタリング後の名前候補: {len(filtered_names)} 個")
        return filtered_names

    def generate_learning_data(self, conversations: List[tuple]):
        """学習データ生成"""
        print(f"\n📚 学習データ生成")
        print("-" * 20)

        # より詳細な分析
        learning_data = {
            'conversation_analysis': [],
            'name_contexts': {},
            'softball_indicators': [],
            'potential_players': []
        }

        # 各会話の詳細分析
        for i, (content, metadata, timestamp) in enumerate(conversations[:20]):  # 最初の20件を詳細分析
            text = content or ''

            analysis = {
                'id': i,
                'content': text,
                'timestamp': timestamp,
                'contains_softball_terms': [],
                'potential_names': [],
                'context_type': 'unknown'
            }

            # ソフトボール関連用語の検出
            softball_terms = ['ソフトボール', 'ソフト', '投手', 'ピッチャー', '選手', 'チーム', '試合', '練習', 'コーチ', '監督']
            for term in softball_terms:
                if term in text:
                    analysis['contains_softball_terms'].append(term)

            # 潜在的な名前の検出
            name_patterns = [r'([一-龯]{2,4})\s*[さ君ちゃん選手がはもので]']
            for pattern in name_patterns:
                matches = re.findall(pattern, text)
                analysis['potential_names'].extend(matches)

            # コンテキストタイプの判定
            if any(term in text for term in ['ソフトボール', 'ソフト']):
                if any(term in text for term in ['選手', '投手', 'チーム']):
                    analysis['context_type'] = 'softball_player_related'
                else:
                    analysis['context_type'] = 'softball_general'

            learning_data['conversation_analysis'].append(analysis)

        # 学習データ保存
        output_path = 'softball_detailed_analysis.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(learning_data, f, ensure_ascii=False, indent=2)

        print(f"✅ 詳細分析データ保存: {output_path}")

        # サマリー表示
        softball_related_count = sum(1 for analysis in learning_data['conversation_analysis']
                                   if analysis['context_type'].startswith('softball'))

        all_potential_names = set()
        for analysis in learning_data['conversation_analysis']:
            all_potential_names.update(analysis['potential_names'])

        print(f"📊 詳細分析結果:")
        print(f"   ソフトボール関連会話: {softball_related_count} 件")
        print(f"   潜在的名前候補: {len(all_potential_names)} 個")

        if all_potential_names:
            print(f"   候補例: {', '.join(list(all_potential_names)[:10])}")

    def create_enhanced_softball_templates(self, potential_names: Set[str]) -> Dict[str, str]:
        """拡張ソフトボールテンプレート作成"""
        print(f"\n📝 拡張ソフトボールテンプレート作成")
        print("-" * 30)

        templates = {}

        # 一般的なソフトボール関連テンプレート
        general_templates = {
            'ソフトボール': '⚾ ソフトボールについてお答えします。選手、ルール、戦術など、どのようなことをお知りになりたいですか？',
            'ソフトボール選手': '🥎 ソフトボール選手についてご案内します。どの選手や、どのような情報をお聞きになりたいですか？',
            'ソフトボールチーム': '👥 ソフトボールチームについてお話しします。どのチームについてお知りになりたいですか？',
            'ソフトボール試合': '🏟️ ソフトボールの試合についてご案内します。どの試合や大会についてお聞きになりたいですか？',
            'ソフトボール練習': '🏃 ソフトボールの練習についてお答えします。練習方法や上達のコツについてお聞きください。',
            'ソフトボールルール': '📋 ソフトボールのルールについて説明します。どのルールについて詳しく知りたいですか？',
            'ソフトボール用具': '🥎 ソフトボール用具についてご案内します。バット、グローブ、ボールなど、どの用具についてお聞きになりたいですか？'
        }

        templates.update(general_templates)

        # 潜在的選手名のテンプレート
        for name in potential_names:
            if len(name) >= 2:
                templates[f'{name}選手'] = f'{name}選手についてお話しします。どのようなことをお知りになりたいですか？'
                templates[f'{name}について'] = f'{name}についてご案内します。ソフトボールに関することでしたらお聞きください。'

        print(f"✅ 作成テンプレート数: {len(templates)}")
        return templates

def main():
    """メイン処理"""
    print("🥎 詳細ソフトボール分析システム")
    print(f"📅 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # データベースパス
    db_path = os.path.join('..', 'db', 'conversation_history.db')

    if not os.path.exists(db_path):
        print(f"❌ データベースが見つかりません: {db_path}")
        return

    # 詳細分析システム
    analyzer = DetailedSoftballAnalysis(db_path)

    # 1. 詳細分析実行
    conversations = analyzer.analyze_softball_conversations_detail()

    if not conversations:
        print("❌ 詳細分析に失敗しました")
        return

    # 2. 名前パターン分析
    potential_names = analyzer.analyze_name_patterns(conversations)

    # 3. 拡張テンプレート作成
    templates = analyzer.create_enhanced_softball_templates(potential_names)

    # 4. テンプレート保存
    templates_path = 'enhanced_softball_templates.json'
    with open(templates_path, 'w', encoding='utf-8') as f:
        json.dump(templates, f, ensure_ascii=False, indent=2)

    print(f"\n💾 拡張テンプレート保存: {templates_path}")

    # 5. 最終サマリー
    print(f"\n📊 詳細分析最終結果")
    print("-" * 40)
    print(f"   🔍 分析した会話数: {len(conversations)}")
    print(f"   👤 潜在的選手名候補: {len(potential_names)}")
    print(f"   📝 作成テンプレート: {len(templates)}")

    if potential_names:
        print(f"\n🆕 発見された名前候補:")
        for name in sorted(potential_names):
            print(f"      🔍 {name}")

    print(f"\n🎉 詳細ソフトボール分析完了！")

if __name__ == "__main__":
    main()
