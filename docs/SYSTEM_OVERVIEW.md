# 🏰 EmpireHazeClaw System Overview

**Erstellt:** 2026-04-13 09:34 UTC
**Version:** 1.0
**Zweck:** Für externe KI-Analyse

---

## 🏗️ SYSTEM ARCHITECTURE

### Basis
- **Platform:** OpenClaw (AI Operating System)
- **Runtime:** Node.js v22.22.2 / Python 3
- **Host:** srv1432586 (Linux 6.8.0)
- **Gateway Port:** 18789 (loopback)
- **Workspace:** `/home/clawbot/.openclaw/workspace`

### Speicher
- **RAM:** 1.8 GB used / 7.8 GB total (23%)
- **Disk:** 70.6 GB free (26% used)
- **Load:** 0.22 (very low)

---

## 📁 STRUKTUR

```
.openclaw/
├── SCRIPTS/
│   ├── core/           # Core services
│   │   ├── config.py          # Path management
│   │   ├── logger.py          # Central logging
│   │   ├── events.py          # SQLite event queue
│   │   ├── config_migration_helper.py
│   │   └── test_services.py  # Integration tests
│   ├── services/       # Business logic (5 services)
│   │   ├── health.py         # Health check service
│   │   ├── git.py            # Git operations
│   │   ├── gateway.py        # Gateway management
│   │   ├── cron_healer.py    # Cron healing
│   │   └── morning_brief.py  # Daily briefings
│   └── scripts/        # Entry points
│       ├── health_check.py
│       ├── git_maintenance.py
│       ├── morning_brief.py
│       ├── gateway_check.py
│       └── cron_check.py
├── workspace/
│   ├── ceo/           # CEO agent files
│   ├── scripts/       # General scripts (40 Python files)
│   ├── memory/        # Daily memory files
│   ├── core_ultralight/memory/
│   │   └── knowledge_graph.json  # 349 entities, 523 relations
│   └── docs/          # Documentation
├── memory/
│   ├── main.sqlite    # 371.7 MB (771 chunks, 4024 embeddings)
│   ├── data.sqlite
│   ├── ceo.sqlite
│   └── events.sqlite  # Event queue
└── cron/
    └── jobs.json      # 51 crons (24 enabled)
```

---

## 🧠 KNOWLEDGE GRAPH

| Metric | Value |
|--------|-------|
| Entities | 349 |
| Relations | 523 |
| Storage | `/workspace/core_ultralight/memory/knowledge_graph.json` |

---

## 🗄️ DATABASE

| Database | Size | Tables | Content |
|----------|------|--------|---------|
| main.sqlite | 371.7 MB | 17 tables | Chunks, embeddings, FTS index |
| data.sqlite | - | - | Operational data |
| ceo.sqlite | - | - | CEO agent data |
| events.sqlite | - | 2 tables | Event queue |

**Main DB Tables:**
- `chunks` (771 rows) - Memory content
- `embedding_cache` (4024 rows) - Cached embeddings
- `chunks_fts` - Full-text search index

---

## 📊 SERVICES (5)

### Core Services

| Service | File | Functions | Status |
|---------|------|-----------|--------|
| health | `SCRIPTS/services/health.py` | `check_gateway()`, `check_database()`, `check_disk()`, `check_memory()`, `run_health_check()` | ✅ Tested |
| git | `SCRIPTS/services/git.py` | `get_branch_status()`, `get_local_branches()`, `prune_remote_refs()` | ✅ Tested |
| gateway | `SCRIPTS/services/gateway.py` | `check_health()`, `get_status()`, `restart_gateway()` | ✅ Tested |
| cron_healer | `SCRIPTS/services/cron_healer.py` | `get_cron_list()`, `run_healing_cycle()`, `get_status()` | ✅ Tested |
| morning_brief | `SCRIPTS/services/morning_brief.py` | `generate_brief()`, `format_telegram()` | ✅ Tested |

### Entry Points

| Entry Point | Service | Command |
|------------|---------|---------|
| `health_check.py` | health | `python3 SCRIPTS/scripts/health_check.py` |
| `git_maintenance.py` | git | `python3 SCRIPTS/scripts/git_maintenance.py` |
| `morning_brief.py` | morning_brief | `python3 SCRIPTS/scripts/morning_brief.py` |
| `gateway_check.py` | gateway | `python3 SCRIPTS/scripts/gateway_check.py` |
| `cron_check.py` | cron_healer | `python3 SCRIPTS/scripts/cron_check.py --status` |

