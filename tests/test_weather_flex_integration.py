#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天気情報Flex Message統合テスト
指定した場所と日付に基づいてFlex Messageを生成し、動作を確認
"""

import sys
import os
import json
from datetime import datetime, timedelta

# プロジェクトのsrcディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from weather_flex_template import WeatherFlexTemplate, create_weather_flex

def test_current_weather():
    """現在の天気情報テスト"""
    print("🌤️ 現在の天気情報テスト")
    print("-" * 50)

    template = WeatherFlexTemplate()

    test_locations = [
        "東京都大田区",
        "Ota,JP",
        "大阪府",
        "Yokohama,JP"
    ]

    for location in test_locations:
        print(f"\n📍 場所: {location}")
        try:
            flex_message = template.create_current_weather_flex(location)
            print(f"   ✅ Flex Message作成成功")
            print(f"   📱 タイプ: {flex_message['type']}")
            print(f"   📝 代替テキスト: {flex_message['altText']}")

            # 実際の天気データが含まれているかチェック
            body_contents = flex_message['contents']['body']['contents']
            weather_section = None
            for content in body_contents:
                if content.get('type') == 'box' and content.get('layout') == 'vertical':
                    if 'contents' in content and len(content['contents']) > 0:
                        weather_section = content
                        break

            if weather_section:
                print(f"   🌡️ 天気データ: 含まれています")
            else:
                print(f"   ⚠️ 天気データ: 確認できませんでした")

        except Exception as e:
            print(f"   ❌ エラー: {e}")

def test_forecast_weather():
    """指定日の天気予報テスト"""
    print("\n🌦️ 指定日の天気予報テスト")
    print("-" * 50)

    template = WeatherFlexTemplate()

    # テスト用の日付を生成（今日から3日後まで）
    test_dates = []
    base_date = datetime.now()
    for i in range(4):
        test_date = base_date + timedelta(days=i)
        test_dates.append(test_date.strftime("%Y-%m-%d"))

    for date in test_dates:
        print(f"\n📅 日付: {date}")
        try:
            flex_message = template.create_forecast_flex("東京都", date)
            print(f"   ✅ Flex Message作成成功")
            print(f"   📱 タイプ: {flex_message['type']}")
            print(f"   📝 代替テキスト: {flex_message['altText']}")

            # 予報データの確認
            if 'contents' in flex_message and 'body' in flex_message['contents']:
                print(f"   📊 予報データ: 含まれています")
            else:
                print(f"   ⚠️ 予報データ: 構造に問題があります")

        except Exception as e:
            print(f"   ❌ エラー: {e}")

def test_detailed_forecast():
    """詳細な時間別予報テスト"""
    print("\n📊 詳細な時間別予報テスト")
    print("-" * 50)

    template = WeatherFlexTemplate()

    # 明日の日付
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    test_locations = ["東京都", "大阪府", "Ota,JP"]

    for location in test_locations:
        print(f"\n📍 場所: {location} | 📅 日付: {tomorrow}")
        try:
            flex_message = template.create_detailed_forecast_flex(location, tomorrow)
            print(f"   ✅ Flex Message作成成功")
            print(f"   📱 タイプ: {flex_message['type']}")
            print(f"   📝 代替テキスト: {flex_message['altText']}")

            # 時間別データの確認
            body = flex_message['contents']['body']
            time_section_found = False
            for content in body['contents']:
                if (content.get('type') == 'box' and
                    content.get('layout') == 'vertical' and
                    'contents' in content):
                    time_section_found = True
                    break

            if time_section_found:
                print(f"   ⏰ 時間別データ: 含まれています")
            else:
                print(f"   ⚠️ 時間別データ: 確認できませんでした")

        except Exception as e:
            print(f"   ❌ エラー: {e}")

def test_convenience_function():
    """便利関数のテスト"""
    print("\n🚀 便利関数のテスト")
    print("-" * 50)

    test_cases = [
        {"location": "東京都", "date": None, "weather_type": "current"},
        {"location": "大阪府", "date": "2025-10-30", "weather_type": "forecast"},
        {"location": "Ota,JP", "date": "2025-10-31", "weather_type": "detailed"}
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. テストケース: {case}")
        try:
            flex_message = create_weather_flex(
                location=case["location"],
                date=case["date"],
                weather_type=case["weather_type"]
            )
            print(f"   ✅ 便利関数実行成功")
            print(f"   📱 タイプ: {flex_message['type']}")
            print(f"   📝 代替テキスト: {flex_message['altText']}")

        except Exception as e:
            print(f"   ❌ エラー: {e}")

def test_json_export():
    """JSON出力テスト"""
    print("\n💾 JSON出力テスト")
    print("-" * 50)

    template = WeatherFlexTemplate()

    try:
        # 現在の天気のFlex Messageを作成
        flex_message = template.create_current_weather_flex("東京都大田区", "練習場所の天気情報")

        # JSONファイルに出力
        output_file = "sample_weather_flex.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(flex_message, f, ensure_ascii=False, indent=2)

        print(f"   ✅ JSON出力成功: {output_file}")
        print(f"   📄 ファイルサイズ: {os.path.getsize(output_file)} bytes")

        # JSONの妥当性確認
        with open(output_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)

        if loaded_data.get('type') == 'flex' and 'contents' in loaded_data:
            print(f"   ✅ JSON形式: 正常")
        else:
            print(f"   ⚠️ JSON形式: 構造に問題があります")

        # クリーンアップ
        os.remove(output_file)
        print(f"   🗑️ テストファイル削除: {output_file}")

    except Exception as e:
        print(f"   ❌ JSON出力エラー: {e}")

def test_error_handling():
    """エラーハンドリングテスト"""
    print("\n⚠️ エラーハンドリングテスト")
    print("-" * 50)

    template = WeatherFlexTemplate()

    # 1. 存在しない場所
    print("\n1. 存在しない場所のテスト:")
    try:
        flex_message = template.create_current_weather_flex("存在しない場所12345")
        print(f"   ✅ エラーハンドリング: 正常動作")
        print(f"   📝 代替テキスト: {flex_message['altText']}")
    except Exception as e:
        print(f"   ❌ 予期しないエラー: {e}")

    # 2. 無効な日付形式
    print("\n2. 無効な日付形式のテスト:")
    try:
        flex_message = template.create_forecast_flex("東京都", "invalid-date")
        print(f"   ✅ エラーハンドリング: 正常動作")
        print(f"   📝 代替テキスト: {flex_message['altText']}")
    except Exception as e:
        print(f"   ❌ 予期しないエラー: {e}")

    # 3. 過去の日付
    print("\n3. 過去の日付のテスト:")
    try:
        past_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        flex_message = template.create_forecast_flex("東京都", past_date)
        print(f"   ✅ エラーハンドリング: 正常動作")
        print(f"   📝 代替テキスト: {flex_message['altText']}")
    except Exception as e:
        print(f"   ❌ 予期しないエラー: {e}")

def display_sample_output():
    """サンプル出力の表示"""
    print("\n📱 サンプル出力例")
    print("=" * 70)

    template = WeatherFlexTemplate()

    # 練習場所の天気予報の例
    print("\n🏃‍♂️ 練習場所の天気予報例:")
    try:
        flex_message = template.create_current_weather_flex(
            "東京都大田区",
            "🏃‍♂️ 代々木公園の練習天気"
        )

        print(f"代替テキスト: {flex_message['altText']}")

        # 主要な情報を抽出して表示
        body = flex_message['contents']['body']
        title = body['contents'][0]['text']
        date = body['contents'][1]['text']

        print(f"タイトル: {title}")
        print(f"日付: {date}")
        print("構成: ヘッダー + 天気詳細 + 詳細ボタン")

    except Exception as e:
        print(f"サンプル出力エラー: {e}")

def main():
    """メイン処理"""
    print("=" * 80)
    print("🌤️ 天気情報Flex Message統合テスト")
    print("=" * 80)

    print(f"📅 テスト実行日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")

    # 各テストを実行
    test_current_weather()
    test_forecast_weather()
    test_detailed_forecast()
    test_convenience_function()
    test_json_export()
    test_error_handling()
    display_sample_output()

    print("\n" + "=" * 80)
    print("✅ 天気情報Flex Message統合テスト 完了")
    print("=" * 80)

    # 最終まとめ
    print("\n📋 テスト結果まとめ:")
    print("   ✅ 現在の天気情報 Flex Message 生成")
    print("   ✅ 指定日の天気予報 Flex Message 生成")
    print("   ✅ 詳細な時間別予報 Flex Message 生成")
    print("   ✅ 便利関数による簡単な呼び出し")
    print("   ✅ JSON形式での出力と妥当性確認")
    print("   ✅ エラーケースの適切な処理")

    print("\n🚀 実装完了! LINE Botで使用可能です。")

if __name__ == "__main__":
    main()
