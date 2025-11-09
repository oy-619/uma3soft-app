#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡素化されたリマインダーFlex Messageのテスト
ボタンなし、上段にノート情報、下段に会場・天候情報の新レイアウト
"""

import os
import sys
import json
from datetime import datetime, timedelta

# プロジェクトルートを追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.reminder_flex_customizer import ReminderFlexCustomizer
from src.weather_flex_template import WeatherFlexTemplate

def test_simplified_reminder_flex():
    """簡素化されたリマインダーFlex Messageのテスト"""

    print("=" * 70)
    print("🧪 簡素化リマインダーFlex Message テスト")
    print("=" * 70)

    # テスト用のイベントデータ
    test_events = [
        {
            "content": """【大会のお知らせ】
場所：東京ドーム
時間：13:00 開始
持ち物：ユニフォーム、スパイク
注意事項：雨天決行
集合場所：正面入口""",
            "date": datetime.now() + timedelta(days=1),
            "days_until": 1,
            "is_input_deadline": False,
            "description": "明日開催のイベント"
        },
        {
            "content": """【入力期限のご案内】
参加申込みの締切が近づいています
【大会会場】神宮球場
連絡先：担当者まで
必要書類：参加申込書""",
            "date": datetime.now() + timedelta(days=0),
            "days_until": 0,
            "is_input_deadline": True,
            "description": "本日期限の入力締切"
        }
    ]

    # カスタマイザーと天気テンプレートを初期化
    customizer = ReminderFlexCustomizer()
    weather_template = WeatherFlexTemplate()

    for i, event in enumerate(test_events, 1):
        print(f"\n📋 テストケース {i}: {event['description']}")
        print("-" * 50)

        try:
            # 場所情報から天気情報を取得
            location_info = customizer._extract_location_info(event['content'])
            print(f"🏟️ 抽出された場所: {location_info}")

            # 基本の天気Flex Message作成
            if location_info:
                if event['days_until'] == 0:
                    base_flex = weather_template.create_current_weather_flex(location_info)
                else:
                    forecast_date = event['date'].strftime('%Y-%m-%d')
                    base_flex = weather_template.create_forecast_flex(location_info, forecast_date)
            else:
                # 場所情報がない場合のダミーデータ
                base_flex = {
                    "type": "flex",
                    "altText": "天候情報",
                    "contents": {
                        "type": "bubble",
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "気温: 20℃"},
                                {"type": "text", "text": "晴れ"},
                                {"type": "text", "text": "湿度: 60%"},
                                {"type": "text", "text": "風速: 2m/s"}
                            ]
                        }
                    }
                }

            # カスタムリマインダーFlex Message作成
            custom_flex = customizer._create_custom_reminder_flex(
                event_content=event['content'],
                event_date=event['date'],
                days_until=event['days_until'],
                is_input_deadline=event['is_input_deadline'],
                base_flex=base_flex
            )

            # 結果を保存
            output_file = f"test_simplified_reminder_{i}.json"
            output_path = os.path.join(project_root, "tests", output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(custom_flex, f, ensure_ascii=False, indent=2)

            # 結果の分析
            flex_size = len(json.dumps(custom_flex))
            alt_text = custom_flex.get("altText", "なし")
            header_text = custom_flex["contents"]["header"]["contents"][0]["text"]

            print(f"✅ カスタムFlex Message作成成功")
            print(f"   📏 サイズ: {flex_size:,} bytes")
            print(f"   📝 Alt Text: {alt_text}")
            print(f"   🎯 ヘッダー: {header_text}")
            print(f"   💾 保存先: {output_file}")

            # 構造チェック
            print(f"\n🔍 構造チェック:")
            contents = custom_flex["contents"]
            print(f"   - ヘッダー: {'✓' if 'header' in contents else '✗'}")
            print(f"   - ボディ: {'✓' if 'body' in contents else '✗'}")
            print(f"   - フッター: {'✓' if 'footer' in contents else '✗'}")

            # ボタンがないことを確認
            flex_json = json.dumps(custom_flex)
            has_buttons = '"type": "button"' in flex_json or '"action"' in flex_json
            print(f"   - ボタンなし: {'✗ ボタンが検出されました' if has_buttons else '✓ ボタンなし'}")

            # セクション構成チェック
            body_contents = contents["body"]["contents"]
            section_count = len(body_contents)
            print(f"   - セクション数: {section_count}")

            print(f"✅ テストケース {i} 完了\n")

        except Exception as e:
            print(f"❌ テストケース {i} でエラー: {e}")
            import traceback
            traceback.print_exc()

    print("=" * 70)
    print("🎯 簡素化リマインダーFlex Message テスト完了")
    print("=" * 70)
    print("\n📋 期待される改善点:")
    print("✓ 参加予定などのボタンが除去されている")
    print("✓ メッセージ上段にノート情報が配置されている")
    print("✓ メッセージ下段に会場名と天候情報が配置されている")
    print("✓ よりシンプルで読みやすいレイアウト")

if __name__ == "__main__":
    test_simplified_reminder_flex()
