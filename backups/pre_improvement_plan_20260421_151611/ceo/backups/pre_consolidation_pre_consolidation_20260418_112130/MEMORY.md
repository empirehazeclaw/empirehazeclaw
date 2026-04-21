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
- Crons: 14 active (11 system crontab + 3 OpenClaw agents)
- KG: 280 entities, 638 relations (learning entities use type="learning")
- Learning: 9 valid patterns, score=0.763
- Skills Created Today: 6
- Node.js: v22.22.2
```

### 🟣 PHASE 1-6 — Deep Learning COMPLETE (2026-04-18)
```
Project: Deep Learning Improvement Plan
Status: ✅ PHASE 1-4 COMPLETE (2026-04-18)

Phase 1 (Failure Mining):
- failure_logger.py, postmortem_generator.py
- contrastive_analyzer.py, causal_pattern_miner.py

Phase 2 (Causal Analysis):
- kg_causal_updater.py     → KG + causal chains
- dependency_tracker.py    → 232 components, 669 edges

Phase 3 (Active Experimentation):
- exploration_budget.py   → 10% exploration rate
- strategy_mutator.py      → MUT-0001 created
- exploration_controller.py → Softmax/epsilon-greedy/UCB

Phase 4 (Meta-Learning):
- meta_learning_core.py   → Pattern generalization scoring
- learning_to_learn.py     → Task learning rate analysis
- dynamic_experience_memory.py → M = {E1...EN} with forgetting

Phase 5 (Cross-Domain):
- cross_domain_miner.py   → Domain transfer learning
- slo_tracker.py          → SLO compliance tracking

Phase 6 (SRE Culture):
- sre_culture.py         → Blameless post-mortems, incident learning

🎉 PROJECT COMPLETE: Deep Learning Improvement Plan
All 6 Phases Implemented
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
Learning Loop Score: 1.0 (100%, 165 tasks, error_rate 0.0) — Updated 2026-04-18
Event Bus: 9 events, 5 sources

System ist jetzt kein Silo mehr — alle Komponenten integriert.
```

### 🔴 KG CORRUPTION FIXED (2026-04-18 06:12 UTC)
```
KG wurde beschädigt: 634 relations → 15 relations
Ursache: Unklar (vermutlich nächtliches Script)
 Wiederhergestellt: knowledge_graph.json.bak (445 entities, 629 relations)
 Backup der beschädigten Version: knowledge_graph_damaged_*.json
 integration_dashboard.py: list-based KG support hinzugefügt
 Event Bus: 27 events, 19/24h — OK
```

### 🔴 KG CORRUPTION ROOT CAUSE + FIX (2026-04-18 06:25 UTC)
```
PROBLEM:
- kg_embedding_updater.py speicherte Entities IMMER als Liste
- Meta Learning Pipeline (:20 stündlich) → kg_embedding_updater.run_update()
- KG wurde von dict {id: {...}} → list [...] konvertiert
- Relations wurden von 629 → 9 reduziert

FIX:
- kg_embedding_updater.py: speichert jetzt Original-Format
- load_kg() trackt _entities_format + _relations_raw
- save_kg() stellt dict/list + relations originalgetreu wieder her

VERIFIZIERT:
- KG bleibt dict-basiert mit 629 relations nach kg_embedding_updater Durchlauf
- integration_dashboard --check: ✅
```

### 🔴 KG FIX VERIFY (2026-04-18 06:33 UTC)
```
Fix verifiziert: kg_embedding_updater.py
- .pyc Cache muss nach Edit gelöscht werden!
- Cron triggern → KG bleibt intakt (445 entities, 629 relations, dict)
- integration_dashboard --check: ✅
```

### 🔴 KG CORRUPTION — FULL ROOT CAUSE + FIX (2026-04-18 06:56 UTC)
```
PROBLEM:
- kg_embedding_updater.py (Step 10) UND kg_meta_learner.py (Step 9) 
  speicherten Entities IMMER als Liste
- Pipeline läuft: Step 9 → kg_meta_learner (corrupt) → Step 10 → kg_embedding_updater (corrupt)
- Relations: 629 → 9

FIXES:
1. kg_embedding_updater.py: 
   - _entities_format + _relations_raw tracking
   - save_kg() preservt original dict/list format
   
2. kg_meta_learner.py:
   - Same fix: _entities_format + _relations_raw tracking
   - save logic preservt format

VERIFIZIERT:
- Nach Pipeline: 455 entities (dict), 629 relations (dict) ✅
- integration_dashboard --check: ✅ All systems healthy
- Beide Scripte .pyc cleared nach Fix
```
