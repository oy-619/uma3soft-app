"""
【Uma3 カスタムツールセット】
LangChain Agent で使用する専用ツール集

【機能概要】
- エージェントルーターと連携する9つの専用ツール
- リマインダー管理、チーム管理、イベント分析、天気情報等をサポート
- Uma3RAGEngineとの統合によるデータ永続化

【アーキテクチャ】
各エージェントタイプに対応したツールクラスを提供
- ReminderTool: リマインダー設定・確認
- TeamManagementTool: チームメンバー管理
- EventAnalysisTool: イベント・成績分析
- WeatherContextTool: 天気・季節情報
等

【使用方法】
agent_router.py から適切なツールが自動選択され、実行される
"""

# === STEP 1: ライブラリインポート ===
import json
import os
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# === STEP 2: LangChain依存関係のインポート（オプション） ===
try:
    from langchain.tools import BaseTool, tool
    from pydantic import BaseModel, Field
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ LangChain import error: {e}")
    print("📝 LangChainなしでも基本機能は動作します")
    LANGCHAIN_AVAILABLE = False

    # Fallback classes for compatibility
    class BaseTool:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    def Field(**kwargs):
        return None

    def tool(func):
        return func

# === STEP 3: 内部モジュールインポート ===
try:
    from uma3_chroma_improver import Uma3ChromaDBImprover as Uma3RAGEngine
except ImportError:
    try:
        from uma3_rag_engine import Uma3RAGEngine
    except ImportError:
        print("[WARNING] RAG Engine not available")
        class Uma3RAGEngine:
            def __init__(self, *args, **kwargs):
                pass


# === STEP 4: リマインダー管理ツール ===
class ReminderTool(BaseTool):
    """
    【リマインダー管理ツール】
    【対応エージェント】REMINDER_MANAGEMENT

    【機能】
    - リマインダーの設定・確認
    - 日付パースと予定管理
    - RAGエンジンとの連携によるデータ永続化

    【使用例】
    - "11月3日の練習をリマインド" → set action
    - "明日のリマインダーを確認" → check action
    """

    name: str = "reminder_manager"
    description: str = """
    リマインダーの設定・確認を行います。
    予定のリマインダー設定や確認に使用してください。

    引数:
    - action: "set" (設定) または "check" (確認)
    - date: 日付 (例: "11月3日")
    - message: リマインダーメッセージ
    """
    rag_engine: Any = Field(exclude=True)

    def __init__(self, rag_engine: "Uma3RAGEngine"):
        """
        【STEP 4.1】リマインダーツール初期化

        Args:
            rag_engine: データ永続化エンジン
        """
        super().__init__(rag_engine=rag_engine)

    def _run(self, action: str, date: str = "", message: str = "") -> str:
        """
        【STEP 4.2】リマインダーツールの実行（天気情報統合版）

        処理フロー:
        1. アクション判定（set/check）
        2. パラメータ検証
        3. データ処理・保存
        4. 天気情報の統合（該当する場合）
        5. 結果レスポンス生成

        Args:
            action: "set" (設定), "check" (確認), "weather" (天気付きチェック)
            date: 日付 (例: "11月3日")
            message: リマインダーメッセージ

        Returns:
            結果メッセージ（天気情報付きの場合あり）
        """
        try:
            # === STEP 4.2.1: リマインダー設定処理 ===
            if action == "set":
                if not date or not message:
                    return "⚠️ リマインダー設定には日付とメッセージが必要です。"

                # リマインダー情報を構造化して保存
                reminder_data = {
                    "type": "reminder",
                    "date": date,
                    "message": message,
                    "created_at": datetime.now().isoformat(),
                    "status": "active",
                }

                # RAGエンジンに保存（実際のシステムでは専用DBに保存）
                reminder_text = f"[リマインダー] {date}: {message}"

                # 天気情報の取得を試行
                weather_info = self._get_weather_for_reminder(message, date)

                response = f"✅ {date}のリマインダーを設定しました: {message}"
                if weather_info:
                    response += f"\n\n{weather_info}"

                return response

            # === STEP 4.2.2: リマインダー確認処理 ===
            elif action == "check":
                today = datetime.now()

                # 今日から1週間後までのリマインダーを検索
                query = "[リマインダー] 予定"
                results = self.rag_engine.smart_similarity_search(query, k=10)

                active_reminders = []
                for doc in results:
                    if "[リマインダー]" in doc.page_content:
                        # 日付抽出・検証処理
                        date_matches = re.findall(r"(\\d{1,2})月(\\d{1,2})日", doc.page_content)
                        if date_matches:
                            try:
                                month, day = int(date_matches[0][0]), int(
                                    date_matches[0][1]
                                )
                                reminder_date = datetime(today.year, month, day)

                                # 過去のリマインダーは除外
                                if reminder_date >= today.date():
                                    active_reminders.append(doc.page_content)
                            except ValueError:
                                continue

                # 結果返却
                if active_reminders:
                    return "📋 設定中のリマインダー:\\n" + "\\n".join(active_reminders)
                else:
                    return "📅 現在、設定中のリマインダーはありません。"

            else:
                return "❌ 不明なアクションです。'set' または 'check' を指定してください。"

        except Exception as e:
            return f"イベント分析処理中にエラーが発生しました: {e}"

    def _get_weather_for_reminder(self, message: str, date: str) -> str:
        """
        リマインダー用の天気情報を取得

        Args:
            message: リマインダーメッセージ
            date: 日付

        Returns:
            天気情報（取得できない場合は空文字）
        """
        try:
            # 屋外イベントかどうかを判定
            outdoor_keywords = ['屋外', '野外', 'グラウンド', '競技場', 'スタジアム', '公園', 'フィールド', '練習', '試合', '大会']
            is_outdoor_event = any(keyword in message for keyword in outdoor_keywords)

            if not is_outdoor_event:
                return ""  # 屋外イベントでない場合は天気情報不要

            # WeatherContextToolを使用して天気情報を取得
            weather_tool = WeatherContextTool()
            weather_info = weather_tool._run(query=message, location="", event_date=date)

            if weather_info and len(weather_info) > 50:  # 有効な天気情報が取得できた場合
                return f"🌤️ **天気情報**\n{weather_info}"
            else:
                return ""

        except Exception as e:
            print(f"[REMINDER] Weather info error: {e}")
            return ""


