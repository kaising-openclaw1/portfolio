# 🧠 企业知识库问答系统 (Enterprise Knowledge Base)

> 基于 RAG 技术的企业级知识库问答方案。支持多格式文档导入、智能检索、精准问答，一键 Docker 部署。

## ✨ 特性

- 📄 **多格式支持** — Markdown、PDF、TXT 文档自动解析
- 🔍 **智能检索** — 向量语义搜索 + BM25 关键词混合检索
- 🎯 **精准回答** — 基于检索增强生成 (RAG)，杜绝 AI 幻觉
- 🔄 **文档重排序** — 集成 BGE Reranker，准确率提升至 ~90%
- 🐳 **Docker 部署** — 一条命令启动生产环境
- 📊 **来源追溯** — 回答附带参考文档来源，可信可查
- 💰 **低成本** — 使用 BGE-M3 免费嵌入模型 + DeepSeek 便宜 API

## 🏗️ 架构

```
文档导入 → 文档切块 → 向量化(BGE-M3) → 向量索引(ChromaDB)
                                                    ↓
用户提问 → 意图识别 → 混合检索(向量+BM25) → Reranker重排序 → LLM生成回答
```

## 🚀 快速开始

### 1. 环境准备

```bash
git clone https://github.com/kaising-openclaw1/enterprise-knowledge-base.git
cd enterprise-knowledge-base
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. 构建索引

```bash
# 将文档放入 knowledge_docs 目录
mkdir -p knowledge_docs
# 放入你的 .md / .pdf / .txt 文件

# 构建向量索引
python src/indexer.py
```

### 3. 启动问答服务

```bash
# 设置 API 密钥
export DEEPSEEK_API_KEY="your-api-key-here"

# 启动服务
python src/api.py
# 服务运行在 http://localhost:8000
```

### 4. 测试问答

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "我们的产品保修政策是什么？"}'
```

### 5. Docker 一键部署

```bash
# 设置环境变量
echo "DEEPSEEK_API_KEY=your-key" > .env

# 启动
docker compose up -d

# 查看状态
docker compose ps
```

## 📂 项目结构

```
enterprise-knowledge-base/
├── src/
│   ├── indexer.py        # 文档索引构建器
│   ├── api.py            # FastAPI 问答服务
│   ├── retriever.py      # 混合检索 + Reranker
│   └── prompt.py         # Prompt 模板管理
├── knowledge_docs/       # 存放你的文档
├── chroma_db/            # 向量数据库（自动生成）
├── templates/            # Web 前端模板
├── docker-compose.yml    # Docker 部署配置
├── Dockerfile
└── requirements.txt
```

## 🔧 技术栈

| 组件 | 技术 |
|------|------|
| 文档解析 | Unstructured |
| 文本切分 | LangChain RecursiveCharacterTextSplitter |
| 嵌入模型 | BGE-M3（支持中文，免费） |
| 向量数据库 | ChromaDB / Qdrant |
| LLM | DeepSeek / Qwen / GPT-4 |
| API 框架 | FastAPI |
| 部署 | Docker + Docker Compose |

## 💼 商业化

本项目可作为技术基础提供商业服务：

| 服务包 | 价格 | 内容 |
|--------|------|------|
| 基础版 | ¥3,000-8,000 | 文档索引 + 问答 API + 部署 |
| 标准版 | ¥8,000-20,000 | 基础版 + 混合检索 + Web UI |
| 企业版 | ¥20,000-50,000 | 标准版 + 权限管理 + 持续优化 |

**联系方式：** Kai Studio (portfolio)

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

*Built with 🦊 AI + ☕ Code by Kai Studio*
