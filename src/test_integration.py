#!/usr/bin/env python3
"""
LangChain + LlamaIndex 統合システム検証スクリプト
統合されたシステムの機能と性能を包括的にテスト
"""

import os
import sys
import time
from datetime import datetime

def test_integrated_system():
    """統合システムの包括的テスト"""
    print("=" * 60)
    print("🚀 LangChain + LlamaIndex 統合システム検証")
    print("=" * 60)

    try:
        # システムのインポートテスト
        print("\n📦 システムコンポーネントのインポートテスト...")

        # 1. 基本インポート
        from uma3_llama_index_engine import Uma3LlamaIndexEngine, test_llama_index_integration
        from uma3_hybrid_rag_engine import Uma3HybridRAGEngine, test_hybrid_rag_engine
        from uma3_custom_tools import create_enhanced_custom_tools
        print("   ✅ 全てのモジュールが正常にインポートされました")

        # 2. ハイブリッドRAGエンジンのテスト
        print("\n🔄 ハイブリッドRAGエンジンテスト...")

        engine = Uma3HybridRAGEngine(
            chroma_persist_directory="test_integration_chroma",
            enable_langchain=True,
            enable_llama_index=True
        )

        # システム統計情報の取得
        stats = engine.get_hybrid_stats()
        print(f"   📊 エンジン統計: {stats}")

        # 3. テストデータの追加
        print("\n📝 テストデータの追加...")

        test_documents = [
            "これはLangChainとLlamaIndexの統合テストです。",
            {"text": "ハイブリッドRAGシステムが正常に動作しています。", "metadata": {"type": "integration_test"}},
            "複数のRAGエンジンを併用することで検索精度が大幅に向上しました。",
            "LangChainのAgentシステムとLlamaIndexのQueryEngineが連携しています。",
            "カスタムツールを通じて高度な質問応答が可能になりました。"
        ]

        add_results = engine.add_documents_to_both(test_documents)
        print(f"   ✅ ドキュメント追加結果: {add_results}")

        # 4. ハイブリッド検索のテスト
        print("\n🔍 ハイブリッド検索テスト...")

        search_queries = [
            "統合テスト",
            "RAGシステム",
            "LangChain LlamaIndex"
        ]

        for query in search_queries:
            print(f"\n   検索クエリ: '{query}'")
            results = engine.hybrid_search(query, k=3)

            print(f"   結果数: {len(results)}")
            for i, doc in enumerate(results, 1):
                score = doc.metadata.get('hybrid_score', 0)
                engine_name = doc.metadata.get('engine', 'unknown')
                content = doc.page_content[:60].replace('\n', ' ')
                print(f"     {i}. [{engine_name}] Score: {score:.3f} - {content}...")

        # 5. LlamaIndexクエリエンジンのテスト
        print("\n🧠 LlamaIndexクエリエンジンテスト...")

        if engine.llama_index_engine:
            query_questions = [
                "統合システムの特徴は何ですか？",
                "ハイブリッドRAGシステムの利点について教えて",
                "LangChainとLlamaIndexの違いは？"
            ]

            for question in query_questions:
                print(f"\n   質問: '{question}'")
                response = engine.llama_index_query(question, top_k=3)
                if response:
                    print(f"   回答: {response[:120]}...")
                else:
                    print("   回答: 取得できませんでした")

        # 6. カスタムツールのテスト
        print("\n🛠️ 拡張カスタムツールテスト...")

        # LangChain互換のRAGエンジンを作成（モック）
        from uma3_chroma_improver import Uma3ChromaDBImprover
        from langchain_chroma import Chroma
        from langchain_huggingface import HuggingFaceEmbeddings

        # 簡易RAGエンジン
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        vector_db = Chroma(
            persist_directory="test_integration_chroma",
            embedding_function=embedding_model,
        )
        mock_rag_engine = Uma3ChromaDBImprover(vector_db)

        # 拡張カスタムツールを作成
        custom_tools = create_enhanced_custom_tools(
            rag_engine=mock_rag_engine,
            hybrid_rag_engine=engine
        )

        print(f"   ✅ 作成されたカスタムツール数: {len(custom_tools)}")
        for tool in custom_tools:
            print(f"     - {tool.name}: {tool.description.strip().split('.')[0]}...")

        # 7. パフォーマンステスト
        print("\n⚡ パフォーマンステスト...")

        # 検索速度テスト
        start_time = time.time()
        for _ in range(5):
            results = engine.hybrid_search("テスト", k=5)
        end_time = time.time()

        avg_time = (end_time - start_time) / 5
        print(f"   ハイブリッド検索 平均実行時間: {avg_time:.3f}秒")

        # メモリ使用量の概算（簡易版）
        try:
            import psutil
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            print(f"   メモリ使用量: {memory_usage:.1f} MB")
        except ImportError:
            print("   メモリ使用量: psutil未インストール（測定スキップ）")
            memory_usage = 0

        # 8. システム完全性チェック
        print("\n🔒 システム完全性チェック...")

        system_status = {
            "langchain_engine": engine.langchain_engine is not None,
            "llama_index_engine": engine.llama_index_engine is not None and engine.llama_index_engine.is_initialized,
            "hybrid_search": len(engine.hybrid_search("test", k=1)) > 0,
            "custom_tools": len(custom_tools) >= 4
        }

        all_ok = all(system_status.values())

        print(f"   📊 システムステータス:")
        for component, status in system_status.items():
            status_icon = "✅" if status else "❌"
            print(f"     {status_icon} {component}: {status}")

        # 最終結果
        print("\n" + "=" * 60)
        if all_ok:
            print("🎉 LangChain + LlamaIndex 統合システム検証完了!")
            print("   全ての機能が正常に動作しています。")

            # システム概要
            print(f"\n📋 システム概要:")
            print(f"   - RAGエンジン: LangChain + LlamaIndex ハイブリッド")
            print(f"   - カスタムツール: {len(custom_tools)}個")
            print(f"   - 検索エンジン: 両方のエンジンが稼働中")
            print(f"   - 平均検索時間: {avg_time:.3f}秒")
            if memory_usage > 0:
                print(f"   - メモリ使用量: {memory_usage:.1f} MB")
            else:
                print(f"   - メモリ使用量: 測定スキップ")

            return True
        else:
            print("⚠️ 一部のコンポーネントに問題があります。")
            return False

    except Exception as e:
        print(f"\n❌ 統合システムテストでエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_integrated_system()
    sys.exit(0 if success else 1)
