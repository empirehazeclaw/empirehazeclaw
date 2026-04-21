# Learnings Service — Unified Learning Feedback API
================================================

**Status:** ✅ IMPLEMENTED (2026-04-21)
**Location:** `SCRIPTS/automation/learnings_service.py`

## Was es macht

Single API für alle Systeme zum Lesen/Schreiben von Learnings.
Implementiert **closed-loop learning**: Learn → Sync → Use → Learn

## Architektur

```
                    ┌─────────────────┐
                    │    Learnings    │
                    │    Service     │
                    │  (Single API)  │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │  Ralph   │      │   Meta    │      │ Capability│
    │ Learning │      │ Learning  │      │ Evolver  │
    └──────────┘      └──────────┘      └──────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                    ┌────────▼────────┐
                    │       KG        │
                    │   (Persistent)  │
                    └─────────────────┘
```

## Usage

```python
from learnings_service import LearningsService
ls = LearningsService()

# Recording
ls.record_learning(
    source="Ralph Learning",
    category="success",
    learning="Higher learning rate improves score",
    context="score_optimization",
    strategy="adaptive_lr",
    outcome="success"
)

# Query for decisions
insights = ls.get_strategy_insights()

# Get agent-specific learnings
ctx = ls.get_agent_context("Sir HazeClaw")

# Get learnings for task
task_ctx = ls.get_context_for_task("pattern_matching")
```

## Core Methods

| Method | Description |
|--------|-------------|
| `record_learning()` | Record a new learning |
| `get_relevant_learnings()` | Get learnings by filters |
| `get_strategy_insights()` | Get strategy effectiveness rankings |
| `get_agent_context()` | Get learnings for a specific agent |
| `get_context_for_task()` | Get learnings for a task type |
| `mark_learning_used()` | Mark learning as used |
| `provide_feedback()` | Feedback on learning usefulness |

## Integrations

### ✅ Already Integrated
- `Ralph Learning Loop` — Records learnings
- `Meta Learning Controller` — Uses learnings for pattern weights
- `Sir HazeClaw` — Uses learnings via `sir_hazeclaw_learnings.py`

### 🔄 To Integrate
- `Capability Evolver` — Should query learnings for gene decisions
- `Self-Improver` — Should use learnings for code improvements
- `Health Monitor` — Should record learnings from incidents

## Data Structure

```json
{
  "recent": [
    {
      "id": "lrn_20260421_124047_0",
      "source": "Ralph Learning",
      "category": "success",
      "learning": "Score improved when pattern diversity is high",
      "context": "pattern_matching",
      "strategy": "diversity",
      "outcome": "success",
      "timestamp": "2026-04-21T12:40:47",
      "used": false,
      "useful": null
    }
  ],
  "by_category": {"success": ["lrn_..."]},
  "by_context": {"pattern_matching": ["lrn_..."]},
  "by_strategy": {"diversity": ["lrn_..."]},
  "strategy_effectiveness": {"diversity": 1, "adaptive_lr": 1}
}
```

## Strategy Effectiveness

Strategies werden getrackt basierend auf Outcomes:

| Outcome | Effect on Strategy Score |
|---------|------------------------|
| success | +1 |
| failure | -1 |

**Top Strategies:**
```python
# Example output
{
  "top_strategies": [
    {"strategy": "diversity", "score": 3, "verdict": "HIGHLY_EFFECTIVE"},
    {"strategy": "adaptive_lr", "score": 2, "verdict": "EFFECTIVE"}
  ]
}
```

## Cron Jobs

| Job | Schedule | Purpose |
|-----|----------|---------|
| Sir HazeClaw Learnings Review | 0 9,18 * * * | Review learnings twice daily |

## Learnings Categories

| Category | Meaning |
|----------|---------|
| success | Action succeeded |
| failure | Action failed |
| pattern | Pattern discovered |
| insight | Important insight |
| fix | Fix applied |
| bug | Bug identified |

## Learnings Contexts

| Context | Used By |
|---------|---------|
| pattern_matching | Learning Loop, Meta Learning |
| score_optimization | Learning Loop, Ralph |
| evolution | Capability Evolver |
| cron_health | Health Monitor |
| event_bus | Event Bus |
| Ralph | Ralph Learning |
| maintenance | Ralph Maintenance |

## Files

| File | Purpose |
|------|---------|
| `SCRIPTS/automation/learnings_service.py` | Main API |
| `SCRIPTS/automation/sir_hazeclaw_learnings.py` | My personal learnings agent |
| `data/learnings/index.json` | Learnings index |
| `ceo/memory/ralph_learnings.md` | Ralph's legacy learnings (migrated) |

## Stats (2026-04-21)

- **Total Learnings:** 34
- **Strategies Tracked:** 4
- **Agents Using:** 3 (Ralph, Meta, Sir HazeClaw)
- **Crons:** 1 (Daily Review)

---

_Last Updated: 2026-04-21 12:54 UTC_
