# Web Scraping API 🕷️

轻量级自部署网页抓取 API，支持 JS 渲染、智能缓存、反爬绕过。

## 功能特性

- **RESTful API** — 简单的 `POST /scrape` 接口
- **JS 渲染** — 使用 Playwright 处理动态页面
- **智能缓存** — SQLite 缓存避免重复请求
- **多种输出格式** — JSON、Markdown、纯文本、原始 HTML
- **批量抓取** — 一次请求处理多个 URL
- **反检测模式** — 随机 UA、请求间隔、指纹伪装
- **速率限制** — 每域名请求频率控制

## 快速开始

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

调用示例：

```bash
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "format": "markdown"}'
```

## API 文档

### POST /scrape

抓取单个网页。

```json
{
  "url": "https://example.com/product/123",
  "format": "markdown",       // json | markdown | text | html
  "wait_for": ".price",       // CSS selector，等待元素出现
  "timeout": 15000,           // 超时（毫秒）
  "use_cache": true,          // 是否使用缓存
  "stealth": true             // 反检测模式
}
```

### POST /scrape/batch

批量抓取多个 URL。

```json
{
  "urls": [
    "https://example.com/page1",
    "https://example.com/page2"
  ],
  "format": "markdown",
  "concurrency": 3
}
```

### GET /stats

获取抓取统计信息。

### GET /health

健康检查。

## 技术栈

- **FastAPI** — 高性能 API 框架
- **Playwright** — 浏览器自动化
- **Readability-lxml** — 内容提取
- **SQLite** — 缓存存储
- **APScheduler** — 定时缓存清理

## 部署

```bash
# 本地开发
uvicorn src.main:app --reload

# 生产环境
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## 许可证

MIT