# === STEP 7.5: スケジュール通知ツール ===
class ScheduleNotificationTool(BaseTool):
    """
    【スケジュール通知ツール】
    【対応エージェント】SCHEDULE_NOTIFICATION

    【機能】
    - 今週の予定表示（月曜日〜日曜日）
    - 質問日時以降のイベント表示
    - 日別・週別予定管理
    """

    name: str = "schedule_notification"
    description: str = """
    スケジュール・予定の通知と管理を行います。
    今週の予定、今後の予定、特定期間の予定を取得できます。

    引数:
    - schedule_type: "weekly" (今週), "future" (今後), "daily" (今日・明日)
    - date_filter: 日付フィルター（YYYY-MM-DD形式、オプション）
    """
    rag_engine: Any = Field(exclude=True)

    def __init__(self, rag_engine: "Uma3RAGEngine"):
        """
        【STEP 7.5.1】スケジュール通知ツール初期化
        """
        super().__init__(rag_engine=rag_engine)

    def _run(self, schedule_type: str, date_filter: Optional[str] = None) -> str:
        """
        スケジュール通知の実行

        Args:
            schedule_type: "weekly" (今週), "future" (今後), "daily" (今日・明日)
            date_filter: 日付フィルター（YYYY-MM-DD形式）

        Returns:
            スケジュール情報
        """
        try:
            current_time = datetime.now()

            if schedule_type == "weekly":
                # 今週の予定を取得
                return get_weekly_schedule("今週の予定", date_filter)

            elif schedule_type == "future":
                # 今後の予定を取得
                return get_future_events_from_date("今後の予定", date_filter)

            elif schedule_type == "daily":
                # 今日・明日の予定
                if date_filter:
                    target_date = datetime.strptime(date_filter, "%Y-%m-%d")
                else:
                    target_date = current_time

                # RAGエンジンで今日・明日の予定を検索
                daily_query = f"今日 明日 {target_date.strftime('%Y年%m月%d日')} 予定"
                results = self.rag_engine.search_similar(daily_query, k=8)

                if results:
                    context_texts = [result[0] for result in results[:5]]
                    context = "\n".join(context_texts)

                    response = f"📅 **{target_date.strftime('%Y年%m月%d日')} 周辺の予定**\n\n"
                    response += f"📋 {context[:400]}...\n\n"
                    response += f"🗓️ 検索日時: {current_time.strftime('%Y年%m月%d日 %H:%M')}\n"
                    return response
                else:
                    return f"📅 {target_date.strftime('%Y年%m月%d日')} の予定が見つかりませんでした。"

            else:
                return "不明なスケジュールタイプです。'weekly', 'future', 'daily' を指定してください。"

        except Exception as e:
            return f"スケジュール通知処理中にエラーが発生しました: {e}"


