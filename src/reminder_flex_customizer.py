#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
リマインダー用Flex Messageカスタマイザー
天気情報Flexテンプレートをリマインダーシステム専用にカスタマイズ
"""

import os
import re
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from typing import Dict, Optional

class ReminderFlexCustomizer:
    """リマインダー用Flex Messageカスタマイザー"""

    def __init__(self):
        """初期化"""
        pass

    def customize_weather_flex_for_reminder(self, base_flex: Dict, note: Dict) -> Dict:
        """
        天気情報Flex MessageをリマインダーシステムFlex専用にカスタマイズ
        上段：ノート情報、下段：会場名と天候情報

        Args:
            base_flex (Dict): 基本の天気Flex Message
            note (Dict): ノート情報

        Returns:
            Dict: カスタマイズされたFlex Message
        """
        try:
            # 新しいFlex Message構造を作成
            event_content = note['content']
            event_date = note["date"]
            days_until = note["days_until"]
            is_input_deadline = note.get("is_input_deadline", False)

            # カスタムFlex Messageを構築
            customized_flex = self._create_custom_reminder_flex(
                event_content, event_date, days_until, is_input_deadline, base_flex
            )

            return customized_flex

        except Exception as e:
            print(f"[REMINDER_FLEX] カスタマイズエラー: {e}")
            return base_flex

    def _create_event_detail_section(self, event_content: str, event_date: datetime, is_input_deadline: bool) -> List:
        """
        イベント詳細セクションを作成

        Args:
            event_content (str): イベント内容
            event_date (datetime): イベント日付
            is_input_deadline (bool): 入力期限かどうか

        Returns:
            list: イベント詳細セクションのコンテンツ
        """
        # 日付フォーマット
        formatted_date = event_date.strftime("%Y年%m月%d日")
        weekdays = ["月", "火", "水", "木", "金", "土", "日"]
        weekday = weekdays[event_date.weekday()]
        date_with_weekday = f"{formatted_date}({weekday})"

        # イベント内容を整理（最初の100文字程度）
        display_content = event_content
        if len(display_content) > 100:
            display_content = display_content[:100] + "..."

        # 場所情報を抽出
        location_info = self._extract_location_info(event_content)

        # イベント詳細セクション
        event_section = [
            {
                "type": "text",
                "text": "📋 イベント詳細",
                "size": "md",
                "weight": "bold",
                "color": "#333333",
                "margin": "lg"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "📅 日時:",
                                "size": "sm",
                                "color": "#666666",
                                "weight": "bold",
                                "flex": 2
                            },
                            {
                                "type": "text",
                                "text": date_with_weekday,
                                "size": "sm",
                                "color": "#333333",
                                "flex": 5,
                                "wrap": True
                            }
                        ],
                        "margin": "md"
                    }
                ],
                "spacing": "sm"
            }
        ]

        # 場所情報があれば追加
        if location_info:
            event_section[1]["contents"].append({
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "text",
                        "text": "📍 場所:",
                        "size": "sm",
                        "color": "#666666",
                        "weight": "bold",
                        "flex": 2
                    },
                    {
                        "type": "text",
                        "text": location_info,
                        "size": "sm",
                        "color": "#333333",
                        "flex": 5,
                        "wrap": True
                    }
                ],
                "margin": "sm"
            })

        # イベント内容を追加
        event_section[1]["contents"].append({
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": "📝 内容:",
                    "size": "sm",
                    "color": "#666666",
                    "weight": "bold",
                    "flex": 2
                },
                {
                    "type": "text",
                    "text": display_content,
                    "size": "sm",
                    "color": "#333333",
                    "flex": 5,
                    "wrap": True
                }
            ],
            "margin": "sm"
        })

        # 期限タイプによる追加情報
        if is_input_deadline:
            event_section[1]["contents"].append({
                "type": "text",
                "text": "⚠️ 参加・欠席のご回答をお願いいたします",
                "size": "sm",
                "color": "#FF6B6B",
                "weight": "bold",
                "margin": "md"
            })

        return event_section

    def _create_custom_reminder_flex(self, event_content: str, event_date: datetime,
                                    days_until: int, is_input_deadline: bool, base_flex: Dict) -> Dict:
        """
        カスタムリマインダーFlex Messageを作成
        上段：ノート情報、下段：会場名と天候情報

        Args:
            event_content (str): イベント内容
            event_date (datetime): イベント日付
            days_until (int): 何日後か
            is_input_deadline (bool): 入力期限かどうか
            base_flex (Dict): 基本の天気Flex Message

        Returns:
            Dict: カスタムFlex Message
        """
        # 日付フォーマット
        formatted_date = event_date.strftime("%Y年%m月%d日")
        weekdays = ["月", "火", "水", "木", "金", "土", "日"]
        weekday = weekdays[event_date.weekday()]
        date_with_weekday = f"{formatted_date}({weekday})"

        # タイトル生成
        if is_input_deadline:
            if days_until <= 1:
                title = f"⏰ 入力期限のご案内（{'本日' if days_until == 0 else '明日'}期限）"
                title_color = "#FF6B6B"
            else:
                title = f"📅 入力期限のご案内（{days_until}日後期限）"
                title_color = "#FFA726"
        else:
            if days_until <= 1:
                title = f"🎯 イベント開催のご案内（{'本日' if days_until == 0 else '明日'}開催）"
                title_color = "#FF6B6B"
            else:
                title = f"📅 イベント開催のご案内（{days_until}日後開催）"
                title_color = "#42A5F5"

        # 場所情報を抽出
        location_info = self._extract_location_info(event_content)

        # 天気情報をbase_flexから抽出
        weather_info = self._extract_weather_info_from_base_flex(base_flex)

        # カスタムFlex Message構造
        custom_flex = {
            "type": "flex",
            "altText": f"{title} - {date_with_weekday}",
            "contents": {
                "type": "bubble",
                "size": "mega",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": title,
                            "weight": "bold",
                            "size": "md",
                            "color": "#FFFFFF",
                            "wrap": True
                        }
                    ],
                    "backgroundColor": title_color,
                    "paddingAll": "15px"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        # 上段：ノート情報
                        {
                            "type": "text",
                            "text": "📋 イベント情報",
                            "size": "lg",
                            "weight": "bold",
                            "color": "#333333"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "📅 日時:",
                                            "size": "sm",
                                            "color": "#666666",
                                            "weight": "bold",
                                            "flex": 2
                                        },
                                        {
                                            "type": "text",
                                            "text": date_with_weekday,
                                            "size": "sm",
                                            "color": "#333333",
                                            "flex": 5,
                                            "wrap": True
                                        }
                                    ]
                                }
                            ]
                        },
                        # ノート内容の詳細を追加
                        self._create_note_content_section(event_content),

                        # 区切り線
                        {
                            "type": "separator",
                            "margin": "lg"
                        },

                        # 下段：会場名と天候情報
                        {
                            "type": "text",
                            "text": "🏟️ 会場・天候情報",
                            "size": "lg",
                            "weight": "bold",
                            "color": "#333333",
                            "margin": "lg"
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "UMA3リマインダー",
                            "size": "xs",
                            "color": "#999999",
                            "align": "center"
                        }
                    ],
                    "paddingAll": "10px"
                }
            }
        }

        # 会場情報と天候情報を下段に追加
        venue_weather_section = self._create_venue_weather_section(location_info, weather_info)
        custom_flex["contents"]["body"]["contents"].extend(venue_weather_section)

        return custom_flex

    def _extract_location_info(self, event_content: str) -> Optional[str]:
        """
        イベント内容から場所情報を抽出

        Args:
            event_content (str): イベント内容

        Returns:
            Optional[str]: 場所情報
        """
        location_patterns = [
            r'場所[：:]\s*([^\n]+)',
            r'会場[：:]\s*([^\n]+)',
            r'開催地[：:]\s*([^\n]+)',
            r'集合場所[：:]\s*([^\n]+)',
            r'【大会会場】\s*([^\n]+)',
            r'(東京都|神奈川県|千葉県|埼玉県|大阪府|愛知県|福岡県)[^\n]*球場',
            r'(東京都|神奈川県|千葉県|埼玉県|大阪府|愛知県|福岡県)[^\n]*グラウンド'
        ]

        for pattern in location_patterns:
            match = re.search(pattern, event_content, re.MULTILINE)
            if match:
                if pattern.startswith('場所') or pattern.startswith('会場') or pattern.startswith('開催地') or pattern.startswith('集合場所') or pattern.startswith('【大会会場】'):
                    return match.group(1).strip()
                else:
                    return match.group(0).strip()

        return None

    def _extract_weather_info_from_base_flex(self, base_flex: Dict) -> Dict:
        """
        base_flexから天気情報を抽出

        Args:
            base_flex (Dict): 基本の天気Flex Message

        Returns:
            Dict: 天気情報
        """
        weather_info = {
            "temperature": "情報なし",
            "condition": "情報なし",
            "humidity": "情報なし",
            "wind_speed": "情報なし",
            "advice": "天候情報を確認してください"
        }

        try:
            if "contents" in base_flex and "body" in base_flex["contents"]:
                body_contents = base_flex["contents"]["body"].get("contents", [])

                for section in body_contents:
                    if section.get("type") == "box" and "contents" in section:
                        for item in section["contents"]:
                            if item.get("type") == "text":
                                text = item.get("text", "")
                                # 気温情報
                                if "℃" in text and "気温" in text:
                                    weather_info["temperature"] = text.replace("気温: ", "")
                                # 天気情報
                                elif any(weather in text for weather in ["晴れ", "曇り", "雨", "雪", "霧"]):
                                    weather_info["condition"] = text
                                # 湿度情報
                                elif "湿度" in text and "%" in text:
                                    weather_info["humidity"] = text.replace("湿度: ", "")
                                # 風速情報
                                elif "風速" in text and "m/s" in text:
                                    weather_info["wind_speed"] = text.replace("風速: ", "")
                                # アドバイス情報
                                elif len(text) > 20 and any(word in text for word in ["おすすめ", "注意", "準備"]):
                                    weather_info["advice"] = text

        except Exception as e:
            print(f"天気情報抽出エラー: {e}")

        return weather_info

    def _create_note_content_section(self, event_content: str) -> Dict:
        """
        ノート内容セクションを作成

        Args:
            event_content (str): イベント内容

        Returns:
            Dict: ノート内容セクション
        """
        # イベント内容を行ごとに分析
        lines = event_content.strip().split('\n')
        content_items = []

        for line in lines:
            line = line.strip()
            if line and len(line) > 2:  # 空行や短すぎる行をスキップ
                # 重要な情報をハイライト
                if any(keyword in line for keyword in ["時間", "集合", "持ち物", "注意", "連絡"]):
                    content_items.append({
                        "type": "text",
                        "text": f"• {line}",
                        "size": "sm",
                        "color": "#2E7D32",
                        "wrap": True
                    })
                else:
                    content_items.append({
                        "type": "text",
                        "text": f"• {line}",
                        "size": "sm",
                        "color": "#555555",
                        "wrap": True
                    })

        # 内容がない場合のデフォルト
        if not content_items:
            content_items.append({
                "type": "text",
                "text": "詳細は別途確認してください",
                "size": "sm",
                "color": "#999999",
                "wrap": True
            })

        return {
            "type": "box",
            "layout": "vertical",
            "spacing": "xs",
            "contents": content_items[:5],  # 最大5項目まで表示
            "backgroundColor": "#F8F9FA",
            "paddingAll": "12px",
            "cornerRadius": "8px"
        }

    def _create_venue_weather_section(self, location_info: Optional[str], weather_info: Dict) -> List[Dict]:
        """
        会場・天候情報セクションを作成

        Args:
            location_info (Optional[str]): 場所情報
            weather_info (Dict): 天気情報

        Returns:
            List[Dict]: 会場・天候情報セクション
        """
        sections = []

        # 会場情報
        if location_info:
            sections.append({
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "text",
                        "text": "📍 会場:",
                        "size": "sm",
                        "color": "#666666",
                        "weight": "bold",
                        "flex": 2
                    },
                    {
                        "type": "text",
                        "text": location_info,
                        "size": "sm",
                        "color": "#333333",
                        "flex": 5,
                        "wrap": True
                    }
                ]
            })
        else:
            sections.append({
                "type": "text",
                "text": "📍 会場: 詳細はイベント情報をご確認ください",
                "size": "sm",
                "color": "#999999",
                "wrap": True
            })

        # 天候情報
        weather_section = {
            "type": "box",
            "layout": "vertical",
            "spacing": "xs",
            "contents": [
                {
                    "type": "text",
                    "text": "🌤️ 天候予報",
                    "size": "sm",
                    "weight": "bold",
                    "color": "#666666",
                    "margin": "sm"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "xxs",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"天気: {weather_info['condition']} | 気温: {weather_info['temperature']}",
                            "size": "xs",
                            "color": "#333333"
                        },
                        {
                            "type": "text",
                            "text": f"湿度: {weather_info['humidity']} | 風速: {weather_info['wind_speed']}",
                            "size": "xs",
                            "color": "#333333"
                        }
                    ]
                }
            ],
            "backgroundColor": "#E3F2FD",
            "paddingAll": "10px",
            "cornerRadius": "6px",
            "margin": "sm"
        }

        sections.append(weather_section)

        # 天候アドバイス
        if weather_info['advice'] and weather_info['advice'] != "天候情報を確認してください":
            advice_section = {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "💡 天候アドバイス",
                        "size": "xs",
                        "weight": "bold",
                        "color": "#666666"
                    },
                    {
                        "type": "text",
                        "text": weather_info['advice'],
                        "size": "xs",
                        "color": "#555555",
                        "wrap": True
                    }
                ],
                "backgroundColor": "#FFF3E0",
                "paddingAll": "8px",
                "cornerRadius": "4px",
                "margin": "xs"
            }
            sections.append(advice_section)

        return sections

    def _create_reminder_footer(self, is_input_deadline: bool, days_until: int) -> Dict:
        if is_input_deadline:
            # 入力期限の場合：参加・欠席ボタン
            return {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "ご都合をお聞かせください",
                        "size": "sm",
                        "color": "#666666",
                        "align": "center",
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "button",
                                "style": "primary",
                                "height": "sm",
                                "action": {
                                    "type": "message",
                                    "label": "✅ 参加します",
                                    "text": "参加します！"
                                },
                                "color": "#28a745",
                                "flex": 1
                            },
                            {
                                "type": "separator",
                                "margin": "sm"
                            },
                            {
                                "type": "button",
                                "style": "secondary",
                                "height": "sm",
                                "action": {
                                    "type": "message",
                                    "label": "❌ 欠席します",
                                    "text": "申し訳ありませんが欠席します"
                                },
                                "flex": 1
                            }
                        ],
                        "spacing": "sm",
                        "margin": "md"
                    },
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "message",
                            "label": "🤔 検討中です",
                            "text": "検討中です。後日回答いたします"
                        },
                        "margin": "sm"
                    }
                ],
                "paddingAll": "15px"
            }
        else:
            # イベント開催日の場合：確認ボタン
            urgency_text = ""
            if days_until == 0:
                urgency_text = "本日開催"
            elif days_until == 1:
                urgency_text = "明日開催"
            elif days_until == 2:
                urgency_text = "明後日開催"
            else:
                urgency_text = f"{days_until}日後開催"

            return {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": urgency_text,
                                "size": "sm",
                                "color": "#FF6B6B",
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
                    },
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "message",
                            "label": "📝 了解しました",
                            "text": "了解しました。気をつけて参加します"
                        },
                        "margin": "md"
                    }
                ],
                "paddingAll": "10px"
            }

    def create_text_with_weather_summary(self, note: Dict) -> str:
        """
        天気情報を含むテキストサマリーを作成

        Args:
            note (Dict): ノート情報

        Returns:
            str: 天気情報を含むテキストサマリー
        """
        try:
            from weather_flex_template import WeatherFlexTemplate

            weather_template = WeatherFlexTemplate()
            event_date = note["date"]
            days_until = note["days_until"]

            # 場所情報を抽出
            location = "東京都"
            event_content = note['content']
            location_patterns = [
                r'場所[：:]\s*([^\n]+)',
                r'会場[：:]\s*([^\n]+)',
                r'(東京都|神奈川県|千葉県|埼玉県)[^\n]*'
            ]

            for pattern in location_patterns:
                match = re.search(pattern, event_content)
                if match:
                    location = match.group(1) if pattern.startswith('場所') or pattern.startswith('会場') else match.group(0)
                    break

            # 天気情報を取得
            if days_until == 0:
                weather_data = weather_template.get_current_weather(location)
            else:
                date_str = event_date.strftime('%Y-%m-%d')
                weather_data = weather_template.get_forecast_weather(location, date_str)

            if weather_data:
                temp = weather_data.get('temperature', weather_data.get('temp', '不明'))
                weather_desc = weather_data.get('description', weather_data.get('weather', '不明'))

                return f"🌤️ {location}: {temp}℃ / {weather_desc}"
            else:
                return f"🌤️ {location}: 天気情報をご確認ください"

        except Exception as e:
            print(f"[WEATHER_SUMMARY] エラー: {e}")
            return "🌤️ 天気情報をご確認ください"

    def _create_reminder_footer(self, is_input_deadline: bool, days_until: int) -> Dict:
        """
        リマインダー専用フッターを作成

        Args:
            is_input_deadline (bool): 入力期限かどうか
            days_until (int): 何日後か

        Returns:
            Dict: フッターセクション
        """
        # 緊急度に応じたメッセージ
        if days_until <= 1:
            if is_input_deadline:
                footer_text = "⚠️ 入力期限が迫っています"
                footer_color = "#FF6B6B"
            else:
                footer_text = "🎯 開催日が近づいています"
                footer_color = "#FF6B6B"
        else:
            footer_text = "📅 UMA3リマインダー"
            footer_color = "#42A5F5"

        return {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": footer_text,
                    "size": "xs",
                    "color": footer_color,
                    "align": "center",
                    "weight": "bold"
                },
                {
                    "type": "text",
                    "text": "詳細は通知をご確認ください",
                    "size": "xxs",
                    "color": "#999999",
                    "align": "center",
                    "margin": "xs"
                }
            ],
            "paddingAll": "10px"
        }
