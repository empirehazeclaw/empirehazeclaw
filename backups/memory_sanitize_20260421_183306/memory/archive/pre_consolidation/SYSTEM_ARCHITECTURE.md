# Sir HazeClaw — System Architektur

**Letzte Aktualisierung:** 2026-04-17  
**Status:** ✅ Produktiv

---

## Überblick

```
        ┌─────────────────────────────────────────────────────────┐
        │                     TELEGRAM (Nico)                     │
        └──────────────────────┬──────────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │      GATEWAY       │
                    │   OpenClaw 2026.4  │
                    │    Port 18789      │
                    └──────────┬──────────┘
                               │
        ┌───────────────────────┼────────────────────────┐
        │                       │                        │
   ┌────▼─────┐          ┌──────▼──────┐          ┌──────▼──────┐
   │  MEMORY  │          │   SCRIPTS   │          │  KNOWLEDGE  │
   │  SYSTEM  │          │  (73 Files)  │          │    GRAPH    │
   └──────────┘          └─────────────┘          └─────────────┘
```

---

## Die 4 Säulen

### 1. Memory System
**Pfad:** `/workspace/memory/`  
**Struktur:**

| Verzeichnis | Inhalt | Kapazität |
|-------------|---------|-----------|
| `short_term/` | Aktuelle Session-Notes | Wird komprimiert |
| `long_term/` | Persistente Fakten über Nico | Bleibt |
| `episodes/` | Abgeschlossene Projekt-Episoden | Archiv |
| `procedural/` | Skills, Workflows, How-Tos | Wächst |
| `kg/` | Knowledge Graph Daten | Synced |
| `notes/` | Permanente Notizen (Doku) | Manuell |
| `ARCHIVE/` | Archivierte alte Notes | Read-only |
| `evolution/` | Evolver State + Narrative | Auto |

**Key Files:**
- `MEMORY.md` — Core Memory Block (geladen im Main Session)
- `SOUL.md` — Persönlichkeit + Guidelines
- `USER.md` — Nico's Profile + Preferences
- `HEARTBEAT.md` — System Status

### 2. Knowledge Graph (KG)
**Pfad:** `/workspace/ceo/memory/kg/knowledge_graph.json`  
**Aktuell:** 444 Entities | 628 Relations  
**Sync:** Learning Loop → KG (10min nach jeder Learning Loop Run)

**Entity Types:**
- person, concept, topic, learning
- script, skill, improvement, pattern
- error_pattern, learning_feedback, metrics

### 3. Learning Loop
**Hauptscript:** `SCRIPTS/automation/learning_loop_v3.py`  
**Cron:** `0 * * * *` (stündlich)  
**Score:** 0.764 | **Iteration:** 129

**Phasen:**
```
Hourly: Feedback sammeln → Pattern erkennen → Verbessern → Validieren → Score updaten
Daily:  Knowledge Graph Sync (10min nach Learning Loop)
```

**Verbunden:**
- `learning_loop_state.json` — Loop Score + Historie
- `learning_loop/patterns.json` — Erkannte Patterns
- `learning_loop/improvements.json` — Durchgeführte Verbesserungen
- `learning_loop/validation_log.json` — Validierungs-Resultate

### 4. Capability Evolver (Smart Evolver)
**Script:** `SCRIPTS/automation/run_smart_evolver.sh`  
**Cron:** Täglich 03:00 UTC  
**Dokumentation:** `memory/notes/smart-evolver-integration.md`

**Loop (6 Steps):**
```
1. check-stagnation        → Event Bus + KG analysieren
2. node index.js           → Evolver mit Strategy (innovate/repair)
3. node index.js solidify  → Patches ANWENDEN
4. --post-evolver-results   → An Event Bus publishen
5. --check (Stagnation)    → Diversität prüfen
6. --clear-pending-solidify → Status zurücksetzen
```

---

## Subsysteme

### 🔄 Autonomy Framework
| Cron | Intervall | Job |
|------|-----------|-----|
| Autonomy Supervisor | alle 5min | VIGIL Pattern-Watcher |
| Gateway Auto-Recovery | alle 15min | Restart wenn down |
| Bug Hunter | alle 30min | Logs auf Bugs scannen |
| Bug Fix Pipeline | stündlich | Auto-Fix + Verify |
| Autonomous Agent | stündlich | Self-Review + Self-Heal |

