#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
リマインダーの会場名と天候情報表示問題の診断テスト
実際のリマインダー生成プロセスを詳細に検証
"""

import os
import sys
import json
from datetime import datetime, timedelta

# プロジェクトルートを追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.reminder_schedule import create_flex_reminder_message

def diagnose_reminder_venue_weather():
    """リマインダーの会場名と天候情報表示問題を診断"""

    print("=" * 70)
    print("🔍 リマインダー会場名・天候情報表示 診断テスト")
    print("=" * 70)

    # 実際のリマインダーデータに近いテストケース
    test_cases = [
        {
            "name": "東京ドーム開催イベント",
            "note": {
                "content": """【野球大会のご案内】
場所：東京ドーム
時間：13:00〜17:00
持ち物：ユニフォーム、グローブ、スパイク
注意事項：雨天決行
集合場所：正面入口""",
                "date": datetime.now() + timedelta(days=1),
                "is_input_deadline": False,
                "days_until": 1
            }
        },
        {
            "name": "神宮球場開催イベント",
            "note": {
                "content": """【春季大会のお知らせ】
【大会会場】神宮球場
開始時間：10:00
持参物：水筒、タオル
備考：駐車場利用不可""",
                "date": datetime.now() + timedelta(days=2),
                "is_input_deadline": False,
                "days_until": 2
            }
        },
        {
            "name": "入力期限リマインダー",
            "note": {
                "content": """【参加申込み締切のご案内】
会場：横浜スタジアム
締切：本日23:59まで
提出書類：参加申込書、健康診断書
連絡先：事務局まで""",
                "date": datetime.now(),
                "is_input_deadline": True,
                "days_until": 0
            }
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 テストケース {i}: {test_case['name']}")
        print("-" * 50)

        try:
            # リマインダーメッセージを生成
            flex_message = create_flex_reminder_message(test_case['note'])

            # 生成されたメッセージを詳細分析
            message_json = json.dumps(flex_message, ensure_ascii=False, indent=2)
            message_size = len(message_json)

            print(f"✅ メッセージ生成成功")
            print(f"   📏 サイズ: {message_size:,} bytes")
            print(f"   📄 Alt Text: {flex_message.get('altText', 'なし')}")

            # 会場名の検索
            venue_found = []
            if "東京ドーム" in message_json:
                venue_found.append("東京ドーム")
            if "神宮球場" in message_json:
                venue_found.append("神宮球場")
            if "横浜スタジアム" in message_json:
                venue_found.append("横浜スタジアム")

            # 天候情報の検索
            weather_keywords = ["天気", "気温", "湿度", "風速", "天候", "℃"]
            weather_found = []
            for keyword in weather_keywords:
                if keyword in message_json:
                    weather_found.append(keyword)

            # 診断結果
            print(f"\n🏟️ 会場名検出:")
            if venue_found:
                print(f"   ✅ 検出: {', '.join(venue_found)}")
            else:
                print(f"   ❌ 会場名が見つかりません")

            print(f"\n🌤️ 天候情報検出:")
            if weather_found:
                print(f"   ✅ 検出: {', '.join(weather_found)}")
            else:
                print(f"   ❌ 天候情報が見つかりません")

            # メッセージ構造の詳細確認
            if flex_message.get("type") == "flex" and "contents" in flex_message:
                contents = flex_message["contents"]
                if "body" in contents and "contents" in contents["body"]:
                    body_sections = contents["body"]["contents"]

                    # セクション別確認
                    venue_section_found = False
                    weather_section_found = False

                    for section in body_sections:
                        if isinstance(section, dict) and section.get("type") == "text":
                            text = section.get("text", "")
                            if "会場" in text:
                                venue_section_found = True
                            if "天候" in text:
                                weather_section_found = True

                    print(f"\n📊 セクション構造:")
                    print(f"   - 総セクション数: {len(body_sections)}")
                    print(f"   - 会場セクション: {'✅' if venue_section_found else '❌'}")
                    print(f"   - 天候セクション: {'✅' if weather_section_found else '❌'}")

            # 問題がある場合の詳細出力
            if not venue_found or not weather_found:
                print(f"\n🔍 問題診断:")

                # 元のノート内容から場所抽出テスト
                content = test_case['note']['content']
                location_patterns = [
                    r'場所[：:]\s*([^\n]+)',
                    r'会場[：:]\s*([^\n]+)',
                    r'【大会会場】\s*([^\n]+)',
                    r'開催地[：:]\s*([^\n]+)',
                ]

                extracted_location = None
                for pattern in location_patterns:
                    import re
                    match = re.search(pattern, content)
                    if match:
                        extracted_location = match.group(1).strip()
                        print(f"   📍 抽出された場所: {extracted_location}")
                        break

                if not extracted_location:
                    print(f"   ❌ 場所情報の抽出に失敗")
                    print(f"   📝 元のノート内容:")
                    for line in content.split('\n'):
                        if line.strip():
                            print(f"      {line}")

            # 結果をファイルに保存
            output_file = f"diagnostic_reminder_{i}.json"
            output_path = os.path.join(project_root, "tests", output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(flex_message, f, ensure_ascii=False, indent=2)

            print(f"\n💾 結果保存: {output_file}")

        except Exception as e:
            print(f"❌ テストケース {i} でエラー: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 70)
    print("🎯 診断完了 - 問題点の特定")
    print("=" * 70)

    print("\n📝 確認項目:")
    print("1. 会場名がメッセージに含まれているか")
    print("2. 天候情報がメッセージに含まれているか")
    print("3. セクション構造が正しく生成されているか")
    print("4. 場所抽出パターンが正常に動作しているか")

if __name__ == "__main__":
    diagnose_reminder_venue_weather()