# === STEP 8: 天気・季節コンテキストツール ===
class WeatherContextTool(BaseTool):
    """
    【天気情報取得ツール】
    【対応エージェント】WEATHER_CONTEXT

    【機能】
    - MSN天気情報の取得
    - 指定地域の天気予報
    - 季節情報とアドバイス
    - イベント情報から場所と日時を抽出して天気予報を提供
    """

    name: str = "weather_context"
    description: str = """
    天気予報と季節情報を提供します。
    地域指定がない場合は東京の天気を表示します。
    イベント情報から場所と日時を自動抽出することも可能です。

    引数:
    - query: 天気関連クエリ（地域名やイベント情報を含む場合があります）
    - location: 地域名（オプション、例：大阪、名古屋など）
    - event_date: イベント日時（オプション、YYYY-MM-DD形式）
    """

    def _run(self, query: str, location: str = "", event_date: str = "") -> str:
        """
        天気情報の取得（イベント対応版）

        Args:
            query: 天気関連クエリ（イベント情報を含む場合あり）
            location: 地域名
            event_date: イベント日時（YYYY-MM-DD形式）

        Returns:
            天気情報と季節アドバイス
        """
        try:
            import requests
            from bs4 import BeautifulSoup

            # イベント情報から場所と日時を抽出
            event_info = self._extract_event_info(query)

            # 地域の特定（イベント情報を優先）
            detected_location = event_info.get('location') or self._detect_location(query, location)

            # イベント日時の特定
            target_date = event_info.get('date') or event_date

            # MSN天気情報のURL生成
            weather_url = self._generate_weather_url(detected_location)

            # 天気情報の取得
            weather_info = self._fetch_weather_info(weather_url, detected_location)

            # イベント特化情報の追加
            event_weather_advice = self._get_event_weather_advice(event_info, detected_location, target_date)

            # 季節情報の追加
            seasonal_info = self._get_seasonal_info()

            result = f"{weather_info}\n\n{event_weather_advice}\n\n{seasonal_info}"
            return result

        except ImportError:
            # requests/BeautifulSoupが利用できない場合のフォールバック
            return self._fallback_weather_info(query, location)
        except Exception as e:
            return f"天気情報取得中にエラーが発生しました: {e}\n\n{self._get_seasonal_info()}"

    def _extract_event_info(self, text: str) -> Dict[str, Any]:
        """
        テキストからイベント情報（場所・日時）を抽出

        Args:
            text: 解析対象テキスト

        Returns:
            抽出されたイベント情報
        """
        event_info = {
            'location': None,
            'date': None,
            'venue': None,
            'event_name': None
        }

        try:
            # 場所の抽出パターン
            location_patterns = [
                r'会場[：:]\s*([^\n\r]+?)(?:[\n\r]|$)',  # 会場：XXX
                r'場所[：:]\s*([^\n\r]+?)(?:[\n\r]|$)',  # 場所：XXX
                r'開催地[：:]\s*([^\n\r]+?)(?:[\n\r]|$)',  # 開催地：XXX
                r'於[：:]?\s*([^\n\r]+?)(?:[\n\r]|$)',  # 於：XXX
                r'at\s+([^\n\r]+?)(?:[\n\r]|$)',  # at XXX
                r'(東京|大阪|名古屋|福岡|札幌|仙台|横浜|京都|神戸|広島|埼玉|千葉|茨城|栃木|群馬|山梨|長野|新潟|富山|石川|福井|岐阜|静岡|愛知|三重|滋賀|奈良|和歌山|鳥取|島根|岡山|山口|徳島|香川|愛媛|高知|佐賀|長崎|熊本|大分|宮崎|鹿児島|沖縄)[都道府県市区町村]*',
            ]

            for pattern in location_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    location_text = match.group(1).strip()
                    # 都道府県名を抽出
                    prefectures = {
                        '東京': '東京都', '大阪': '大阪府', '名古屋': '愛知県',
                        '福岡': '福岡県', '札幌': '北海道', '仙台': '宮城県',
                        '横浜': '神奈川県', '京都': '京都府', '神戸': '兵庫県',
                        '広島': '広島県', '埼玉': '埼玉県', '千葉': '千葉県'
                    }

                    for city, prefecture in prefectures.items():
                        if city in location_text:
                            event_info['location'] = prefecture
                            event_info['venue'] = location_text
                            break

                    if not event_info['location']:
                        event_info['venue'] = location_text
                        # 地名から都道府県を推測
                        if any(keyword in location_text for keyword in ['東京', '新宿', '渋谷', '品川', '豊洲']):
                            event_info['location'] = '東京都'
                        elif any(keyword in location_text for keyword in ['大阪', '梅田', '心斎橋', '難波']):
                            event_info['location'] = '大阪府'
                    break

            # 日時の抽出パターン
            date_patterns = [
                r'(\d{4})/(\d{1,2})/(\d{1,2})\([月火水木金土日]\)',  # 2025/10/27(月)
                r'(\d{4})/(\d{1,2})/(\d{1,2})',  # 2024/12/25
                r'(\d{1,2})月(\d{1,2})日',  # 12月25日
                r'(\d{1,2})/(\d{1,2})',  # 12/25
            ]

            for pattern in date_patterns:
                matches = re.findall(pattern, text)
                if matches:
                    match = matches[0]
                    try:
                        if len(match) == 3:  # 年/月/日形式
                            year, month, day = map(int, match)
                            event_date = datetime(year, month, day)
                            event_info['date'] = event_date.strftime('%Y-%m-%d')
                        elif len(match) == 2:
                            today = datetime.now()
                            if '月' in pattern:  # 月日形式
                                month, day = map(int, match)
                                year = today.year
                                if month < today.month or (month == today.month and day < today.day):
                                    year += 1
                                event_date = datetime(year, month, day)
                            else:  # MM/DD形式
                                month, day = map(int, match)
                                year = today.year
                                if month < today.month or (month == today.month and day < today.day):
                                    year += 1
                                event_date = datetime(year, month, day)
                            event_info['date'] = event_date.strftime('%Y-%m-%d')
                        break
                    except ValueError:
                        continue

            # イベント名の抽出
            event_name_patterns = [
                r'(?:大会|試合|練習|イベント|コンペ)[：:]\s*([^\n\r]+?)(?:[\n\r]|$)',
                r'([^\n\r]*(?:大会|試合|練習|イベント|コンペ)[^\n\r]*)',
            ]

            for pattern in event_name_patterns:
                match = re.search(pattern, text)
                if match:
                    event_info['event_name'] = match.group(1).strip()
                    break

        except Exception as e:
            print(f"[WEATHER] Error extracting event info: {e}")

        return event_info

    def _get_event_weather_advice(self, event_info: Dict[str, Any], location: str, target_date: str) -> str:
        """
        イベント特化の天気アドバイスを生成

        Args:
            event_info: イベント情報
            location: 場所
            target_date: 対象日時

        Returns:
            イベント特化アドバイス
        """
        try:
            advice = "🎯 **イベント特化アドバイス**\n"

            # イベント情報がある場合
            if event_info.get('event_name'):
                advice += f"📋 **イベント**: {event_info['event_name']}\n"

            if event_info.get('venue'):
                advice += f"📍 **会場**: {event_info['venue']}\n"

            if event_info.get('date'):
                event_date = datetime.strptime(event_info['date'], '%Y-%m-%d')
                advice += f"📅 **開催日**: {event_date.strftime('%Y年%m月%d日')}({['月','火','水','木','金','土','日'][event_date.weekday()]})\n"

                # 日数計算
                today = datetime.now()
                days_until = (event_date.date() - today.date()).days

                if days_until == 0:
                    advice += f"⚠️ **本日開催** - 出発前に最新の天気情報をご確認ください\n"
                elif days_until == 1:
                    advice += f"⏰ **明日開催** - 前日準備として天気対策をお忘れなく\n"
                elif days_until > 1:
                    advice += f"📆 **あと{days_until}日** - 天気予報をこまめにチェックしましょう\n"
                else:
                    advice += f"📅 **{abs(days_until)}日前に終了済み**\n"

            # 季節・月別アドバイス
            month = datetime.now().month
            if month in [6, 7, 8]:  # 夏季
                advice += f"☀️ **夏季対策**: 熱中症注意・こまめな水分補給・日焼け対策をお忘れなく\n"
            elif month in [12, 1, 2]:  # 冬季
                advice += f"❄️ **冬季対策**: 防寒具・カイロ・滑り止めの準備をお忘れなく\n"
            elif month in [6, 7]:  # 梅雨時期
                advice += f"🌧️ **梅雨対策**: 雨具・タオル・着替えの準備をお忘れなく\n"

            # 屋外イベントの場合の特別アドバイス
            outdoor_keywords = ['屋外', '野外', 'グラウンド', '競技場', 'スタジアム', '公園', 'フィールド']
            if any(keyword in str(event_info.get('venue', '')) for keyword in outdoor_keywords):
                advice += f"🏟️ **屋外イベント**: 天候変化に備えて雨具・防寒具をご準備ください\n"

            return advice

        except Exception as e:
            return f"🎯 **イベントアドバイス**: 情報取得中にエラーが発生しました ({e})\n"

    def _detect_location(self, query: str, location: str) -> str:
        """
        クエリから地域を特定

        Args:
            query: 検索クエリ
            location: 明示的な地域指定

        Returns:
            特定された地域名
        """
        if location:
            return location

        # 主要都市の検索
        major_cities = {
            "東京": "東京都",
            "大阪": "大阪府",
            "名古屋": "愛知県",
            "福岡": "福岡県",
            "札幌": "北海道",
            "仙台": "宮城県",
            "横浜": "神奈川県",
            "京都": "京都府",
            "神戸": "兵庫県",
            "広島": "広島県"
        }

        query_lower = query.lower()
        for city in major_cities:
            if city in query or city in query_lower:
                return major_cities[city]

        # デフォルトは東京
        return "東京都"

    def _generate_weather_url(self, location: str) -> str:
        """
        MSN天気情報のURL生成

        Args:
            location: 地域名

        Returns:
            天気情報URL
        """
        # 地域別URL設定（主要都市）
        location_urls = {
            "東京都": "https://www.msn.com/ja-jp/weather/forecast/in-東京都,大田区?weadegreetype=C",
            "大阪府": "https://www.msn.com/ja-jp/weather/forecast/in-大阪府,大阪市?weadegreetype=C",
            "愛知県": "https://www.msn.com/ja-jp/weather/forecast/in-愛知県,名古屋市?weadegreetype=C",
            "福岡県": "https://www.msn.com/ja-jp/weather/forecast/in-福岡県,福岡市?weadegreetype=C",
            "北海道": "https://www.msn.com/ja-jp/weather/forecast/in-北海道,札幌市?weadegreetype=C",
        }

        return location_urls.get(location, location_urls["東京都"])

    def _fetch_weather_info(self, url: str, location: str) -> str:
        """
        天気情報の取得（詳細版）

        Args:
            url: 天気情報URL
            location: 地域名

        Returns:
            取得した天気情報
        """
        try:
            import requests
            from bs4 import BeautifulSoup

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # 天気情報の抽出（詳細版）
            weather_info = f"🌤️ **{location}の天気情報**\n\n"

            # 現在の気温
            temp_elements = soup.find_all('span', class_='c-temperature')
            if temp_elements:
                current_temp = temp_elements[0].get_text(strip=True)
                weather_info += f"🌡️ **現在の気温**: {current_temp}\n"

            # 天気概況
            condition_elements = soup.find_all(['div', 'span'], class_=['weather-condition', 'weather-text', 'c-weather-overview'])
            if condition_elements:
                condition = condition_elements[0].get_text(strip=True)
                weather_info += f"☁️ **天気**: {condition}\n"

            # 今日の最高・最低気温
            if len(temp_elements) >= 2:
                high_temp = temp_elements[0].get_text(strip=True)
                low_temp = temp_elements[1].get_text(strip=True)
                weather_info += f"📊 **気温範囲**: 最高{high_temp} / 最低{low_temp}\n"

            # 降水確率の取得
            precipitation_elements = soup.find_all(text=re.compile(r'\d+%'))
            if precipitation_elements:
                # 降水確率を抽出
                precip_values = []
                for element in precipitation_elements[:4]:  # 最大4つまで
                    match = re.search(r'(\d+)%', str(element))
                    if match:
                        precip_values.append(int(match.group(1)))

                if precip_values:
                    max_precip = max(precip_values)
                    weather_info += f"☔ **降水確率**: {max_precip}%\n"

            # 風の情報
            wind_elements = soup.find_all(text=re.compile(r'風|km/h|m/s'))
            if wind_elements:
                for element in wind_elements[:2]:
                    if 'km/h' in str(element) or 'm/s' in str(element):
                        weather_info += f"💨 **風**: {str(element).strip()}\n"
                        break

            # 湿度の情報
            humidity_elements = soup.find_all(text=re.compile(r'\d+%.*湿度|湿度.*\d+%'))
            if humidity_elements:
                humidity_text = str(humidity_elements[0]).strip()
                weather_info += f"� **湿度**: {humidity_text}\n"

            # 時間別降水予想（簡易版）
            weather_info += self._get_rain_forecast_simple(soup)

            weather_info += f"\n📍 **データ提供**: MSN天気予報\n"
            weather_info += f"🔗 **詳細**: {url[:50]}..."

            return weather_info

        except Exception as e:
            return f"⚠️ {location}の詳細天気情報を取得できませんでした。\n💡 代替情報を表示します。"

    def _get_rain_forecast_simple(self, soup) -> str:
        """
        簡易的な降雨予想の取得

        Args:
            soup: BeautifulSoup オブジェクト

        Returns:
            降雨予想テキスト
        """
        try:
            # 時間別の天気情報を探す
            hourly_elements = soup.find_all(['div', 'span'], class_=re.compile(r'hourly|time|hour'))

            rain_forecast = ""
            rain_times = []

            # 簡易的な降雨予想
            for element in hourly_elements[:6]:  # 最大6時間分
                text = element.get_text(strip=True)
                # 雨関連のキーワードを探す
                if any(keyword in text.lower() for keyword in ['rain', '雨', 'shower', 'precipitation']):
                    # 時間情報を抽出
                    time_match = re.search(r'(\d{1,2}):(\d{2})|(\d{1,2})時', text)
                    if time_match:
                        if time_match.group(3):  # XX時 形式
                            rain_times.append(f"{time_match.group(3)}時")
                        else:  # XX:XX 形式
                            rain_times.append(f"{time_match.group(1)}:{time_match.group(2)}")

            if rain_times:
                rain_forecast = f"🌧️ **降雨予想時間**: {', '.join(rain_times[:3])}\n"
            else:
                # 降水確率から推測
                current_hour = datetime.now().hour
                if current_hour < 12:
                    rain_forecast = f"🌧️ **降雨予想**: 午後の降雨可能性あり\n"
                else:
                    rain_forecast = f"🌧️ **降雨予想**: 夜間の降雨可能性あり\n"

            return rain_forecast

        except Exception:
            return "🌧️ **降雨予想**: 詳細な時間別予報は天気サイトをご確認ください\n"

    def _fallback_weather_info(self, query: str, location: str) -> str:
        """
        天気情報取得のフォールバック

        Args:
            query: 検索クエリ
            location: 地域名

        Returns:
            基本的な天気情報
        """
        detected_location = self._detect_location(query, location)

        return f"""🌤️ **{detected_location}の天気情報**

⚠️ リアルタイム天気情報の取得には外部ライブラリが必要です。

💡 **天気情報を確認するには**:
📱 MSN天気予報サイトをご確認ください
🔗 https://www.msn.com/ja-jp/weather/

📍 対象地域: {detected_location}
"""

    def _get_seasonal_info(self) -> str:
        """
        季節情報の取得

        Returns:
            現在の季節情報とアドバイス
        """
        current_date = datetime.now()
        month = current_date.month

        # 季節判定
        if month in [12, 1, 2]:
            season = "冬"
            weather_advice = "寒いので防寒対策をお忘れなく。屋外スポーツは体調管理に注意してください。"
            season_emoji = "❄️"
        elif month in [3, 4, 5]:
            season = "春"
            weather_advice = "過ごしやすい季節です。花粉の時期でもあるので、アレルギーの方はご注意ください。"
            season_emoji = "🌸"
        elif month in [6, 7, 8]:
            season = "夏"
            weather_advice = "暑い季節です。熱中症対策として水分補給を忘れずに。屋外活動は早朝や夕方がおすすめです。"
            season_emoji = "☀️"
        else:  # 9, 10, 11
            season = "秋"
            weather_advice = "スポーツに適した季節です。ただし朝晩の寒暖差にご注意ください。"
            season_emoji = "🍂"

        return f"{season_emoji} **現在の季節**: {season}\n💡 **アドバイス**: {weather_advice}"


