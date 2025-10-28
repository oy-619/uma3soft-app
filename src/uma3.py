"""
【Uma3 LINE Bot メインアプリケーション】
FlaskとLINE Bot SDKを使用したLINE Botアプリケーション

【主な機能】
- インテリジェントエージェントルーティングシステム
- Flex Message履歴表示
- 選手情報管理（28名対応）
- RAGエンジン統合
- リマインダー・スケジュール管理

【アーキテクチャ】
- Flask Webアプリケーション
- LINE Bot SDK v3
- Uma3AgentRouter（エージェント自動選択）
- Uma3RAGEngine（データ検索・保存）
- カスタムツールセット
"""

from typing import Optional

# === STEP 1: 選手情報管理システム ===
class ExpandablePlayerInfoHandler:
    """
    【拡張可能選手情報ハンドラー】
    【機能】選手名検出・管理システム（28名対応）

    【特徴】
    - 動的選手情報管理
    - メッセージからの選手名自動検出
    - 学習・拡張機能サポート
    """

    def __init__(self):
        """
        【STEP 1.1】選手情報ハンドラー初期化
        """
        # === 確認済み選手（28名） ===
        self.confirmed_players = [
            "陸功", "湊", "錬", "南", "統司", "春輝", "新", "由眞", "心寧", "唯浬", "朋樹", "佑多", "穂美",
            "翔平", "尚真", "柚希", "心翔", "広起", "想真", "奏", "英汰", "聡太", "暖大", "悠琉", "陽", "美玖里", "優", "勘太"
        ]

        # 候補選手（更新版 - 0名）
        self.potential_players = []

        # 全選手
        self.all_players = self.confirmed_players + self.potential_players
        self.total_players = len(self.all_players)
        self.team_name = "馬三ソフト"

        # 学習・更新機能
        self.expandable = True
        self.can_learn_new_players = True
        self.batch_learning_supported = True

        # 一括更新情報
        self.last_batch_update = "2025-10-28T08:56:42"
        self.batch_update_count = 16

    def find_player_in_message(self, message: str) -> Optional[str]:
        """メッセージから選手名を検出（拡張版）"""
        for player in self.all_players:
            # 直接マッチング
            patterns = [
                player,
                f'{player}選手',
                f'{player}君',
                f'{player}さん',
                f'{player}について',
                f'{player}の',
                f'{player}は',
                f'{player}が'
            ]

            for pattern in patterns:
                if pattern in message:
                    return player

        return None

    def get_player_status(self, player_name: str) -> str:
        """選手のステータス取得"""
        if player_name in self.confirmed_players:
            return 'confirmed'
        elif player_name in self.potential_players:
            return 'potential'
        else:
            return 'unknown'

    def handle_message(self, message: str) -> Optional[str]:
        """メッセージハンドリング（拡張版）"""
        detected_player = self.find_player_in_message(message)

        if detected_player:
            status = self.get_player_status(detected_player)
            player_index = self.all_players.index(detected_player) + 1

            if status == 'confirmed':
                # 翔平の特別処理（候補から確認済みに昇格）
                if detected_player == "翔平":
                    return f"{detected_player}選手についてお答えします。{detected_player}選手は{self.team_name}の確認済み選手として新たに正式登録されました。"
                else:
                    return f"{detected_player}選手についてお答えします。{detected_player}選手は{self.team_name}の確認済み選手で、{player_index}番目に登録されています。"
            elif status == 'potential':
                return f"{detected_player}選手についてお答えします。{detected_player}選手は分析により発見された{self.team_name}のメンバーの可能性があります。詳細情報をお持ちでしたら教えてください。"

        # チーム全体への質問
        team_keywords = ['選手', 'チーム', '馬三ソフト', 'メンバー', '参加者']
        if any(keyword in message for keyword in team_keywords):
            if '一覧' in message or 'リスト' in message:
                confirmed_list = ', '.join(self.confirmed_players)
                if self.potential_players:
                    potential_list = ', '.join(self.potential_players)
                    return f"選手一覧：\n確認済み選手（{len(self.confirmed_players)}名）: {confirmed_list}\n候補選手（{len(self.potential_players)}名）: {potential_list}"
                else:
                    return f"確認済み選手一覧（{len(self.confirmed_players)}名）: {confirmed_list}"
            elif '何人' in message or '人数' in message:
                return f"{self.team_name}の現在の選手情報は{self.total_players}名です（確認済み{len(self.confirmed_players)}名、候補{len(self.potential_players)}名）。"
            elif '更新' in message or '新しい' in message:
                return f"最新の一括更新で{self.batch_update_count}名の選手情報をいただき、システムに統合いたしました。現在{self.total_players}名の選手情報があります。"
            else:
                return f"{self.team_name}には現在{self.total_players}名の選手情報があります。確認済み{len(self.confirmed_players)}名、候補{len(self.potential_players)}名です。どの選手について詳しく知りたいですか？"

        return None

    def add_new_player(self, player_name: str, status: str = 'confirmed') -> bool:
        """新規選手追加（拡張機能）"""
        if player_name not in self.all_players:
            if status == 'confirmed':
                self.confirmed_players.append(player_name)
            else:
                self.potential_players.append(player_name)

            self.all_players = self.confirmed_players + self.potential_players
            self.total_players = len(self.all_players)
            return True
        return False

    def confirm_potential_player(self, player_name: str) -> bool:
        """候補選手を確認済みに変更"""
        if player_name in self.potential_players:
            self.potential_players.remove(player_name)
            self.confirmed_players.append(player_name)
            self.all_players = self.confirmed_players + self.potential_players
            return True
        return False

# グローバル拡張選手情報ハンドラー
player_info_handler = ExpandablePlayerInfoHandler()


