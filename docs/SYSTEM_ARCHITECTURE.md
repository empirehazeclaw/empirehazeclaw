# 🏛️ SYSTEM ARCHITECTURE — DEEP ANALYSIS

**Erstellt:** 2026-04-12 06:52 UTC
**Version:** 2.0
**Status:** ✅ Documented

---

## 🎯 EXECUTIVE SUMMARY

Sir HazeClaw ist ein **autonomer KI-Agent** auf Basis von OpenClaw, der kontinuierlich lernt, sich verbessert und automatisch operative Aufgaben ausführt.

| Component | Tech | Status |
|-----------|------|--------|
| **Runtime** | OpenClaw (Node.js) | ✅ Running |
| **Agent** | CEO (Python + Node) | ✅ Active |
| **Model** | MiniMax M2.7 | ✅ Primary |
| **Memory** | KG + SQLite + Files | ✅ Hybrid |
| **Crons** | 18 OpenClaw + 1 System | ✅ Scheduled |

---

## 🏗️ SYSTEM LAYERS

```
┌─────────────────────────────────────────────────────────────┐
│  TIER 4: USER INTERFACE                                     │
│  Telegram (DM), Gateway Dashboard, CLI                      │
├─────────────────────────────────────────────────────────────┤
│  TIER 3: AGENT / ORCHESTRATION                             │
│  OpenClaw CEO Agent + Cron Scheduler + Skills               │
├─────────────────────────────────────────────────────────────┤
│  TIER 2: MEMORY / KNOWLEDGE                                │
│  ┌─────────────┬──────────────┬─────────────────────────┐ │
│  │ KG (JSON)   │ SQLite (Vec) │ Files (Markdown)         │ │
│  │ 249 entities│ 191 chunks  │ 33 memory files          │ │
│  │ 1085 rels   │ FTS + Vec   │ Daily + Permanent        │ │
│  └─────────────┴──────────────┴─────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  TIER 1: INFRASTRUCTURE                                     │
│  Linux + Node.js + Python + systemd + cron               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 PACKAGE.LAYERS

### Tier 1: Infrastructure
```
/home/clawbot/
├── .openclaw/
│   ├── openclaw.json          # Main config
│   ├── agents/                # Agent auth + sessions
│   ├── workspace/             # Agent workspace (linked)
│   └── logs/                 # System logs
├── Workspace:
│   /home/clawbot/.openclaw/workspace/  # 84 directories
└── Services:
    • systemd (openclaw-gateway)
    • Node.js runtime
    • Python 3 environment
```

### Tier 2: Memory Systems (DUAL MEMORY ARCHITECTURE)

| System | Location | Type | Purpose | Size |
|-------|----------|------|---------|------|
| **Knowledge Graph** | `core_ultralight/memory/` | JSON | Explizite Learnings, Entities, Patterns | 1.1 MB |
| **Memory-Core SQLite** | `~/.openclaw/memory/` | SQLite | Vector Embeddings, FTS, Recall | 380 MB |
| **File Memory** | `memory/` | Markdown | Tägliche Logs, Notes, Insights | varies |
| **Session Memory** | `memory/sessions/` | JSON | Kurzlebige Session-Transcripts | varies |

**Memory Flow:**
```
Short-Term (Session)
    ↓ [Every 30min heartbeat]
Short-Term File Memory (memory/YYYY-MM-DD.md)
    ↓ [Nightly Dreaming 04:40 UTC]
Long-Term Memory (KG + SQLite)
```

### Tier 3: Agent Orchestration

```
CEO AGENT (Sir HazeClaw)
├── OpenClaw Runtime (Node.js)
│   └── Gateway + RPC + Cron Scheduler
├── Python Scripts (97 files)
│   ├── Learning Loop: learning_coordinator.py, continuous_improver.py
│   ├── Health: health_check.py, cron_watchdog.py
│   ├── Memory: MEMORY_API.py, kg_updater.py
│   └── Utility: auto_backup.py, gateway_recovery.py
├── Skills (16 directories)
│   ├── capability-evolver   # Self-improvement testing
│   ├── self-improvement    # Autonomous learning
│   ├── system-manager      # System operations
│   └── research           # Web research
└── Cron Jobs (18 active)
    ├── Gateway Recovery: alle 5 min
    ├── Learning Coordinator: stündlich
    ├── Health Check: alle 3h
    ├── Memory-Core Dreaming: 04:40 UTC
    └── Innovation Research: 14:00 UTC
```

---

## 🧠 KNOWLEDGE GRAPH ARCHITECTURE

### Structure
```json
{
  "entities": {
    "entity_id": {
      "type": "learning|error_pattern|research|improvement|...",
      "category": "...",
      "facts": [...],
      "hypotheses": [...],
      "created": "ISO8601",
      "last_accessed": "ISO8601",
      "access_count": 0
    }
  },
  "relations": [
    {"from": "...", "to": "...", "type": "relates_to|implements|uses|..."}
  ]
}
```

### Entity Types
| Type | Count | Purpose |
|------|-------|---------|
| learning | ~50 | Extracted learnings |
| error_pattern | 20 | Error handling patterns |
| success_pattern | 19 | Successful approaches |
| research | ~30 | Research insights |
| improvement | ~15 | Improvement experiments |
| dream_insight | 0 | (Deleted - was custom script) |
| category | ~10 | Anchor entities |

### Quality Issues
- **Before:** 65 orphans (entities without relations)
- **After:** 3 orphans (now connected via category anchors)
- **Relation Quality:** 68.7% low-quality (`shares_category`)
- **Relation Types:** `related_to`, `implements`, `uses`, `follows`, etc.

---

## 🔄 CORE LOOPS

### 1. Learning Loop (Autonomous Improvement)
```
Hourly Cron: learning_coordinator.py
    ↓
