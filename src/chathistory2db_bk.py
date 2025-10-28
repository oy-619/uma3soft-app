import hashlib
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

from langchain.agents import Tool, initialize_agent
from langchain.chat_models import ChatOpenAI
from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)

DATA_DIR = Path("data")
DEFAULT_CHATHISTORY_PATH = Path(
    r"C:\Users\o_you\iCloudDrive\3L68KQB4HG~com~readdle~CommonDocuments\chat_history\[LINE] ☆馬三ソフト☆のトーク.txt"
)
STORE_DIR = Path(r"C:\work\ws_python\GenerationAiCamp\Lesson25\uma3soft-app\storage")
REGISTRY = Path(
    r"C:\work\ws_python\GenerationAiCamp\Lesson25\uma3soft-app\file_registry.json"
)  # ファイルのハッシュ管理用（自作）
DEFAULT_CHATHISTORY_PATH_BK = Path(
    r"C:\Users\o_you\iCloudDrive\3L68KQB4HG~com~readdle~CommonDocuments\chat_history\done\[LINE] ☆馬三ソフト☆のトーク.txt"
)


def file_hash(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def file_meta(path, **kwargs):
    # 例：相対パスを doc_id に
    return {"doc_id": str(Path(path).as_posix())}


def main():
    print("雄一さん、こんにちは！これは main 関数からの実行です。")
    verbose = (os.getenv("DEBUG"),)  # 詳細ログ出力フラグ

    # ステップ2: 入力ファイルの存在確認
    if not os.path.exists(DEFAULT_CHATHISTORY_PATH):
        print(f"[warning] Chat history file not found: {DEFAULT_CHATHISTORY_PATH}")
        return  # ファイルが存在しない場合は処理終了

    # 1) 既存インデックスがあれば読む／なければ新規作成
    if STORE_DIR.exists():
        storage_context = StorageContext.from_defaults(persist_dir=str(STORE_DIR))
        index = load_index_from_storage(storage_context)
    else:
        docs = SimpleDirectoryReader(
            input_dir="data",
            recursive=True,
            filename_as_id=True,
            file_metadata=file_meta,
            input_files=[DEFAULT_CHATHISTORY_PATH],
        ).load_data()
        index = VectorStoreIndex.from_documents(docs)
        index.storage_context.persist(persist_dir=str(STORE_DIR))

    # 2) 直近状態（ファイル→ハッシュ）を作る
    current = {str(p): file_hash(p) for p in DATA_DIR.rglob("*") if p.is_file()}

    # 3) 前回状態を読む
    prev = json.loads(REGISTRY.read_text()) if REGISTRY.exists() else {}

    # 4) 差分を計算
    added = [p for p in current.keys() if p not in prev]
    removed = [p for p in prev.keys() if p not in current]
    updated = [p for p in current.keys() if p in prev and current[p] != prev[p]]

    # 5) 削除を反映（doc_id=ファイルパスをそのまま使う）
    for p in removed:
        # 参照ドキュメント単位で削除（チャンクもベクターもまとめて）
        index.delete_ref_doc(ref_doc_id=p, delete_from_docstore=True)

    # 6) 追加・更新を反映（filename_as_id=True で doc_id=ファイルパス になる）
    targets = added + updated
    if targets:
        docs = SimpleDirectoryReader(
            input_files=targets, filename_as_id=True
        ).load_data()

        # update_ref_doc があれば1発、無ければ「削除→挿入」でもOK
        for d in docs:
            # 安全策：先に消してから入れ直す（存在しなくてもエラーにならない実装が多い）
            index.delete_ref_doc(ref_doc_id=d.doc_id, delete_from_docstore=True)
            index.insert(d)

    # 7) 永続化
    index.storage_context.persist(persist_dir=str(STORE_DIR))
    REGISTRY.write_text(json.dumps(current, ensure_ascii=False, indent=2))

    now = datetime.now()  # 現在日時取得
    now_str = now.strftime("%Y-%m-%d_%H-%M-%S-%f")[
        :-3
    ]  # タイムスタンプ文字列生成（ミリ秒まで）
    done_dir = os.path.dirname(DEFAULT_CHATHISTORY_PATH_BK)  # doneディレクトリパス取得
    os.makedirs(done_dir, exist_ok=True)  # doneディレクトリ作成（存在しない場合）

    # タイムスタンプ付きファイル名で移動先パスを生成
    original_filename = os.path.basename(DEFAULT_CHATHISTORY_PATH)
    name_without_ext, ext = os.path.splitext(original_filename)
    moved_filename = (
        f"{name_without_ext}_{now_str}{ext}"  # タイムスタンプ付きファイル名生成
    )
    moved_path = os.path.join(done_dir, moved_filename)  # 移動先ファイルの完全パス

    # ファイルを移動（copyではなくmove）
    shutil.move(DEFAULT_CHATHISTORY_PATH, moved_path)
    print(f"[MOVE] Chat history moved to: {moved_path}")  # 移動完了確認

    query_engine = index.as_query_engine()
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.3,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )
    search_tool = Tool(
        name="ChatHistorySearch",
        func=lambda q: query_engine.query(q).response,
        description="過去のトーク履歴から関連情報を検索します",
    )

    agent = initialize_agent(
        [search_tool], llm, agent_type="zero-shot-react-description"
    )

    return agent


if __name__ == "__main__":
    agent = main()
    query = "今週の予定は？"
    response = agent.run(query)
    print(response)
