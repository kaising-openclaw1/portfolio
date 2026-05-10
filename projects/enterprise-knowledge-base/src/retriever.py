"""
混合检索模块：BM25 关键词检索 + 向量语义检索 + Reranker 重排序
显著提升知识库问答的准确率。
"""

from typing import List, Optional
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_core.documents import Document


class HybridRetriever:
    """混合检索器：结合 BM25 关键词检索和向量语义检索"""

    def __init__(
        self,
        chroma_db: Chroma,
        documents: Optional[List[Document]] = None,
        bm25_k: int = 3,
        vector_k: int = 3,
        bm25_weight: float = 0.3,
        vector_weight: float = 0.7,
        use_reranker: bool = True,
        reranker_top_n: int = 3,
        reranker_model: str = "BAAI/bge-reranker-v2-m3",
    ):
        self.chroma_db = chroma_db
        self.bm25_k = bm25_k
        self.vector_k = vector_k
        self.use_reranker = use_reranker

        # 向量检索
        self.vector_retriever = chroma_db.as_retriever(
            search_kwargs={"k": vector_k}
        )

        # BM25 关键词检索（需要原始文档）
        self.bm25_retriever = None
        if documents:
            self.bm25_retriever = BM25Retriever.from_documents(documents)
            self.bm25_retriever.k = bm25_k

        # 混合检索器
        if self.bm25_retriever:
            self.ensemble = EnsembleRetriever(
                retrievers=[self.bm25_retriever, self.vector_retriever],
                weights=[bm25_weight, vector_weight],
            )
        else:
            self.ensemble = self.vector_retriever

        # Reranker 重排序
        if use_reranker:
            try:
                from langchain_community.cross_encoders import HuggingFaceCrossEncoder
                reranker_model_obj = HuggingFaceCrossEncoder(model_name=reranker_model)
                self.compressor = CrossEncoderReranker(
                    model=reranker_model_obj,
                    top_n=reranker_top_n,
                )
                self.compressed_retriever = ContextualCompressionRetriever(
                    base_compressor=self.compressor,
                    base_retriever=self.ensemble,
                )
            except Exception:
                print("⚠️  Reranker 模型加载失败，使用基础混合检索")
                self.use_reranker = False
                self.compressed_retriever = self.ensemble

    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Document]:
        """执行检索"""
        if self.use_reranker:
            return self.compressed_retriever.invoke(query)
        return self.ensemble.invoke(query)
