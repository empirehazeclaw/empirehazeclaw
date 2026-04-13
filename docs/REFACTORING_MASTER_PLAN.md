# 🔄 REFACTORING MASTER PLAN v3.0
## EmpireHazeClaw — Architecture Refactoring

**Erstellt:** 2026-04-13 07:44 UTC
**Version:** 3.1 — Updated 2026-04-13 08:16 UTC
**Status:** IN PROGRESS — Phases 1-3 Complete

---

## Kernprinzip

> *"We are NOT building a framework.*
> *We are creating order."*

---

## 📊 PROGRESS TRACKER

| Phase | Status | Completed | Tag |
|-------|--------|-----------|-----|
| Phase 0 | ✅ DONE | 08:03 | `phase0_cleanup_start_20260413` |
| Phase 1 | ✅ DONE | 08:05 | `phase1_cleanup_complete_20260413` |
| Phase 2 | ✅ DONE | 08:08 | `phase2_config_layer_complete_20260413` |
| Phase 3 | ✅ DONE | 08:15 | `phase3_logging_complete_20260413` |
| Phase 4 | 🔄 NEXT | — | — |
| Phase 5 | ⏳ PENDING | — | — |
| Phase 6 | ⏳ PENDING | — | — |
| Phase 7 | ⏳ PENDING | — | — |
| Phase 8 | ⏳ PENDING | — | — |

---

## ✅ PHASE 1: Cleanup (DONE ✓)

**Ziel:** Verwirrung eliminieren, keine funktionalen Änderungen

**Completed:**
- ✅ 3 Archive konsolidiert → `_archive/consolidated/` (5.8 MB)
- ✅ 4 Duplicate Scripts archiviert
- ✅ Alte Archive entfernt (archive/, _archive/scripts_old/, ARCHIVE/)

**Git:** `80dc76f Phase 1 Complete: Archive Consolidation`

---

## ✅ PHASE 2: Config Layer (DONE ✓)

**Ziel:** Alle Pfade an EINEM Ort

**Created:**
- `SCRIPTS/core/config.py` — Zentrale Konfiguration
- `SCRIPTS/core/__init__.py` — Package Init
- `SCRIPTS/core/config_migration_helper.py` — Migration Tool

**Config bietet:**
```python
BASE_DIR, WORKSPACE, SCRIPTS_DIR
MEMORY_DIR, DB_PATH, DATA_DB_PATH, CEO_DB_PATH
KG_PATH, LOG_DIR, LOG_PATH, ARCHIVE_DIR
SERVICES_DIR, SCRIPTS_ENTRY_DIR, EVENTS_DB_PATH
```

**Git:** `9243b3f Phase 2: Config Layer created`

**Identified:** 98 files with hardcoded paths

---

## ✅ PHASE 3: Logging Layer (DONE ✓)

**Ziel:** Observability — alles muss geloggt werden

**Created:**
- `SCRIPTS/core/logger.py` — Zentrales Logging

**Usage:**
```python
from SCRIPTS.core.logger import get_logger
logger = get_logger(__name__)
logger.info("Health check done", duration=1.5)
```

**Log Location:** `/home/clawbot/.openclaw/logs/system.log`

**Git:** `ff64df1 Phase 3: Logging Layer created`

---

## 🔄 PHASE 4: SQLite Event Queue (NEXT)

**Ziel:** Race Conditions eliminieren

**Plan:**
```python
# SCRIPTS/core/events.py
EVENTS_DB = "/home/clawbot/.openclaw/memory/events.sqlite"

def publish(event_type: str, payload: dict):
    """Atomic event publish"""
    
def consume(event_type: str, limit: int = 10) -> list:
    """Consume unprocessed events"""
```

**Anwendung:** HEARTBEAT.md → Event Queue (Race Conditions eliminieren)

---

## ⏳ PHASE 5: Subprocess Eliminierung

**Ziel:** Direkte Funktionsaufrufe statt Shell-Skripte

**Problem:** 42 Scripts verwenden `subprocess.run(['python3', 'script.py'])`

**Solution:** Services erstellen
```python
# SCRIPTS/services/health.py
def run_health_check() -> dict:
    """Direct function call instead of subprocess"""
```

---

## ⏳ PHASE 6: Services Struktur

**Ziel:** Klare Trennung — Entry Points vs. Logik

```
.openclaw/
├── SCRIPTS/
│   ├── core/
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── events.py (Phase 4)
│   ├── services/  # LOGIK
│   └── scripts/   # ENTRY POINTS
```

---

## ⏳ PHASE 7: DB Cleanup

**Ziel:** main.sqlite 380MB → <100MB

---

## ⏳ PHASE 8: Tests

**Ziel:** Wartbarkeit sicherstellen

---

## 🛟 ROLLBACK

```bash
# Backup exists at:
bash /home/clawbot/.openclaw/backup_pre_refactor/20260413/ROLLBACK_RESTORE.sh

# Git rollback:
git checkout refactor_v3_start_20260413
```

---

## 🏷️ GIT TAGS

```
refactor_v3_start_20260413    — Master plan start
phase0_cleanup_start_20260413  — Phase 0 baseline
phase1_cleanup_complete_20260413  — Phase 1 done
phase2_config_layer_complete_20260413  — Phase 2 done
phase3_logging_complete_20260413  — Phase 3 done
checkpoint_phase1_complete     — Previous work
```

---

**Letzte Änderung:** 2026-04-13 08:16 UTC (v3.1 — phases 1-3 verified)