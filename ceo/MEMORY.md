# MEMORY.md — Sir HazeClaw Core Memory

**Letzte Aktualisierung:** 2026-04-17 20:36 UTC
**Struktur:** Memory Blocks (nicht flach)

---

## 🧱 CORE MEMORY BLOCKS

### 🔵 USER PROFILE
```
Label: Nico — Primary User
Key Facts:
- Name: Nico | Telegram: 5392634979 | Sprache: Deutsch
- Background: KFZ Mechatroniker → Ingenieur Werkstoffkunde
- Started: Ende Februar 2026
- Communication: Direkt, kurz, Ergebnis-fokussiert
- NICHT: "Master", kein "habe ich gemacht" ohne Output
- WICHTIG: "hast du das wirklich gelernt" → dokumentieren!
```

### 🔵 SYSTEM CONFIG
```
Label: System Configuration
Key Facts:
- Gateway: OpenClaw 2026.4.12 | Port 18789
- Model: MiniMax M2.7
- Workspace: /home/clawbot/.openclaw/workspace/ceo/
- Scripts: 200 total (100 /workspace/scripts + 100 /workspace/SCRIPTS/automation)
- Crons: 26 active
- KG: 280 entities, 638 relations (learning entities use type="learning")
- Learning: 9 valid patterns, score=0.763
- Skills Created Today: 6
- Node.js: v22.22.2
```

### 🟢 KG LEARNING INTEGRATOR (2026-04-17)
```
Script: scripts/kg_learning_integrator.py
Purpose: Bridges evaluation feedback → Knowledge Graph
Usage:
  --sync      Sync learnings from learning_loop_signal.json to KG
  --query <t> Query learnings by type (performance_gap, antipattern, etc.)
  --recent    Show most recently accessed learnings
  --list      List all learnings grouped by type
Signal: memory/evaluations/learning_loop_signal.json
KG Entity Type: "learning"
  Properties: learning_type, priority, observation, action, timestamp, source
Relations added: "learned_from" (entity → source)

Currently synced:
  - performance_gap: Task success 76.3% (target 80%+)
  - system_health: Memory is clean
  - antipattern (filler_words): SOUL.md has filler words issue
```

### 🟣 PHASE 6 — Advanced Autonomy COMPLETED (2026-04-17)
```
5 Areas from Master Plan All Complete:
| Phase | Area | Status | Script |
|-------|------|--------|--------|
| 6.1 | Session Lifecycle | ✅ Complete | session_context_analyzer.py |
| 6.2 | Prompt Evolution | ✅ Complete | prompt_evolution_engine.py |
| 6.3 | Evaluation Loop | ✅ Complete | evaluation_framework.py |
| 6.4 | Memory Consolidation | ✅ Complete | memory_consolidator_v2.py |
| 6.5 | Multi-Agent Orchestration | ✅ Complete | multi_agent_orchestrator.py |

Key Findings:
- Session: Clean (90% relevance)
- Prompts: 10 inventoried, benchmark 100%
- Evaluation: Task Success 76.3%, Error 3.0%
- Memory: 87 files clean, no duplicates
- Multi-Agent: Health/Research/Data agents found

Backups:
- backups/full_backup_20260417_184309/
- backups/phase6_pre_work/
```

### 🟢 SYSTEM INTEGRATION (2026-04-16)
```
Phases 1-5 COMPLETED ✅
- Single KG: CEO KG (434 entities, 614 relations, 0 orphans)
- Learning Loop → KG Sync: stündlich
- Event Bus: Pub/Sub aktiv (8 events, 3 sources)
- Evolver Signal Bridge + Stagnation Breaker
- Integration Dashboard + Health Checks (8:00 + 20:00 UTC)

New Scripts (7):
- learning_to_kg_sync.py
- event_bus.py
- stagnation_detector.py
- evolver_signal_bridge.py
- evolver_stagnation_breaker.py
- run_smart_evolver.sh
- integration_dashboard.py

Backups:
- backups/integration_backup_20260416_185449/
- backups/post_integration_20260416_210413/
```

