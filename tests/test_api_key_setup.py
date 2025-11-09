#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenWeatherMap API キー設定確認テスト
"""

import os
import sys

# プロジェクトのパスを追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

def check_api_key_setup():
    """API キー設定状況を確認"""
    print("🔑 OpenWeatherMap API キー設定確認")
    print("=" * 50)

    # 環境変数から取得
    api_key = os.getenv('OPENWEATHERMAP_API_KEY')

    print(f"📋 環境変数確認:")
    if api_key:
        # セキュリティのため、キーの一部のみ表示
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "短すぎます"
        print(f"  ✅ OPENWEATHERMAP_API_KEY: {masked_key}")
        print(f"  📏 キー長: {len(api_key)} 文字")

        if len(api_key) == 32:
            print("  ✅ キー長: 正常（32文字）")
        else:
            print("  ⚠️ キー長: 標準的でない長さ")
    else:
        print("  ❌ OPENWEATHERMAP_API_KEY: 設定されていません")

    # サービスクラスでの読み込み確認
    try:
        import sys; import os; sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'archive')); from openweather_service import OpenWeatherMapService
        service = OpenWeatherMapService()

        print(f"\n🔧 サービスクラス確認:")
        if service.api_key and service.api_key != "your_api_key_here":
            masked_service_key = service.api_key[:8] + "..." + service.api_key[-4:] if len(service.api_key) > 12 else "短すぎます"
            print(f"  ✅ サービス内APIキー: {masked_service_key}")
            print("  ✅ 実際のAPIキーが設定されています")
        else:
            print(f"  ❌ サービス内APIキー: {service.api_key}")
            print("  ❌ デフォルト値またはなし")

    except Exception as e:
        print(f"  ❌ サービス読み込みエラー: {e}")

    # 実際のAPI接続テスト
    print(f"\n🌐 API接続テスト:")
    try:
        import sys; import os; sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'archive')); from openweather_service import get_weather_for_location

        # 東京の現在の天気を取得（実際のAPIを試行）
        weather_data = get_weather_for_location("東京都", "新宿", 0)

        if weather_data:
            if weather_data.get('is_mock_data', False):
                print("  ⚠️ モックデータが返されました")
                print("  📝 APIキーの設定または接続に問題がある可能性があります")
            else:
                print("  ✅ 実際のAPIデータを取得しました")
                print(f"  🌡️ 気温: {weather_data.get('temperature', 'N/A')}°C")
                print(f"  ☁️ 天気: {weather_data.get('description', 'N/A')}")
                print(f"  📡 データソース: 実際のOpenWeatherMap API")
        else:
            print("  ❌ データ取得失敗")

    except Exception as e:
        print(f"  ❌ API接続テストエラー: {e}")

    # 環境変数設定方法の案内
    print(f"\n💡 環境変数設定方法:")
    print("  Windows (PowerShell):")
    print("    $env:OPENWEATHERMAP_API_KEY='your_actual_api_key'")
    print("  Windows (コマンドプロンプト):")
    print("    set OPENWEATHERMAP_API_KEY=your_actual_api_key")
    print("  Linux/Mac:")
    print("    export OPENWEATHERMAP_API_KEY='your_actual_api_key'")
    print("\n  または .env ファイルを作成:")
    print("    OPENWEATHERMAP_API_KEY=your_actual_api_key")

def test_real_api_call():
    """実際のAPI呼び出しテスト"""
    print(f"\n" + "=" * 50)
    print("🌐 実際のAPI呼び出し詳細テスト")
    print("=" * 50)

    try:
        import requests
        import sys; import os; sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'archive')); from openweather_service import OpenWeatherMapService

        service = OpenWeatherMapService()

        if service.api_key and service.api_key != "your_api_key_here":
            print("🔍 直接API呼び出しテスト:")

            # 東京の座標
            lat, lon = 35.6762, 139.6503

            # 現在の天気API呼び出し
            params = {
                'lat': lat,
                'lon': lon,
                'appid': service.api_key,
                'units': 'metric',
                'lang': 'ja'
            }

            try:
                response = requests.get(f"{service.base_url}/weather",
                                      params=params, timeout=10)

                print(f"  📡 APIリクエスト: {response.url}")
                print(f"  📊 レスポンスコード: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    print("  ✅ API呼び出し成功")
                    print(f"  🌡️ 気温: {data['main']['temp']}°C")
                    print(f"  💧 湿度: {data['main']['humidity']}%")
                    print(f"  ☁️ 天気: {data['weather'][0]['description']}")
                    print(f"  📍 場所: {data.get('name', 'N/A')}")
                elif response.status_code == 401:
                    print("  ❌ 認証エラー: APIキーが無効です")
                elif response.status_code == 429:
                    print("  ⚠️ レート制限: API呼び出し制限に達しました")
                else:
                    print(f"  ❌ APIエラー: {response.status_code}")
                    print(f"  📝 エラー内容: {response.text}")

            except requests.exceptions.RequestException as e:
                print(f"  ❌ ネットワークエラー: {e}")

        else:
            print("⚠️ APIキーが設定されていないため、直接テストをスキップします")

    except Exception as e:
        print(f"❌ 詳細テストエラー: {e}")

if __name__ == "__main__":
    check_api_key_setup()
    test_real_api_call()