Innovation Research (arXiv + HN)
    ↓
Hypothesis Generation
    ↓
KG Update (research entities + hypotheses)
    ↓
Meta-Improvement Analysis
    ↓
Strategy Refinement
```

### 2. Memory Consolidation Loop
```
Every 30min: Heartbeat (CEO agent)
    ↓
Short-term signals collected
    ↓
04:40 UTC (Nightly): Memory-Core Dreaming
    ├── Light Phase: Sort & stage signals
    ├── REM Phase: Theme reflection
    └── Deep Phase: Score & promote to MEMORY.md
```

### 3. Health Monitoring Loop
```
Gateway Recovery: alle 5 min
    ↓
Health Check: alle 3h
    ↓
Cron Watchdog: alle 6h
    ↓
Error Healer: alle 6h (auto-fix)
```

---

## 📊 SYSTEM METRICS

### Current State (2026-04-12 06:50 UTC)

| Metric | Value | Status |
|--------|-------|--------|
| KG Entities | 249 | ✅ Growing |
| KG Relations | 1085 | ✅ Healthy |
| KG Orphans | 3 | ✅ Fixed (was 65) |
| Memory Files | 33 | ✅ Active |
| SQLite Chunks | 191 | ✅ Indexed |
| Vector Status | ready | ✅ Gemini |
| Cron Jobs | 18 | ✅ Active |
| Error Rate | 1.41% | ✅ Low |

### Error Breakdown
| Category | % |
|----------|---|
| exec_error | 46.4% |
| unknown | 43.4% |
| timeout | 6.8% |

---

## 🔐 SECURITY ARCHITECTURE

### Memory Security Patterns
| Pattern | Status | Purpose |
|---------|--------|---------|
| Memory Sanitizer | ✅ Active | Block malicious memory injection |
| Memory Validator | ✅ Active | Validate all writes |
| Memory Versioning | ✅ Active | Rollback capability |
| Memory Audit Log | ✅ Active | Complete trail |
| Memory Isolation | ✅ Active | Session separation |

### Security Features
- **Exec Safety:** Script preflight validation
- **Gateway Auth:** Token-based (14 chars)
- **Telegram DM:** Allowlist (5392634979)
- **Tools:** AlsoAllow (tts, message, canvas)

---

## 🚀 CAPABILITIES

### Skills (16 active)
```
• capability-evolver  — Self-testing & validation
• self-improvement   — Autonomous learning
• system-manager     — Operations & health
• research           — Web research (Brave)
• semantic-search    — Memory search
• voice-agent       — TTS (German)
• backup-advisor    — Backup recommendations
• coding            — Code generation
• content-creator   — Content pipeline
• frontend          — UI development
• qa-enforcer       — Quality enforcement
• loop-prevention   — Infinite loop detection
• backend-api       — API development
```

### Key Scripts
| Script | Purpose | Frequency |
|--------|---------|-----------|
| `learning_coordinator.py` | Main learning loop | Hourly |
| `continuous_improver.py` | Autonomous improvements | Hourly |
| `cron_error_healer.py` | Auto-fix cron failures | 6h |
| `gateway_recovery.py` | Auto-restart gateway | 5min |
| `kg_updater.py` | KG entity management | On-demand |
| `health_check.py` | System health check | 3h |

---

## 📁 DIRECTORY STRUCTURE

```
workspace/
├── scripts/              # 97 Python scripts
│   ├── MEMORY_API.py   # Memory interface
│   ├── *_tracker.py    # Tracking
│   ├── *_cleaner.py    # Cleanup
│   └── *_monitor.py    # Monitoring
├── skills/             # 16 skill directories
├── memory/             # File-based memory
│   ├── .dreams/        # Dreaming state
│   ├── dreaming/        # Dreaming output
│   ├── notes/          # Permanent notes
│   └── shared/         # Shared insights
├── core_ultralight/    # Portable core
│   ├── memory/         # Knowledge Graph
│   └── scripts/        # Core scripts
├── ceo/                # CEO workspace
│   ├── HEARTBEAT.md    # Status file
│   └── memory/         # CEO daily logs
├── docs/                # Documentation
│   ├── MEMORY_DREAMING.md
│   ├── CRON_INDEX.md
│   └── patterns/       # Pattern library
├── data/                # Logs & state
└── logs/                # System logs
```

---

## ⚠️ KNOWN ISSUES

| Issue | Priority | Status |
|-------|----------|--------|
| CEO Daily Briefing delivery failed | 🔴 HIGH | ⚠️ 3 consecutive errors |
| Security Audit delivery failed | 🟡 MED | ⚠️ 1 error |
| exec_error (46.4%) | 🟡 MED | System-level, not agent |
| shares_category relations (68.7%) | 🟡 MED | Low quality relations |

---

## 🎯 ARCHITECTURE PRINCIPLES

1. **Autonomy First** — Agent operates without human intervention
2. **Memory Hybrid** — KG + SQLite + Files for different use cases
3. **Self-Healing** — Auto-recovery for failures
4. **Continuously Learning** — Hourly research + improvement loops
5. **Security by Design** — Memory sanitization + validation

---

## 🔗 DOCUMENTATION MAP

| Doc | Purpose |
|-----|---------|
| `SYSTEM_ARCHITECTURE.md` | This file - Architecture overview |
| `MEMORY_DREAMING.md` | Memory-Core plugin documentation |
| `CRON_INDEX.md` | All cron jobs documented |
| `MEMORY_ARCHITECTURE.md` | Memory system details |
| `docs/patterns/` | Reusable patterns |

---

*Letztes Update: 2026-04-12 06:52 UTC*
*Sir HazeClaw — System Documentation*
