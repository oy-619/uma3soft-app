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

    def __str__(self):
        return "ReminderFlexCustomizer: リマインダー用Flex Messageカスタマイザー"

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

    def _create_custom_reminder_flex(self, event_content: str, event_date: datetime,
                                    days_until: int, is_input_deadline: bool, base_flex: Dict) -> Dict:
        """
        調整さん確認・入力依頼を主体とするリマインダーFlex Messageを作成
        主要コンテンツ：調整さんの確認と入力依頼
        付属情報：天候情報（簡潔に表示）

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

        # 調整さん依頼を主体とするタイトル生成
        if is_input_deadline:
            if days_until <= 1:
                title = f"📝 参加可否のご回答をお願いします（{'本日' if days_until == 0 else '明日'}期限）"
                title_color = "#FF5722"
                urgency_emoji = "🚨"
            else:
                title = f"� 参加可否のご回答をお願いします（{days_until}日後期限）"
                title_color = "#FF9800"
                urgency_emoji = "⏰"
        else:
            if days_until <= 1:
                title = f"🎯 {'本日' if days_until == 0 else '明日'}開催予定のイベントについて"
                title_color = "#4CAF50"
                urgency_emoji = "📢"
            else:
                title = f"📅 {days_until}日後開催予定のイベントについて"
                title_color = "#2196F3"
                urgency_emoji = "📋"

        # 場所情報を抽出
        location_info = self._extract_location_info(event_content)

        # 天気情報をbase_flexから詳細に抽出
        weather_info = self._extract_weather_info_from_base_flex(base_flex)

        # 調整さん確認を主体とするFlex Message構造
        custom_flex = {
            "type": "flex",
            "altText": f"【調整さん】{title} - {date_with_weekday}",
            "contents": {
                "type": "bubble",
                "size": "mega",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"{urgency_emoji} 調整さん確認依頼",
                            "weight": "bold",
                            "size": "lg",
                            "color": "#FFFFFF",
                            "align": "center"
                        },
                        {
                            "type": "text",
                            "text": title,
                            "weight": "regular",
                            "size": "sm",
                            "color": "#FFFFFF",
                            "wrap": True,
                            "align": "center",
                            "margin": "sm"
                        }
                    ],
                    "backgroundColor": title_color,
                    "paddingAll": "20px"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "lg",
                    "contents": [
                        # 主要コンテンツ：調整さん確認・入力依頼
                        self._create_main_reminder_section(event_content, date_with_weekday, is_input_deadline, days_until),

                        # 区切り線
                        {
                            "type": "separator",
                            "margin": "lg"
                        },

                        # 付属情報：詳細な天候情報
                        self._create_compact_weather_section(location_info, weather_info)
                    ]
                },
                "footer": self._create_reminder_action_footer(is_input_deadline, days_until, event_content)
            }
        }

        return custom_flex

    def _extract_location_info(self, event_content: str) -> Optional[str]:
        """
        イベント内容から具体的な場所情報を抽出（地名のみ：葛飾区柴又球場など）

        Args:
            event_content (str): イベント内容

        Returns:
            Optional[str]: 具体的な場所情報
        """
        location_patterns = [
            # 明示的な場所表記（最優先）
            r'場所[：:]\s*([^\n、。，]+)',
            r'会場[：:]\s*([^\n、。，]+)',
            r'開催地[：:]\s*([^\n、。，]+)',
            r'集合場所[：:]\s*([^\n、。，]+)',
            r'【大会会場】\s*([^\n、。，]+)',

            # 具体的な施設名パターン（区市町村＋施設名）
            r'([^都道府県\n]*区[^\n]*球場)',
            r'([^都道府県\n]*市[^\n]*球場)',
            r'([^都道府県\n]*町[^\n]*球場)',
            r'([^都道府県\n]*区[^\n]*グラウンド)',
            r'([^都道府県\n]*市[^\n]*グラウンド)',
            r'([^都道府県\n]*町[^\n]*グラウンド)',

            # ドーム・スタジアムなどの施設（「にて」「で」などの助詞を除く）
            r'([^都道府県\n、。]*ドーム)(?:にて|で|において)?',
            r'([^都道府県\n、。]*スタジアム)(?:にて|で|において)?',
            r'([^都道府県\n、。]*野球場)(?:にて|で|において)?',
            r'([^都道府県\n、。]*運動場)(?:にて|で|において)?',
            r'([^都道府県\n、。]*公園)(?:野球場|にて|で|において)?',

            # 都道府県付きの場合は具体的な地域を抽出
            r'東京都([^東京都\n]*区[^\n]*球場)',
            r'東京都([^東京都\n]*市[^\n]*球場)',
            r'神奈川県([^神奈川県\n]*区[^\n]*球場)',
            r'神奈川県([^神奈川県\n]*市[^\n]*球場)',
            r'千葉県([^千葉県\n]*区[^\n]*球場)',
            r'千葉県([^千葉県\n]*市[^\n]*球場)',
            r'埼玉県([^埼玉県\n]*区[^\n]*球場)',
            r'埼玉県([^埼玉県\n]*市[^\n]*球場)'
        ]

        for pattern in location_patterns:
            match = re.search(pattern, event_content, re.MULTILINE)
            if match:
                if pattern.startswith('場所') or pattern.startswith('会場') or pattern.startswith('開催地') or pattern.startswith('集合場所') or pattern.startswith('【大会会場】'):
                    location_text = match.group(1).strip()
                else:
                    # 括弧内のグループ（具体的な地名）を取得
                    location_text = match.group(1).strip() if '(' in pattern else match.group(0).strip()

                # 調整さん関連の文字列を除外
                exclude_keywords = ["調整さん", "chouseisan", "URL", "https://", "http://"]
                if not any(keyword in location_text for keyword in exclude_keywords):
                    # 余分な文字列をクリーンアップ
                    location_text = self._clean_specific_location_name(location_text)
                    return location_text

        return None

    def _clean_specific_location_name(self, raw_location: str) -> str:
        """
        具体的な場所名をクリーンアップして、施設名のみを抽出

        Args:
            raw_location (str): 生の場所名

        Returns:
            str: クリーンアップされた具体的な場所名
        """
        if not raw_location:
            return ""

        # 不要な文字列を除去
        location = raw_location.strip()

        # 都道府県プレフィックスを除去（既に抽出済みの場合）
        location = re.sub(r'^(東京都|神奈川県|千葉県|埼玉県|大阪府|愛知県|福岡県|北海道)\s*', '', location)

        # カンマや句点で区切られた最初の部分のみを取得（追加情報を除去）
        location = re.split(r'[、。，,]', location)[0].strip()

        # 括弧以降の情報を除去
        location = re.sub(r'[（）()【】\[\]].*$', '', location)

        # 「にて」「で」「において」などの助詞を除去
        location = re.sub(r'(にて|において|で)$', '', location)

        # 「開催」「実施」などの不要な文言を除去
        location = re.sub(r'(開催|実施|にて開催|で開催)$', '', location)

        # 公園+野球場のパターンを正規化
        if '公園' in location and '野球場' not in location:
            # 「〇〇公園」→「〇〇公園野球場」（野球場がない場合のみ）
            if re.search(r'公園$', location):
                location = location + '野球場'

        # 連続する空白を単一の空白に変換し、前後の空白を除去
        location = re.sub(r'\s+', ' ', location).strip()

        return location

    def _clean_event_content_for_display(self, event_content: str) -> str:
        """
        イベント内容から調整さん関連情報を除外してクリーンアップ

        Args:
            event_content (str): 元のイベント内容

        Returns:
            str: クリーンアップされたイベント内容
        """
        if not event_content:
            return ""

        lines = event_content.strip().split('\n')
        cleaned_lines = []

        exclude_keywords = ["調整さん", "chouseisan", "URL", "https://", "http://", "↑必ず", "必ずご入力"]
        exclude_patterns = [
            r'調整さん.*入力',
            r'.*URL.*入力',
            r'↑.*ください',
            r'.*chouseisan\.com.*'
        ]

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 除外キーワードをチェック
            should_exclude = False
            for keyword in exclude_keywords:
                if keyword in line:
                    should_exclude = True
                    break

            # 除外パターンをチェック
            if not should_exclude:
                for pattern in exclude_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        should_exclude = True
                        break

            if not should_exclude:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _extract_author_info(self, event_content: str) -> str:
        """
        イベント内容から投稿者の氏名を抽出
        投稿者の氏名をより正確に抽出するため、複数のパターンを試行

        Args:
            event_content (str): イベント内容

        Returns:
            str: 投稿者の氏名
        """
        # より正確な氏名抽出パターン
        author_patterns = [
            # 基本パターン（姓名形式）
            r'連絡先[：:]\s*([^\s\n（）【】、。]+[太郎次郎三郎四郎花子美子恵子春子夏子秋子冬子][^\s\n]*)',
            r'担当[：:]\s*([^\s\n（）【】、。]+[太郎次郎三郎四郎花子美子恵子春子夏子秋子冬子][^\s\n]*)',
            r'投稿者[：:]\s*([^\s\n（）【】、。]+[太郎次郎三郎四郎花子美子恵子春子夏子秋子冬子][^\s\n]*)',
            r'主催[：:]\s*([^\s\n（）【】、。]+[太郎次郎三郎四郎花子美子恵子春子夏子秋子冬子][^\s\n]*)',
            r'問い合わせ[：:]\s*([^\s\n（）【】、。]+[太郎次郎三郎四郎花子美子恵子春子夏子秋子冬子][^\s\n]*)',

            # 一般的な氏名パターン（姓+名の形式）
            r'連絡先[：:]\s*([^\s\n（）【】、。]*[山田田中佐藤鈴木高橋小林松本中村石川前田青木藤田井上][^\s\n]*)',
            r'担当[：:]\s*([^\s\n（）【】、。]*[山田田中佐藤鈴木高橋小林松本中村石川前田青木藤田井上][^\s\n]*)',
            r'投稿者[：:]\s*([^\s\n（）【】、。]*[山田田中佐藤鈴木高橋小林松本中村石川前田青木藤田井上][^\s\n]*)',
            r'主催[：:]\s*([^\s\n（）【】、。]*[山田田中佐藤鈴木高橋小林松本中村石川前田青木藤田井上][^\s\n]*)',
            r'問い合わせ[：:]\s*([^\s\n（）【】、。]*[山田田中佐藤鈴木高橋小林松本中村石川前田青木藤田井上][^\s\n]*)',

            # より寛容なパターン（カタカナ氏名も含む）
            r'連絡先[：:]\s*([^\s\n（）【】、。]*[タナカヤマダサトウスズキタカハシ][^\s\n]*)',
            r'担当[：:]\s*([^\s\n（）【】、。]*[タナカヤマダサトウスズキタカハシ][^\s\n]*)',

            # 最後の行から氏名らしき文字列を抽出
            r'([^\s\n（）【】、。]*[太郎次郎三郎四郎花子美子恵子春子夏子秋子冬子][^\s\n]*)\s*$',
            r'([^\s\n（）【】、。]*[山田田中佐藤鈴木高橋小林松本中村石川前田青木藤田井上][^\s\n]*)\s*$',

            # 基本形式（氏名っぽい文字列）
            r'連絡先[：:]\s*([^\s\n（）【】、。]+)',
            r'担当[：:]\s*([^\s\n（）【】、。]+)',
            r'投稿者[：:]\s*([^\s\n（）【】、。]+)',
            r'主催[：:]\s*([^\s\n（）【】、。]+)',
            r'問い合わせ[：:]\s*([^\s\n（）【】、。]+)',
        ]

        for pattern in author_patterns:
            match = re.search(pattern, event_content, re.MULTILINE)
            if match:
                author_name = match.group(1).strip()

                # 不要な文字列を除外
                exclude_keywords = ["調整さん", "chouseisan", "URL", "https://", "http://", "Tel", "電話", "番号", "メール", "@"]
                if not any(keyword in author_name for keyword in exclude_keywords):
                    # 数字のみ、記号のみ、短すぎる名前を除外
                    if (len(author_name) >= 2 and
                        not author_name.isdigit() and
                        not re.match(r'^[0-9\-\(\)]+$', author_name) and
                        len(author_name) <= 10):  # 氏名として妥当な長さ
                        return self._clean_author_name(author_name)

        return "投稿者"

    def _clean_author_name(self, raw_name: str) -> str:
        """
        抽出された氏名をクリーンアップ

        Args:
            raw_name (str): 生の氏名

        Returns:
            str: クリーンアップされた氏名
        """
        if not raw_name:
            return "投稿者"

        # 前後の空白を除去
        name = raw_name.strip()

        # 不要な記号を除去
        name = re.sub(r'[（）()【】\[\]「」『』]', '', name)

        # 連続する空白を単一の空白に変換
        name = re.sub(r'\s+', ' ', name)

        # 電話番号やメールアドレスの一部が含まれていないかチェック
        if re.search(r'[0-9\-@.]', name) and len(name) > 6:
            return "投稿者"

        return name.strip() if name.strip() else "投稿者"

    def _clean_location_name(self, raw_location: str) -> str:
        """
        場所名をクリーンアップして天気API用に最適化

        Args:
            raw_location (str): 生の場所名

        Returns:
            str: クリーンアップされた場所名
        """
        if not raw_location:
            return "東京都"

        # 都道府県名を抽出
        prefecture_patterns = [
            r'(東京都)',
            r'(神奈川県)',
            r'(千葉県)',
            r'(埼玉県)',
            r'(大阪府)',
            r'(愛知県)',
            r'(福岡県)',
            r'(北海道)',
            r'([^県都府道]+県)',
            r'([^県都府道]+府)',
            r'([^県都府道]+都)'
        ]

        for pattern in prefecture_patterns:
            match = re.search(pattern, raw_location)
            if match:
                return match.group(1)

        # 主要都市名を抽出
        city_patterns = [
            r'(横浜|川崎|相模原)',  # 神奈川
            r'(千葉|船橋|松戸)',    # 千葉
            r'(さいたま|川口|所沢)', # 埼玉
            r'(大阪|堺|東大阪)',    # 大阪
            r'(名古屋|豊田|岡崎)',  # 愛知
            r'(福岡|北九州|久留米)', # 福岡
            r'(札幌|函館|旭川)'     # 北海道
        ]

        for pattern in city_patterns:
            match = re.search(pattern, raw_location)
            if match:
                city = match.group(1)
                # 市名に対応する都道府県を返す
                if city in ['横浜', '川崎', '相模原']:
                    return '神奈川県'
                elif city in ['千葉', '船橋', '松戸']:
                    return '千葉県'
                elif city in ['さいたま', '川口', '所沢']:
                    return '埼玉県'
                elif city in ['大阪', '堺', '東大阪']:
                    return '大阪府'
                elif city in ['名古屋', '豊田', '岡崎']:
                    return '愛知県'
                elif city in ['福岡', '北九州', '久留米']:
                    return '福岡県'
                elif city in ['札幌', '函館', '旭川']:
                    return '北海道'

        # デフォルトは東京都
        return "東京都"

    def _extract_gathering_time(self, event_content: str) -> Optional[str]:
        """
        イベント内容から集合時間を抽出（当日リマインド設定用）

        Args:
            event_content (str): イベント内容

        Returns:
            Optional[str]: 集合時間（HH:MM形式）
        """
        time_patterns = [
            r'集合時間[：:]\s*(\d{1,2}):(\d{2})',
            r'集合[：:]\s*(\d{1,2}):(\d{2})',
            r'(\d{1,2}):(\d{2})\s*集合',
            r'(\d{1,2}):(\d{2})\s*に集合',
            r'午前\s*(\d{1,2}):(\d{2})',
            r'午後\s*(\d{1,2}):(\d{2})',
            r'(\d{1,2})時(\d{2})分\s*集合',
            r'(\d{1,2})時(\d{2})分',
        ]

        for pattern in time_patterns:
            match = re.search(pattern, event_content)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2))

                # 午後の場合は12時間加算（午後12時は例外）
                if '午後' in pattern and hour != 12:
                    hour += 12
                elif '午前' in pattern and hour == 12:
                    hour = 0

                return f"{hour:02d}:{minute:02d}"

        return None

    def _calculate_reminder_time(self, gathering_time: str) -> Optional[str]:
        """
        集合時間から1時間前のリマインド時間を計算

        Args:
            gathering_time (str): 集合時間（HH:MM形式）

        Returns:
            Optional[str]: リマインド時間（HH:MM形式）
        """
        try:
            hour, minute = map(int, gathering_time.split(':'))

            # 1時間前に設定
            reminder_hour = hour - 1
            reminder_minute = minute

            # 0時を下回った場合は23時に調整
            if reminder_hour < 0:
                reminder_hour = 23

            return f"{reminder_hour:02d}:{reminder_minute:02d}"
        except:
            return None

    def _create_full_event_content_section(self, event_content: str) -> Dict:
        """
        イベント内容の全文を表示するセクションを作成（調整さん関連は除外）

        Args:
            event_content (str): イベント内容

        Returns:
            Dict: イベント内容全文セクション
        """
        # 調整さん関連情報を除外してクリーンアップ
        display_content = self._clean_event_content_for_display(event_content)

        if not display_content:
            display_content = "詳細は別途ご確認ください"

        return {
            "type": "box",
            "layout": "vertical",
            "spacing": "xs",
            "contents": [
                {
                    "type": "text",
                    "text": "📋 イベント詳細",
                    "size": "sm",
                    "weight": "bold",
                    "color": "#4A5568",
                    "margin": "none"
                },
                {
                    "type": "text",
                    "text": display_content,
                    "size": "xs",
                    "color": "#2D3748",
                    "wrap": True,
                    "margin": "sm"
                }
            ],
            "backgroundColor": "#F8F9FA",
            "paddingAll": "12px",
            "cornerRadius": "8px",
            "margin": "sm"
        }

    def _extract_weather_info_from_base_flex(self, base_flex: Dict) -> Dict:
        """
        base_flexから天気情報を詳細に抽出
        リマインダー用に必要な情報：会場、気温、湿度、降水確率、アドバイス

        Args:
            base_flex (Dict): 基本の天気Flex Message

        Returns:
            Dict: 天気情報
        """
        weather_info = {
            "venue": "情報なし",
            "temperature": "情報なし",
            "humidity": "情報なし",
            "precipitation": "情報なし",
            "advice": "天候情報を確認してください"
        }

        try:
            # contentsがある場合とない場合の両方に対応
            flex_contents = base_flex.get("contents", base_flex)

            # 会場名をheaderから抽出
            if "header" in flex_contents:
                header_contents = flex_contents["header"].get("contents", [])
                for item in header_contents:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text = item.get("text", "")
                        if "📍" in text:
                            weather_info["venue"] = text.replace("📍 ", "").strip()
                            break

            # bodyから天気情報を抽出
            if "body" in flex_contents:
                body_contents = flex_contents["body"].get("contents", [])

                # 再帰的に全てのテキスト要素をチェック
                self._extract_weather_data_recursive(body_contents, weather_info)

        except Exception as e:
            print(f"❌ 天気情報抽出エラー: {e}")
            import traceback
            traceback.print_exc()

        return weather_info

    def _extract_weather_data_recursive(self, contents, weather_info):
        """
        再帰的に天気データを抽出する

        Args:
            contents: 抽出対象のcontents配列
            weather_info: 結果を格納するdict
        """
        if not isinstance(contents, list):
            return

        for section in contents:
            if not isinstance(section, dict):
                continue

            # テキスト要素の場合
            if section.get("type") == "text":
                text = section.get("text", "")
                self._parse_weather_text(text, weather_info)

            # ボックス要素の場合
            elif section.get("type") == "box":
                # 水平レイアウトの場合（ラベル：値の形式）
                if section.get("layout") == "horizontal":
                    horizontal_contents = section.get("contents", [])
                    if len(horizontal_contents) >= 2:
                        # ラベルと値を抽出
                        label_text = self._extract_text_from_element(horizontal_contents[0])
                        value_text = self._extract_text_from_element(horizontal_contents[1])

                        if label_text and value_text:
                            self._categorize_weather_info(label_text, value_text, weather_info)

                # contents配列がある場合は再帰処理
                if "contents" in section:
                    self._extract_weather_data_recursive(section["contents"], weather_info)

    def _extract_text_from_element(self, element):
        """
        要素からテキストを抽出

        Args:
            element: Flex要素

        Returns:
            str: 抽出されたテキスト
        """
        if not isinstance(element, dict):
            return ""

        # 直接テキスト要素の場合
        if element.get("type") == "text":
            return element.get("text", "").strip()

        # contentsがある場合は再帰的に探す
        if "contents" in element:
            for sub_element in element["contents"]:
                text = self._extract_text_from_element(sub_element)
                if text:
                    return text

        return ""

    def _parse_weather_text(self, text, weather_info):
        """
        テキストから天気情報を解析

        Args:
            text (str): 解析対象のテキスト
            weather_info (dict): 結果格納用
        """
        if not text:
            return

        # 温度情報
        temp_match = re.search(r'(\d+(?:\.\d+)?(?:℃|°C))', text)
        if temp_match and weather_info["temperature"] == "情報なし":
            weather_info["temperature"] = temp_match.group(1)

        # 湿度情報
        humidity_match = re.search(r'(\d+%)', text)
        if humidity_match and "湿度" in text and weather_info["humidity"] == "情報なし":
            weather_info["humidity"] = humidity_match.group(1)

        # 降水確率情報
        if ("降水" in text or "雨" in text) and weather_info["precipitation"] == "情報なし":
            precip_match = re.search(r'(\d+%)', text)
            if precip_match:
                weather_info["precipitation"] = precip_match.group(1)

    def _categorize_weather_info(self, label_text, value_text, weather_info):
        """
        ラベルテキストに基づいて天気情報を分類

        Args:
            label_text (str): ラベルテキスト
            value_text (str): 値テキスト
            weather_info (dict): 結果格納用
        """
        if "🌡️" in label_text or "気温" in label_text:
            weather_info["temperature"] = value_text
        elif "💧" in label_text or "湿度" in label_text:
            weather_info["humidity"] = value_text
        elif "☔" in label_text or "降水" in label_text or "雨" in label_text:
            weather_info["precipitation"] = value_text

    def _extract_text_from_box(self, box: Dict) -> str:
        """
        Boxからテキストを抽出するヘルパーメソッド

        Args:
            box (Dict): Flexのboxオブジェクト

        Returns:
            str: 抽出されたテキスト
        """
        if isinstance(box, dict) and "contents" in box:
            for item in box["contents"]:
                if isinstance(item, dict) and item.get("type") == "text":
                    return item.get("text", "").strip()
        return ""

    def _create_main_reminder_section(self, event_content: str, date_with_weekday: str,
                                    is_input_deadline: bool, days_until: int) -> Dict:
        """
        調整さん確認・入力依頼の主要セクションを作成

        Args:
            event_content (str): イベント内容
            date_with_weekday (str): 日付（曜日付き）
            is_input_deadline (bool): 入力期限かどうか
            days_until (int): 何日後か

        Returns:
            Dict: 主要リマインダーセクション
        """
        # 場所情報を抽出
        location_info = self._extract_location_info(event_content)

        # 緊急度に応じたメッセージ
        if is_input_deadline:
            if days_until <= 1:
                main_message = "🚨 参加・欠席のご回答期限が迫っています"
                sub_message = "お忙しい中恐れ入りますが、参加可否のご回答をお願いいたします。"
                message_color = "#FF5722"
            else:
                main_message = "📝 参加・欠席のご回答をお願いします"
                sub_message = f"期限まで{days_until}日です。ご都合をお聞かせください。"
                message_color = "#FF9800"
        else:
            if days_until <= 1:
                main_message = f"🎯 {'本日' if days_until == 0 else '明日'}開催予定です"
                sub_message = "最終確認として、参加予定の方は準備をお願いします。"
                message_color = "#4CAF50"
            else:
                main_message = f"📅 {days_until}日後に開催予定です"
                sub_message = "参加可否をまだご回答いただいていない方は、お早めにお知らせください。"
                message_color = "#2196F3"

        return {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                # メインメッセージ
                {
                    "type": "text",
                    "text": main_message,
                    "size": "md",
                    "weight": "bold",
                    "color": message_color,
                    "align": "center"
                },
                {
                    "type": "text",
                    "text": sub_message,
                    "size": "sm",
                    "color": "#666666",
                    "align": "center",
                    "wrap": True,
                    "margin": "sm"
                },

                # イベント詳細情報
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
                                    "text": "📅",
                                    "size": "md",
                                    "flex": 1
                                },
                                {
                                    "type": "text",
                                    "text": date_with_weekday,
                                    "size": "md",
                                    "weight": "bold",
                                    "color": "#333333",
                                    "flex": 6
                                }
                            ]
                        }
                    ],
                    "backgroundColor": "#F5F5F5",
                    "paddingAll": "15px",
                    "cornerRadius": "8px",
                    "margin": "md"
                },

                # イベント内容全文表示
                self._create_full_event_content_section(event_content),

                # 場所情報（ある場合）
                *([{
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": "📍",
                            "size": "md",
                            "flex": 1
                        },
                        {
                            "type": "text",
                            "text": location_info,
                            "size": "sm",
                            "color": "#333333",
                            "flex": 6,
                            "wrap": True
                        }
                    ],
                    "backgroundColor": "#F5F5F5",
                    "paddingAll": "12px",
                    "cornerRadius": "6px",
                    "margin": "sm"
                }] if location_info else [])
            ]
        }

    def _create_essential_event_details(self, event_content: str) -> Dict:
        """
        イベントの重要な詳細情報のみを抽出

        Args:
            event_content (str): イベント内容

        Returns:
            Dict: 重要詳細情報セクション
        """
        lines = event_content.strip().split('\n')
        essential_items = []

        # 重要キーワードを含む行を抽出（調整さん関連は除外）
        important_keywords = ["時間", "集合", "持ち物", "注意", "連絡", "費用", "料金", "締切"]
        exclude_keywords = ["調整さん", "chouseisan", "URL", "https://", "http://"]

        for line in lines:
            line = line.strip()
            if line and len(line) > 3:  # 短すぎる行をスキップ
                # 調整さん関連の行は除外
                if any(exclude_keyword in line for exclude_keyword in exclude_keywords):
                    continue

                if any(keyword in line for keyword in important_keywords):
                    essential_items.append({
                        "type": "text",
                        "text": f"• {line}",
                        "size": "xs",
                        "color": "#555555",
                        "wrap": True
                    })

        # 重要な情報がない場合は一般的な内容を1行表示
        if not essential_items:
            # 最初の有意義な行を表示
            for line in lines:
                line = line.strip()
                if line and len(line) > 10:  # ある程度長い行
                    essential_items.append({
                        "type": "text",
                        "text": f"• {line[:50]}{'...' if len(line) > 50 else ''}",
                        "size": "xs",
                        "color": "#777777",
                        "wrap": True
                    })
                    break

        if not essential_items:  # それでも何もない場合
            essential_items.append({
                "type": "text",
                "text": "詳細は別途ご確認ください",
                "size": "xs",
                "color": "#999999"
            })

        return {
            "type": "box",
            "layout": "vertical",
            "spacing": "xs",
            "contents": essential_items[:3],  # 最大3項目まで
            "backgroundColor": "#FAFAFA",
            "paddingAll": "10px",
            "cornerRadius": "6px",
            "margin": "sm"
        }

    def _generate_sports_weather_advice(self, temperature: str, humidity: str, precipitation: str, original_advice: str) -> str:
        """
        天候情報に基づいてスポーツ向けの具体的なアドバイスを生成

        Args:
            temperature (str): 気温情報
            humidity (str): 湿度情報
            precipitation (str): 降水確率情報
            original_advice (str): 元のアドバイス

        Returns:
            str: スポーツ向けアドバイス
        """
        try:
            # 気温を数値として抽出
            temp_match = re.search(r'(\d+(?:\.\d+)?)(?:℃|°C)', temperature)
            temp_value = float(temp_match.group(1)) if temp_match else 20.0

            # 湿度を数値として抽出
            humidity_match = re.search(r'(\d+)(?:%)', humidity)
            humidity_value = int(humidity_match.group(1)) if humidity_match else 50

            # 降水確率を数値として抽出
            precipitation_match = re.search(r'(\d+)(?:%)', precipitation)
            precipitation_value = int(precipitation_match.group(1)) if precipitation_match else 0

            # スポーツ向けアドバイスの生成
            if precipitation_value >= 70:
                return "☔ 雨天のため室内での練習や雨具の準備を。滑りやすいので注意してください"
            elif precipitation_value >= 40:
                return "🌦️ 雨の可能性があります。念のため雨具を持参し、グラウンド状態にご注意を"
            elif precipitation_value >= 20:
                return "☁️ 曇り空ですが運動には適しています。急な雨に備え軽い雨具があると安心"

            # 気温に基づくアドバイス
            if temp_value >= 30:
                if humidity_value >= 70:
                    return "🥵 高温多湿です。熱中症対策必須！こまめな水分・塩分補給と適度な休憩を"
                else:
                    return "☀️ 高温注意！日陰での休憩、帽子・冷却タオルの準備、水分補給をお忘れなく"
            elif temp_value >= 25:
                if humidity_value >= 70:
                    return "💧 蒸し暑い日です。汗をかきやすいので着替えと水分補給をしっかりと"
                else:
                    return "🌤️ スポーツ日和！ただし直射日光対策と水分補給は忘れずに"
            elif temp_value >= 20:
                return "👍 運動に最適な気温です。軽い準備運動から始めて怪我の予防を心がけましょう"
            elif temp_value >= 15:
                return "🧥 少し肌寒いです。ウォーミングアップをしっかり行い、体を温めてから運動開始を"
            elif temp_value >= 10:
                return "❄️ 寒い日です。防寒対策と十分なウォーミングアップで怪我を防ぎましょう"
            else:
                return "🧣 非常に寒いです。防寒具必須！屋内での活動も検討してください"

        except Exception as e:
            print(f"スポーツアドバイス生成エラー: {e}")
            return "⚽ スポーツを楽しんでください！天候に応じた準備と安全対策をお忘れなく"

    def _create_compact_weather_section(self, location_info: Optional[str], weather_info: Dict) -> Dict:
        """
        必要最低限の天候情報セクションを作成（補足情報として）
        必須項目：会場名、気温、湿度、降水確率、一言アドバイス

        Args:
            location_info (Optional[str]): 場所情報
            weather_info (Dict): 天気情報

        Returns:
            Dict: 詳細天候情報セクション
        """
        weather_location = location_info or "会場周辺"

        # 天候情報の整理（修正されたキー名を使用）
        venue = weather_info.get("venue", weather_location)
        temperature = weather_info.get("temperature", "情報なし")
        humidity = weather_info.get("humidity", "情報なし")
        precipitation = weather_info.get("precipitation", "情報なし")
        advice = weather_info.get("advice", "天候に注意してご参加ください")

        # スポーツ向けの具体的なアドバイスに変更
        sports_advice = self._generate_sports_weather_advice(temperature, humidity, precipitation, advice)
        if sports_advice:
            advice = sports_advice

        return {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "text",
                    "text": "⚽ スポーツ向け天候情報",
                    "size": "sm",
                    "weight": "bold",
                    "color": "#4A5568"
                },
                # 会場名
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "xs",
                    "contents": [
                        {
                            "type": "text",
                            "text": "📍 会場:",
                            "size": "xs",
                            "color": "#718096",
                            "flex": 2
                        },
                        {
                            "type": "text",
                            "text": venue,
                            "size": "xs",
                            "color": "#2D3748",
                            "weight": "bold",
                            "flex": 5,
                            "wrap": True
                        }
                    ]
                },
                # 気温
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "xs",
                    "contents": [
                        {
                            "type": "text",
                            "text": "🌡️ 気温:",
                            "size": "xs",
                            "color": "#718096",
                            "flex": 2
                        },
                        {
                            "type": "text",
                            "text": temperature,
                            "size": "xs",
                            "color": "#2D3748",
                            "weight": "bold",
                            "flex": 5
                        }
                    ]
                },
                # 湿度
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "xs",
                    "contents": [
                        {
                            "type": "text",
                            "text": "💧 湿度:",
                            "size": "xs",
                            "color": "#718096",
                            "flex": 2
                        },
                        {
                            "type": "text",
                            "text": humidity,
                            "size": "xs",
                            "color": "#2D3748",
                            "weight": "bold",
                            "flex": 5
                        }
                    ]
                },
                # 降水確率
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "xs",
                    "contents": [
                        {
                            "type": "text",
                            "text": "☔ 降水確率:",
                            "size": "xs",
                            "color": "#718096",
                            "flex": 2
                        },
                        {
                            "type": "text",
                            "text": precipitation,
                            "size": "xs",
                            "color": "#2D3748",
                            "weight": "bold",
                            "flex": 5
                        }
                    ]
                },
                # 一言アドバイス
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "xs",
                    "margin": "sm",
                    "contents": [
                        {
                            "type": "text",
                            "text": "💡",
                            "size": "xs",
                            "flex": 1
                        },
                        {
                            "type": "text",
                            "text": advice,
                            "size": "xs",
                            "color": "#2B6CB0",
                            "flex": 6,
                            "wrap": True
                        }
                    ]
                },
                # 注意書き
                {
                    "type": "text",
                    "text": "※ 天候により変更の可能性があります",
                    "size": "xxs",
                    "color": "#A0AEC0",
                    "align": "center",
                    "margin": "sm"
                }
            ],
            "backgroundColor": "#F7FAFC",
            "paddingAll": "12px",
            "cornerRadius": "6px"
        }

    def _extract_weather_summary_from_base_flex(self, base_flex: Dict) -> str:
        """
        base_flexから天気情報を簡潔なサマリーとして抽出

        Args:
            base_flex (Dict): 基本の天気Flex Message

        Returns:
            str: 天気サマリー（例：「晴れ 22℃」）
        """
        try:
            if "contents" in base_flex and "body" in base_flex["contents"]:
                body_contents = base_flex["contents"]["body"].get("contents", [])

                temperature = ""
                condition = ""

                for section in body_contents:
                    if section.get("type") == "box" and "contents" in section:
                        for item in section["contents"]:
                            if item.get("type") == "box" and "contents" in item:
                                for sub_item in item["contents"]:
                                    if sub_item.get("type") == "box" and "contents" in sub_item:
                                        for text_item in sub_item["contents"]:
                                            if text_item.get("type") == "text":
                                                text = text_item.get("text", "")
                                                # 気温情報
                                                if "℃" in text and not temperature:
                                                    temperature = text.strip()
                                                # 天気情報
                                                elif any(weather in text for weather in ["晴れ", "曇り", "雨", "雪", "霧"]) and not condition:
                                                    condition = text.strip()

                if condition and temperature:
                    return f"{condition} {temperature}"
                elif condition:
                    return condition
                elif temperature:
                    return temperature
                else:
                    return "天候情報をご確認ください"

        except Exception as e:
            print(f"天気サマリー抽出エラー: {e}")

        return "天候情報をご確認ください"

    def _create_reminder_action_footer(self, is_input_deadline: bool, days_until: int, event_content: str = "") -> Dict:
        """
        シンプルな情報表示のみのフッターを作成（ボタンなし）
        当日開催の場合は集合時間とリマインド設定情報を含む

        Args:
            is_input_deadline (bool): 入力期限かどうか
            days_until (int): 何日後か
            event_content (str): イベント内容（投稿者情報抽出用）

        Returns:
            Dict: 情報表示フッター
        """
        footer_contents = []

        if is_input_deadline:
            # 入力期限の場合：確認依頼メッセージのみ
            urgency_text = "🙏 参加可否のご確認をお願いします"
            if days_until <= 1:
                urgency_text = "⚠️ 入力期限が迫っています"
        else:
            # イベント開催日の場合：開催日情報のみ
            if days_until == 0:
                urgency_text = "🎯 本日開催です"

                # 当日の場合、集合時間とリマインド情報を追加
                gathering_time = self._extract_gathering_time(event_content)
                if gathering_time:
                    reminder_time = self._calculate_reminder_time(gathering_time)
                    footer_contents.extend([
                        {
                            "type": "text",
                            "text": f"⏰ 集合時間: {gathering_time}",
                            "size": "xs",
                            "color": "#4CAF50",
                            "align": "center",
                            "weight": "bold",
                            "margin": "sm"
                        },
                        {
                            "type": "text",
                            "text": f"📱 リマインド設定: {reminder_time}（1時間前）",
                            "size": "xxs",
                            "color": "#2196F3",
                            "align": "center",
                            "margin": "xs"
                        }
                    ])
            elif days_until == 1:
                urgency_text = "🎯 明日開催です"
            else:
                urgency_text = f"📅 {days_until}日後開催予定"

        # 基本のフッターコンテンツを追加
        footer_contents.extend([
            {
                "type": "text",
                "text": urgency_text,
                "size": "sm",
                "color": "#666666",
                "align": "center",
                "weight": "bold"
            },
            {
                "type": "text",
                "text": f"詳細は個別にご確認ください（{self._extract_author_info(event_content)}）",
                "size": "xs",
                "color": "#999999",
                "align": "center",
                "margin": "xs"
            }
        ])

        return {
            "type": "box",
            "layout": "vertical",
            "contents": footer_contents,
            "paddingAll": "15px"
        }
