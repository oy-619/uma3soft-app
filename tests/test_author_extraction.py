#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投稿者情報抽出機能のテスト
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from reminder_flex_customizer import ReminderFlexCustomizer

def test_author_extraction():
    """投稿者情報の抽出テスト"""
    print("=" * 80)
    print("🔍 投稿者情報抽出テスト")
    print("=" * 80)

    customizer = ReminderFlexCustomizer()

    # テストケース
    test_cases = [
        {
            "name": "連絡先パターン（太郎）",
            "content": """葛飾区柴又少年野球大会
場所：葛飾区柴又球場第一グラウンド
集合時間：17:45（試合開始18:00）
持ち物：グローブ、バット、飲み物、タオル、着替え
注意事項：雨天の場合は翌日同時刻に順延
参加費：500円（当日徴収）
駐車場：利用可能（1日300円）
連絡先：柴又太郎""",
            "expected": "柴又太郎"
        },
        {
            "name": "担当者パターン（花子）",
            "content": """横浜市青葉区春季大会
会場：横浜市青葉区総合運動場野球場
時間：午後2時開始
持参：ユニフォーム、スパイク
費用：1000円
担当：青葉花子""",
            "expected": "青葉花子"
        },
        {
            "name": "問い合わせパターン（次郎）",
            "content": """さいたま市大宮区秋季リーグ戦
開催地：さいたま市大宮区営球場A面
集合：午前10時30分
試合開始：午前11時
持ち物：ユニフォーム一式、グローブ、バット
雨天：中止（延期なし）
問い合わせ：大宮次郎""",
            "expected": "大宮次郎"
        },
        {
            "name": "主催者パターン（田中）",
            "content": """春の親善試合
場所：荒川河川敷野球場
日時：3月15日（土）午前9時開始
主催：田中一郎
参加費：無料""",
            "expected": "田中一郎"
        },
        {
            "name": "投稿者パターン（佐藤）",
            "content": """夏季合宿のお知らせ
期間：8月10日-12日
場所：軽井沢合宿所
投稿者：佐藤美子""",
            "expected": "佐藤美子"
        },
        {
            "name": "名前がない場合",
            "content": """野球大会のお知らせ
場所：東京ドーム
時間：午後1時開始
参加費：2000円""",
            "expected": "投稿者"
        },
        {
            "name": "電話番号混在ケース",
            "content": """秋季大会
場所：神宮球場
連絡先：山田太郎 090-1234-5678""",
            "expected": "山田太郎"
        },
        {
            "name": "メールアドレス混在ケース",
            "content": """練習試合
場所：駒沢球場
問い合わせ：鈴木花子 suzuki@example.com""",
            "expected": "鈴木花子"
        }
    ]

    # テスト実行
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 テスト {i}: {test_case['name']}")
        print("-" * 50)

        # 投稿者情報抽出
        extracted_author = customizer._extract_author_info(test_case["content"])

        # 結果表示
        print(f"📝 入力内容: {test_case['content'][:100]}...")
        print(f"🎯 期待値: {test_case['expected']}")
        print(f"📤 抽出結果: {extracted_author}")

        # 判定
        if extracted_author == test_case["expected"]:
            print("✅ 成功")
        else:
            print("❌ 失敗")

    print("\n" + "=" * 80)
    print("🎉 投稿者情報抽出テスト完了")
    print("=" * 80)

if __name__ == "__main__":
    test_author_extraction()
