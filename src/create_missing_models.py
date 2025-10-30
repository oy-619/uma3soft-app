#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
不足しているモデルファイルを生成するスクリプト
"""

import os
import pickle
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
import numpy as np

# パス設定
PROJECT_ROOT = Path(r"C:\work\ws_python\GenerationAiCamp")
ML_MODELS_PATH = PROJECT_ROOT / 'Lesson25' / 'uma3soft-app' / 'ml_models'

def create_missing_models():
    """不足しているモデルファイルを作成"""
    print("🔧 不足しているモデルファイルを生成中...")

    # ベクトライザー作成
    print("  📝 ベクトライザー作成中...")
    vectorizer = TfidfVectorizer(
        max_features=310,
        ngram_range=(1, 2),
        stop_words='english'
    )

    # サンプルテキストでfit
    sample_texts = [
        "翔平選手の成績について教えてください",
        "チームの戦略を知りたいです",
        "練習はいつですか",
        "ありがとうございます",
        "その他の質問です",
        "選手情報を確認したい",
        "質問があります",
        "回答をお願いします",
        "チーム情報について",
        "サンプルテキスト"
    ]

    vectorizer.fit(sample_texts)

    # 保存
    vectorizer_path = ML_MODELS_PATH / 'vectorizer.pkl'
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    print(f"  ✅ ベクトライザー保存: {vectorizer_path}")

    # スケーラー作成
    print("  📊 スケーラー作成中...")
    scaler = StandardScaler()

    # サンプルデータでfit
    sample_features = vectorizer.transform(sample_texts).toarray()
    scaler.fit(sample_features)

    # 保存
    scaler_path = ML_MODELS_PATH / 'scaler.pkl'
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    print(f"  ✅ スケーラー保存: {scaler_path}")

    print("🎉 不足しているモデルファイル生成完了!")

if __name__ == "__main__":
    create_missing_models()
