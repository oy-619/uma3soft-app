"""
Uma3 Hybrid RAG Engine
LangChain + LlamaIndex のハイブリッドRAGシステム
"""

import os
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

# LangChain imports
try:
    from langchain_chroma import Chroma
    from langchain_core.documents import Document as LangChainDocument
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_openai import ChatOpenAI
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"[HYBRID] ❌ LangChain import error: {e}")
    LANGCHAIN_AVAILABLE = False

# LlamaIndex imports
try:
    from llama_index.core.schema import NodeWithScore

    # レスポンス型の互換性対応
    try:
        from llama_index.core.response.schema import Response
    except ImportError:
        try:
            from llama_index.core.base.response.schema import Response
        except ImportError:
            # フォールバック: 自前のResponse型定義
            class Response:
                def __init__(self, response: str, source_nodes=None, metadata=None):
                    self.response = response
                    self.source_nodes = source_nodes or []
                    self.metadata = metadata or {}

    LLAMA_INDEX_AVAILABLE = True
except ImportError as e:
    print(f"[HYBRID] ❌ LlamaIndex import error: {e}")
    LLAMA_INDEX_AVAILABLE = False

# デフォルトのChromaDB保存先（絶対パス方式）
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_CHROMA_PERSIST_DIRECTORY = os.path.join(PROJECT_ROOT, "db", "chroma_store")

# フォールバック クラス定義
class Response:
    def __init__(self, response: str, source_nodes=None, metadata=None):
        self.response = response
        self.source_nodes = source_nodes or []
        self.metadata = metadata or {}

class NodeWithScore:
    def __init__(self, node, score: float = 0.0):
        self.node = node
        self.score = score

# 内部モジュール
from uma3_llama_index_engine import Uma3LlamaIndexEngine, LlamaIndexLangChainBridge
from uma3_chroma_improver import Uma3ChromaDBImprover


