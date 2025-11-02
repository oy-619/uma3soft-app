"""
Uma3 LlamaIndex Integration Engine
LangChain システムにLlamaIndexを統合するハイブリッドRAGエンジン
"""

import os
import logging
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

try:
    from llama_index.core import VectorStoreIndex, StorageContext
    from llama_index.core.indices.base import BaseIndex
    from llama_index.core.query_engine import BaseQueryEngine
    from llama_index.core.retrievers import BaseRetriever
    from llama_index.core.schema import Document as LlamaDocument, NodeWithScore
    from llama_index.core.llms import LLM
    from llama_index.core.embeddings import BaseEmbedding

    # LlamaIndex embeddings - 新しいパッケージ構造に対応
    HuggingFaceEmbedding = None
    try:
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        print("[LLAMA] ✅ HuggingFace embeddings imported")
    except ImportError as e1:
        print(f"[LLAMA] ⚠️ HuggingFace embeddings not available: {e1}")

    # OpenAI Embeddings as fallback
    try:
        from llama_index.embeddings.openai import OpenAIEmbedding
        print("[LLAMA] ✅ OpenAI embeddings imported")
    except ImportError as e3:
        print(f"[LLAMA] ⚠️ OpenAI embeddings not available: {e3}")
        OpenAIEmbedding = None

    from llama_index.llms.openai import OpenAI
    from llama_index.vector_stores.chroma import ChromaVectorStore
    from llama_index.core.storage.storage_context import StorageContext
    from llama_index.core.vector_stores.types import VectorStore

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
    print("[LLAMA] ✅ LlamaIndex components successfully imported")
except ImportError as e:
    print(f"[LLAMA] ❌ LlamaIndex import error: {e}")
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

# LangChain互換性インポート
try:
    from langchain_chroma import Chroma
    from langchain_core.documents import Document as LangChainDocument
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_openai import ChatOpenAI
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"[LLAMA] ❌ LangChain import error: {e}")
    LANGCHAIN_AVAILABLE = False

# ChromaDB直接インポート
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError as e:
    print(f"[LLAMA] ❌ ChromaDB import error: {e}")
    CHROMADB_AVAILABLE = False


