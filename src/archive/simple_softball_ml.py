#!/usr/bin/env python3
"""
ソフトボールチーム簡易機械学習システム

作成された学習データを使用して基本的な機械学習を実行する
軽量版 - 基本的な分類とパターン分析に集中
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any
import warnings
warnings.filterwarnings('ignore')

# 基本的な機械学習ライブラリ
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score
import joblib

class SimpleSoftballMLTrainer:
    """ソフトボール簡易機械学習トレーナークラス"""

    def __init__(self, data_dir: str):
        """初期化"""
        self.data_dir = data_dir
        self.df = None
        self.models = {}
        self.encoders = {}
        self.vectorizer = None

        print("🤖 ソフトボール簡易機械学習トレーナーを初期化しました")

    def load_data(self) -> bool:
        """学習データの読み込み"""
        csv_file = os.path.join(self.data_dir, "softball_learning_data.csv")

        if not os.path.exists(csv_file):
            print(f"❌ データファイルが見つかりません: {csv_file}")
            return False

        try:
            self.df = pd.read_csv(csv_file)
            print(f"✅ データ読み込み完了: {len(self.df)}件")
            return True
        except Exception as e:
            print(f"❌ データ読み込みエラー: {e}")
            return False

    def preprocess_data(self):
        """データの前処理"""
        print("🔧 データを前処理中...")

        # 欠損値処理
        self.df['content'] = self.df['content'].fillna('')
        self.df['user'] = self.df['user'].fillna('unknown')

        # カテゴリエンコーディング
        self.encoders['category'] = LabelEncoder()
        self.df['category_encoded'] = self.encoders['category'].fit_transform(self.df['category'])

        print(f"✅ カテゴリ数: {len(self.encoders['category'].classes_)}")
        print(f"📊 カテゴリ: {list(self.encoders['category'].classes_)}")

    def train_category_classifier(self) -> Dict[str, float]:
        """カテゴリ分類モデルの訓練"""
        print("\n🎯 カテゴリ分類モデルを訓練中...")

        # TF-IDF特徴量作成
        self.vectorizer = TfidfVectorizer(
            max_features=500,  # 特徴量数を減らして高速化
            ngram_range=(1, 1),  # unigramのみ
            min_df=2
        )

        X = self.vectorizer.fit_transform(self.df['content'])
        y = self.df['category_encoded']

        # 訓練・テストデータ分割
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        print(f"📊 訓練データ: {X_train.shape[0]}件, テストデータ: {X_test.shape[0]}件")

        # ランダムフォレストで訓練
        model = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=1)
        model.fit(X_train, y_train)

        # 評価
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        self.models['category_classifier'] = model

        print(f"✅ カテゴリ分類精度: {accuracy:.3f}")

        # 詳細レポート
        print("\n📊 詳細評価レポート:")
        report = classification_report(y_test, y_pred,
                                     target_names=self.encoders['category'].classes_,
                                     output_dict=True)

        for category, metrics in report.items():
            if isinstance(metrics, dict) and 'precision' in metrics:
                print(f"   {category}: 精度={metrics['precision']:.3f}, "
                      f"再現率={metrics['recall']:.3f}, F1={metrics['f1-score']:.3f}")

        return {'accuracy': accuracy, 'report': report}

    def analyze_data_patterns(self) -> Dict[str, Any]:
        """データパターン分析"""
        print("\n📈 データパターンを分析中...")

        patterns = {}

        # カテゴリ分布
        category_dist = self.df['category'].value_counts()
        patterns['category_distribution'] = category_dist.to_dict()

        print("📊 カテゴリ分布:")
        for category, count in category_dist.items():
            percentage = (count / len(self.df)) * 100
            print(f"   {category}: {count}件 ({percentage:.1f}%)")

        # 選手言及パターン
        player_mentions = {}
        for _, row in self.df.iterrows():
            players_str = str(row['players_mentioned'])
            if players_str and players_str != 'nan' and players_str != '':
                players = [p.strip() for p in players_str.split(',')]
                for player in players:
                    if player:
                        player_mentions[player] = player_mentions.get(player, 0) + 1

        # 上位10選手
        top_players = dict(sorted(player_mentions.items(), key=lambda x: x[1], reverse=True)[:10])
        patterns['top_mentioned_players'] = top_players

        print("\n👥 よく言及される選手 (上位5名):")
        for player, count in list(top_players.items())[:5]:
            print(f"   {player}: {count}回")

        # メッセージ長の統計
        msg_length_stats = {
            'mean': float(self.df['message_length'].mean()),
            'median': float(self.df['message_length'].median()),
            'max': int(self.df['message_length'].max()),
            'min': int(self.df['message_length'].min())
        }
        patterns['message_length_stats'] = msg_length_stats

        print(f"\n📝 メッセージ長統計:")
        print(f"   平均: {msg_length_stats['mean']:.1f}文字")
        print(f"   中央値: {msg_length_stats['median']:.1f}文字")
        print(f"   最大: {msg_length_stats['max']}文字")
        print(f"   最小: {msg_length_stats['min']}文字")

        # 時間帯分析（データがある場合）
        if 'hour' in self.df.columns:
            hour_data = self.df[self.df['hour'].notna()]
            if not hour_data.empty:
                hour_dist = hour_data['hour'].value_counts().sort_index()
                patterns['hourly_distribution'] = hour_dist.to_dict()

                print(f"\n⏰ 投稿時間帯 (上位3時間帯):")
                for hour, count in hour_dist.head(3).items():
                    print(f"   {int(hour)}時: {count}件")

        return patterns

    def predict_category(self, text: str) -> str:
        """新しいテキストのカテゴリを予測"""
        if 'category_classifier' not in self.models or self.vectorizer is None:
            return "モデルが訓練されていません"

        # テキストをベクトル化
        text_vector = self.vectorizer.transform([text])

        # 予測
        prediction = self.models['category_classifier'].predict(text_vector)[0]
        category = self.encoders['category'].inverse_transform([prediction])[0]

        # 予測確率
        probabilities = self.models['category_classifier'].predict_proba(text_vector)[0]
        confidence = max(probabilities)

        return f"{category} (信頼度: {confidence:.3f})"

    def save_results(self, results: Dict[str, Any], output_dir: str):
        """結果の保存"""
        os.makedirs(output_dir, exist_ok=True)

        # モデル保存
        if 'category_classifier' in self.models:
            model_file = os.path.join(output_dir, "category_classifier.joblib")
            joblib.dump(self.models['category_classifier'], model_file)
            print(f"💾 分類モデル保存: {model_file}")

        # ベクトライザー保存
        if self.vectorizer:
            vec_file = os.path.join(output_dir, "tfidf_vectorizer.joblib")
            joblib.dump(self.vectorizer, vec_file)
            print(f"💾 ベクトライザー保存: {vec_file}")

        # エンコーダー保存
        if self.encoders:
            for name, encoder in self.encoders.items():
                enc_file = os.path.join(output_dir, f"encoder_{name}.joblib")
                joblib.dump(encoder, enc_file)
                print(f"💾 エンコーダー保存: {enc_file}")

        # 結果レポート保存
        report = {
            "timestamp": datetime.now().isoformat(),
            "dataset_size": len(self.df),
            "categories": list(self.encoders['category'].classes_),
            "results": results
        }

        report_file = os.path.join(output_dir, "training_results.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"📋 結果レポート保存: {report_file}")

    def demo_predictions(self):
        """予測デモ"""
        print("\n🎯 予測デモ:")

        demo_texts = [
            "今日の練習お疲れ様でした",
            "明日の試合頑張りましょう",
            "集合時間は9時です",
            "新くんナイスプレーでした",
            "ありがとうございました"
        ]

        for text in demo_texts:
            prediction = self.predict_category(text)
            print(f"   「{text}」 → {prediction}")

def main():
    """メイン処理"""
    print("=" * 60)
    print("🥎 ソフトボールチーム簡易機械学習システム")
    print("=" * 60)

    # 設定
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_dir = os.path.join(project_root, "softball_learning_data")
    output_dir = os.path.join(project_root, "ml_results")

    # トレーナー初期化
    trainer = SimpleSoftballMLTrainer(data_dir)

    # データ読み込み
    if not trainer.load_data():
        return

    # データ前処理
    trainer.preprocess_data()

    # 結果格納用
    results = {}

    # カテゴリ分類モデル訓練
    classification_results = trainer.train_category_classifier()
    results['classification'] = classification_results

    # データパターン分析
    pattern_results = trainer.analyze_data_patterns()
    results['patterns'] = pattern_results

    # 結果保存
    trainer.save_results(results, output_dir)

    # 予測デモ
    trainer.demo_predictions()

    # 結果サマリー
    print("\n" + "=" * 60)
    print("🎯 機械学習システム完了!")
    print("=" * 60)
    print(f"📊 データセット サイズ: {len(trainer.df)}件")
    print(f"🎯 カテゴリ数: {len(trainer.encoders['category'].classes_)}")
    print(f"✅ 分類精度: {classification_results['accuracy']:.3f}")
    print(f"📁 出力先: {output_dir}")
    print(f"   - category_classifier.joblib (分類モデル)")
    print(f"   - tfidf_vectorizer.joblib (テキスト特徴抽出)")
    print(f"   - training_results.json (詳細結果)")

if __name__ == "__main__":
    main()
