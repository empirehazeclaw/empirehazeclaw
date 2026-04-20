# MEMORY.md — Sir HazeClaw Core Memory

**Letzte Aktualisierung:** 2026-04-19 17:32 UTC

---

## 🧱 CORE MEMORY BLOCKS

### 🔵 USER PROFILE
```
Name: Nico | Telegram: 5392634979 | Sprache: Deutsch
Background: KFZ Mechatroniker → Ingenieur Werkstoffkunde
Started: Ende Februar 2026
Communication: Direkt, kurz, Ergebnis-fokussiert
NICHT: "Master", kein "habe ich gemacht" ohne Output
WICHTIG: "hast du das wirklich gelernt" → dokumentieren!
```

### 🔵 SYSTEM CONFIG
```
Gateway: OpenClaw 2026.4.12 | Port 18789
Model: MiniMax M2.7
Workspace: /home/clawbot/.openclaw/workspace/ceo/
Scripts: ~200 total
Crons: 30 active (nach Deep Audit + Doc Cleanup 2026-04-18)
KG: 479 entities, 33.8% orphans (korrekte Messung 2026-04-19)
Learning: 100% success rate, 165 tasks
```

---

## 🤖 MULTI-AGENT SYSTEM

### Architektur
```
Agent Delegation Cron (15min)
    → multi_agent_orchestrator
    → task queue
        → Agent Executor Cron (5min)
        → agent_executor
        → health_agent / research_agent / data_agent
```

### Agenten
| Agent | Status | Kapazitäten |
|-------|--------|------------|
| `data_agent` | ✅ ENHANCED | KG Health, Script Health, Doc Audit, Cron Redundancy |
| `health_agent` | ✅ OK | Process, Memory, Disk, Network, Gateway, Cron Checks + Self-Healing |
| `research_agent` | ✅ FIXED | Brave Search API, arXiv, HN — Web Search funktioniert jetzt! |

---

## 🟢 SYSTEM MAINTENANCE AUTOMATION (2026-04-18)

### Data Agent — Enhanced
```
Location: /workspace/SCRIPTS/automation/data_agent.py
Runs:    Via Agent Executor (alle 15min als data_analysis task)
Capabilities:
  --kg-maintain      KG quality (80% orphan threshold)
  --script-health    Broken symlinks, missing scripts, wrong paths
  --doc-audit        Stale docs (>30 days)
  --cron-redundancy  Similar cron payloads
  --full             Complete cycle
```

---

## 🟢 DEEP SYSTEM AUDIT (2026-04-18)

```
CRITISCHE PROBLEME GEFUNDEN + GELÖST:
1. kg_lifecycle_manager.py: BROKEN SYMLINK → Cron deleted
2. auto_doc.py: WRONG PATH → Cron korrigiert
3. kg_auto_prune.py: 30% threshold → 80% + dry-run
4. KG Auto-Prune löschte 409 entities → Cron deleted, KG restored
5. Meta Learning Pipeline: Script fehlte → Cron deleted
6. Evening Capture: deprecated → Cron deleted
7. Bug Fix Pipeline: redundant → Cron deleted
8. research_agent: DuckDuckGo kaputt → Brave Search API

CRONS: 37 → 30
DOKUMENTATION: 35 alte Plans → docs/_archive_plans/
```

---

## 🚨 SECURITY LEARNING (2026-04-18)

```
VORFALL: Brave API Key in Telegram gepostet.
FOUND: BSADT...REDACTED (jetzt kompromittiert)

WAS PASSIERT IST:
- Key aus secrets.env gelesen → in Telegram-Nachricht gepostet
- Nico hat sofort bemerkt und mich konfrontiert

FEHLER:
- SOUL.md: "Private things stay private. Period." → verletzt
- AGENTS.md Red Line: "Don't exfiltrate private data" → verletzt
- Kein nachdenken bevor posten

REGELN DIE ICH JETZT HABE:
1. API Keys / Tokens / Secrets → IMMER redacted in Nachrichten
   Beispiel: BSADT...Y44 oder [KEY REDACTED]
2. secrets.env lesen → Key NIE im Klartext in Telegram/Output
3. Bei Unsicherheit: FRAGEN statt posten
4. SOUL.md "Private things stay private" = bindet auch API Keys

ACTION: Brave API Key muss rotiert werden ( bereits-reported)
```

---

## 🟢 QMD INTEGRATION (2026-04-19)
```
QMD v2.1.0 | Index: 19.3 MB
Collections:
  - memory: 58 files (alter Pfad, 10d alt)
  - ceo_memory: 113 files (NEU! 2026-04-19)
Vectors: 1756 embedded
Embedding: läuft im Hintergrund
Cron: QMD Watchdog (alle 15min)
```

