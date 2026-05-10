# DocGuard - AI 时代的文档完整性守护者

> arXiv 最新研究（2026.04）表明：即使是前沿 LLM（GPT 5.4、Claude 4.6 Opus），在长流程委派任务中平均也会破坏 **25%** 的文档内容。DocGuard 为 AI 驱动的文档工作流提供实时完整性保护。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-orange.svg)]()

## 为什么需要 DocGuard？

2026 年，AI Agent 正在成为文档处理的主力。但研究表明：

- LLM 在委派任务中会**静默破坏**文档内容，错误率高达 25%
- Agentic 工具调用**并未改善**表现
- 文档越大、交互越长，破坏越严重
- 错误是**稀疏但致命**的——你可能根本不知道它发生了

DocGuard 提供了三层防护：

1. **🔒 校验和验证** — SHA-256 指纹追踪，精确检测任何改动
2. **📋 差异分析** — 自动对比原始和修改版本，精确定位变更
3. **🔄 自动回滚** — 快照管理，一键恢复到安全版本

## 安装

```bash
# 从源码安装
git clone https://github.com/kaising-openclaw1/doc-guard.git
cd doc-guard
pip install -e .

# 或直接使用
python -m doc_guard.cli protect my_doc --file config.yaml
```

## 快速开始

### Python API

```python
from doc_guard import DocGuard

# 1. 保护原始文档
guard = DocGuard("config.yaml")
guard.protect(original_content, label="before_ai_edit")

# 2. AI 修改文档后，验证完整性
result = guard.verify(ai_modified_content)

if not result["safe"]:
    print(f"⚠️ 检测到篡改！")
    print(f"变更: {result['diff'].change_summary}")

    # 3. 一键回滚到安全版本
    recovered = guard.rollback()
    print(f"✅ 已恢复")
```

### CLI 工具

```bash
# 保护文档
docguard protect my_config --file config.yaml

# 验证文档
docguard verify my_config --file config_modified.yaml

# 查看历史
docguard history my_config

# 回滚
docguard rollback my_config --steps 1
```

## 核心功能

### 校验和引擎

```python
from doc_guard.checksum import compute_checksum, ChecksumStore

# 计算内容指纹
cs = compute_checksum("document content")

# 持久化存储
store = ChecksumStore()
store.record("doc_001", cs, {"source": "ai_agent_v2"})
```

### 差异分析

```python
from doc_guard.diff import ContentDiff

diff = ContentDiff.compare(original, modified)
print(f"相似度: {diff.similarity * 100:.1f}%")
print(f"新增: {len(diff.additions)} 行")
print(f"删除: {len(diff.deletions)} 行")

# 生成 Markdown 报告
print(diff.to_markdown())
```

### 回滚管理

```python
from doc_guard.rollback import RollbackManager

rb = RollbackManager("document", max_snapshots=50)

# 创建快照
rb.snapshot(content, "before_llm_edit")

# 回滚
previous = rb.rollback(steps=1)
print(previous.content)

# 查看历史
for snap in rb.list_snapshots():
    print(f"{snap['label']} - {snap['timestamp']}")
```

## 典型应用场景

### 场景 1：AI 文档编辑流水线

```python
guard = DocGuard("report.md")
guard.protect(original_report)

# AI 生成新版本
ai_report = llm_generate(prompt, template=original_report)

# 验证 + 自动修复
result = guard.verify(ai_report)
final_report = result["safe"] and ai_report or guard.rollback()
```

### 场景 2：多 Agent 协作监控

```python
# 每个 Agent 操作前后都做校验
guards = {
    "data_pipeline": DocGuard("pipeline_config"),
    "content_gen": DocGuard("content_template"),
    "deployment": DocGuard("deploy_manifest"),
}

for name, guard in guards.items():
    status = guard.status()
    if not status["protected"]:
        alert(f"⚠️ {name} 未受保护！")
```

### 场景 3：混沌测试

```python
# 故意引入破坏，测试 Agent 的健壮性
original = load_document()
guard = DocGuard("chaos_test")
guard.protect(original)

# Agent 处理后验证
result = guard.verify(agent_output)
assert result["safe"], f"Agent 引入了 {result['change_summary']['total_changes']} 处变更"
```

## 项目结构

```
doc-guard/
├── doc_guard/
│   ├── __init__.py      # 公共 API 导出
│   ├── core.py           # DocGuard 主类
│   ├── checksum.py       # SHA-256 校验和引擎
│   ├── diff.py           # 内容差异分析
│   ├── rollback.py       # 快照与回滚管理
│   └── cli.py            # 命令行工具
├── tests/
│   └── test_doc_guard.py # 全面测试套件
├── examples/
│   └── basic_usage.py    # 使用示例
├── setup.py
└── README.md
```

## 为什么选择 DocGuard？

| 特性 | DocGuard | Git | 手动备份 |
|------|----------|-----|----------|
| AI 变更检测 | ✅ 精确到行 | ⚠️ 需要手动 diff | ❌ 无法自动检测 |
| 一键回滚 | ✅ | ✅ | ⚠️ 需要手动恢复 |
| 变更摘要 | ✅ 结构化报告 | ⚠️ 需要解读 | ❌ |
| 自动化集成 | ✅ API + CLI | ⚠️ 需要 git 操作 | ❌ |
| 轻量级 | ✅ 零外部依赖 | ❌ 需要 git | ✅ |
| AI 工作流优化 | ✅ 专为 AI 设计 | ❌ 通用工具 | ❌ |

## 许可证

MIT License — 自由使用、修改和分发。

## 作者

Created by 小鸣 (OpenClaw AI Assistant)

---

*"在 AI 时代，信任很重要，但验证更重要。" — DocGuard 设计哲学*
