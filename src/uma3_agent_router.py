"""
Uma3 インテリジェント・エージェント・ルーター
【目的】ユーザーメッセージを分析して最適な専門エージェントを自動選択
【機能】FAQ検索、履歴検索、スケジュール通知などを自動選択する仕組み
【アルゴリズム】信頼度ベースのマルチエージェント選択システム
"""

# ==========================================
# STEP 1: 必要なライブラリのインポート
# ==========================================
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# LangChain関連（オプション）
try:
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_openai import ChatOpenAI
    from langchain.tools import BaseTool
except ImportError as e:
    print(f"⚠️ LangChain import error: {e}")


# ==========================================
# STEP 2: エージェントタイプの定義
# ==========================================
class AgentType(Enum):
    """
    利用可能なエージェントタイプの列挙
    【重要】新しいエージェントを追加する場合は、ここに追加し、
           _initialize_intent_patterns()と_initialize_agent_config()も更新する
    """
    FAQ_SEARCH = "faq_search"                    # よくある質問・一般情報検索
    HISTORY_SEARCH = "history_search"            # 過去の記録・履歴検索（テキスト）
    SCHEDULE_NOTIFICATION = "schedule_notification"  # 予定確認・通知機能
    REMINDER_MANAGEMENT = "reminder_management"   # リマインダー設定・管理
    TEAM_MANAGEMENT = "team_management"          # チームメンバー情報管理
    EVENT_ANALYSIS = "event_analysis"            # イベント・成績分析
    WEATHER_CONTEXT = "weather_context"          # 天気・季節コンテキスト
    GENERAL_CHAT = "general_chat"               # 一般会話・挨拶
    FLEX_HISTORY = "flex_history"               # Flex履歴カード表示（最高優先度）


# ==========================================
# STEP 3: エージェント意図データ構造の定義
# ==========================================
@dataclass
class AgentIntent:
    """
    エージェント選択結果を格納するデータクラス
    【用途】分析結果とメタデータの構造化
    """
    agent_type: AgentType          # 選択されたエージェントタイプ
    confidence: float              # 信頼度 (0.0-1.0)
    reasoning: str                 # 選択理由の説明文
    extracted_params: Dict[str, str]  # 抽出されたパラメータ
    priority: int = 1              # 優先度（低い数値=高優先度）


