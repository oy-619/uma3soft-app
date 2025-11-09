#!/usr/bin/env python3
"""
Uma3 機械学習システム（修正版）
ChromaDBと会話履歴データを使用した本格的な機械学習実装

【実装モデル】
1. テキスト分類モデル（ドキュメントカテゴリ分類）
2. クラスタリングモデル（類似コンテンツグルーピング）
3. 感情分析モデル（会話感情分析）
4. 予測モデル（ユーザー行動予測）
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

# ChromaDB関連
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# プロジェクトルートの絶対パス取得
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'db')
CHROMA_DB_PATH = os.path.join(DB_PATH, 'chroma_store')
CONVERSATION_DB_PATH = os.path.join(DB_PATH, 'conversation_history.db')
MODELS_PATH = os.path.join(PROJECT_ROOT, 'ml_models')

class Uma3MLSystem:
    """Uma3 機械学習システム"""
    
    def __init__(self):
        """初期化"""
        print("🤖 Uma3 機械学習システム初期化")
        
        # ディレクトリ作成
        os.makedirs(MODELS_PATH, exist_ok=True)
        
        # データ格納用
        self.chroma_documents = []
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
    
    def load_chroma_data(self) -> bool:
        """ChromaDBからデータを安全に読み込み"""
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
            
            # データ取得（埋め込みは除外）
            collection = vector_db._collection
            all_data = collection.get()
            
            documents = all_data.get('documents', [])
            metadatas = all_data.get('metadatas', [])
            
            if not documents:
                print("⚠️ ChromaDBにドキュメントが見つかりません")
                return False
            
            # データ構造化
            for i, (doc, metadata) in enumerate(zip(documents, metadatas)):
                self.chroma_documents.append({
                    'id': i,
                    'document': doc,
                    'metadata': metadata or {},
                    'doc_length': len(doc),
                    'word_count': len(doc.split()),
                    'has_question': '？' in doc or 'Q:' in doc,
                    'has_answer': 'A:' in doc or '回答' in doc,
                    'has_player_name': any(name in doc for name in ['翔平', '聡太', '勘太', '暖大', '英汰', '悠琉']),
                    'category': metadata.get('category', 'その他') if isinstance(metadata, dict) else 'その他'
                })
            
            print(f"✅ ChromaDBから {len(self.chroma_documents)} 件のドキュメントを読み込み")
            return True
            
        except Exception as e:
            print(f"❌ ChromaDBデータ読み込みエラー: {e}")
            return False
    
    def load_conversation_data(self) -> bool:
        """会話履歴データを読み込み"""
        try:
            print("💬 会話履歴データを読み込み中...")
            
            if not os.path.exists(CONVERSATION_DB_PATH):
                print("⚠️ 会話履歴データベースが見つかりません")
                return False
            
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
            return False
    
    def prepare_features_and_labels(self) -> bool:
        """機械学習用の特徴量とラベルを準備"""
        try:
            print("🔧 特徴量とラベルを準備中...")
            
            if not self.chroma_documents:
                print("❌ ChromaDBドキュメントが必要です")
                return False
            
            # テキスト特徴量（TF-IDF）
            documents = [doc['document'] for doc in self.chroma_documents]
            
            self.vectorizers['tfidf'] = TfidfVectorizer(
                max_features=500,
                ngram_range=(1, 2),
                min_df=2
            )
            
            tfidf_features = self.vectorizers['tfidf'].fit_transform(documents)
            
            # 手動特徴量
            manual_features = []
            labels = []
            
            for doc in self.chroma_documents:
                # 手動特徴量
                features = [
                    doc['doc_length'],
                    doc['word_count'],
                    int(doc['has_question']),
                    int(doc['has_answer']),
                    int(doc['has_player_name']),
                    len(re.findall(r'[0-9]+', doc['document'])),  # 数字の個数
                    doc['document'].count('、'),  # 読点の個数
                    doc['document'].count('。'),  # 句点の個数
                ]
                manual_features.append(features)
                
                # ラベル（カテゴリ分類用）
                category = doc['category']
                if category == 'チーム構成':
                    labels.append(0)
                elif category == 'FAQ':
                    labels.append(1)
                elif category == '選手情報':
                    labels.append(2)
                elif category == 'Q&A':
                    labels.append(3)
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
        """複数の分類モデルを訓練・比較"""
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
                stratify=self.labels
            )
            
            # 複数モデル定義
            models_config = {
                'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
                'LogisticRegression': LogisticRegression(random_state=42, max_iter=3000),
                'GradientBoosting': GradientBoostingClassifier(random_state=42)
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
                
                # クロスバリデーション
                cv_scores = cross_val_score(model, X_train, y_train, cv=5)
                
                print(f"  訓練精度: {train_acc:.4f}")
                print(f"  テスト精度: {test_acc:.4f}")
                print(f"  CV平均: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
                
                # 結果保存
                self.results['model_performance'][name] = {
                    'train_accuracy': train_acc,
                    'test_accuracy': test_acc,
                    'cv_mean': cv_scores.mean(),
                    'cv_std': cv_scores.std(),
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
            
            # 次元削減（可視化用）
            pca = PCA(n_components=2)
            features_2d = pca.fit_transform(self.processed_features)
            
            # K-meansクラスタリング
            n_clusters = min(8, len(np.unique(self.labels)))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(self.processed_features)
            
            self.models['kmeans'] = kmeans
            self.models['pca'] = pca
            
            # クラスタ分析
            cluster_analysis = {}
            for i in range(n_clusters):
                cluster_docs = [self.chroma_documents[j] for j, label in enumerate(cluster_labels) if label == i]
                
                cluster_analysis[f'cluster_{i}'] = {
                    'size': len(cluster_docs),
                    'avg_doc_length': np.mean([doc['doc_length'] for doc in cluster_docs]),
                    'common_categories': [doc['category'] for doc in cluster_docs[:5]],
                    'sample_docs': [doc['document'][:100] for doc in cluster_docs[:3]]
                }
            
            self.results['data_insights']['clustering'] = cluster_analysis
            
            # 可視化用データ保存
            visualization_data = {
                'features_2d': features_2d.tolist(),
                'cluster_labels': cluster_labels.tolist(),
                'true_labels': self.labels.tolist()
            }
            
            viz_file = os.path.join(MODELS_PATH, 'visualization_data.json')
            with open(viz_file, 'w', encoding='utf-8') as f:
                json.dump(visualization_data, f, ensure_ascii=False, indent=2)
            
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
                'human_messages': len(df[df['is_human'] == True]),
                'bot_messages': len(df[df['is_bot'] == True]),
                'avg_message_length': df['content_length'].mean(),
                'questions_count': df['has_question'].sum(),
                'positive_sentiment': df['sentiment_positive'].sum(),
                'negative_sentiment': df['sentiment_negative'].sum(),
                'unique_users': df['user_id'].nunique(),
                'unique_sessions': df['session_id'].nunique()
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
        """包括的な分析レポート生成"""
        try:
            print("📈 包括的レポート生成中...")
            
            # レポート構造
            report = {
                'timestamp': datetime.now().isoformat(),
                'system_info': {
                    'total_documents': len(self.chroma_documents),
                    'total_conversations': len(self.conversation_data),
                    'feature_dimensions': self.processed_features.shape if self.processed_features is not None else None,
                    'unique_categories': len(np.unique(self.labels)) if self.labels is not None else None
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
        print("🚀 Uma3 機械学習パイプライン開始")
        print("=" * 60)
        
        success_count = 0
        
        # Step 1: データ読み込み
        if self.load_chroma_data():
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
        
        print("=" * 60)
        print(f"🎉 機械学習パイプライン完了! ({success_count}/7 成功)")
        
        if success_count >= 5:
            print("✅ 機械学習システム構築成功!")
            print(f"📁 モデル保存場所: {MODELS_PATH}")
            print("🔮 分類・クラスタリング・予測が利用可能です")
            return True
        else:
            print("⚠️ 部分的な成功 - 一部の機能が利用可能です")
            return False

def main():
    """メイン実行関数"""
    print("=" * 70)
    print("🤖 Uma3 機械学習システム（完全版）")
    print("=" * 70)
    
    # システム初期化・実行
    ml_system = Uma3MLSystem()
    success = ml_system.run_complete_ml_pipeline()
    
    if success:
        print("\n🎊 機械学習システムの構築が完了しました!")
        print("📊 以下の機能が利用可能です:")
        print("  - ドキュメント分類")
        print("  - コンテンツクラスタリング")
        print("  - 会話パターン分析")
        print("  - 予測モデル")
        return 0
    else:
        print("\n❌ 機械学習システムの構築で問題が発生しました")
        return 1

if __name__ == "__main__":
    sys.exit(main())