"""
LlamaIndex RAG エンジン
LangChain + LlamaIndex を組み合わせた高度なRAGシステム
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    from llama_index.core import (
        Document,
        QueryBundle,
        Settings,
        StorageContext,
        VectorStoreIndex,
        load_index_from_storage,
    )
    from llama_index.core.node_parser import SimpleNodeParser
    from llama_index.core.query_engine import BaseQueryEngine
    from llama_index.core.retrievers import BaseRetriever
    from llama_index.core.schema import NodeWithScore
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from llama_index.llms.openai import OpenAI
    from llama_index.vector_stores.chroma import ChromaVectorStore
except ImportError as e:
    print(f"⚠️ LlamaIndex import error: {e}")
    print(
        "Please install: pip install llama-index llama-index-vector-stores-chroma llama-index-embeddings-huggingface llama-index-llms-openai"
    )
    sys.exit(1)

import chromadb
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


class Uma3RAGEngine:
    """
    LlamaIndex を使用した高度なRAG エンジン

    機能:
    - マルチモーダル検索（Vector + Semantic + キーワード）
    - メタデータフィルタリング
    - 時間軸検索
    - スケジュール特化検索
    """

    def __init__(
        self,
        persist_directory: str = "Lesson25/uma3soft-app/db/chroma_store",
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        llm_model: str = "gpt-3.5-turbo",
        openai_api_key: Optional[str] = None,
    ):
        """
        RAG エンジンの初期化

        Args:
            persist_directory: ChromaDBの保存ディレクトリ
            embedding_model_name: 埋め込みモデル名
            llm_model: LLMモデル名
            openai_api_key: OpenAI APIキー
        """
        self.persist_directory = persist_directory
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")

        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")

        # LlamaIndex グローバル設定
        Settings.embed_model = HuggingFaceEmbedding(model_name=embedding_model_name)
        Settings.llm = OpenAI(model=llm_model, api_key=self.openai_api_key)

        # ChromaDB クライアント初期化
        self.chroma_client = chromadb.PersistentClient(path=persist_directory)

        # LangChain ChromaDB（既存システムとの互換性）
        self.langchain_embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model_name
        )
        self.langchain_vectordb = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.langchain_embeddings,
        )

        # LlamaIndex VectorStore
        try:
            chroma_collection = self.chroma_client.get_or_create_collection("langchain")
            self.vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

            # インデックス構築または読み込み
            self._initialize_index()

        except Exception as e:
            print(f"⚠️ ChromaVectorStore initialization error: {e}")
            # フォールバックとして既存のChromaDBを使用
            self.vector_store = None
            self.index = None
            print("Falling back to LangChain ChromaDB compatibility mode")

    def _initialize_index(self):
        """LlamaIndex インデックスの初期化"""
        try:
            if self.vector_store:
                # 既存のインデックスから読み込み
                storage_context = StorageContext.from_defaults(
                    vector_store=self.vector_store
                )
                self.index = VectorStoreIndex.from_vector_store(
                    vector_store=self.vector_store, storage_context=storage_context
                )
                print("✅ LlamaIndex initialized from existing ChromaDB")
            else:
                self.index = None
                print("⚠️ LlamaIndex index not available, using compatibility mode")

        except Exception as e:
            print(f"⚠️ Index initialization error: {e}")
            self.index = None

    def hybrid_search(
        self,
        query: str,
        k: int = 5,
        score_threshold: float = 0.0,
        metadata_filters: Optional[Dict[str, Any]] = None,
        include_schedule_data: bool = True,
        time_range_days: Optional[int] = None,
    ) -> List[Document]:
        """
        ハイブリッド検索（Vector + Semantic + メタデータフィルタリング）

        Args:
            query: 検索クエリ
            k: 取得する結果数
            score_threshold: スコア閾値
            metadata_filters: メタデータフィルタ条件
            include_schedule_data: スケジュールデータを含めるか
            time_range_days: 時間範囲フィルタ（日数）

        Returns:
            検索結果のDocumentリスト
        """
        print(f"[RAG] Hybrid search: '{query}' (k={k}, threshold={score_threshold})")

        results = []

        # LlamaIndex による検索
        if self.index:
            try:
                # 時間フィルタの設定
                filters = {}
                if time_range_days:
                    current_date = datetime.now()
                    start_date = current_date - timedelta(days=time_range_days)
                    filters["timestamp"] = {">=": start_date.isoformat()}

                if metadata_filters:
                    filters.update(metadata_filters)

                # クエリ実行
                query_engine = self.index.as_query_engine(
                    similarity_top_k=k,
                    response_mode="no_text",  # 検索結果のみ取得
                )

                response = query_engine.query(query)

                # 結果をDocument形式に変換
                if hasattr(response, "source_nodes"):
                    for node_with_score in response.source_nodes:
                        if node_with_score.score >= score_threshold:
                            doc = Document(
                                text=node_with_score.node.text,
                                metadata=node_with_score.node.metadata or {},
                            )
                            results.append(doc)

                print(f"[RAG] LlamaIndex search returned {len(results)} results")

            except Exception as e:
                print(f"⚠️ LlamaIndex search error: {e}")

        # フォールバック: LangChain ChromaDB 検索
        if len(results) < k // 2:  # 結果が少ない場合は補完
            try:
                langchain_results = self._langchain_fallback_search(
                    query, k=k - len(results), score_threshold=score_threshold
                )

                # 重複除去して追加
                existing_texts = {doc.text for doc in results}
                for lc_doc in langchain_results:
                    if lc_doc.page_content not in existing_texts:
                        doc = Document(
                            text=lc_doc.page_content, metadata=lc_doc.metadata
                        )
                        results.append(doc)

                print(
                    f"[RAG] Added {len(langchain_results)} results from LangChain fallback"
                )

            except Exception as e:
                print(f"⚠️ LangChain fallback error: {e}")

        # スケジュール特化検索の追加
        if include_schedule_data and self._is_schedule_query(query):
            schedule_results = self._schedule_enhanced_search(query, k=2)
            for sched_doc in schedule_results:
                if sched_doc.text not in {doc.text for doc in results}:
                    results.append(sched_doc)

        # 結果の後処理
        results = self._post_process_results(results, query)

        print(f"[RAG] Final results: {len(results)} documents")
        return results[:k]  # 最大k件まで

    def _langchain_fallback_search(
        self, query: str, k: int = 5, score_threshold: float = 0.0
    ):
        """LangChain ChromaDB を使用したフォールバック検索"""
        return self.langchain_vectordb.similarity_search_with_score(query, k=k)

    def _is_schedule_query(self, query: str) -> bool:
        """スケジュール関連クエリの判定"""
        schedule_keywords = [
            "予定",
            "スケジュール",
            "大会",
            "練習",
            "試合",
            "リーグ",
            "今日",
            "明日",
            "来週",
            "今週",
            "週末",
            "いつ",
            "日程",
        ]
        return any(keyword in query for keyword in schedule_keywords)

    def _schedule_enhanced_search(self, query: str, k: int = 2) -> List[Document]:
        """スケジュール特化検索"""
        results = []
        try:
            # [ノート]データを優先的に検索
            note_query = f"[ノート] {query}"
            note_results = self.langchain_vectordb.similarity_search(note_query, k=k)

            for doc in note_results:
                if "[ノート]" in doc.page_content:
                    results.append(
                        Document(text=doc.page_content, metadata=doc.metadata)
                    )

            print(f"[RAG] Schedule enhanced search found {len(results)} note documents")

        except Exception as e:
            print(f"⚠️ Schedule enhanced search error: {e}")

        return results

    def _post_process_results(
        self, results: List[Document], query: str
    ) -> List[Document]:
        """検索結果の後処理（重複除去、関連度ソート等）"""
        # 重複除去
        seen_texts = set()
        unique_results = []

        for doc in results:
            text_signature = doc.text[:100]  # 最初の100文字で重複判定
            if text_signature not in seen_texts:
                seen_texts.add(text_signature)
                unique_results.append(doc)

        # スケジュール関連の場合は[ノート]データを優先
        if self._is_schedule_query(query):
            note_docs = [doc for doc in unique_results if "[ノート]" in doc.text]
            other_docs = [doc for doc in unique_results if "[ノート]" not in doc.text]
            unique_results = note_docs + other_docs

        return unique_results

    def get_query_engine(self, **kwargs) -> Optional[BaseQueryEngine]:
        """LlamaIndex QueryEngine の取得"""
        if self.index:
            return self.index.as_query_engine(**kwargs)
        return None

    def get_retriever(self, **kwargs) -> Optional[BaseRetriever]:
        """LlamaIndex Retriever の取得"""
        if self.index:
            return self.index.as_retriever(**kwargs)
        return None

    def add_documents(self, documents: List[Document]) -> bool:
        """文書の追加"""
        try:
            if self.index and documents:
                # LlamaIndex に文書を追加
                for doc in documents:
                    self.index.insert(doc)
                print(f"✅ Added {len(documents)} documents to LlamaIndex")
                return True
        except Exception as e:
            print(f"⚠️ Document addition error: {e}")

        return False

    def get_analytics(self, query: str) -> Dict[str, Any]:
        """検索分析情報の取得"""
        analytics = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "is_schedule_query": self._is_schedule_query(query),
            "available_engines": {
                "llamaindex": self.index is not None,
                "langchain": self.langchain_vectordb is not None,
            },
        }

        return analytics


def test_rag_engine():
    """RAG エンジンのテスト"""
    try:
        print("🧪 Testing Uma3RAGEngine...")

        # エンジン初期化
        rag_engine = Uma3RAGEngine()

        # テストクエリ
        test_queries = [
            "今週の予定を教えて",
            "羽村ライオンズの試合はいつ？",
            "練習の予定はありますか？",
        ]

        for query in test_queries:
            print(f"\n📝 Testing query: '{query}'")
            results = rag_engine.hybrid_search(query, k=3)

            print(f"Results: {len(results)}")
            for i, doc in enumerate(results, 1):
                print(f"  {i}. {doc.text[:100]}...")

        print("✅ RAG Engine test completed")

    except Exception as e:
        print(f"❌ RAG Engine test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_rag_engine()