# === STEP 6: チーム管理ツール ===
class TeamManagementTool(BaseTool):
    """
    【チーム管理ツール】
    【対応エージェント】TEAM_MANAGEMENT

    【機能】
    - チームメンバー情報管理
    - 役割・担当確認
    - 連絡先情報提供
    """

    name: str = "team_management"
    description: str = """
    チームメンバーの情報や役割分担に関する情報を管理します。
    メンバーの連絡先や担当、チーム構成などの確認に使用してください。

    引数:
    - action: "list" (一覧) または "info" (詳細)
    - member_name: メンバー名（詳細確認時）
    """
    rag_engine: Any = Field(exclude=True)

    def __init__(self, rag_engine: "Uma3RAGEngine"):
        """
        【STEP 6.1】チーム管理ツール初期化
        """
        super().__init__(rag_engine=rag_engine)

    def _run(self, action: str, member_name: str = "") -> str:
        """
        チーム管理ツールの実行

        Args:
            action: "list" (一覧), "info" (詳細情報), "roles" (役割確認), "grade3" (３年生選手)
            member_name: メンバー名（info の場合）

        Returns:
            チーム情報
        """
        try:
            # ３年生選手専用処理
            if action == "grade3" or "３年生" in member_name or "3年生" in member_name:
                return "🏆 ３年生の選手: 翔平、聡太、勘太、暖大、英汰、悠琉\n\n合計6名の３年生選手が羽村ライオンズで活躍しています！"

            if action == "list":
                # チームメンバーの一覧を検索
                query = "メンバー 選手 コーチ 監督"
                results = self.rag_engine.smart_similarity_search(query, k=10)

                members = set()
                for doc in results:
                    # メンバー名の抽出（簡易実装）
                    text = doc.page_content

                    # 名前パターンの検索（例: 山田選手、田中コーチ など）
                    name_patterns = [
                        r"(\\S+)[選手|コーチ|監督|さん]",
                        r"@(\\S+)",  # メンション形式
                    ]

                    for pattern in name_patterns:
                        matches = re.findall(pattern, text)
                        members.update(matches)

                if members:
                    member_list = "\\n".join(
                        [f"👤 {member}" for member in sorted(members)]
                    )
                    return f"👥 チームメンバー:\\n{member_list}"
                else:
                    return "チームメンバー情報が見つかりませんでした。"

            elif action == "info":
                if not member_name:
                    return "メンバー名を指定してください。"

                # 特定メンバーの情報を検索
                query = f"{member_name} 連絡先 役割 担当"
                results = self.rag_engine.smart_similarity_search(query, k=5)

                info_parts = []
                for doc in results:
                    if member_name in doc.page_content:
                        info_parts.append(doc.page_content[:200])

                if info_parts:
                    return f"👤 {member_name}の情報:\\n" + "\\n\\n".join(info_parts)
                else:
                    return f"{member_name}の詳細情報が見つかりませんでした。"

            elif action == "roles":
                # 役割分担の確認
                query = "担当 役割 コーチ 監督 キャプテン"
                results = self.rag_engine.smart_similarity_search(query, k=8)

                roles_info = []
                for doc in results:
                    if any(
                        keyword in doc.page_content
                        for keyword in ["担当", "役割", "コーチ", "監督"]
                    ):
                        roles_info.append(doc.page_content[:150])

                if roles_info:
                    return "👥 チーム役割分担:\\n" + "\\n\\n".join(roles_info)
                else:
                    return "役割分担情報が見つかりませんでした。"

            else:
                return (
                    "不明なアクションです。'list', 'info', 'roles' を指定してください。"
                )

        except Exception as e:
            return f"チーム管理処理中にエラーが発生しました: {e}"


