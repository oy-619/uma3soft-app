#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
実際のChromaDBデータを使ったリマインダーテスト
実際のノートデータでリマインダー生成をテスト
"""

import os
import sys
import json
from datetime import datetime, timedelta

# プロジェクトルートを追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.reminder_schedule import create_flex_reminder_message, load_chromadb, extract_notes_from_yesterday, extract_notes_from_date

def test_real_chromadb_reminders():
    """実際のChromaDBデータを使ったリマインダーテスト"""

    print("=" * 70)
    print("🔍 実際のChromaDBデータによるリマインダーテスト")
    print("=" * 70)

    try:
        # ChromaDBを読み込み
        print("📂 ChromaDBを読み込み中...")
        vectorstore = load_chromadb()

        if not vectorstore:
            print("❌ ChromaDBの読み込みに失敗")
            return

        print("✅ ChromaDB読み込み成功")

        # 実際のノートデータを取得
        print("\n📋 実際のノートデータを取得中...")

        # 昨日から明日までの期間で検索
        target_dates = [
            datetime.now() - timedelta(days=1),  # 昨日
            datetime.now(),                      # 今日
            datetime.now() + timedelta(days=1),  # 明日
            datetime.now() + timedelta(days=2),  # 明後日
        ]

        all_notes = []
        for target_date in target_dates:
            try:
                notes = extract_notes_from_date(vectorstore, target_date)
                if notes:
                    all_notes.extend(notes)
                    print(f"   📅 {target_date.strftime('%Y-%m-%d')}: {len(notes)}件のノート発見")
            except Exception as e:
                print(f"   ❌ {target_date.strftime('%Y-%m-%d')}: エラー {e}")

        if not all_notes:
            print("⚠️ 実際のノートデータが見つかりません。サンプルデータでテストします。")

            # サンプルデータでテスト
            sample_notes = [
                {
                    "content": """【練習試合のお知らせ】
場所：東京ドーム
時間：14:00開始
持ち物：ユニフォーム、スパイク
注意：雨天中止""",
                    "date": datetime.now() + timedelta(days=1),
                    "is_input_deadline": False,
                    "days_until": 1
                }
            ]
            all_notes = sample_notes

        print(f"\n🎯 テスト対象ノート数: {len(all_notes)}")

        # 各ノートでリマインダー生成をテスト
        for i, note in enumerate(all_notes[:3], 1):  # 最大3件までテスト
            print(f"\n📋 ノート {i}: リマインダー生成テスト")
            print("-" * 50)

            # ノート内容を表示
            content_preview = note['content'][:100] + "..." if len(note['content']) > 100 else note['content']
            print(f"📝 内容: {content_preview}")

            try:
                # リマインダーメッセージを生成
                flex_message = create_flex_reminder_message(note)

                # 会場名と天候情報の確認
                message_json = json.dumps(flex_message, ensure_ascii=False)

                # 会場名検索
                venue_keywords = ["東京ドーム", "神宮球場", "横浜スタジアム", "甲子園", "球場", "グラウンド", "会場"]
                found_venues = [kw for kw in venue_keywords if kw in message_json]

                # 天候情報検索
                weather_keywords = ["天気", "気温", "湿度", "風速", "℃", "天候予報"]
                found_weather = [kw for kw in weather_keywords if kw in message_json]

                print(f"✅ リマインダー生成成功")
                print(f"   📏 サイズ: {len(message_json):,} bytes")
                print(f"   🏟️ 会場情報: {', '.join(found_venues) if found_venues else '❌ なし'}")
                print(f"   🌤️ 天候情報: {', '.join(found_weather) if found_weather else '❌ なし'}")

                # 問題がある場合の詳細診断
                if not found_venues:
                    print(f"\n🔍 会場情報なしの詳細診断:")
                    print(f"   📝 元のノート内容:")
                    for line in note['content'].split('\n'):
                        if line.strip():
                            print(f"      {line}")

                    # 場所抽出パターンテスト
                    import re
                    location_patterns = [
                        r'場所[：:]\s*([^\n]+)',
                        r'会場[：:]\s*([^\n]+)',
                        r'【大会会場】\s*([^\n]+)',
                        r'開催地[：:]\s*([^\n]+)',
                    ]

                    for pattern in location_patterns:
                        match = re.search(pattern, note['content'])
                        if match:
                            print(f"   📍 パターン'{pattern}'で抽出: {match.group(1)}")
                            break
                    else:
                        print(f"   ❌ どのパターンでも場所を抽出できませんでした")

                if not found_weather:
                    print(f"\n🔍 天候情報なしの詳細診断:")
                    print(f"   ⚠️ OpenWeatherMap APIエラーの可能性")
                    print(f"   💡 天候情報取得プロセスを確認してください")

                # 結果をファイルに保存
                output_file = f"real_chromadb_reminder_{i}.json"
                output_path = os.path.join(project_root, "tests", output_file)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(flex_message, f, ensure_ascii=False, indent=2)

                print(f"   💾 保存: {output_file}")

            except Exception as e:
                print(f"❌ リマインダー生成エラー: {e}")
                import traceback
                traceback.print_exc()

        print("\n" + "=" * 70)
        print("🎯 実際のChromaDBデータテスト完了")
        print("=" * 70)

    except Exception as e:
        print(f"❌ テスト全体でエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_chromadb_reminders()
