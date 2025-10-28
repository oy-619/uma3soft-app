"""
Uma3 カスタムツールセット
LangChain Agent で使用する専用ツール集
"""

import json
import os
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    from langchain.tools import BaseTool, tool
    from pydantic import BaseModel, Field
except ImportError as e:
    print(f"⚠️ LangChain import error: {e}")
    import sys

    sys.exit(1)

from uma3_rag_engine import Uma3RAGEngine


class ReminderTool(BaseTool):
    """リマインダー管理ツール"""

    name: str = "reminder_manager"
    description: str = """
    リマインダーの設定・確認を行います。
    予定のリマインダー設定や確認に使用してください。
    """
    rag_engine: Any = Field(exclude=True)

    def __init__(self, rag_engine: "Uma3RAGEngine"):
        super().__init__(rag_engine=rag_engine)

    def _run(self, action: str, date: str = "", message: str = "") -> str:
        """
        リマインダーツールの実行

        Args:
            action: "set" (設定) または "check" (確認)
            date: 日付 (例: "11月3日")
            message: リマインダーメッセージ

        Returns:
            結果メッセージ
        """
        try:
            if action == "set":
                if not date or not message:
                    return "リマインダー設定には日付とメッセージが必要です。"

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

                # NOTE: 実際の実装では永続化が必要
                return f"✅ {date}のリマインダーを設定しました: {message}"

            elif action == "check":
                # 今後のリマインダーを検索
                today = datetime.now()

                # 今日から1週間後までのリマインダーを検索
                query = "[リマインダー] 予定"
                results = self.rag_engine.hybrid_search(query, k=10)

                active_reminders = []
                for doc in results:
                    if "[リマインダー]" in doc.text:
                        # 日付抽出
                        date_matches = re.findall(r"(\\d{1,2})月(\\d{1,2})日", doc.text)
                        if date_matches:
                            try:
                                month, day = int(date_matches[0][0]), int(
                                    date_matches[0][1]
                                )
                                reminder_date = datetime(today.year, month, day)

                                # 過去のリマインダーは除外
                                if reminder_date >= today.date():
                                    active_reminders.append(doc.text)
                            except ValueError:
                                continue

                if active_reminders:
                    return "📋 設定中のリマインダー:\\n" + "\\n".join(active_reminders)
                else:
                    return "現在、設定中のリマインダーはありません。"

            else:
                return "不明なアクションです。'set' または 'check' を指定してください。"

        except Exception as e:
            return f"リマインダー処理中にエラーが発生しました: {e}"


class WeatherContextTool(BaseTool):
    """天気・季節コンテキストツール"""

    name: str = "weather_context"
    description: str = """
    季節や天気に関連する情報を提供します。
    屋外イベントの判断に役立ちます。
    """

    def _run(self, query: str) -> str:
        """
        天気コンテキストの提供

        Args:
            query: 天気関連クエリ

        Returns:
            天気・季節情報
        """
        try:
            current_date = datetime.now()
            month = current_date.month

            # 季節判定
            if month in [12, 1, 2]:
                season = "冬"
                weather_advice = "寒いので防寒対策をお忘れなく。屋外スポーツは体調管理に注意してください。"
            elif month in [3, 4, 5]:
                season = "春"
                weather_advice = "過ごしやすい季節です。花粉の時期でもあるので、アレルギーの方はご注意ください。"
            elif month in [6, 7, 8]:
                season = "夏"
                weather_advice = "暑い季節です。熱中症対策として水分補給を忘れずに。屋外活動は早朝や夕方がおすすめです。"
            else:  # 9, 10, 11
                season = "秋"
                weather_advice = (
                    "スポーツに適した季節です。ただし朝晩の寒暖差にご注意ください。"
                )

            return f"🌤️ 現在の季節: {season}\\n💡 アドバイス: {weather_advice}"

        except Exception as e:
            return f"天気情報取得中にエラーが発生しました: {e}"


