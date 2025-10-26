"""
チャット履歴をChromaDBにロードする単体モジュール。

・このファイル単体で実行可能（コマンドライン引数対応）
・importしても副作用なし
・Flaskや他アプリ依存なし
・DB登録後はチャット履歴ファイルをdoneディレクトリに移動
"""

import argparse
import os
import re
import shutil
from datetime import datetime

try:
    from langchain_chroma import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    Chroma = None
    HuggingFaceEmbeddings = None


# チャット履歴ファイルのパス定数（デフォルト値）
DEFAULT_CHATHISTORY_PATH = r"C:\Users\o_you\iCloudDrive\3L68KQB4HG~com~readdle~CommonDocuments\chat_history\[LINE] ☆馬三ソフト☆のトーク.txt"
DEFAULT_CHATHISTORY_PATH_BK = r"C:\Users\o_you\iCloudDrive\3L68KQB4HG~com~readdle~CommonDocuments\chat_history\done\[LINE] ☆馬三ソフト☆のトーク.txt"

# --- chroma_storeの保存先を必ずdbディレクトリ直下にする ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_DIR = os.path.join(PROJECT_ROOT, "db")
os.makedirs(DB_DIR, exist_ok=True)
PERSIST_DIRECTORY = os.path.join(DB_DIR, "chroma_store")