class Uma3LlamaIndexEngine:
    """
    Uma3専用LlamaIndex統合エンジン

    機能:
    - LangChain ChromaDBとの互換性
    - LlamaIndex VectorStoreIndex
    - ハイブリッド検索システム
    - カスタムクエリエンジン
    """

    def __init__(
        self,
        chroma_persist_directory: str = None,
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        llm_model: str = "gpt-3.5-turbo",
        collection_name: str = "uma3_documents"
    ):
        """
        LlamaIndex エンジンの初期化

        Args:
            chroma_persist_directory: ChromaDBの保存ディレクトリ (Noneの場合はデフォルト使用)
            embedding_model_name: 埋め込みモデル名
            llm_model: LLMモデル名
            collection_name: コレクション名
        """
        # 絶対パス方式でデフォルトディレクトリを設定
        if chroma_persist_directory is None:
            chroma_persist_directory = DEFAULT_CHROMA_PERSIST_DIRECTORY

        print(f"[LLAMA] 🚀 Initializing Uma3LlamaIndexEngine")
        print(f"[LLAMA] ChromaDB directory: {chroma_persist_directory}")
        print(f"[LLAMA] Embedding model: {embedding_model_name}")
        print(f"[LLAMA] LLM model: {llm_model}")

        self.chroma_persist_directory = chroma_persist_directory
        self.embedding_model_name = embedding_model_name
        self.llm_model = llm_model
        self.collection_name = collection_name

        # 初期化フラグ
        self.is_initialized = False
        self.index: Optional[VectorStoreIndex] = None
        self.query_engine: Optional[BaseQueryEngine] = None
        self.retriever: Optional[BaseRetriever] = None

        # コンポーネント初期化
        if not LLAMA_INDEX_AVAILABLE:
            print("[LLAMA] ⚠️ LlamaIndex not available - running in compatibility mode")
            return

        try:
            self._initialize_components()
            self.is_initialized = True
            print("[LLAMA] ✅ LlamaIndex engine successfully initialized")
        except Exception as e:
            print(f"[LLAMA] ❌ Initialization failed: {e}")
            print("[LLAMA] 🔄 Falling back to compatibility mode")
            self.is_initialized = False

    def _initialize_components(self):
        """LlamaIndexコンポーネントの初期化"""

        # 1. LLM初期化
        self.llm = OpenAI(model=self.llm_model, temperature=0.1)
        print(f"[LLAMA] ✅ LLM initialized: {self.llm_model}")

        # 2. Embedding初期化 - 複数の方法を試行
        try:
            self.embed_model = HuggingFaceEmbedding(
                model_name=self.embedding_model_name
            )
            print(f"[LLAMA] ✅ HuggingFace Embedding model initialized: {self.embedding_model_name}")
        except Exception as e:
            print(f"[LLAMA] ⚠️ HuggingFace embedding failed: {e}")
            # OpenAI埋め込みにフォールバック
            try:
                from llama_index.embeddings.openai import OpenAIEmbedding
                self.embed_model = OpenAIEmbedding()
                print(f"[LLAMA] 🔄 Fallback to OpenAI embedding")
            except Exception as e2:
                print(f"[LLAMA] ❌ All embedding options failed: {e2}")
                raise e2

        # 3. ChromaDBクライアント初期化
        if CHROMADB_AVAILABLE:
            self.chroma_client = chromadb.PersistentClient(
                path=self.chroma_persist_directory
            )
            print(f"[LLAMA] ✅ ChromaDB client initialized")

            # コレクション取得または作成
            try:
                self.chroma_collection = self.chroma_client.get_collection(
                    name=self.collection_name
                )
                print(f"[LLAMA] ✅ Existing collection loaded: {self.collection_name}")
            except:
                self.chroma_collection = self.chroma_client.create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
                print(f"[LLAMA] ✅ New collection created: {self.collection_name}")

        # 4. LlamaIndex ChromaVectorStore初期化
        self.vector_store = ChromaVectorStore(
            chroma_collection=self.chroma_collection
        )
        print("[LLAMA] ✅ LlamaIndex ChromaVectorStore initialized")

        # 5. StorageContext初期化
        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )
        print("[LLAMA] ✅ StorageContext initialized")

        # 6. ServiceContext初期化（LlamaIndex v0.10+）
        try:
            from llama_index.core import Settings
            Settings.llm = self.llm
            Settings.embed_model = self.embed_model
            print("[LLAMA] ✅ Global Settings configured")
        except ImportError:
            # 古いバージョン用のフォールバック
            from llama_index.core import ServiceContext
            self.service_context = ServiceContext.from_defaults(
                llm=self.llm,
                embed_model=self.embed_model
            )
            print("[LLAMA] ✅ ServiceContext initialized (legacy)")

        # 7. VectorStoreIndex初期化
        try:
            # 既存のインデックスがあるかチェック
            self.index = VectorStoreIndex.from_vector_store(
                vector_store=self.vector_store,
                storage_context=self.storage_context
            )
            print("[LLAMA] ✅ Existing VectorStoreIndex loaded")
        except Exception as e:
            print(f"[LLAMA] 📝 Creating new VectorStoreIndex: {e}")
            # 新規インデックス作成（空のドキュメントで初期化）
            self.index = VectorStoreIndex(
                nodes=[],
                storage_context=self.storage_context
            )
            print("[LLAMA] ✅ New VectorStoreIndex created")

        # 8. QueryEngine初期化
        self.query_engine = self.index.as_query_engine(
            similarity_top_k=10,
            response_mode="compact"
        )
        print("[LLAMA] ✅ QueryEngine initialized")

        # 9. Retriever初期化
        self.retriever = self.index.as_retriever(
            similarity_top_k=10
        )
        print("[LLAMA] ✅ Retriever initialized")

    def add_documents(self, documents: List[Union[str, Dict[str, Any]]]) -> bool:
        """
        ドキュメントをLlamaIndexに追加

        Args:
            documents: 追加するドキュメントリスト

        Returns:
            bool: 追加成功フラグ
        """
        if not self.is_initialized:
            print("[LLAMA] ⚠️ Engine not initialized - cannot add documents")
            return False

        try:
            llama_docs = []

            for doc in documents:
                if isinstance(doc, str):
                    llama_doc = LlamaDocument(
                        text=doc,
                        metadata={
                            "timestamp": datetime.now().isoformat(),
                            "source": "uma3_system"
                        }
                    )
                elif isinstance(doc, dict):
                    text = doc.get("text", doc.get("page_content", ""))
                    metadata = doc.get("metadata", {})
                    metadata.update({
                        "timestamp": datetime.now().isoformat(),
                        "source": "uma3_system"
                    })
                    llama_doc = LlamaDocument(text=text, metadata=metadata)
                else:
                    continue

                llama_docs.append(llama_doc)

            # インデックスに追加
            self.index.insert_documents(llama_docs)
            print(f"[LLAMA] ✅ Added {len(llama_docs)} documents to index")
            return True

        except Exception as e:
            print(f"[LLAMA] ❌ Error adding documents: {e}")
            return False

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        response_mode: str = "compact"
    ) -> Optional[Response]:
        """
        LlamaIndex クエリエンジンでクエリ実行

        Args:
            query_text: クエリテキスト
            top_k: 取得する結果数
            response_mode: レスポンスモード

        Returns:
            LlamaIndex Response オブジェクト
        """
        if not self.is_initialized:
            print("[LLAMA] ⚠️ Engine not initialized - cannot execute query")
            return None

        try:
            # 動的にtop_kを設定
            query_engine = self.index.as_query_engine(
                similarity_top_k=top_k,
                response_mode=response_mode
            )

            response = query_engine.query(query_text)
            print(f"[LLAMA] ✅ Query executed: '{query_text[:50]}...'")
            return response

        except Exception as e:
            print(f"[LLAMA] ❌ Query error: {e}")
            return None

    def retrieve(self, query_text: str, top_k: int = 5) -> List[NodeWithScore]:
        """
        類似文書の検索（回答生成なし）

        Args:
            query_text: クエリテキスト
            top_k: 取得する結果数

        Returns:
            NodeWithScore のリスト
        """
        if not self.is_initialized:
            print("[LLAMA] ⚠️ Engine not initialized - cannot retrieve")
            return []

        try:
            # 動的にtop_kを設定
            retriever = self.index.as_retriever(similarity_top_k=top_k)
            nodes = retriever.retrieve(query_text)

            print(f"[LLAMA] ✅ Retrieved {len(nodes)} nodes for: '{query_text[:50]}...'")
            return nodes

        except Exception as e:
            print(f"[LLAMA] ❌ Retrieval error: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """
        インデックス統計情報を取得

        Returns:
            統計情報辞書
        """
        if not self.is_initialized:
            return {"status": "not_initialized"}

        try:
            # ChromaDBコレクション統計
            collection_count = self.chroma_collection.count() if hasattr(self.chroma_collection, 'count') else 0

            return {
                "status": "initialized",
                "llm_model": self.llm_model,
                "embedding_model": self.embedding_model_name,
                "collection_name": self.collection_name,
                "document_count": collection_count,
                "chroma_directory": self.chroma_persist_directory
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# LangChain互換性レイヤー
class LlamaIndexLangChainBridge:
    """
    LlamaIndexとLangChainの橋渡しクラス
    LangChainのDocumentをLlamaIndexに変換し、逆変換も行う
    """

    @staticmethod
    def langchain_to_llama_documents(langchain_docs: List[LangChainDocument]) -> List[LlamaDocument]:
        """LangChain DocumentをLlamaIndex Documentに変換"""
        if not LLAMA_INDEX_AVAILABLE:
            return []

        llama_docs = []
        for doc in langchain_docs:
            llama_doc = LlamaDocument(
                text=doc.page_content,
                metadata=doc.metadata or {}
            )
            llama_docs.append(llama_doc)

        return llama_docs

    @staticmethod
    def llama_to_langchain_documents(llama_nodes: List[NodeWithScore]) -> List[LangChainDocument]:
        """LlamaIndex NodeWithScoreをLangChain Documentに変換"""
        if not LANGCHAIN_AVAILABLE:
            return []

        langchain_docs = []
        for node_with_score in llama_nodes:
            doc = LangChainDocument(
                page_content=node_with_score.node.text,
                metadata={
                    **node_with_score.node.metadata,
                    "llama_score": node_with_score.score
                }
            )
            langchain_docs.append(doc)

        return langchain_docs


# テスト用関数
def test_llama_index_integration():
    """LlamaIndex統合テスト"""
    print("\n=== LlamaIndex Integration Test ===")

    if not LLAMA_INDEX_AVAILABLE:
        print("❌ LlamaIndex not available - skipping test")
        return False

    try:
        # テスト用のディレクトリ
        test_directory = "test_chroma_store"

        # エンジン初期化
        engine = Uma3LlamaIndexEngine(
            chroma_persist_directory=test_directory,
            collection_name="test_collection"
        )

        if not engine.is_initialized:
            print("❌ Engine initialization failed")
            return False

        # テストドキュメント追加
        test_docs = [
            "これはテスト用のドキュメントです。",
            {"text": "LlamaIndexとLangChainの統合テストを実行中です。", "metadata": {"type": "test"}},
            "RAGシステムが正常に動作することを確認します。"
        ]

        success = engine.add_documents(test_docs)
        if not success:
            print("❌ Document addition failed")
            return False

        # クエリテスト
        response = engine.query("テスト")
        if response is None:
            print("❌ Query failed")
            return False

        print(f"✅ Query response: {response.response[:100]}...")

        # 統計情報取得
        stats = engine.get_stats()
        print(f"✅ Stats: {stats}")

        print("✅ LlamaIndex integration test passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    test_llama_index_integration()
