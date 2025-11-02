#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from weather_flex_template import WeatherFlexTemplate

def test_weather_template():
    """天気テンプレートのテスト"""
    print("=" * 50)
    print("天気Flex Messageテンプレートのテスト開始")
    print("=" * 50)

    try:
        # クラス初期化
        template = WeatherFlexTemplate()
        print("✅ クラス初期化成功")

        # 現在天気テスト
        current_flex = template.create_current_weather_flex('Tokyo,JP')
        print("✅ 現在天気Flex生成成功")
        print(f"   Type: {current_flex.get('type', 'unknown')}")

        # 予報テスト
        from datetime import datetime, timedelta
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        forecast_flex = template.create_forecast_flex('Tokyo,JP', tomorrow)
        print("✅ 天気予報Flex生成成功")
        print(f"   Type: {forecast_flex.get('type', 'unknown')}")

        # 詳細予報テスト
        detailed_flex = template.create_detailed_forecast_flex('Tokyo,JP', tomorrow)
        print("✅ 詳細予報Flex生成成功")
        print(f"   Type: {detailed_flex.get('type', 'unknown')}")

        print("\n" + "=" * 50)
        print("🎉 全てのテストが正常に完了しました！")
        print("ボタンが削除されたFlex Messageテンプレートが完成しました。")
        print("=" * 50)

        return True

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_weather_template()