class Uma3HybridRAGEngine:
    """
    LangChain + LlamaIndex ハイブリッドRAGエンジン

    機能:
    - 既存のLangChain ChromaDBシステムとの完全互換性
    - LlamaIndexの高度なクエリエンジンとの統合
    - 両方のエンジンを併用したハイブリッド検索
    - 結果の統合とランキング
    - パフォーマンス最適化
    """

    def __init__(
        self,
        chroma_persist_directory: str = None,
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        llm_model: str = "gpt-3.5-turbo",
        # llm_model: str = "gpt-4-turbo",
        enable_langchain: bool = True,
        enable_llama_index: bool = True
    ):
        """
        ハイブリッドRAGエンジンの初期化

        Args:
            chroma_persist_directory: ChromaDBディレクトリ (Noneの場合はデフォルト使用)
            embedding_model_name: 埋め込みモデル名
            llm_model: LLMモデル名
            enable_langchain: LangChainエンジンを有効にするか
            enable_llama_index: LlamaIndexエンジンを有効にするか
        """
        # 絶対パス方式でデフォルトディレクトリを設定
        if chroma_persist_directory is None:
            chroma_persist_directory = DEFAULT_CHROMA_PERSIST_DIRECTORY

        print(f"[HYBRID] 🚀 Initializing Uma3HybridRAGEngine")
        print(f"[HYBRID] LangChain enabled: {enable_langchain}")
        print(f"[HYBRID] LlamaIndex enabled: {enable_llama_index}")

        self.chroma_persist_directory = chroma_persist_directory
        self.embedding_model_name = embedding_model_name
        self.llm_model = llm_model
        self.enable_langchain = enable_langchain and LANGCHAIN_AVAILABLE
        self.enable_llama_index = enable_llama_index and LLAMA_INDEX_AVAILABLE

        # エンジン初期化
        self.langchain_engine: Optional[Uma3ChromaDBImprover] = None
        self.llama_index_engine: Optional[Uma3LlamaIndexEngine] = None
        self.bridge = LlamaIndexLangChainBridge()

        # スレッドプール（並列検索用）
        self.thread_pool = ThreadPoolExecutor(max_workers=4)

        # 初期化実行
        self._initialize_engines()

        print(f"[HYBRID] ✅ Hybrid RAG engine initialized")
        print(f"[HYBRID] Active engines: LangChain={self.langchain_engine is not None}, LlamaIndex={self.llama_index_engine is not None}")

    def _initialize_engines(self):
        """各エンジンの初期化"""

        # 1. LangChain エンジン初期化
        if self.enable_langchain:
            try:
                # 埋め込みモデル
                embedding_model = HuggingFaceEmbeddings(
                    model_name=self.embedding_model_name
                )

                # ChromaDBの初期化
                vector_db = Chroma(
                    persist_directory=self.chroma_persist_directory,
                    embedding_function=embedding_model,
                )

                # ChromaDB改良器の初期化
                self.langchain_engine = Uma3ChromaDBImprover(vector_db)
                print("[HYBRID] ✅ LangChain engine initialized")

            except Exception as e:
                print(f"[HYBRID] ❌ LangChain engine initialization failed: {e}")
                self.langchain_engine = None

        # 2. LlamaIndex エンジン初期化
        if self.enable_llama_index:
            try:
                self.llama_index_engine = Uma3LlamaIndexEngine(
                    chroma_persist_directory=self.chroma_persist_directory,
                    embedding_model_name=self.embedding_model_name,
                    llm_model=self.llm_model,
                    collection_name="uma3_documents_llama"
                )

                if self.llama_index_engine.is_initialized:
                    print("[HYBRID] ✅ LlamaIndex engine initialized")
                else:
                    print("[HYBRID] ⚠️ LlamaIndex engine failed to initialize")
                    self.llama_index_engine = None

            except Exception as e:
                print(f"[HYBRID] ❌ LlamaIndex engine initialization failed: {e}")
                self.llama_index_engine = None

    def hybrid_search(
        self,
        query: str,
        k: int = 10,
        langchain_weight: float = 0.6,
        llama_index_weight: float = 0.4,
        use_parallel: bool = True
    ) -> List[LangChainDocument]:
        """
        ハイブリッド検索の実行

        Args:
            query: 検索クエリ
            k: 取得する結果数
            langchain_weight: LangChainエンジンの重み
            llama_index_weight: LlamaIndexエンジンの重み
            use_parallel: 並列検索を使用するか

        Returns:
            統合された検索結果
        """
        print(f"[HYBRID] 🔍 Executing hybrid search: '{query[:50]}...'")

        # 重みの正規化
        total_weight = langchain_weight + llama_index_weight
        if total_weight > 0:
            langchain_weight /= total_weight
            llama_index_weight /= total_weight

        results = []

        if use_parallel and self.langchain_engine and self.llama_index_engine:
            # 並列検索
            results = self._parallel_search(query, k, langchain_weight, llama_index_weight)
        else:
            # 順次検索
            results = self._sequential_search(query, k, langchain_weight, llama_index_weight)

        print(f"[HYBRID] ✅ Hybrid search completed: {len(results)} results")
        return results

    def _parallel_search(
        self,
        query: str,
        k: int,
        langchain_weight: float,
        llama_index_weight: float
    ) -> List[LangChainDocument]:
        """並列検索の実行"""

        futures = []

        # LangChain検索をサブミット
        if self.langchain_engine:
            future_langchain = self.thread_pool.submit(
                self._search_langchain, query, k
            )
            futures.append(('langchain', future_langchain, langchain_weight))

        # LlamaIndex検索をサブミット
        if self.llama_index_engine:
            future_llama = self.thread_pool.submit(
                self._search_llama_index, query, k
            )
            futures.append(('llama_index', future_llama, llama_index_weight))

        # 結果の収集
        engine_results = {}
        for engine_name, future, weight in futures:
            try:
                result = future.result(timeout=30)  # 30秒タイムアウト
                engine_results[engine_name] = (result, weight)
                print(f"[HYBRID] ✅ {engine_name} search completed: {len(result)} results")
            except Exception as e:
                print(f"[HYBRID] ❌ {engine_name} search failed: {e}")
                engine_results[engine_name] = ([], weight)

        # 結果の統合
        return self._merge_results(engine_results, k)

    def _sequential_search(
        self,
        query: str,
        k: int,
        langchain_weight: float,
        llama_index_weight: float
    ) -> List[LangChainDocument]:
        """順次検索の実行"""

        engine_results = {}

        # LangChain検索
        if self.langchain_engine:
            try:
                langchain_results = self._search_langchain(query, k)
                engine_results['langchain'] = (langchain_results, langchain_weight)
                print(f"[HYBRID] ✅ LangChain search: {len(langchain_results)} results")
            except Exception as e:
                print(f"[HYBRID] ❌ LangChain search failed: {e}")
                engine_results['langchain'] = ([], langchain_weight)

        # LlamaIndex検索
        if self.llama_index_engine:
            try:
                llama_results = self._search_llama_index(query, k)
                engine_results['llama_index'] = (llama_results, llama_index_weight)
                print(f"[HYBRID] ✅ LlamaIndex search: {len(llama_results)} results")
            except Exception as e:
                print(f"[HYBRID] ❌ LlamaIndex search failed: {e}")
                engine_results['llama_index'] = ([], llama_index_weight)

        # 結果の統合
        return self._merge_results(engine_results, k)

    def _search_langchain(self, query: str, k: int) -> List[LangChainDocument]:
        """LangChain検索の実行"""
        if not self.langchain_engine:
            return []

        return self.langchain_engine.smart_similarity_search(
            query=query,
            k=k,
            boost_recent=True,
            score_threshold=0.7
        )

    def _search_llama_index(self, query: str, k: int) -> List[LangChainDocument]:
        """LlamaIndex検索の実行"""
        if not self.llama_index_engine:
            return []

        # LlamaIndexで検索
        nodes = self.llama_index_engine.retrieve(query, top_k=k)

        # LangChain Documentに変換
        return self.bridge.llama_to_langchain_documents(nodes)

    def _merge_results(
        self,
        engine_results: Dict[str, Tuple[List[LangChainDocument], float]],
        k: int
    ) -> List[LangChainDocument]:
        """検索結果の統合とランキング"""

        merged_docs = []
        content_seen = set()  # 重複除去用

        # 各エンジンの結果を統合
        for engine_name, (docs, weight) in engine_results.items():
            for i, doc in enumerate(docs):
                # スコア計算（順位ベース + 重み）
                rank_score = (len(docs) - i) / len(docs) if docs else 0
                final_score = rank_score * weight

                # LlamaIndexスコアがある場合は考慮
                if hasattr(doc, 'metadata') and 'llama_score' in doc.metadata:
                    llama_score = doc.metadata['llama_score']
                    final_score = (final_score + llama_score) / 2

                # 重複チェック
                content_key = doc.page_content[:100]  # 最初の100文字で重複判定
                if content_key in content_seen:
                    continue
                content_seen.add(content_key)

                # メタデータに統合情報を追加
                enhanced_metadata = doc.metadata.copy() if doc.metadata else {}
                enhanced_metadata.update({
                    'hybrid_score': final_score,
                    'engine': engine_name,
                    'rank': i + 1
                })

                enhanced_doc = LangChainDocument(
                    page_content=doc.page_content,
                    metadata=enhanced_metadata
                )

                merged_docs.append(enhanced_doc)

        # スコア順でソート
        merged_docs.sort(key=lambda x: x.metadata.get('hybrid_score', 0), reverse=True)

        print(f"[HYBRID] 📊 Merged results: {len(merged_docs)} unique documents")
        return merged_docs[:k]

    def llama_index_query(self, query: str, top_k: int = 5) -> Optional[str]:
        """
        LlamaIndexクエリエンジンを使用した回答生成

        Args:
            query: クエリテキスト
            top_k: 参照する文書数

        Returns:
            生成された回答テキスト
        """
        if not self.llama_index_engine:
            print("[HYBRID] ⚠️ LlamaIndex engine not available")
            return None

        try:
            response = self.llama_index_engine.query(query, top_k=top_k)
            if response:
                print(f"[HYBRID] ✅ LlamaIndex query response generated")
                return response.response
            return None

        except Exception as e:
            print(f"[HYBRID] ❌ LlamaIndex query error: {e}")
            return None

    def add_documents_to_both(self, documents: List[Union[str, Dict[str, Any]]]) -> Dict[str, bool]:
        """
        両方のエンジンにドキュメントを追加

        Args:
            documents: 追加するドキュメント

        Returns:
            各エンジンでの追加結果
        """
        results = {"langchain": False, "llama_index": False}

        # LangChain用ドキュメント変換
        langchain_docs = []
        for doc in documents:
            if isinstance(doc, str):
                langchain_doc = LangChainDocument(
                    page_content=doc,
                    metadata={"timestamp": datetime.now().isoformat()}
                )
            elif isinstance(doc, dict):
                langchain_doc = LangChainDocument(
                    page_content=doc.get("text", doc.get("page_content", "")),
                    metadata=doc.get("metadata", {})
                )
            else:
                continue
            langchain_docs.append(langchain_doc)

        # LangChainに追加
        if self.langchain_engine and langchain_docs:
            try:
                # ChromaDBに直接追加（Uma3ChromaDBImproverには追加メソッドがないため）
                vector_db = self.langchain_engine.vector_db
                vector_db.add_documents(langchain_docs)
                results["langchain"] = True
                print(f"[HYBRID] ✅ Added {len(langchain_docs)} documents to LangChain")
            except Exception as e:
                print(f"[HYBRID] ❌ LangChain document addition failed: {e}")

        # LlamaIndexに追加
        if self.llama_index_engine:
            results["llama_index"] = self.llama_index_engine.add_documents(documents)

        return results

    def get_hybrid_stats(self) -> Dict[str, Any]:
        """ハイブリッドシステムの統計情報"""
        stats = {
            "engines": {
                "langchain": self.langchain_engine is not None,
                "llama_index": self.llama_index_engine is not None
            },
            "configuration": {
                "chroma_directory": self.chroma_persist_directory,
                "embedding_model": self.embedding_model_name,
                "llm_model": self.llm_model
            }
        }

        # LlamaIndex統計
        if self.llama_index_engine:
            stats["llama_index"] = self.llama_index_engine.get_stats()

        return stats

    def __del__(self):
        """リソースのクリーンアップ"""
        if hasattr(self, 'thread_pool'):
            self.thread_pool.shutdown(wait=False)


