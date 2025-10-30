#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenWeatherMap 天気カード付きリマインダーのデモ
"""

import sys
import os
import json
from datetime import datetime, timedelta

# プロジェクトのパスを追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

def create_demo_reminders():
    """デモ用のリマインダーを作成"""
    print("🎯 天気カード付きリマインダーデモ")
    print("=" * 50)

    try:
        from enhanced_reminder_messages import generate_weather_flex_card

        # さまざまなシナリオのテストデータ
        demo_events = [
            {
                "name": "屋外BBQイベント",
                "content": "[ノート] 11月3日(日) 秋のBBQパーティー\n会場: 代々木公園バーベキュー広場\n集合時間: 11:00\n持ち物: 食材、飲み物、炭、軍手\n雨天中止",
                "date": (datetime.now() + timedelta(days=1)).date(),
                "weather_important": True
            },
            {
                "name": "結婚式参列",
                "content": "[ノート] 12月20日(土) 友人の結婚式\n会場: 新宿パークハイアット東京\n時間: 14:00受付開始\n服装: 正装\n交通: JR新宿駅南口から徒歩12分",
                "date": (datetime.now() + timedelta(days=2)).date(),
                "weather_important": True
            },
            {
                "name": "スポーツイベント",
                "content": "[ノート] 11月15日(土) マラソン大会参加\n会場: 渋谷・代々木公園スタート\n集合時間: 7:30\n持ち物: ランニングウェア、シューズ、タオル、飲み物",
                "date": (datetime.now() + timedelta(days=0)).date(),  # 今日
                "weather_important": True
            },
            {
                "name": "商談会議",
                "content": "[ノート] 12月5日(木) 重要商談\n場所: 大阪・梅田オフィス\n時間: 14:00-16:00\n参加者: 営業部、開発部\n資料: 提案書、サンプル",
                "date": (datetime.now() + timedelta(days=3)).date(),
                "weather_important": False
            }
        ]

        for i, event in enumerate(demo_events, 1):
            print(f"\n--- デモ {i}: {event['name']} ---")

            # 天気カードを生成
            weather_flex = generate_weather_flex_card(event)

            if weather_flex:
                print("✅ 天気カード生成成功")

                # JSONファイルとして保存
                filename = f"demo_weather_card_{i}_{event['name'].replace(' ', '_')}.json"
                output_path = os.path.join(project_root, "tests", filename)

                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(weather_flex, f, ensure_ascii=False, indent=2)

                print(f"💾 保存先: {filename}")

                # 天気情報の要約を表示
                contents = weather_flex.get("contents", {})
                alt_text = weather_flex.get("altText", "不明")
                print(f"📱 Alt Text: {alt_text}")

                # ヘッダー情報
                header = contents.get("header", {})
                if header:
                    header_contents = header.get("contents", [])
                    if header_contents and len(header_contents) > 1:
                        location_text = header_contents[1].get("text", "不明")
                        print(f"📍 場所: {location_text}")

            else:
                print("❌ 天気カード生成失敗")

            # 天気重要度による追加情報
            if event.get("weather_important"):
                print("🌤️ 天気情報重要: このイベントは天気の影響を受けやすいです")
            else:
                print("🏢 屋内イベント: 天気の影響は限定的です")

        print("\n" + "=" * 50)
        print("🎉 天気カード付きリマインダーデモ完了！")
        print("\n💡 活用方法:")
        print("  1. LINE Bot で天気カードと通常リマインダーを組み合わせて送信")
        print("  2. 雨天時は自動で「傘を忘れずに！」メッセージを追加")
        print("  3. 屋外イベントには詳細な天気情報を表示")
        print("  4. 温度に応じた服装アドバイスも含まれます")
        print("\n🔧 カスタマイズ可能:")
        print("  - OpenWeatherMap API キーを設定してリアルタイム情報取得")
        print("  - 地域や会場名の自動認識精度向上")
        print("  - 天気に応じたカラーテーマとアイコン")
        print("  - 複数日の予報表示")

    except Exception as e:
        print(f"❌ デモ実行エラー: {e}")

def show_flex_message_structure():
    """Flex Message の構造例を表示"""
    print("\n📋 Flex Message 構造例:")
    print("-" * 30)

    sample_structure = {
        "type": "flex",
        "altText": "東京都の天気情報",
        "contents": {
            "type": "bubble",
            "header": "天気アイコンと地域名",
            "body": {
                "会場名": "例: 代々木公園",
                "天気説明": "例: 晴れ時々曇り",
                "天気カード": {
                    "気温": "22°C (体感24°C)",
                    "湿度": "65%",
                    "降水確率": "20%",
                    "風速": "8km/h"
                },
                "注意メッセージ": "例: 傘を忘れずに！"
            },
            "footer": "データ提供元と取得日時"
        }
    }

    print(json.dumps(sample_structure, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    create_demo_reminders()
    show_flex_message_structure()
