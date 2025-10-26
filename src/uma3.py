"""
FlaskとLINE Bot SDKを使用したLINE Botアプリケーション。

このモジュールは、メッセージを受信してコンソールに出力する
シンプルなLINE Botを提供します。
"""

import os
import re
import subprocess
import sys
import traceback
from datetime import datetime, timedelta

# 環境変数の読み込み（実行ディレクトリに応じた.envファイルパス）
from dotenv import load_dotenv

# .envファイルのパスを動的に設定
current_dir = os.getcwd()
env_file_path = os.path.join("Lesson25", "uma3soft-app", ".env")
if os.path.exists(env_file_path):
    load_dotenv(env_file_path)
else:
    load_dotenv()  # 通常のロード

from chathistory2db import load_chathistory_to_chromadb
from flask import Flask, request
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from linebot.v3.messaging import ApiClient, Configuration, MessagingApi
from linebot.v3.messaging.models import ReplyMessageRequest, TextMessage
from linebot.v3.webhook import WebhookHandler
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from reminder_schedule import send_reminder_via_line
from uma3_chroma_improver import Uma3ChromaDBImprover

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

# BotのユーザーID（環境変数から取得）
BOT_USER_ID = os.getenv("BOT_USER_ID", "U2b1bb2a638b714727085c7317a3b54a0")

# グローバル変数の初期化
CHAT_HISTORY = []

app = Flask(__name__)

# LINE Bot設定（環境変数から取得）
ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

if not ACCESS_TOKEN or not CHANNEL_SECRET:
    print("⚠️ LINE_ACCESS_TOKENまたはLINE_CHANNEL_SECRETの環境変数を設定してください")
    sys.exit(1)

# LINE Bot SDKの初期化
configuration = Configuration(access_token=ACCESS_TOKEN)
line_api = MessagingApi(ApiClient(configuration))
handler = WebhookHandler(CHANNEL_SECRET)

# 埋め込みモデルとベクトルデータベースの初期化
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
vector_db = Chroma(
    persist_directory=PERSIST_DIRECTORY, embedding_function=embedding_model
)