# ==========================================
# STEP 4: メインルータークラス
# ==========================================
class Uma3AgentRouter:
    """
    Uma3 インテリジェント・エージェント・ルーター
    【機能】メッセージ分析 → エージェント選択 → 実行指示
    【アルゴリズム】パターンマッチング + 信頼度計算 + 優先度評価
    """

    def __init__(self, llm: Optional[Any] = None):
        """
        ルーターの初期化
        【STEP 4.1】必要なコンポーネントの初期化

        Args:
            llm: LangChain LLM インスタンス（分析用、オプション）
        """
        self.llm = llm

        # STEP 4.1.1: 意図認識パターンの初期化
        self.intent_patterns = self._initialize_intent_patterns()

        # STEP 4.1.2: エージェント設定の初期化
        self.agent_config = self._initialize_agent_config()

    def _initialize_intent_patterns(self) -> Dict[AgentType, List[Dict]]:
        """
        【STEP 4.2】意図認識パターンの初期化
        【重要】新しいエージェントを追加する場合は、ここにパターンを追加

        Returns:
            各エージェントタイプに対応する認識パターンの辞書
        """
        return {
            # === FAQ検索エージェント ===
            # 一般的な質問、教えて系の問い合わせを担当
            AgentType.FAQ_SEARCH: [
                {
                    # よくある質問関連のキーワード
                    "keywords": ["FAQ", "よくある質問", "質問", "教えて", "知りたい", "どうやって"],
                    # 質問パターンの正規表現（「〜について教えて」など）
                    "patterns": [r"(.+)について教えて", r"(.+)の方法", r"(.+)はどう"],
                    # 除外キーワード（他のエージェントが担当すべき内容）
                    "negative_keywords": ["履歴", "予定", "スケジュール"]
                }
            ],

            # === 履歴検索エージェント ===
            # 過去の記録や履歴に関する問い合わせを担当
            AgentType.HISTORY_SEARCH: [
                {
                    # 履歴・過去関連のキーワード
                    "keywords": ["履歴", "過去", "前回", "以前", "昔", "記録"],
                    # 履歴検索パターンの正規表現
                    "patterns": [r"(.+)の履歴", r"過去の(.+)", r"前回の(.+)"],
                    # 除外キーワード（未来の予定は別エージェント）
                    "negative_keywords": ["予定", "未来"]
                }
            ],

            # === Flex履歴表示エージェント ===
            # カード形式での履歴表示専用エージェント
            AgentType.FLEX_HISTORY: [
                {
                    # Flex表示関連のキーワード
                    "keywords": ["F履歴", "カード", "表示", "Flex"],
                    # Flex表示パターンの正規表現
                    "patterns": [r"F履歴", r"履歴.*表示", r"カード.*表示"],
                    # 完全一致でのマッチング（優先度高）
                    "exact_matches": ["@Bot F履歴", "F履歴を表示", "履歴カード"]
                }
            ],

            # === スケジュール通知エージェント ===
            # 予定・スケジュール関連の問い合わせを担当
            AgentType.SCHEDULE_NOTIFICATION: [
                {
                    # スケジュール関連のキーワード
                    "keywords": ["予定", "スケジュール", "明日", "今日", "次", "今度", "今週", "週間"],
                    # 時間指定を含む予定パターン
                    "patterns": [r"明日の(.+)", r"今日の(.+)", r"次の(.+)", r"(.+)の予定",
                               r"今週の(.+)", r"今週(.+)", r"週間(.+)", r"この週の(.+)"],
                    # 時間を表すインジケーター
                    "time_indicators": ["明日", "今日", "来週", "来月", "今週", "この週", "週間"]
                }
            ],

            # === リマインダー管理エージェント ===
            # リマインダーの設定・管理を担当
            AgentType.REMINDER_MANAGEMENT: [
                {
                    # リマインダー関連のキーワード
                    "keywords": ["リマインダー", "通知", "覚えて", "思い出して", "忘れないで"],
                    # リマインダー設定パターン
                    "patterns": [r"(.+)をリマインド", r"(.+)を覚えて", r"(.+)の通知を"],
                    # 実行可能なアクション
                    "actions": ["設定", "追加", "削除", "確認"]
                }
            ],

            # === チーム管理エージェント ===
            # チーム情報・メンバー管理を担当
            AgentType.TEAM_MANAGEMENT: [
                {
                    # チーム関連のキーワード
                    "keywords": ["チーム", "メンバー", "選手", "コーチ", "監督", "役割"],
                    # チーム関連パターン
                    "patterns": [r"(.+)選手", r"コーチ(.+)", r"チームの(.+)"],
                    # チーム管理で実行可能なアクション
                    "actions": ["一覧", "情報", "連絡先"]
                }
            ],
            # === イベント分析エージェント ===
            # データ分析・統計処理を担当
            AgentType.EVENT_ANALYSIS: [
                {
                    # 分析関連のキーワード
                    "keywords": ["分析", "結果", "成績", "傾向", "パフォーマンス", "統計"],
                    # 分析要求パターン
                    "patterns": [r"(.+)の分析", r"(.+)の結果", r"(.+)の成績"],
                    # 分析可能な種類
                    "analysis_types": ["結果", "傾向", "成績", "記録"]
                }
            ],
            # === 天気コンテキストエージェント ===
            # 天気情報・気象条件に関する問い合わせを担当
            AgentType.WEATHER_CONTEXT: [
                {
                    # 天気関連のキーワード
                    "keywords": ["天気", "気温", "雨", "晴れ", "曇り", "雪", "季節"],
                    # 天気問い合わせパターン
                    "patterns": [r"今日の天気", r"(.+)の天気", r"天気.*どう"],
                    # 天気情報が必要なコンテキスト
                    "context_needs": ["屋外", "イベント", "練習"]
                }
            ],

            # === 一般チャットエージェント ===
            # 挨拶や雑談、その他の分類されない会話を担当（フォールバック）
            AgentType.GENERAL_CHAT: [
                {
                    # 挨拶・雑談関連のキーワード
                    "keywords": ["こんにちは", "ありがとう", "おはよう", "お疲れ", "元気"],
                    # 一般的な会話パターン
                    "patterns": [r"挨拶", r"感謝", r"雑談"],
                    # フォールバックエージェント（他が該当しない場合）
                    "fallback": True
                }
            ]
        }

    def _initialize_agent_config(self) -> Dict[AgentType, Dict]:
        """
        【STEP 4.3】エージェント設定の初期化
        【重要】各エージェントの詳細設定（優先度、ツール、応答形式など）を定義

        Returns:
            各エージェントタイプに対応する設定情報の辞書
        """
        return {
            # === FAQ検索エージェント設定 ===
            AgentType.FAQ_SEARCH: {
                "name": "FAQ検索エージェント",
                "description": "よくある質問や一般的な情報検索を担当",
                "priority": 3,  # 優先度（1=最高、5=最低）
                "tools": ["hybrid_search", "context_retrieval"],  # 使用可能ツール
                "response_format": "detailed_explanation"  # 応答形式
            },

            # === 履歴検索エージェント設定 ===
            AgentType.HISTORY_SEARCH: {
                "name": "履歴検索エージェント",
                "description": "過去の記録や履歴情報の検索を担当",
                "priority": 2,  # 高優先度
                "tools": ["history_search", "conversation_db"],  # 履歴検索ツール
                "response_format": "chronological_list"  # 時系列リスト形式
            },

            # === Flex履歴表示エージェント設定 ===
            AgentType.FLEX_HISTORY: {
                "name": "Flex履歴表示エージェント",
                "description": "リッチなカード形式での履歴表示を担当",
                "priority": 1,  # 最高優先度（専用機能）
                "tools": ["flex_message", "card_formatter"],  # Flexカード生成ツール
                "response_format": "flex_card"  # Flexカード形式
            },

            # === スケジュール通知エージェント設定 ===
            AgentType.SCHEDULE_NOTIFICATION: {
                "name": "スケジュール通知エージェント",
                "description": "予定確認や通知機能を担当",
                "priority": 2,  # 高優先度
                "tools": ["schedule_search", "date_parser"],  # スケジュール関連ツール
                "response_format": "schedule_card"  # スケジュールカード形式
            },

            # === リマインダー管理エージェント設定 ===
            AgentType.REMINDER_MANAGEMENT: {
                "name": "リマインダー管理エージェント",
                "description": "リマインダーの設定・管理を担当",
                "priority": 2,  # 高優先度
                "tools": ["reminder_tool", "date_parser"],  # リマインダーツール
                "response_format": "confirmation"  # 確認メッセージ形式
            },

            # === チーム管理エージェント設定 ===
            AgentType.TEAM_MANAGEMENT: {
                "name": "チーム管理エージェント",
                "description": "チームメンバー情報管理を担当",
                "priority": 3,  # 中優先度
                "tools": ["team_tool", "member_search"],  # チーム管理ツール
                "response_format": "member_info"  # メンバー情報形式
            },

            # === イベント分析エージェント設定 ===
            AgentType.EVENT_ANALYSIS: {
                "name": "イベント分析エージェント",
                "description": "過去のイベントや成績分析を担当",
                "priority": 3,  # 中優先度
                "tools": ["event_tool", "analysis"],  # 分析ツール
                "response_format": "analysis_report"  # 分析レポート形式
            },

            # === 天気コンテキストエージェント設定 ===
            AgentType.WEATHER_CONTEXT: {
                "name": "天気コンテキストエージェント",
                "description": "天気情報や季節コンテキストを担当",
                "priority": 4,  # 低優先度
                "tools": ["weather_tool", "season_context"],  # 天気ツール
                "response_format": "weather_info"  # 天気情報形式
            },

            # === 一般会話エージェント設定（フォールバック） ===
            AgentType.GENERAL_CHAT: {
                "name": "一般会話エージェント",
                "description": "一般的な会話や挨拶を担当",
                "priority": 5,  # 最低優先度（フォールバック）
                "tools": ["general_response"],  # 一般応答ツール
                "response_format": "casual_chat"  # カジュアル会話形式
            }
        }

    def analyze_intent(self, message: str) -> List[AgentIntent]:
        """
        【STEP 5】メッセージから意図を分析してエージェントを選択
        【重要】この関数がエージェント選択の核心機能

        処理フロー：
        1. メッセージの前処理（小文字化）
        2. 各エージェントパターンとのマッチング
        3. 信頼度スコアの計算
        4. 優先度順でのソート

        Args:
            message: ユーザーメッセージ

        Returns:
            分析されたエージェント意図のリスト（優先度順）
        """
        message_lower = message.lower()
        intents = []

        # === STEP 5.1: 各エージェントタイプについて分析 ===
        for agent_type, patterns in self.intent_patterns.items():
            for pattern_set in patterns:
                # 各パターンセットに対する信頼度計算
                confidence, reasoning, params = self._calculate_confidence(
                    message, message_lower, pattern_set
                )

                # === STEP 5.2: 信頼度閾値チェック ===
                if confidence > 0.1:  # 閾値: 10%以上の信頼度で候補とする
                    # 型注釈を明示的に追加してエラー回避
                    extracted_params: Dict[str, str] = params

                    intent = AgentIntent(
                        agent_type=agent_type,
                        confidence=confidence,
                        reasoning=reasoning,
                        extracted_params=extracted_params,
                        priority=self.agent_config[agent_type]["priority"]
                    )
                    intents.append(intent)

        # === STEP 5.3: 結果のソート（優先度 → 信頼度） ===
        # 優先度が低い数値ほど高優先度、信頼度は高いほど優先
        intents.sort(key=lambda x: (x.priority, -x.confidence))

        return intents

    def _calculate_confidence(self, message: str, message_lower: str, pattern_set: Dict) -> Tuple[float, str, Dict]:
        """
        【STEP 6】パターンセットに基づいて信頼度を計算
        【重要】エージェント選択の信頼度を決定する核心アルゴリズム

        計算要素：
        - キーワードマッチング（20-60%）
        - 正規表現パターンマッチング（30%）
        - 完全一致（100%）
        - 除外キーワード（信頼度減算）

        Returns:
            (confidence, reasoning, extracted_params): 信頼度、推論根拠、抽出パラメータ
        """
        confidence = 0.0
        reasoning_parts = []
        extracted_params: Dict[str, str] = {}

        # === STEP 6.1: 完全一致チェック（最高優先度） ===
        if "exact_matches" in pattern_set:
            for exact in pattern_set["exact_matches"]:
                if exact.lower() in message_lower:
                    confidence = 0.95  # 95%の信頼度
                    reasoning_parts.append(f"完全一致: '{exact}'")
                    return confidence, "; ".join(reasoning_parts), extracted_params

        # === STEP 6.2: キーワードマッチング ===
        if "keywords" in pattern_set:
            keyword_matches = 0
            for keyword in pattern_set["keywords"]:
                if keyword.lower() in message_lower:
                    keyword_matches += 1
                    reasoning_parts.append(f"キーワード: '{keyword}'")

            # キーワード数に応じて信頼度計算（基本30% + 追加キーワード毎に15%）
            if keyword_matches > 0:
                confidence += 0.3 + (keyword_matches * 0.15)

        # === STEP 6.3: 正規表現パターンマッチング ===
        if "patterns" in pattern_set:
            for pattern in pattern_set["patterns"]:
                matches = re.findall(pattern, message, re.IGNORECASE)
                if matches:
                    confidence += 0.25  # パターンマッチで25%追加
                    reasoning_parts.append(f"パターン: '{pattern}'")
                    # マッチした内容をパラメータとして抽出
                    if matches[0]:
                        extracted_params["extracted_term"] = matches[0]

        # === STEP 6.4: 時間指標チェック ===
        if "time_indicators" in pattern_set:
            for indicator in pattern_set["time_indicators"]:
                if indicator in message:
                    confidence += 0.2  # 時間指標で20%追加
                    reasoning_parts.append(f"時間指標: '{indicator}'")
                    extracted_params["time_context"] = indicator

        # === STEP 6.5: アクション指標チェック ===
        if "actions" in pattern_set:
            for action in pattern_set["actions"]:
                if action in message:
                    confidence += 0.15  # アクション指標で15%追加
                    reasoning_parts.append(f"アクション: '{action}'")
                    extracted_params["action"] = action

        # === STEP 6.6: 除外キーワードチェック（信頼度減算） ===
        if "negative_keywords" in pattern_set:
            for neg_keyword in pattern_set["negative_keywords"]:
                if neg_keyword.lower() in message_lower:
                    confidence *= 0.5  # 信頼度を半分に減算
                    reasoning_parts.append(f"ネガティブ: '{neg_keyword}'")

        # === STEP 6.7: フォールバック設定 ===
        if pattern_set.get("fallback", False) and confidence == 0.0:
            confidence = 0.1  # 最低限の信頼度を設定
            reasoning_parts.append("フォールバック選択")

        # 信頼度は最大100%に制限
        return min(confidence, 1.0), "; ".join(reasoning_parts), extracted_params

    def route_to_agent(self, message: str) -> Tuple[AgentType, AgentIntent]:
        """
        【STEP 7】メッセージを適切なエージェントにルーティング
        【重要】この関数が外部から呼び出される主要インターフェース

        処理フロー：
        1. 意図分析の実行
        2. 最適エージェントの選択
        3. フォールバック処理

        Args:
            message: ユーザーメッセージ

        Returns:
            (選択されたエージェントタイプ, 意図情報)
        """
        # === STEP 7.1: 意図分析の実行 ===
        intents = self.analyze_intent(message)

        # === STEP 7.2: フォールバック処理 ===
        if not intents:
            # マッチするエージェントがない場合は一般会話エージェントを使用
            fallback_intent = AgentIntent(
                agent_type=AgentType.GENERAL_CHAT,
                confidence=0.1,
                reasoning="フォールバック選択",
                extracted_params={},
                priority=5
            )
            return AgentType.GENERAL_CHAT, fallback_intent

        # === STEP 7.3: 最適エージェントの選択 ===
        # リストの先頭が最高優先度（既にソート済み）
        selected_intent = intents[0]
        return selected_intent.agent_type, selected_intent

    def get_agent_info(self, agent_type: AgentType) -> Dict:
        """
        【STEP 8】エージェント情報を取得

        Args:
            agent_type: エージェントタイプ

        Returns:
            エージェントの設定情報
        """
        return self.agent_config.get(agent_type, {})

    def explain_routing_decision(self, message: str) -> str:
        """
        【STEP 9】ルーティング決定の説明を生成
        【デバッグ用】エージェント選択の理由を詳細に説明

        Args:
            message: ユーザーメッセージ

        Returns:
            ルーティング決定の説明文（markdown形式）
        """
        intents = self.analyze_intent(message)

        if not intents:
            return "🤖 一般会話エージェントが選択されました（フォールバック）"

        selected = intents[0]
        agent_info = self.get_agent_info(selected.agent_type)

        explanation = f"""🧠 エージェント選択結果:

👤 選択エージェント: {agent_info.get('name', selected.agent_type.value)}
📝 説明: {agent_info.get('description', '説明なし')}
🎯 信頼度: {selected.confidence:.2f} ({selected.confidence * 100:.1f}%)
💭 選択理由: {selected.reasoning}
⚙️ 使用ツール: {', '.join(agent_info.get('tools', []))}
"""

        if selected.extracted_params:
            explanation += f"📋 抽出パラメータ: {selected.extracted_params}\n"

        # 他の候補も表示
        if len(intents) > 1:
            explanation += "\n🔄 その他の候補:\n"
            for intent in intents[1:3]:  # 上位3つまで
                other_info = self.get_agent_info(intent.agent_type)
                explanation += f"  • {other_info.get('name', intent.agent_type.value)} (信頼度: {intent.confidence:.2f})\n"

        return explanation


