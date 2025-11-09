#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime, timedelta

def test_complete_reminder_system():
    """完全なリマインダーシステムのテスト"""
    print("=" * 70)
    print("🎯 完全リマインダーシステム統合テスト")
    print("主要目的：調整さんの確認と入力依頼")
    print("付属情報：天候情報（簡潔表示）")
    print("=" * 70)

    try:
        # モジュールのインポートテスト
        from weather_flex_template import WeatherFlexTemplate
        from reminder_flex_customizer import ReminderFlexCustomizer

        print("✅ 必要モジュールのインポート成功")

        # システム初期化
        weather_template = WeatherFlexTemplate()
        flex_customizer = ReminderFlexCustomizer()

        print("✅ システム初期化成功")

        # テストデータ
        test_scenarios = [
            {
                "name": "緊急入力期限リマインダー（明日期限）",
                "note": {
                    "content": """【野球大会参加確認】
場所：平和島公園野球場
日時：11月2日(日) 9:00集合
持ち物：グローブ、スパイク、飲み物
参加費：500円
注意：雨天の場合は中止""",
                    "date": datetime.now() + timedelta(days=2),
                    "days_until": 1,  # 明日期限
                    "is_input_deadline": True
                },
                "location": "東京都大田区"
            },
            {
                "name": "イベント開催日リマインダー（明日開催）",
                "note": {
                    "content": """【練習試合】
会場：萩中公園野球場
時間：13:00集合、13:30開始
相手チーム：XX野球クラブ
連絡：天候不良時は当日朝に連絡""",
                    "date": datetime.now() + timedelta(days=1),
                    "days_until": 1,  # 明日開催
                    "is_input_deadline": False
                },
                "location": "東京都大田区"
            },
            {
                "name": "事前入力期限リマインダー（3日後期限）",
                "note": {
                    "content": """【月例大会エントリー】
場所：東京ドーム
日時：11月5日(火) 10:00～
エントリー費：1000円
締切：11月2日(日)まで""",
                    "date": datetime.now() + timedelta(days=5),
                    "days_until": 3,  # 3日後期限
                    "is_input_deadline": True
                },
                "location": "東京都"
            }
        ]

        print(f"\n📊 {len(test_scenarios)}つのシナリオでテスト開始:\n")

        results = []

        for i, scenario in enumerate(test_scenarios, 1):
            print(f"🔍 シナリオ {i}: {scenario['name']}")

            try:
                note = scenario["note"]
                location = scenario["location"]

                # 天気Flex Messageを生成
                if note["days_until"] == 0:
                    base_flex = weather_template.create_current_weather_flex(location)
                else:
                    target_date = note["date"].strftime("%Y-%m-%d")
                    base_flex = weather_template.create_forecast_flex(location, target_date)

                # リマインダー専用にカスタマイズ
                reminder_flex = flex_customizer.customize_weather_flex_for_reminder(base_flex, note)

                # 結果を保存
                filename = f"reminder_test_{i}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(reminder_flex, f, ensure_ascii=False, indent=2)

                # 結果確認
                header_text = reminder_flex['contents']['header']['contents'][0]['text']
                alt_text = reminder_flex['altText']
                has_buttons = 'footer' in reminder_flex['contents']

                print(f"   ✅ 生成成功: {filename}")
                print(f"   📝 ヘッダー: {header_text}")
                print(f"   📧 altText: {alt_text[:50]}...")
                print(f"   🔘 ボタン: {'あり' if has_buttons else 'なし'}")
                print()

                results.append({
                    "scenario": scenario["name"],
                    "success": True,
                    "filename": filename,
                    "has_buttons": has_buttons
                })

            except Exception as e:
                print(f"   ❌ エラー: {e}")
                results.append({
                    "scenario": scenario["name"],
                    "success": False,
                    "error": str(e)
                })

        # 結果サマリー
        print("=" * 70)
        print("📋 テスト結果サマリー:")
        print("=" * 70)

        success_count = sum(1 for r in results if r["success"])
        total_count = len(results)

        print(f"✅ 成功: {success_count}/{total_count}")

        for result in results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['scenario']}")
            if result["success"]:
                print(f"   📁 ファイル: {result['filename']}")
                print(f"   🔘 調整さんボタン: {'設置済み' if result['has_buttons'] else 'なし'}")

        print("\n🎯 システム特徴:")
        print("• 主要コンテンツ：調整さんの確認と入力依頼")
        print("• 付属情報：天候情報（簡潔に表示）")
        print("• ユーザビリティ：見やすい整形とアクション誘導")
        print("• LINE API準拠：ボタン付きFlex Message（リマインダー用）")

        print("\n" + "=" * 70)
        print("🎉 完全リマインダーシステム統合テスト完了！")
        print("=" * 70)

        return success_count == total_count

    except ImportError as e:
        print(f"❌ モジュールインポートエラー: {e}")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_complete_reminder_system()