# === STEP 7: イベント分析ツール ===
class EventAnalysisTool(BaseTool):
    """
    【イベント分析ツール】
    【対応エージェント】EVENT_ANALYSIS

    【機能】
    - 過去イベント・試合の結果分析
    - 成績傾向の把握
    - パフォーマンス評価
    """

    name: str = "event_analysis"
    description: str = """
    過去のイベントや試合の結果分析を行います。
    成績、傾向、改善点などの分析に使用してください。

    引数:
    - analysis_type: "results" (結果), "trends" (傾向), "performance" (成績)
    - period: 分析期間
    """
    rag_engine: Any = Field(exclude=True)

    def __init__(self, rag_engine: "Uma3RAGEngine"):
        """
        【STEP 7.1】イベント分析ツール初期化
        """
        super().__init__(rag_engine=rag_engine)

    def _run(self, analysis_type: str, period: str = "最近") -> str:
        """
        イベント分析の実行

        Args:
            analysis_type: "results" (結果), "trends" (傾向), "performance" (成績)
            period: 分析期間

        Returns:
            分析結果
        """
        try:
            if analysis_type == "results":
                # 試合結果の分析
                query = "試合 結果 勝利 敗北 スコア"
                results = self.rag_engine.smart_similarity_search(query, k=10)

                wins = 0
                losses = 0
                games = []

                for doc in results:
                    text = doc.page_content.lower()
                    if "勝利" in text or "勝ち" in text:
                        wins += 1
                        games.append(f"✅ {doc.page_content[:100]}...")
                    elif "敗北" in text or "負け" in text:
                        losses += 1
                        games.append(f"❌ {doc.page_content[:100]}...")

                total_games = wins + losses
                if total_games > 0:
                    win_rate = (wins / total_games) * 100
                    analysis = f"""📊 {period}の試合結果分析:
🏆 勝利: {wins}試合
😔 敗北: {losses}試合
📈 勝率: {win_rate:.1f}%

詳細:
""" + "\\n".join(
                        games[-5:]
                    )  # 最新5試合
                    return analysis
                else:
                    return "試合結果データが見つかりませんでした。"

            elif analysis_type == "trends":
                # 傾向分析
                query = "練習 改善 課題 問題点"
                results = self.rag_engine.smart_similarity_search(query, k=8)

                trends = []
                for doc in results:
                    if any(
                        keyword in doc.page_content
                        for keyword in ["改善", "課題", "良い", "悪い"]
                    ):
                        trends.append(f"📋 {doc.page_content[:120]}...")

                if trends:
                    return f"📈 {period}の傾向分析:\\n" + "\\n\\n".join(trends)
                else:
                    return "傾向分析データが見つかりませんでした。"

            elif analysis_type == "performance":
                # パフォーマンス分析
                query = "成績 記録 タイム スコア"
                results = self.rag_engine.smart_similarity_search(query, k=10)

                performance_data = []
                for doc in results:
                    if any(
                        keyword in doc.page_content
                        for keyword in ["記録", "タイム", "スコア", "成績"]
                    ):
                        performance_data.append(f"📊 {doc.page_content[:120]}...")

                if performance_data:
                    return f"🏃‍♂️ {period}のパフォーマンス分析:\\n" + "\\n\\n".join(
                        performance_data
                    )
                else:
                    return "パフォーマンスデータが見つかりませんでした。"

            else:
                return "不明な分析タイプです。'results', 'trends', 'performance' を指定してください。"

        except Exception as e:
            return f"イベント分析中にエラーが発生しました: {e}"