def load_chathistory_to_chromadb(
    chathistory_path=DEFAULT_CHATHISTORY_PATH,  # 読み込み対象のチャット履歴ファイルパス
    persist_directory=PERSIST_DIRECTORY,  # ChromaDB保存先ディレクトリ
    embedding_model_name="sentence-transformers/all-MiniLM-L6-v2",  # 埋め込みモデル名
    verbose=True,  # 詳細ログ出力フラグ
):
    """
    チャット履歴をChromaDBにロードする関数。
    既存ChromaDBがある場合は差分のみ登録します。
    登録完了後は、元のチャット履歴ファイルをdoneディレクトリに移動します。
    """
    # ステップ1: デバッグ情報出力（現在の作業ディレクトリとパス確認）
    if verbose:
        print(f"[DEBUG] Current working directory: {os.getcwd()}")
        print(f"[DEBUG] PERSIST_DIRECTORY: {persist_directory}")
        print(f"[DEBUG] Absolute path check: {os.path.isabs(persist_directory)}")

    # ステップ2: 入力ファイルの存在確認
    if not os.path.exists(chathistory_path):
        print(f"[warning] Chat history file not found: {chathistory_path}")
        return False  # ファイルが存在しない場合は処理終了

    # ステップ3: 必要なライブラリのインポート確認
    if Chroma is None or HuggingFaceEmbeddings is None:
        print(
            "[ERROR] langchain_chroma, langchain_huggingfaceがインポートできません。必要なパッケージをインストールしてください。"
        )
        return False  # ライブラリが不足している場合は処理終了

    # ステップ4: 埋め込みモデルとベクトルデータベースの初期化
    embedding_model = HuggingFaceEmbeddings(
        model_name=embedding_model_name
    )  # HuggingFace埋め込みモデル作成
    vector_db = Chroma(
        persist_directory=persist_directory,  # ChromaDB保存先指定
        embedding_function=embedding_model,  # 埋め込み関数設定
    )

    try:
        # ステップ5: 変数初期化
        date = ""  # 現在処理中の日付
        current_message = ""  # 現在構築中のメッセージ
        current_metadata = {}  # 現在のメタデータ（ユーザー、タイムスタンプ）
        messages_to_save = []  # 保存対象メッセージのリスト

        # ステップ6: 既存データの重複チェック用セット作成（差分登録のため）
        existing_texts = set()  # 既存メッセージのハッシュセット（重複防止用）

        # ChromaDBディレクトリの存在確認と既存データ読み込み
        chromadb_exists = os.path.exists(persist_directory) and os.listdir(
            persist_directory
        )

        if chromadb_exists:  # ChromaDBが存在し、空でない場合
            print(
                "[INFO] Existing ChromaDB detected. Loading for differential registration..."
            )
            try:
                # ChromaDBから既存の全ドキュメントを取得
                docs = vector_db.get()  # 全ドキュメント取得

                if docs and docs.get("documents") and len(docs["documents"]) > 0:
                    print(
                        f"[INFO] Loading {len(docs['documents'])} existing documents for duplicate check..."
                    )

                    # 各既存ドキュメントから重複チェック用キーを生成
                    for i in range(len(docs["documents"])):
                        msg = docs["documents"][i]  # メッセージ本文
                        meta = (
                            docs.get("metadatas", [{}])[i]
                            if i < len(docs.get("metadatas", []))
                            else {}
                        )
                        timestamp = meta.get("timestamp", "")

                        # 重複チェック用の複合キー（メッセージ内容 + タイムスタンプ）
                        key = f"{msg}|{timestamp}"
                        existing_texts.add(key)

                        # 進捗表示（大量データ対応）
                        if (i + 1) % 1000 == 0:
                            print(
                                f"[INFO] Processed {i + 1}/{len(docs['documents'])} existing messages..."
                            )

                    print(
                        f"[INFO] Successfully loaded {len(existing_texts)} existing messages for duplicate check"
                    )
                else:
                    print("[INFO] ChromaDB exists but contains no documents")

            except Exception as e:
                print(f"[WARNING] Could not load existing ChromaDB data: {e}")
                print("[INFO] Proceeding with full import...")
                existing_texts = set()  # エラー時は全件登録に fallback
        else:
            print("[INFO] No existing ChromaDB found. Performing full import...")

        # ステップ7: チャット履歴ファイルの読み込み
        with open(chathistory_path, encoding="utf-8") as f:  # UTF-8でファイルを開く
            lines = f.readlines()  # 全行を一度に読み込み

            # ステップ8: 各行を順次処理してメッセージを抽出
            for i, line in enumerate(lines):  # 行番号付きでループ
                cleaned_line = clean_invisible_characters(line)  # 制御文字除去
                parts = cleaned_line.strip().split("\t")  # タブ区切りで分割

                if not cleaned_line.strip():  # 空行の場合
                    continue  # スキップして次の行へ

                # ケース1: 1つの要素（日付行または継続メッセージ）
                if len(parts) == 1:
                    if is_date_format(
                        parts[0]
                    ):  # 日付形式かチェック（例：R5/10/22(日)）
                        # 前のメッセージが残っている場合は保存
                        if current_message.strip():
                            messages_to_save.append(
                                (
                                    current_message.strip(),
                                    current_metadata.copy(),
                                )  # メッセージとメタデータを保存リストに追加
                            )
                            current_message = ""  # メッセージをクリア
                        date = parts[0]  # 新しい日付を設定
                    else:
                        # 継続メッセージ（複数行にわたるメッセージの続き）
                        if current_message:
                            current_message += " " + parts[0]  # 既存メッセージに追加
                        else:
                            current_message = parts[0]  # 新しいメッセージとして設定

                # ケース2: 2つ以上の要素（タイムスタンプ、ユーザー、メッセージ）
                elif len(parts) >= 2:
                    # 前のメッセージが残っている場合は保存
                    if current_message.strip():
                        messages_to_save.append(
                            (
                                current_message.strip(),
                                current_metadata.copy(),
                            )  # 前のメッセージを保存
                        )

                    # 新しいメッセージの構成要素を抽出
                    timestamp = clean_invisible_characters(
                        parts[0]
                    )  # タイムスタンプ（例：14:30）
                    user = (
                        clean_invisible_characters(parts[1])
                        if len(parts) > 1
                        else ""  # ユーザー名
                    )
                    message_text = (
                        clean_invisible_characters(parts[2])
                        if len(parts) > 2
                        else ""  # メッセージ本文
                    )

                    # 新しいメッセージとメタデータを設定
                    current_message = message_text
                    current_metadata = {
                        "user": user,  # ユーザー名
                        "timestamp": date
                        + " "
                        + timestamp,  # 日付+時刻の完全なタイムスタンプ
                    }

                # ケース3: 予期しない形式
                else:
                    print(
                        f"[WARNING] Unexpected format in line {i+1}: {cleaned_line.strip()}"  # 警告出力
                    )

            # ステップ9: 最後のメッセージが残っている場合は保存
            if current_message.strip():
                messages_to_save.append(
                    (
                        current_message.strip(),
                        current_metadata.copy(),
                    )  # 最後のメッセージを保存
                )

        # ステップ10: 差分データのみをChromaDBに保存（重複除外処理）
        print(
            f"[INFO] Starting differential registration. Checking {len(messages_to_save)} messages against {len(existing_texts)} existing entries..."
        )

        new_count = 0  # 新規追加カウンター
        skip_count = 0  # スキップカウンター
        error_count = 0  # エラーカウンター

        for idx, (message, metadata) in enumerate(
            messages_to_save
        ):  # 保存対象メッセージをループ
            # 進捗表示（大量データ対応）
            if (idx + 1) % 500 == 0:
                print(f"[INFO] Processing message {idx + 1}/{len(messages_to_save)}...")

            if not message or not message.strip():  # 空のメッセージはスキップ
                continue

            # 重複チェック用キー生成（メッセージ + タイムスタンプ）
            timestamp = metadata.get("timestamp", "")
            key = f"{message}|{timestamp}"

            # 差分登録: 既存データに存在しない場合のみ追加
            if key not in existing_texts:
                try:
                    vector_db.add_texts(
                        [message], metadatas=[metadata]
                    )  # ChromaDBに新規メッセージを追加
                    existing_texts.add(
                        key
                    )  # 追加後に既存セットにも追加（同一実行内での重複防止）

                    if verbose:  # 詳細モードの場合のみ保存メッセージを表示
                        print(
                            f"[SAVE] New: {message[:80]}{'...' if len(message) > 80 else ''}"
                        )

                    new_count += 1  # 新規追加数をカウントアップ

                except Exception as e:
                    print(f"[ERROR] Failed to save message: {e}")
                    error_count += 1
            else:
                # 重複メッセージの場合
                if verbose:  # 詳細モードの場合のみスキップメッセージを表示
                    print(
                        f"[SKIP] Duplicate: {message[:60]}{'...' if len(message) > 60 else ''}"
                    )
                skip_count += 1

        # ステップ11: 処理結果のサマリー表示
        print(f"[INFO] === Processing Summary ===")
        print(f"[INFO] Total messages processed: {len(messages_to_save)}")
        print(f"[INFO] New messages added: {new_count}")
        print(f"[INFO] Duplicate messages skipped: {skip_count}")
        if error_count > 0:
            print(f"[WARNING] Errors encountered: {error_count}")
        print(f"[INFO] Differential registration completed successfully.")

        # ステップ12: ファイル移動処理（新しいデータが追加された場合のみ実行）
        if new_count > 0:  # 新規データが1件以上追加された場合
            try:
                now = datetime.now()  # 現在日時取得
                now_str = now.strftime("%Y-%m-%d_%H-%M-%S-%f")[
                    :-3
                ]  # タイムスタンプ文字列生成（ミリ秒まで）
                done_dir = os.path.dirname(
                    DEFAULT_CHATHISTORY_PATH_BK
                )  # doneディレクトリパス取得
                os.makedirs(
                    done_dir, exist_ok=True
                )  # doneディレクトリ作成（存在しない場合）

                # タイムスタンプ付きファイル名で移動先パスを生成
                original_filename = os.path.basename(chathistory_path)
                name_without_ext, ext = os.path.splitext(original_filename)
                moved_filename = f"{name_without_ext}_{now_str}{ext}"  # タイムスタンプ付きファイル名生成
                moved_path = os.path.join(
                    done_dir, moved_filename
                )  # 移動先ファイルの完全パス

                # ファイルを移動（copyではなくmove）
                shutil.move(chathistory_path, moved_path)
                print(f"[MOVE] Chat history moved to: {moved_path}")  # 移動完了確認
                print(
                    f"[MOVE] Original file removed from: {chathistory_path}"
                )  # 元ファイル削除確認
            except Exception as e:
                print(f"[WARNING] File move failed: {e}")  # 移動失敗時の警告
                print(f"[WARNING] Original file remains at: {chathistory_path}")
        else:
            print(
                "[INFO] No new data added, file move skipped"
            )  # 新規データなしの場合は移動スキップ

        print("[SUCCESS] All chat history loaded into ChromaDB.")  # 処理完了メッセージ
        return True  # 成功を返す

    # ステップ13: 例外処理（各種エラーに対応）
    except FileNotFoundError as e:
        print(f"[ERROR] File not found: {e}")  # ファイルが見つからない場合
        return False  # 失敗を返す
    except UnicodeDecodeError as e:
        print(
            f"[ERROR] Encoding error while reading file: {e}"
        )  # 文字エンコーディングエラー
        return False  # 失敗を返す
    except PermissionError as e:
        print(
            f"[ERROR] Permission denied accessing file: {e}"
        )  # ファイルアクセス権限エラー
        return False  # 失敗を返す
    except OSError as e:
        print(f"[ERROR] OS error while accessing file: {e}")  # OS関連エラー
        return False  # 失敗を返す
    except ValueError as e:
        print(f"[ERROR] Invalid data format in chat history: {e}")  # データ形式エラー
        return False  # 失敗を返す