class FlexHistoryCardHandler:
    """F履歴をカード形式で表示するハンドラー"""

    def __init__(self):
        self.card_color_scheme = {
            'primary': '#1DB446',      # LINE緑
            'secondary': '#06C755',    # LINE薄緑
            'accent': '#00B900',       # アクセント色
            'text_primary': '#333333',  # メインテキスト
            'text_secondary': '#666666', # サブテキスト
            'background': '#FAFAFA',    # 背景色
            'border': '#E0E0E0'        # ボーダー色
        }

    def create_history_flex_message(self, history_data: list, title: str = "F履歴"):
        """履歴データからFlex Messageカードを作成"""

        if not history_data:
            # 履歴がない場合のメッセージ
            empty_container = {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": title,
                            "size": "xl",
                            "weight": "bold",
                            "color": self.card_color_scheme['primary']
                        },
                        {
                            "type": "separator",
                            "margin": "md"
                        },
                        {
                            "type": "text",
                            "text": "履歴データがありません",
                            "size": "md",
                            "color": self.card_color_scheme['text_secondary'],
                            "align": "center",
                            "margin": "lg"
                        }
                    ]
                }
            }

            return FlexMessage(
                alt_text=f"{title} - 履歴なし",
                contents=empty_container
            )

        # 履歴データがある場合のカルーセル作成
        bubbles = []

        for i, record in enumerate(history_data[:10]):  # 最大10件まで表示
            bubble = self.create_single_history_card(record, i + 1)
            bubbles.append(bubble)

        # カルーセル形式でFlex Message作成
        carousel_container = {
            "type": "carousel",
            "contents": bubbles
        }

        return FlexMessage(
            alt_text=f"{title} - {len(history_data)}件の履歴",
            contents=carousel_container
        )

    def create_single_history_card(self, record: dict, index: int) -> dict:
        """単一の履歴レコードからカードを作成"""

        # レコードから情報を抽出
        timestamp = record.get('timestamp', '不明')
        user_message = record.get('user_message', '不明')
        bot_response = record.get('bot_response', '応答なし')
        conversation_id = record.get('id', 'N/A')

        # テキストを適切な長さに切り詰め
        user_message_short = self.truncate_text(user_message, 100)
        bot_response_short = self.truncate_text(bot_response, 120)

        # 日時フォーマット
        formatted_time = self.format_timestamp(timestamp)

        bubble = {
            "type": "bubble",
            "size": "kilo",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"履歴 #{index}",
                        "size": "lg",
                        "weight": "bold",
                        "color": self.card_color_scheme['primary']
                    },
                    {
                        "type": "text",
                        "text": formatted_time,
                        "size": "xs",
                        "color": self.card_color_scheme['text_secondary'],
                        "margin": "xs"
                    }
                ],
                "backgroundColor": self.card_color_scheme['background'],
                "paddingAll": "15px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "👤 ユーザー",
                                "size": "sm",
                                "weight": "bold",
                                "color": self.card_color_scheme['accent']
                            },
                            {
                                "type": "text",
                                "text": user_message_short,
                                "size": "sm",
                                "wrap": True,
                                "color": self.card_color_scheme['text_primary'],
                                "margin": "xs"
                            }
                        ],
                        "backgroundColor": "#F0F8FF",
                        "cornerRadius": "8px",
                        "paddingAll": "10px"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "🤖 Bot応答",
                                "size": "sm",
                                "weight": "bold",
                                "color": self.card_color_scheme['primary']
                            },
                            {
                                "type": "text",
                                "text": bot_response_short,
                                "size": "sm",
                                "wrap": True,
                                "color": self.card_color_scheme['text_primary'],
                                "margin": "xs"
                            }
                        ],
                        "backgroundColor": "#F0FFF0",
                        "cornerRadius": "8px",
                        "paddingAll": "10px"
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"ID: {conversation_id}",
                        "size": "xxs",
                        "color": self.card_color_scheme['text_secondary'],
                        "align": "center"
                    }
                ],
                "paddingAll": "8px"
            }
        }

        return bubble

    def truncate_text(self, text: str, max_length: int) -> str:
        """テキストを指定された長さに切り詰め"""
        if not text:
            return "なし"

        if len(text) <= max_length:
            return text

        return text[:max_length - 3] + "..."

    def format_timestamp(self, timestamp: str) -> str:
        """タイムスタンプをフォーマット"""
        try:
            from datetime import datetime

            # さまざまなタイムスタンプフォーマットに対応
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S.%f"
            ]

            for fmt in formats:
                try:
                    dt = datetime.strptime(timestamp, fmt)
                    return dt.strftime("%m/%d %H:%M")
                except ValueError:
                    continue

            # パースできない場合はそのまま返す
            return str(timestamp)[:16]

        except Exception:
            return "不明"

    def get_recent_history_from_db(self, limit: int = 10) -> list:
        """データベースから最近の履歴を取得"""
        try:
            # conversation_managerがグローバルに定義されている場合
            if 'conversation_manager' in globals():
                # SQLiteから履歴を取得
                import sqlite3
                db_path = CONVERSATION_DB_PATH

                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id, timestamp, user_message, bot_response
                    FROM conversations
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (limit,))

                rows = cursor.fetchall()
                conn.close()

                history_data = []
                for row in rows:
                    history_data.append({
                        'id': row[0],
                        'timestamp': row[1],
                        'user_message': row[2],
                        'bot_response': row[3]
                    })

                return history_data

        except Exception as e:
            print(f"[FLEX_HISTORY] Error getting history from DB: {e}")
            return []

    def handle_history_request(self, message: str):
        """履歴表示リクエストを処理"""

        # F履歴関連のキーワードをチェック
        history_keywords = ['F履歴', 'f履歴', '履歴', '会話履歴', 'history', '過去の会話']
        card_keywords = ['カード', 'card', 'flex']

        message_lower = message.lower()

        if any(keyword in message for keyword in history_keywords):
            # 履歴データを取得
            history_data = self.get_recent_history_from_db(10)

            # Flex Messageカードを作成
            flex_message = self.create_history_flex_message(history_data, "F履歴カード")

            return flex_message

        return None


# グローバルFlex履歴ハンドラー
flex_history_handler = FlexHistoryCardHandler()

import os
import re
import subprocess
import sys
import traceback
from datetime import datetime, timedelta

# 環境変数の読み込み（ルートディレクトリからの実行を前提）
from dotenv import load_dotenv

# .envファイルのパスを設定（ルートディレクトリからの相対パス）
current_dir = os.getcwd()
root_dir = current_dir

# ルートディレクトリかどうかの判定
if os.path.basename(current_dir) == "src":
    # srcディレクトリから実行された場合はルートディレクトリに移動
    root_dir = os.path.join(current_dir, "..", "..", "..")
    root_dir = os.path.abspath(root_dir)
    os.chdir(root_dir)
    print(f"[INFO] Working directory changed to root: {root_dir}")

# .envファイルのパス設定
env_file_path = os.path.join("Lesson25", "uma3soft-app", ".env")
if os.path.exists(env_file_path):
    load_dotenv(env_file_path)
    print(f"[INFO] Loaded .env from: {env_file_path}")
else:
    load_dotenv()  # 通常のロード
    print("[INFO] Loaded .env from default location")

