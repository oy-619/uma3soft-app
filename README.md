# Uma3 Smart Assistant

LINE会話履歴を利用したAIアシスタントアプリケーション

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env.example`をコピーして`.env`ファイルを作成し、必要な環境変数を設定してください。

```bash
cp .env.example .env
```

`.env`ファイルを編集して、OpenAI API Keyを設定：

```env
OPENAI_API_KEY=your_actual_openai_api_key_here
```

### 3. 実行方法

```bash
# メインアプリケーション
python src/uma3.py

# テストの実行
python tests/test_future_integration.py
```

## セキュリティ注意事項

- API Keyやシークレットは決してコードに直接埋め込まないでください
- `.env`ファイルはGitリポジトリにコミットしないでください
- 環境変数を使用してセンシティブな情報を管理してください

## ファイル構成

- `src/` - メインアプリケーションコード
- `tests/` - テストファイル
- `.env.example` - 環境変数設定の例
- `requirements.txt` - 必要なパッケージ一覧
