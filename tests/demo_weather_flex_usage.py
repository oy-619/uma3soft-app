#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天気情報Flex Message実用デモ
リマインダーシステムと統合した実際の使用例
"""

import sys
import os
import json
from datetime import datetime, timedelta

# プロジェクトのsrcディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from weather_flex_template import WeatherFlexTemplate, create_weather_flex

def demo_practice_reminder():
    """練習予定リマインダーのデモ"""
    print("🏃‍♂️ 練習予定リマインダーデモ")
    print("=" * 60)

    # 明日の練習予定
    tomorrow = datetime.now() + timedelta(days=1)
    date_str = tomorrow.strftime("%Y-%m-%d")
    weekday = ["月", "火", "水", "木", "金", "土", "日"][tomorrow.weekday()]

    print(f"📅 練習予定: {tomorrow.strftime('%Y年%m月%d日')}（{weekday}）")
    print(f"📍 場所: 代々木公園")
    print(f"⏰ 時間: 19:00-21:00")

    # 天気情報付きFlex Message作成
    template = WeatherFlexTemplate()

    try:
        # 1. 練習当日の天気予報
        flex_message = template.create_forecast_flex(
            "東京都",
            date_str,
            f"🏃‍♂️ 明日の練習天気情報"
        )

        print(f"\n✅ 天気予報Flex Message作成成功")
        print(f"📱 代替テキスト: {flex_message['altText']}")

        # 2. 詳細な時間別予報も作成
        detailed_flex = template.create_detailed_forecast_flex("東京都", date_str)
        print(f"📊 詳細予報Flex Message作成成功")
        print(f"📱 代替テキスト: {detailed_flex['altText']}")

        # 実際のLINE Bot送信例（疑似コード）
        print(f"\n📲 LINE Bot送信例:")
        print(f"   1. テキストメッセージ: '明日の練習予定をお知らせします！'")
        print(f"   2. Flex Message: 天気予報カード")
        print(f"   3. テキストメッセージ: '参加可否の連絡をお願いします'")

        return flex_message, detailed_flex

    except Exception as e:
        print(f"❌ エラー: {e}")
        return None, None

def demo_event_notification():
    """イベント通知のデモ"""
    print("\n🎉 イベント通知デモ")
    print("=" * 60)

    # イベント情報
    event_date = datetime.now() + timedelta(days=3)
    date_str = event_date.strftime("%Y-%m-%d")

    print(f"🎪 イベント: 運動会")
    print(f"📅 日程: {event_date.strftime('%Y年%m月%d日')}")
    print(f"📍 場所: 大田区総合体育館")

    template = WeatherFlexTemplate()

    try:
        flex_message = template.create_forecast_flex(
            "大田区,JP",
            date_str,
            f"🎪 運動会当日の天気予報"
        )

        print(f"\n✅ イベント用天気予報作成成功")
        print(f"📱 代替テキスト: {flex_message['altText']}")

        return flex_message

    except Exception as e:
        print(f"❌ エラー: {e}")
        return None

def demo_daily_weather_notification():
    """毎日の天気通知デモ"""
    print("\n🌅 毎日の天気通知デモ")
    print("=" * 60)

    print(f"⏰ 毎朝7:00の定期通知")
    print(f"📍 対象地域: 東京都（ユーザーの居住地）")

    template = WeatherFlexTemplate()

    try:
        # 現在の天気
        current_flex = template.create_current_weather_flex(
            "東京都",
            "🌅 今日の天気情報"
        )

        # 今日の詳細予報
        today = datetime.now().strftime("%Y-%m-%d")
        today_forecast = template.create_detailed_forecast_flex("東京都", today)

        print(f"\n✅ 現在天気Flex Message作成成功")
        print(f"📱 代替テキスト: {current_flex['altText']}")

        print(f"✅ 今日の詳細予報作成成功")
        print(f"📱 代替テキスト: {today_forecast['altText']}")

        # 送信パターンの例
        print(f"\n📲 送信パターン例:")
        print(f"   パターン1: 現在天気のみ（簡潔）")
        print(f"   パターン2: 現在天気 + 詳細予報（詳細）")
        print(f"   パターン3: 雨予報時のみ送信（条件付き）")

        return current_flex, today_forecast

    except Exception as e:
        print(f"❌ エラー: {e}")
        return None, None

def demo_conditional_notifications():
    """条件付き通知のデモ"""
    print("\n☔ 条件付き通知デモ")
    print("=" * 60)

    print(f"🎯 通知条件:")
    print(f"   - 降水確率50%以上")
    print(f"   - 最高気温30℃以上")
    print(f"   - 最低気温5℃以下")

    template = WeatherFlexTemplate()

    # 明日の天気をチェック
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        forecasts = template.get_forecast_by_date("東京都", tomorrow)

        if forecasts:
            # 降水確率の最大値
            max_pop = max([f['pop'] for f in forecasts])

            # 気温の範囲
            temps = [f['temperature'] for f in forecasts]
            max_temp = max(temps)
            min_temp = min(temps)

            print(f"\n📊 明日の天気データ:")
            print(f"   🌧️ 最大降水確率: {max_pop}%")
            print(f"   🌡️ 最高気温: {max_temp}℃")
            print(f"   🌡️ 最低気温: {min_temp}℃")

            # 条件チェック
            notifications = []

            if max_pop >= 50:
                rain_flex = template.create_forecast_flex(
                    "東京都",
                    tomorrow,
                    f"☔ 雨予報！明日の天気"
                )
                notifications.append(("雨予報通知", rain_flex))
                print(f"   ⚠️ 雨予報通知: 有効（降水確率{max_pop}%）")

            if max_temp >= 30:
                hot_flex = template.create_forecast_flex(
                    "東京都",
                    tomorrow,
                    f"🌡️ 暑さ注意！明日の天気"
                )
                notifications.append(("暑さ注意通知", hot_flex))
                print(f"   🔥 暑さ注意通知: 有効（最高気温{max_temp}℃）")

            if min_temp <= 5:
                cold_flex = template.create_forecast_flex(
                    "東京都",
                    tomorrow,
                    f"🧊 寒波注意！明日の天気"
                )
                notifications.append(("寒波注意通知", cold_flex))
                print(f"   🧊 寒波注意通知: 有効（最低気温{min_temp}℃）")

            if not notifications:
                print(f"   ✅ 通常の天気です（特別な通知なし）")

            return notifications

        else:
            print(f"❌ 天気データの取得に失敗")
            return []

    except Exception as e:
        print(f"❌ エラー: {e}")
        return []

def demo_integration_with_notes():
    """ノート情報との統合デモ"""
    print("\n📝 ノート情報統合デモ")
    print("=" * 60)

    # 11月1日のノート情報デモ（前回のテストから）
    print(f"📋 2025年11月1日のノート情報:")
    print(f"   1. 【重要】プロジェクト打ち合わせ - 15:00〜")
    print(f"   2. 忘年会の日程調整 - 締切")
    print(f"   3. 資料準備のお知らせ")

    template = WeatherFlexTemplate()

    try:
        # 11月1日の天気予報
        weather_flex = template.create_forecast_flex(
            "東京都",
            "2025-11-01",
            f"📅 11月1日の天気情報"
        )

        print(f"\n✅ ノート連携天気予報作成成功")
        print(f"📱 代替テキスト: {weather_flex['altText']}")

        # 統合メッセージの例
        print(f"\n📲 統合メッセージ例:")
        print(f"   1. テキスト: '11月1日のスケジュールをお知らせします'")
        print(f"   2. テキスト: 'ノート情報 3件（重要事項含む）'")
        print(f"   3. Flex Message: 天気予報カード")
        print(f"   4. テキスト: '詳細はノートをご確認ください'")

        return weather_flex

    except Exception as e:
        print(f"❌ エラー: {e}")
        return None

def save_demo_outputs():
    """デモ出力をJSONファイルに保存"""
    print("\n💾 デモ出力保存")
    print("=" * 60)

    template = WeatherFlexTemplate()

    demo_outputs = {}

    try:
        # 各種デモのFlex Messageを作成
        demo_outputs["practice_reminder"] = template.create_forecast_flex(
            "東京都",
            (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "🏃‍♂️ 練習予定天気情報"
        )

        demo_outputs["current_weather"] = template.create_current_weather_flex(
            "東京都",
            "🌅 今日の天気"
        )

        demo_outputs["detailed_forecast"] = template.create_detailed_forecast_flex(
            "東京都",
            datetime.now().strftime("%Y-%m-%d")
        )

        # JSONファイルに保存
        output_file = "weather_flex_demo_outputs.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(demo_outputs, f, ensure_ascii=False, indent=2, default=str)

        print(f"✅ デモ出力保存成功: {output_file}")
        print(f"📄 ファイルサイズ: {os.path.getsize(output_file)} bytes")
        print(f"📊 保存したパターン数: {len(demo_outputs)}種類")

        return output_file

    except Exception as e:
        print(f"❌ 保存エラー: {e}")
        return None

def main():
    """メイン処理"""
    print("🌤️ 天気情報Flex Message実用デモ")
    print("=" * 80)

    print(f"📅 デモ実行日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")

    # 各デモを実行
    demo_practice_reminder()
    demo_event_notification()
    demo_daily_weather_notification()
    demo_conditional_notifications()
    demo_integration_with_notes()

    # デモ出力を保存
    output_file = save_demo_outputs()

    print("\n" + "=" * 80)
    print("✅ 天気情報Flex Message実用デモ 完了")
    print("=" * 80)

    # 実装まとめ
    print(f"\n📋 実装内容まとめ:")
    print(f"   ✅ 現在天気のFlex Message生成")
    print(f"   ✅ 指定日予報のFlex Message生成")
    print(f"   ✅ 詳細時間别予報のFlex Message生成")
    print(f"   ✅ 練習予定リマインダー連携")
    print(f"   ✅ イベント通知連携")
    print(f"   ✅ 条件付き通知（雨/暑さ/寒さ）")
    print(f"   ✅ ノート情報との統合")
    print(f"   ✅ JSON出力とファイル保存")

    print(f"\n🎯 活用例:")
    print(f"   📱 LINE Bot自動通知")
    print(f"   🏃‍♂️ 練習予定リマインダー")
    print(f"   🎉 イベント当日の天気案内")
    print(f"   ☔ 天候警告通知")
    print(f"   📝 ノート連携スケジュール通知")

    if output_file:
        print(f"\n📄 サンプルファイル: {output_file}")
        print(f"   このファイルをLINE Messaging APIに送信可能")

    print(f"\n🚀 これで天気情報付きLINE Botが完成です！")

if __name__ == "__main__":
    main()
