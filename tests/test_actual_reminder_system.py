#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
実際のリマインダー関数を使った会場・天候情報表示テスト
"""

import os
import sys
import json
from datetime import datetime, timedelta

# プロジェクトルートを追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.reminder_schedule import get_reminders_for_tomorrow, get_next_day_reminders, create_flex_reminder_message

def test_actual_reminder_system():
    """実際のリマインダーシステムの会場・天候情報表示テスト"""

    print("=" * 70)
    print("🔍 実際のリマインダーシステム 会場・天候情報表示テスト")
    print("=" * 70)

    try:
        # 明日のリマインダーを取得
        print("📅 明日のリマインダーを取得中...")
        tomorrow_reminders = get_reminders_for_tomorrow()

        print(f"   📋 明日のリマインダー: {len(tomorrow_reminders)}件")

        # 翌日のリマインダーも取得
        print("📅 翌日のリマインダーを取得中...")
        next_day_reminders = get_next_day_reminders()

        print(f"   📋 翌日のリマインダー: {len(next_day_reminders)}件")

        # すべてのリマインダーを結合
        all_reminders = tomorrow_reminders + next_day_reminders

        if not all_reminders:
            print("⚠️ 実際のリマインダーデータが見つかりません。")
            print("📝 手動でサンプルデータを作成してテストします。")

            # サンプルリマインダー作成
            sample_reminder = {
                "content": """【定期練習のお知らせ】
場所：神宮球場
時間：9:00〜12:00
持ち物：グローブ、水筒
集合場所：球場正面入口
連絡先：090-1234-5678""",
                "date": datetime.now() + timedelta(days=1),
                "is_input_deadline": False,
                "days_until": 1
            }
            all_reminders = [sample_reminder]

        print(f"\n🎯 テスト対象リマインダー数: {len(all_reminders)}")

        # 各リマインダーでテスト
        for i, reminder in enumerate(all_reminders[:3], 1):  # 最大3件
            print(f"\n📋 リマインダー {i}: Flex Message生成テスト")
            print("-" * 50)

            # リマインダー内容の概要表示
            content_preview = reminder['content'][:80] + "..." if len(reminder['content']) > 80 else reminder['content']
            print(f"📝 内容概要: {content_preview}")

            try:
                # Flex Messageを生成
                flex_message = create_flex_reminder_message(reminder)

                if not flex_message:
                    print(f"❌ Flex Message生成失敗")
                    continue

                # JSON化して分析
                message_json = json.dumps(flex_message, ensure_ascii=False)
                message_size = len(message_json)

                print(f"✅ Flex Message生成成功")
                print(f"   📏 サイズ: {message_size:,} bytes")
                print(f"   📄 Alt Text: {flex_message.get('altText', 'なし')}")

                # 会場名の検出
                venue_patterns = [
                    "神宮球場", "東京ドーム", "横浜スタジアム", "甲子園球場",
                    "球場", "グラウンド", "会場", "ドーム", "スタジアム"
                ]

                found_venues = []
                for pattern in venue_patterns:
                    if pattern in message_json:
                        found_venues.append(pattern)

                # 天候情報の検出
                weather_patterns = [
                    "天気", "気温", "湿度", "風速", "℃", "天候予報",
                    "晴れ", "曇り", "雨", "雪", "weather"
                ]

                found_weather = []
                for pattern in weather_patterns:
                    if pattern in message_json:
                        found_weather.append(pattern)

                # 検出結果
                print(f"\n🏟️ 会場名検出結果:")
                if found_venues:
                    print(f"   ✅ 検出された会場: {', '.join(set(found_venues))}")
                else:
                    print(f"   ❌ 会場名が検出されませんでした")

                print(f"\n🌤️ 天候情報検出結果:")
                if found_weather:
                    print(f"   ✅ 検出された天候情報: {', '.join(set(found_weather))}")
                else:
                    print(f"   ❌ 天候情報が検出されませんでした")

                # 問題分析
                if not found_venues or not found_weather:
                    print(f"\n🔍 問題分析:")

                    if not found_venues:
                        print(f"   📍 会場名問題:")
                        print(f"      - 元のノート内容から場所情報が抽出できていない可能性")
                        print(f"      - 場所抽出パターンの見直しが必要かもしれません")

                        # 元のノート内容から場所を手動抽出
                        import re
                        location_patterns = [
                            r'場所[：:]\s*([^\n]+)',
                            r'会場[：:]\s*([^\n]+)',
                            r'【大会会場】\s*([^\n]+)',
                            r'集合場所[：:]\s*([^\n]+)',
                        ]

                        for pattern in location_patterns:
                            match = re.search(pattern, reminder['content'])
                            if match:
                                print(f"      ✅ パターン'{pattern}': {match.group(1)}")
                                break
                        else:
                            print(f"      ❌ 既知のパターンで場所を抽出できません")

                    if not found_weather:
                        print(f"   🌤️ 天候情報問題:")
                        print(f"      - OpenWeatherMap API接続エラーの可能性")
                        print(f"      - 場所情報の形式がAPI仕様に合わない可能性")
                        print(f"      - APIキーまたはネットワーク接続の問題")

                # JSONファイルに保存
                output_file = f"actual_reminder_test_{i}.json"
                output_path = os.path.join(project_root, "tests", output_file)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(flex_message, f, ensure_ascii=False, indent=2)

                print(f"\n💾 結果保存: {output_file}")

            except Exception as e:
                print(f"❌ リマインダー {i} でエラー: {e}")
                import traceback
                traceback.print_exc()

        print("\n" + "=" * 70)
        print("🎯 実際のリマインダーシステムテスト完了")
        print("=" * 70)

        print("\n📊 総合診断:")
        print("1. リマインダーデータの取得状況")
        print("2. Flex Message生成の成功率")
        print("3. 会場名表示の問題点")
        print("4. 天候情報表示の問題点")

    except Exception as e:
        print(f"❌ テスト全体でエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_actual_reminder_system()
