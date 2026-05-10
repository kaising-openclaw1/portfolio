"""
企业知识库问答 API 服务
基于 FastAPI + RAG，提供企业级知识库问答接口。
"""

import os
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


# ─── 配置 ───────────────────────────────────────────────

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")
LLM_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
LLM_API_BASE = os.getenv("LLM_API_BASE", "https://api.deepseek.com")
CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_db")
TOP_K = int(os.getenv("TOP_K", "5"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))


# ─── 初始化组件 ──────────────────────────────────────────

embeddings = None
db = None
llm = None
rag_chain = None


def init_components():
    """初始化 RAG 组件"""
    global embeddings, db, llm, rag_chain

    print("🔧 初始化 RAG 组件...")

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": os.getenv("EMBEDDING_DEVICE", "cpu")},
        encode_kwargs={"normalize_embeddings": True},
    )

    db = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
    doc_count = db._collection.count()
    print(f"  📚 向量库加载完成，共 {doc_count} 个文档块")

    llm = ChatOpenAI(
        model=LLM_MODEL,
        api_key=LLM_API_KEY,
        api_base=LLM_API_BASE,
        temperature=TEMPERATURE,
    )

    # RAG Prompt
    qa_prompt = PromptTemplate.from_template(
        """你是企业知识库助手。请根据以下参考资料回答问题。

参考资料：
{context}

问题：{question}

要求：
1. 只根据参考资料回答，不要编造信息
2. 如果参考资料不足以回答问题，请直接说"抱歉，知识库中没有相关信息"
3. 回答要简洁、准确、专业
4. 引用相关文档来源（如果有）

回答："""
    )

    retriever = db.as_retriever(search_kwargs={"k": TOP_K})

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | qa_prompt
        | llm
        | StrOutputParser()
    )

    print("  ✅ RAG 组件初始化完成\n")


def format_docs(docs):
    """格式化检索到的文档"""
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


# ─── FastAPI 应用 ────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    init_components()
    yield


app = FastAPI(
    title="企业知识库问答系统",
    description="基于 RAG 技术的企业级知识库问答方案",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── 数据模型 ────────────────────────────────────────────


class QueryRequest(BaseModel):
    question: str
    top_k: int = 5


class QueryResponse(BaseModel):
    answer: str
    sources: List[str]


# ─── 路由 ────────────────────────────────────────────────


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """知识库问答接口"""
    try:
        if rag_chain is None:
            raise HTTPException(status_code=503, detail="服务未初始化")

        answer = rag_chain.invoke(request.question)

        # 检索来源文档
        sources = []
        retriever = db.as_retriever(search_kwargs={"k": request.top_k})
        docs = retriever.invoke(request.question)
        for doc in docs:
            source = doc.metadata.get("source", "unknown")
            if source not in sources:
                sources.append(source)

        return QueryResponse(answer=answer, sources=sources)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """健康检查"""
    doc_count = db._collection.count() if db else 0
    return {
        "status": "ok",
        "documents": doc_count,
        "model": LLM_MODEL,
        "embedding": EMBEDDING_MODEL,
    }


@app.get("/stats")
async def stats():
    """知识库统计信息"""
    if db is None:
        raise HTTPException(status_code=503, detail="服务未初始化")
    return {
        "total_documents": db._collection.count(),
        "embedding_model": EMBEDDING_MODEL,
        "llm_model": LLM_MODEL,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
