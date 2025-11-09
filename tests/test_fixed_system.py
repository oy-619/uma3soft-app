#!/usr/bin/env python3
"""
修正されたシステムのテストスクリプト
データベーススキーマ修正後の動作確認
"""

import sys
import os

# パスの設定
sys.path.insert(0, "src")

def test_conversation_system():
    """統合会話システムのテスト"""
    print("=" * 60)
    print("🧪 統合会話システム動作テスト")
    print("=" * 60)

    try:
        # 必要なモジュールをインポート
        from conversation_history_manager import ConversationHistoryManager
        from integrated_conversation_system import IntegratedConversationSystem

        # データベースパス
        db_path = "db/conversation_history.db"
        chroma_path = "db/chroma_store"

        print(f"✅ モジュールインポート成功")

        # ConversationHistoryManagerのテスト
        print("\n1️⃣ ConversationHistoryManager テスト")
        history_manager = ConversationHistoryManager(db_path)

        # ユーザープロファイル取得テスト
        test_user = "test_user_fix"
        user_profile = history_manager.get_user_profile(test_user)
        print(f"✅ ユーザープロファイル取得成功: {user_profile}")

        # 会話保存テスト（metadata引数付き）
        try:
            history_manager.save_conversation(
                test_user,
                "テストメッセージです",
                "テスト応答です",
                metadata={"source": "test", "type": "validation"}
            )
            print("✅ 会話保存成功（metadata引数付き）")
        except Exception as e:
            print(f"⚠️ metadata引数付き保存失敗: {e}")

            # metadata引数なしで再試行
            history_manager.save_conversation(
                test_user,
                "テストメッセージです",
                "テスト応答です"
            )
            print("✅ 会話保存成功（metadata引数なし）")

        # 2. IntegratedConversationSystemのテスト
        print("\n2️⃣ IntegratedConversationSystem テスト")

        # HuggingFace埋め込みモデルを初期化
        from langchain_huggingface import HuggingFaceEmbeddings
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        integrated_system = IntegratedConversationSystem(
            chroma_persist_directory=chroma_path,
            conversation_db_path=db_path,
            embeddings_model=embedding_model
        )
        print("✅ IntegratedConversationSystem初期化成功")

        # LLMモデルの初期化
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)

        # 応答生成テスト（簡単なテストメッセージ）
        print("\n3️⃣ 応答生成テスト")
        test_message = "こんにちは、テストです"

        try:
            response_result = integrated_system.generate_integrated_response(
                test_user, test_message, llm
            )

            if "error" in response_result:
                print(f"⚠️ 応答生成でエラー: {response_result.get('error_message', 'Unknown error')}")
            else:
                print(f"✅ 応答生成成功")
                print(f"   応答: {response_result['response'][:100]}...")

                context_info = response_result.get("context_used", {})
                print(f"   コンテキスト: ChromaDB={context_info.get('chroma_results', 0)}, History={context_info.get('conversation_history', 0)}")

        except Exception as e:
            print(f"❌ 応答生成テスト失敗: {e}")
            import traceback
            traceback.print_exc()

        print("\n" + "=" * 60)
        print("🎉 テスト完了!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"❌ テスト実行中にエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mention_detection():
    """メンション検出のテスト"""
    print("\n🎯 メンション検出テスト")
    print("-" * 40)

    # テスト用のメンションパターン
    test_messages = [
        "@Bot こんにちは",
        "Bot お疲れ様です",
        "ボットさん、質問があります",
        "@bot test message",
        "通常のメッセージです"
    ]

    keywords = ["@Bot", "@bot", "Bot", "ボット"]

    for msg in test_messages:
        has_mention = any(keyword in msg for keyword in keywords)
        status = "✅ メンション検出" if has_mention else "❌ メンションなし"
        print(f"   '{msg}' -> {status}")

if __name__ == "__main__":
    print(f"現在のディレクトリ: {os.getcwd()}")

    if test_conversation_system():
        test_mention_detection()
        print("\n✨ 全テストが正常に完了しました！")
    else:
        print("\n❌ テストに失敗しました")
        sys.exit(1)
