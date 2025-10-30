## 📝 LINE Bot ノート投稿検出機能

### 概要
LINE Botでノート投稿時の通知メッセージやURLを自動検出し、データベースに保存する機能です。

### 🎯 検出可能な内容

#### 1. ノート投稿通知メッセージ
```
田中さんがノートを投稿しました
https://line.me/R/note/C1234567890/NOTE123456
```

#### 2. 直接ノートURL投稿
```
https://line.me/R/note/C1234567890/NOTE123456
https://line.me/R/home/note/C1234567890/NOTE789012
```

#### 3. 調整さんURL（ノート内）
```
https://chouseisan.com/s?h=abc123xyz
```

### 🤖 Botコマンド

#### ノート一覧取得
```
ノート一覧
ノートリスト
ノート確認
```

#### 調整さんURL取得
```
調整さんURL教えて
調整さんリンク
調整くんURL
```

### 💾 保存されるデータ

```json
{
  "note_id": "NOTE123456",
  "note_url": "https://line.me/R/note/C1234567890/NOTE123456",
  "group_id": "C1234567890",
  "user_id": "U0987654321",
  "user_name": "田中さん",
  "title": "練習試合の件",
  "detected_at": "2025-10-29T14:53:00",
  "message_text": "田中さんがノートを投稿しました\nhttps://line.me/R/note/..."
}
```

### 🔧 実装ファイル

- **`note_detector.py`**: ノート検出・保存システム
- **`uma3.py`**: LINE Bot統合（メッセージハンドラー）
- **`detected_notes.json`**: ノート情報データベース

### 📱 使用例

1. **ノート投稿時**
   - ユーザーがノートを投稿
   - LINEが自動通知メッセージを送信
   - Bot が通知を検出してデータベースに保存

2. **ノート一覧確認**
   ```
   ユーザー: ノート一覧
   Bot: 📝 検出済みノート情報 (総数: 5件)
        1. 練習試合の件
           👤 田中さん | 📅 2025/10/29 14:53
           🔗 https://line.me/R/note/...
   ```

3. **調整さんURL確認**
   ```
   ユーザー: 調整さんURL教えて
   Bot: 📊 調整さんURL一覧
        1. 次回練習について: https://chouseisan.com/s?h=...
   ```

### ⚙️ 設定・カスタマイズ

#### 検出パターンの追加
`note_detector.py` の `note_patterns` を編集：

```python
self.note_patterns = [
    r'(.+)がノートを投稿しました',
    r'(.+) posted a note',
    # カスタムパターンを追加
]
```

#### データベースファイルの変更
```python
detector = NoteDetector(storage_file="custom_notes.json")
```

### 🛠️ トラブルシューティング

#### ノートが検出されない場合
1. メッセージパターンの確認
2. URLが正しい形式か確認
3. ログの確認（`[NOTE_DETECTOR]`）

#### データが保存されない場合
1. ファイル権限の確認
2. JSON形式エラーの確認
3. `detected_notes.json` の内容確認

### 🔄 アップデート履歴

- **v1.0** (2025/10/29): 初回リリース
  - ノート投稿通知検出
  - 調整さんURL抽出
  - LINE Botコマンド統合
