# 🔄 REFACTORING MASTER PLAN v3.0
## EmpireHazeClaw — Architecture Refactoring

**Erstellt:** 2026-04-13 07:44 UTC  
**Version:** 3.0 — Mit externem Feedback verbessert
**Status:** APPROVED — Ready for Execution

---

## Kernprinzip

> *"We are NOT building a framework.*  
> *We are creating order."*

---

## 📊 Coupling Map — Key Findings (Phase 0)

| Metrik | Wert | Bewertung |
|--------|------|-----------|
| Scripts total | 107 | Hoch |
| Hochgekoppelt (>8 deps) | 15 | Kritisch |
| Subprocess-Nutzung | **42 Scripts** | ⚠️ ARCHITEKTUR-PROBLEM |
| Hardcoded Paths | ~30 Scripts | Wartungs-Albtraum |

**Top Probleme:**
```
14 deps: cron_error_healer.py
42 Scripts: subprocess.run() verwendet     ← ECHTES PROBLEM
30 Scripts: hardcoded Pfade              ← ECHTES PROBLEM
```

---

## 🎯 REALISTISCHER 8-PHASEN PLAN

### PHASE 1: Cleanup (1-2 Tage)
**Ziel:** Verwirrung eliminieren, keine funktionalen Änderungen

```
□ 3 Archive konsolidieren
  └─ _archive/consolidated/ als SOT
  └─ archive/, ARCHIVE/ → _archive/consolidated/
  
□ Duplicate Scripts archivieren
  └─ SCRIPTS/analysis/learning_coordinator.py
  └─ 3x evening_*.py (später Phase 7)
  
□ scripts/ → SCRIPTS/ verschieben (nur 6 Python files)
```

**Impact:** Mittelhoch | **Risk:** Minimal

---

### PHASE 2: Config Layer (1 Tag)
**Ziel:** Alle Pfade an EINEM Ort

```python
# SCRIPTS/config.py — ZENTRAL
from pathlib import Path

BASE_DIR = Path("/home/clawbot/.openclaw")
SCRIPTS_DIR = BASE_DIR / "SCRIPTS"
WORKSPACE = BASE_DIR / "workspace"
MEMORY_DIR = BASE_DIR / "memory"
DB_PATH = MEMORY_DIR / "main.sqlite"
KG_PATH = WORKSPACE / "core_ultralight/memory/knowledge_graph.json"
LOG_PATH = BASE_DIR / "logs/system.log"

# NICHT MEHR:
# /home/clawbot/.openclaw/... hardcoded
# subprocess.run(['python3', '/path/to/script.py'])
```

**Aufgaben:**
```bash
# Alle Scripts die hardcoded paths haben → config.py importieren
# Alt: subprocess.run(['python3', '/home/clawbot/.../health.py'])
# Neu: from config import SCRIPTS_DIR; subprocess.run(['python3', f'{SCRIPTS_DIR}/health.py'])
```

**Impact:** Wartbarkeit | **Risk:** Niedrig

---

### PHASE 3: Logging Layer (1 Tag)
**Ziel:** Observability — alles muss geloggt werden

```python
# SCRIPTS/core/logger.py
import logging
from pathlib import Path

def get_logger(name: str) -> logging.Logger:
    log_path = Path("/home/clawbot/.openclaw/logs/system.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        filename=str(log_path),
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    return logging.getLogger(name)
```

**Nutzen:**
```python
# Statt: print("Health check done")
# Neu:
logger = get_logger(__name__)
logger.info("Health check completed in %ss", duration)
logger.warning("Gateway slow: %sms", latency)
```

**Impact:** Debugging | **Risk:** Niedrig

---

### PHASE 4: SQLite Event Queue (2 Tage)
**Ziel:** Race Conditions eliminieren (statt Message Bus)

```python
# SCRIPTS/core/events.py
import sqlite3
import json
from datetime import datetime

EVENTS_DB = "/home/clawbot/.openclaw/memory/events.sqlite"

def init_events_db():
    conn = sqlite3.connect(EVENTS_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY,
            event_type TEXT,
            payload TEXT,
            created_at TEXT,
            processed INTEGER DEFAULT 0
        )
    """)
    conn.commit()

def publish(event_type: str, payload: dict):
    """Atomic event publish"""
    conn = sqlite3.connect(EVENTS_DB)
    conn.execute(
        "INSERT INTO events (event_type, payload, created_at) VALUES (?, ?, ?)",
        (event_type, json.dumps(payload), datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def consume(event_type: str, limit: int = 10) -> list:
    """Consume unprocessed events"""
    conn = sqlite3.connect(EVENTS_DB)
    rows = conn.execute(
        "SELECT * FROM events WHERE event_type=? AND processed=0 LIMIT ?",
        (event_type, limit)
    ).fetchall()
    conn.execute("UPDATE events SET processed=1 WHERE id IN (?)", [r[0] for r in rows])
    conn.commit()
    return [json.loads(r[2]) for r in rows]
```

**Anwendung HEARTBEAT:**
```python
# NICHT MEHR: Direktes Schreiben auf HEARTBEAT.md
# NEU:
publish('heartbeat', {'component': 'memory', 'status': 'ok', 'time': time.time()})
```

**Warum SQLite statt Message Bus:**
- Einfacher (kein extra Service)
- Persistent (Events gehen nicht verloren)
-Passt zum bestehenden Stack

**Impact:** Race Conditions | **Risk:** Mittel

---

### PHASE 5: Subprocess Eliminierung (2-4 Tage)
**Ziel:** Direkte Funktionsaufrufe statt Shell-Skripte

