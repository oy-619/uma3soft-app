#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenWeatherMap API を使用した天気情報取得システム
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

class OpenWeatherMapService:
    """OpenWeatherMap API サービスクラス"""

    def __init__(self):
        """初期化"""
        self.api_key = self._get_api_key()
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.geocoding_url = "https://api.openweathermap.org/geo/1.0"

        # 日本の主要都市座標（フォールバック用）
        self.fallback_coordinates = {
            "東京都": {"lat": 35.6762, "lon": 139.6503},
            "大阪府": {"lat": 34.6937, "lon": 135.5023},
            "愛知県": {"lat": 35.1815, "lon": 136.9066},
            "福岡県": {"lat": 33.5904, "lon": 130.4017},
            "北海道": {"lat": 43.0642, "lon": 141.3469},
            "神奈川県": {"lat": 35.4478, "lon": 139.6425},
            "千葉県": {"lat": 35.6074, "lon": 140.1065},
            "埼玉県": {"lat": 35.8617, "lon": 139.6455}
        }

    def _get_api_key(self) -> str:
        """APIキーを取得"""
        # .envファイルから環境変数を読み込み
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            # python-dotenvがインストールされていない場合はスキップ
            pass

        # 環境変数から取得を試す
        api_key = os.getenv('OPENWEATHERMAP_API_KEY')

        if not api_key:
            # .envファイルを直接読み込み（フォールバック）
            try:
                env_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
                if os.path.exists(env_file_path):
                    with open(env_file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.startswith('OPENWEATHERMAP_API_KEY='):
                                api_key = line.split('=', 1)[1].strip()
                                break
            except Exception as e:
                print(f"[ENV_FILE] 読み込みエラー: {e}")

        if not api_key:
            # フリーAPIキー（制限あり）- 実際の使用では独自のAPIキーを設定してください
            # 注意: このキーは制限があるため、実運用では環境変数で設定してください
            api_key = "your_api_key_here"  # 実際のAPIキーに置き換えてください

        return api_key

    def get_coordinates(self, location: str, venue_name: str = "") -> Tuple[float, float]:
        """地名から座標を取得"""
        try:
            # まず venue_name から詳細な場所を抽出
            search_query = self._extract_detailed_location(venue_name) or location

            # Geocoding API で座標取得
            if self.api_key != "your_api_key_here":
                geocoding_params = {
                    'q': f"{search_query},Japan",
                    'limit': 1,
                    'appid': self.api_key
                }

                response = requests.get(f"{self.geocoding_url}/direct",
                                      params=geocoding_params, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    if data:
                        return data[0]['lat'], data[0]['lon']

            # フォールバック: 都道府県の座標を使用
            return self._get_fallback_coordinates(location)

        except Exception as e:
            print(f"[GEOCODING] エラー: {e}")
            return self._get_fallback_coordinates(location)

    def _extract_detailed_location(self, venue_name: str) -> Optional[str]:
        """会場名から詳細な場所を抽出"""
        location_keywords = {
            "代々木公園": "代々木公園",
            "新宿": "新宿",
            "渋谷": "渋谷",
            "池袋": "池袋",
            "品川": "品川",
            "東京ドーム": "東京ドーム",
            "横浜": "横浜",
            "大阪城": "大阪城",
            "京都": "京都",
            "名古屋": "名古屋",
            "福岡": "福岡",
            "札幌": "札幌"
        }

        for keyword, location in location_keywords.items():
            if keyword in venue_name:
                return location

        return None

    def _get_fallback_coordinates(self, location: str) -> Tuple[float, float]:
        """フォールバック座標を取得"""
        coords = self.fallback_coordinates.get(location, self.fallback_coordinates["東京都"])
        return coords["lat"], coords["lon"]

    def get_current_weather(self, location: str, venue_name: str = "") -> Dict:
        """現在の天気情報を取得"""
        try:
            lat, lon = self.get_coordinates(location, venue_name)

            if self.api_key == "your_api_key_here":
                return self._get_mock_weather_data(location)

            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',  # 摂氏温度
                'lang': 'ja'        # 日本語
            }

            response = requests.get(f"{self.base_url}/weather", params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return self._format_current_weather(data, location)
            else:
                print(f"[WEATHER_API] エラー: HTTP {response.status_code}")
                return self._get_mock_weather_data(location)

        except Exception as e:
            print(f"[WEATHER_API] エラー: {e}")
            return self._get_mock_weather_data(location)

    def get_forecast_weather(self, location: str, venue_name: str = "", days: int = 1) -> Dict:
        """予報天気情報を取得"""
        try:
            lat, lon = self.get_coordinates(location, venue_name)

            if self.api_key == "your_api_key_here":
                return self._get_mock_forecast_data(location, days)

            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'ja'
            }

            response = requests.get(f"{self.base_url}/forecast", params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return self._format_forecast_weather(data, location, days)
            else:
                return self._get_mock_forecast_data(location, days)

        except Exception as e:
            print(f"[FORECAST_API] エラー: {e}")
            return self._get_mock_forecast_data(location, days)

    def _format_current_weather(self, data: Dict, location: str) -> Dict:
        """現在の天気データをフォーマット"""
        return {
            "location": location,
            "temperature": round(data["main"]["temp"]),
            "feels_like": round(data["main"]["feels_like"]),
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": round(data["wind"]["speed"] * 3.6, 1),  # m/s to km/h
            "wind_direction": data["wind"].get("deg", 0),
            "description": data["weather"][0]["description"],
            "main": data["weather"][0]["main"],
            "icon": data["weather"][0]["icon"],
            "visibility": data.get("visibility", 10000) / 1000,  # km
            "clouds": data["clouds"]["all"],
            "timestamp": datetime.now(),
            "rain": data.get("rain", {}).get("1h", 0),  # mm/h
            "snow": data.get("snow", {}).get("1h", 0)   # mm/h
        }

    def _format_forecast_weather(self, data: Dict, location: str, days: int) -> Dict:
        """予報天気データをフォーマット"""
        forecasts = []
        target_date = datetime.now().date() + timedelta(days=days)

        for item in data["list"]:
            forecast_time = datetime.fromtimestamp(item["dt"])
            if forecast_time.date() == target_date:
                forecasts.append({
                    "time": forecast_time,
                    "temperature": round(item["main"]["temp"]),
                    "humidity": item["main"]["humidity"],
                    "wind_speed": round(item["wind"]["speed"] * 3.6, 1),
                    "description": item["weather"][0]["description"],
                    "main": item["weather"][0]["main"],
                    "rain_probability": item.get("pop", 0) * 100,  # %
                    "rain": item.get("rain", {}).get("3h", 0)     # mm/3h
                })

        if forecasts:
            # 日中の平均値を計算
            avg_temp = sum(f["temperature"] for f in forecasts) / len(forecasts)
            max_temp = max(f["temperature"] for f in forecasts)
            min_temp = min(f["temperature"] for f in forecasts)
            avg_humidity = sum(f["humidity"] for f in forecasts) / len(forecasts)
            max_rain_prob = max(f["rain_probability"] for f in forecasts)
            avg_wind = sum(f["wind_speed"] for f in forecasts) / len(forecasts)

            return {
                "location": location,
                "date": target_date,
                "average_temperature": round(avg_temp),
                "max_temperature": round(max_temp),
                "min_temperature": round(min_temp),
                "humidity": round(avg_humidity),
                "rain_probability": round(max_rain_prob),
                "wind_speed": round(avg_wind, 1),
                "description": forecasts[len(forecasts)//2]["description"],  # 中間時刻
                "hourly_forecasts": forecasts
            }
        else:
            return self._get_mock_forecast_data(location, days)

    def _get_mock_weather_data(self, location: str) -> Dict:
        """モック天気データ（APIキー未設定時）"""
        import random

        # 現在の日付と季節に応じた現実的な模擬データ
        now = datetime.now()
        month = now.month
        day = now.day

        # 2025年10月30日の現実的な天気データ
        if month == 10:  # 10月（秋）
            # 10月末の現実的な気温範囲
            temp_base = random.randint(12, 20)  # より現実的な範囲
            weather_patterns = [
                {"desc": "晴れ", "humidity": random.randint(45, 65), "rain_prob": random.randint(0, 20)},
                {"desc": "曇り", "humidity": random.randint(60, 80), "rain_prob": random.randint(10, 40)},
                {"desc": "小雨", "humidity": random.randint(75, 90), "rain_prob": random.randint(60, 80)},
                {"desc": "雨", "humidity": random.randint(80, 95), "rain_prob": random.randint(70, 90)}
            ]
        elif month in [12, 1, 2]:  # 冬
            temp_base = random.randint(2, 12)
            weather_patterns = [
                {"desc": "晴れ", "humidity": random.randint(35, 55), "rain_prob": random.randint(0, 15)},
                {"desc": "曇り", "humidity": random.randint(50, 70), "rain_prob": random.randint(5, 25)},
                {"desc": "小雪", "humidity": random.randint(70, 85), "rain_prob": random.randint(40, 60)},
            ]
        elif month in [3, 4, 5]:  # 春
            temp_base = random.randint(10, 22)
            weather_patterns = [
                {"desc": "晴れ", "humidity": random.randint(40, 60), "rain_prob": random.randint(0, 25)},
                {"desc": "曇り", "humidity": random.randint(55, 75), "rain_prob": random.randint(15, 45)},
                {"desc": "雨", "humidity": random.randint(70, 90), "rain_prob": random.randint(60, 85)},
            ]
        elif month in [6, 7, 8]:  # 夏
            temp_base = random.randint(22, 35)
            weather_patterns = [
                {"desc": "晴れ", "humidity": random.randint(60, 80), "rain_prob": random.randint(0, 30)},
                {"desc": "曇り", "humidity": random.randint(70, 90), "rain_prob": random.randint(20, 50)},
                {"desc": "雷雨", "humidity": random.randint(80, 95), "rain_prob": random.randint(70, 95)},
            ]
        else:  # 秋（9,11月）
            temp_base = random.randint(8, 25)
            weather_patterns = [
                {"desc": "晴れ", "humidity": random.randint(45, 65), "rain_prob": random.randint(0, 20)},
                {"desc": "曇り", "humidity": random.randint(60, 80), "rain_prob": random.randint(10, 40)},
                {"desc": "雨", "humidity": random.randint(75, 90), "rain_prob": random.randint(60, 85)},
            ]

        # ランダムに天気パターンを選択
        weather_pattern = random.choice(weather_patterns)

        return {
            "location": location,
            "temperature": temp_base,
            "feels_like": temp_base + random.randint(-2, 3),
            "humidity": weather_pattern["humidity"],
            "pressure": random.randint(1005, 1025),  # より現実的な気圧範囲
            "wind_speed": round(random.uniform(3, 12), 1),  # より現実的な風速
            "wind_direction": random.randint(0, 360),
            "description": weather_pattern["desc"],
            "main": "Clear" if weather_pattern["desc"] == "晴れ" else "Clouds",
            "icon": "01d",
            "visibility": round(random.uniform(8, 15), 1),
            "clouds": random.randint(0, 100),
            "timestamp": datetime.now(),
            "rain": random.uniform(0, 2) if "雨" in weather_pattern["desc"] else 0,
            "rain_probability": weather_pattern["rain_prob"],
            "snow": 0,
            "is_mock_data": True,  # モックデータフラグ
            "data_source": "テスト用シミュレーションデータ"
        }

    def _get_mock_forecast_data(self, location: str, days: int) -> Dict:
        """モック予報データ"""
        import random

        base_weather = self._get_mock_weather_data(location)

        return {
            "location": location,
            "date": datetime.now().date() + timedelta(days=days),
            "average_temperature": base_weather["temperature"],
            "max_temperature": base_weather["temperature"] + random.randint(2, 8),
            "min_temperature": base_weather["temperature"] - random.randint(2, 8),
            "humidity": base_weather["humidity"],
            "rain_probability": random.randint(0, 90),
            "wind_speed": base_weather["wind_speed"],
            "description": base_weather["description"],
            "hourly_forecasts": [],
            "is_mock_data": True  # モックデータフラグ
        }

# グローバルインスタンス
weather_service = OpenWeatherMapService()

def get_weather_for_location(location: str, venue_name: str = "", days_ahead: int = 0) -> Dict:
    """指定地域の天気情報を取得（外部インターフェース）"""
    if days_ahead == 0:
        return weather_service.get_current_weather(location, venue_name)
    else:
        return weather_service.get_forecast_weather(location, venue_name, days_ahead)

if __name__ == "__main__":
    # テスト実行
    print("=== OpenWeatherMap API テスト ===")

    test_locations = [
        ("東京都", "代々木公園グラウンド"),
        ("大阪府", "大阪城ホール"),
        ("北海道", "札幌ドーム")
    ]

    for location, venue in test_locations:
        print(f"\n📍 {location} - {venue}")
        weather = get_weather_for_location(location, venue)
        print(f"  気温: {weather['temperature']}°C")
        print(f"  湿度: {weather['humidity']}%")
        print(f"  風速: {weather['wind_speed']}km/h")
        print(f"  天気: {weather['description']}")
