#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
リマインダーメッセージ強化システム
丁寧なメッセージ生成と天気情報統合
"""

import os
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# プロジェクトルート設定
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class EnhancedReminderMessageGenerator:
    """拡張リマインダーメッセージ生成クラス"""

    def __init__(self):
        """初期化"""
        self.weather_cache = {}
        self.message_templates = self._load_message_templates()

    def _load_message_templates(self) -> Dict:
        """メッセージテンプレートを読み込み"""
        return {
            "greeting": {
                "morning": "おはようございます。",
                "afternoon": "お疲れ様です。",
                "evening": "お疲れ様です。"
            },
            "polite_phrases": {
                "request_start": "お忙しい中恐れ入りますが、",
                "request_confirm": "ご都合の確認をお願いいたします。",
                "request_input": "ご入力をお願いいたします。",
                "thank_you": "ご協力ありがとうございます。",
                "end_formal": "よろしくお願いいたします。",
                "apology": "お忙しいところ申し訳ございません。"
            },
            "weather_intro": {
                "outdoor": "当日の天気情報もお知らせいたします。",
                "indoor": "屋内開催ですが、移動時の天気情報をお知らせいたします。",
                "general": "天気情報もあわせてご確認ください。"
            },
            "urgency_levels": {
                "high": {
                    "prefix": "🚨 【緊急】",
                    "tone": "至急のご案内",
                    "color": "#FF0000"
                },
                "medium": {
                    "prefix": "⏰ 【重要】",
                    "tone": "重要なお知らせ",
                    "color": "#FF8C00"
                },
                "low": {
                    "prefix": "📅",
                    "tone": "ご案内",
                    "color": "#4169E1"
                }
            }
        }

    def _get_greeting_by_time(self) -> str:
        """時間帯に応じた挨拶を取得"""
        current_hour = datetime.now().hour

        if 5 <= current_hour < 12:
            return self.message_templates["greeting"]["morning"]
        elif 12 <= current_hour < 18:
            return self.message_templates["greeting"]["afternoon"]
        else:
            return self.message_templates["greeting"]["evening"]

    def _determine_urgency_level(self, days_until: int, is_input_deadline: bool) -> str:
        """緊急度レベルを判定"""
        if days_until == 0:
            return "high"
        elif days_until == 1:
            return "medium" if is_input_deadline else "medium"
        else:
            return "low"

    def _extract_event_type(self, content: str) -> str:
        """イベントタイプを抽出"""
        content_lower = content.lower()

        # 屋外イベントキーワード
        outdoor_keywords = ["試合", "練習", "グラウンド", "球場", "競技場", "公園", "屋外"]
        # 屋内イベントキーワード
        indoor_keywords = ["会議", "ミーティング", "体育館", "教室", "会議室", "屋内"]

        for keyword in outdoor_keywords:
            if keyword in content:
                return "outdoor"

        for keyword in indoor_keywords:
            if keyword in content:
                return "indoor"

        return "general"

    def _get_weather_info(self, event_date: datetime, event_content: str) -> str:
        """天気情報を取得（OpenWeatherMap API使用）"""
        try:
            # 会場情報を抽出
            location = self._extract_location_from_event(event_content)
            venue_name = self._extract_venue_name(event_content)

            # イベントまでの日数を計算
            if hasattr(event_date, 'date'):  # datetime オブジェクトの場合
                days_until = (event_date.date() - datetime.now().date()).days
            else:  # date オブジェクトの場合
                days_until = (event_date - datetime.now().date()).days

            # OpenWeatherMap API を使用して天気情報を取得
            from openweather_service import get_weather_for_location

            weather_data = get_weather_for_location(location, venue_name, days_until)

            if weather_data:
                return self._format_openweather_data(weather_data, location, venue_name)
            else:
                return self._get_detailed_fallback_weather_message(location, event_date)

        except Exception as e:
            print(f"[WEATHER] エラー: {e}")
            location = self._extract_location_from_event(event_content)
            return self._get_detailed_fallback_weather_message(location, event_date)

    def _extract_venue_name(self, event_content: str) -> str:
        """イベント内容から会場名を抽出"""
        try:
            lines = event_content.split('\n')
            for line in lines:
                # 会場、場所、開催地などのキーワードを含む行を探す
                if any(keyword in line for keyword in ['会場', '場所', '開催地', '集合場所', 'venue', 'place']):
                    # コロンの後の部分を抽出
                    if ':' in line:
                        return line.split(':', 1)[1].strip()
                    elif '：' in line:
                        return line.split('：', 1)[1].strip()

            # 特定の会場名を直接検索
            venue_keywords = [
                "代々木公園", "新宿", "渋谷", "池袋", "品川", "東京ドーム",
                "横浜", "大阪城", "京都", "名古屋", "福岡", "札幌"
            ]

            for keyword in venue_keywords:
                if keyword in event_content:
                    return keyword

            return ""

        except Exception:
            return ""

    def _format_openweather_data(self, weather_data: Dict, location: str, venue_name: str) -> str:
        """OpenWeatherMap データをリマインダー用にフォーマット"""
        try:
            weather_info = f"🌤️ **{location}の詳細天気情報**"
            if venue_name:
                weather_info += f"（{venue_name}周辺）"
            weather_info += "\n\n"

            # 開催場所の詳細表示
            weather_info += f"📍 **開催場所**: {venue_name if venue_name else location}\n"
            weather_info += f"🗺️ **対象地域**: {location}\n\n"

            # 現在の天気か予報かで分岐
            if "timestamp" in weather_data:  # 現在の天気
                weather_info += f"🌡️ **現在の気温**: {weather_data['temperature']}°C"
                if weather_data.get('feels_like'):
                    weather_info += f" (体感: {weather_data['feels_like']}°C)"
                weather_info += "\n"

                weather_info += f"💧 **湿度**: {weather_data['humidity']}%\n"
                weather_info += f"💨 **風速**: {weather_data['wind_speed']}km/h\n"

                if weather_data.get('visibility'):
                    weather_info += f"👁️ **視界**: {weather_data['visibility']}km\n"

                weather_info += f"☁️ **天気**: {weather_data['description']}\n"

                # 降雨情報
                if weather_data.get('rain', 0) > 0:
                    weather_info += f"☔ **降雨量**: {weather_data['rain']}mm/h\n"

            else:  # 予報
                weather_info += f"🌡️ **予想気温**: {weather_data['average_temperature']}°C "
                weather_info += f"(最高: {weather_data['max_temperature']}°C / 最低: {weather_data['min_temperature']}°C)\n"

                weather_info += f"💧 **湿度**: {weather_data['humidity']}%\n"
                weather_info += f"💨 **風速**: {weather_data['wind_speed']}km/h\n"
                weather_info += f"☔ **降水確率**: {weather_data['rain_probability']}%\n"
                weather_info += f"☁️ **天気**: {weather_data['description']}\n"

            # データ提供元と引用元
            weather_info += f"\n� **データ提供**: OpenWeatherMap API\n"
            weather_info += f"� **引用元**: https://openweathermap.org/\n"
            weather_info += f"�📅 **取得日時**: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}\n"

            # API使用状況の表示
            if weather_data.get('is_mock_data', False):
                weather_info += f"⚠️ **注意**: 現在はテスト用データを表示しています。\n"
                weather_info += f"正確な天気情報には OpenWeatherMap API キーの設定が必要です。\n"

            # 特別な注意喚起
            alert_message = self._get_weather_alert(weather_data)
            if alert_message:
                weather_info += f"\n⚠️ **注意**: {alert_message}\n"

            return weather_info

        except Exception as e:
            print(f"[FORMAT_OPENWEATHER] エラー: {e}")
            return self._get_detailed_fallback_weather_message(location, datetime.now())

    def _get_weather_alert(self, weather_data: Dict) -> str:
        """天気に応じた注意喚起メッセージ"""
        alerts = []

        # 雨の警告
        rain_prob = weather_data.get('rain_probability', 0)
        rain_amount = weather_data.get('rain', 0)

        if rain_prob >= 70 or rain_amount > 1:
            alerts.append("🌧️ 雨の可能性が高いです。傘を忘れずに！")
        elif rain_prob >= 40:
            alerts.append("☂️ 雨が降る可能性があります。折りたたみ傘があると安心です。")

        # 風の警告
        wind_speed = weather_data.get('wind_speed', 0)
        if wind_speed > 25:
            alerts.append("💨 風が強いです。帽子や軽いものが飛ばされないよう注意してください。")
        elif wind_speed > 15:
            alerts.append("🌪️ やや風が強めです。屋外活動では注意が必要です。")

        # 気温の警告
        temp = weather_data.get('temperature') or weather_data.get('average_temperature', 20)
        if temp >= 30:
            alerts.append("🌡️ 暑いです。熱中症対策と水分補給をお忘れなく！")
        elif temp <= 5:
            alerts.append("❄️ 寒いです。防寒対策をしっかりと！")

        # 湿度の警告
        humidity = weather_data.get('humidity', 50)
        if humidity >= 85:
            alerts.append("💧 湿度が高いです。蒸し暑く感じられるかもしれません。")
        elif humidity <= 30:
            alerts.append("🏜️ 乾燥しています。のどの保湿や静電気にご注意ください。")

        return " ".join(alerts)

    def create_weather_flex_message(self, weather_data: Dict, location: str, venue_name: str) -> Dict:
        """天気情報をFlex Messageカードで作成"""
        try:
            # 基本色の設定
            main_color = self._get_weather_color(weather_data)

            # アイコンと背景色を決定
            weather_icon, bg_color = self._get_weather_icon_and_color(weather_data)

            # 気温表示
            if "timestamp" in weather_data:  # 現在の天気
                temp_text = f"{weather_data['temperature']}°C"
                feels_like = weather_data.get('feels_like')
                if feels_like:
                    temp_text += f"\n体感 {feels_like}°C"
            else:  # 予報
                temp_text = f"{weather_data['average_temperature']}°C"
                temp_text += f"\n{weather_data['min_temperature']}° - {weather_data['max_temperature']}°"

            # 降水確率
            rain_prob = weather_data.get('rain_probability', 0)
            rain_text = f"{rain_prob}%"

            # 風速
            wind_speed = weather_data.get('wind_speed', 0)
            wind_text = f"{wind_speed}km/h"

            # 湿度
            humidity = weather_data.get('humidity', 50)
            humidity_text = f"{humidity}%"

            # 天気の状況説明
            description = weather_data.get('description', '天気情報取得中')

            # 特別なメッセージ
            alert_message = self._get_weather_alert(weather_data)

            # Flex Message の構築
            flex_message = {
                "type": "flex",
                "altText": f"{location}の天気情報",
                "contents": {
                    "type": "bubble",
                    "styles": {
                        "header": {"backgroundColor": bg_color},
                        "body": {"backgroundColor": "#f8f9fa"}
                    },
                    "header": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": weather_icon,
                                "size": "xxl",
                                "align": "center",
                                "margin": "sm"
                            },
                            {
                                "type": "text",
                                "text": location,
                                "weight": "bold",
                                "size": "lg",
                                "align": "center",
                                "color": "#ffffff"
                            }
                        ],
                        "paddingTop": "15px",
                        "paddingBottom": "15px"
                    },
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            # 開催場所の詳細表示
                            *([{
                                "type": "text",
                                "text": f"📍 開催場所: {venue_name}",
                                "size": "sm",
                                "color": "#666666",
                                "margin": "none",
                                "wrap": True,
                                "weight": "bold"
                            }, {
                                "type": "text",
                                "text": f"🗺️ 対象地域: {location}",
                                "size": "xs",
                                "color": "#999999",
                                "margin": "xs",
                                "wrap": True
                            }, {
                                "type": "separator",
                                "margin": "md"
                            }] if venue_name else [{
                                "type": "text",
                                "text": f"🗺️ 対象地域: {location}",
                                "size": "sm",
                                "color": "#666666",
                                "margin": "none",
                                "wrap": True
                            }, {
                                "type": "separator",
                                "margin": "md"
                            }]),

                            # 天気の説明
                            {
                                "type": "text",
                                "text": description,
                                "size": "md",
                                "align": "center",
                                "margin": "md",
                                "weight": "bold",
                                "color": main_color
                            },
                            {
                                "type": "separator",
                                "margin": "lg"
                            },

                            # 天気情報カード部分
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "horizontal",
                                        "contents": [
                                            # 気温カード
                                            {
                                                "type": "box",
                                                "layout": "vertical",
                                                "contents": [
                                                    {
                                                        "type": "text",
                                                        "text": "🌡️",
                                                        "size": "lg",
                                                        "align": "center"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "text": "気温",
                                                        "size": "xs",
                                                        "align": "center",
                                                        "color": "#666666",
                                                        "margin": "xs"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "text": temp_text,
                                                        "size": "sm",
                                                        "align": "center",
                                                        "weight": "bold",
                                                        "margin": "xs"
                                                    }
                                                ],
                                                "flex": 1,
                                                "backgroundColor": "#ffffff",
                                                "cornerRadius": "8px",
                                                "paddingAll": "8px",
                                                "margin": "xs"
                                            },

                                            # 湿度カード
                                            {
                                                "type": "box",
                                                "layout": "vertical",
                                                "contents": [
                                                    {
                                                        "type": "text",
                                                        "text": "💧",
                                                        "size": "lg",
                                                        "align": "center"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "text": "湿度",
                                                        "size": "xs",
                                                        "align": "center",
                                                        "color": "#666666",
                                                        "margin": "xs"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "text": humidity_text,
                                                        "size": "sm",
                                                        "align": "center",
                                                        "weight": "bold",
                                                        "margin": "xs"
                                                    }
                                                ],
                                                "flex": 1,
                                                "backgroundColor": "#ffffff",
                                                "cornerRadius": "8px",
                                                "paddingAll": "8px",
                                                "margin": "xs"
                                            }
                                        ]
                                    },

                                    # 下段カード
                                    {
                                        "type": "box",
                                        "layout": "horizontal",
                                        "contents": [
                                            # 降水確率カード
                                            {
                                                "type": "box",
                                                "layout": "vertical",
                                                "contents": [
                                                    {
                                                        "type": "text",
                                                        "text": "☔",
                                                        "size": "lg",
                                                        "align": "center"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "text": "降水確率",
                                                        "size": "xs",
                                                        "align": "center",
                                                        "color": "#666666",
                                                        "margin": "xs"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "text": rain_text,
                                                        "size": "sm",
                                                        "align": "center",
                                                        "weight": "bold",
                                                        "margin": "xs"
                                                    }
                                                ],
                                                "flex": 1,
                                                "backgroundColor": "#ffffff",
                                                "cornerRadius": "8px",
                                                "paddingAll": "8px",
                                                "margin": "xs"
                                            },

                                            # 風速カード
                                            {
                                                "type": "box",
                                                "layout": "vertical",
                                                "contents": [
                                                    {
                                                        "type": "text",
                                                        "text": "💨",
                                                        "size": "lg",
                                                        "align": "center"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "text": "風速",
                                                        "size": "xs",
                                                        "align": "center",
                                                        "color": "#666666",
                                                        "margin": "xs"
                                                    },
                                                    {
                                                        "type": "text",
                                                        "text": wind_text,
                                                        "size": "sm",
                                                        "align": "center",
                                                        "weight": "bold",
                                                        "margin": "xs"
                                                    }
                                                ],
                                                "flex": 1,
                                                "backgroundColor": "#ffffff",
                                                "cornerRadius": "8px",
                                                "paddingAll": "8px",
                                                "margin": "xs"
                                            }
                                        ],
                                        "margin": "sm"
                                    }
                                ]
                            },

                            # 注意メッセージ（あれば）
                            *([{
                                "type": "separator",
                                "margin": "lg"
                            }, {
                                "type": "text",
                                "text": alert_message,
                                "size": "sm",
                                "color": "#ff6b6b",
                                "wrap": True,
                                "margin": "md",
                                "weight": "bold"
                            }] if alert_message else [])
                        ]
                    },
                    "footer": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": f"📅 {datetime.now().strftime('%Y年%m月%d日 %H:%M')}",
                                "size": "xs",
                                "color": "#999999",
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": "🌐 OpenWeatherMap API",
                                "size": "xs",
                                "color": "#999999",
                                "align": "center",
                                "margin": "xs"
                            },
                            *([{
                                "type": "text",
                                "text": "⚠️ テスト用データ",
                                "size": "xs",
                                "color": "#ff6b6b",
                                "align": "center",
                                "margin": "xs"
                            }] if weather_data.get('is_mock_data', False) else [])
                        ],
                        "paddingTop": "10px",
                        "paddingBottom": "10px"
                    }
                }
            }

            return flex_message

        except Exception as e:
            print(f"[FLEX_MESSAGE] エラー: {e}")
            return self._create_fallback_flex_message(location, venue_name)

    def _get_weather_color(self, weather_data: Dict) -> str:
        """天気に応じたテーマカラーを取得"""
        description = weather_data.get('description', '').lower()
        main = weather_data.get('main', '').lower()

        if '晴' in description or 'clear' in main:
            return "#ff9500"  # オレンジ
        elif '雨' in description or 'rain' in main:
            return "#007aff"  # ブルー
        elif '雪' in description or 'snow' in main:
            return "#5ac8fa"  # ライトブルー
        elif '曇' in description or 'cloud' in main:
            return "#8e8e93"  # グレー
        else:
            return "#34c759"  # グリーン

    def _get_weather_icon_and_color(self, weather_data: Dict) -> tuple:
        """天気に応じたアイコンと背景色を取得"""
        description = weather_data.get('description', '').lower()
        main = weather_data.get('main', '').lower()

        if '晴' in description or 'clear' in main:
            return "☀️", "#ff9500"
        elif '雨' in description or 'rain' in main:
            return "🌧️", "#007aff"
        elif '雪' in description or 'snow' in main:
            return "❄️", "#5ac8fa"
        elif '曇' in description or 'cloud' in main:
            return "☁️", "#8e8e93"
        elif '雷' in description or 'thunder' in main:
            return "⛈️", "#af52de"
        else:
            return "🌤️", "#34c759"

    def _create_fallback_flex_message(self, location: str, venue_name: str) -> Dict:
        """フォールバック用のシンプルなFlex Message"""
        return {
            "type": "flex",
            "altText": f"{location}の天気情報",
            "contents": {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"🌤️ {location}の天気",
                            "weight": "bold",
                            "size": "lg",
                            "align": "center"
                        },
                        {
                            "type": "text",
                            "text": "天気情報を取得中です...",
                            "size": "sm",
                            "align": "center",
                            "margin": "md",
                            "color": "#666666"
                        }
                    ]
                }
            }
        }

    def _extract_location_from_event(self, event_content: str) -> str:
        """イベント内容から会場情報を抽出"""
        try:
            # 会場キーワードを探す
            location_keywords = {
                "代々木公園": "東京都",
                "新宿": "東京都",
                "渋谷": "東京都",
                "池袋": "東京都",
                "品川": "東京都",
                "大阪": "大阪府",
                "名古屋": "愛知県",
                "福岡": "福岡県",
                "札幌": "北海道",
                "横浜": "神奈川県",
                "千葉": "千葉県",
                "さいたま": "埼玉県"
            }

            content_lower = event_content.lower()

            for location, prefecture in location_keywords.items():
                if location in event_content:
                    return prefecture

            # デフォルトは東京都
            return "東京都"

        except Exception:
            return "東京都"

    def _get_detailed_weather_forecast(self, location: str, event_date: datetime, event_content: str) -> str:
        """詳細な天気予報を取得"""
        try:
            import requests
            from bs4 import BeautifulSoup
            import re

            # MSN天気予報URLを生成
            location_urls = {
                "東京都": "https://www.msn.com/ja-jp/weather/forecast/in-東京都,大田区?weadegreetype=C",
                "大阪府": "https://www.msn.com/ja-jp/weather/forecast/in-大阪府,大阪市?weadegreetype=C",
                "愛知県": "https://www.msn.com/ja-jp/weather/forecast/in-愛知県,名古屋市?weadegreetype=C",
                "福岡県": "https://www.msn.com/ja-jp/weather/forecast/in-福岡県,福岡市?weadegreetype=C",
                "北海道": "https://www.msn.com/ja-jp/weather/forecast/in-北海道,札幌市?weadegreetype=C",
            }

            url = location_urls.get(location, location_urls["東京都"])

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # 詳細な天気情報を構築
            weather_details = []

            # 現在の気温を取得
            temp_current = self._extract_current_temperature(soup)
            if temp_current:
                weather_details.append(f"🌡️ 現在の気温: {temp_current}")

            # 最高・最低気温を取得
            temp_range = self._extract_temperature_range(soup)
            if temp_range:
                weather_details.append(f"📊 気温範囲: {temp_range}")

            # 天気概況を取得
            condition = self._extract_weather_condition(soup)
            if condition:
                weather_details.append(f"☁️ 天気: {condition}")

            # 降水確率を取得
            precipitation = self._extract_precipitation(soup)
            if precipitation:
                weather_details.append(f"☔ 降水確率: {precipitation}")

            # 風の情報を取得
            wind_info = self._extract_wind_info(soup)
            if wind_info:
                weather_details.append(f"💨 風: {wind_info}")

            # 湿度を取得
            humidity = self._extract_humidity(soup)
            if humidity:
                weather_details.append(f"💧 湿度: {humidity}")

            if weather_details:
                result = f"🌤️ **{location}の詳細天気情報**\n\n"
                result += "\n".join(weather_details)
                result += f"\n\n📍 データ提供: MSN天気予報"
                result += f"\n📅 情報取得日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}"
                return result
            else:
                return ""

        except Exception as e:
            print(f"[DETAILED_WEATHER] エラー: {e}")
            return ""

    def _extract_current_temperature(self, soup) -> str:
        """現在の気温を抽出"""
        try:
            # 複数のセレクタを試す
            selectors = [
                'span.c-temperature',
                '.current-temp',
                '[data-testid="temperature"]',
                '.temperature-value'
            ]

            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    temp_text = elements[0].get_text(strip=True)
                    if '°' in temp_text or '℃' in temp_text:
                        return temp_text

            # 正規表現での検索
            temp_pattern = re.compile(r'(\d+)\s*[°℃]C?')
            for element in soup.find_all(text=temp_pattern):
                match = temp_pattern.search(str(element))
                if match:
                    return f"{match.group(1)}°C"

            return ""
        except Exception:
            return ""

    def _extract_temperature_range(self, soup) -> str:
        """気温範囲を抽出"""
        try:
            # 最高・最低気温の抽出
            temp_elements = soup.find_all(text=re.compile(r'\d+°|最高|最低'))
            temperatures = []

            for element in temp_elements:
                temp_match = re.search(r'(\d+)°', str(element))
                if temp_match:
                    temperatures.append(int(temp_match.group(1)))

            if len(temperatures) >= 2:
                max_temp = max(temperatures)
                min_temp = min(temperatures)
                return f"最高{max_temp}°C / 最低{min_temp}°C"

            return ""
        except Exception:
            return ""

    def _extract_weather_condition(self, soup) -> str:
        """天気概況を抽出"""
        try:
            # 天気状況のキーワード
            weather_keywords = ['晴れ', '曇り', '雨', '雪', '快晴', '晴時々曇', '曇時々雨', 'Clear', 'Cloudy', 'Rainy', 'Sunny']

            for element in soup.find_all(text=re.compile('|'.join(weather_keywords))):
                text = str(element).strip()
                for keyword in weather_keywords:
                    if keyword in text:
                        return text

            return ""
        except Exception:
            return ""

    def _extract_precipitation(self, soup) -> str:
        """降水確率を抽出"""
        try:
            precip_elements = soup.find_all(text=re.compile(r'\d+%'))
            precip_values = []

            for element in precip_elements:
                match = re.search(r'(\d+)%', str(element))
                if match:
                    precip_values.append(int(match.group(1)))

            if precip_values:
                max_precip = max(precip_values)
                return f"{max_precip}%"

            return ""
        except Exception:
            return ""

    def _extract_wind_info(self, soup) -> str:
        """風の情報を抽出"""
        try:
            wind_elements = soup.find_all(text=re.compile(r'風|km/h|m/s|\d+\s*(km/h|m/s)'))

            for element in wind_elements[:3]:
                text = str(element).strip()
                if 'km/h' in text or 'm/s' in text:
                    # 風速の数値を抽出
                    wind_match = re.search(r'(\d+)\s*(km/h|m/s)', text)
                    if wind_match:
                        return f"{wind_match.group(1)}{wind_match.group(2)}"

            return ""
        except Exception:
            return ""

    def _extract_humidity(self, soup) -> str:
        """湿度を抽出"""
        try:
            humidity_elements = soup.find_all(text=re.compile(r'\d+%.*湿度|湿度.*\d+%'))

            for element in humidity_elements:
                humidity_match = re.search(r'(\d+)%', str(element))
                if humidity_match and '湿度' in str(element):
                    return f"{humidity_match.group(1)}%"

            return ""
        except Exception:
            return ""

    def _get_detailed_fallback_weather_message(self, location: str, event_date: datetime) -> str:
        """詳細なフォールバック天気メッセージ"""
        try:
            # 季節に応じたアドバイス
            month = event_date.month
            season_advice = self._get_seasonal_advice(month)

            return f"""🌤️ **{location}の天気情報**

