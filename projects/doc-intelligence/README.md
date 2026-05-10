# 📄 Doc Intelligence — 智能文档处理工具

> 一键完成文档摘要、翻译、格式转换、关键词提取。企业办公自动化利器。

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 功能特性

| 功能 | 说明 | 适用场景 |
|------|------|----------|
| **智能摘要** | AI 自动生成长文档摘要 | 合同/报告快速阅读 |
| **多语言翻译** | 中英日韩互译 | 跨境业务文档 |
| **格式转换** | PDF ↔ Word ↔ Markdown | 文档标准化 |
| **关键词提取** | TF-IDF + TextRank 双引擎 | SEO / 标签生成 |
| **批量处理** | 文件夹级批量操作 | 企业文档流水线 |
| **API 服务** | FastAPI REST 接口 | 系统集成 |

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/kaising-openclaw1/doc-intelligence.git
cd doc-intelligence

# 安装依赖
pip install -r requirements.txt

# 可选：安装 OCR 引擎（用于扫描件处理）
pip install pytesseract
# macOS: brew install tesseract
# Ubuntu: sudo apt install tesseract-ocr tesseract-ocr-chi-sim
```

### 基本使用

```python
from doc_intelligence import DocumentProcessor

# 初始化处理器
processor = DocumentProcessor(
    llm_api_key="your-api-key",        # OpenAI / DeepSeek / 其他兼容接口
    llm_base_url="https://api.deepseek.com/v1",  # LLM API 地址
    llm_model="deepseek-chat"           # 模型名称
)

# 1. 智能摘要
summary = processor.summarize("contract.pdf", max_length=500)
print(summary)

# 2. 翻译文档
translated = processor.translate("report.pdf", target_lang="en")
print(translated)

# 3. 格式转换
processor.convert("input.pdf", output_format="markdown")
# 输出: input.md

# 4. 关键词提取
keywords = processor.extract_keywords("article.docx", top_k=10)
print(keywords)

# 5. 批量处理
results = processor.batch_process(
    input_dir="./documents",
    operations=["summarize", "keywords"],
    output_dir="./results"
)
```

### CLI 命令行

```bash
# 摘要
doc-intel summarize contract.pdf --max-length 500

# 翻译
doc-intel translate report.pdf --target en

# 转换格式
doc-intel convert input.pdf --format markdown

# 提取关键词
doc-intel keywords article.docx --top-k 10

# 批量处理
doc-intel batch ./docs --ops summarize,keywords --output ./results
```

### API 服务

```bash
# 启动 API 服务
doc-intel serve --host 0.0.0.0 --port 8000

# 或直接运行
python -m doc_intelligence.server
```

API 端点：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/summarize` | POST | 文档摘要 |
| `/api/translate` | POST | 文档翻译 |
| `/api/convert` | POST | 格式转换 |
| `/api/keywords` | POST | 关键词提取 |
| `/api/batch` | POST | 批量处理 |
| `/api/health` | GET | 健康检查 |

## 📁 项目结构

```
doc-intelligence/
├── doc_intelligence/
│   ├── __init__.py
│   ├── processor.py          # 核心处理引擎
│   ├── llm_client.py         # LLM API 客户端
│   ├── pdf_handler.py        # PDF 解析
│   ├── docx_handler.py       # Word 文档处理
│   ├── md_handler.py         # Markdown 处理
│   ├── keywords.py           # 关键词提取
│   ├── translator.py         # 翻译模块
│   ├── summarizer.py         # 摘要生成
│   ├── batch.py              # 批量处理
│   ├── server.py             # FastAPI 服务
│   └── cli.py                # 命令行入口
├── templates/
│   ├── api_doc.html          # API 文档模板
│   └── report.html           # 报告生成模板
├── examples/
│   ├── basic_usage.py        # 基础使用示例
│   └── batch_example.py     # 批量处理示例
├── tests/
│   ├── test_processor.py
│   └── test_api.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🔧 技术栈

- **LLM 集成**: OpenAI 兼容 API（支持 DeepSeek、通义千问、本地模型）
- **PDF 解析**: PyMuPDF (fitz) + pdfplumber
- **Word 处理**: python-docx
- **OCR**: Tesseract（可选）
- **关键词提取**: jieba + TF-IDF + TextRank
- **API 框架**: FastAPI + Uvicorn
- **容器化**: Docker + docker-compose

## 💼 商业应用场景

1. **律所合同审查** — 快速提取合同要点，标记关键条款
2. **跨境贸易** — 批量翻译采购合同、报关文件
3. **学术研究** — 论文摘要生成，文献关键词提取
4. **企业内审** — 自动摘要季度报告，生成管理层摘要
5. **内容运营** — 长文转短视频脚本，多语言内容发布

## 📈 定价参考

| 部署方式 | 价格区间 | 说明 |
|----------|----------|------|
| SaaS 订阅 | ¥299-999/月 | 按文档量计费 |
| 私有部署 | ¥8,000-20,000 | 一次性 + 年维护费 |
| 定制开发 | ¥15,000-50,000 | 根据需求定制 |

## 📄 License

MIT License — 详见 [LICENSE](LICENSE)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系

- 项目主页: github.com/kaising-openclaw1/doc-intelligence
- 技术支持: Kai Studio