# テスト関数
def test_hybrid_rag_engine():
    """ハイブリッドRAGエンジンのテスト"""
    print("\n=== Hybrid RAG Engine Test ===")

    try:
        # エンジン初期化
        engine = Uma3HybridRAGEngine(
            chroma_persist_directory="test_hybrid_chroma",
            enable_langchain=True,
            enable_llama_index=True
        )

        # テストドキュメント追加
        test_docs = [
            "これはハイブリッドRAGシステムのテストドキュメントです。",
            {"text": "LangChainとLlamaIndexを統合したシステムが動作しています。", "metadata": {"type": "test"}},
            "複数のRAGエンジンを併用することで検索精度が向上します。"
        ]

        add_results = engine.add_documents_to_both(test_docs)
        print(f"✅ Document addition results: {add_results}")

        # ハイブリッド検索テスト
        search_results = engine.hybrid_search("テスト", k=5)
        print(f"✅ Hybrid search returned {len(search_results)} results")

        for i, doc in enumerate(search_results[:3]):  # 上位3件表示
            score = doc.metadata.get('hybrid_score', 0)
            engine_name = doc.metadata.get('engine', 'unknown')
            print(f"  {i+1}. [{engine_name}] Score: {score:.3f} - {doc.page_content[:80]}...")

        # LlamaIndexクエリテスト
        if engine.llama_index_engine:
            response = engine.llama_index_query("ハイブリッドRAGシステムについて教えて")
            if response:
                print(f"✅ LlamaIndex response: {response[:150]}...")

        # 統計情報
        stats = engine.get_hybrid_stats()
        print(f"✅ Hybrid stats: {stats}")

        print("✅ Hybrid RAG Engine test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Hybrid RAG Engine test failed: {e}")
        return False


if __name__ == "__main__":
    test_hybrid_rag_engine()
