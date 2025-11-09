#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会場名抽出機能のテスト
"""

import sys
import os

# プロジェクトのパスを追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

def test_venue_extraction():
    """会場名抽出のテスト"""
    print("🏢 会場名抽出機能テスト")
    print("=" * 50)

    try:
        from enhanced_reminder_messages import EnhancedReminderMessageGenerator

        generator = EnhancedReminderMessageGenerator()

        # テストケース
        test_cases = [
            {
                "name": "標準的な会場指定（コロン）",
                "content": "[ノート] 11月3日(日) BBQイベント\n会場: 代々木公園バーベキュー広場\n集合時間: 11:00",
                "expected_venue": "代々木公園バーベキュー広場",
                "expected_location": "東京都"
            },
            {
                "name": "全角コロンでの会場指定",
                "content": "[ノート] 12月15日(日) 忘年会\n会場：新宿パークハイアット東京\n時間: 18:00",
                "expected_venue": "新宿パークハイアット東京",
                "expected_location": "東京都"
            },
            {
                "name": "場所キーワードでの指定",
                "content": "[ノート] 1月20日(月) 会議\n場所: 渋谷オフィスビル5階\n時間: 10:00",
                "expected_venue": "渋谷オフィスビル5階",
                "expected_location": "東京都"
            },
            {
                "name": "開催地キーワードでの指定",
                "content": "[ノート] 2月10日(土) セミナー\n開催地: 大阪城ホール\n参加費: 2000円",
                "expected_venue": "大阪城ホール",
                "expected_location": "大阪府"
            },
            {
                "name": "集合場所での指定",
                "content": "[ノート] 3月5日(日) ハイキング\n集合場所: 横浜駅西口\n持ち物: リュック",
                "expected_venue": "横浜駅西口",
                "expected_location": "神奈川県"
            },
            {
                "name": "英語のvenueキーワード",
                "content": "[NOTE] March 15th Concert\nvenue: Tokyo Dome\ntime: 19:00",
                "expected_venue": "Tokyo Dome",
                "expected_location": "東京都"
            },
            {
                "name": "直接検索（キーワードなし）",
                "content": "[ノート] 4月20日(木) 出張\n札幌での商談です\n交通費支給",
                "expected_venue": "札幌",
                "expected_location": "北海道"
            },
            {
                "name": "複数キーワード（最初を抽出）",
                "content": "[ノート] 5月1日(月) 会議\n会場: 新宿オフィス\n渋谷でも打ち合わせ予定",
                "expected_venue": "新宿オフィス",
                "expected_location": "東京都"
            },
            {
                "name": "会場情報なし",
                "content": "[ノート] 6月10日(土) 作業\nオンライン会議\n資料準備",
                "expected_venue": "",
                "expected_location": "東京都"  # デフォルト
            },
            {
                "name": "複雑な住所",
                "content": "[ノート] 7月15日(月) 訪問\n会場：千葉県千葉市中央区新町1-17 JPR千葉ビル\n駐車場あり",
                "expected_venue": "千葉県千葉市中央区新町1-17 JPR千葉ビル",
                "expected_location": "千葉県"
            }
        ]

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- テスト {i}: {test_case['name']} ---")
            print(f"📄 入力内容:")
            for line in test_case['content'].split('\\n'):
                print(f"    {line}")

            # 会場名抽出
            extracted_venue = generator._extract_venue_name(test_case['content'])
            expected_venue = test_case['expected_venue']

            print(f"\\n🏢 会場名抽出結果:")
            print(f"    期待値: '{expected_venue}'")
            print(f"    実際値: '{extracted_venue}'")

            if extracted_venue == expected_venue:
                print("    ✅ 会場名: 正解")
            else:
                print("    ❌ 会場名: 不一致")

            # 地域抽出
            extracted_location = generator._extract_location_from_event(test_case['content'])
            expected_location = test_case['expected_location']

            print(f"\\n📍 地域抽出結果:")
            print(f"    期待値: '{expected_location}'")
            print(f"    実際値: '{extracted_location}'")

            if extracted_location == expected_location:
                print("    ✅ 地域: 正解")
            else:
                print("    ❌ 地域: 不一致")

            # 総合評価
            venue_match = extracted_venue == expected_venue
            location_match = extracted_location == expected_location

            if venue_match and location_match:
                print("    🎯 総合: 完全一致 ✨")
            elif venue_match:
                print("    🎯 総合: 会場名のみ一致")
            elif location_match:
                print("    🎯 総合: 地域のみ一致")
            else:
                print("    🎯 総合: 両方不一致")

        print("\\n" + "=" * 50)
        print("📊 会場名抽出ロジックの詳細:")
        print("=" * 50)

        print("\\n🔍 **会場名抽出の仕組み:**")
        print("  1. キーワード検索:")
        print("     - '会場', '場所', '開催地', '集合場所'")
        print("     - 'venue', 'place' (英語対応)")
        print("\\n  2. 区切り文字での抽出:")
        print("     - ':' (半角コロン)")
        print("     - '：' (全角コロン)")
        print("\\n  3. 直接キーワード検索:")
        print("     - 代々木公園, 新宿, 渋谷, 池袋, 品川")
        print("     - 東京ドーム, 横浜, 大阪城, 京都, 名古屋, 福岡, 札幌")

        print("\\n🗺️ **地域抽出の仕組み:**")
        print("  1. 会場名→都道府県マッピング:")
        print("     - 代々木公園 → 東京都")
        print("     - 大阪 → 大阪府")
        print("     - 札幌 → 北海道")
        print("     - など...")
        print("\\n  2. デフォルト値: 東京都")

        print("\\n💡 **改善提案:**")
        print("  - より多くの会場キーワードの追加")
        print("  - 住所からの自動地域判定")
        print("  - 曖昧な表現への対応（例: 'あの場所'）")
        print("  - 複数会場の場合の優先順位設定")

    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")

if __name__ == "__main__":
    test_venue_extraction()
