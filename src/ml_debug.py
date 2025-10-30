#!/usr/bin/env python3
"""
機械学習トレーニングシステム（デバッグ版）
ChromaDBと会話履歴データを使用した機械学習の実施
"""

import os
import sys
import sqlite3
import traceback

def debug_database_content():
    """データベースの内容をデバッグ確認"""
    print("🔍 データベース内容デバッグ")

    # プロジェクトルートの絶対パス取得
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    DB_PATH = os.path.join(PROJECT_ROOT, 'db')
    CHROMA_DB_PATH = os.path.join(DB_PATH, 'chroma_store')
    CONVERSATION_DB_PATH = os.path.join(DB_PATH, 'conversation_history.db')

    print(f"📁 PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"📁 DB_PATH: {DB_PATH}")
    print(f"📁 CHROMA_DB_PATH: {CHROMA_DB_PATH}")
    print(f"📁 CONVERSATION_DB_PATH: {CONVERSATION_DB_PATH}")

    # ChromaDBデバッグ
    try:
        print("\n=== ChromaDB デバッグ ===")
        from langchain_chroma import Chroma
        from langchain_huggingface import HuggingFaceEmbeddings

        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        vector_db = Chroma(
            persist_directory=CHROMA_DB_PATH,
            embedding_function=embedding_model
        )

        collection = vector_db._collection
        all_data = collection.get()

        print(f"📊 ChromaDBドキュメント数: {len(all_data.get('documents', []))}")
        print(f"📊 メタデータ数: {len(all_data.get('metadatas', []))}")
        print(f"📊 埋め込み数: {len(all_data.get('embeddings', []))}")

        # サンプルデータ表示
        if all_data.get('documents'):
            for i, (doc, meta) in enumerate(zip(all_data['documents'][:3], all_data['metadatas'][:3])):
                print(f"サンプル {i+1}: {doc[:100]}... | メタデータ: {meta}")

    except Exception as e:
        print(f"❌ ChromaDBエラー: {e}")
        traceback.print_exc()

    # 会話履歴デバッグ
    try:
        print("\n=== 会話履歴データベース デバッグ ===")

        if os.path.exists(CONVERSATION_DB_PATH):
            conn = sqlite3.connect(CONVERSATION_DB_PATH)
            cursor = conn.cursor()

            # テーブル確認
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"📋 テーブル: {[table[0] for table in tables]}")

            for table_name in [table[0] for table in tables]:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"📊 {table_name}: {count} 件")

                    # サンプルデータ
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                    sample_data = cursor.fetchall()
                    if sample_data:
                        cursor.execute(f"PRAGMA table_info({table_name})")
                        columns = [column[1] for column in cursor.fetchall()]
                        print(f"📋 カラム: {columns}")
                        for i, row in enumerate(sample_data):
                            print(f"サンプル {i+1}: {dict(zip(columns, row))}")
                except Exception as inner_e:
                    print(f"⚠️ {table_name} エラー: {inner_e}")

            conn.close()
        else:
            print("❌ 会話履歴データベースが見つかりません")

    except Exception as e:
        print(f"❌ 会話履歴エラー: {e}")
        traceback.print_exc()

def simple_ml_test():
    """シンプルな機械学習テスト"""
    try:
        print("\n=== シンプル機械学習テスト ===")

        # 必要なライブラリのインポート確認
        try:
            import numpy as np
            import pandas as pd
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score
            print("✅ 機械学習ライブラリインポート成功")
        except ImportError as e:
            print(f"❌ ライブラリインポートエラー: {e}")
            return

        # サンプルデータ作成
        np.random.seed(42)
        X = np.random.randn(100, 5)  # 100サンプル、5特徴量
        y = np.random.randint(0, 3, 100)  # 3クラス分類

        print(f"📊 サンプルデータ: {X.shape}, ラベル: {len(np.unique(y))} クラス")

        # 訓練テスト分割
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        # ランダムフォレストモデル
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X_train, y_train)

        # 予測
        predictions = model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)

        print(f"✅ テストモデル精度: {accuracy:.4f}")

        # モデル保存テスト
        import pickle
        PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        MODELS_PATH = os.path.join(PROJECT_ROOT, 'ml_models')
        os.makedirs(MODELS_PATH, exist_ok=True)

        test_model_file = os.path.join(MODELS_PATH, 'test_model.pkl')
        with open(test_model_file, 'wb') as f:
            pickle.dump(model, f)

        print(f"💾 テストモデル保存: {test_model_file}")

        # 保存確認
        if os.path.exists(test_model_file):
            print("✅ ファイル保存成功")
            with open(test_model_file, 'rb') as f:
                loaded_model = pickle.load(f)
            print("✅ ファイル読み込み成功")

    except Exception as e:
        print(f"❌ シンプル機械学習テストエラー: {e}")
        traceback.print_exc()

def main():
    """メイン実行関数"""
    print("=" * 60)
    print("🔍 機械学習システム デバッグ")
    print("=" * 60)

    # データベース内容確認
    debug_database_content()

    # シンプル機械学習テスト
    simple_ml_test()

    print("\n✅ デバッグ完了")

if __name__ == "__main__":
    main()
