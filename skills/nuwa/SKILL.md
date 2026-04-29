---
name: nuwa
description: 超级记忆系统 — 多层记忆管理、智能编码、语义检索、知识关联、记忆巩固。Use when: managing agent memories, searching past experiences, storing important context, building knowledge connections, consolidating daily notes into long-term memory, creating memory indexes, organizing memory files, or anything involving structured memory operations beyond basic file read/write. Triggers: "记住这个", "memory", "记忆", "搜索记忆", "recall", "memory search", "整理记忆", "consolidate memory", "知识图谱", "knowledge graph", "nuwa", "女娲".
---

# Nuwa · 超级记忆系统

Multi-layer memory management for persistent agent intelligence. Three layers, smart encoding, semantic retrieval, and knowledge linking.

## Memory Architecture

```
Layer 1: Working Memory    → memory/YYYY-MM-DD.md (daily notes, raw events)
Layer 2: Long-Term Memory  → MEMORY.md (curated insights, distilled knowledge)
Layer 3: Knowledge Index   → memory/index.md (searchable topic/person/project index)
```

## Core Operations

### Encode — Write It Down

Never rely on "mental notes." All significant information goes to files immediately.

**Daily notes** (`memory/YYYY-MM-DD.md`):
- Raw logs: events, decisions, conversations, outcomes
- Timestamp key actions: `### HH:MM - Event`
- Tag important items: `!important`, `!todo`, `!decision`
- Append throughout the day; don't wait for a summary

**Long-term memory** (`MEMORY.md`):
- Curated, distilled insights from daily notes
- Organize by topic sections with `##` headers
- Include: people preferences, project status, lessons learned, patterns
- Update during heartbeats or when explicitly asked
- Keep under 200 lines; prune aggressively

### Retrieve — Smart Search

Tiered retrieval approach:

1. **memory_search** with focused query first
2. **memory_get** to pull specific line ranges from results
3. Read daily files directly if you know the date
4. Check `memory/index.md` for topic-based navigation

**Search strategies:**
- Semantic queries: `memory_search("user timezone preference")` not `memory_search("timezone")`
- Cross-reference: search MEMORY.md for context, daily files for details
- Temporal: if approximate date is known, read that day's file directly

### Consolidate — Distill Daily → Long-Term

Every few days (during heartbeat or idle time):

1. Read recent `memory/YYYY-MM-DD.md` files
2. Extract: decisions, lessons, preferences, project updates
3. Merge into `MEMORY.md` under relevant sections
4. Remove outdated info from MEMORY.md
5. Update `memory/index.md` with new topics/people

**Rules:**
- Distill, don't copy — extract the essence
- Archive old daily files that have been fully consolidated
- When MEMORY.md grows too large, split into `memory/topics/*.md`

### Connect — Knowledge Index

Maintain `memory/index.md` as a lightweight topic index:

```markdown
## People
- 大凯 → MEMORY.md#L5, memory/2026-03-27.md

## Projects
- 财务自由 → MEMORY.md#L12, memory/2026-03-26.md
```

Update during consolidation. Keep lean — only entries with multiple references.

## Memory Lifecycle

```
Capture → Organize → Distill → Connect → Prune
  ↓          ↓          ↓         ↓        ↓
 daily     tag +     merge to   update   archive
 notes    timestamp  MEMORY.md  index    old files
```

## Advanced Patterns

See [references/memory-patterns.md](references/memory-patterns.md) for:
- Associative memory linking (connecting related concepts across files)
- Temporal memory queries (finding events by date range)
- Memory conflict resolution (handling contradictory stored information)
- Emergency recall (maximum-context recovery for critical decisions)

## When to Use

- Storing important information that must persist across sessions
- Searching for past decisions, preferences, or events
- Consolidating daily notes into long-term memory
- Building and maintaining a knowledge index
- Organizing memory files when they get messy
- Cross-referencing information across multiple memory files
