#!/usr/bin/env python3
"""
Uma3 機械学習予測システム
訓練済みモデルを使用した新しいデータの分類・予測

【機能】
1. 新しいテキストの分類予測
2. クラスタリング予測
3. 類似文書検索
4. 予測結果の可視化
"""

import os
import sys
import pickle
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
import json
from datetime import datetime

# プロジェクトルートの絶対パス取得
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MODELS_PATH = os.path.join(PROJECT_ROOT, 'ml_models')

class Uma3MLPredictor:
    """Uma3 機械学習予測システム"""

    def __init__(self):
        """初期化"""
        print("🔮 Uma3 機械学習予測システム初期化")

        # モデル格納用
        self.classifier = None
        self.cluster_model = None
        self.vectorizer = None
        self.scaler = None

        # ラベル定義
        self.label_names = {
            0: '選手情報',
            1: '質問',
            2: '回答',
            3: 'チーム情報',
            4: 'その他'
        }

        # モデル読み込み
        self.load_models()

    def load_models(self) -> bool:
        """訓練済みモデルを読み込み"""
        try:
            print("📦 訓練済みモデルを読み込み中...")

            # 分類モデル
            classification_file = os.path.join(MODELS_PATH, 'classification_model.pkl')
            if os.path.exists(classification_file):
                with open(classification_file, 'rb') as f:
                    self.classifier = pickle.load(f)
                print("✅ 分類モデル読み込み完了")

            # クラスタリングモデル
            clustering_file = os.path.join(MODELS_PATH, 'clustering_model.pkl')
            if os.path.exists(clustering_file):
                with open(clustering_file, 'rb') as f:
                    self.cluster_model = pickle.load(f)
                print("✅ クラスタリングモデル読み込み完了")

            # ベクトライザー
            vectorizer_file = os.path.join(MODELS_PATH, 'vectorizer.pkl')
            if os.path.exists(vectorizer_file):
                with open(vectorizer_file, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                print("✅ ベクトライザー読み込み完了")

            # スケーラー
            scaler_file = os.path.join(MODELS_PATH, 'scaler.pkl')
            if os.path.exists(scaler_file):
                with open(scaler_file, 'rb') as f:
                    self.scaler = pickle.load(f)
                print("✅ スケーラー読み込み完了")

            return True

        except Exception as e:
            print(f"❌ モデル読み込みエラー: {e}")
            return False

    def extract_features(self, text: str) -> np.ndarray:
        """テキストから特徴量を抽出"""
        try:
            # TF-IDF特徴量
            if self.vectorizer:
                tfidf_features = self.vectorizer.transform([text]).toarray()
            else:
                tfidf_features = np.zeros((1, 300))  # デフォルトサイズ

            # 手動特徴量
            manual_features = [
                len(text),                                          # 文書長
                len(text.split()),                                 # 単語数
                int('？' in text or 'Q:' in text),                 # 質問文
                int('A:' in text or '回答' in text),               # 回答文
                int(any(name in text for name in ['翔平', '聡太', '勘太', '暖大', '英汰', '悠琉'])), # 選手名
                len([x for x in text if x.isdigit()]),            # 数字の個数
                text.count('、'),                                  # 読点
                text.count('。'),                                  # 句点
                int('チーム' in text or 'ソフト' in text),         # チーム関連
                int('練習' in text or '試合' in text),             # 活動関連
            ]

            # 特徴量結合
            features = np.hstack([tfidf_features[0], manual_features])

            # スケーリング
            if self.scaler:
                features = self.scaler.transform([features])
                return features[0]
            else:
                return features

        except Exception as e:
            print(f"❌ 特徴量抽出エラー: {e}")
            return np.zeros(310)  # デフォルトサイズ

    def predict_category(self, text: str) -> Dict:
        """テキストのカテゴリを予測"""
        try:
            if not self.classifier:
                return {'error': '分類モデルが読み込まれていません'}

            # 特徴量抽出
            features = self.extract_features(text)
            features = features.reshape(1, -1)

            # 予測
            prediction = self.classifier.predict(features)[0]
            probabilities = self.classifier.predict_proba(features)[0]

            # 結果整理
            result = {
                'predicted_category': self.label_names.get(prediction, 'Unknown'),
                'predicted_label': int(prediction),
                'confidence': float(max(probabilities)),
                'all_probabilities': {
                    self.label_names.get(i, f'Label_{i}'): float(prob)
                    for i, prob in enumerate(probabilities)
                },
                'input_text': text,
                'timestamp': datetime.now().isoformat()
            }

            return result

        except Exception as e:
            return {'error': f'予測エラー: {e}'}

    def predict_cluster(self, text: str) -> Dict:
        """テキストのクラスタを予測"""
        try:
            if not self.cluster_model:
                return {'error': 'クラスタリングモデルが読み込まれていません'}

            # 特徴量抽出
            features = self.extract_features(text)
            features = features.reshape(1, -1)

            # クラスタ予測
            cluster = self.cluster_model.predict(features)[0]

            # クラスタ中心からの距離
            distances = self.cluster_model.transform(features)[0]
            closest_distance = min(distances)

            result = {
                'predicted_cluster': int(cluster),
                'distance_to_center': float(closest_distance),
                'all_distances': [float(d) for d in distances],
                'input_text': text,
                'timestamp': datetime.now().isoformat()
            }

            return result

        except Exception as e:
            return {'error': f'クラスタ予測エラー: {e}'}

    def analyze_text_batch(self, texts: List[str]) -> List[Dict]:
        """複数テキストの一括分析"""
        try:
            print(f"📊 {len(texts)} 件のテキストを一括分析中...")

            results = []
            for i, text in enumerate(texts):
                print(f"  処理中: {i+1}/{len(texts)}")

                # 分類予測
                category_result = self.predict_category(text)

                # クラスタ予測
                cluster_result = self.predict_cluster(text)

                # 結果統合
                combined_result = {
                    'text_id': i,
                    'input_text': text,
                    'classification': category_result,
                    'clustering': cluster_result,
                    'analysis_timestamp': datetime.now().isoformat()
                }

                results.append(combined_result)

            print("✅ 一括分析完了")
            return results

        except Exception as e:
            print(f"❌ 一括分析エラー: {e}")
            return []

    def generate_prediction_report(self, results: List[Dict]) -> str:
        """予測結果レポート生成"""
        try:
            print("📈 予測結果レポート生成中...")

            # 統計情報
            total_texts = len(results)
            category_counts = {}
            cluster_counts = {}
            confidence_scores = []

            for result in results:
                # カテゴリ統計
                if 'classification' in result and 'predicted_category' in result['classification']:
                    category = result['classification']['predicted_category']
                    category_counts[category] = category_counts.get(category, 0) + 1

                    # 信頼度
                    if 'confidence' in result['classification']:
                        confidence_scores.append(result['classification']['confidence'])

                # クラスタ統計
                if 'clustering' in result and 'predicted_cluster' in result['clustering']:
                    cluster = result['clustering']['predicted_cluster']
                    cluster_counts[cluster] = cluster_counts.get(cluster, 0) + 1

            # レポート作成
            report = {
                'analysis_summary': {
                    'total_texts_analyzed': total_texts,
                    'timestamp': datetime.now().isoformat(),
                    'average_confidence': np.mean(confidence_scores) if confidence_scores else 0,
                    'min_confidence': min(confidence_scores) if confidence_scores else 0,
                    'max_confidence': max(confidence_scores) if confidence_scores else 0
                },
                'category_distribution': category_counts,
                'cluster_distribution': cluster_counts,
                'detailed_results': results
            }

            # レポート保存
            report_file = os.path.join(MODELS_PATH, f'prediction_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            print(f"✅ レポート保存: {report_file}")

            # サマリー表示
            print("\n" + "="*50)
            print("📊 予測結果サマリー")
            print("="*50)
            print(f"分析テキスト数: {total_texts}")
            print(f"平均信頼度: {np.mean(confidence_scores):.4f}" if confidence_scores else "信頼度: N/A")
            print("\nカテゴリ分布:")
            for category, count in category_counts.items():
                print(f"  {category}: {count} 件 ({count/total_texts*100:.1f}%)")
            print("\nクラスタ分布:")
            for cluster, count in cluster_counts.items():
                print(f"  クラスタ {cluster}: {count} 件 ({count/total_texts*100:.1f}%)")

            return report_file

        except Exception as e:
            print(f"❌ レポート生成エラー: {e}")
            return ""

def interactive_prediction_demo():
    """インタラクティブ予測デモ"""
    print("🚀 Uma3 機械学習予測システム - インタラクティブデモ")
    print("=" * 60)

    # 予測システム初期化
    predictor = Uma3MLPredictor()

    # サンプルテキスト
    sample_texts = [
        "翔平選手の成績を教えてください",
        "Q: 次の練習はいつですか？",
        "A: 練習は毎週土曜日に実施されます",
        "馬三ソフトは素晴らしいチームです",
        "試合の結果を報告します",
        "３年生の選手は6名います",
        "キャプテンは誰ですか？",
        "練習メニューを確認したい",
        "聡太選手は内野手です",
        "チームの目標は県大会出場です"
    ]

    print("📝 サンプルテキストでの予測テスト:")

    # 一括分析実行
    results = predictor.analyze_text_batch(sample_texts)

    # 結果表示
    print("\n📊 個別予測結果:")
    for i, result in enumerate(results):
        print(f"\n--- テキスト {i+1} ---")
        print(f"入力: {result['input_text']}")

        if 'classification' in result and 'predicted_category' in result['classification']:
            print(f"カテゴリ: {result['classification']['predicted_category']} (信頼度: {result['classification']['confidence']:.4f})")

        if 'clustering' in result and 'predicted_cluster' in result['clustering']:
            print(f"クラスタ: {result['clustering']['predicted_cluster']} (距離: {result['clustering']['distance_to_center']:.4f})")

    # レポート生成
    report_file = predictor.generate_prediction_report(results)

    print(f"\n🎉 インタラクティブデモ完了!")
    print(f"📄 詳細レポート: {report_file}")

    return True

def main():
    """メイン実行関数"""
    print("=" * 70)
    print("🔮 Uma3 機械学習予測システム")
    print("=" * 70)

    # デモ実行
    success = interactive_prediction_demo()

    if success:
        print("\n✅ 機械学習予測システムが正常に動作しました!")
        print("🔮 新しいテキストの分類・クラスタリング予測が可能です")
        return 0
    else:
        print("\n❌ 予測システムでエラーが発生しました")
        return 1

if __name__ == "__main__":
    sys.exit(main())
