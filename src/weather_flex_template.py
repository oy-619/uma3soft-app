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
        """現在天気データを整形"""
        main = data.get('main', {})
        weather = data.get('weather', [{}])[0]
        wind = data.get('wind', {})
        clouds = data.get('clouds', {})
        visibility = data.get('visibility', 0)

        return {
            'location': data.get('name', '不明'),
            'temperature': round(main.get('temp', 0), 1),
            'description': weather.get('description', '不明'),
            'humidity': main.get('humidity', 0),
            'pressure': main.get('pressure', 0),
            'wind_speed': wind.get('speed', 0),
            'clouds': clouds.get('all', 0),
            'visibility': visibility / 1000 if visibility else 0,
            'temp_max': round(main.get('temp_max', 0), 1),
            'temp_min': round(main.get('temp_min', 0), 1),
            'icon': weather.get('icon', '01d')
        }

    def _extract_date_forecast(self, data: Dict, target_date: str) -> List[Dict]:
        """指定日付の予報データを抽出"""
        forecast_list = []

        for item in data.get('list', []):
            dt_txt = item.get('dt_txt', '')
            if dt_txt.startswith(target_date):
                main = item.get('main', {})
                weather = item.get('weather', [{}])[0]
                wind = item.get('wind', {})
                clouds = item.get('clouds', {})

                forecast_list.append({
                    'time': dt_txt.split(' ')[1][:5],  # HH:MM
                    'temperature': round(main.get('temp', 0), 1),
                    'description': weather.get('description', '不明'),
                    'humidity': main.get('humidity', 0),
                    'pressure': main.get('pressure', 0),
                    'wind_speed': wind.get('speed', 0),
                    'clouds': clouds.get('all', 0),
                    'pop': item.get('pop', 0) * 100,  # 降水確率
                    'icon': weather.get('icon', '01d')
                })

        return forecast_list

    def _get_mock_weather_data(self, location: str) -> Dict:
        """モック天気データ"""
        return {
            'location': location,
            'temperature': 22.5,
            'description': '晴れ',
            'humidity': 65,
            'pressure': 1013,
            'wind_speed': 3.2,
            'clouds': 25,
            'visibility': 10.0,
            'temp_max': 25.8,
            'temp_min': 18.3,
            'pop': 20,  # 降水確率を追加
            'icon': '01d'
        }

    def _get_mock_forecast_data(self, location: str, target_date: str) -> List[Dict]:
        """モック予報データ"""
        return [
            {
                'time': '09:00',
                'temperature': 20.5,
                'description': '晴れ',
                'humidity': 60,
                'pressure': 1015,
                'wind_speed': 2.8,
                'clouds': 15,
                'pop': 10,
                'icon': '01d'
            },
            {
                'time': '15:00',
                'temperature': 25.2,
                'description': '晴れ',
                'humidity': 55,
                'pressure': 1012,
                'wind_speed': 3.5,
                'clouds': 20,
                'pop': 5,
                'icon': '01d'
            },
            {
                'time': '21:00',
                'temperature': 18.7,
                'description': '晴れ',
                'humidity': 70,
                'pressure': 1016,
                'wind_speed': 2.1,
                'clouds': 10,
                'pop': 0,
                'icon': '01n'
            }
        ]

    def create_current_weather_flex(self, location: str, custom_title: str = None) -> Dict:
        """現在の天気情報Flex Messageを作成"""
        weather_data = self.get_current_weather(location)

        if not weather_data:
            return self._create_error_flex("天気情報の取得に失敗しました")

        return {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "20px",
                "backgroundColor": "#0367D3",
                "spacing": "md",
                "contents": [
                    {
                        "type": "text",
                        "text": f"🌤️ 現在の天気",
                        "color": "white",
                        "align": "center",
                        "size": "xl",
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": f"📍 {weather_data['location']}",
                        "color": "white",
                        "align": "center",
                        "size": "md"
                    },
                    {
                        "type": "text",
                        "text": datetime.now().strftime("%Y年%m月%d日 %H:%M"),
                        "color": "white",
                        "align": "center",
                        "size": "sm"
                    }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "20px",
                "spacing": "md",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 1,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "🌤 天気:",
                                        "size": "sm",
                                        "color": "#666666",
                                        "weight": "bold"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 2,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": str(weather_data['description']),
                                        "size": "sm",
                                        "wrap": True
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 1,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "🌡️ 気温:",
                                        "size": "sm",
                                        "color": "#666666",
                                        "weight": "bold"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 2,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": f"{weather_data['temperature']}°C",
                                        "size": "sm",
                                        "wrap": True
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 1,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "📊 最高/最低:",
                                        "size": "sm",
                                        "color": "#666666",
                                        "weight": "bold"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 2,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": f"{weather_data['temp_max']}°C / {weather_data['temp_min']}°C",
                                        "size": "sm",
                                        "wrap": True
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 1,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "💧 湿度:",
                                        "size": "sm",
                                        "color": "#666666",
                                        "weight": "bold"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 2,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": f"{weather_data['humidity']}%",
                                        "size": "sm",
                                        "wrap": True
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 1,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "☔ 降水確率:",
                                        "size": "sm",
                                        "color": "#666666",
                                        "weight": "bold"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 2,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": f"{weather_data.get('pop', 0)}%",
                                        "size": "sm",
                                        "wrap": True
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 1,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "💨 風速:",
                                        "size": "sm",
                                        "color": "#666666",
                                        "weight": "bold"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 2,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": f"{weather_data['wind_speed']} m/s",
                                        "size": "sm",
                                        "wrap": True
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 1,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "🌫️ 気圧:",
                                        "size": "sm",
                                        "color": "#666666",
                                        "weight": "bold"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 2,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": f"{weather_data['pressure']} hPa",
                                        "size": "sm",
                                        "wrap": True
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 1,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "👁️ 視程:",
                                        "size": "sm",
                                        "color": "#666666",
                                        "weight": "bold"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 2,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": f"{weather_data['visibility']} km",
                                        "size": "sm",
                                        "wrap": True
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 1,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "☁️ 雲量:",
                                        "size": "sm",
                                        "color": "#666666",
                                        "weight": "bold"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 2,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": f"{weather_data['clouds']}%",
                                        "size": "sm",
                                        "wrap": True
                                    }
                                ]
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
                        "margin": "lg",
                        "contents": [
                            {
                                "type": "text",
                                "text": "🌈 天気アドバイス",
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
                    }
                ]
            }
        }

    def create_forecast_flex(self, location: str, target_date: str, custom_title: str = None) -> Dict:
        """指定日の天気予報Flex Messageを作成"""
        forecast_data = self.get_forecast_by_date(location, target_date)

        if not forecast_data:
            return self._create_error_flex("天気予報の取得に失敗しました")

        # 日付をフォーマット
        try:
            date_obj = datetime.strptime(target_date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%Y年%m月%d日")
        except:
            formatted_date = target_date

        body_contents = [
            {
                "type": "text",
                "text": f"📅 {formatted_date}の天気予報",
                "size": "lg",
                "weight": "bold",
                "color": "#333333",
                "align": "center",
                "margin": "md"
            },
            {
                "type": "separator",
                "margin": "md"
            }
        ]

        # 各時間帯の予報を追加
        for i, forecast in enumerate(forecast_data):
            if i > 0:
                body_contents.append({
                    "type": "separator",
                    "margin": "md"
                })

            body_contents.extend([
                {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "margin": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"⏰ {forecast['time']}",
                            "size": "md",
                            "weight": "bold",
                            "color": "#0367D3"
                        }
                    ]
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "flex": 1,
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "🌤 天気:",
                                    "size": "sm",
                                    "color": "#666666",
                                    "weight": "bold"
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "flex": 2,
                            "contents": [
                                {
                                    "type": "text",
                                    "text": str(forecast['description']),
                                    "size": "sm",
                                    "wrap": True
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "flex": 1,
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "🌡️ 気温:",
                                    "size": "sm",
                                    "color": "#666666",
                                    "weight": "bold"
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "flex": 2,
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"{forecast['temperature']}°C",
                                    "size": "sm",
                                    "wrap": True
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "flex": 1,
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "💧 湿度:",
                                    "size": "sm",
                                    "color": "#666666",
                                    "weight": "bold"
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "flex": 2,
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"{forecast['humidity']}%",
                                    "size": "sm",
                                    "wrap": True
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "flex": 1,
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "💨 風速:",
                                    "size": "sm",
                                    "color": "#666666",
                                    "weight": "bold"
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "flex": 2,
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"{forecast['wind_speed']} m/s",
                                    "size": "sm",
                                    "wrap": True
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "flex": 1,
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "☔ 降水確率:",
                                    "size": "sm",
                                    "color": "#666666",
                                    "weight": "bold"
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "flex": 2,
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"{forecast['pop']:.0f}%",
                                    "size": "sm",
                                    "wrap": True
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "flex": 1,
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "🌫️ 気圧:",
                                    "size": "sm",
                                    "color": "#666666",
                                    "weight": "bold"
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "flex": 2,
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"{forecast['pressure']} hPa",
                                    "size": "sm",
                                    "wrap": True
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "flex": 1,
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "☁️ 雲量:",
                                    "size": "sm",
                                    "color": "#666666",
                                    "weight": "bold"
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "flex": 2,
                            "contents": [
                                {
                                    "type": "text",
                                    "text": f"{forecast['clouds']}%",
                                    "size": "sm",
                                    "wrap": True
                                }
                            ]
                        }
                    ]
                }
            ])

        # 天気アドバイスを追加
        body_contents.extend([
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
                        "text": "🌈 天気アドバイス",
                        "size": "md",
                        "weight": "bold",
                        "color": "#FF8C00",
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": self._get_forecast_advice(forecast_data),
                        "size": "sm",
                        "color": "#666666",
                        "align": "center",
                        "wrap": True
                    }
                ]
            }
        ])

        return {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "20px",
                "backgroundColor": "#0367D3",
                "spacing": "md",
                "contents": [
                    {
                        "type": "text",
                        "text": "📅 天気予報",
                        "color": "white",
                        "align": "center",
                        "size": "xl",
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": f"📍 {location}",
                        "color": "white",
                        "align": "center",
                        "size": "md"
                    }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "20px",
                "spacing": "md",
                "contents": body_contents
            }
        }

    def create_detailed_forecast_flex(self, location: str, target_date: str) -> Dict:
        """詳細天気予報Flex Messageを作成"""
        forecast_data = self.get_forecast_by_date(location, target_date)

        if not forecast_data:
            return self._create_error_flex("天気予報の取得に失敗しました")

        # 日付をフォーマット
        try:
            date_obj = datetime.strptime(target_date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%Y年%m月%d日")
            weekday = ["月", "火", "水", "木", "金", "土", "日"][date_obj.weekday()]
            formatted_date += f"({weekday})"
        except:
            formatted_date = target_date

        # 統計情報を計算
        temps = [f['temperature'] for f in forecast_data]
        humidities = [f['humidity'] for f in forecast_data]
        pops = [f['pop'] for f in forecast_data]

        avg_temp = sum(temps) / len(temps) if temps else 0
        max_temp = max(temps) if temps else 0
        min_temp = min(temps) if temps else 0
        avg_humidity = sum(humidities) / len(humidities) if humidities else 0
        max_pop = max(pops) if pops else 0

        return {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "20px",
                "backgroundColor": "#0367D3",
                "spacing": "md",
                "contents": [
                    {
                        "type": "text",
                        "text": "📊 詳細天気予報",
                        "color": "white",
                        "align": "center",
                        "size": "xl",
                        "weight": "bold"
                    },
                    {
                        "type": "text",
                        "text": f"📍 {location}",
                        "color": "white",
                        "align": "center",
                        "size": "md"
                    },
                    {
                        "type": "text",
                        "text": formatted_date,
                        "color": "white",
                        "align": "center",
                        "size": "sm"
                    }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "20px",
                "spacing": "md",
                "contents": [
                    {
                        "type": "text",
                        "text": "📈 1日の概要",
                        "size": "lg",
                        "weight": "bold",
                        "color": "#333333",
                        "margin": "md"
                    },
                    {
                        "type": "separator",
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "sm",
                        "margin": "md",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 1,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "🌡️ 平均気温:",
                                        "size": "sm",
                                        "color": "#666666",
                                        "weight": "bold"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 2,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": f"{avg_temp:.1f}°C",
                                        "size": "sm",
                                        "wrap": True
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 1,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "📊 最高/最低:",
                                        "size": "sm",
                                        "color": "#666666",
                                        "weight": "bold"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 2,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": f"{max_temp:.1f}°C / {min_temp:.1f}°C",
                                        "size": "sm",
                                        "wrap": True
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 1,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "💧 平均湿度:",
                                        "size": "sm",
                                        "color": "#666666",
                                        "weight": "bold"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 2,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": f"{avg_humidity:.0f}%",
                                        "size": "sm",
                                        "wrap": True
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 1,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "☔ 最大降水確率:",
                                        "size": "sm",
                                        "color": "#666666",
                                        "weight": "bold"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 2,
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": f"{max_pop:.0f}%",
                                        "size": "sm",
                                        "wrap": True
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
                        "type": "text",
                        "text": "⏰ 時間別詳細",
                        "size": "lg",
                        "weight": "bold",
                        "color": "#333333",
                        "margin": "md"
                    }
                ]
            }
        }

    def _get_weather_advice(self, weather_data: Dict) -> str:
        """天気に基づくアドバイスを生成"""
        temp = weather_data.get('temperature', 0)
        humidity = weather_data.get('humidity', 0)
        wind_speed = weather_data.get('wind_speed', 0)
        description = weather_data.get('description', '')

        advice = []

        # 気温に基づくアドバイス
        if temp >= 30:
            advice.append("🌡️ 暑いので水分補給を忘れずに")
        elif temp >= 25:
            advice.append("☀️ 暖かい陽気です")
        elif temp >= 15:
            advice.append("🌤️ 過ごしやすい気温です")
        elif temp >= 5:
            advice.append("🧥 軽めの上着があると良いでしょう")
        else:
            advice.append("🧥 防寒対策をしっかりと")

        # 湿度に基づくアドバイス
        if humidity >= 80:
            advice.append("💧 湿度が高めです")
        elif humidity <= 30:
            advice.append("🌵 乾燥しています、水分補給を")

        # 風速に基づくアドバイス
        if wind_speed >= 10:
            advice.append("💨 風が強いのでご注意を")

        # 天気に基づくアドバイス
        if '雨' in description:
            advice.append("☔ 雨の予報です、傘をお忘れなく")
        elif '雪' in description:
            advice.append("❄️ 雪の予報です、足元にご注意を")

        return "・".join(advice) if advice else "良い天気をお楽しみください！"

    def _get_forecast_advice(self, forecast_data: List[Dict]) -> str:
        """予報データに基づくアドバイスを生成"""
        if not forecast_data:
            return "予報データがありません"

        max_pop = max([f.get('pop', 0) for f in forecast_data])
        temps = [f.get('temperature', 0) for f in forecast_data]
        max_temp = max(temps) if temps else 0
        min_temp = min(temps) if temps else 0

        advice = []

        # 降水確率に基づくアドバイス
        if max_pop >= 70:
            advice.append("☔ 雨の可能性が高いです、傘をお持ちください")
        elif max_pop >= 30:
            advice.append("🌦️ 雨の可能性があります、折りたたみ傘があると安心")

        # 気温変化に基づくアドバイス
        temp_diff = max_temp - min_temp
        if temp_diff >= 10:
            advice.append("🌡️ 気温差が大きいです、調節しやすい服装を")

        if max_temp >= 30:
            advice.append("🌡️ 暑くなりそうです、水分補給をお忘れなく")
        elif min_temp <= 5:
            advice.append("🧥 冷え込みそうです、暖かい服装を")

        return "・".join(advice) if advice else "快適な一日になりそうです！"

    def _create_error_flex(self, error_message: str) -> Dict:
        """エラー用Flex Messageを作成"""
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "20px",
                "spacing": "md",
                "contents": [
                    {
                        "type": "text",
                        "text": "❌ エラー",
                        "size": "xl",
                        "weight": "bold",
                        "color": "#FF0000",
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": error_message,
                        "size": "md",
                        "color": "#666666",
                        "align": "center",
                        "wrap": True,
                        "margin": "md"
                    }
                ]
            }
        }

# テスト用の実行部分
if __name__ == "__main__":
    template = WeatherFlexTemplate()

    # 現在の天気をテスト
    current_flex = template.create_current_weather_flex("Tokyo,JP")
    print("=== 現在の天気 Flex Message ===")
    print(json.dumps(current_flex, ensure_ascii=False, indent=2))

    # 明日の天気予報をテスト
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    forecast_flex = template.create_forecast_flex("Tokyo,JP", tomorrow)
    print(f"\n=== {tomorrow} 天気予報 Flex Message ===")
    print(json.dumps(forecast_flex, ensure_ascii=False, indent=2))