def is_date_format(text):
    """
    R5/10/22(日) の形式かどうかを判定する

    Args:
        text (str): 判定したい文字列

    Returns:
        bool: 指定した日付形式ならTrue、そうでなければFalse
    """
    # R + 数字 + / + 1-2桁の数字 + / + 1-2桁の数字 + (曜日)
    pattern = r"^R\d+/\d{1,2}/\d{1,2}\([月火水木金土日]\)$"
    return re.match(pattern, text) is not None


def is_time_format(text):
    """
    14:30 の形式かどうかを判定する

    Args:
        text (str): 判定したい文字列

    Returns:
        bool: 時刻形式ならTrue、そうでなければFalse
    """
    pattern = r"^\d{1,2}:\d{2}$"
    return re.match(pattern, text) is not None


def clean_invisible_characters(text):
    """
    見えない制御文字を除去する関数

    LINE等から取得したテキストに含まれる制御文字（U+2068, U+2069等）を除去し、
    文字化けを防ぐ。

    Args:
        text (str): クリーニングしたいテキスト

    Returns:
        str: クリーニング後のテキスト
    """
    # 問題のある制御文字を除去
    # U+2068: First Strong Isolate
    # U+2069: Pop Directional Isolate
    # U+202A-U+202E: 方向制御文字
    # U+200E, U+200F: 左右マーク
    cleaned = re.sub(r"[\u2068\u2069\u202a-\u202e\u200e\u200f]", "", text)

    # 全角スペースを半角スペースに正規化
    cleaned = cleaned.replace("　", " ")

    # 連続する空白を単一に
    cleaned = re.sub(r" +", " ", cleaned)

    return cleaned.strip()


# --- CLI実行用 ---
def main():
    parser = argparse.ArgumentParser(
        description="チャット履歴をChromaDBにロードするツール"
    )
    parser.add_argument(
        "--input",
        "-i",
        default=DEFAULT_CHATHISTORY_PATH,
        help="チャット履歴テキストファイルのパス",
    )
    parser.add_argument(
        "--persist", "-p", default=PERSIST_DIRECTORY, help="ChromaDB保存先ディレクトリ"
    )
    parser.add_argument(
        "--model",
        "-m",
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="埋め込みモデル名",
    )
    parser.add_argument("--quiet", "-q", action="store_true", help="詳細出力を抑制")
    args = parser.parse_args()

    print("📚 Loading chat history to ChromaDB...")
    success = load_chathistory_to_chromadb(
        chathistory_path=args.input,
        persist_directory=args.persist,
        embedding_model_name=args.model,
        verbose=not args.quiet,
    )
    if success:
        print("🎉 Chat history loading completed successfully!")
    else:
        print("⚠️ Chat history loading failed.")


if __name__ == "__main__":
    main()
