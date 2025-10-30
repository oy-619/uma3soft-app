#!/usr/bin/env python3
"""
チームデータをChromaDBに追加するスクリプト
３年生選手情報を学習データとして追加
"""

import os
import sys
from datetime import datetime
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# プロジェクトルートの絶対パス取得
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DEFAULT_CHROMA_PERSIST_DIRECTORY = os.path.join(PROJECT_ROOT, 'db', 'chroma_store')

def add_team_data():
    """３年生選手情報をChromaDBに追加"""

    print("=== チーム情報学習データ追加 ===")

    # 現在のディレクトリを確認
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")

    # ChromaDBの初期化（uma3.pyと同じ設定）
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # ChromaDBパスの設定（絶対パス方式）
    chroma_path = DEFAULT_CHROMA_PERSIST_DIRECTORY

    # ディレクトリが存在しない場合は作成
    os.makedirs(chroma_path, exist_ok=True)

    print(f"ChromaDB path: {chroma_path}")

    try:
        vector_db = Chroma(
            persist_directory=chroma_path,
            embedding_function=embedding_model,
        )
        print("✅ ChromaDB接続成功")
    except Exception as e:
        print(f"❌ ChromaDB接続エラー: {e}")
        return False

    # 現在の日時をタイムスタンプとして使用
    current_time = datetime.now()
    timestamp = current_time.strftime("R7/%m/%d(%a) %H:%M")

    # ３年生選手情報のドキュメント作成
    team_documents = [
        # 基本的な３年生選手情報
        Document(
            page_content="[チーム情報] ３年生の選手: 翔平、聡太、勘太、暖大、英汰、悠琉",
            metadata={
                "user": "システム管理者",
                "timestamp": timestamp,
                "category": "チーム構成",
                "grade": "3年生",
                "data_type": "選手リスト"
            }
        ),

        # より自然な質問形式での学習データ
        Document(
            page_content="３年生の選手は誰ですか？→翔平、聡太、勘太、暖大、英汰、悠琉の6名です。",
            metadata={
                "user": "システム管理者",
                "timestamp": timestamp,
                "category": "FAQ",
                "grade": "3年生",
                "data_type": "質問回答"
            }
        ),

        # 詳細情報版
        Document(
            page_content="[ノート] 羽村ライオンズ 3年生選手名簿\n・翔平（しょうへい）\n・聡太（そうた）\n・勘太（かんた）\n・暖大（はるだい）\n・英汰（えいた）\n・悠琉（ゆうる）\n合計6名",
            metadata={
                "user": "システム管理者",
                "timestamp": timestamp,
                "category": "チーム構成",
                "grade": "3年生",
                "data_type": "詳細名簿"
            }
        ),

        # バリエーション質問対応
        Document(
            page_content="3年生メンバー: 翔平、聡太、勘太、暖大、英汰、悠琉",
            metadata={
                "user": "システム管理者",
                "timestamp": timestamp,
                "category": "チーム構成",
                "grade": "3年生",
                "data_type": "メンバーリスト"
            }
        ),

        # 検索キーワード拡充版
        Document(
            page_content="３年生 3年生 最上級生 先輩 翔平 聡太 勘太 暖大 英汰 悠琉 羽村ライオンズ ソフトボール選手",
            metadata={
                "user": "システム管理者",
                "timestamp": timestamp,
                "category": "検索キーワード",
                "grade": "3年生",
                "data_type": "キーワード集"
            }
        )
    ]

    try:
        # ドキュメントをChromaDBに追加
        print(f"📝 {len(team_documents)}件のチーム情報を追加中...")

        for i, doc in enumerate(team_documents, 1):
            vector_db.add_documents([doc])
            print(f"  {i}. 追加完了: {doc.page_content[:50]}...")

        print("✅ チーム情報の追加完了")

        # 追加結果の確認テスト
        print("\n=== 追加結果テスト ===")
        test_queries = [
            "３年生の選手",
            "3年生選手",
            "3年生メンバー",
            "翔平",
            "最上級生"
        ]

        for query in test_queries:
            results = vector_db.similarity_search(query, k=2)
            print(f"\nクエリ: '{query}'")
            for j, result in enumerate(results, 1):
                content_preview = result.page_content.replace('\n', ' ')[:80]
                print(f"  {j}. {content_preview}...")

        return True

    except Exception as e:
        print(f"❌ データ追加エラー: {e}")
        return False

if __name__ == "__main__":
    success = add_team_data()
    if success:
        print("\n🎉 チーム情報学習データの追加が完了しました！")
        print("これで「３年生の選手」という質問に正確に回答できるようになります。")
    else:
        print("\n❌ チーム情報の追加に失敗しました。")
        sys.exit(1)