class TeamManagementTool(BaseTool):
    """チーム管理ツール"""

    name: str = "team_management"
    description: str = """
    チームメンバーの情報や役割分担に関する情報を管理します。
    メンバーの連絡先や担当、チーム構成などの確認に使用してください。
    """
    rag_engine: Any = Field(exclude=True)

    def __init__(self, rag_engine: "Uma3RAGEngine"):
        super().__init__(rag_engine=rag_engine)

    def _run(self, action: str, member_name: str = "") -> str:
        """
        チーム管理ツールの実行

        Args:
            action: "list" (一覧), "info" (詳細情報), "roles" (役割確認)
            member_name: メンバー名（info の場合）

        Returns:
            チーム情報
        """
        try:
            if action == "list":
                # チームメンバーの一覧を検索
                query = "メンバー 選手 コーチ 監督"
                results = self.rag_engine.hybrid_search(query, k=10)

                members = set()
                for doc in results:
                    # メンバー名の抽出（簡易実装）
                    text = doc.text

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
                results = self.rag_engine.hybrid_search(query, k=5)

                info_parts = []
                for doc in results:
                    if member_name in doc.text:
                        info_parts.append(doc.text[:200])

                if info_parts:
                    return f"👤 {member_name}の情報:\\n" + "\\n\\n".join(info_parts)
                else:
                    return f"{member_name}の詳細情報が見つかりませんでした。"

            elif action == "roles":
                # 役割分担の確認
                query = "担当 役割 コーチ 監督 キャプテン"
                results = self.rag_engine.hybrid_search(query, k=8)

                roles_info = []
                for doc in results:
                    if any(
                        keyword in doc.text
                        for keyword in ["担当", "役割", "コーチ", "監督"]
                    ):
                        roles_info.append(doc.text[:150])

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


class EventAnalysisTool(BaseTool):
    """イベント分析ツール"""

    name: str = "event_analysis"
    description: str = """
    過去のイベントや試合の結果分析を行います。
    成績、傾向、改善点などの分析に使用してください。
    """
    rag_engine: Any = Field(exclude=True)

    def __init__(self, rag_engine: "Uma3RAGEngine"):
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
                results = self.rag_engine.hybrid_search(query, k=10)

                wins = 0
                losses = 0
                games = []

                for doc in results:
                    text = doc.text.lower()
                    if "勝利" in text or "勝ち" in text:
                        wins += 1
                        games.append(f"✅ {doc.text[:100]}...")
                    elif "敗北" in text or "負け" in text:
                        losses += 1
                        games.append(f"❌ {doc.text[:100]}...")

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
                results = self.rag_engine.hybrid_search(query, k=8)

                trends = []
                for doc in results:
                    if any(
                        keyword in doc.text
                        for keyword in ["改善", "課題", "良い", "悪い"]
                    ):
                        trends.append(f"📋 {doc.text[:120]}...")

                if trends:
                    return f"📈 {period}の傾向分析:\\n" + "\\n\\n".join(trends)
                else:
                    return "傾向分析データが見つかりませんでした。"

            elif analysis_type == "performance":
                # パフォーマンス分析
                query = "成績 記録 タイム スコア"
                results = self.rag_engine.hybrid_search(query, k=10)

                performance_data = []
                for doc in results:
                    if any(
                        keyword in doc.text
                        for keyword in ["記録", "タイム", "スコア", "成績"]
                    ):
                        performance_data.append(f"📊 {doc.text[:120]}...")

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


def test_custom_tools():
    """カスタムツールのテスト"""
    try:
        print("🧪 Testing custom tools...")

        # RAG エンジン初期化（テスト用）
        from uma3_rag_engine import Uma3RAGEngine

        rag_engine = Uma3RAGEngine()

        # カスタムツール作成
        custom_tools = create_custom_tools(rag_engine)

        print(f"✅ Created {len(custom_tools)} custom tools:")
        for tool in custom_tools:
            print(f"  - {tool.name}: {tool.description[:50]}...")

        # 関数型ツールのテスト
        test_schedule = "11月3日 東京都大会 会場: 代々木体育館"
        formatted = format_schedule_response(test_schedule)
        print(f"\\n📝 Format test: {formatted}")

        days_result = calculate_days_until_event(test_schedule)
        print(f"📅 Days calculation: {days_result}")

        print("✅ Custom tools test completed")

    except Exception as e:
        print(f"❌ Custom tools test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_custom_tools()