# ChromaDB精度向上機能の初期化
chroma_improver = Uma3ChromaDBImprover(vector_db)


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
        # 署名を安全に取得
        signature = request.headers.get("X-Line-Signature", "")
        if not signature:
            print("[ERROR] X-Line-Signature header is missing")
            print("[DEBUG] Available headers:", list(request.headers.keys()))
            return "Bad Request: Missing signature", 400

        body = request.get_data(as_text=True)
        print(f"[BODY] Received body length: {len(body)}")
        print(f"[BODY] Content: {body[:200]}...")  # 最初の200文字をログ出力

        # LINE Webhook処理
        handler.handle(body, signature)
        print("[SUCCESS] Message handled successfully")
        return "OK", 200

    except Exception as e:
        print(f"[ERROR] Exception in callback: {type(e).__name__}: {e}")
        traceback.print_exc()
        # LINE プラットフォームには200を返して再送を防ぐ
        return "OK", 200


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
        group_id = getattr(event.source, "group_id", "unknown")
        text = event.message.text

        # グループIDをセット
        os.environ["TO_USER_ID"] = group_id

        # Botがメンションされたか判定
        if is_mentioned_by_other or "@Bot" in text:
            print("[MENTION] Botがメンションされました！")

            # ChromaDB精度向上検索で関連する過去の会話を検索
            print(f"[SEARCH] Using improved search for user: {user_id}")

            # 予定関連クエリの場合は専用検索を実行
            results = chroma_improver.schedule_aware_search(
                text, k=6, score_threshold=0.5
            )

            print(f"[SEARCH] Schedule-aware search returned {len(results)} results")

            # [ノート]データの割合をログ出力
            if results:
                note_count = sum(1 for doc in results if "[ノート]" in doc.page_content)
                note_ratio = note_count / len(results) * 100
                print(
                    f"[SEARCH] Note data ratio: {note_count}/{len(results)} ({note_ratio:.1f}%)"
                )

            # 結果が少ない場合はコンテキスト検索で補完
            if len(results) < 3:
                print(f"[SEARCH] Using contextual search for better results")
                context_results = chroma_improver.get_contextual_search(
                    text, user_id, k=3
                )
                # 重複を避けて追加
                existing_content = {doc.page_content for doc in results}
                for doc in context_results:
                    if doc.page_content not in existing_content:
                        results.append(doc)
                        if len(results) >= 6:
                            break

            # コンテキスト構築
            context = ""
            if results:
                context_parts = []
                for doc in results:
                    context_parts.append(doc.page_content)
                context = "\n".join(context_parts)
                print(f"[CONTEXT] Found {len(results)} relevant messages")
            else:
                print("[CONTEXT] No relevant context found")

            # 検索分析情報をログ出力
            analytics = chroma_improver.get_search_analytics(text)
            print(f"[ANALYTICS] Total results: {analytics['total_results']}")
            print(
                f"[ANALYTICS] Score range: {analytics['score_range']['min']:.4f}-{analytics['score_range']['max']:.4f}"
            )
            print(
                f"[ANALYTICS] Top users: {list(analytics['user_distribution'].keys())[:3]}"
            )
            print(f"[ANALYTICS] Time distribution: {analytics['time_distribution']}")

            # コンテキスト品質の評価
            if results:
                user_match_count = sum(
                    1 for doc in results if doc.metadata.get("user") == user_id
                )
                context_quality = (user_match_count / len(results)) * 100
                print(
                    f"[QUALITY] User context match: {user_match_count}/{len(results)} ({context_quality:.1f}%)"
                )

                # 正解データ確認（スケジュール関連の場合）
                if any(
                    keyword in text.lower()
                    for keyword in ["予定", "スケジュール", "大会", "練習"]
                ):
                    target_keywords = ["東京都大会", "羽村ライオンズ", "大森リーグ"]
                    found_targets = []
                    for doc in results:
                        for target in target_keywords:
                            if target in doc.page_content:
                                found_targets.append(target)
                                break
                    if found_targets:
                        print(f"[TARGET] Found target data: {found_targets}")
            else:
                print(f"[QUALITY] No context found for query")

            # OpenAI ChatGPTを使用して回答生成
            llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.3,
                openai_api_key=os.getenv("OPENAI_API_KEY"),
            )

            # プロンプトテンプレート作成
            if context:
                # コンテキストの品質に応じてプロンプトを調整
                user_match_count = sum(
                    1 for doc in results if doc.metadata.get("user") == user_id
                )
                if user_match_count > 0:
                    # ユーザー固有のコンテキストがある場合
                    prompt_template = ChatPromptTemplate.from_messages(
                        [
                            (
                                "system",
                                """あなたは優秀なアシスタントです。以下の過去の会話履歴（特にユーザーの過去の発言）を参考にして、ユーザーの質問に自然で親しみやすく答えてください。
                                    回答時は以下の点を心がけてください：
                                    - スマートフォンで読みやすいように、適度に改行を入れる
                                    - 重要な情報は箇条書きで整理する
                                    - 予定や日程がある場合は、日付・時間・場所を明確に記載する
                                    - 長い回答の場合は、要点をまとめて最初に記載する

                                    ---
                                    {context}
                                    ---""",
                            ),
                            ("human", "{input}"),
                        ]
                    )
                else:
                    # 一般的なコンテキストのみの場合
                    prompt_template = ChatPromptTemplate.from_messages(
                        [
                            (
                                "system",
                                """あなたは優秀なアシスタントです。以下の関連する会話履歴を参考にして、ユーザーの質問に答えてください。
                                    回答時は以下の点を心がけてください：
                                    - スマートフォンで読みやすいように、適度に改行を入れる
                                    - 重要な情報は箇条書きで整理する
                                    - 予定や日程がある場合は、日付・時間・場所を明確に記載する

                                    ---
                                    {context}
                                    ---""",
                            ),
                            ("human", "{input}"),
                        ]
                    )
                prompt = prompt_template.format(context=context, input=text)
            else:
                prompt_template = ChatPromptTemplate.from_messages(
                    [
                        (
                            "system",
                            """あなたは優秀なアシスタントです。
                                回答時は以下の点を心がけてください：
                                - スマートフォンで読みやすいように、適度に改行を入れる
                                - 重要な情報は箇条書きで整理する
                                - 丁寧で親しみやすい口調で回答する""",
                        ),
                        ("human", "{input}"),
                    ]
                )
                prompt = prompt_template.format(input=text)

            # OpenAIで応答生成
            response = llm.invoke(prompt)
            ai_msg = {"answer": response.content}

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

        # 通常のメッセージ処理
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
    import os
    import subprocess
    import sys

    monitoring_script = os.path.join(
        os.path.dirname(__file__), "monitoring_historyfile.py"
    )
    subprocess.Popen([sys.executable, monitoring_script])

    # Flaskアプリ起動
    app.run(host="0.0.0.0", port=5000, debug=debug_mode, use_reloader=use_reloader)
