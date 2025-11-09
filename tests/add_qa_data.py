#!/usr/bin/env python3
"""
３年生選手に関するQ&A学習データを追加
様々な質問パターンに対応
"""

import os
from datetime import datetime
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# プロジェクトルートの絶対パス取得
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DEFAULT_CHROMA_PERSIST_DIRECTORY = os.path.join(PROJECT_ROOT, 'db', 'chroma_store')

def add_qa_data():
    """３年生選手のQ&A学習データを追加"""

    print("=== ３年生選手Q&A学習データ追加 ===")

    # ChromaDBの初期化
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # ChromaDBパスの設定（絶対パス方式）
    chroma_path = DEFAULT_CHROMA_PERSIST_DIRECTORY

    # ディレクトリが存在しない場合は作成
    os.makedirs(chroma_path, exist_ok=True)

    vector_db = Chroma(
        persist_directory=chroma_path,
        embedding_function=embedding_model,
    )

    # 現在の日時をタイムスタンプとして使用
    current_time = datetime.now()
    timestamp = current_time.strftime("R7/%m/%d(%a) %H:%M")

    # Q&A形式の学習データ
    qa_documents = [
        # 直接的な質問と回答
        Document(
            page_content="Q: ３年生の選手は誰ですか？\nA: 翔平、聡太、勘太、暖大、英汰、悠琉の6名です。",
            metadata={
                "user": "システム管理者",
                "timestamp": timestamp,
                "category": "Q&A",
                "data_type": "質問回答"
            }
        ),

        # バリエーション質問
        Document(
            page_content="Q: 3年生選手を教えて\nA: 翔平、聡太、勘太、暖大、英汰、悠琉",
            metadata={
                "user": "システム管理者",
                "timestamp": timestamp,
                "category": "Q&A",
                "data_type": "質問回答"
            }
        ),

        Document(
            page_content="Q: 最上級生のメンバーは？\nA: 翔平、聡太、勘太、暖大、英汰、悠琉の６人です。",
            metadata={
                "user": "システム管理者",
                "timestamp": timestamp,
                "category": "Q&A",
                "data_type": "質問回答"
            }
        ),

        Document(
            page_content="Q: 3年生は何人いますか？\nA: 6人います。翔平、聡太、勘太、暖大、英汰、悠琉です。",
            metadata={
                "user": "システム管理者",
                "timestamp": timestamp,
                "category": "Q&A",
                "data_type": "質問回答"
            }
        ),

        # 個別名前での検索対応
        Document(
            page_content="翔平は３年生の選手です。同学年には聡太、勘太、暖大、英汰、悠琉がいます。",
            metadata={
                "user": "システム管理者",
                "timestamp": timestamp,
                "category": "選手情報",
                "data_type": "個別情報"
            }
        ),

        Document(
            page_content="聡太は３年生です。３年生選手は翔平、聡太、勘太、暖大、英汰、悠琉の6名です。",
            metadata={
                "user": "システム管理者",
                "timestamp": timestamp,
                "category": "選手情報",
                "data_type": "個別情報"
            }
        ),

        # 関連用語での検索強化
        Document(
            page_content="羽村ライオンズ 最上級生 先輩 ３年生選手 翔平 聡太 勘太 暖大 英汰 悠琉 6名 6人",
            metadata={
                "user": "システム管理者",
                "timestamp": timestamp,
                "category": "検索用語",
                "data_type": "関連キーワード"
            }
        )
    ]

    try:
        # ドキュメントをChromaDBに追加
        print(f"📝 {len(qa_documents)}件のQ&A学習データを追加中...")

        for i, doc in enumerate(qa_documents, 1):
            vector_db.add_documents([doc])
            print(f"  {i}. 追加完了: {doc.page_content[:60]}...")

        print("✅ Q&A学習データの追加完了")
        return True

    except Exception as e:
        print(f"❌ Q&Aデータ追加エラー: {e}")
        return False

if __name__ == "__main__":
    success = add_qa_data()
    if success:
        print("\n🎉 ３年生選手Q&A学習データの追加が完了しました！")
    else:
        print("\n❌ Q&Aデータの追加に失敗しました。")
