"""
企业知识库文档索引构建器
支持 Markdown、PDF、TXT 等多种格式文档的自动解析、切分、向量化和索引构建。
"""

import os
import sys
from pathlib import Path
from typing import List, Optional
from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    UnstructuredPDFLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings


class KnowledgeIndexer:
    """企业知识库索引构建器"""

    def __init__(
        self,
        docs_dir: str = "./knowledge_docs",
        persist_dir: str = "./chroma_db",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        model_name: str = "BAAI/bge-m3",
        device: str = "cpu",
    ):
        self.docs_dir = docs_dir
        self.persist_dir = persist_dir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": device},
            encode_kwargs={"normalize_embeddings": True},
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],
        )

    def load_documents(self) -> list:
        """加载多种格式的文档"""
        docs: list = []
        loaders = [
            (DirectoryLoader(self.docs_dir, glob="**/*.md", loader_cls=UnstructuredMarkdownLoader), "Markdown"),
            (DirectoryLoader(self.docs_dir, glob="**/*.pdf", loader_cls=UnstructuredPDFLoader), "PDF"),
            (DirectoryLoader(self.docs_dir, glob="**/*.txt", loader_cls=TextLoader), "TXT"),
        ]

        for loader, fmt_name in loaders:
            try:
                loaded = loader.load()
                if loaded:
                    print(f"  ✅ 加载 {len(loaded)} 篇 {fmt_name} 文档")
                    docs.extend(loaded)
            except Exception as e:
                print(f"  ⚠️  加载 {fmt_name} 文档时出错: {e}")

        print(f"\n📚 共加载 {len(docs)} 篇文档")
        return docs

    def split_documents(self, docs: list) -> list:
        """切分文档为小块"""
        chunks = self.text_splitter.split_documents(docs)
        print(f"✂️  切分为 {len(chunks)} 个文档块 (chunk_size={self.chunk_size})")
        return chunks

    def build_index(self) -> Chroma:
        """构建完整的向量索引"""
        print("🔨 开始构建知识库索引...\n")

        # 检查文档目录
        if not os.path.exists(self.docs_dir):
            print(f"⚠️  文档目录 {self.docs_dir} 不存在，请先放入文档")
            sys.exit(1)

        # 加载文档
        docs = self.load_documents()
        if not docs:
            print("⚠️  没有找到任何文档，请先将文档放入 knowledge_docs 目录")
            sys.exit(1)

        # 切分文档
        chunks = self.split_documents(docs)

        # 存入 ChromaDB
        print(f"\n💾 正在构建向量索引...")
        db = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_dir,
        )

        print(f"\n✅ 索引构建完成！")
        print(f"   存储位置: {self.persist_dir}")
        print(f"   文档块数: {len(chunks)}")
        print(f"   嵌入模型: BGE-M3")

        return db

    def rebuild_index(self) -> Chroma:
        """重建索引（清空旧数据后重新构建）"""
        import shutil
        if os.path.exists(self.persist_dir):
            print(f"🗑️  删除旧索引: {self.persist_dir}")
            shutil.rmtree(self.persist_dir)
        return self.build_index()


if __name__ == "__main__":
    indexer = KnowledgeIndexer(
        docs_dir=os.getenv("DOCS_DIR", "./knowledge_docs"),
        persist_dir=os.getenv("PERSIST_DIR", "./chroma_db"),
        chunk_size=int(os.getenv("CHUNK_SIZE", "500")),
        device=os.getenv("EMBEDDING_DEVICE", "cpu"),
    )
    indexer.build_index()