📅 **イベント日**: {event_date.strftime('%Y年%m月%d日')}
📍 **地域**: {location}

⚠️ **リアルタイム天気情報の取得について**
申し訳ございませんが、現在詳細な天気情報を自動で取得できない状況です。

💡 **おすすめの確認方法**
以下の方法で最新の天気予報をご確認ください：

📱 **スマートフォンアプリ**
• Yahoo!天気 / ウェザーニュース
• NHK あなたの天気・防災

🌐 **ウェブサイト**
• 気象庁 (jma.go.jp)
• 日本気象協会 tenki.jp

{season_advice}

🎯 **イベント当日の準備**
• 前日夜または当日朝に最新の天気予報を確認
• 雨の可能性がある場合は傘やレインウェアを準備
• 気温に応じた適切な服装を選択

📞 **緊急時の連絡**
天候による開催可否の判断については、
主催者からの連絡をお待ちください。"""

        except Exception:
            return self._get_fallback_weather_message()

    def _get_seasonal_advice(self, month: int) -> str:
        """季節に応じたアドバイス"""
        if month in [12, 1, 2]:  # 冬
            return """❄️ **冬季のアドバイス**
• 防寒対策をしっかりと
• 路面凍結に注意
• マフラーや手袋の準備"""
        elif month in [3, 4, 5]:  # 春
            return """🌸 **春季のアドバイス**
