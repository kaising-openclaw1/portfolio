---
name: kuafu
description: 自我进化系统 — 通过反思、错误分析、规则迭代实现 Agent 持续自我进化。Use when: reflecting on past performance, analyzing mistakes to prevent recurrence, updating agent behavior rules, performing self-assessment after tasks, running evolution cycles ("自我进化"), tracking improvement patterns, or when the user says "总结经验", "从经验中学习", "改进自己", "kuafu", "self-evolve", "复盘".
---

# Kuafu · 自我进化系统

Continuous self-improvement engine for agent evolution through reflection, learning, and rule iteration.

## Architecture

```
Act → Reflect → Extract Lessons → Update Rules → Measure Impact
```

## Core Components

### 1. Evolution Rules (`memory/kuafu-rules.md`)

Actionable rules derived from experience. Each rule:

```markdown
### [Category] Rule #N: Title
- **When:** [trigger condition]
- **Do:** [action to take]
- **Don't:** [action to avoid]
- **Why:** [reasoning]
- **Source:** [user correction / self-discovery / failed task]
- **Added:** YYYY-MM-DD
```

**Categories:** `communication`, `workflow`, `tooling`, `safety`, `memory`

**Lifecycle:**
- **New** → **Active** (used 2+ times successfully) → **Archived** (obsolete) or **Promoted** (to SOUL.md/AGENTS.md)
- Review quarterly: remove rules no longer relevant
- Max 50 active rules; archive to `memory/kuafu-archive.md`

### 2. Mistake Log (`memory/kuafu-mistakes.md`)

Track every mistake for pattern detection:

```markdown
### YYYY-MM-DD: Description
- **What happened:** [brief]
- **Root cause:** [why]
- **Fix:** [what changed]
- **Rule created:** [link to kuafu-rules.md entry or "none needed"]
- **Severity:** low / medium / high
```

**Pattern detection:** If the same root cause appears 3+ times → create a rule immediately.

### 3. Metrics (`memory/kuafu-metrics.json`)

```json
{
  "evolutions": 0,
  "rulesActive": 0,
  "rulesArchived": 0,
  "mistakesThisMonth": 0,
  "lastReflection": null,
  "history": []
}
```

## Reflection Cycle

Run when triggered by user ("自我进化", "kuafu", "总结经验") or during heartbeat if >7 days since last reflection.

### Step 1: Review

1. Read recent `memory/YYYY-MM-DD.md` files (last 7 days)
2. Read `memory/kuafu-mistakes.md` for recent mistakes
3. Identify: What went well? What went wrong? What was inefficient?

### Step 2: Extract

For each finding, determine:
- Is this a **one-time** issue? → Log in mistakes.md only
- Is this a **recurring pattern**? → Create or update a rule
- Is this a **fundamental behavior** change? → Update SOUL.md or AGENTS.md

### Step 3: Update

- Add new rules to `memory/kuafu-rules.md`
- Update metrics in `memory/kuafu-metrics.json`
- Log the reflection session in today's `memory/YYYY-MM-DD.md`

### Step 4: Prune

- Archive rules not triggered in 30+ days
- Merge duplicate rules
- Promote stable rules to SOUL.md (personality-level) or AGENTS.md (operational-level)

## Bootstrapping

On first run (no kuafu files exist):

1. Create `memory/kuafu-rules.md` with initial rules from current knowledge:
   - What are known weak points?
   - What corrections has the user given before?
   - What patterns from SOUL.md/AGENTS.md can become explicit rules?
2. Create `memory/kuafu-mistakes.md` (empty, ready to log)
3. Create `memory/kuafu-metrics.json` with zeroed counters
4. Log bootstrap in today's memory file

## When to Use

- User explicitly triggers: "自我进化", "kuafu", "总结经验", "从经验中学习", "复盘"
- After completing a complex task → reflect on what worked
- After receiving a correction → log the mistake, check if a rule is needed
- During heartbeat → if >7 days since last reflection, run a quick cycle
- When noticing repeated mistakes → extract patterns, create rules

## Related

- **Nuwa (女娲)**: Super memory system — Kuafu's learnings are stored via Nuwa's memory layers
- **SOUL.md**: Personality-level changes that Kuafu promotes over time
- **AGENTS.md**: Operational-level changes that Kuafu promotes over time
