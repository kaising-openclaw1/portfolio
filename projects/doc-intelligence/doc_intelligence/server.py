"""Doc Intelligence - FastAPI 服务"""

import os
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

from .processor import DocumentProcessor

app = FastAPI(
    title="Doc Intelligence API",
    description="智能文档处理服务 - 摘要、翻译、转换、关键词提取",
    version="1.0.0",
)

processor: Optional[DocumentProcessor] = None


def get_processor() -> DocumentProcessor:
    global processor
    if processor is None:
        processor = DocumentProcessor(
            llm_api_key=os.environ.get("LLM_API_KEY"),
            llm_base_url=os.environ.get("LLM_BASE_URL", "https://api.deepseek.com/v1"),
            llm_model=os.environ.get("LLM_MODEL", "deepseek-chat"),
        )
    return processor


class SummarizeRequest(BaseModel):
    max_length: int = 500


class TranslateRequest(BaseModel):
    target_lang: str = "en"


class KeywordsRequest(BaseModel):
    top_k: int = 10
    method: str = "hybrid"


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


@app.post("/api/summarize")
async def summarize(file: UploadFile = File(...), max_length: int = Form(500)):
    proc = get_processor()
    content = await file.read()
    tmp_path = f"/tmp/{file.filename}"
    with open(tmp_path, "wb") as f:
        f.write(content)
    try:
        summary = proc.summarize(tmp_path, max_length=max_length)
        return {"file": file.filename, "summary": summary}
    finally:
        os.remove(tmp_path)


@app.post("/api/translate")
async def translate(file: UploadFile = File(...), target_lang: str = Form("en")):
    proc = get_processor()
    content = await file.read()
    tmp_path = f"/tmp/{file.filename}"
    with open(tmp_path, "wb") as f:
        f.write(content)
    try:
        translated = proc.translate(tmp_path, target_lang=target_lang)
        return {"file": file.filename, "target_lang": target_lang, "text": translated}
    finally:
        os.remove(tmp_path)


@app.post("/api/keywords")
async def keywords(file: UploadFile = File(...), top_k: int = Form(10), method: str = Form("hybrid")):
    proc = get_processor()
    content = await file.read()
    tmp_path = f"/tmp/{file.filename}"
    with open(tmp_path, "wb") as f:
        f.write(content)
    try:
        kws = proc.extract_keywords(tmp_path, top_k=top_k, method=method)
        return {"file": file.filename, "keywords": kws}
    finally:
        os.remove(tmp_path)


@app.post("/api/convert")
async def convert(file: UploadFile = File(...), output_format: str = Form("markdown")):
    proc = get_processor()
    content = await file.read()
    tmp_path = f"/tmp/{file.filename}"
    with open(tmp_path, "wb") as f:
        f.write(content)
    try:
        out = proc.convert(tmp_path, output_format=output_format, output_dir="/tmp")
        return {"file": file.filename, "output_format": output_format, "output": out}
    finally:
        os.remove(tmp_path)
