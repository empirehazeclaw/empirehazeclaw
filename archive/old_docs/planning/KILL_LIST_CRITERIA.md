# Agent Kill List Criteria

## Overview
- **Total agents scanned:** 281
- **Goal:** Reduce to ≤68 agents (50%+ reduction)
- **Generated:** 2026-03-28

---

## SECTION A: KEEP Criteria (ALL must be true)

An agent is kept if **ALL** of the following are true:

| # | Criterion | How to Verify |
|---|-----------|---------------|
| 1 | **Active in last 30 days** | Has log entries or call records since 2026-02-28 |
| 2 | **Unique functionality** | No other agent does the same task |
| 3 | **No critical errors** | Runs without crashing / no error logs |
| 4 | **Properly documented** | Has docstring or comments explaining purpose |
| 5 | **>100 lines of code** OR delegating to a real subdirectory agent | Stub files <100 lines = candidate for merge |

---

## SECTION B: MERGE Criteria (ANY = merge with similar)

An agent is a MERGE candidate if **ANY** of the following are true:

| # | Criterion | Target |
|---|-----------|--------|
| 1 | **Overlap** | Another agent has same/nearly same functionality |
| 2 | **Subset** | This agent does less than another (e.g., agent has 100 lines vs 500 lines) |
| 3 | **Tiny + no unique logic** | <100 lines of code and just calls another script |
| 4 | **_llm.py variant** | Older LLM wrapper version of a main agent |
| 5 | **Stub/wrapper** | Only imports and calls a subdirectory agent |

---

## SECTION C: KILL Criteria (ANY = delete)

An agent is KILLED if **ANY** of the following are true:

| # | Criterion | Evidence |
|---|-----------|----------|
| 1 | **Never called** | No logs exist or all logs are empty (0 bytes) |
| 2 | **Complete duplicate** | Another agent with identical code/functionality exists |
| 3 | **Broken** | Causes errors / exceptions when run |
| 4 | **Deprecated version** | Has `_v1`, `_v2`, `_old`, `_deprecated` in name |
| 5 | **Irrelevant vertical** | Niche-specific (gardening, petcare, agriculture) not in business scope |
| 6 | **3-line wrapper** | File is <10 lines and only does `exec` or `subprocess.run` |
| 7 | **Replaced by consolidated version** | An equivalent exists in `consolidated_agents.py` |

---

## Quick Decision Tree

```
agent exists?
│
├─ No logs / empty logs → KILL
├─ <10 lines (wrapper) → KILL
├─ Has _llm.py variant → MERGE into main
├─ Duplicate name pattern (2+ agents) → KEEP best, MERGE rest
├─ Irrelevant niche (gardening, petcare, etc.) → KILL
├─ Has _v1/_v2/_old in name → KILL
├─ <100 lines, no unique logic → KILL or MERGE
├─ Overlaps another agent → MERGE into more complete version
└─ Active + unique + working → KEEP
```

---

## Special Cases

### Infrastructure Agents (ALWAYS KEEP)
- `master_orchestrator.py` - Main orchestrator
- `orchestrator.py` - Task routing
- `dag_executor.py` - DAG execution
- `agent_registry.py` - Registry
- `reporting.py` - Reporting

### Deprecated Version Pattern
These are ALWAYS KILL (replaced by consolidated_agents.py):
- `cold_outreach_llm.py` → replaced by `cold_outreach_agent.py`
- `lead_qualifier_llm.py` → replaced by `lead_qualifier_agent.py`
- `content_production_llm.py` → replaced by `content_production_agent.py`
- `sales_executor_llm.py` → replaced by `sales_executor_agent.py`

### Tiny Stubs (ALWAYS KILL)
- `gardening_agent.py` (3 lines - just bash exec)
- `petcare_agent.py` (3 lines - just bash exec)
- `photography_agent.py` (3 lines - just bash exec)
- `home_agent.py` (10 lines - trivial wrapper)
- `support_agent.py` (19 lines - minimal stub)
- `translation_agent.py` (10 lines - minimal stub)

### Irrelevant Niche Agents (ALWAYS KILL)
These verticals don't match EmpireHazeClaw's business:
- `agriculture/` directory
- `automotive/` directory  
- `civic/` directory
- `construction/` directory
- `education/` directory (except tutor_agent.py if used)
- `energy/` directory
- `entertainment/` directory
- `fitness/` directory
- `food/` directory
- `gardening/` directory
- `government/` directory
- `grant/` directory
- `healthcare/` directory
- `insurance/` directory
- `legal/` directory
- `manufacturing/` directory
- `hospitality/` directory
