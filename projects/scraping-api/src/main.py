"""Web Scraping API - Main application"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional
import httpx
import sqlite3
import time
import hashlib
import json
import random
from datetime import datetime
from pathlib import Path

from .scraper import ScraperEngine
from .cache import CacheManager

app = FastAPI(
    title="Web Scraping API",
    description="轻量级自部署网页抓取 API",
    version="1.0.0",
)

scraper = ScraperEngine()
cache = CacheManager()

# ── Request Models ──

class ScrapeRequest(BaseModel):
    url: str = Field(..., description="目标 URL")
    format: str = Field(default="markdown", description="输出格式: json | markdown | text | html")
    wait_for: Optional[str] = Field(None, description="CSS selector，等待元素加载")
    timeout: int = Field(default=15000, description="超时毫秒")
    use_cache: bool = Field(default=True, description="使用缓存")
    stealth: bool = Field(default=True, description="反检测模式")
    headers: Optional[dict] = Field(None, description="自定义请求头")

class BatchScrapeRequest(BaseModel):
    urls: list[str] = Field(..., min_length=1, max_length=20)
    format: str = Field(default="markdown")
    concurrency: int = Field(default=3, ge=1, le=10)
    wait_for: Optional[str] = None
    timeout: int = Field(default=15000)
    use_cache: bool = Field(default=True)
    stealth: bool = Field(default=True)

class ScrapeResponse(BaseModel):
    url: str
    status: int
    format: str
    content: str
    title: Optional[str] = None
    timestamp: str
    cached: bool = False
    elapsed_ms: float

# ── Endpoints ──

@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_single(req: ScrapeRequest):
    """抓取单个网页"""
    start = time.time()
    cached = False

    # Check cache
    if req.use_cache:
        cached_data = cache.get(req.url)
        if cached_data:
            cached = True
            elapsed = (time.time() - start) * 1000
            return ScrapeResponse(
                url=req.url,
                status=200,
                format=req.format,
                content=cached_data["content"],
                title=cached_data.get("title"),
                timestamp=cached_data["timestamp"],
                cached=True,
                elapsed_ms=round(elapsed, 2),
            )

    # Scrape
    try:
        result = await scraper.scrape(
            url=req.url,
            format=req.format,
            wait_for=req.wait_for,
            timeout=req.timeout,
            stealth=req.stealth,
            headers=req.headers,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"抓取失败: {str(e)}")

    elapsed = (time.time() - start) * 1000

    # Save to cache
    if req.use_cache:
        cache.save(req.url, result)

    return ScrapeResponse(
        url=req.url,
        status=200,
        format=req.format,
        content=result["content"],
        title=result.get("title"),
        timestamp=result.get("timestamp", datetime.now().isoformat()),
        cached=False,
        elapsed_ms=round(elapsed, 2),
    )


@app.post("/scrape/batch")
async def scrape_batch(req: BatchScrapeRequest):
    """批量抓取多个 URL"""
    results = []
    for url in req.urls:
        try:
            single_req = ScrapeRequest(
                url=url,
                format=req.format,
                wait_for=req.wait_for,
                timeout=req.timeout,
                use_cache=req.use_cache,
                stealth=req.stealth,
            )
            resp = await scrape_single(single_req)
            results.append(resp.model_dump())
        except HTTPException as e:
            results.append({
                "url": url,
                "status": e.status_code,
                "error": e.detail,
            })

    return {"total": len(req.urls), "results": results}


@app.get("/stats")
async def get_stats():
    """抓取统计信息"""
    return {
        "cache_entries": cache.count(),
        "cache_size_bytes": cache.size(),
        "cache_hit_rate": cache.hit_rate(),
        "uptime_since": app.state.start_time,
    }


@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.on_event("startup")
async def startup():
    app.state.start_time = datetime.now().isoformat()
    await scraper.init()


@app.on_event("shutdown")
async def shutdown():
    await scraper.close()
    cache.close()