• 気温の変化に注意
• 花粉症対策をお忘れなく
• 薄手の上着があると安心"""
        elif month in [6, 7, 8]:  # 夏
            return """☀️ **夏季のアドバイス**
• 熱中症対策が重要
• こまめな水分補給を
• 日焼け止めや帽子を準備"""
        else:  # 秋
            return """🍂 **秋季のアドバイス**
• 朝晩の気温差に注意
• 長袖の準備をおすすめ
• 台風情報にもご注意を"""

    def _format_weather_for_reminder(self, weather_info: str) -> str:
        """天気情報をリマインダー用にフォーマット（改良版）"""
        try:
            # 既に詳細フォーマットされている場合はそのまま返す
            if "詳細天気情報" in weather_info:
                # 服装提案を追加
                weather_info += "\n\n💡 **服装のご提案**\n"
                weather_info += self._get_clothing_suggestion(weather_info)
                return weather_info

            # 天気情報から重要な部分を抽出
            lines = weather_info.split('\n')
            formatted_weather = "🌤️ **当日の天気情報**\n\n"

            important_lines = []
            weather_data = {}

            for line in lines:
                clean_line = line.replace('**', '').replace('*', '').strip()

                # 重要な情報を分類して抽出
                if any(keyword in line for keyword in ['現在の気温', '気温']):
                    weather_data['temperature'] = clean_line
                elif '天気' in line and not clean_line.startswith('🔗'):
                    weather_data['condition'] = clean_line
                elif '降水確率' in line:
                    weather_data['precipitation'] = clean_line
                elif '風' in line and ('km/h' in line or 'm/s' in line):
                    weather_data['wind'] = clean_line
                elif '湿度' in line:
                    weather_data['humidity'] = clean_line
                elif any(keyword in line for keyword in ['最高', '最低', '気温範囲']):
                    weather_data['temp_range'] = clean_line

            # 優先順位に従って情報を表示
            priority_order = ['condition', 'temperature', 'temp_range', 'precipitation', 'wind', 'humidity']

            for key in priority_order:
                if key in weather_data:
                    formatted_weather += f"{weather_data[key]}\n"

            # 追加情報があれば表示
            for line in lines:
                if ('データ提供' in line or '情報取得日時' in line) and not any(line in weather_data.values()):
                    formatted_weather += f"\n{line.strip()}\n"

            # 情報が不足している場合のメッセージ
            if len(weather_data) == 0:
                formatted_weather += "詳細な天気予報は以下でご確認ください：\n"
                formatted_weather += "📱 Yahoo!天気 / ウェザーニュース\n"
                formatted_weather += "🌐 気象庁 (jma.go.jp)\n"

            # 服装提案を追加
            formatted_weather += "\n💡 **服装のご提案**\n"
            formatted_weather += self._get_clothing_suggestion(weather_info)

            return formatted_weather

        except Exception as e:
            print(f"[WEATHER_FORMAT] エラー: {e}")
            return self._get_fallback_weather_message()

    def _get_clothing_suggestion(self, weather_info: str) -> str:
        """天気に基づく服装提案（詳細版）"""
        try:
            suggestions = []

            # 気温を抽出
            temp_matches = re.findall(r'(\d+)°C?', weather_info)
            temperatures = [int(match) for match in temp_matches]

            if temperatures:
                avg_temp = sum(temperatures) / len(temperatures)
                max_temp = max(temperatures)
                min_temp = min(temperatures)

                # 基本的な服装提案
                if max_temp >= 30:
                    suggestions.append("🌡️ 非常に暑いです。薄着で、帽子と日焼け止めが必須です。")
                    suggestions.append("💧 こまめな水分補給と休憩を心がけてください。")
                elif max_temp >= 25:
                    suggestions.append("☀️ 暑いので軽装で。Tシャツやポロシャツがおすすめです。")
                    suggestions.append("🧢 帽子と水分補給をお忘れなく。")
                elif max_temp >= 20:
                    suggestions.append("🌤️ 過ごしやすい気温です。長袖シャツや薄手のトップスで。")
                elif max_temp >= 15:
                    suggestions.append("🧥 少し涼しいです。薄手のカーディガンやライトジャケットを。")
                elif max_temp >= 10:
                    suggestions.append("🧥 肌寒いです。セーターやジャケットをおすすめします。")
                else:
                    suggestions.append("🧣 寒いです。コート、マフラー、手袋で防寒対策を。")

                # 気温差が大きい場合の提案
                if max_temp - min_temp > 10:
                    suggestions.append("📊 気温差が大きいです。重ね着で調節できる服装を。")

            # 降水確率をチェック
            precip_matches = re.findall(r'(\d+)%', weather_info)
            if precip_matches:
                precip_values = [int(match) for match in precip_matches]
                max_precip = max(precip_values)

                if max_precip >= 70:
                    suggestions.append("☔ 雨の可能性が高いです。傘とレインウェアを必ず持参。")
                elif max_precip >= 40:
                    suggestions.append("🌦️ 雨の可能性があります。折りたたみ傘を持参がおすすめ。")
                elif max_precip >= 20:
                    suggestions.append("☁️ 曇りがちです。念のため傘があると安心です。")

            # 風の情報をチェック
            if '風' in weather_info:
                wind_match = re.search(r'(\d+)\s*(km/h|m/s)', weather_info)
                if wind_match:
                    wind_speed = int(wind_match.group(1))
                    unit = wind_match.group(2)

                    # km/hをm/sに変換（必要に応じて）
                    if unit == 'km/h' and wind_speed > 20:
                        suggestions.append("💨 風が強めです。帽子やスカートは飛ばされないよう注意。")
                    elif unit == 'm/s' and wind_speed > 5:
                        suggestions.append("💨 風が強いです。しっかりした服装と帽子の固定をお願いします。")

            # 基本的なアドバイスを追加（情報が少ない場合）
            if not suggestions:
                suggestions.append("天気に適した服装でお越しください。")
                suggestions.append("前日または当日朝に最新の天気予報をご確認ください。")

            return "\n".join(suggestions)

        except Exception as e:
            print(f"[CLOTHING_SUGGESTION] エラー: {e}")
            return "天気に適した服装でお越しください。体調管理にお気をつけください。"

    def _get_fallback_weather_message(self) -> str:
        """フォールバック天気メッセージ（改良版）"""
        current_date = datetime.now()
        season_advice = self._get_seasonal_advice(current_date.month)

        return f"""🌤️ **天気情報のご案内**