---

## ⏰ CRON JOBS

| Status | Count |
|--------|-------|
| Total Crons | 51 |
| Enabled | 24 |
| Disabled | 27 |
| Errors | 9 |

**Active Crons (24):**
- CEO Daily Briefing (11:00 Berlin)
- Health Check Hourly (every 3h)
- HEARTBEAT Auto-Update (every 3h)
- Gateway Recovery Check (every 5min)
- Learning Loop (hourly)
- + 19 more

---

## 🔐 AUTHENTIFIKATION

| Provider | Status | Key |
|----------|--------|-----|
| minimax | ✅ Configured | `sk-cp-eQ6...` (125 chars) |
| google | ✅ Configured | `AIzaSyD9...` |
| openrouter | ❌ Not configured | - |

**Auth File:** `/home/clawbot/.openclaw/agents/ceo/agent/auth-profiles.json`

---

## 📈 METRIKEN (Live)

```json
{
  "gateway": "UP (port 18789)",
  "ram": "23.4% used (1.8GB / 7.8GB)",
  "disk": "26.4% used (70.6GB free)",
  "load": "0.22",
  "db_size": "371.7 MB",
  "kg_entities": 349,
  "kg_relations": 523,
  "scripts": 40,
  "services": 5,
  "crons": "24/51 enabled",
  "cron_errors": 9
}
```

---

## 🔧 HOW TO USE SERVICES

### Python Import
```python
import sys
sys.path.insert(0, '/home/clawbot/.openclaw')

from SCRIPTS.services.health import check_disk
result = check_disk()
print(result)  # {'status': 'ok', 'used_percent': 26.4, ...}
```

### CLI Entry Points
```bash
# Health check
python3 /home/clawbot/.openclaw/SCRIPTS/scripts/health_check.py

# Gateway status
python3 /home/clawbot/.openclaw/SCRIPTS/scripts/gateway_check.py

# Cron status
python3 /home/clawbot/.openclaw/SCRIPTS/scripts/cron_check.py --status
```

---

## 📝 WICHTIGE DATEIEN

| File | Purpose |
|------|---------|
| `/home/clawbot/.openclaw/SCRIPTS/core/config.py` | Central path configuration |
| `/home/clawbot/.openclaw/SCRIPTS/core/logger.py` | Central logging |
| `/home/clawbot/.openclaw/SCRIPTS/core/events.py` | Event queue |
| `/home/clawbot/.openclaw/workspace/ceo/HEARTBEAT.md` | System status (auto-updated) |
| `/home/clawbot/.openclaw/workspace/docs/REFACTORING_MASTER_PLAN.md` | Refactoring documentation |
| `/home/clawbot/.openclaw/workspace/docs/SERVICES_INDEX.md` | Service documentation |

---

## ⚠️ BEKANNTE ISSUES

| Issue | Status | Notes |
|-------|--------|-------|
| MiniMax API overload (HTTP 529) | 🔴 Temporär | Provider-seitig, wartet auf Erholung |
| 9 Cron errors | 🟡 Aktiv |mostly old (>3 days), GatewayDraining or model overload |
| DB Size 371.7 MB | 🟡 Hoch | Embedding cache dominiert (254MB) |
| KG access_count = 0 | 🟡 Bekannt | Bug seit Week 1, Fix in Week 2 geplant |

---

## 🎯 REFACTORING (2026-04-13)

**Durchgeführt:** 8-Phase Refactoring (08:03 - 08:48 UTC)

| Phase | Status |
|-------|--------|
| Phase 0: Baseline | ✅ |
| Phase 1: Cleanup | ✅ |
| Phase 2: Config Layer | ✅ |
| Phase 3: Logging | ✅ |
| Phase 4: Event Queue | ✅ |
| Phase 5: Subprocess Elimination | ✅ |
| Phase 6: Services Struktur | ✅ |
| Phase 7: DB Cleanup | ✅ |
| Phase 8: Tests | ✅ |

**Ergebnis:**
- Services: 0 → 5
- Entry Points: 0 → 5
- FTS Entries: 4,546 → 771 (-83%)
- DB Size: 380MB → 371.7MB

---

_Letzte Aktualisierung: 2026-04-13 09:34 UTC_
_Erstellt für: Externe KI-Analyse_