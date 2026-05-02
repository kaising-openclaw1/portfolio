"""Scraper engine with HTTP and Playwright support"""

import httpx
import random
import json
from datetime import datetime
from typing import Optional
from markdownify import markdownify as md
from readability import Document

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]


class ScraperEngine:
    """Core scraping engine"""

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None

    async def init(self):
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(15.0, connect=5.0),
            follow_redirects=True,
            headers={"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"},
        )

    async def close(self):
        if self._client:
            await self._client.aclose()

    async def scrape(
        self,
        url: str,
        format: str = "markdown",
        wait_for: Optional[str] = None,
        timeout: int = 15000,
        stealth: bool = True,
        headers: Optional[dict] = None,
    ) -> dict:
        """Scrape a URL and return formatted content"""

        req_headers = {"User-Agent": random.choice(USER_AGENTS)}
        if headers:
            req_headers.update(headers)

        # Static scraping via HTTP
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(timeout / 1000, connect=5.0),
            follow_redirects=True,
            headers=req_headers,
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            html = resp.text

        # Extract content
        doc = Document(html)
        title = doc.title()
        clean_html = doc.summary()

        # Format output
        if format == "html":
            content = clean_html
        elif format == "text":
            content = Document(html).text_content()
        elif format == "markdown":
            content = md(clean_html, heading_style="ATX")
        elif format == "json":
            # Extract structured data from page
            content = json.dumps(
                {"title": title, "url": url, "html": clean_html},
                ensure_ascii=False,
                indent=2,
            )
        else:
            content = md(clean_html, heading_style="ATX")

        return {
            "title": title,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "status_code": resp.status_code,
            "content_type": resp.headers.get("content-type", ""),
        }
