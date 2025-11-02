#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天気情報Flex Messageテンプレートシステム
指定した場所と日付に基づいて天気情報を取得し、LINE Flex Message形式に変換
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class WeatherFlexTemplate:
    """天気情報のFlex Messageテンプレート生成クラス"""

    def __init__(self):
        """初期化"""
        self.api_key = self._get_api_key()
        self.base_url = "https://api.openweathermap.org/data/2.5"

    def _get_api_key(self) -> str:
        """OpenWeatherMap APIキーを取得"""
        # 環境変数から取得を試行
        api_key = os.getenv('OPENWEATHERMAP_API_KEY')

        if not api_key:
            # .envファイルから読み込み
            env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
            if os.path.exists(env_file):
                try:
                    with open(env_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.startswith('OPENWEATHERMAP_API_KEY='):
                                api_key = line.split('=', 1)[1].strip()
                                break
                except Exception as e:
                    print(f"[WEATHER_FLEX] .envファイル読み込みエラー: {e}")

        if not api_key:
            print("[WEATHER_FLEX] 警告: OpenWeatherMap APIキーが設定されていません")
            return "mock_api_key"

        return api_key

    def get_current_weather(self, location: str) -> Optional[Dict]:
        """現在の天気情報を取得"""
        if self.api_key == "mock_api_key":
            return self._get_mock_weather_data(location)

        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'ja'
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            return self._format_current_weather(data)

        except Exception as e:
            print(f"[WEATHER_FLEX] 現在天気取得エラー: {e}")
            return self._get_mock_weather_data(location)

    def get_forecast_by_date(self, location: str, target_date: str) -> List[Dict]:
        """指定日付の天気予報を取得

        Args:
            location: 場所（例: "Ota,JP", "東京都"）
            target_date: 対象日付（YYYY-MM-DD形式）

        Returns:
            List[Dict]: 指定日の天気予報リスト
        """
        if self.api_key == "mock_api_key":
            return self._get_mock_forecast_data(location, target_date)

        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'ja'
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            return self._extract_date_forecast(data, target_date)

        except Exception as e:
            print(f"[WEATHER_FLEX] 予報取得エラー: {e}")
            return self._get_mock_forecast_data(location, target_date)

    def _format_current_weather(self, data: Dict) -> Dict:
        """現在天気データをフォーマット"""
        return {
            'location': data['name'],
            'country': data['sys'].get('country', ''),
            'temperature': round(data['main']['temp']),
            'feels_like': round(data['main']['feels_like']),
            'temp_min': round(data['main']['temp_min']),
            'temp_max': round(data['main']['temp_max']),
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'description': data['weather'][0]['description'],
            'main': data['weather'][0]['main'],
            'icon': data['weather'][0]['icon'],
            'wind_speed': round(data['wind'].get('speed', 0) * 3.6, 1),  # m/s to km/h
            'wind_direction': data['wind'].get('deg', 0),
            'clouds': data['clouds']['all'],
            'visibility': data.get('visibility', 10000) / 1000,  # meters to km
            'timestamp': datetime.now()
        }

    def _extract_date_forecast(self, data: Dict, target_date: str) -> List[Dict]:
        """指定日付の予報データを抽出"""
        forecasts = data.get("list", [])
        result = []

        for item in forecasts:
            dt_txt = item["dt_txt"]  # 例: "2025-10-30 09:00:00"
            if dt_txt.startswith(target_date):
                forecast_data = {
                    "time": dt_txt,
                    "datetime": datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S"),
                    "weather": item["weather"][0]["description"],
                    "main": item["weather"][0]["main"],
                    "icon": item["weather"][0]["icon"],
                    "temperature": round(item["main"]["temp"]),
                    "feels_like": round(item["main"]["feels_like"]),
                    "temp_min": round(item["main"]["temp_min"]),
                    "temp_max": round(item["main"]["temp_max"]),
                    "humidity": item["main"]["humidity"],
                    "pressure": item["main"]["pressure"],
                    "wind_speed": round(item["wind"].get("speed", 0) * 3.6, 1),  # m/s to km/h
                    "wind_direction": item["wind"].get("deg", 0),
                    "clouds": item["clouds"]["all"],
                    "pop": round(item.get("pop", 0) * 100),  # 降水確率（0〜1 → %）
                    "rain": item.get("rain", {}).get("3h", 0),  # 3時間降水量
                    "snow": item.get("snow", {}).get("3h", 0)   # 3時間降雪量
                }
                result.append(forecast_data)

        return result

    def create_current_weather_flex(self, location: str, custom_title: str = None) -> Dict:
        """現在の天気情報のFlex Messageを作成"""
        weather_data = self.get_current_weather(location)

        if not weather_data:
            return self._create_error_flex("天気情報の取得に失敗しました")

        title = custom_title or f"🌤 {weather_data['location']}の現在の天気"
        date_str = weather_data['timestamp'].strftime("%Y年%m月%d日 %H:%M")

        return {
            "type": "flex",
            "altText": f"{weather_data['location']}の現在の天気情報",
            "contents": {
                "type": "bubble",
                "size": "mega",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": title,
                            "weight": "bold",
                            "size": "xl",
                            "align": "center",
                            "wrap": True
                        },
                        {
                            "type": "text",
                            "text": f"📅 {date_str}",
                            "size": "sm",
                            "color": "#888888",
                            "align": "center"
                        },
                        {
                            "type": "separator",
                            "margin": "md"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "margin": "md",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "🌤 天気:",
                                            "size": "md",
                                            "color": "#555555",
                                            "flex": 0,
                                            "weight": "bold"
                                        },
                                        {
                                            "type": "text",
                                            "text": weather_data['description'],
                                            "size": "md",
                                            "flex": 0,
                                            "margin": "sm"
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "🌡️ 気温:",
                                            "size": "md",
                                            "color": "#555555",
                                            "flex": 0,
                                            "weight": "bold"
                                        },
                                        {
                                            "type": "text",
                                            "text": f"{weather_data['temperature']}℃ (体感: {weather_data['feels_like']}℃)",
                                            "size": "md",
                                            "flex": 0,
                                            "margin": "sm"
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "📊 最高/最低:",
                                            "size": "md",
                                            "color": "#555555",
                                            "flex": 0,
                                            "weight": "bold"
                                        },
                                        {
                                            "type": "text",
                                            "text": f"{weather_data['temp_max']}℃ / {weather_data['temp_min']}℃",
                                            "size": "md",
                                            "flex": 0,
                                            "margin": "sm"
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "💧 湿度:",
                                            "size": "md",
                                            "color": "#555555",
                                            "flex": 0,
                                            "weight": "bold"
                                        },
                                        {
                                            "type": "text",
                                            "text": f"{weather_data['humidity']}%",
                                            "size": "md",
                                            "flex": 0,
                                            "margin": "sm"
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "💨 風速:",
                                            "size": "md",
                                            "color": "#555555",
                                            "flex": 0,
                                            "weight": "bold"
                                        },
                                        {
                                            "type": "text",
                                            "text": f"{weather_data['wind_speed']}km/h (風向: {weather_data['wind_direction']}°)",
                                            "size": "md",
                                            "flex": 0,
                                            "margin": "sm"
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "🌫️ 気圧:",
                                            "size": "md",
                                            "color": "#555555",
                                            "flex": 0,
                                            "weight": "bold"
                                        },
                                        {
                                            "type": "text",
                                            "text": f"{weather_data['pressure']}hPa",
                                            "size": "md",
                                            "flex": 0,
                                            "margin": "sm"
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "👁️ 視程:",
                                            "size": "md",
                                            "color": "#555555",
                                            "flex": 0,
                                            "weight": "bold"
                                        },
                                        {
                                            "type": "text",
                                            "text": f"{weather_data['visibility']}km",
                                            "size": "md",
                                            "flex": 0,
                                            "margin": "sm"
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "☁️ 雲量:",
                                            "size": "md",
                                            "color": "#555555",
                                            "flex": 0,
                                            "weight": "bold"
                                        },
                                        {
                                            "type": "text",
                                            "text": f"{weather_data['clouds']}%",
                                            "size": "md",
                                            "flex": 0,
                                            "margin": "sm"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "separator",
                            "margin": "lg"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "margin": "lg",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "� 天気アドバイス",
                                    "size": "md",
                                    "weight": "bold",
                                    "color": "#FF8C00",
                                    "align": "center"
                                },
                                {
                                    "type": "text",
                                    "text": self._get_weather_advice(weather_data),
                                    "size": "sm",
                                    "color": "#666666",
                                    "align": "center",
                                    "wrap": True
                                }
                            ]
                        },
                        {
                            "type": "separator",
                            "margin": "md"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "margin": "md",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "�💬 参加可否をお知らせください",
                                    "size": "md",
                                    "weight": "bold",
                                    "color": "#0066CC",
                                    "align": "center"
                                },
                                {
                                    "type": "text",
                                    "text": "天気を確認して、参加予定をお聞かせください！",
                                    "size": "sm",
                                    "color": "#666666",
                                    "align": "center",
                                    "wrap": True
                                }
                            ]
                        }
                    ]
                }
            }
        }

    def create_forecast_flex(self, location: str, target_date: str, custom_title: str = None) -> Dict:
        """指定日付の天気予報Flex Messageを作成"""
        forecasts = self.get_forecast_by_date(location, target_date)

        if not forecasts:
            return self._create_error_flex(f"{target_date}の天気予報が見つかりませんでした")

        # 日付をフォーマット
        date_obj = datetime.strptime(target_date, "%Y-%m-%d")
        date_str = date_obj.strftime("%Y年%m月%d日")
        weekday = ["月", "火", "水", "木", "金", "土", "日"][date_obj.weekday()]

        title = custom_title or f"🌤 {location}の天気予報"

        # 代表的な天気情報を取得（昼頃の予報を優先）
        noon_forecast = None
        for f in forecasts:
            hour = f['datetime'].hour
            if 11 <= hour <= 14:  # 11:00-14:00の予報を優先
                noon_forecast = f
                break

        if not noon_forecast:
            noon_forecast = forecasts[0]  # なければ最初の予報を使用

        # 気温の範囲を計算
        temps = [f['temperature'] for f in forecasts]
        temp_min = min(temps)
        temp_max = max(temps)

        # 降水確率の最大値
        pop_max = max([f['pop'] for f in forecasts])

        # アドバイスメッセージを生成
        advice_message = self._get_weather_advice(noon_forecast, forecasts)

        return {
            "type": "flex",
            "altText": f"{date_str}({weekday})の天気予報（{location}）",
            "contents": {
                "type": "bubble",
                "size": "mega",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": title,
                            "weight": "bold",
                            "size": "xl",
                            "align": "center",
                            "wrap": True
                        },
                        {
                            "type": "text",
                            "text": f"📅 日付：{date_str}（{weekday}）",
                            "size": "sm",
                            "color": "#888888",
                            "align": "center"
                        },
                        {
                            "type": "separator",
                            "margin": "md"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "margin": "md",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "🌤 天気:",
                                            "size": "md",
                                            "color": "#555555",
                                            "flex": 0,
                                            "weight": "bold"
                                        },
                                        {
                                            "type": "text",
                                            "text": noon_forecast['weather'],
                                            "size": "md",
                                            "flex": 0,
                                            "margin": "sm"
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "🌡️ 気温:",
                                            "size": "md",
                                            "color": "#555555",
                                            "flex": 0,
                                            "weight": "bold"
                                        },
                                        {
                                            "type": "text",
                                            "text": f"{temp_max}℃（最高） / {temp_min}℃（最低）",
                                            "size": "md",
                                            "flex": 0,
                                            "margin": "sm"
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "💧 湿度:",
                                            "size": "md",
                                            "color": "#555555",
                                            "flex": 0,
                                            "weight": "bold"
                                        },
                                        {
                                            "type": "text",
                                            "text": f"{noon_forecast['humidity']}%",
                                            "size": "md",
                                            "flex": 0,
                                            "margin": "sm"
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "💨 風速:",
                                            "size": "md",
                                            "color": "#555555",
                                            "flex": 0,
                                            "weight": "bold"
                                        },
                                        {
                                            "type": "text",
                                            "text": f"{noon_forecast['wind_speed']}km/h (風向: {noon_forecast['wind_direction']}°)",
                                            "size": "md",
                                            "flex": 0,
                                            "margin": "sm"
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "☔ 降水確率:",
                                            "size": "md",
                                            "color": "#555555",
                                            "flex": 0,
                                            "weight": "bold"
                                        },
                                        {
                                            "type": "text",
                                            "text": f"{pop_max}%",
                                            "size": "md",
                                            "flex": 0,
                                            "margin": "sm"
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "🌫️ 気圧:",
                                            "size": "md",
                                            "color": "#555555",
                                            "flex": 0,
                                            "weight": "bold"
                                        },
                                        {
                                            "type": "text",
                                            "text": f"{noon_forecast['pressure']}hPa",
                                            "size": "md",
                                            "flex": 0,
                                            "margin": "sm"
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "☁️ 雲量:",
                                            "size": "md",
                                            "color": "#555555",
                                            "flex": 0,
                                            "weight": "bold"
                                        },
                                        {
                                            "type": "text",
                                            "text": f"{noon_forecast['clouds']}%",
                                            "size": "md",
                                            "flex": 0,
                                            "margin": "sm"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "separator",
                            "margin": "lg"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "margin": "lg",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "� 天気アドバイス",
                                    "size": "md",
                                    "weight": "bold",
                                    "color": "#FF8C00",
                                    "align": "center"
                                },
                                {
                                    "type": "text",
                                    "text": advice_message,
                                    "size": "sm",
                                    "color": "#666666",
                                    "align": "center",
                                    "wrap": True
                                }
                            ]
                        },
                        {
                            "type": "separator",
                            "margin": "md"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "margin": "md",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "�📅 予定確認をお願いします",
                                    "size": "md",
                                    "weight": "bold",
                                    "color": "#0066CC",
                                    "align": "center"
                                },
                                {
                                    "type": "text",
                                    "text": "天気予報を確認して、当日の参加可否をお知らせください！",
                                    "size": "sm",
                                    "color": "#666666",
                                    "align": "center",
                                    "wrap": True
                                }
                            ]
                        }
                    ]
                }
            }
        }

    def create_detailed_forecast_flex(self, location: str, target_date: str) -> Dict:
        """指定日付の詳細な時間別天気予報Flex Messageを作成"""
        forecasts = self.get_forecast_by_date(location, target_date)

        if not forecasts:
            return self._create_error_flex(f"{target_date}の天気予報が見つかりませんでした")

        # 日付をフォーマット
        date_obj = datetime.strptime(target_date, "%Y-%m-%d")
        date_str = date_obj.strftime("%Y年%m月%d日")
        weekday = ["月", "火", "水", "木", "金", "土", "日"][date_obj.weekday()]

        # 時間別予報のコンテンツを作成
        time_contents = []
        for i, forecast in enumerate(forecasts[:8]):  # 最大8個まで表示
            time_str = forecast['datetime'].strftime("%H:%M")

            time_content = {
                "type": "box",
                "layout": "horizontal",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "text",
                        "text": time_str,
                        "size": "sm",
                        "color": "#555555",
                        "flex": 1
                    },
                    {
                        "type": "text",
                        "text": forecast['weather'],
                        "size": "sm",
                        "flex": 2
                    },
                    {
                        "type": "text",
                        "text": f"{forecast['temperature']}℃",
                        "size": "sm",
                        "align": "end",
                        "flex": 1
                    },
                    {
                        "type": "text",
                        "text": f"{forecast['pop']}%",
                        "size": "sm",
                        "align": "end",
                        "flex": 1,
                        "color": "#0066CC" if forecast['pop'] > 30 else "#888888"
                    }
                ]
            }
            time_contents.append(time_content)

            # 区切り線（最後以外）
            if i < len(forecasts[:8]) - 1:
                time_contents.append({
                    "type": "separator",
                    "margin": "sm"
                })

        return {
            "type": "flex",
            "altText": f"{date_str}({weekday})の詳細天気予報（{location}）",
            "contents": {
                "type": "bubble",
                "size": "mega",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"🌤 {location}の詳細予報",
                            "weight": "bold",
                            "size": "xl",
                            "align": "center",
                            "wrap": True
                        },
                        {
                            "type": "text",
                            "text": f"📅 {date_str}（{weekday}）",
                            "size": "sm",
                            "color": "#888888",
                            "align": "center"
                        },
                        {
                            "type": "separator",
                            "margin": "md"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "時刻",
                                    "size": "sm",
                                    "color": "#333333",
                                    "weight": "bold",
                                    "flex": 1
                                },
                                {
                                    "type": "text",
                                    "text": "天気",
                                    "size": "sm",
                                    "color": "#333333",
                                    "weight": "bold",
                                    "flex": 2
                                },
                                {
                                    "type": "text",
                                    "text": "気温",
                                    "size": "sm",
                                    "color": "#333333",
                                    "weight": "bold",
                                    "align": "end",
                                    "flex": 1
                                },
                                {
                                    "type": "text",
                                    "text": "降水",
                                    "size": "sm",
                                    "color": "#333333",
                                    "weight": "bold",
                                    "align": "end",
                                    "flex": 1
                                }
                            ]
                        },
                        {
                            "type": "separator",
                            "margin": "sm"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "xs",
                            "margin": "sm",
                            "contents": time_contents
                        },
                        {
                            "type": "separator",
                            "margin": "lg"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "margin": "md",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "📝 時間別予報を確認して参加をお知らせください",
                                    "size": "sm",
                                    "weight": "bold",
                                    "color": "#0066CC",
                                    "align": "center",
                                    "wrap": True
                                }
                            ]
                        }
                    ]
                }
            }
        }

    def _create_error_flex(self, error_message: str) -> Dict:
        """エラー用のFlex Messageを作成"""
        return {
            "type": "flex",
            "altText": "天気情報エラー",
            "contents": {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "⚠️ エラー",
                            "weight": "bold",
                            "size": "xl",
                            "color": "#FF6B6B",
                            "align": "center"
                        },
                        {
                            "type": "text",
                            "text": error_message,
                            "wrap": True,
                            "margin": "md",
                            "align": "center"
                        }
                    ]
                }
            }
        }

    def _get_mock_weather_data(self, location: str) -> Dict:
        """モックデータ（APIキーが無い場合）"""
        return {
            'location': location.split(',')[0],
            'country': 'JP',
            'temperature': 21,
            'feels_like': 20,
            'temp_min': 14,
            'temp_max': 25,
            'humidity': 65,
            'pressure': 1013,
            'description': '曇り時々晴れ',
            'main': 'Clouds',
            'icon': '03d',
            'wind_speed': 3.2,
            'wind_direction': 180,
            'clouds': 40,
            'visibility': 10.0,
            'timestamp': datetime.now()
        }

    def _get_weather_advice(self, weather_data: Dict, forecast_data: List[Dict] = None) -> str:
        """天気に応じたアドバイスメッセージを生成"""
        advice_parts = []

        # 気温に応じたアドバイス
        temp = weather_data.get('temperature', 20)
        if temp >= 30:
            advice_parts.append("🌡️ 暑いです！水分補給と熱中症対策をお忘れなく")
        elif temp >= 25:
            advice_parts.append("☀️ 暖かいです。軽装で快適に過ごせそうです")
        elif temp >= 15:
            advice_parts.append("🌤️ 過ごしやすい気温です")
        elif temp >= 10:
            advice_parts.append("🧥 少し肌寒いです。上着があると良いでしょう")
        else:
            advice_parts.append("🧊 寒いです！防寒対策をしっかりと")

        # 降水確率に応じたアドバイス
        if forecast_data:
            max_pop = max([f.get('pop', 0) for f in forecast_data])
        else:
            max_pop = 0

        if max_pop >= 70:
            advice_parts.append("☔ 雨の可能性が高いです。傘をお忘れなく！")
        elif max_pop >= 40:
            advice_parts.append("🌦️ 雨の可能性があります。念のため傘を持参ください")
        elif max_pop >= 20:
            advice_parts.append("☁️ 雨の心配は少なそうです")

        # 風速に応じたアドバイス
        wind_speed = weather_data.get('wind_speed', 0)
        if wind_speed >= 15:
            advice_parts.append("💨 風が強いです。帽子など飛ばされないよう注意してください")
        elif wind_speed >= 8:
            advice_parts.append("🍃 やや風があります")

        # 湿度に応じたアドバイス
        humidity = weather_data.get('humidity', 50)
        if humidity >= 80:
            advice_parts.append("💧 湿度が高めです。蒸し暑く感じるかもしれません")
        elif humidity <= 30:
            advice_parts.append("🏜️ 乾燥しています。のど飴や保湿対策があると良いでしょう")

        return " | ".join(advice_parts) if advice_parts else "🌤️ 良い天気をお楽しみください！"

    def _get_mock_forecast_data(self, location: str, target_date: str) -> List[Dict]:
        """モック予報データ（APIキーが無い場合）"""
        base_date = datetime.strptime(target_date, "%Y-%m-%d")
        forecasts = []

        for hour in [9, 12, 15, 18, 21]:
            forecast_time = base_date.replace(hour=hour, minute=0, second=0)
            forecasts.append({
                "time": forecast_time.strftime("%Y-%m-%d %H:%M:%S"),
                "datetime": forecast_time,
                "weather": "曇り時々晴れ",
                "main": "Clouds",
                "icon": "03d",
                "temperature": 21 + (hour - 12) // 3,  # 時間により気温変化
                "feels_like": 20 + (hour - 12) // 3,
                "temp_min": 18,
                "temp_max": 24,
                "humidity": 65,
                "pressure": 1013,
                "wind_speed": 3.2,
                "wind_direction": 180,
                "clouds": 40,
                "pop": 20,  # 降水確率20%
                "rain": 0,
                "snow": 0
            })

        return forecasts