### 📊 Monitoring
| Cron | Intervall | Job |
|------|-----------|-----|
| Health Check | alle 3h | Critical Issues |
| Cron Watchdog | alle 6h | Crons prüfen |
| Stagnation Detector | alle 6h | System-Stagnation |
| KG Access Updater | alle 4h | KG Access-Counts |
| Integration Health | 08:00 + 20:00 | Dashboard |

### 📚 Tägliche Runs
| Cron | Zeit | Job |
|------|------|-----|
| Learning Coordinator | 09:00 + 18:00 | Koordiniert Learning |
| Morning Brief | 11:00 Berlin | An Nico |
| Security Audit | 08:00 | Security Check |
| Bug Hunter Report | 30min | Neue Bugs melden |
| GitHub Backup | 23:00 | Commit + Push |
| Session Cleanup | 03:00 | Alte Sessions |
| Token Budget | 00:00 | Tages-Report |
| Evening Capture | 21:00 | Tages-Ende |
| Memory Sync | 5min nach HH | current.md updaten |
| Learning Loop → KG | 10min nach HH | KG sync |
| Dreaming Promotion | 04:40 | Short→Long Term |

---

## Event Bus
**Pfad:** `/workspace/data/events/events.jsonl`  
**System:** Zentraler Event-Stream für alle Subsysteme

**Event Types:**
- `kg_update` — Knowledge Graph Änderungen
- `evolver_completed` — Evolver hat fertig
- `learning_loop_*` — Learning Loop Events
- `system_heartbeat` — Heartbeat-Signale
- `backup_completed` — Backup-Resultate
- `improvement_applied` — Verbesserungen

---

## Scripts-Überblick (73 Files)
**Hauptorte:**
- `/workspace/scripts/` — Primary Scripts
- `/workspace/SCRIPTS/automation/` — Automation (Learning, Bug Fix, etc.)
- `/workspace/SCRIPTS/analysis/` — Analyse Tools
- `/workspace/SCRIPTS/tools/` — Utilities

**Wichtigste:**
| Script | Zweck |
|--------|-------|
| `learning_loop_v3.py` | Haupt Learning Loop |
| `run_smart_evolver.sh` | Evolver Pipeline |
| `evolver_signal_bridge.py` | Event Bus ↔ Evolver |
| `evolver_stagnation_breaker.py` | Diversität erzwingen |
| `autonomous_agent.py` | Self-Review + Heal |
| `autonomy_supervisor.py` | VIGIL Pattern |
| `bug_scanner.py` | Bug Detection |
| `bug_fix_pipeline.py` | Auto-Fix |
| `kg_access_updater.py` | KG Analytics |
| `learning_coordinator.py` | Learning Orchestration |
| `context_compressor.py` | Memory Kompression |
| `gateway_recovery.py` | Gateway Health |
| `cron_watchdog.py` | Cron Monitor |
| `morning_brief.py` | Daily Report |

---

## Verbindungen

```
Telegram (Nico)
       │
       ▼
┌──────────────────────────────────────────────────────┐
│                    MAIN SESSION                      │
│  (Solarm, Soul, User, Memory, HEARTBEAT geladen)      │
└──────────────────────────────────────────────────────┘
       │
       ├──────────────────────────────────┐
       │                                  │
       ▼                                  ▼
┌─────────────┐                   ┌──────────────┐
│  Crons      │◄──────────────────│  Event Bus   │
│  (65 Jobs)  │                   │  (events.jsonl)
└─────────────┘                   └──────────────┘
       │                                  │
       ├──────────────────────────────────┤
       ▼                                  ▼
┌─────────────┐                   ┌──────────────┐
│  Learning   │                   │   Capability │
│  Loop v3    │                   │   Evolver    │
└─────────────┘                   └──────────────┘
       │                                  │
       ▼                                  ▼
┌─────────────┐                   ┌──────────────┐
│  Knowledge  │◄──────────────────│  Solidify   │
│  Graph      │   (Pattern sync)  │  (Patches)   │
└─────────────┘                   └──────────────┘
```

---

## Config

| Setting | Wert |
|---------|------|
| Model | MiniMax M2.7 |
| Gateway Port | 18789 |
| Workspace | `/home/clawbot/.openclaw/workspace/ceo/` |
| Timezone | Europe/Berlin (UTC+2) |
| Crons | 65 total, ~27 aktiv |

---

*Sir HazeClaw — System Architektur*
