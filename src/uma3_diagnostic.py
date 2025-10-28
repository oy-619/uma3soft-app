"""
uma3.py用の軽量な動作確認とテスト
"""

import sys
import os

def test_imports():
    """必要なモジュールのインポートテスト"""
    print("🔍 モジュールインポートテスト")
    print("-" * 40)

    test_results = []

    # 基本モジュール
    try:
        import flask
        test_results.append(("✅ Flask", True))
    except ImportError as e:
        test_results.append((f"❌ Flask: {e}", False))

    # LangChain
    try:
        from langchain_openai import ChatOpenAI
        test_results.append(("✅ LangChain OpenAI", True))
    except ImportError as e:
        test_results.append((f"❌ LangChain OpenAI: {e}", False))

    # LINE Bot SDK
    try:
        from linebot.v3.messaging import MessagingApi
        test_results.append(("✅ LINE Bot SDK", True))
    except ImportError as e:
        test_results.append((f"❌ LINE Bot SDK: {e}", False))

    # 改善システム
    try:
        sys.path.insert(0, '../tests')
        from improved_response_system import ImprovedResponseGenerator
        test_results.append(("✅ Improved Response System", True))
    except ImportError as e:
        test_results.append((f"❌ Improved Response System: {e}", False))

    # 結果表示
    all_passed = True
    for result, passed in test_results:
        print(f"   {result}")
        if not passed:
            all_passed = False

    return all_passed

def create_minimal_line_bot():
    """最小限のLINE Bot作成"""
    print("\n🤖 最小限LINE Bot作成")
    print("-" * 40)

    minimal_bot_code = '''
"""
最小限のLINE Bot (エラー回避版)
"""

import os
from flask import Flask, request
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv('../.env')

app = Flask(__name__)

@app.route('/')
def health_check():
    return "LINE Bot is running! (Minimal Version)"

@app.route('/callback', methods=['POST'])
def callback():
    try:
        print("[WEBHOOK] Received LINE webhook")
        return 'OK', 200
    except Exception as e:
        print(f"[ERROR] Webhook error: {e}")
        return 'Error', 500

if __name__ == "__main__":
    print("🚀 Minimal LINE Bot starting...")
    print(f"Health check: http://localhost:5000/")
    print(f"Webhook: http://localhost:5000/callback")

    app.run(host='0.0.0.0', port=5000, debug=True)
'''

    # 最小限Botを保存
    minimal_path = 'minimal_uma3_bot.py'
    with open(minimal_path, 'w', encoding='utf-8') as f:
        f.write(minimal_bot_code)

    print(f"✅ 最小限LINE Bot作成: {minimal_path}")
    print("   依存関係エラーが解決するまでの暫定的なBot")

    return minimal_path

def diagnose_dependencies():
    """依存関係の診断"""
    print("\n🔧 依存関係診断")
    print("-" * 40)

    print("📦 インストール済みパッケージ:")
    os.system("pip list | findstr -i 'pydantic langchain line'")

    print("\n💡 推奨対応:")
    print("1. Pydanticバージョンの確認:")
    print("   pip show pydantic")
    print()
    print("2. LangChainバージョンの確認:")
    print("   pip show langchain langchain-openai")
    print()
    print("3. LINE Bot SDKバージョンの確認:")
    print("   pip show line-bot-sdk")
    print()
    print("4. 互換性問題の解決:")
    print("   pip install pydantic==1.10.12")
    print("   pip install langchain==0.1.0")

def main():
    """メイン処理"""
    print("🎯 uma3.py動作確認・診断ツール")
    print("=" * 60)

    # インポートテスト
    imports_ok = test_imports()

    if not imports_ok:
        print("\n❌ 依存関係に問題があります")

        # 最小限Botの作成
        minimal_bot_path = create_minimal_line_bot()

        # 診断情報
        diagnose_dependencies()

        print(f"\n🔄 暫定的な解決方法:")
        print(f"   python {minimal_bot_path}")
        print("   この最小限Botで基本動作を確認")

    else:
        print("\n✅ 全てのモジュールが正常にインポートできます")
        print("   uma3.pyの起動を再試行してください")

if __name__ == "__main__":
    main()