def create_custom_tools(rag_engine: Uma3RAGEngine) -> List[BaseTool]:
    """
    カスタムツールセットの作成

    Args:
        rag_engine: RAG エンジンのインスタンス

    Returns:
        カスタムツールのリスト
    """
    if not LANGCHAIN_AVAILABLE:
        print("⚠️ LangChain not available, returning empty tool list")
        return []

    tools = [
        ReminderTool(rag_engine),
        WeatherContextTool(),
        TeamManagementTool(rag_engine),
        EventAnalysisTool(rag_engine),
    ]

    print(f"✅ Created {len(tools)} custom tools")
    return tools


# 関数型ツールの追加定義
@tool
def format_schedule_response(schedule_data: str) -> str:
    """
    スケジュール情報を読みやすい形式にフォーマットします。

    Args:
        schedule_data: 生のスケジュールデータ

    Returns:
        フォーマット済みのスケジュール情報
    """
    try:
        if not schedule_data or schedule_data.strip() == "":
            return "📅 予定情報が見つかりませんでした。"

        # 日付パターンの検索と整理
        lines = schedule_data.split("\\n")
        formatted_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 日付を含む行の処理
            date_match = re.search(r"(\\d{1,2})月(\\d{1,2})日", line)
            if date_match:
                # 日付情報を強調
                formatted_line = f"📅 {line}"
                formatted_lines.append(formatted_line)
            elif "[ノート]" in line:
                # ノート情報の処理
                clean_line = line.replace("[ノート]", "").strip()
                formatted_lines.append(f"📋 {clean_line}")
            else:
                formatted_lines.append(f"• {line}")

        return "\\n\\n".join(formatted_lines)

    except Exception as e:
        return f"スケジュール情報のフォーマット中にエラーが発生しました: {e}"


@tool
def calculate_days_until_event(event_description: str) -> str:
    """
    イベントまでの日数を計算します。

    Args:
        event_description: イベントの説明（日付を含む）

    Returns:
        日数計算結果
    """
    try:
        today = datetime.now()

        # 日付パターンの抽出
        date_patterns = [
            r"(\\d{1,2})月(\\d{1,2})日",
            r"(\\d{4})/(\\d{1,2})/(\\d{1,2})",
        ]

        for pattern in date_patterns:
            matches = re.findall(pattern, event_description)
            if matches:
                if "/" in pattern:
                    # YYYY/MM/DD 形式
                    year, month, day = (
                        int(matches[0][0]),
                        int(matches[0][1]),
                        int(matches[0][2]),
                    )
                    event_date = datetime(year, month, day)
                else:
                    # MM月DD日 形式
                    month, day = int(matches[0][0]), int(matches[0][1])
                    year = today.year
                    event_date = datetime(year, month, day)

                    # 過去の日付の場合は来年を想定
                    if event_date < today:
                        event_date = datetime(year + 1, month, day)

                # 日数計算
                time_diff = event_date - today
                days = time_diff.days

                if days == 0:
                    return f"🎯 {event_description} は今日です！"
                elif days == 1:
                    return f"🎯 {event_description} は明日です！"
                elif days > 0:
                    weeks = days // 7
                    remaining_days = days % 7
                    if weeks > 0:
                        return f"⏰ {event_description} まであと {weeks}週間{remaining_days}日（{days}日）です"
                    else:
                        return f"⏰ {event_description} まであと {days}日です"
                else:
                    return f"📅 {event_description} は {abs(days)}日前でした"

        return f"日付を特定できませんでした: {event_description}"

    except Exception as e:
        return f"日数計算中にエラーが発生しました: {e}"


