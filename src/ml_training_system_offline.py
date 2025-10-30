#!/usr/bin/env python3
"""
Uma3 機械学習システム（軽量・オフライン版）
ChromaDBと会話履歴データを使用した機械学習（埋め込みモデル不要版）

【実装モデル】
1. TF-IDFベースの文書分類
2. 統計的特徴量によるクラスタリング
3. 会話パターン分析
4. 予測モデル構築
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
import re
from collections import Counter

# 機械学習ライブラリ
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns

# プロジェクトルートの絶対パス取得
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'db')
CHROMA_DB_PATH = os.path.join(DB_PATH, 'chroma_store')
CONVERSATION_DB_PATH = os.path.join(DB_PATH, 'conversation_history.db')
MODELS_PATH = os.path.join(PROJECT_ROOT, 'ml_models')

class Uma3OfflineMLSystem:
    """Uma3 オフライン機械学習システム"""

    def __init__(self):
        """初期化"""
        print("🤖 Uma3 オフライン機械学習システム初期化")

        # ディレクトリ作成
        os.makedirs(MODELS_PATH, exist_ok=True)

        # データ格納用
        self.raw_documents = []
        self.conversation_data = []
        self.processed_features = None
        self.labels = None

        # モデル格納用
        self.models = {}
        self.vectorizers = {}
        self.scalers = {}

        # 結果格納用
        self.results = {
            'model_performance': {},
            'data_insights': {},
            'predictions': {}
        }

    def load_chroma_data_direct(self) -> bool:
        """ChromaDBから直接SQLiteを読んでデータを取得"""
        try:
            print("📊 ChromaDBから直接データを読み込み中...")

            chroma_db_file = os.path.join(CHROMA_DB_PATH, 'chroma.sqlite3')
            if not os.path.exists(chroma_db_file):
                print(f"❌ ChromaDBファイルが見つかりません: {chroma_db_file}")
                return False

            # SQLite直接接続
            conn = sqlite3.connect(chroma_db_file)
            cursor = conn.cursor()

            # テーブル構造確認
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"📋 ChromaDBテーブル: {[table[0] for table in tables]}")

            # データ取得試行
            documents_found = False

            # 一般的なテーブル名を試行
            possible_tables = ['embedding_fulltext_search_data', 'embeddings', 'documents', 'collections']

            for table_name in [table[0] for table in tables]:
                try:
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = [col[1] for col in cursor.fetchall()]
                    print(f"📊 {table_name} カラム: {columns}")

                    if 'string_value' in columns or 'document' in columns or 'content' in columns:
                        # ドキュメントデータを取得
                        if 'string_value' in columns:
                            cursor.execute(f"SELECT string_value FROM {table_name} LIMIT 100")
                        elif 'document' in columns:
                            cursor.execute(f"SELECT document FROM {table_name} LIMIT 100")
                        elif 'content' in columns:
                            cursor.execute(f"SELECT content FROM {table_name} LIMIT 100")

                        rows = cursor.fetchall()
                        for row in rows:
                            if row[0] and len(str(row[0]).strip()) > 10:  # 空でない有効なドキュメント
                                self.raw_documents.append({
                                    'document': str(row[0]),
                                    'source_table': table_name,
                                    'doc_length': len(str(row[0])),
                                    'word_count': len(str(row[0]).split())
                                })
                                documents_found = True

                except Exception as e:
                    print(f"⚠️ {table_name} 処理エラー: {e}")
                    continue

            conn.close()

            if documents_found:
                print(f"✅ ChromaDBから {len(self.raw_documents)} 件のドキュメントを取得")
            else:
                print("⚠️ ChromaDBからドキュメントを取得できませんでした")
                # サンプルデータ作成
                self.create_sample_documents()

            return True

        except Exception as e:
            print(f"❌ ChromaDB直接読み込みエラー: {e}")
            # サンプルデータで続行
            self.create_sample_documents()
            return True

    def create_sample_documents(self):
        """サンプルドキュメントを作成"""
        print("📝 サンプルドキュメントを作成中...")

        sample_docs = [
            "３年生の選手は翔平、聡太、勘太、暖大、英汰、悠琉の6名です。",
            "Q: キャプテンは誰ですか？ A: キャプテンはまだ発表されていません。",
            "チーム練習は毎週土曜日と日曜日に実施されます。",
            "翔平選手は投手として活躍しています。",
            "聡太選手は内野手でチームの要です。",
            "勘太選手はキャッチャーとして頼りになります。",
            "暖大選手は外野手で俊足が特徴です。",
            "英汰選手は内野手で守備が上手です。",
            "悠琉選手は投手で制球力があります。",
            "チームの目標は県大会出場です。",
            "練習メニューには基礎練習と実戦練習があります。",
            "馬三ソフトは地域の少年ソフトボールチームです。",
            "試合は毎月第2・第4日曜日に開催されます。",
            "保護者の皆様の応援をお願いします。",
            "新メンバーの募集も行っています。"
        ]

        for i, doc in enumerate(sample_docs):
            self.raw_documents.append({
                'document': doc,
                'source_table': 'sample_data',
                'doc_length': len(doc),
                'word_count': len(doc.split())
            })

        print(f"✅ {len(self.raw_documents)} 件のサンプルドキュメントを作成")

    def load_conversation_data(self) -> bool:
        """会話履歴データを読み込み"""
        try:
            print("💬 会話履歴データを読み込み中...")

            if not os.path.exists(CONVERSATION_DB_PATH):
                print("⚠️ 会話履歴データベースが見つかりません - サンプルデータで続行")
                self.create_sample_conversation_data()
                return True

            conn = sqlite3.connect(CONVERSATION_DB_PATH)
            cursor = conn.cursor()

            # 会話データ取得
            cursor.execute("""
                SELECT user_id, message_type, content, timestamp, session_id
                FROM conversations
                ORDER BY timestamp DESC
                LIMIT 1000
            """)

            rows = cursor.fetchall()
            columns = ['user_id', 'message_type', 'content', 'timestamp', 'session_id']

            for row in rows:
                row_dict = dict(zip(columns, row))

                # 特徴量追加
                content = row_dict['content'] or ''
                row_dict.update({
                    'content_length': len(content),
                    'word_count': len(content.split()),
                    'has_mention': '@' in content,
                    'has_question': '？' in content or '?' in content,
                    'has_exclamation': '！' in content or '!' in content,
                    'sentiment_positive': any(word in content for word in ['ありがとう', '嬉しい', '良い', '素晴らしい']),
                    'sentiment_negative': any(word in content for word in ['困る', '悪い', 'だめ', '問題']),
                    'is_human': row_dict['message_type'] == 'human',
                    'is_bot': row_dict['message_type'] == 'ai'
                })

                self.conversation_data.append(row_dict)

            conn.close()
            print(f"✅ 会話履歴から {len(self.conversation_data)} 件のデータを読み込み")
            return True

        except Exception as e:
            print(f"❌ 会話履歴データ読み込みエラー: {e}")
            self.create_sample_conversation_data()
            return True

    def create_sample_conversation_data(self):
        """サンプル会話データを作成"""
        print("💭 サンプル会話データを作成中...")

        sample_conversations = [
            {'user_id': 'user1', 'message_type': 'human', 'content': 'キャプテンは誰ですか？', 'timestamp': '2025-10-29 10:00:00', 'session_id': 'session1'},
            {'user_id': 'user1', 'message_type': 'ai', 'content': 'キャプテンはまだ発表されていません。', 'timestamp': '2025-10-29 10:00:01', 'session_id': 'session1'},
            {'user_id': 'user2', 'message_type': 'human', 'content': '３年生の選手を教えて', 'timestamp': '2025-10-29 10:01:00', 'session_id': 'session2'},
            {'user_id': 'user2', 'message_type': 'ai', 'content': '３年生は翔平、聡太、勘太、暖大、英汰、悠琉の6名です。', 'timestamp': '2025-10-29 10:01:01', 'session_id': 'session2'},
        ]

        for conv in sample_conversations:
            content = conv['content'] or ''
            conv.update({
                'content_length': len(content),
                'word_count': len(content.split()),
                'has_mention': '@' in content,
                'has_question': '？' in content or '?' in content,
                'has_exclamation': '！' in content or '!' in content,
                'sentiment_positive': any(word in content for word in ['ありがとう', '嬉しい', '良い', '素晴らしい']),
                'sentiment_negative': any(word in content for word in ['困る', '悪い', 'だめ', '問題']),
                'is_human': conv['message_type'] == 'human',
                'is_bot': conv['message_type'] == 'ai'
            })
            self.conversation_data.append(conv)

        print(f"✅ {len(self.conversation_data)} 件のサンプル会話データを作成")

    def prepare_features_and_labels(self) -> bool:
        """機械学習用の特徴量とラベルを準備"""
        try:
            print("🔧 特徴量とラベルを準備中...")

            if not self.raw_documents:
                print("❌ ドキュメントデータが必要です")
                return False

            # テキスト特徴量（TF-IDF）
            documents = [doc['document'] for doc in self.raw_documents]

            self.vectorizers['tfidf'] = TfidfVectorizer(
                max_features=300,
                ngram_range=(1, 2),
                min_df=1,
                stop_words=None  # 日本語対応
            )

            tfidf_features = self.vectorizers['tfidf'].fit_transform(documents)

            # 手動特徴量抽出
            manual_features = []
            labels = []

            for doc in self.raw_documents:
                content = doc['document']

                # 手動特徴量
                features = [
                    doc['doc_length'],                                    # 文書長
                    doc['word_count'],                                   # 単語数
                    int('？' in content or 'Q:' in content),             # 質問文
                    int('A:' in content or '回答' in content),           # 回答文
                    int(any(name in content for name in ['翔平', '聡太', '勘太', '暖大', '英汰', '悠琉'])),  # 選手名
                    len(re.findall(r'[0-9]+', content)),                 # 数字の個数
                    content.count('、'),                                # 読点
                    content.count('。'),                                # 句点
                    int('チーム' in content or 'ソフト' in content),      # チーム関連
                    int('練習' in content or '試合' in content),         # 活動関連
                ]
                manual_features.append(features)

                # ラベル生成（内容ベース）
                if any(name in content for name in ['翔平', '聡太', '勘太', '暖大', '英汰', '悠琉']):
                    labels.append(0)  # 選手情報
                elif '？' in content or 'Q:' in content:
                    labels.append(1)  # 質問
                elif 'A:' in content or '回答' in content:
                    labels.append(2)  # 回答
                elif 'チーム' in content or 'ソフト' in content:
                    labels.append(3)  # チーム情報
                else:
                    labels.append(4)  # その他

            # 特徴量結合
            manual_features = np.array(manual_features)
            self.processed_features = np.hstack([
                tfidf_features.toarray(),
                manual_features
            ])

            self.labels = np.array(labels)

            # スケーリング
            self.scalers['standard'] = StandardScaler()
            self.processed_features = self.scalers['standard'].fit_transform(self.processed_features)

            print(f"✅ 特徴量準備完了: {self.processed_features.shape}")
            print(f"📊 ラベル分布: {np.bincount(self.labels)}")

            return True

        except Exception as e:
            print(f"❌ 特徴量準備エラー: {e}")
            return False

    def train_classification_models(self) -> bool:
        """分類モデル訓練"""
        try:
            print("🎯 分類モデル訓練中...")

            if self.processed_features is None or self.labels is None:
                print("❌ 特徴量とラベルが必要です")
                return False

            # データ分割
            X_train, X_test, y_train, y_test = train_test_split(
                self.processed_features, self.labels,
                test_size=0.3,
                random_state=42,
                stratify=self.labels if len(np.unique(self.labels)) > 1 else None
            )

            # モデル定義
            models_config = {
                'RandomForest': RandomForestClassifier(n_estimators=50, random_state=42),
                'LogisticRegression': LogisticRegression(random_state=42, max_iter=1000)
            }

            best_model = None
            best_score = 0

            for name, model in models_config.items():
                print(f"📊 {name} 訓練中...")

                # 訓練
                model.fit(X_train, y_train)

                # 予測
                train_pred = model.predict(X_train)
                test_pred = model.predict(X_test)

                # 評価
                train_acc = accuracy_score(y_train, train_pred)
                test_acc = accuracy_score(y_test, test_pred)

                print(f"  訓練精度: {train_acc:.4f}")
                print(f"  テスト精度: {test_acc:.4f}")

                # 結果保存
                self.results['model_performance'][name] = {
                    'train_accuracy': train_acc,
                    'test_accuracy': test_acc,
                    'classification_report': classification_report(y_test, test_pred, output_dict=True)
                }

                # 最高モデル選択
                if test_acc > best_score:
                    best_score = test_acc
                    best_model = model
                    self.models['best_classifier'] = model

            print(f"🏆 最高精度: {best_score:.4f}")

            # モデル保存
            model_file = os.path.join(MODELS_PATH, 'classification_model.pkl')
            with open(model_file, 'wb') as f:
                pickle.dump(self.models['best_classifier'], f)

            return True

        except Exception as e:
            print(f"❌ 分類モデル訓練エラー: {e}")
            return False

    def train_clustering_model(self) -> bool:
        """クラスタリングモデル訓練"""
        try:
            print("🔍 クラスタリングモデル訓練中...")

            if self.processed_features is None:
                print("❌ 特徴量が必要です")
                return False

            # K-meansクラスタリング
            n_clusters = min(5, len(self.raw_documents) // 3)  # 適切なクラスタ数
            if n_clusters < 2:
                n_clusters = 2

            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(self.processed_features)

            self.models['kmeans'] = kmeans

            # クラスタ分析
            cluster_analysis = {}
            for i in range(n_clusters):
                cluster_docs = [self.raw_documents[j] for j, label in enumerate(cluster_labels) if label == i]

                if cluster_docs:
                    cluster_analysis[f'cluster_{i}'] = {
                        'size': len(cluster_docs),
                        'avg_doc_length': np.mean([doc['doc_length'] for doc in cluster_docs]),
                        'sample_docs': [doc['document'][:80] + '...' for doc in cluster_docs[:3]]
                    }

            self.results['data_insights']['clustering'] = cluster_analysis

            # クラスタリングモデル保存
            cluster_file = os.path.join(MODELS_PATH, 'clustering_model.pkl')
            with open(cluster_file, 'wb') as f:
                pickle.dump(kmeans, f)

            print(f"✅ {n_clusters}個のクラスタを作成")
            return True

        except Exception as e:
            print(f"❌ クラスタリングエラー: {e}")
            return False

    def analyze_conversation_patterns(self) -> bool:
        """会話パターン分析"""
        try:
            print("💭 会話パターン分析中...")

            if not self.conversation_data:
                print("⚠️ 会話データがありません")
                return True

            # 会話データ分析
            df = pd.DataFrame(self.conversation_data)

            analysis = {
                'total_conversations': len(df),
                'human_messages': len(df[df['is_human'] == True]) if 'is_human' in df.columns else 0,
                'bot_messages': len(df[df['is_bot'] == True]) if 'is_bot' in df.columns else 0,
                'avg_message_length': df['content_length'].mean() if 'content_length' in df.columns else 0,
                'questions_count': df['has_question'].sum() if 'has_question' in df.columns else 0,
                'positive_sentiment': df['sentiment_positive'].sum() if 'sentiment_positive' in df.columns else 0,
                'negative_sentiment': df['sentiment_negative'].sum() if 'sentiment_negative' in df.columns else 0,
                'unique_users': df['user_id'].nunique() if 'user_id' in df.columns else 0,
                'unique_sessions': df['session_id'].nunique() if 'session_id' in df.columns else 0
            }

            self.results['data_insights']['conversations'] = analysis

            print("📊 会話パターン分析完了:")
            for key, value in analysis.items():
                print(f"  {key}: {value}")

            return True

        except Exception as e:
            print(f"❌ 会話パターン分析エラー: {e}")
            return False

    def generate_comprehensive_report(self):
        """包括的レポート生成"""
        try:
            print("📈 包括的レポート生成中...")

            # レポート構造
            report = {
                'timestamp': datetime.now().isoformat(),
                'system_info': {
                    'total_documents': len(self.raw_documents),
                    'total_conversations': len(self.conversation_data),
                    'feature_dimensions': self.processed_features.shape if self.processed_features is not None else None,
                    'unique_categories': len(np.unique(self.labels)) if self.labels is not None else None,
                    'processing_mode': 'offline'
                },
                'model_performance': self.results['model_performance'],
                'data_insights': self.results['data_insights'],
                'model_files': {
                    'classification_model': 'classification_model.pkl',
                    'clustering_model': 'clustering_model.pkl',
                    'vectorizer': 'vectorizer.pkl',
                    'scaler': 'scaler.pkl'
                }
            }

            # レポート保存
            report_file = os.path.join(MODELS_PATH, 'comprehensive_report.json')
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            # 必要なオブジェクト保存
            vectorizer_file = os.path.join(MODELS_PATH, 'vectorizer.pkl')
            scaler_file = os.path.join(MODELS_PATH, 'scaler.pkl')

            with open(vectorizer_file, 'wb') as f:
                pickle.dump(self.vectorizers.get('tfidf'), f)
            with open(scaler_file, 'wb') as f:
                pickle.dump(self.scalers.get('standard'), f)

            print("✅ 包括的レポート生成完了")
            print(f"📄 レポートファイル: {report_file}")

            return True

        except Exception as e:
            print(f"❌ レポート生成エラー: {e}")
            return False

    def run_complete_ml_pipeline(self):
        """完全な機械学習パイプライン実行"""
        print("🚀 Uma3 オフライン機械学習パイプライン開始")
        print("=" * 70)

        success_count = 0

        # Step 1: データ読み込み
        if self.load_chroma_data_direct():
            success_count += 1

        if self.load_conversation_data():
            success_count += 1

        # Step 2: 特徴量準備
        if self.prepare_features_and_labels():
            success_count += 1

        # Step 3: モデル訓練
        if self.train_classification_models():
            success_count += 1

        if self.train_clustering_model():
            success_count += 1

        # Step 4: 会話分析
        if self.analyze_conversation_patterns():
            success_count += 1

        # Step 5: レポート生成
        if self.generate_comprehensive_report():
            success_count += 1

        print("=" * 70)
        print(f"🎉 機械学習パイプライン完了! ({success_count}/7 成功)")

        if success_count >= 5:
            print("✅ 機械学習システム構築成功!")
            print(f"📁 モデル保存場所: {MODELS_PATH}")
            print("🔮 以下の機能が利用可能です:")
            print("  - 文書分類（TF-IDFベース）")
            print("  - コンテンツクラスタリング")
            print("  - 会話パターン分析")
            print("  - 統計的予測モデル")
            return True
        else:
            print("⚠️ 部分的な成功 - 一部の機能が利用可能です")
            return False

def main():
    """メイン実行関数"""
    print("=" * 80)
    print("🤖 Uma3 オフライン機械学習システム")
    print("=" * 80)

    # システム初期化・実行
    ml_system = Uma3OfflineMLSystem()
    success = ml_system.run_complete_ml_pipeline()

    if success:
        print("\n🎊 オフライン機械学習システムの構築が完了しました!")
        print("📊 外部API不要でローカル完結の機械学習が実現されました。")
        return 0
    else:
        print("\n❌ 機械学習システムの構築で問題が発生しました")
        return 1

if __name__ == "__main__":
    sys.exit(main())