def test_agent_router():
    """エージェントルーターのテスト"""
    print("🧪 Uma3 Agent Router テスト")
    print("=" * 50)

    router = Uma3AgentRouter()

    # テストケース
    test_messages = [
        "@Bot F履歴を表示して",
        "明日の予定を教えて",
        "過去の試合結果はどうでしたか？",
        "リマインダーを設定してください",
        "チームメンバーの一覧を見たい",
        "今日の天気はどうですか？",
        "よくある質問について教えて",
        "こんにちは、元気ですか？",
        "陸功選手の成績分析をお願いします",
        "11月3日の東京都大会の詳細は？"
    ]

    for i, message in enumerate(test_messages, 1):
        print(f"\n🧮 テスト {i}: '{message}'")
        print("-" * 30)

        # ルーティング実行
        agent_type, intent = router.route_to_agent(message)
        agent_info = router.get_agent_info(agent_type)

        print(f"🎯 選択エージェント: {agent_info.get('name', agent_type.value)}")
        print(f"📊 信頼度: {intent.confidence:.3f}")
        print(f"💭 理由: {intent.reasoning}")

        # 抽出パラメータの表示
        if intent.extracted_params:
            print(f"📋 パラメータ: {intent.extracted_params}")

        # 詳細説明（最初の3つのテストケースのみ）
        if i <= 3:
            explanation = router.explain_routing_decision(message)
            print(f"\n📋 詳細説明:\n{explanation}")

    print("\n✅ Agent Router テスト完了")


if __name__ == "__main__":
    """
    【実行エントリーポイント】
    スクリプト単体実行時のテスト関数呼び出し
    """
    test_agent_router()