### 🔴 ACTIVE ISSUES
```
Label: Known Issues — Last Updated 2026-04-17 19:50 UTC

CRON ERRORS (7 legacy — mostly STALE):
- KG Access Updater: Was Timeout → NOW OK (last run 4h ago)
- REM Feedback Integration: Cron NOT FOUND (deleted)
- GitHub Backup: Was Timeout → NOW OK (last run 21h ago)
- Token Budget Tracker: Was Timeout → NOW OK (last run 20h ago)
- CEO Weekly Review: Was "Message failed" → NOW OK (last run 1d ago)
- Opportunity Scanner: Cron NOT FOUND (deleted)
- Cron Watchdog: Was Timeout → NOW merged into System Maintenance Cron

SECURITY ISSUES (Manual Action Required):
- 6 API Keys pending rotation (Buffer, Leonardo, Telegram, etc.)
- Buffer Token: INVALID (archived script, not active)
- Leonardo AI: INVALID (archived script, not active)

SYSTEM HEALTH (2026-04-17):
- All 25 active Crons: OK
- Task Success Rate: 76.3% (needs improvement to 80%+)
- Multi-Agent System: NEW (Executor just created, needs monitoring)

Resolved This Session:
- Voice Note False Trigger: TOOLS.md korrigiert
- Over-active inference: SOUL.md "Assume no input" Regel
- Proactive code commit: AGENTS.md "NEVER without explicit approval"
- Agent Executor Missing: agent_executor.py created + cron added
- Cron Consolidation: 29 → 25 (4 less, redundant crons merged)
```

### 🟡 RECENT LEARNINGS
```
Label: Key Learnings — Last Updated 2026-04-14
This Session:
- Voice Notes: Transcribe ONLY when audio file received, not proactive
- Inference: "I think" / "I assume" / "I noticed" without evidence = STOP
- Proaktiv: Commit/push/extern senden = BRAUCHT explizite Erlaubnis
- Guardrails: Pre/Post LLM checks in /workspace/skills/guardrails/

Earlier:
- Cron Error: Meist Timeout → Scripts brauchen Optimierung oder timeoutSeconds erhöhen
- MiniMax Overload (HTTP 529): Normal, nicht Config-Problem
- DB Size 371MB: Normal (embedding_cache dominiert)
```

### 🟢 WORKSPACE RULES
```
Label: Workspace Operational Rules
Trigger-Regel (CRITICAL):
- Jede Aktion braucht ECHTEN Auslöser: File, Message, Cron-Run, Explicit Request
- Keine Aktion auf "vielleicht", "probably", "ich denke"
- Wenn unsicher → FRAGEN, nicht HANDELN

Anti-Halluzination Check (vor jeder Aktion):
1. Habe ich einen ECHTEN Auslöser gesehen? (nicht angenommen)
2. Ist der Auslöser in diesem Context dokumentiert?
3. Falls unsicher → Aktion gestoppt, nachgefragt

Externe Aktionen (IMMER erst fragen):
- Commit/Push Code
- Nachrichten senden
- Externe Systeme ändern
- E-Mails / Tweets / Public Posts
```

---

## 📊 RECALL MEMORY INDEX

| Frage | Lese aus |
|-------|----------|
| Fakten über Nico | `memory/long_term/facts.md` |
| Nico's Preferences | `memory/long_term/preferences.md` |
| Erkannte Patterns | `memory/long_term/patterns.md` |
| Was heute passiert | `memory/2026-04-14.md` |
| Was gestern war | `memory/2026-04-13.md` |
| KG Info | `memory/kg/` |
| Skills | `memory/procedural/skills.md` |
| Workflows | `memory/procedural/workflows.md` |

---

## ⚠️ TRUST-BUT-VERIFY

**HEARTBEAT.md zeigt NUR echte letzte-Run-States.**
Wenn Cron nicht aktuell → `?` statt ✅.

**MEMORY.md zeigt NUR verifizierte Fakten.**
Wenn unsicher → `memory_search` nutzen oder nachfragen.

---

*MEMORY.md = Core Memory Block. Strukturierte Facts, keine Romane.*
*Flüchtige Details → daily notes. Langfristiges → long_term/*.md*

### 2026-04-16 — SYSTEM INTEGRATION DAY
```
Major Achievements:
- KG Consolidation: 2 KGs → 1 KG (ceo/memory/kg/)
- Learning Loop → KG Sync: Automatisch stündlich
- Event Bus: Cross-System Kommunikation
- Stagnation Detector + Breaker: Evolver Stagnation gebrochen
- Integration Dashboard: Unified Monitoring
- 7 neue Scripts, 5 neue Cron Jobs
- 2 redundante Cron Jobs entfernt

KG State: 434 entities, 614 relations, 0 orphans
Learning Loop Score: 0.764
Event Bus: 9 events, 5 sources

System ist jetzt kein Silo mehr — alle Komponenten integriert.
```