⚠️ **リアルタイム天気情報について**
申し訳ございませんが、現在自動での天気情報取得ができません。
イベント当日の天気は以下で最新情報をご確認ください。

💡 **おすすめの天気予報サイト・アプリ**
📱 **スマートフォンアプリ**
• Yahoo!天気・災害
• ウェザーニュース
• NHK あなたの天気・防災

🌐 **ウェブサイト**
• 気象庁 (jma.go.jp)
• 日本気象協会 tenki.jp
• MSN天気

{season_advice}

🎯 **イベント当日の準備チェックリスト**
□ 前日夜または当日朝に天気予報を確認
□ 雨の可能性がある場合は傘を準備
□ 気温に応じた適切な服装を選択
□ 屋外イベントの場合は日焼け止めや帽子も検討

📞 **天候による開催判断について**
悪天候の場合の開催可否については、
主催者からの正式な連絡をお待ちください。

🕐 **最終更新**: {current_date.strftime('%Y年%m月%d日 %H:%M')}"""

    def generate_polite_reminder_message(self, note_info: Dict) -> str:
        """丁寧なリマインダーメッセージを生成"""
        try:
            # 基本情報を取得
            days_until = note_info.get("days_until", 0)
            is_input_deadline = note_info.get("is_input_deadline", False)
            event_date = note_info.get("date")
            content = note_info.get("content", "")

            # 緊急度を判定
            urgency = self._determine_urgency_level(days_until, is_input_deadline)
            urgency_info = self.message_templates["urgency_levels"][urgency]

            # イベントタイプを判定
            event_type = self._extract_event_type(content)

            # 日付情報を整理
            if isinstance(event_date, str):
                event_date = datetime.strptime(event_date, '%Y-%m-%d').date()
            elif hasattr(event_date, 'date'):
                event_date = event_date.date()

            formatted_date = event_date.strftime("%Y年%m月%d日")
            weekdays = ["月", "火", "水", "木", "金", "土", "日"]
            weekday = weekdays[event_date.weekday()]
            date_with_weekday = f"{formatted_date}({weekday})"

            # メッセージ構築開始
            message_parts = []

            # 1. ヘッダー（緊急度付き）
            if is_input_deadline:
                if days_until == 0:
                    header = f"{urgency_info['prefix']} 入力期限のご案内（本日期限）"
                elif days_until == 1:
                    header = f"{urgency_info['prefix']} 入力期限のご案内（明日期限）"
                else:
                    header = f"{urgency_info['prefix']} 入力期限のご案内（{days_until}日後期限）"
            else:
                if days_until == 0:
                    header = f"{urgency_info['prefix']} イベント開催のご案内（本日開催）"
                elif days_until == 1:
                    header = f"{urgency_info['prefix']} イベント開催のご案内（明日開催）"
                elif days_until == 2:
                    header = f"{urgency_info['prefix']} イベント開催のご案内（明後日開催）"
                else:
                    header = f"{urgency_info['prefix']} イベント開催のご案内（{days_until}日後開催）"

            message_parts.append(header)
            message_parts.append("")  # 空行

            # 2. 挨拶
            greeting = self._get_greeting_by_time()
            message_parts.append(greeting)
            message_parts.append("")

            # 3. 丁寧な本文
            polite_phrases = self.message_templates["polite_phrases"]

            if is_input_deadline:
                if days_until <= 1:
                    main_text = f"{polite_phrases['apology']}\n"
                    main_text += f"入力期限が{date_with_weekday}となっているイベントがございます。\n"
                    main_text += f"{polite_phrases['request_start']}{polite_phrases['request_input']}"
                else:
                    main_text = f"入力期限が{days_until}日後の{date_with_weekday}となっている予定がございます。\n"
                    main_text += f"事前にご都合をご確認いただき、期限内でのご入力をお願いいたします。"
            else:
                if days_until <= 1:
                    main_text = f"{date_with_weekday}にイベントが開催されます。\n"
                    main_text += "改めてご確認いただき、お気をつけてお越しください。"
                else:
                    main_text = f"{date_with_weekday}にイベントが開催されます。\n"
                    main_text += f"{polite_phrases['request_confirm']}"

            message_parts.append(main_text)
            message_parts.append("")

            # 4. イベント詳細
            message_parts.append("📋 **イベント詳細**")
            message_parts.append(content)
            message_parts.append("")

            # 5. 天気情報（該当する場合）
            if event_type == "outdoor" or days_until <= 2:
                weather_info = self._get_weather_info(event_date, content)
                message_parts.append("=" * 50)
                message_parts.append("")
                message_parts.append(weather_info)
                message_parts.append("")

            # 6. 締めの挨拶
            message_parts.append("=" * 50)
            message_parts.append("")
            message_parts.append("ご不明な点がございましたら、お気軽にお声かけください。")
            message_parts.append(f"{polite_phrases['thank_you']}")
            message_parts.append(f"{polite_phrases['end_formal']}")

            # メッセージを結合
            final_message = "\n".join(message_parts)

            return final_message

        except Exception as e:
            print(f"[REMINDER_MESSAGE] エラー: {e}")
            # フォールバック: 基本的なメッセージを返す
            return self._generate_fallback_message(note_info)

    def _generate_fallback_message(self, note_info: Dict) -> str:
        """フォールバック用基本メッセージ"""
        content = note_info.get("content", "イベントの詳細")
        days_until = note_info.get("days_until", 0)

        return f"""📅 イベントのお知らせ

