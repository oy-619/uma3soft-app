"""
28名選手情報統合テスト
新規16名 + 既存13名 + 翔平昇格の動作確認
"""

import sys
import os

# uma3.pyのパスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from uma3 import player_info_handler

def test_28_players_integration():
    """28名選手情報統合テスト"""
    print("🚀 28名選手情報統合テスト")
    print("=" * 50)

    # システム状態確認
    print(f"📊 システム状態:")
    print(f"   ✅ 確認済み選手: {len(player_info_handler.confirmed_players)}名")
    print(f"   🔍 候補選手: {len(player_info_handler.potential_players)}名")
    print(f"   🏆 総選手数: {player_info_handler.total_players}名")
    print()

    # 確認済み選手リスト表示
    print(f"📝 確認済み選手一覧:")
    for i, player in enumerate(player_info_handler.confirmed_players, 1):
        print(f"   {i:2d}. {player}")
    print()

    # テストクエリ実行
    test_queries = [
        # 既存13名のテスト
        "陸功選手について教えて",
        "湊について",
        "穂美選手は？",

        # 新規追加選手のテスト
        "尚真選手について",
        "柚希について教えて",
        "心翔選手は？",
        "広起について",
        "想真選手の情報",
        "奏について",
        "英汰選手は？",
        "聡太について教えて",
        "暖大選手について",
        "悠琉について",
        "陽選手は？",
        "美玖里について",
        "優選手について",
        "勘太について教えて",

        # 翔平の特別テスト（昇格確認）
        "翔平選手について教えて",
        "翔平について",

        # チーム全体のテスト
        "選手一覧を教えて",
        "馬三ソフトには何人いる？",
        "チームメンバーは？",
        "新しい更新について教えて"
    ]

    print(f"🧪 テストクエリ実行:")
    print("=" * 30)

    for i, query in enumerate(test_queries, 1):
        print(f"\n{i:2d}. クエリ: 「{query}」")

        response = player_info_handler.handle_message(query)

        if response:
            print(f"    💬 応答: {response}")
        else:
            print(f"    ❌ 応答: なし")

    print(f"\n🎊 統合テスト完了!")
    print("=" * 30)

    # 統計情報
    successful_tests = 0
    total_tests = len(test_queries)

    for query in test_queries:
        if player_info_handler.handle_message(query):
            successful_tests += 1

    success_rate = (successful_tests / total_tests) * 100

    print(f"📊 テスト結果統計:")
    print(f"   ✅ 成功: {successful_tests}/{total_tests} クエリ")
    print(f"   📈 成功率: {success_rate:.1f}%")
    print(f"   🏆 選手認識: {len(player_info_handler.confirmed_players)}名")

    # 新規追加選手の認識確認
    new_players = ["尚真", "柚希", "心翔", "広起", "想真", "奏", "英汰", "聡太", "暖大", "悠琉", "陽", "美玖里", "優", "勘太"]
    recognized_new_players = 0

    for player in new_players:
        if player in player_info_handler.confirmed_players:
            recognized_new_players += 1

    print(f"   🆕 新規選手認識: {recognized_new_players}/{len(new_players)}名")

    # 翔平の昇格確認
    if "翔平" in player_info_handler.confirmed_players and "翔平" not in player_info_handler.potential_players:
        print(f"   ⬆️ 翔平昇格: ✅ 候補→確認済み")
    else:
        print(f"   ⬆️ 翔平昇格: ❌ 未完了")

    print(f"\n🌟 28名選手情報統合システム動作確認完了！")

if __name__ == "__main__":
    test_28_players_integration()