# パスの設定（ルートディレクトリからの実行を前提）
src_path = os.path.join("Lesson25", "uma3soft-app", "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from chathistory2db import load_chathistory_to_chromadb
from flask import Flask, request
from integrated_conversation_system import IntegratedConversationSystem
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings

# LangChain verbose属性エラー回避のための設定
import os
os.environ.setdefault("LANGCHAIN_VERBOSE", "false")

# LangChainのverbose属性問題を事前に解決
try:
    import langchain
    if not hasattr(langchain, 'verbose'):
        # verbose属性が存在しない場合は追加
        langchain.verbose = False
        print("[INIT] Set langchain.verbose = False")
except ImportError:
    print("[INIT] langchain module not available for verbose setting")

from langchain_openai import ChatOpenAI
from linebot.v3.messaging import ApiClient, Configuration, MessagingApi
from linebot.v3.messaging.models import ReplyMessageRequest, TextMessage, FlexMessage
from linebot.v3.webhook import WebhookHandler
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from reminder_schedule import send_reminder_via_line
from uma3_chroma_improver import Uma3ChromaDBImprover
from uma3_agent_router import Uma3AgentRouter, AgentType
from uma3_custom_tools import create_custom_tools

# Chains import disabled - not available in current LangChain version
# Documents chain import disabled

# OpenAI API設定（環境変数から取得）
if "OPENAI_API_KEY" not in os.environ:
    print("⚠️ OPENAI_API_KEYの環境変数を設定してください")
    sys.exit(1)

# ChromaDBの保存ディレクトリ定数（実行ディレクトリからの相対パス）
# 実行ディレクトリが C:\work\ws_python\GenerationAiCamp の場合を想定
# ChromaDBの保存ディレクトリ定数（C:\work\ws_python\GenerationAiCamp>から実行）
PERSIST_DIRECTORY = "Lesson25/uma3soft-app/db/chroma_store"
CONVERSATION_DB_PATH = "Lesson25/uma3soft-app/db/conversation_history.db"

# BotのユーザーID（環境変数から取得）
BOT_USER_ID = os.getenv("BOT_USER_ID", "U2b1bb2a638b714727085c7317a3b54a0")

# グローバル変数の初期化
CHAT_HISTORY = []

app = Flask(__name__)

# LINE Bot設定（環境変数から取得）
ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
DEBUG_SKIP_SIGNATURE = os.getenv("DEBUG_SKIP_SIGNATURE", "false").lower() == "true"

if not ACCESS_TOKEN or not CHANNEL_SECRET:
    print("⚠️ LINE_ACCESS_TOKENまたはLINE_CHANNEL_SECRETの環境変数を設定してください")
    sys.exit(1)

if DEBUG_SKIP_SIGNATURE:
    print(
        "⚠️ [DEBUG MODE] 署名検証をスキップしています。本番環境では使用しないでください。"
    )

# LINE Bot SDKの初期化
configuration = Configuration(access_token=ACCESS_TOKEN)
line_api = MessagingApi(ApiClient(configuration))
handler = WebhookHandler(CHANNEL_SECRET)

# 埋め込みモデルとベクトルデータベースの初期化
try:
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    print("[INIT] Using HuggingFace embeddings")
except Exception as e:
    print(f"[WARNING] HuggingFace embeddings failed: {e}")
    print("[INIT] Using OpenAI embeddings as fallback")
    from langchain_openai import OpenAIEmbeddings
    embedding_model = OpenAIEmbeddings()

vector_db = Chroma(
    persist_directory=PERSIST_DIRECTORY, embedding_function=embedding_model
)

# ChromaDB精度向上機能の初期化
chroma_improver = Uma3ChromaDBImprover(vector_db)

# 統合会話システムの初期化
integrated_conversation_system = IntegratedConversationSystem(
    chroma_persist_directory=PERSIST_DIRECTORY,
    conversation_db_path=CONVERSATION_DB_PATH,
    embeddings_model=embedding_model
)

print(f"[INIT] Integrated conversation system initialized")
print(f"[INIT] ChromaDB path: {PERSIST_DIRECTORY}")
print(f"[INIT] ConversationDB path: {CONVERSATION_DB_PATH}")

# エージェントルーターの初期化
try:
    # LLMを初期化（エージェント分析用）
    llm_for_agent = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
    agent_router = Uma3AgentRouter(llm=llm_for_agent)

    # カスタムツールの作成
    custom_tools = create_custom_tools(chroma_improver)

    print(f"[INIT] ✅ Agent router initialized with {len(custom_tools)} custom tools")
except Exception as e:
    print(f"[INIT] ⚠️ Agent router initialization failed: {e}")
    agent_router = Uma3AgentRouter()  # LLMなしで初期化
    custom_tools = []


def format_message_for_mobile(text):
    """
    スマートフォンで見やすい形式にメッセージを整形する

    Args:
        text (str): 整形前のメッセージ

    Returns:
        str: 整形後のメッセージ
    """
    if not text:
        return text

    # 基本的な改行の正規化
    formatted_text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 長い文章を段落に分割
    sentences = []
    current_sentence = ""

    for char in formatted_text:
        current_sentence += char
        if char in ["。", "！", "？", "\n"] and len(current_sentence.strip()) > 0:
            sentences.append(current_sentence.strip())
            current_sentence = ""

    if current_sentence.strip():
        sentences.append(current_sentence.strip())

    # 段落を構築
    paragraphs = []
    current_paragraph = ""

    for sentence in sentences:
        if sentence.startswith(("1.", "2.", "3.", "4.", "5.", "•", "・", "-")):
            if current_paragraph:
                paragraphs.append(current_paragraph.strip())
                current_paragraph = ""
            paragraphs.append(sentence)
        elif len(current_paragraph) + len(sentence) > 100:
            if current_paragraph:
                paragraphs.append(current_paragraph.strip())
            current_paragraph = sentence
        else:
            if current_paragraph:
                current_paragraph += " " + sentence
            else:
                current_paragraph = sentence

    if current_paragraph:
        paragraphs.append(current_paragraph.strip())

    # 段落間に適切な改行を追加
    formatted_paragraphs = []
    for paragraph in paragraphs:
        if paragraph.startswith(("1.", "2.", "3.", "4.", "5.", "•", "・", "-")):
            formatted_paragraphs.append(paragraph)
        else:
            formatted_paragraphs.append(paragraph)

    result = "\n\n".join(formatted_paragraphs)

    # 絵文字の追加（予定関連の場合）
    if any(keyword in result for keyword in ["予定", "大会", "練習", "試合"]):
        result = "📅 " + result

    return result


def split_long_message(text, max_length=1000):
    """
    長いメッセージを複数のメッセージに分割する

    Args:
        text (str): 分割対象のメッセージ
        max_length (int): 1メッセージの最大長

    Returns:
        list: 分割されたメッセージのリスト
    """
    if len(text) <= max_length:
        return [text]

    messages = []
    current_message = ""

    paragraphs = text.split("\n\n")

    for paragraph in paragraphs:
        if len(current_message) + len(paragraph) + 2 <= max_length:
            if current_message:
                current_message += "\n\n" + paragraph
            else:
                current_message = paragraph
        else:
            if current_message:
                messages.append(current_message)

            if len(paragraph) > max_length:
                # 段落が長すぎる場合、文で分割
                sentences = paragraph.split("。")
                temp_message = ""
                for sentence in sentences:
                    if sentence and len(temp_message) + len(sentence) + 1 <= max_length:
                        if temp_message:
                            temp_message += "。" + sentence
                        else:
                            temp_message = sentence
                    else:
                        if temp_message:
                            messages.append(
                                temp_message + "。"
                                if not temp_message.endswith("。")
                                else temp_message
                            )
                        temp_message = sentence
                if temp_message:
                    current_message = (
                        temp_message + "。"
                        if not temp_message.endswith("。")
                        else temp_message
                    )
                else:
                    current_message = ""
            else:
                current_message = paragraph

    if current_message:
        messages.append(current_message)

    # メッセージが複数に分割された場合、番号を追加
    if len(messages) > 1:
        numbered_messages = []
        for i, msg in enumerate(messages, 1):
            numbered_messages.append(f"({i}/{len(messages)})\n{msg}")
        return numbered_messages

    return messages


@app.route("/")
def health_check():
    """
    アプリケーションの動作確認用エンドポイント。

    Returns:
        str: アプリケーションの状態
    """
    import datetime

    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[HEALTH] Health check accessed at {current_time}")
    print(f"[HEALTH] Request from: {request.remote_addr}")
    print(f"[HEALTH] User-Agent: {request.headers.get('User-Agent', 'Unknown')}")

    status_info = {
        "status": "running",
        "timestamp": current_time,
        "webhook_url": "/callback",
        "chromadb_path": PERSIST_DIRECTORY,
    }

    return f"LINE Bot Application is running!\nStatus: {status_info}", 200


@app.route("/callback", methods=["POST"])
def callback():
    """
    LINE MessagingAPIからのWebhookを受信するエンドポイント。

    Returns:
        str: レスポンスメッセージ "OK"
    """
    print(f"[WEBHOOK] Callback endpoint accessed! Method: {request.method}")
    print(f"[HEADERS] Request headers: {dict(request.headers)}")

    try:
        body = request.get_data(as_text=True)
        print(f"[BODY] Received body length: {len(body)}")
        print(f"[BODY] Content: {body[:200]}...")  # 最初の200文字をログ出力

        # DEBUG_SKIP_SIGNATURE環境変数が設定されている場合は署名検証をスキップ
        if DEBUG_SKIP_SIGNATURE:
            print("⚠️ [DEBUG MODE] 署名検証をスキップしています")
            # 署名検証をスキップして直接メッセージを処理
            import json

            webhook_body = json.loads(body)
            events = webhook_body.get("events", [])

            for event in events:
                if (
                    event.get("type") == "message"
                    and event.get("message", {}).get("type") == "text"
                ):
                    user_message = event["message"]["text"]
                    user_id = event["source"]["userId"]
                    print(f"[MESSAGE] User {user_id}: {user_message}")

                    # メッセージ処理を呼び出し
                    handle_message_event_direct(event)

            print(
                "[SUCCESS] Message handled successfully (signature verification skipped)"
            )
            return "OK", 200

        # 通常の署名検証処理
        signature = request.headers.get("X-Line-Signature", "")
        if not signature:
            print("[ERROR] X-Line-Signature header is missing")
            print("[DEBUG] Available headers:", list(request.headers.keys()))
            return "Bad Request: Missing signature", 400

        # デバッグ: 設定値確認
        channel_secret = os.getenv("LINE_CHANNEL_SECRET")
        print(
            f"[DEBUG] Channel Secret length: {len(channel_secret) if channel_secret else 0}"
        )
        print(f"[DEBUG] Signature received: {signature}")

        # 署名検証をより詳細にログ出力
        import base64
        import hashlib
        import hmac

        if channel_secret:
            expected_signature = base64.b64encode(
                hmac.new(
                    channel_secret.encode("utf-8"), body.encode("utf-8"), hashlib.sha256
                ).digest()
            ).decode("utf-8")
            print(f"[DEBUG] Expected signature: {expected_signature}")
            print(f"[DEBUG] Signatures match: {signature == expected_signature}")

        # LINE Webhook処理
        handler.handle(body, signature)
        print("[SUCCESS] Message handled successfully")
        return "OK", 200

    except Exception as e:
        print(f"[ERROR] Exception in callback: {type(e).__name__}: {e}")
        traceback.print_exc()
        # LINE プラットフォームには200を返して再送を防ぐ
        return "OK", 200


def handle_message_event_direct(event):
    """
    【STEP N: デバッグモード用の直接メッセージ処理関数】
    【重要】エージェントルーターと統合された処理フロー

    処理フロー:
    1. メッセージイベント検証
    2. ユーザー・グループID取得
    3. エージェントルーターによる処理

    Args:
        event (dict): LINE Webhook event dictionary
    """
    try:
        if (
            event.get("type") == "message"
            and event.get("message", {}).get("type") == "text"
        ):
            user_message = event["message"]["text"]
            user_id = event["source"]["userId"]
            group_id = event["source"].get("groupId") or event["source"].get("roomId")

            print(
                f"🔍 [DEBUG] ユーザー {user_id[:8]}... からのメッセージ: {user_message}"
            )

            # グループIDをセット（有効なIDの場合のみ）
            if group_id and len(group_id) >= 10:
                os.environ["TO_USER_ID"] = group_id
                print(f"🔍 [DEBUG] Set target group ID: {group_id[:20]}...")
            elif user_id and len(user_id) >= 10:
                os.environ["TO_USER_ID"] = user_id
                print(f"🔍 [DEBUG] Set target user ID: {user_id[:20]}...")
            else:
                print("🔍 [DEBUG] No valid target ID found")

            # Botメンションされているかチェック（デバッグモードでは簡単なチェック）
            if "@Bot" in user_message or user_message.startswith("Bot"):
                print("🔍 [DEBUG] Botがメンションされました（検出）")

                # ChromaDB検索を実行
                results = chroma_improver.schedule_aware_search(
                    user_message, k=6, score_threshold=0.5
                )

                print(f"🔍 [DEBUG] 検索結果: {len(results)}件")

                # LLMで応答生成（実際の送信はしない）
                if results:
                    context = "\n".join([doc.page_content for doc in results])
                    print(f"🔍 [DEBUG] コンテキスト長: {len(context)}文字")
                    print(f"📤 [DEBUG] 応答生成完了（実際の送信はスキップ）")
                else:
                    print("🔍 [DEBUG] コンテキストが見つかりませんでした")
            else:
                print("🔍 [DEBUG] メンションなし、処理をスキップ")

    except Exception as e:
        print(
            f"[ERROR] Exception in handle_message_event_direct: {type(e).__name__}: {e}"
        )
        traceback.print_exc()


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    """
    テキストメッセージを受信した際の処理。

    Args:
        event: LINEから送信されたメッセージイベント
    """
    print("[MESSAGE] handle_message function called!")  # 関数が呼ばれたことを確認

    try:
        # メンション情報の取得
        mention = getattr(event.message, "mention", None)
        is_mentioned_by_other = False

        if mention and hasattr(mention, "mentionees"):
            for m in mention.mentionees:
                # Bot自身がメンションされているかつ、送信者がBot自身でない
                if m.user_id == BOT_USER_ID and m.is_self:
                    if getattr(event.source, "user_id", None) != BOT_USER_ID:
                        is_mentioned_by_other = True

        user_id = getattr(event.source, "user_id", "private")
        group_id = getattr(event.source, "group_id", None) or getattr(event.source, "room_id", None)
        text = event.message.text

        # グループIDをセット（有効なIDの場合のみ）
        if group_id and group_id != "unknown" and len(group_id) >= 10:
            os.environ["TO_USER_ID"] = group_id
            print(f"[GROUP] Set target group ID: {group_id[:20]}...")
        else:
            # プライベートチャットの場合はユーザーIDを使用
            if user_id and user_id != "private" and len(user_id) >= 10:
                os.environ["TO_USER_ID"] = user_id
                print(f"[USER] Set target user ID: {user_id[:20]}...")
            else:
                print("[WARNING] No valid target ID found in message event")

        # Botがメンションされたか判定
        if is_mentioned_by_other or "@Bot" in text:
            print("[MENTION] Botがメンションされました！")

            # ===== エージェントルーター：インテリジェント分析開始 =====
            try:
                agent_type, agent_intent = agent_router.route_to_agent(text)
                agent_info = agent_router.get_agent_info(agent_type)

                print(f"[AGENT_ROUTER] 🧠 Selected Agent: {agent_info.get('name', agent_type.value)}")
                print(f"[AGENT_ROUTER] 🎯 Confidence: {agent_intent.confidence:.3f}")
                print(f"[AGENT_ROUTER] 💭 Reasoning: {agent_intent.reasoning}")

                if agent_intent.extracted_params:
                    print(f"[AGENT_ROUTER] 📋 Parameters: {agent_intent.extracted_params}")

            except Exception as router_error:
                print(f"[AGENT_ROUTER] ⚠️ Router error: {router_error}")
                agent_type = AgentType.GENERAL_CHAT
                agent_intent = None

            # ===== エージェント別処理 =====

            # 1. 最優先：Flex履歴表示エージェント
            if agent_type == AgentType.FLEX_HISTORY:
                flex_history_message = flex_history_handler.handle_history_request(text)
                if flex_history_message:
                    print(f"[FLEX_HISTORY] ✅ History card request detected, responding with Flex Message")

                # 履歴表示リクエストを会話履歴に保存
                try:
                    conversation_manager.save_conversation(
                        user_id, text, "F履歴カードを表示しました",
                        metadata={"source": "flex_history_display", "response_type": "flex_card"}
                    )
                    print(f"[FLEX_HISTORY] ✅ Saved history request to conversation log")
                except Exception as save_error:
                    print(f"[WARNING] ❌ Failed to save history request: {save_error}")

                    # Flex Messageで応答
                    line_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token, messages=[flex_history_message]
                        )
                    )
                    return

            # 2. リマインダー管理エージェント
            elif agent_type == AgentType.REMINDER_MANAGEMENT:
                try:
                    reminder_tool = next((tool for tool in custom_tools if tool.name == "reminder_manager"), None)
                    if reminder_tool:
                        action = agent_intent.extracted_params.get("action", "check")
                        if "設定" in text or "追加" in text:
                            action = "set"

                        # 日付とメッセージを抽出
                        date_match = re.search(r'(\d{1,2}月\d{1,2}日)', text)
                        date = date_match.group(1) if date_match else ""

                        # メッセージ部分を抽出
                        message_part = text.replace("@Bot", "").replace("リマインダー", "").replace(date, "").strip()

                        reminder_result = reminder_tool._run(action=action, date=date, message=message_part)

                        reply_message = TextMessage(text=f"🔔 {reminder_result}")
                        line_api.reply_message(
                            ReplyMessageRequest(
                                reply_token=event.reply_token, messages=[reply_message]
                            )
                        )
                        return
                except Exception as reminder_error:
                    print(f"[REMINDER] ⚠️ Reminder tool error: {reminder_error}")

            # 3. チーム管理エージェント
            elif agent_type == AgentType.TEAM_MANAGEMENT:
                try:
                    team_tool = next((tool for tool in custom_tools if tool.name == "team_management"), None)
                    if team_tool:
                        action = "list"  # デフォルト
                        member_name = ""

                        if "一覧" in text or "リスト" in text:
                            action = "list"
                        elif "情報" in text or "詳細" in text:
                            action = "info"
                            # メンバー名を抽出
                            for player in player_info_handler.all_players:
                                if player in text:
                                    member_name = player
                                    break
                        elif "役割" in text:
                            action = "roles"

                        team_result = team_tool._run(action=action, member_name=member_name)

                        reply_message = TextMessage(text=team_result)
                        line_api.reply_message(
                            ReplyMessageRequest(
                                reply_token=event.reply_token, messages=[reply_message]
                            )
                        )
                        return
                except Exception as team_error:
                    print(f"[TEAM] ⚠️ Team management error: {team_error}")

            # 4. イベント分析エージェント
            elif agent_type == AgentType.EVENT_ANALYSIS:
                try:
                    analysis_tool = next((tool for tool in custom_tools if tool.name == "event_analysis"), None)
                    if analysis_tool:
                        analysis_type = "results"  # デフォルト

                        if "結果" in text:
                            analysis_type = "results"
                        elif "傾向" in text:
                            analysis_type = "trends"
                        elif "成績" in text or "パフォーマンス" in text:
                            analysis_type = "performance"

                        period = agent_intent.extracted_params.get("time_context", "最近")

                        analysis_result = analysis_tool._run(analysis_type=analysis_type, period=period)

                        reply_message = TextMessage(text=analysis_result)
                        line_api.reply_message(
                            ReplyMessageRequest(
                                reply_token=event.reply_token, messages=[reply_message]
                            )
                        )
                        return
                except Exception as analysis_error:
                    print(f"[ANALYSIS] ⚠️ Event analysis error: {analysis_error}")

            # 5. 天気コンテキストエージェント
            elif agent_type == AgentType.WEATHER_CONTEXT:
                try:
                    weather_tool = next((tool for tool in custom_tools if tool.name == "weather_context"), None)
                    if weather_tool:
                        weather_result = weather_tool._run(query=text)

                        reply_message = TextMessage(text=weather_result)
                        line_api.reply_message(
                            ReplyMessageRequest(
                                reply_token=event.reply_token, messages=[reply_message]
                            )
                        )
                        return
                except Exception as weather_error:
                    print(f"[WEATHER] ⚠️ Weather context error: {weather_error}")

            # 6. スケジュール通知エージェント（強化版）
            elif agent_type == AgentType.SCHEDULE_NOTIFICATION:
                try:
                    print(f"[SCHEDULE] Processing schedule request: {text}")

                    # 今週の予定かどうかを判断
                    weekly_keywords = ["今週", "週間", "この週", "今週の予定"]
                    is_weekly_request = any(keyword in text for keyword in weekly_keywords)

                    # 今後の予定かどうかを判断
                    future_keywords = ["今後", "これから", "以降", "未来"]
                    is_future_request = any(keyword in text for keyword in future_keywords)

                    if is_weekly_request:
                        # 今週の予定を取得
                        try:
                            from uma3_custom_tools import get_weekly_schedule
                            current_date = datetime.now().strftime("%Y-%m-%d")
                            response_text = get_weekly_schedule(text, current_date)
                            print(f"[SCHEDULE] 📅 Weekly schedule response generated")
                        except Exception as weekly_error:
                            print(f"[SCHEDULE] ⚠️ Weekly schedule error: {weekly_error}")
                            response_text = "今週の予定取得中にエラーが発生しました。"

                    elif is_future_request:
                        # 今後の予定を取得
                        try:
                            from uma3_custom_tools import get_future_events_from_date
                            current_date = datetime.now().strftime("%Y-%m-%d")
                            response_text = get_future_events_from_date(text, current_date)
                            print(f"[SCHEDULE] 🔮 Future events response generated")
                        except Exception as future_error:
                            print(f"[SCHEDULE] ⚠️ Future events error: {future_error}")
                            response_text = "今後の予定取得中にエラーが発生しました。"
                    else:
                        # 従来のスケジュール検索
                        time_context = agent_intent.extracted_params.get("time_context", "")
                        search_query = f"予定 スケジュール {time_context}"

                        schedule_results = chroma_improver.schedule_aware_search(search_query, k=5)

                        if schedule_results:
                            # スケジュール情報をフォーマット
                            schedule_text = ""
                            for i, doc in enumerate(schedule_results[:3], 1):
                                schedule_text += f"{i}. {doc.page_content[:150]}...\n\n"

                            # フォーマット関数を使用
                            try:
                                from uma3_custom_tools import format_schedule_response, calculate_days_until_event
                                formatted_schedule = format_schedule_response(schedule_text)

                                # 日数計算も追加
                                days_info = calculate_days_until_event(schedule_text)
                                response_text = f"{formatted_schedule}\n\n{days_info}"
                            except Exception as format_error:
                                print(f"[SCHEDULE] ⚠️ Format error: {format_error}")
                                response_text = f"📅 スケジュール情報:\n\n{schedule_text}"
                        else:
                            response_text = "📅 該当するスケジュール情報が見つかりませんでした。"

                    reply_message = TextMessage(text=response_text)
                    line_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token, messages=[reply_message]
                        )
                    )
                    return

                except Exception as schedule_error:
                    print(f"[SCHEDULE] ⚠️ Schedule agent error: {schedule_error}")

            # 7. 履歴検索エージェント（通常のテキスト形式）
            elif agent_type == AgentType.HISTORY_SEARCH:
                try:
                    print(f"[HISTORY_SEARCH] Processing history search: {text}")

                    # 履歴検索を実行
                    extracted_term = agent_intent.extracted_params.get("extracted_term", "")
                    search_query = f"履歴 過去 {extracted_term}" if extracted_term else text

                    history_results = chroma_improver.smart_similarity_search(search_query, k=5)

                    if history_results:
                        response_text = "📋 検索された履歴情報:\n\n"
                        for i, doc in enumerate(history_results[:3], 1):
                            response_text += f"{i}. {doc.page_content[:200]}...\n\n"

                        reply_message = TextMessage(text=response_text)
                        line_api.reply_message(
                            ReplyMessageRequest(
                                reply_token=event.reply_token, messages=[reply_message]
                            )
                        )
                        return
                    else:
                        reply_message = TextMessage(text="📋 該当する履歴情報が見つかりませんでした。")
                        line_api.reply_message(
                            ReplyMessageRequest(
                                reply_token=event.reply_token, messages=[reply_message]
                            )
                        )
                        return

                except Exception as history_error:
                    print(f"[HISTORY_SEARCH] ⚠️ History search error: {history_error}")

            # 8. 学習済み選手情報のチェック（FAQ検索エージェント内）
            player_response = player_info_handler.handle_message(text)
            if player_response:
                print(f"[PLAYER_INFO] ✅ Player information found, responding with player data")

                # 選手情報を会話履歴に保存
                try:
                    conversation_manager.save_conversation(
                        user_id, text, player_response,
                        metadata={"source": "learned_player_info", "response_type": "player_data"}
                    )
                    print(f"[PLAYER_INFO] ✅ Saved player conversation to history")
                except Exception as save_error:
                    print(f"[WARNING] ❌ Failed to save player conversation: {save_error}")

                # 選手情報で即座に応答
                reply_message = TextMessage(text=player_response)
                line_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token, messages=[reply_message]
                    )
                )
                return

            # 3. 統合会話システムを使用して応答を生成
            print(f"[INTEGRATED] Using integrated conversation system for user: {user_id}")

            # LLMの初期化（verbose属性エラー回避）
            try:
                # 環境変数での設定を試行
                import langchain
                if hasattr(langchain, 'verbose'):
                    langchain.verbose = False

                llm = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0.3,
                    openai_api_key=os.getenv("OPENAI_API_KEY")
                )
                print("[LLM] ChatOpenAI initialized successfully")

            except AttributeError as verbose_error:
                print(f"[WARNING] LangChain verbose attribute error: {verbose_error}")
                # verbose属性なしでの初期化
                llm = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    temperature=0.3,
                    openai_api_key=os.getenv("OPENAI_API_KEY")
                )
                print("[LLM] ChatOpenAI initialized without verbose setting")

            except Exception as llm_error:
                print(f"[ERROR] LLM initialization failed: {llm_error}")
                # 最後のフォールバック
                ai_msg = {"answer": "申し訳ございません。現在システムの初期化に問題が発生しています。"}
                reply_message = TextMessage(text=ai_msg["answer"])
                line_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token, messages=[reply_message]
                    )
                )
                return

            try:
                # 統合システムで応答生成（改善版）
                print(f"[ENHANCED] Trying improved response system first...")

                # 1. 改善されたテンプレートシステムを試行
                enhanced_response = None
                try:
                    # ImprovedResponseGeneratorを初期化（必要時のみ）
                    if not hasattr(handle_message, 'improved_generator'):
                        from tests.improved_response_system import ImprovedResponseGenerator
                        db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'conversation_history.db')
                        handle_message.improved_generator = ImprovedResponseGenerator(db_path)
                        print("[ENHANCED] Improved response generator initialized")

                    # 改善された応答生成
                    improved_result = handle_message.improved_generator.generate_improved_response(user_id, text)

                    # 高品質な応答が生成された場合は使用
                    if improved_result.get('quality_score', 0) >= 3.0:
                        enhanced_response = improved_result['response']
                        print(f"[ENHANCED] ✅ High quality response (score: {improved_result['quality_score']:.1f})")

                        # 統合システムの会話履歴に保存
                        try:
                            integrated_conversation_system.history_manager.save_conversation(
                                user_id, text, enhanced_response,
                                metadata={
                                    "source": "enhanced_template",
                                    "quality_score": improved_result['quality_score'],
                                    "template_type": improved_result.get('template_type', 'unknown')
                                }
                            )
                            print(f"[ENHANCED] ✅ Saved enhanced conversation to history")
                        except Exception as save_error:
                            print(f"[WARNING] ❌ Failed to save enhanced conversation: {save_error}")

                    else:
                        print(f"[ENHANCED] ⚠️ Low quality response, trying integrated system (score: {improved_result['quality_score']:.1f})")

                except Exception as e:
                    print(f"[WARNING] Enhanced response generation failed: {e}")

                # 2. 改善システムで高品質な応答が得られた場合はそれを使用
                if enhanced_response:
                    ai_msg = {"answer": enhanced_response}
                    print(f"[ENHANCED] Using enhanced template response")

                else:
                    # 3. 既存の統合システムにフォールバック
                    response_result = integrated_conversation_system.generate_integrated_response(
                        user_id, text, llm
                    )

                if not enhanced_response and "error" in response_result:
                    # エラーが発生した場合のフォールバック処理
                    print(f"[ERROR] Integrated system error: {response_result.get('error_message', 'Unknown error')}")

                    # 従来のChromaDB検索にフォールバック
                    results = chroma_improver.schedule_aware_search(
                        text, k=6, score_threshold=0.5
                    )

                    if results:
                        context = "\n".join([doc.page_content for doc in results])

                        prompt_template = ChatPromptTemplate.from_messages([
                            (
                                "system",
                                """あなたは優秀なアシスタントです。以下の関連情報を参考にして、
                                ユーザーの質問に自然で親しみやすく答えてください。
                                回答時はスマートフォンで読みやすいように、適度に改行を入れてください。

                                ---
                                {context}
                                ---""",
                            ),
                            ("human", "{input}"),
                        ])

                        formatted_prompt = prompt_template.format_messages(
                            context=context, input=text
                        )
                        response = llm.invoke(formatted_prompt)
                        ai_msg = {"answer": response.content}
                    else:
                        ai_msg = {"answer": "申し訳ございません。関連する情報が見つかりませんでした。"}
                elif not enhanced_response:
                    # 正常応答の場合（改善システムでない場合のみ）
                    ai_msg = {"answer": response_result["response"]}

                    # 応答情報をログ出力
                    context_info = response_result.get("context_used", {})
                    print(f"[INTEGRATED] Response generated successfully")
                    print(f"[INTEGRATED] ChromaDB results: {context_info.get('chroma_results', 0)}")
                    print(f"[INTEGRATED] Conversation history: {context_info.get('conversation_history', 0)}")
                    print(f"[INTEGRATED] Response type: {response_result.get('response_type', 'unknown')}")

                    # ユーザプロフィール情報をログ出力
                    user_profile = context_info.get('user_profile', {})
                    if user_profile:
                        print(f"[PROFILE] User conversation count: {user_profile.get('conversation_count', 0)}")
                        if user_profile.get('interests'):
                            print(f"[PROFILE] User interests: {user_profile['interests'][:3]}")

                    # ★★★ 統合システムで生成した会話を履歴に保存（改善システムでない場合のみ）★★★
                    try:
                        integrated_conversation_system.history_manager.save_conversation(
                            user_id, text, ai_msg["answer"],
                            metadata={"source": "line_mention", "response_type": response_result.get('response_type', 'integrated')}
                        )
                        print(f"[HISTORY] ✅ Saved conversation to history (user: {user_id[:10]}...)")
                    except Exception as save_error:
                        print(f"[WARNING] ❌ Failed to save conversation to history: {save_error}")
                        traceback.print_exc()

            except Exception as e:
                print(f"[ERROR] Integrated conversation system error: {e}")
                traceback.print_exc()

                # エラー時のフォールバック：従来の処理
                results = chroma_improver.schedule_aware_search(
                    text, k=6, score_threshold=0.5
                )

                if results:
                    context = "\n".join([doc.page_content for doc in results])

                    prompt_template = ChatPromptTemplate.from_messages([
                        (
                            "system",
                            """あなたは優秀なアシスタントです。以下の関連情報を参考にして、
                            ユーザーの質問に自然で親しみやすく答えてください。

                            ---
                            {context}
                            ---""",
                        ),
                        ("human", "{input}"),
                    ])

                    formatted_prompt = prompt_template.format_messages(
                        context=context, input=text
                    )
                    response = llm.invoke(formatted_prompt)
                    ai_msg = {"answer": response.content}
                else:
                    ai_msg = {"answer": "申し訳ございません。現在応答の生成に問題が発生しています。"}

                # ★★★ エラー時も会話履歴に保存（改善システムでない場合のみ）★★★
                if not enhanced_response:
                    try:
                        integrated_conversation_system.history_manager.save_conversation(
                            user_id, text, ai_msg["answer"],
                            metadata={"source": "line_mention_fallback", "error_occurred": True}
                        )
                        print(f"[HISTORY] ✅ Saved fallback conversation to history")
                    except Exception as save_error:
                        print(f"[WARNING] ❌ Failed to save fallback conversation: {save_error}")

            # 会話履歴に追加
            CHAT_HISTORY.extend(
                [HumanMessage(content=text), HumanMessage(content=ai_msg["answer"])]
            )

            # LINEに応答メッセージを送信（スマートフォン対応）
            answer_text = ai_msg["answer"]

            # スマートフォン用にメッセージを整形
            formatted_text = format_message_for_mobile(answer_text)

            # 長いメッセージの場合は分割
            message_parts = split_long_message(formatted_text, max_length=1000)

            # メッセージを送信
            if len(message_parts) == 1:
                # 単一メッセージの場合
                reply_message = TextMessage(text=message_parts[0])
                line_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token, messages=[reply_message]
                    )
                )
                print(f"[REPLY] Sent single message: {message_parts[0][:100]}...")
            else:
                # 複数メッセージに分割された場合
                reply_messages = [
                    TextMessage(text=part) for part in message_parts[:5]
                ]  # 最大5メッセージまで
                line_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token, messages=reply_messages
                    )
                )
                print(f"[REPLY] Sent {len(reply_messages)} split messages")

        # 通常のメッセージ処理（メンションなし）
        else:
            message_info = f"Received message from {user_id} in {group_id}"
            print(f"[USER] {message_info}: {text}")

            # より詳細なメタデータで保存
            import time

            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            metadata = {
                "user": user_id,
                "timestamp": group_id,
                "saved_at": current_time,
                "message_type": "user_message",
            }

            vector_db.add_texts([text], metadatas=[metadata])
            print(
                f"[SAVE] Saved to ChromaDB: {text[:50]}..."
                if len(text) > 50
                else f"[SAVE] Saved to ChromaDB: {text}"
            )

            # 会話履歴システムにも保存（応答なしの場合）
            try:
                integrated_conversation_system.history_manager.save_conversation(
                    user_id, text, "",  # 応答なしなので空文字
                    metadata={"source": "line_message_only", "no_response": True}
                )
                print(f"[HISTORY] Saved user message to conversation history")
            except Exception as e:
                print(f"[WARNING] Failed to save to conversation history: {e}")

            # 定期的なパフォーマンス統計を表示
            if hasattr(chroma_improver, "_message_count"):
                chroma_improver._message_count += 1
            else:
                chroma_improver._message_count = 1

            if chroma_improver._message_count % 10 == 0:
                print(
                    f"[STATS] Processed {chroma_improver._message_count} messages. DB size check recommended."
                )

    except ValueError as e:
        print(f"[ERROR] ValueError in handle_message: {e}")
        traceback.print_exc()
    except KeyError as e:
        print(f"[ERROR] KeyError in handle_message: {e}")
        traceback.print_exc()
    except OSError as e:
        print(f"[ERROR] OSError in handle_message: {e}")
        traceback.print_exc()


