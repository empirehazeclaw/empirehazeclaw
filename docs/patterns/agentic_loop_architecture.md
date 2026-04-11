# 🧠 Agentic Loop Architecture Skill
**Created:** 2026-04-11
**Category:** workflow
**Priority:** CRITICAL

## Research Source
Web Search 2026-04-11: AI agent loop prevention patterns

## Key Insight
**"Plan-and-execute patterns reduce LLM calls by planning upfront rather than reasoning at every step"**
— blogs.oracle.com

## Core Patterns

### 1. Plan-and-Execute (BEST)
```
BEFORE doing anything:
  → Plan all steps first
  → Execute sequentially
  → NO re-planning mid-execution
```

### 2. Caching Pattern
```
After tool use:
  → Cache result
  → Before calling same tool: Check cache
  → If cached: Use cached result
```

### 3. Self-Correction Loop
```
AFTER each step:
  → Did it work?
  → YES: Next step
  → NO: Root cause → Fix → Continue
  → STOP after 3 corrections
```

### 4. Verification before Action
```
BEFORE calling tool:
  → Do I have the right parameters?
  → Is this the right tool?
  → Has this worked before?
```

---

## Implementation

### The Sir HazeClaw Loop (Optimized)
```
┌─────────────────────────────────────────────────────────┐
│                   PLAN PHASE                            │
├─────────────────────────────────────────────────────────┤
│ 1. Task verstehen (was ist das Ziel?)                   │
│ 2. Steps identifizieren (was sind die Teilschritte?)    │
│ 3. Reihenfolge festlegen                                │
│ 4. Ressourcen prüfen (Paths, Tools)                     │
│ 5. Timeline schätzen (< 60s pro Step?)                  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  EXECUTE PHASE                          │
├─────────────────────────────────────────────────────────┤
│ For each step:                                          │
│   1. Execute                                            │
│   2. Verify result                                      │
│   3. If fail → Fix → Continue (max 3 corrections)      │
│   4. If success → Next step                             │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                 VERIFY PHASE                            │
├─────────────────────────────────────────────────────────┤
│ Final check:                                            │
│   - Does result meet goal?                              │
│   - All steps completed?                                │
│   - Document if new pattern found                        │
└─────────────────────────────────────────────────────────┘
```

---

## Anti-Loop Rules

### ❌ VERBOTEN:
- Mid-execution re-planning
- Calling same tool twice without caching
- Retry without root cause analysis
- "Just try again" approach

### ✅ ERLAUBT:
- Plan once, execute fully
- Cache and reuse
- Self-correct with limit (max 3)
- Stop and escalate if stuck

---

## Metrics

**Loop Prevention Score:**
```
(actions_without_loop / total_actions) × 100
```

Target: > 90%

---

## Sources
- https://blogs.oracle.com/developers/what-is-the-ai-agent-loop
- https://developers.openai.com/cookbook/examples/partners/self_evolving_agents

---

*Sir HazeClaw — Agentic Loop Master*
