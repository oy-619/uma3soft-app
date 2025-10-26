#!/usr/bin/env python3
"""
環境設定テスト - メインBot統合テスト用
"""
import os
import sys


def test_environment():
    """環境設定の総合テスト"""
    print("==================================================")
    print("🧪 メインBot統合テスト - 環境設定確認")
    print("==================================================")

    # 1. .envファイル確認
    if os.path.exists(".env"):
        print("✅ .envファイル存在確認")
    else:
        print("❌ .envファイルが見つかりません")
        return False

    # 2. 環境変数確認
    try:
        from dotenv import load_dotenv

        load_dotenv()

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key.startswith("sk-"):
            print("✅ OPENAI_API_KEY環境変数設定確認")
            print(f"   Key prefix: {api_key[:10]}...")
        else:
            print("❌ OPENAI_API_KEY環境変数が正しく設定されていません")
            return False
    except ImportError:
        print("❌ python-dotenvパッケージが見つかりません")
        return False

    # 3. 主要パッケージ確認
    required_packages = [
        "langchain_openai",
        "langchain_chroma",
        "langchain_huggingface",
        "flask",
        "linebot",
        "streamlit",
        "apscheduler",
    ]

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} パッケージ確認")
        except ImportError:
            print(f"❌ {package} パッケージが見つかりません")
            return False

    # 4. OpenAI接続テスト
    try:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(temperature=0.0)
        print("✅ OpenAI接続設定確認")
    except Exception as e:
        print(f"❌ OpenAI接続エラー: {e}")
        return False

    print("\n==================================================")
    print("🎉 メインBot統合テスト環境準備完了！")
    print("   全システム連携テストを開始できます")
    print("==================================================")
    return True


if __name__ == "__main__":
    success = test_environment()
    sys.exit(0 if success else 1)