**Problem:**
```
42 Scripts rufen subprocess.run(['python3', 'script.py']) auf
Das ist wie Programme mit os.system() zu starten statt Funktionen aufzurufen
```

**Lösung — Services erstellen:**
```python
# SCRIPTS/services/health.py — STATT subprocess
def run_health_check() -> dict:
    """Direct function call instead of subprocess"""
    return {
        'status': 'ok',
        'gateway': check_gateway(),
        'memory': check_memory(),
        'disk': check_disk()
    }

# SCRIPTS/scripts/health_check.py — ENTRYPOINT
from services.health import run_health_check
print(run_health_check())
```

**Nutzen:**
- 10x schneller (kein Process-Spawn)
- Typsicher (kein String-Parsing)
- Testbar (unittests möglich)

**Reihenfolge (nach Impact):**
```
1. health_check.py (11 deps)
2. health_monitor.py (10 deps)  
3. cron_error_healer.py (14 deps) ← WICHTIG
4. learning_loop.py (10 deps)
```

**Impact:** Performance + Testability | **Risk:** Mittel

---

### PHASE 6: Services Struktur (3-5 Tage)
**Ziel:** Klare Trennung — Entry Points vs. Logik

```
.openclaw/
├── SCRIPTS/
│   ├── config.py           # Zentral (Phase 2)
│   ├── core/
│   │   ├── logger.py      # Logging (Phase 3)
│   │   └── events.py      # Event Queue (Phase 4)
│   ├── services/           # LOGIK (Phase 5-6)
│   │   ├── health.py
│   │   ├── memory.py
│   │   ├── learning.py
│   │   ├── kg.py
│   │   └── infra.py
│   ├── scripts/           # ENTRY POINTS
│   │   ├── health_check.py
│   │   ├── daily_review.py
│   │   └── ...
│   └── infra/
│       ├── db.py
│       └── scheduler.py
├── archive/              # Phase 1
└── memory/
    └── events.sqlite      # Phase 4
```

**Regel:**
```
scripts/    = Entry Points (nur import + call)
services/   = Business Logic (kein subprocess.run)
core/       = Infrastructure (config, logger, events)
```

---

### PHASE 7: DB Cleanup (2 Tage)
**Ziel:** main.sqlite 380MB → <100MB

```bash
# Analyse
sqlite3 /home/clawbot/.openclaw/memory/main.sqlite "
SELECT name, page_count * page_size as size 
FROM dbstat ORDER BY size DESC LIMIT 10;"

# Archivierung
# - Sessions older than 30 days → archive table
# - memory entries with access_count=0 → archive
# - Add indexes on frequently queried columns
```

**3 Evening Scripts → 1:**
```
evening_capture.py    \
evening_review.py      → daily_review.py
evening_summary.py   /
```

---

### PHASE 8: Minimal Tests
**Ziel:** Wartbarkeit sicherstellen

```python
# SCRIPTS/tests/test_health.py
import pytest
from services.health import run_health_check

def test_health_returns_status():
    result = run_health_check()
    assert 'status' in result
    assert result['status'] in ['ok', 'warning', 'error']
```

**Regel:** Jeder Service hat einen Test

---

## 📅 ZEITPLAN

```
Phase 1: Cleanup          — 1-2 Tage
Phase 2: Config Layer      — 1 Tag
Phase 3: Logging           — 1 Tag
Phase 4: Event Queue        — 2 Tage
Phase 5: Subprocess Removal — 2-4 Tage
Phase 6: Services Struktur  — 3-5 Tage
Phase 7: DB Cleanup        — 2 Tage
Phase 8: Tests             — 1 Tag

Total: 13-19 Tage = 3-4 Wochen
```

---

## 🚨 RISIKO-MATRIX

| Phase | Risk | Mitigation |
|-------|------|------------|
| Phase 1 | LOW | Nichts kaputt, nur moves |
| Phase 2 | LOW | Config versionieren |
| Phase 3 | LOW | Logging nur zusätzlich |
| Phase 4 | MEDIUM | SQLite Events erst parallel laufen lassen |
| Phase 5 | MEDIUM | Ein Service nach dem anderen |
| Phase 6 | MEDIUM | Langsam refactoren, testen |
| Phase 7 | HIGH | 3x Backup, alte DB behalten |
| Phase 8 | LOW | Tests können parallel |

---

## ✅ ERFOLGS-KRITIERIEN

| Kriterium | Vorher | Ziel |
|-----------|--------|------|
| Subprocess-Nutzer | 42 Scripts | <10 |
| Hardcoded Paths | ~30 Scripts | 0 |
| Archive-Strukturen | 3 | 1 |
| Race Conditions | HEARTBEAT.md | Event Queue |
| Evening Crons | 3 | 1 |
| main.sqlite | 380MB | <100MB |
| Services mit Tests | 0 | alle |

---

## 🛠️ VORBEREITUNG

```bash
# Backup
mkdir -p /home/clawbot/.openclaw/backup_pre_refactor/$(date +%Y%m%d)
cp -r /home/clawbot/.openclaw/workspace/archive /home/clawbot/.openclaw/backup_pre_refactor/
cp /home/clawbot/.openclaw/memory/*.sqlite /home/clawbot/.openclaw/backup_pre_refactor/

# Git
cd /home/clawbot/.openclaw/workspace
git add -A && git commit -m "Pre-refactor checkpoint"
git tag refactor_v3_start_20260413
```

---

**Letzte Änderung:** 2026-04-13 07:55 UTC (v3.0 — mit Feedback verbessert)