---

## 🔴 ACTIVE ISSUES
```
- Brave API Key rotieren (kompromittiert)
- Mad-Dog Script: nicht executable (LOW)
```

---

## 🟢 PHASE 3 IMPROVEMENTS (2026-04-19)

### Learning Loop Plateau Fix
```
Scripts: learning_loop_v3.py (modified)
Changes:
  - Adaptive LR: Bei 3x Plateau → LR -20% (0.1 → 0.08)
  - Pattern Source Rotation: task → failure → success → capability
  - Plateau Detection: novelty boost bei <1.5% Variation
State:
  - LR: 0.1 (noch nicht reduziert, Plateau nicht hart genug)
  - stagnation_count: 0
  - pattern_source: failure
  - Score: 0.768
```

### Phase 5 Self-Modifying Learning
```
Scripts: learning_rule_modifier.py (fixed + applied), evolver_meta_bridge.py (syntax fixed)
Applied Changes:
  - pattern_match_threshold: 0.6 → 0.7
  - generalization_min_score: 0.4 → 0.5
  - self_modification_enabled: true
Files modified:
  - learning_rule_modifier.py: load_data() liest jetzt rules aus file
  - evolver_meta_bridge.py: f-string syntax gefixt (\" escaped quotes)
```

### Cron Delivery Fix (2026-04-19)
```
- capability_probe_nightly: mode "announce" → "none" (läuft 02:00 UTC)
- Morning CEO Report: bleibt announce (8:00 UTC, user-facing)
- Phase 5 Reminder: deleted (nicht mehr nötig)
```

---

## 🟡 SYSTEM OPTIMIZATIONS (2026-04-19 16:45 UTC)

### 1. Event Bus Diversifikation
```
Script: learning_loop_v3.py (emit_learning_cycle_events)
New Events:
  - learning_score_update, learning_cycle_completed
  - learning_issues_detected, learning_patterns_update
  - learning_plateau_detected
```

### 2. Evolver Signal Bridge — Smarter Fallback
```
Fallback wenn keine starken Stagnation-Signale:
  - KG orphan >35% → kg_relation_reconstruction
  - LR stagnation >= 2 → learning_lr_reduction
  - Score <0.6 → learning_low_performance
  - All green → system_diagnostic_probe
```

### 3. Learning Loop Plateau Escape — Aggressiver
```
Plateau threshold: 0.015 → 0.010
Stagnation trigger: >= 3 → >= 2
LR-Reduktion: -20% → -30%
LR Floor: 0.01 → 0.005
```

---

## 🔴 KG ANALYSIS ERROR + FIX (2026-04-19)

```
FEHLER: Falsche KG Orphan-Analyse
=================================
Ich habe KG orphan detection falsch gemacht:
- Script: (ich selbst, integration_dashboard.py)
- Fehler: entity.get('relations', []) statt top-level relations zu prüfen
- KG hat Relations auf Top-Level (dict), nicht in Entity-Objects
- Hätte 99% Orphans报告显示 — falsch!
- Korrekt: 161 Orphans (33.8%) mit korrekter Top-Level-Relation-Analyse

KG STRUKTUR (wichtig!):
```json
{
  "entities": { "name": { "type": "...", "facts": [...] } },
  "relations": { "0": { "from": "EntityA", "to": "EntityB", "type": "..." } }
}
```
- entities: DICT (nicht list)
- relations: DICT (nicht list) — Top-Level!
- Orphan = Entity dessen Name nicht in irgendeiner Relation's from/to vorkommt

KORREKTE ORPHAN DETECTION:
```python
linked = set()
for r in kg['relations'].values():
    linked.add(r['from'])
    linked.add(r['to'])
orphan_count = len(entities.keys() - linked)
```

SCRIPTE DIE ICH GEPRÜFT HABE:
- data_agent.py: ✅ Korrekt (handelt both dict/list)
- capability_probe.py: ✅ Korrekt (Top-Level)
- health_monitor.py: ✅ Korrekt (len(dict) = count)
- integration_dashboard.py: ❌ FALSCH → GEFIXT
- stagnation_detector.py: ✅ Keine orphan detection (Event-basiert)
```

---

## 📊 RECALL INDEX

| Frage | Lese aus |
|-------|----------|
| Was heute passiert | `memory/2026-04-18.md` |
| Deep Audit | `docs/DEEP_AUDIT_REPORT_20260418.md` |
| System Architektur | `docs/architecture/INDEX.md` |
| Security Learning | `MEMORY.md` (dieses File) |

---

*MEMORY.md = Core Memory. Flüchtige Details → daily notes.*
