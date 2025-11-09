# Uma3 Software 機械学習統合システム運用ガイド

## 📋 目次
1. [システム概要](#システム概要)
2. [運用前準備](#運用前準備)
3. [日常運用手順](#日常運用手順)
4. [モニタリング](#モニタリング)
5. [メンテナンス](#メンテナンス)
6. [トラブルシューティング](#トラブルシューティング)

---

## 🔧 システム概要

### 構成コンポーネント
```
Uma3 ML統合システム
├── リアルタイム分析エンジン (realtime_ml_analyzer.py)
├── 機械学習訓練システム (ml_training_system_offline.py)
├── 予測システム (ml_prediction_system.py)
├── 統合テストスイート (ml_integration_test.py)
└── LINE Bot統合 (uma3.py)
```

### 主要機能
- **🎯 テキスト分類**: 95.6%精度でメッセージを自動分類
- **🔍 類似検索**: 既存データから関連コンテンツを発見
- **👥 行動予測**: ユーザーパターンに基づく推薦
- **📊 リアルタイム分析**: 66.5件/秒の高速処理

---

## 🚀 運用前準備

### 1. 環境確認チェックリスト
```powershell
# 仮想環境の確認
C:/work/ws_python/GenerationAiCamp/venv/Scripts/python.exe --version

# 必要なディレクトリ構造の確認
ls C:\work\ws_python\GenerationAiCamp\Lesson25\uma3soft-app\ml_models\
ls C:\work\ws_python\GenerationAiCamp\Lesson25\uma3soft-app\db\
```

### 2. 学習済みモデルの確認
必要なファイル:
- `classification_model.pkl` (153KB)
- `clustering_model.pkl` (13KB)
- `vectorizer.pkl`
- `scaler.pkl`

### 3. 統合テスト実行
```powershell
cd C:\work\ws_python\GenerationAiCamp
C:/work/ws_python/GenerationAiCamp/venv/Scripts/python.exe "Lesson25\uma3soft-app\src\ml_integration_test.py"
```

**期待結果**: 全テスト100%成功

---

## 📱 日常運用手順

### A. LINE Bot with ML統合システム起動

#### 1. ngrokトンネル開始
```powershell
# Task実行（推奨）
# VS Codeで Ctrl+Shift+P → "Tasks: Run Task" → "Clean Start ngrok (Lesson25)"

# または手動実行
cd C:\work\ws_python\GenerationAiCamp\Lesson25\uma3soft-app
ngrok http 5000 --log=stdout --region=jp
```

#### 2. LINE Bot + ML統合システム起動
```powershell
cd C:\work\ws_python\GenerationAiCamp
C:/work/ws_python/GenerationAiCamp/venv/Scripts/python.exe "Lesson25\uma3soft-app\src\uma3.py"
```

### B. スタンドアロンML分析システム

#### リアルタイム分析実行
```powershell
C:/work/ws_python/GenerationAiCamp/venv/Scripts/python.exe "Lesson25\uma3soft-app\src\realtime_ml_analyzer.py"
```

#### 個別予測実行
```python
from realtime_ml_analyzer import Uma3RealTimeMLAnalyzer

# 分析システム初期化
analyzer = Uma3RealTimeMLAnalyzer()

# テキスト分類
result = analyzer.classify_text_realtime("翔平選手の成績について教えて")
print(f"分類: {result['predicted_category']}")
print(f"信頼度: {result['confidence']:.3f}")

# 類似コンテンツ検索
similar = analyzer.find_similar_content("チーム戦略", top_k=5)
print(f"発見数: {len(similar)}件")

# ユーザー行動予測
behavior = analyzer.predict_user_behavior("user123", "練習について質問")
print(f"予測: {behavior['prediction']}")
print(f"推薦: {behavior['recommendations']}")
```

---

## 📊 モニタリング

### 1. システム健全性チェック

#### 日次チェック項目
```powershell
# 統合テスト実行
C:/work/ws_python/GenerationAiCamp/venv/Scripts/python.exe "Lesson25\uma3soft-app\src\ml_integration_test.py"

# 期待値:
# 🎯 成功テスト: 5/5 (100.0%)
# ⚡ 分類精度: 100.0%
# 📊 処理スループット: >60件/秒
```

#### パフォーマンス指標
- **分類精度**: 92%以上の信頼度維持
- **処理速度**: 60件/秒以上
- **メモリ使用量**: <500MB
- **応答時間**: <100ms/件

### 2. ログモニタリング
```powershell
# ログファイル確認
cat C:\work\ws_python\GenerationAiCamp\Lesson25\uma3soft-app\logs\ml_integration_test.log

# エラーパターンの監視
grep "ERROR\|CRITICAL" C:\work\ws_python\GenerationAiCamp\Lesson25\uma3soft-app\logs\*.log
```

### 3. データベース状態確認
```python
# ChromaDB状態確認スクリプト
import chromadb
client = chromadb.PersistentClient(path="C:/work/ws_python/GenerationAiCamp/Lesson25/uma3soft-app/db/chroma_store")
collection = client.get_collection("uma3_knowledge")
print(f"総ドキュメント数: {collection.count()}")
```

---

## 🔄 メンテナンス

### 週次メンテナンス

#### 1. モデル再訓練（推奨：毎週日曜日）
```powershell
# 新しいデータでモデル再訓練
C:/work/ws_python/GenerationAiCamp/venv/Scripts/python.exe "Lesson25\uma3soft-app\src\ml_training_system_offline.py"

# 期待結果: >95%精度維持
```

#### 2. データベース最適化
```powershell
# ChromaDB最適化
cd C:\work\ws_python\GenerationAiCamp\Lesson25\uma3soft-app\src
C:/work/ws_python/GenerationAiCamp/venv/Scripts/python.exe reset_chromadb.py --optimize
```

#### 3. ログローテーション
```powershell
# 古いログファイルのアーカイブ
cd C:\work\ws_python\GenerationAiCamp\Lesson25\uma3soft-app\logs
mkdir archive\$(Get-Date -Format "yyyy-MM")
move *.log archive\$(Get-Date -Format "yyyy-MM")\
```

### 月次メンテナンス

#### 1. システム全体検証
```powershell
# 全コンポーネント統合テスト
C:/work/ws_python/GenerationAiCamp/venv/Scripts/python.exe "Lesson25\uma3soft-app\src\ml_integration_test.py"

# パフォーマンステスト実行
# 期待値: 全テスト100%成功
```

#### 2. モデルベンチマーク更新
```python
# 新しいテストデータでの精度検証
# baseline: 95.6%精度を維持または改善
```

---

## 🚨 トラブルシューティング

### よくある問題と解決方法

#### 1. **ベクトライザーエラー**
```
❌ 特徴量抽出エラー: The TF-IDF vectorizer is not fitted
```

**解決方法:**
```powershell
# モデル再訓練
C:/work/ws_python/GenerationAiCamp/venv/Scripts/python.exe "Lesson25\uma3soft-app\src\ml_training_system_offline.py"
```

#### 2. **ChromaDB接続エラー**
```
❌ ChromaDB接続エラー
```

**解決方法:**
```powershell
# データベースパス確認
ls C:\work\ws_python\GenerationAiCamp\Lesson25\uma3soft-app\db\chroma_store\

# 権限修正
icacls "C:\work\ws_python\GenerationAiCamp\Lesson25\uma3soft-app\db" /grant Everyone:F /T
```

#### 3. **メモリ不足エラー**
```
❌ MemoryError: Unable to allocate array
```

**解決方法:**
```python
# バッチサイズ削減
analyzer = Uma3RealTimeMLAnalyzer()
# デフォルトのバッチサイズを50から10に変更
```

#### 4. **ngrok接続切断**
```powershell
# ngrok再起動
taskkill /F /IM ngrok.exe
Start-Sleep -Seconds 2
cd C:\work\ws_python\GenerationAiCamp\Lesson25\uma3soft-app
ngrok http 5000 --log=stdout --region=jp
```

#### 5. **LINE Bot応答遅延**
**診断:**
```powershell
# 統合テストでパフォーマンス確認
C:/work/ws_python\GenerationAiCamp/venv/Scripts/python.exe "Lesson25\uma3soft-app\src\ml_integration_test.py"
```

**解決方法:**
```python
# スループットが60件/秒を下回る場合：
# 1. モデルキャッシュの確認
# 2. データベースインデックス最適化
# 3. バックグラウンド処理への移行
```

---

## 📞 緊急時対応

### システム停止が必要な場合
```powershell
# 全サービス停止
taskkill /F /IM python.exe
taskkill /F /IM ngrok.exe

# 最小限システム再起動
cd C:\work\ws_python\GenerationAiCamp
C:/work/ws_python/GenerationAiCamp/venv/Scripts/python.exe "Lesson25\uma3soft-app\src\ml_integration_test.py"
# 100%成功確認後、本番再開
```

### バックアップからの復旧
```powershell
# モデルファイルの復旧
copy "backup\ml_models\*" "C:\work\ws_python\GenerationAiCamp\Lesson25\uma3soft-app\ml_models\"

# 統合テストで動作確認
C:/work/ws_python/GenerationAiCamp/venv/Scripts/python.exe "Lesson25\uma3soft-app\src\ml_integration_test.py"
```

---

## 🎯 運用成功の指標

### KPI目標値
- **システム稼働率**: >99.5%
- **分類精度**: >92%信頼度
- **応答時間**: <100ms
- **スループット**: >60件/秒
- **ユーザー満足度**: ML推薦の採用率>70%

### 月次レポート項目
1. システム稼働実績
2. ML精度トレンド
3. パフォーマンス指標
4. エラー発生状況
5. ユーザー利用パターン

---

## 📈 継続改善

### データ収集強化
```python
# 新しい学習データの追加
# 1. ユーザーフィードバックの収集
# 2. 分類精度の向上施策
# 3. 新しいカテゴリの追加
```

### モデル精度向上
```python
# A/Bテスト実施
# 1. 異なるアルゴリズムの比較
# 2. ハイパーパラメータ最適化
# 3. アンサンブル手法の導入
```

---

**🚀 Uma3 Software機械学習統合システムの運用により、95.6%精度の自動分類とリアルタイム分析が実現されます！**