def get_next_note_for_reminder():
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_date = tomorrow.date()
    notes = chroma_improver.smart_similarity_search("[ノート]", k=20)
    for note in notes:
        import re

        date_patterns = re.findall(
            r"(\d{4}/\d{2}/\d{2}|(\d{1,2})月(\d{1,2})日)", note.page_content
        )
        for dp in date_patterns:
            # 西暦形式
            if isinstance(dp, str) and "/" in dp:
                try:
                    nd = datetime.strptime(dp, "%Y/%m/%d").date()
                    if nd >= tomorrow_date:
                        return note.page_content
                except Exception:
                    continue
            # 月日形式
            elif isinstance(dp, tuple) and dp[1] and dp[2]:
                try:
                    year = tomorrow.year
                    nd = datetime(year, int(dp[1]), int(dp[2])).date()
                    if nd >= tomorrow_date:
                        return note.page_content
                except Exception:
                    continue
    if notes:
        return notes[0].page_content
    return "直近の[ノート]は見つかりませんでした。"


if __name__ == "__main__":
    print("Starting Flask application...")
    print(f"Access token: {ACCESS_TOKEN[:20]}...")
    print(f"Channel secret: {CHANNEL_SECRET[:10]}...")
    print("Webhook endpoint: http://localhost:5000/callback")
    print("Health check endpoint: http://localhost:5000/")
    print("Flask app is now ready to receive requests!")

    # 開発環境での安定性向上のためリローダーを無効化
    debug_mode = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    use_reloader = os.getenv("FLASK_USE_RELOADER", "False").lower() == "true"

    # チャット履歴をChromaDBにロード
    debug_info = f"""
    [UMA3 DEBUG] Before load_chathistory_to_chromadb:
    CWD: {os.getcwd()}
    __file__: {__file__}
    sys.path[0]: {sys.path[0] if sys.path else 'None'}
    """
    print(debug_info)

    # デバッグ情報をファイルにも保存
    with open("debug_uma3_f5.log", "w", encoding="utf-8") as f:
        f.write(debug_info + "\n")

    load_chathistory_to_chromadb()

    after_debug = f"[UMA3 DEBUG] After load_chathistory_to_chromadb: CWD={os.getcwd()}"
    print(after_debug)

    # 完了をファイルに記録
    with open("debug_uma3_f5.log", "a", encoding="utf-8") as f:
        f.write(after_debug + "\n")
        f.write("load_chathistory_to_chromadb() completed successfully\n")

    # monitoring_historyfile.py をサブプロセスでバックグラウンド起動
    import subprocess

    monitoring_script = os.path.join("Lesson25", "uma3soft-app", "src", "monitoring_historyfile.py")
    if os.path.exists(monitoring_script):
        subprocess.Popen([sys.executable, monitoring_script])
        print(f"[INFO] Started monitoring script: {monitoring_script}")
    else:
        print(f"[WARNING] Monitoring script not found: {monitoring_script}")

    # Flaskアプリ起動
    app.run(host="0.0.0.0", port=5000, debug=debug_mode, use_reloader=use_reloader)
