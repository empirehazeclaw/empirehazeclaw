# 🏗️ CLEAN SWEEP ARCHITECTURE BLUEPRINT
## Sir HazeClaw — Architektonischer Neuaufbau

**Erstellt:** 2026-04-13 07:39 UTC
**Status:** DRAFT — In Evaluation
**Version:** 1.0

---

## Executive Summary

Das aktuelle System ist über 6 Monate organisch gewachsen mit:
- **114 Scripts** in doppelten Verzeichnisstrukturen
- **3 SQLite DBs** (380MB+ fragmentiert)
- **3 Archive-Strukturen** ohne klare Trennung
- **48 Cron Jobs** mit Overlaps und Redundanzen

**Ziel:** Zero-Downtime Migration zu 5 klar getrennten Modulen.

---

## 1️⃣ ZIEL-ARCHITEKTUR: 5 CORE MODULES

```
┌─────────────────────────────────────────────────────────────────┐
│                    EMPIREHAZECLAW v2                             │
│                                                                 │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────────┐   │
│  │ MEMORY ENGINE │  │ ORCHESTRATOR  │  │ KNOWLEDGE GRAPH   │   │
│  │               │  │               │  │                   │   │
│  │ • Session     │  │ • Cron Jobs   │  │ • Entities        │   │
│  │ • Notes       │  │ • Subagents   │  │ • Relations       │   │
│  │ • Dreams      │  │ • Health      │  │ • Search         │   │
│  │ • Archive     │  │ • Recovery    │  │ • Insights       │   │
│  └───────┬───────┘  └───────┬───────┘  └─────────┬─────────┘   │
│          │                  │                    │              │
│          └──────────────────┼────────────────────┘              │
│                             │                                   │
│                    ┌────────▼────────┐                        │
│                    │   LEARNING      │                        │
│                    │   CORE          │                        │
│                    └────────┬────────┘                        │
│                             │                                   │
│          ┌──────────────────┼──────────────────┐                │
│          │                  │                  │                │
│  ┌───────▼───────┐  ┌───────▼───────┐  ┌───────▼───────┐      │
│  │ INFRASTRUCTURE │  │    SKILLS     │  │   SECURITY    │      │
│  └───────────────┘  └───────────────┘  └───────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2️⃣ MODUL-DEFINITIONEN

### MODULE A: MEMORY ENGINE
**Owner:** `SCRIPTS/memory_engine/`
**Verantwortung:** Alle Persistenz — Sessions, Notes, Dreams, Archive

### MODULE B: KNOWLEDGE GRAPH
**Owner:** `SCRIPTS/knowledge_graph/`
**Verantwortung:** Wissensrepräsentation, Semantic Search, Insights

### MODULE C: ORCHESTRATOR
**Owner:** `SCRIPTS/orchestrator/`
**Verantwortung:** Cron Scheduling, Subagent Management, Health, Recovery

### MODULE D: LEARNING CORE
**Owner:** `SCRIPTS/learning_core/`
**Verantwortung:** Self-Improvement, Research, Evaluation, Adaptation

### MODULE E: INFRASTRUCTURE
**Owner:** `SCRIPTS/infrastructure/`
**Verantwortung:** Backup, Git Sync, Security, Utilities

---

## 3️⃣ KONSOLIDIERUNGS-VORSCHLÄGE

| Aktuell | Vorschlag | Grund |
|---------|-----------|-------|
| `scripts/` + `SCRIPTS/` | Nur `SCRIPTS/` | Verwirrung vermeiden |
| `archive/`, `_archive/`, `ARCHIVE/` | Nur `_archive/consolidated/` | Klare Struktur |
| 8 learning_*.py | 1 learning_core.py + Submodules | Redundanz reduzieren |
| 3 evening_*.py (21:00) | 1 daily_review.py | Cron-Overlap |
| HEARTBEAT.md double-write | File locking oder Single writer | Race conditions |

---

## 4️⃣ MIGRATION-PFAD

### Phase 1: Foundation (Woche 1-2)
- Message-Bus implementieren
- Archive konsolidieren
- HEARTBEAT.md → Event-Sourced

### Phase 2: Data Consolidation (Woche 3-4)
- 3 DBs → 1 DB
- KG-Chunked Loading

### Phase 3: Module Extraction (Woche 5-8)
- MEMORY_ENGINE extrahieren
- KNOWLEDGE_GRAPH extrahieren
- ORCHESTRATOR extrahieren
- LEARNING_CORE extrahieren

### Phase 4: Cleanup (Woche 9-10)
- Legacy-Verzeichnisse auflösen
- Dokumentation neu schreiben
- Finaler Deploy: v2.0

---

## 5️⃣ ERFOLGS-METRIKEN

| Metrik | Aktuell | Ziel |
|--------|---------|------|
| DB Size (main.sqlite) | 380MB | <100MB |
| Archive-Strukturen | 3 | 1 |
| KG Load Time | ~2s (full) | <100ms (chunked) |
| HEARTBEAT Writes | 2 (racy) | 1 (atomic) |

---

*Letzte Änderung: 2026-04-13 07:39 UTC*
