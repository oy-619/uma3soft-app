#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_weather_data_extraction():
    """天気情報抽出ロジックのデバッグテスト"""
    print("=" * 60)
    print("🔍 天気情報抽出ロジックのデバッグテスト")
    print("=" * 60)

    try:
        from weather_flex_template import WeatherFlexTemplate
        from reminder_flex_customizer import ReminderFlexCustomizer

        # 天気テンプレート生成
        weather_template = WeatherFlexTemplate()
        customizer = ReminderFlexCustomizer()

        # モック天気Flexを生成
        print("📊 モック天気Flex Message生成:")
        weather_flex = weather_template.create_current_weather_flex("東京都大田区")
        print("✅ 天気Flex生成成功")

        # 天気情報抽出テスト
        print("\n🔍 天気情報抽出テスト:")
        weather_info = customizer._extract_weather_info_from_base_flex(weather_flex)

        print("抽出された天気情報:")
        for key, value in weather_info.items():
            print(f"  {key}: {value}")

        # 実際のFlex構造をファイルに保存して確認
        with open('debug_weather_flex.json', 'w', encoding='utf-8') as f:
            json.dump(weather_flex, f, ensure_ascii=False, indent=2)

        print(f"\n💾 デバッグ用ファイル保存: debug_weather_flex.json")

        # Flexの構造を簡単に確認
        def analyze_flex_structure(obj, path="", level=0):
            """Flex構造を再帰的に分析"""
            if level > 5:  # 深すぎる場合は停止
                return

            if isinstance(obj, dict):
                if obj.get("type") == "text":
                    text = obj.get("text", "")
                    if any(keyword in text for keyword in ["湿度", "降水", "気温", "天気"]):
                        print(f"    📍 {path}: {text}")
                elif "contents" in obj:
                    analyze_flex_structure(obj["contents"], path + ".contents", level + 1)
                else:
                    for key, value in obj.items():
                        if key in ["contents", "body", "header"]:
                            analyze_flex_structure(value, path + f".{key}", level + 1)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    analyze_flex_structure(item, path + f"[{i}]", level + 1)

        print("\n🔍 Flex構造内のテキスト要素:")
        analyze_flex_structure(weather_flex)

        return True

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_weather_data_extraction()