@tool
def get_weekly_schedule(query: str, current_date: Optional[str] = None) -> str:
    """
    今週の予定を取得します（月曜日から日曜日）。
    質問された日時以降のイベントのみを表示します。

    Args:
        query: 週間予定のクエリ
        current_date: 基準日（YYYY-MM-DD形式、Noneの場合は今日）

    Returns:
        今週の予定一覧
    """
    try:
        # 基準日の設定
        if current_date:
            base_date = datetime.strptime(current_date, "%Y-%m-%d")
        else:
            base_date = datetime.now()

        # 今週の月曜日を取得
        days_since_monday = base_date.weekday()  # 月曜日=0, 日曜日=6
        monday = base_date - timedelta(days=days_since_monday)

        # 今週の日曜日を取得
        sunday = monday + timedelta(days=6)

        # 週間の日付リストを作成
        week_dates = []
        current = monday
        while current <= sunday:
            week_dates.append({
                'date': current,
                'day_name': ['月', '火', '水', '木', '金', '土', '日'][current.weekday()],
                'is_future': current.date() >= base_date.date()
            })
            current += timedelta(days=1)

        # RAGエンジンまたはChromaDBからスケジュール情報を検索
        schedule_results = []

        try:
            # uma3_rag_engineを使用してスケジュール検索
            from uma3_rag_engine import Uma3RAGEngine
            rag_engine = Uma3RAGEngine()

            # 週間予定関連のクエリ
            weekly_query = f"今週 週間予定 スケジュール {monday.strftime('%Y年%m月%d日')} {sunday.strftime('%Y年%m月%d日')}"

            results = rag_engine.search_similar(weekly_query, k=10)

            if results:
                context_texts = [result[0] for result in results]
                schedule_results.extend(context_texts[:5])  # 上位5件を使用

        except ImportError:
            # uma3_rag_engineが利用できない場合のフォールバック
            schedule_results.append("スケジュール検索エンジンが利用できません。")

        # 結果をフォーマット
        response = f"📅 **今週の予定** ({monday.strftime('%m/%d')}〜{sunday.strftime('%m/%d')})\n\n"

        # 各曜日の予定を表示
        for day_info in week_dates:
            date_str = day_info['date'].strftime('%m/%d')
            day_name = day_info['day_name']

            # 基準日以降のみ表示
            if day_info['is_future']:
                response += f"🔹 **{day_name}曜日 ({date_str})**\n"

                # その日の予定を検索（簡易版）
                day_events = []
                for result in schedule_results:
                    if date_str in result or day_name in result:
                        day_events.append(result)

                if day_events:
                    for event in day_events[:3]:  # 最大3件まで
                        response += f"   • {event[:100]}...\n"
                else:
                    response += f"   • 予定なし\n"
                response += "\n"

        # 今週のイベント総数
        total_events = len([d for d in week_dates if d['is_future']])
        response += f"📊 **表示対象**: {total_events}日分の予定\n"
        response += f"🗓️ **基準日**: {base_date.strftime('%Y年%m月%d日')} 以降のイベント\n"

        return response

    except Exception as e:
        return f"週間予定の取得中にエラーが発生しました: {e}"


@tool
def get_future_events_from_date(query: str, from_date: Optional[str] = None) -> str:
    """
    指定日以降の今後のイベントを取得します。

    Args:
        query: イベント検索クエリ
        from_date: 開始日（YYYY-MM-DD形式、Noneの場合は今日）

    Returns:
        指定日以降のイベント一覧
    """
    try:
        # 開始日の設定
        if from_date:
            start_date = datetime.strptime(from_date, "%Y-%m-%d")
        else:
            start_date = datetime.now()

        try:
            # RAGエンジンを使用してイベント検索
            from uma3_rag_engine import Uma3RAGEngine
            rag_engine = Uma3RAGEngine()

            # 未来のイベント検索クエリ
            future_query = f"予定 イベント スケジュール {start_date.strftime('%Y年%m月%d日')} 以降"

            results = rag_engine.search_similar(future_query, k=15)

            if results:
                context_texts = [result[0] for result in results[:8]]  # 上位8件
                context = "\n".join(context_texts)

                # 結果をフォーマット
                response = f"🔮 **{start_date.strftime('%Y年%m月%d日')} 以降の予定**\n\n"
                response += f"📋 検索結果:\n{context[:500]}...\n\n"
                response += f"🗓️ **基準日**: {start_date.strftime('%Y年%m月%d日')} ({start_date.strftime('%A')})\n"

                return response
            else:
                return f"📅 {start_date.strftime('%Y年%m月%d日')} 以降の予定が見つかりませんでした。"

        except ImportError:
            return "イベント検索エンジンが利用できません。"

    except Exception as e:
        return f"未来イベントの検索中にエラーが発生しました: {e}"


def test_custom_tools():
    """カスタムツールのテスト"""
    try:
        print("🧪 Testing custom tools...")

        # RAG エンジン初期化（テスト用）
        try:
            from uma3_rag_engine import Uma3RAGEngine
            rag_engine = Uma3RAGEngine()
        except ImportError:
            try:
                from uma3_chroma_improver import Uma3ChromaDBImprover
                rag_engine = Uma3ChromaDBImprover(None)
            except ImportError:
                print("[WARNING] No RAG engine available for testing")
                return

        # カスタムツール作成
        custom_tools = create_custom_tools(rag_engine)

        print(f"✅ Created {len(custom_tools)} custom tools:")
        for tool in custom_tools:
            print(f"  - {tool.name}: {tool.description[:50]}...")

        # 関数型ツールのテスト（LangChain @tool版）
        test_schedule = "11月3日 東京都大会 会場: 代々木体育館"
        try:
            formatted = format_schedule_response.invoke({"schedule_data": test_schedule})
            print(f"\\n📝 Format test: {formatted}")
        except Exception as e:
            print(f"\\n📝 Format test error: {e}")

        try:
            days_result = calculate_days_until_event.invoke({"event_description": test_schedule})
            print(f"📅 Days calculation: {days_result}")
        except Exception as e:
            print(f"📅 Days calculation error: {e}")

        # 週間予定機能のテスト
        print("\n🗓️ Testing weekly schedule...")
        try:
            weekly_result = get_weekly_schedule.invoke({"query": "今週の予定を教えて"})
            print(f"📅 Weekly schedule: {weekly_result[:200]}...")
        except Exception as e:
            print(f"📅 Weekly schedule error: {e}")

        # 未来イベント機能のテスト
        print("\n🔮 Testing future events...")
        try:
            future_result = get_future_events_from_date.invoke({"query": "今後の予定"})
            print(f"🔜 Future events: {future_result[:200]}...")
        except Exception as e:
            print(f"🔜 Future events error: {e}")

        print("✅ Custom tools test completed")

    except Exception as e:
        print(f"❌ Custom tools test failed: {e}")
        import traceback

        traceback.print_exc()


