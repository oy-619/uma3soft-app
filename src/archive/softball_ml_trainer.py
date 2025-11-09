#!/usr/bin/env python3
"""
ソフトボールチーム機械学習トレーナー

作成された学習データを使用して複数の機械学習モデルを訓練する
- テキスト分類（カテゴリ予測）
- 感情分析
- 選手言及予測
- 時系列パターン分析
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# 機械学習ライブラリ
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.pipeline import Pipeline
import joblib

# 日本語テキスト処理
import re

class SoftballMLTrainer:
    """ソフトボール機械学習トレーナークラス"""

    def __init__(self, data_dir: str):
        """初期化"""
        self.data_dir = data_dir
        self.df = None
        self.models = {}
        self.encoders = {}
        self.vectorizers = {}
        self.scalers = {}

        # 日本語テキスト処理の初期化
        self.mecab = None  # MeCabは使用せず、基本的なテキスト処理を使用
        print("📝 基本的なテキスト処理を使用します（MeCabなし）")
        print("📝 基本的なテキスト処理を使用します（MeCabなし）")

        print("🤖 ソフトボール機械学習トレーナーを初期化しました")

    def load_data(self) -> bool:
        """学習データの読み込み"""
        csv_file = os.path.join(self.data_dir, "softball_learning_data.csv")

        if not os.path.exists(csv_file):
            print(f"❌ データファイルが見つかりません: {csv_file}")
            return False

        try:
            self.df = pd.read_csv(csv_file)
            print(f"✅ データ読み込み完了: {len(self.df)}件")
            print(f"📊 カラム: {list(self.df.columns)}")
            return True
        except Exception as e:
            print(f"❌ データ読み込みエラー: {e}")
            return False

    def preprocess_text(self, text: str) -> str:
        """テキストの前処理"""
        if pd.isna(text):
            return ""

        # 基本的なクリーニング
        text = str(text)
        text = re.sub(r'https?://[^\s]+', '', text)  # URL削除
        text = re.sub(r'[【】()]', '', text)  # 括弧削除
        text = re.sub(r'\s+', ' ', text)  # 空白正規化

        # MeCabが利用可能な場合は形態素解析
        if self.mecab:
            try:
                text = self.mecab.parse(text).strip()
            except:
                pass

        return text

    def prepare_features(self) -> Dict[str, Any]:
        """特徴量の準備"""
        print("🔧 特徴量を準備中...")

        # テキスト前処理
        self.df['processed_content'] = self.df['content'].apply(self.preprocess_text)

        # カテゴリカル変数のエンコーディング
        self.encoders['category'] = LabelEncoder()
        self.df['category_encoded'] = self.encoders['category'].fit_transform(self.df['category'])

        # ユーザーエンコーディング
        self.encoders['user'] = LabelEncoder()
        self.df['user_encoded'] = self.encoders['user'].fit_transform(self.df['user'].fillna('unknown'))

        # TF-IDF特徴量
        self.vectorizers['tfidf'] = TfidfVectorizer(
            max_features=1000,
            stop_words=None,  # 日本語用ストップワードは別途設定
            ngram_range=(1, 2),
            min_df=2
        )

        tfidf_features = self.vectorizers['tfidf'].fit_transform(self.df['processed_content'])

        # 数値特徴量
        numeric_features = [
            'message_length', 'has_question', 'has_exclamation',
            'has_emoji', 'is_weekend', 'hour'
        ]

        # 欠損値処理
        for col in numeric_features:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0)

        # スケーリング
        self.scalers['numeric'] = StandardScaler()
        numeric_scaled = self.scalers['numeric'].fit_transform(self.df[numeric_features])

        features = {
            'tfidf': tfidf_features,
            'numeric': numeric_scaled,
            'category_labels': self.df['category_encoded'].values,
            'user_labels': self.df['user_encoded'].values
        }

        print(f"✅ 特徴量準備完了")
        print(f"   - TF-IDF: {tfidf_features.shape}")
        print(f"   - 数値特徴量: {numeric_scaled.shape}")
        print(f"   - カテゴリ数: {len(self.encoders['category'].classes_)}")

        return features

    def train_category_classifier(self, features: Dict[str, Any]) -> Dict[str, float]:
        """カテゴリ分類モデルの訓練"""
        print("\n🎯 カテゴリ分類モデルを訓練中...")

        # TF-IDF特徴量と数値特徴量を結合
        from scipy.sparse import hstack
        X = hstack([features['tfidf'], features['numeric']])
        y = features['category_labels']

        # 訓練・テストデータ分割
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # 複数のモデルを試行
        classifiers = {
            'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
            'NaiveBayes': MultinomialNB(),
            'LogisticRegression': LogisticRegression(random_state=42, max_iter=1000),
            'SVM': SVC(random_state=42, probability=True)
        }

        results = {}
        best_score = 0
        best_model = None

        for name, classifier in classifiers.items():
            # 訓練
            classifier.fit(X_train, y_train)

            # 予測
            y_pred = classifier.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)

            # クロスバリデーション
            cv_scores = cross_val_score(classifier, X_train, y_train, cv=5)

            results[name] = {
                'accuracy': accuracy,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std()
            }

            print(f"   {name}: 精度={accuracy:.3f}, CV={cv_scores.mean():.3f}±{cv_scores.std():.3f}")

            # 最高性能モデルを記録
            if accuracy > best_score:
                best_score = accuracy
                best_model = classifier
                self.models['category_classifier'] = classifier

        # 詳細な評価レポート
        print(f"\n📊 最高性能モデルの詳細評価:")
        y_pred_best = best_model.predict(X_test)
        print(classification_report(y_test, y_pred_best,
                                  target_names=self.encoders['category'].classes_))

        return results

    def train_sentiment_analyzer(self, features: Dict[str, Any]) -> Dict[str, float]:
        """感情分析モデルの訓練"""
        print("\n😊 感情分析モデルを訓練中...")

        # 感情ラベルの作成（基本的なルールベース）
        sentiment_labels = []
        for _, row in self.df.iterrows():
            content = str(row['content']).lower()

            # ポジティブキーワード
            positive_words = ['ありがとう', '感謝', '頑張', '応援', '素晴らしい', '良い', '楽しい']
            # ネガティブキーワード
            negative_words = ['残念', '心配', '疲れ', '困った', '難しい', '問題']

            pos_count = sum(1 for word in positive_words if word in content)
            neg_count = sum(1 for word in negative_words if word in content)

            if pos_count > neg_count:
                sentiment_labels.append(1)  # ポジティブ
            elif neg_count > pos_count:
                sentiment_labels.append(-1)  # ネガティブ
            else:
                sentiment_labels.append(0)  # ニュートラル

        sentiment_labels = np.array(sentiment_labels)

        # 特徴量
        X = features['tfidf']
        y = sentiment_labels

        # 訓練・テストデータ分割
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # ロジスティック回帰で訓練
        sentiment_model = LogisticRegression(random_state=42, max_iter=1000)
        sentiment_model.fit(X_train, y_train)

        # 評価
        y_pred = sentiment_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        self.models['sentiment_analyzer'] = sentiment_model

        print(f"✅ 感情分析精度: {accuracy:.3f}")

        # 感情分布
        sentiment_dist = pd.Series(sentiment_labels).value_counts().sort_index()
        print(f"📊 感情分布: ネガティブ={sentiment_dist.get(-1, 0)}, "
              f"ニュートラル={sentiment_dist.get(0, 0)}, ポジティブ={sentiment_dist.get(1, 0)}")

        return {'accuracy': accuracy, 'distribution': sentiment_dist.to_dict()}

    def train_player_mention_predictor(self, features: Dict[str, Any]) -> Dict[str, float]:
        """選手言及予測モデルの訓練"""
        print("\n👥 選手言及予測モデルを訓練中...")

        # 選手言及バイナリラベルの作成
        has_player_mention = (self.df['players_mentioned'].fillna('').str.len() > 0).astype(int)

        # 特徴量
        from scipy.sparse import hstack
        X = hstack([features['tfidf'], features['numeric']])
        y = has_player_mention

        # 訓練・テストデータ分割
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # ランダムフォレストで訓練
        player_model = RandomForestClassifier(n_estimators=100, random_state=42)
        player_model.fit(X_train, y_train)

        # 評価
        y_pred = player_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        self.models['player_mention_predictor'] = player_model

        print(f"✅ 選手言及予測精度: {accuracy:.3f}")
        print(f"📊 選手言及率: {has_player_mention.mean():.3f}")

        return {'accuracy': accuracy, 'mention_rate': has_player_mention.mean()}

    def analyze_patterns(self) -> Dict[str, Any]:
        """パターン分析"""
        print("\n📈 パターン分析中...")

        patterns = {}

        # 時間帯別投稿パターン
        hour_pattern = self.df.groupby('hour')['category'].value_counts().unstack(fill_value=0)
        patterns['hourly_categories'] = hour_pattern.to_dict()

        # 週末vs平日パターン
        weekend_pattern = self.df.groupby('is_weekend')['category'].value_counts().unstack(fill_value=0)
        patterns['weekend_categories'] = weekend_pattern.to_dict()

        # 選手別言及パターン
        player_mentions = {}
        for _, row in self.df.iterrows():
            players = str(row['players_mentioned']).split(',')
            category = row['category']
            for player in players:
                player = player.strip()
                if player and player != 'nan':
                    if player not in player_mentions:
                        player_mentions[player] = {}
                    player_mentions[player][category] = player_mentions[player].get(category, 0) + 1

        patterns['player_category_mentions'] = player_mentions

        # メッセージ長とカテゴリの関係
        length_by_category = self.df.groupby('category')['message_length'].agg(['mean', 'std']).to_dict()
        patterns['message_length_by_category'] = length_by_category

        print("✅ パターン分析完了")

        return patterns

    def save_models(self, output_dir: str):
        """訓練済みモデルの保存"""
        models_dir = os.path.join(output_dir, "trained_models")
        os.makedirs(models_dir, exist_ok=True)

        # モデル保存
        for name, model in self.models.items():
            model_file = os.path.join(models_dir, f"{name}.joblib")
            joblib.dump(model, model_file)
            print(f"💾 {name}を保存: {model_file}")

        # エンコーダー保存
        for name, encoder in self.encoders.items():
            encoder_file = os.path.join(models_dir, f"encoder_{name}.joblib")
            joblib.dump(encoder, encoder_file)

        # ベクタライザー保存
        for name, vectorizer in self.vectorizers.items():
            vec_file = os.path.join(models_dir, f"vectorizer_{name}.joblib")
            joblib.dump(vectorizer, vec_file)

        # スケーラー保存
        for name, scaler in self.scalers.items():
            scaler_file = os.path.join(models_dir, f"scaler_{name}.joblib")
            joblib.dump(scaler, scaler_file)

        print(f"📁 全モデル保存完了: {models_dir}")

    def generate_training_report(self, results: Dict[str, Any], output_dir: str):
        """訓練レポートの生成"""
        report = {
            "training_summary": {
                "timestamp": datetime.now().isoformat(),
                "dataset_size": len(self.df),
                "categories": list(self.encoders['category'].classes_),
                "num_categories": len(self.encoders['category'].classes_)
            },
            "model_performance": results,
            "data_statistics": {
                "category_distribution": self.df['category'].value_counts().to_dict(),
                "average_message_length": float(self.df['message_length'].mean()),
                "total_players_mentioned": len(set(
                    [p.strip() for players in self.df['players_mentioned'].fillna('').str.split(',')
                     for p in players if p.strip() and p.strip() != 'nan']
                ))
            }
        }

        report_file = os.path.join(output_dir, "training_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"📋 訓練レポート保存: {report_file}")
        return report

def main():
    """メイン処理"""
    print("=" * 70)
    print("🤖 ソフトボールチーム機械学習システム")
    print("=" * 70)

    # 設定
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_dir = os.path.join(project_root, "softball_learning_data")
    output_dir = os.path.join(project_root, "ml_outputs")

    os.makedirs(output_dir, exist_ok=True)

    # トレーナー初期化
    trainer = SoftballMLTrainer(data_dir)

    # データ読み込み
    if not trainer.load_data():
        return

    # 特徴量準備
    features = trainer.prepare_features()

    # モデル訓練
    results = {}

    # 1. カテゴリ分類
    results['category_classification'] = trainer.train_category_classifier(features)

    # 2. 感情分析
    results['sentiment_analysis'] = trainer.train_sentiment_analyzer(features)

    # 3. 選手言及予測
    results['player_mention_prediction'] = trainer.train_player_mention_predictor(features)

    # 4. パターン分析
    results['pattern_analysis'] = trainer.analyze_patterns()

    # モデル保存
    trainer.save_models(output_dir)

    # レポート生成
    report = trainer.generate_training_report(results, output_dir)

    # 結果サマリー
    print("\n" + "=" * 70)
    print("🎯 機械学習システム構築完了!")
    print("=" * 70)
    print(f"📊 データセット: {len(trainer.df)}件")
    print(f"🎯 カテゴリ数: {len(trainer.encoders['category'].classes_)}")
    print(f"👥 ユニークユーザー数: {len(trainer.encoders['user'].classes_)}")
    print(f"📁 出力先: {output_dir}")
    print(f"   - trained_models/ (訓練済みモデル)")
    print(f"   - training_report.json (訓練レポート)")

if __name__ == "__main__":
    main()
