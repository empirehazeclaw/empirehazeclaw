# System Architecture — Sir HazeClaw
**Updated:** 2026-04-20 16:45 UTC
**Version:** 2.0

---

## 🏗️ System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Sir HazeClaw (CEO)                       │
│                   /workspace/ceo/                           │
└─────────────────┬───────────────────────────────────────────┘
                  │
      ┌───────────┴───────────┐
      ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│  Orchestrator   │     │   Event Bus    │
│  (multi_agent)   │     │  (1040 events) │
└───────┬─────────┘     └────────┬────────┘
        │                        │
        ▼                        ▼
┌─────────────────┐     ┌─────────────────┐
│  Agent Executor │     │   KG Sync      │
│  (Queue-based)  │     │  (learning→KG)  │
└───────┬─────────┘     └─────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│         Specialized Agents             │
│  health_agent | data_agent | research │
└───────────────────────────────────────┘
```

---

## 🔧 Core Components

### 1. Multi-Agent System
- **Orchestrator:** Routes tasks based on capability matching
- **Executor:** Queue-based task execution (60s timeout)
- **Agents:** health (95% SR), data (90%), research (85%)
- **State:** `orchestrator_state.json`

### 2. Learning Loop (v3)
- **Score:** 0.764 (Target: 0.80)
- **Iteration:** 215
- **Validation:** v2 (3/3 tests, ±0.1% error threshold)
- **Success Rate:** 200/205 (97.6%)
- **Location:** `SCRIPTS/automation/learning_loop_v3.py`

### 3. Knowledge Graph
- **Entities:** 210 (after cleanup)
- **Relations:** 647
- **Orphan Rate:** 0% (fixed 2026-04-20)
- **Location:** `ceo/memory/kg/knowledge_graph.json`

### 4. Event Bus
- **Total Events:** 1040
- **Top Types:** agent_completed (827), evolver_completed (59)
- **Consumer:** Internal only (learning_to_kg_sync)
- **Location:** `data/events/events.jsonl`

### 5. Memory System
- **main.sqlite:** 372MB (4024 embeddings)
- **ceo.sqlite:** 84MB (347 chunks)
- **QMD:** 20MB index, BM25 fallback
- **Short-term recall:** 546 entries (after fix)

### 6. Capability Evolver
- **Gene Pool:** 4 types (repair, innovate, optimize, auto)
- **Strategy:** balanced (default)
- **Signal Bridge:** Active
- **Location:** `skills/capability-evolver/`

---

## 📁 Workspace Structure (2026-04-20)

```
workspace/
├── ceo/                    # Main agent workspace
│   ├── memory/            # Memory system
│   │   ├── kg/            # Knowledge Graph
│   │   ├── meta_learning/ # Learning loop state
│   │   └── .dreams/       # Short-term recall
│   ├── scripts/           # Agent scripts
│   └── logs/              # Agent logs
├── SCRIPTS/               # Automation scripts
│   ├── automation/        # Main automation
│   │   ├── learning_loop_v3.py
│   │   ├── health_agent.py
│   │   ├── data_agent.py
│   │   ├── research_agent.py
│   │   └── cron_health_monitor.py
│   └── self_healing/
├── skills/                # 30 skills registered
│   ├── capability-evolver/
│   ├── semantic-search/
│   └── ralph_loop/        # NEW 2026-04-20
├── docs/                  # Documentation
│   ├── SYSTEM_DEEP_DIVE_ENHANCED_PLAN_v2.md
│   ├── EVENT_BUS_CONSUMER_AUDIT.md
│   └── BACKUP_RETENTION_POLICY.md
└── data/                  # Runtime data
    ├── events/           # Event bus
    ├── learning_loop/     # Learning loop data
    └── feedback_queue.json
```

---

## 🔄 System Integration

### Event Flow
```
Cron Trigger → Agent Executor → Task Queue → Orchestrator
                                                    │
                                    ┌───────────────┴───────────────┐
                                    ▼                               ▼
                              health_agent              data_agent / research_agent
                                    │                               │
                                    └───────────┬───────────────────┘
                                                ▼
                                    Learning Loop → KG Sync → Event Bus
```

### Backup Locations (Consolidated)
- `backups/`: Current backup targets
- `ceo/backups/`: Phase backups
- `_archive/`: Old archived backups (>30 days)

---

## 📊 Success Metrics

| Metric | Current | Target |
|--------|----------|--------|
| Learning Score | 0.764 | 0.80 |
| KG Orphan Rate | 0% | <5% |
| Agent Health | 95-90-85% | >90% each |
| Crons Active | 28 | 28 |
| Short-term Recall | 546 | >100 |

---

**Last Updated:** 2026-04-20 16:45 UTC
**Status:** Active ✅
