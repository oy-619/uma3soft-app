#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def debug_flex_structure():
    """Flex構造を詳細にデバッグ"""
    print("=" * 70)
    print("🔍 Flex構造詳細デバッグ")
    print("=" * 70)

    try:
        from weather_flex_template import WeatherFlexTemplate

        # 天気テンプレート生成
        weather_template = WeatherFlexTemplate()

        # モック天気Flexを生成
        print("📊 モック天気Flex Message生成:")
        weather_flex = weather_template.create_current_weather_flex("東京都")

        # 完全なFlex構造をファイルに保存
        with open('debug_full_flex_structure.json', 'w', encoding='utf-8') as f:
            json.dump(weather_flex, f, ensure_ascii=False, indent=2)

        print("💾 完全なFlex構造保存: debug_full_flex_structure.json")

        # Flexの最上位キーを確認
        print("\n📋 Flexの最上位キー:")
        for key in weather_flex.keys():
            print(f"  - {key}")

        # 実際の構造を探索
        print("\n🔍 構造探索:")
        def explore_structure(obj, path="root", depth=0):
            if depth > 10:  # 無限再帰防止
                return

            indent = "  " * depth
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in ['text', 'contents', 'type', 'layout']:
                        if isinstance(value, str):
                            print(f"{indent}{path}.{key}: '{value}'")
                        elif isinstance(value, list):
                            print(f"{indent}{path}.{key}: [リスト - {len(value)}項目]")
                            for i, item in enumerate(value[:3]):  # 最初の3項目のみ
                                explore_structure(item, f"{path}.{key}[{i}]", depth + 1)
                        elif isinstance(value, dict):
                            print(f"{indent}{path}.{key}: {{オブジェクト}}")
                            explore_structure(value, f"{path}.{key}", depth + 1)
            elif isinstance(obj, list):
                for i, item in enumerate(obj[:3]):  # 最初の3項目のみ
                    explore_structure(item, f"{path}[{i}]", depth + 1)

        explore_structure(weather_flex)

        return weather_flex

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    debug_flex_structure()