お疲れ様です。

{days_until}日後にイベントが予定されています。
詳細をご確認ください。

{content}

よろしくお願いいたします。"""

    def generate_flex_message_data(self, note_info: Dict) -> Dict:
        """Flex Message用のデータ構造を生成"""
        try:
            days_until = note_info.get("days_until", 0)
            is_input_deadline = note_info.get("is_input_deadline", False)
            event_date = note_info.get("date")
            content = note_info.get("content", "")

            # 緊急度を判定
            urgency = self._determine_urgency_level(days_until, is_input_deadline)
            urgency_info = self.message_templates["urgency_levels"][urgency]

            # 日付フォーマット
            if isinstance(event_date, str):
                event_date = datetime.strptime(event_date, '%Y-%m-%d').date()
            elif hasattr(event_date, 'date'):
                event_date = event_date.date()

            formatted_date = event_date.strftime("%Y年%m月%d日")
            weekdays = ["月", "火", "水", "木", "金", "土", "日"]
            weekday = weekdays[event_date.weekday()]
            date_with_weekday = f"{formatted_date}({weekday})"

            # タイトルと説明を生成
            if is_input_deadline:
                if days_until == 0:
                    title = "⚠️ 入力期限（本日）"
                    subtitle = "本日期限です"
                elif days_until == 1:
                    title = "⏰ 入力期限（明日）"
                    subtitle = "明日期限です"
                else:
                    title = f"📅 入力期限（{days_until}日後）"
                    subtitle = f"{days_until}日後が期限です"
            else:
                if days_until == 0:
                    title = "🎯 イベント開催（本日）"
                    subtitle = "本日開催です"
                elif days_until == 1:
                    title = "⏰ イベント開催（明日）"
                    subtitle = "明日開催です"
                elif days_until == 2:
                    title = "📅 イベント開催（明後日）"
                    subtitle = "明後日開催です"
                else:
                    title = f"📅 イベント開催（{days_until}日後）"
                    subtitle = f"{days_until}日後開催です"

            # 天気情報取得
            weather_summary = ""
            try:
                weather_info = self._get_weather_info(event_date, content)
                if weather_info:
                    # 簡潔な天気サマリーを作成
                    if "気温" in weather_info:
                        temp_match = re.search(r'(\d+°C)', weather_info)
                        if temp_match:
                            weather_summary = f"天気: {temp_match.group(1)}"

                    if "降水確率" in weather_info:
                        precip_match = re.search(r'降水確率.*?(\d+%)', weather_info)
                        if precip_match:
                            if weather_summary:
                                weather_summary += f" / 降水: {precip_match.group(1)}"
                            else:
                                weather_summary = f"降水: {precip_match.group(1)}"
            except Exception:
                pass

            if not weather_summary:
                weather_summary = "天気予報をご確認ください"

            # Flex Message構造
            flex_data = {
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": title,
                            "weight": "bold",
                            "size": "md",
                            "color": "#FFFFFF"
                        }
                    ],
                    "backgroundColor": urgency_info["color"],
                    "paddingAll": "15px"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "📅 日時",
                                    "size": "sm",
                                    "color": "#666666",
                                    "weight": "bold"
                                },
                                {
                                    "type": "text",
                                    "text": date_with_weekday,
                                    "size": "lg",
                                    "weight": "bold",
                                    "color": urgency_info["color"],
                                    "margin": "xs"
                                }
                            ],
                            "margin": "none"
                        },
                        {
                            "type": "separator",
                            "margin": "md"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "📋 内容",
                                    "size": "sm",
                                    "color": "#666666",
                                    "weight": "bold"
                                },
                                {
                                    "type": "text",
                                    "text": content[:100] + ("..." if len(content) > 100 else ""),
                                    "size": "md",
                                    "wrap": True,
                                    "margin": "xs"
                                }
                            ],
                            "margin": "md"
                        },
                        {
                            "type": "separator",
                            "margin": "md"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "🌤️ 天気情報",
                                    "size": "sm",
                                    "color": "#666666",
                                    "weight": "bold"
                                },
                                {
                                    "type": "text",
                                    "text": weather_summary,
                                    "size": "sm",
                                    "wrap": True,
                                    "margin": "xs"
                                }
                            ],
                            "margin": "md"
                        }
                    ],
                    "paddingAll": "15px"
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": subtitle,
                                    "size": "sm",
                                    "color": urgency_info["color"],
                                    "weight": "bold",
                                    "flex": 1
                                },
                                {
                                    "type": "text",
                                    "text": "UMA3リマインダー",
                                    "size": "xs",
                                    "color": "#999999",
                                    "align": "end",
                                    "flex": 1
                                }
                            ]
                        }
                    ],
                    "paddingAll": "10px"
                }
            }

            return flex_data

        except Exception as e:
            print(f"[FLEX_MESSAGE] エラー: {e}")
            # フォールバック: 基本的なFlex Message
            return self._generate_fallback_flex_message(note_info)

    def _generate_fallback_flex_message(self, note_info: Dict) -> Dict:
        """フォールバック用基本Flex Message"""
        content = note_info.get("content", "イベントの詳細")

        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "📅 イベントのお知らせ",
                        "weight": "bold",
                        "size": "lg"
                    },
                    {
                        "type": "text",
                        "text": content,
                        "wrap": True,
                        "margin": "md"
                    }
                ]
            }
        }

# グローバルインスタンス
reminder_message_generator = EnhancedReminderMessageGenerator()

def generate_enhanced_reminder_message(note_info: Dict) -> str:
    """拡張リマインダーメッセージ生成（外部インターフェース）"""
    return reminder_message_generator.generate_polite_reminder_message(note_info)

def generate_enhanced_flex_message(note_info: Dict) -> Dict:
    """拡張Flex Message生成（外部インターフェース）"""
    return reminder_message_generator.generate_flex_message_data(note_info)

def generate_weather_flex_card(note_info: Dict) -> Dict:
    """天気情報カードのFlex Message生成（OpenWeatherMap API使用）"""
    try:
        # イベント日の取得
        event_date = note_info.get("date")
        if isinstance(event_date, str):
            event_date = datetime.strptime(event_date, '%Y-%m-%d').date()
        event_datetime = datetime.combine(event_date, datetime.min.time())

        # 会場情報の抽出
        content = note_info.get("content", "")
        location = reminder_message_generator._extract_location_from_event(content)
        venue_name = reminder_message_generator._extract_venue_name(content)

        # イベントまでの日数
        days_until = (event_date - datetime.now().date()).days

        # OpenWeatherMap API で天気情報を取得
        from openweather_service import get_weather_for_location

        weather_data = get_weather_for_location(location, venue_name, days_until)

        if weather_data:
            return reminder_message_generator.create_weather_flex_message(weather_data, location, venue_name)
        else:
            return reminder_message_generator._create_fallback_flex_message(location, venue_name)

    except Exception as e:
        print(f"[WEATHER_FLEX] エラー: {e}")
        return reminder_message_generator._create_fallback_flex_message("", "")

if __name__ == "__main__":
    # テスト実行
    test_note = {
        "content": "[ノート] 11月3日(日) ソフトボール練習試合\n会場: 代々木公園グラウンド\n集合時間: 9:00\n持ち物: グローブ、帽子、飲み物",
        "date": datetime(2025, 11, 3).date(),
        "days_until": 1,
        "is_input_deadline": False
    }

    print("=== 拡張リマインダーメッセージテスト ===")
    enhanced_message = generate_enhanced_reminder_message(test_note)
    print(enhanced_message)

    print("\n=== Flex Messageテスト ===")
    flex_data = generate_enhanced_flex_message(test_note)
    print(json.dumps(flex_data, ensure_ascii=False, indent=2))
