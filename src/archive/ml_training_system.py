#!/usr/bin/env python3
"""
機械学習トレーニングシステム
ChromaDBと会話履歴データを使用した機械学習の実施

【主な機能】
1. ChromaDBからベクトルデータを抽出
2. 会話履歴データからテキストパターンを学習
3. 分類・予測モデルの構築
4. モデル評価と保存
"""

import os
import sys
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import json
import pickle

# 機械学習ライブラリ
try:
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    import matplotlib.pyplot as plt
    import seaborn as sns
except ImportError as e:
    print(f"❌ 必要なライブラリがインストールされていません: {e}")
    print("以下のコマンドでインストールしてください:")
    print("pip install scikit-learn matplotlib seaborn pandas numpy")
    sys.exit(1)

# ChromaDB関連
try:
    from langchain_chroma import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError as e:
    print(f"❌ ChromaDB関連ライブラリがインストールされていません: {e}")
    sys.exit(1)

# プロジェクトルートの絶対パス取得
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'db')
CHROMA_DB_PATH = os.path.join(DB_PATH, 'chroma_store')
CONVERSATION_DB_PATH = os.path.join(DB_PATH, 'conversation_history.db')
MODELS_PATH = os.path.join(PROJECT_ROOT, 'ml_models')

class UmaMLTrainingSystem:
    """
    Uma3 機械学習トレーニングシステム
    """

    def __init__(self):
        """初期化"""
        print("🤖 Uma3 機械学習トレーニングシステム初期化")

        # モデル保存ディレクトリ作成
        os.makedirs(MODELS_PATH, exist_ok=True)

        # データ格納用
        self.chroma_data = []
        self.conversation_data = []
        self.features = None
        self.labels = None

        # モデル
        self.vectorizer = None
        self.scaler = None
        self.classifier = None
        self.cluster_model = None

    def load_chroma_data(self) -> bool:
        """ChromaDBからデータを読み込み"""
        try:
            print("📊 ChromaDBからデータを読み込み中...")

            # 埋め込みモデル初期化
            embedding_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )

            # ChromaDB接続
            vector_db = Chroma(
                persist_directory=CHROMA_DB_PATH,
                embedding_function=embedding_model
            )

            # 全データを取得
            collection = vector_db._collection
            all_data = collection.get()

            if not all_data['documents']:
                print("⚠️ ChromaDBにデータが見つかりません")
                return False

            # データ構造化
            for i, (doc, metadata, embedding) in enumerate(zip(
                all_data['documents'],
                all_data['metadatas'],
                all_data.get('embeddings', [])
            )):
                self.chroma_data.append({
                    'id': i,
                    'document': doc,
                    'metadata': metadata or {},
                    'embedding': embedding
                })

            print(f"✅ ChromaDBから {len(self.chroma_data)} 件のデータを読み込み")
            return True

        except Exception as e:
            print(f"❌ ChromaDBデータ読み込みエラー: {e}")
            return False

    def load_conversation_data(self) -> bool:
        """会話履歴データベースからデータを読み込み"""
        try:
            print("💬 会話履歴データを読み込み中...")

            if not os.path.exists(CONVERSATION_DB_PATH):
                print("⚠️ 会話履歴データベースが見つかりません")
                return False

            # SQLite接続
            conn = sqlite3.connect(CONVERSATION_DB_PATH)
            cursor = conn.cursor()

            # テーブル構造確認
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"📋 データベーステーブル: {[table[0] for table in tables]}")

            # 会話データ取得
            try:
                cursor.execute("""
                    SELECT * FROM conversation_history
                    ORDER BY timestamp DESC
                    LIMIT 1000
                """)
                rows = cursor.fetchall()

                # カラム名取得
                cursor.execute("PRAGMA table_info(conversation_history)")
                columns = [column[1] for column in cursor.fetchall()]

                # データ構造化
                for row in rows:
                    row_dict = dict(zip(columns, row))
                    self.conversation_data.append(row_dict)

                print(f"✅ 会話履歴から {len(self.conversation_data)} 件のデータを読み込み")

            except sqlite3.OperationalError as e:
                print(f"⚠️ 会話履歴テーブルエラー: {e}")
                # 代替テーブル確認
                for table_name in [table[0] for table in tables]:
                    try:
                        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                        sample_data = cursor.fetchall()
                        print(f"📊 {table_name} サンプル: {len(sample_data)} 件")
                    except:
                        continue

            conn.close()
            return True

        except Exception as e:
            print(f"❌ 会話履歴データ読み込みエラー: {e}")
            return False

    def prepare_features(self) -> bool:
        """機械学習用特徴量を準備"""
        try:
            print("🔧 機械学習用特徴量を準備中...")

            if not self.chroma_data:
                print("❌ ChromaDBデータが必要です")
                return False

            # テキストデータ準備
            documents = [item['document'] for item in self.chroma_data]

            # TF-IDFベクトル化
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words=None,  # 日本語対応のため
                ngram_range=(1, 2)
            )

            tfidf_features = self.vectorizer.fit_transform(documents)

            # メタデータから特徴量抽出
            metadata_features = []
            for item in self.chroma_data:
                metadata = item['metadata']
                features = [
                    len(item['document']),  # 文書長
                    1 if metadata.get('category') == 'チーム構成' else 0,  # カテゴリ
                    1 if metadata.get('grade') == '3年生' else 0,  # 学年
                    1 if '翔平' in item['document'] else 0,  # 特定選手名
                    1 if '聡太' in item['document'] else 0,
                    1 if '勘太' in item['document'] else 0,
                    1 if '質問' in item['document'] else 0,  # 質問タイプ
                    1 if '回答' in item['document'] else 0   # 回答タイプ
                ]
                metadata_features.append(features)

            metadata_features = np.array(metadata_features)

            # 特徴量結合
            self.features = np.hstack([
                tfidf_features.toarray(),
                metadata_features
            ])

            # ラベル準備（カテゴリ分類用）
            self.labels = []
            for item in self.chroma_data:
                category = item['metadata'].get('category', 'その他')
                if category == 'チーム構成':
                    self.labels.append(0)
                elif category == 'FAQ':
                    self.labels.append(1)
                elif category == '選手情報':
                    self.labels.append(2)
                else:
                    self.labels.append(3)

            self.labels = np.array(self.labels)

            print(f"✅ 特徴量準備完了: {self.features.shape}, ラベル数: {len(np.unique(self.labels))}")
            return True

        except Exception as e:
            print(f"❌ 特徴量準備エラー: {e}")
            return False

    def train_classification_model(self) -> bool:
        """分類モデルの訓練"""
        try:
            print("🎯 分類モデルを訓練中...")

            if self.features is None or self.labels is None:
                print("❌ 特徴量とラベルが必要です")
                return False

            # データ分割
            X_train, X_test, y_train, y_test = train_test_split(
                self.features, self.labels,
                test_size=0.3,
                random_state=42,
                stratify=self.labels
            )

            # スケーリング
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)

            # 複数モデルで比較
            models = {
                'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
                'LogisticRegression': LogisticRegression(random_state=42, max_iter=1000)
            }

            best_model = None
            best_score = 0

            for name, model in models.items():
                print(f"📊 {name} モデル訓練中...")

                model.fit(X_train_scaled, y_train)
                predictions = model.predict(X_test_scaled)
                score = accuracy_score(y_test, predictions)

                print(f"✅ {name} 精度: {score:.4f}")
                print("📋 分類レポート:")
                print(classification_report(y_test, predictions))

                if score > best_score:
                    best_score = score
                    best_model = model
                    self.classifier = model

            print(f"🏆 最高精度モデル: {best_score:.4f}")

            # モデル保存
            model_file = os.path.join(MODELS_PATH, 'classification_model.pkl')
            scaler_file = os.path.join(MODELS_PATH, 'scaler.pkl')
            vectorizer_file = os.path.join(MODELS_PATH, 'vectorizer.pkl')

            with open(model_file, 'wb') as f:
                pickle.dump(self.classifier, f)
            with open(scaler_file, 'wb') as f:
                pickle.dump(self.scaler, f)
            with open(vectorizer_file, 'wb') as f:
                pickle.dump(self.vectorizer, f)

            print(f"💾 モデル保存完了: {MODELS_PATH}")
            return True

        except Exception as e:
            print(f"❌ モデル訓練エラー: {e}")
            return False

    def train_clustering_model(self) -> bool:
        """クラスタリングモデルの訓練"""
        try:
            print("🔍 クラスタリングモデルを訓練中...")

            if self.features is None:
                print("❌ 特徴量が必要です")
                return False

            # 特徴量スケーリング
            if self.scaler is None:
                self.scaler = StandardScaler()
                features_scaled = self.scaler.fit_transform(self.features)
            else:
                features_scaled = self.scaler.transform(self.features)

            # K-meansクラスタリング
            n_clusters = min(5, len(np.unique(self.labels)))  # 最大5クラスタ
            self.cluster_model = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = self.cluster_model.fit_predict(features_scaled)

            # クラスタ分析
            print("📊 クラスタ分析結果:")
            for i in range(n_clusters):
                cluster_docs = [self.chroma_data[j]['document'] for j, label in enumerate(cluster_labels) if label == i]
                print(f"クラスタ {i}: {len(cluster_docs)} 件")
                if cluster_docs:
                    print(f"  サンプル: {cluster_docs[0][:100]}...")

            # クラスタモデル保存
            cluster_file = os.path.join(MODELS_PATH, 'cluster_model.pkl')
            with open(cluster_file, 'wb') as f:
                pickle.dump(self.cluster_model, f)

            print("✅ クラスタリング完了")
            return True

        except Exception as e:
            print(f"❌ クラスタリングエラー: {e}")
            return False

    def generate_training_report(self):
        """訓練結果レポート生成"""
        try:
            print("📈 訓練結果レポートを生成中...")

            report = {
                'timestamp': datetime.now().isoformat(),
                'data_summary': {
                    'chroma_documents': len(self.chroma_data),
                    'conversation_records': len(self.conversation_data),
                    'feature_dimensions': self.features.shape if self.features is not None else None,
                    'unique_labels': len(np.unique(self.labels)) if self.labels is not None else None
                },
                'models_trained': {
                    'classification': self.classifier is not None,
                    'clustering': self.cluster_model is not None,
                    'vectorizer': self.vectorizer is not None,
                    'scaler': self.scaler is not None
                }
            }

            # レポート保存
            report_file = os.path.join(MODELS_PATH, 'training_report.json')
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            print("✅ レポート生成完了")
            print(f"📄 レポートファイル: {report_file}")

            # サマリー表示
            print("\n" + "="*50)
            print("🎉 機械学習訓練完了サマリー")
            print("="*50)
            print(f"📊 学習データ数: {report['data_summary']['chroma_documents']} 件")
            print(f"💬 会話履歴数: {report['data_summary']['conversation_records']} 件")
            print(f"🔧 特徴量次元: {report['data_summary']['feature_dimensions']}")
            print(f"🏷️ ラベル種類: {report['data_summary']['unique_labels']} 種類")
            print(f"💾 保存場所: {MODELS_PATH}")

        except Exception as e:
            print(f"❌ レポート生成エラー: {e}")

    def run_full_training(self):
        """完全な機械学習パイプライン実行"""
        print("🚀 機械学習訓練パイプライン開始")

        # Step 1: データ読み込み
        if not self.load_chroma_data():
            print("❌ ChromaDBデータ読み込み失敗")
            return False

        if not self.load_conversation_data():
            print("⚠️ 会話履歴データ読み込み失敗（継続）")

        # Step 2: 特徴量準備
        if not self.prepare_features():
            print("❌ 特徴量準備失敗")
            return False

        # Step 3: モデル訓練
        classification_success = self.train_classification_model()
        clustering_success = self.train_clustering_model()

        if not (classification_success or clustering_success):
            print("❌ すべてのモデル訓練が失敗")
            return False

        # Step 4: レポート生成
        self.generate_training_report()

        print("🎉 機械学習訓練パイプライン完了！")
        return True

def main():
    """メイン実行関数"""
    print("=" * 60)
    print("🤖 Uma3 機械学習トレーニングシステム")
    print("=" * 60)

    # システム初期化
    ml_system = UmaMLTrainingSystem()

    # 完全訓練実行
    success = ml_system.run_full_training()

    if success:
        print("\n✅ 機械学習システムの構築が完了しました！")
        print(f"📁 モデルファイル: {MODELS_PATH}")
        print("🔮 これらのモデルを使用して、新しいデータの分類や予測が可能です。")
    else:
        print("\n❌ 機械学習システムの構築に失敗しました。")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
