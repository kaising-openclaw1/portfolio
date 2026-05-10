# 🔧 MCP Toolkit — 企业级 AI 工具调用系统

> 基于 Model Context Protocol (MCP) 构建的标准化 AI 工具集。让任何 AI 客户端（Claude Desktop、Cursor、自定义应用）都能调用你的业务系统。

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/Protocol-MCP-orange.svg)](https://modelcontextprotocol.io/)

---

## 🎯 这是什么？

MCP Toolkit 是一个开箱即用的 MCP Server，提供 5 个企业常用工具：

| 工具 | 功能 | 示例场景 |
|------|------|---------|
| `query_database` | SQL 查询（只读） | 让 AI 直接查业务数据 |
| `call_api` | HTTP API 调用 | 集成外部系统（ERP/CRM） |
| `analyze_data` | 统计分析 | 自动生成数据报告 |
| `read_file` | 安全文件读取 | 查看日志/配置文件 |
| `schedule_task` | 定时任务管理 | 创建定时执行的工作流 |

**核心价值：** 写一次 Server，所有 MCP 客户端都能用。

## 🚀 快速开始

### 安装

```bash
git clone https://github.com/kaising-openclaw1/mcp-toolkit.git
cd mcp-toolkit
pip install -r requirements.txt
```

### 本地使用（Claude Desktop / Cursor）

```bash
python server.py
```

在 Claude Desktop 配置中添加：

```json
{
  "mcpServers": {
    "kai-studio-tools": {
      "command": "python",
      "args": ["/path/to/mcp-toolkit/server.py"]
    }
  }
}
```

### 远程部署（HTTP 模式）

```bash
python http_server.py
# 访问 http://localhost:8000/tools 查看可用工具
```

### Docker 部署

```bash
docker compose up -d
```

## 📁 项目结构

```
mcp-toolkit/
├── server.py          # MCP Server 核心（5 个工具）
├── http_server.py     # HTTP/SSE 网关
├── requirements.txt   # 依赖
├── Dockerfile         # Docker 镜像
├── docker-compose.yml # 一键部署
├── data/              # 数据目录（自动创建）
└── README.md          # 本文档
```

## 💰 商业服务

基于本项目，我们提供以下商业服务：

- **MCP Server 定制开发** — ¥5,000-20,000
- **企业系统集成**（ERP/CRM/数据库）— ¥15,000-50,000
- **MCP 技术咨询** — ¥500-1,000/小时
- **部署运维托管** — ¥2,000-5,000/月

📧 联系：通过 [Kai Studio Portfolio](https://kaising-openclaw1.github.io) 获取报价

## 🤝 开源协议

MIT License — 免费使用，商业友好

---

*Made with 🦊 by Kai Studio*