# 便利関数
def create_weather_flex(location: str, date: Optional[str] = None, weather_type: str = "current") -> Dict:
    """
    天気情報のFlex Messageを作成する便利関数

    Args:
        location: 場所
        date: 日付（YYYY-MM-DD形式、Noneの場合は現在の天気）
        weather_type: "current", "forecast", "detailed"

    Returns:
        Dict: Flex Message
    """
    template = WeatherFlexTemplate()

    if weather_type == "current" or date is None:
        return template.create_current_weather_flex(location)
    elif weather_type == "detailed":
        return template.create_detailed_forecast_flex(location, date)
    else:  # forecast
        return template.create_forecast_flex(location, date)


if __name__ == "__main__":
    # テスト実行
    print("=== 天気情報Flex Messageテンプレート テスト ===")

    template = WeatherFlexTemplate()

    # 1. 現在の天気
    print("\n1. 現在の天気情報:")
    current_flex = template.create_current_weather_flex("東京都大田区")
    print(f"   タイプ: {current_flex['type']}")
    print(f"   代替テキスト: {current_flex['altText']}")

    # 2. 指定日の天気予報
    print("\n2. 指定日の天気予報:")
    target_date = "2025-10-30"
    forecast_flex = template.create_forecast_flex("Ota,JP", target_date)
    print(f"   タイプ: {forecast_flex['type']}")
    print(f"   代替テキスト: {forecast_flex['altText']}")

    # 3. 詳細な時間別予報
    print("\n3. 詳細な時間別予報:")
    detailed_flex = template.create_detailed_forecast_flex("Ota,JP", target_date)
    print(f"   タイプ: {detailed_flex['type']}")
    print(f"   代替テキスト: {detailed_flex['altText']}")

    print("\n=== テスト完了 ===")