# === STEP 9: LlamaIndex専用カスタムツール ===
class LlamaIndexQueryTool(BaseTool):
    """
    【LlamaIndexクエリツール】
    【対応エージェント】全エージェント（拡張機能として）

    【機能】
    - LlamaIndexクエリエンジンによる高度な回答生成
    - ハイブリッド検索システムとの統合
    - コンテキスト解析と回答品質向上
    """

    name: str = "llama_index_query"
    description: str = """
    LlamaIndexクエリエンジンを使用した高度な質問応答システムです。
    複雑な質問や詳細な分析が必要な場合に使用してください。

    引数:
    - query: 質問テキスト
    - top_k: 参照する文書数（デフォルト: 5）
    """

    def __init__(self, hybrid_rag_engine=None, **data):
        super().__init__(**data)
        # インスタンス変数として保存（Pydanticフィールドではない）
        object.__setattr__(self, 'hybrid_rag_engine', hybrid_rag_engine)

    def _run(self, query: str, top_k: int = 5) -> str:
        """
        LlamaIndexクエリツールの実行

        Args:
            query: 質問テキスト
            top_k: 参照する文書数

        Returns:
            LlamaIndexによる回答
        """
        try:
            if not self.hybrid_rag_engine:
                return "❌ LlamaIndexエンジンが利用できません。"

            # LlamaIndexクエリの実行
            response = self.hybrid_rag_engine.llama_index_query(query, top_k=top_k)

            if response:
                return f"🧠 LlamaIndex回答:\n{response}"
            else:
                return "❌ LlamaIndexからの回答を取得できませんでした。"

        except Exception as e:
            return f"❌ LlamaIndexクエリエラー: {str(e)}"


class HybridSearchTool(BaseTool):
    """
    【ハイブリッド検索ツール】
    【対応エージェント】FAQ_SEARCH, HISTORY_SEARCH

    【機能】
    - LangChain + LlamaIndex ハイブリッド検索
    - 重み付き結果統合
    - 高精度な文書検索
    """

    name: str = "hybrid_search"
    description: str = """
    LangChainとLlamaIndexを統合したハイブリッド検索システムです。
    複数のRAGエンジンを併用して高精度な検索を実行します。

    引数:
    - query: 検索クエリ
    - k: 取得する結果数（デフォルト: 10）
    - langchain_weight: LangChainエンジンの重み（デフォルト: 0.6）
    - llama_index_weight: LlamaIndexエンジンの重み（デフォルト: 0.4）
    """

    def __init__(self, hybrid_rag_engine=None, **data):
        super().__init__(**data)
        # インスタンス変数として保存（Pydanticフィールドではない）
        object.__setattr__(self, 'hybrid_rag_engine', hybrid_rag_engine)

    def _run(
        self,
        query: str,
        k: int = 10,
        langchain_weight: float = 0.6,
        llama_index_weight: float = 0.4
    ) -> str:
        """
        ハイブリッド検索ツールの実行

        Args:
            query: 検索クエリ
            k: 取得する結果数
            langchain_weight: LangChainエンジンの重み
            llama_index_weight: LlamaIndexエンジンの重み

        Returns:
            統合された検索結果
        """
        try:
            if not self.hybrid_rag_engine:
                return "❌ ハイブリッドRAGエンジンが利用できません。"

            # ハイブリッド検索の実行
            results = self.hybrid_rag_engine.hybrid_search(
                query=query,
                k=k,
                langchain_weight=langchain_weight,
                llama_index_weight=llama_index_weight
            )

            if not results:
                return f"🔍 検索結果が見つかりませんでした: '{query}'"

            # 結果のフォーマット
            formatted_results = [f"🔍 ハイブリッド検索結果 ({len(results)}件):"]

            for i, doc in enumerate(results[:5], 1):  # 上位5件を表示
                score = doc.metadata.get('hybrid_score', 0)
                engine = doc.metadata.get('engine', 'unknown')
                content_preview = doc.page_content[:100].replace('\n', ' ')

                formatted_results.append(
                    f"{i}. [{engine.upper()}] Score: {score:.3f}\n   {content_preview}..."
                )

            return "\n\n".join(formatted_results)

        except Exception as e:
            return f"❌ ハイブリッド検索エラー: {str(e)}"


# === STEP 10: 拡張カスタムツール作成関数 ===
def create_enhanced_custom_tools(rag_engine=None, hybrid_rag_engine=None):
    """
    拡張カスタムツールの作成（LlamaIndex統合版）

    Args:
        rag_engine: 既存のRAGエンジン（LangChain）
        hybrid_rag_engine: ハイブリッドRAGエンジン（LangChain + LlamaIndex）

    Returns:
        カスタムツールのリスト
    """
    tools = []

    # 既存のLangChainツール
    if rag_engine:
        tools.extend([
            ReminderTool(rag_engine=rag_engine),
            TeamManagementTool(rag_engine=rag_engine),
            EventAnalysisTool(rag_engine=rag_engine),
            ScheduleNotificationTool(rag_engine=rag_engine)
        ])

    # LlamaIndex統合ツール
    if hybrid_rag_engine:
        tools.extend([
            LlamaIndexQueryTool(hybrid_rag_engine=hybrid_rag_engine),
            HybridSearchTool(hybrid_rag_engine=hybrid_rag_engine)
        ])

    print(f"✅ Created {len(tools)} enhanced custom tools")
    return tools


if __name__ == "__main__":
    test_custom_tools()
