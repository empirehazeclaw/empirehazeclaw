# Ralph Loop — Skill Documentation

> **Version:** 1.0.0  
> **Created:** 2026-04-20  
> **Author:** Sir HazeClaw

## Overview

Ralph Loop = Autonomer AI Agent Loop der iteriert bis alle Tasks fertig sind. Benannt nach Ralph Wiggum (Simpsons).

**Kern-Problem das Ralph löst:** LLMs hören auf wenn sie *denken* sie sind fertig — nicht wenn sie *tatsächlich* fertig sind.

---

## Core Principle

```
Traditional Agent:
  Observation → Reasoning → Acting → [LLM entscheidet: fertig? → EXIT]

Ralph Loop:
  Observation → Reasoning → Acting → [STOP HOOK: fertig? → NEIN → re-inject]
```

---

## 3 Kern-Elemente

| Element | Purpose |
|---------|---------|
| **Clear Task + Completion Criteria** | Verifizierbare Standards (machine-verifiable) |
| **Stop Hook** | Interceptet Exit-Versuche, re-injectet Prompt wenn nicht fertig |
| **Max-Iterations Safety** | Verhindert infinite loops — IMMER setzen |

---

## Architecture

```
Ralph Loop
├── Ralph Marker: <promise>COMPLETE</promise>
├── State File: data/ralph_*_state.json
├── Learnings: memory/ralph_learnings.md
└── Max Iterations: Safety limit
```

---

## Scripts

### Ralph Learning Loop
```
Location:  scripts/ralph_learning_loop.py
Purpose:   Learning Loop Verbesserung → Score 0.80 stabil
Schedule:  09:00 + 18:00 UTC (via cron)
Max Iter:  20
```

**Check Criteria:**
- Score ≥ 0.80
- 3x stable runs

**Workflow:**
1. Run Learning Loop v3
2. Parse score from output/state
3. If stable 3x → `<promise>COMPLETE</promise>`

---

### Ralph Maintenance Loop
```
Location:  scripts/ralph_maintenance_loop.py
Purpose:   System Maintenance bis alle Checks grün
Schedule:  0 */6 * * * (alle 6h via cron)
Max Iter:  10
```

**Check Criteria:**
- 3 Checks: Health, Stagnation, Data Agent
- Alle 3 müssen grün sein
- 2x stable runs

**Checks:**
1. Health Monitor (Gateway, Disk, Memory)
2. Stagnation Detector
3. Data Agent (KG, Scripts, Docs)

**Workflow:**
1. Run Health Check
2. Run Stagnation Check
3. Run Data Agent
4. Wenn alle OK 2x → `<promise>COMPLETE</promise>`

---

### Ralph Loop Adapter (Generic)
```
Location:  skills/ralph_loop/scripts/ralph_loop_adapter.py
Purpose:   Generic adapter für eigene Ralph Loops
Usage:     Manuell für eigene Tasks
```

**Usage:**
```bash
# Check-only mode
python3 scripts/ralph_loop_adapter.py check --check "python3 score_checker.py"

# Full Ralph Loop
python3 scripts/ralph_loop_adapter.py loop <task_name> \
    --check "python3 score_checker.py" \
    --action "python3 do_work.py" \
    --max-iterations 20

# Show learnings
python3 scripts/ralph_loop_adapter.py learnings
```

---

## Crons

| Cron | Schedule | Mode | Description |
|------|----------|------|-------------|
| Ralph Learning Loop | `0 9,18 * * *` | announce | Learning Verbesserung → 0.80 |
| Ralph Maintenance Loop | `0 */6 * * *` | silent | System Maintenance |

---

## Learnings File

`memory/ralph_learnings.md` — persistent learnings zwischen iterations

Format:
```markdown
- [2026-04-20 07:34] [category] finding description
```

Categories: `improvement`, `issue`, `error`, `success`, `safety`

---

## Completion Promise

`<promise>COMPLETE</promise>` — exact string signal

- Stop Hook sucht nach diesem String
- Wenn gefunden → Loop beendet
- Exact string matching (kein smart detection)

---

## Test Results (2026-04-20)

### Ralph Learning Loop
```
Status:     READY (waiting for scheduled run)
Score:      0.767
Iteration:  204
Target:     0.80
Stable:     0/3 runs
```

### Ralph Maintenance Loop
```
Status:     ✅ TESTED AND PASSING
Run 1:      3/3 checks OK, stable 1/2
Run 2:      3/3 checks OK, stable 2/2
Output:     <promise>COMPLETE</promise>
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Lösung |
|--------------|---------|--------|
| Kein max-iterations | Infinite loop risk | IMMER setzen |
| Vage completion criteria | Loop weiß nicht wann fertig | Machine-verifiable criteria |
| Zu große Stories/Tasks | Context overflow | Right-size: einer pro iteration |
| Kein feedback loop | Fehler werden nicht erkannt | Typecheck + Tests + CI |

---

## References

- [Alibaba Cloud: ReAct to Ralph Loop](https://www.alibabacloud.com/blog/from-react-to-ralph-loop-a-continuous-iteration-paradigm-for-ai-agents_602799)
- [GitHub: snarktank/ralph](https://github.com/snarktank/ralph)
- [Vercel Labs: ralph-loop-agent](https://github.com/vercel-labs/ralph-loop-agent)
- [Agent Factory: Ralph Wiggum Loop](https://agentfactory.panaversity.org/docs/General-Agents-Foundations/general-agents/ralph-wiggum-loop)
- [ASDLC.io: Ralph Loop Pattern](https://asdlc.io/patterns/ralph-loop/)

---

*Zuletzt aktualisiert: 2026-04-20 07:35 UTC*
