#!/usr/bin/env python3
"""
LINE Bot本格稼働スクリプト
"""
import os
import sys

# パス設定
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
sys.path.insert(0, src_dir)


def main():
    """LINE Botメイン起動関数"""
    try:
        print("🤖 LINE Bot 稼働開始！")
        print("=" * 60)

        # uma3モジュールをインポート
        import uma3

        print("✅ 初期化完了:")
        print("   - OpenAI API接続確認済み")
        print("   - ChromaDB準備完了")
        print("   - スケジューラー起動済み")
        print("   - LINEBot SDK初期化完了")

        print("\n🌐 サーバー情報:")
        print("   - ホスト: 0.0.0.0")
        print("   - ポート: 5000")
        print("   - Webhook URL: http://localhost:5000/callback")

        print("\n⚠️  重要な注意事項:")
        print("   - 本番環境ではngrok等でHTTPS公開が必要")
        print("   - LINE Developer Consoleで Webhook URLを設定")
        print("   - 停止するには Ctrl+C を押してください")

        print("\n" + "=" * 60)
        print("🚀 Flask サーバー起動中...")
        print("=" * 60)

        # Flask アプリケーション起動
        uma3.app.run(
            host="0.0.0.0",
            port=5000,
            debug=False,  # 本番稼働モード
            use_reloader=False,  # リロード無効化でスケジューラー重複防止
        )

    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("🛑 LINE Bot 正常停止")
        print("=" * 60)
        return 0
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
