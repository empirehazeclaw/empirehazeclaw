# 📋 Struktur & Übersicht — Master Improvement Plan

**Erstellt:** 2026-04-17  
**Status:** 🔍 Evaluierungphase  
**Quelle:** Research aus Best Practices + Eigenanalyse

---

## 📊 Research Key Insights

### From Web Search (2026-04-17)

| Source | Key Insight |
|--------|-------------|
| **Mem0 / AgentCore** | Drei Memory-Typen: Semantic (Fakten), Episodic (Erfahrungen), Procedural (Skills) |
| **Reddit r/AI_Agents** | "Keep it simple, searchable, always updated. Agents won't use it if it's cluttered or outdated." |
| **AddyOsmani** | "Each improvement makes future ones easier — compound effect through AGENTS.md" |
| **Databricks** | Evaluator-Loop: evaluate → reflect → refine |
| **IBM AI Docs** | "AI can automatically reflect code changes in docs" |
| **Oracle** | "Start with simplest loop that works. Only add complexity when you can measure improvement." |
| **Claude Code Docs** | Persistent memory via CLAUDE.md — conversation-only instructions persist |
| **Redis** | Short-term = session context; Long-term = survives restarts |

---

## 🔍 Current State Analysis

### ✅ What's Working
```
memory/
├── long_term/           ✅ Fresh but structured
│   ├── facts.md
│   ├── preferences.md
│   └── patterns.md
└── notes/
    ├── SYSTEM_ARCHITECTURE.md     ✅
    ├── SCRIPT_KATALOG.md          ✅
    └── smart-evolver-integration.md ✅
```

### ⚠️ Problems Identified

| # | Problem | Impact | Root Cause |
|---|---------|--------|------------|
| 1 | **21 Archiv-Scripts** in `SCRIPTS/automation/` | Verstopft Liste, täuscht Zustand vor | Keine echte Archivierung |
| 2 | **Doku nicht selbstaktualisierend** | Veraltet schnell | Kein Maintenance-Trigger |
| 3 | **Notes ohne System** | Chaos wenn neue hinzukommen | Keine Sortier-Regeln |
| 4 | **`long_term/` nicht getestet** | Niemand weiß ob es nach Restart funktioniert | Zu neu |
| 5 | **Kein Versionstracking für Docs** | Änderungen nicht nachvollziehbar | Kein Git-Workflow für Docs |
| 6 | **SCRIPT_KATALOG.md wird veralten** | Scripte ändern sich, Index wird falsch | Kein Sync-Mechanismus |

---

## 🎯 Best Practices aus Research

### Memory Architecture (Mem0/AgentCore Pattern)
```
┌─────────────────────────────────────────────────────┐
│                 MEMORY HIERARCHY                     │
├─────────────────────────────────────────────────────┤
│  WORKING    │  Short-term, session-bound            │
│  EPISODIC   │  Experiences, completed events       │
│  SEMANTIC   │  Facts, knowledge, learned concepts  │
│  PROCEDURAL │  Skills, how-tos, workflows         │
└─────────────────────────────────────────────────────┘
```

### Documentation Best Practices
1. **Single topic per doc** — Concise, focused, clearly structured
2. **Living docs** — "Treat it like a living doc, not a static one"
3. **Self-updating where possible** — AI reflects changes in docs
4. **Searchable** — Names like `Product_setup_guide_2024.pdf`, not `Manual_v2_final.pdf`
5. **Version control** — Audit trail for changes

### Self-Improving Agent Loop
```
┌──────────────┐
│   OBSERVE    │  Collect signals, logs, feedback
└──────┬───────┘
       ▼
┌──────────────┐
│   EVALUATE   │  Check against patterns, measure
└──────┬───────┘
       ▼
┌──────────────┐
│   REFLECT   │  Extract learnings, update memory
└──────┬───────┘
       ▼
┌──────────────┐
│   IMPROVE   │  Apply fix, validate, document
└─────────────┘
```

---

## 📋 Master Plan — Phase 1 bis 4

### PHASE 1: Aufräumen (Dauer: 1-2h)
**Ziel:** Codebase spiegelt Realität wider

- [ ] **1.1** Backup erstellen (vor allen Änderungen)
- [ ] **1.2** Archiv-Scripts identifizieren (21 alte Scripts)
- [ ] **1.3** Archive verschieben → `SCRIPTS/_ARCHIVE/`
- [ ] **1.4** SCRIPT_KATALOG.md updaten (nur aktive Scripts)
- [ ] **1.5** Integrity Check: Alle aktiven Scripts syntaktisch valid

### PHASE 2: Notes Systematisieren (Dauer: 1h)
**Ziel:** Notes wachsen kontrolliert, veralten nicht

- [ ] **2.1** `notes/` strukturieren:
  ```
  notes/
  ├── _index.md          # Master Index (auto-generated)
  ├── SYSTEM/             # Architektur-Docs
  ├── SCRIPTS/            # Script-Docs
  ├── LEARNING/           # Learnings, Patterns
  ├── OPERATIONS/         # Runbooks, Procedures
  └── ARCHIVE/            # Alte/ersetzte Docs
  ```
- [ ] **2.2** Maintenance-Trigger definieren:
  - Wenn Script verschoben → SCRIPT_KATALOG.md updaten
  - Wenn System-Doc geändert → _index.md updaten
  - Wöchentlicher Doc-Review via Cron
- [ ] **2.3** _index.md erstellen (Master-Index aller Notes)
- [ ] **2.4** Doc-Audit Cron: prüft auf veraltete Docs

### PHASE 3: Memory Validieren (Dauer: 1h)
**Ziel:** `long_term/` funktioniert nach Restart

- [ ] **3.1** Test: Nach Restart prüfen ob `memory/long_term/` korrekt geladen
- [ ] **3.2** Memory-Integrity-Check Script erstellen
- [ ] **3.3** Session-Startup-Procedure dokumentieren
- [ ] **3.4** Long-Term Memory Audit (monatlich)

### PHASE 4: Self-Maintaining Docs (Dauer: 2-3h)
**Ziel:** Docs aktualisieren sich selbst wo möglich

- [ ] **4.1** Script-Tracker: Aktive Scripts in JSON → SCRIPT_KATALOG.md lesbar
- [ ] **4.2** Doc-Change-Log: Werden Docs in Git committed? Ja.
- [ ] **4.3** Learning-Loop Integration: Verbesserungen reflektieren sich in Docs
- [ ] **4.4** Auto-Doc-Generator für neue Scripts (Template)

---

## ⚖️ Evaluation: Plancritic

### Strengths
- Klare Phasen, logische Reihenfolge
- Research-grounded (Mem0, AddyOsmani, etc.)
- addressiert alle 6 identifizierten Probleme
- Mit Backup + Rollback vor Absturz geschützt

### Schwächen / Risks
- **P1:** Archiv-Scripts verschieben ändert Pfade → Crons die Pfade hardcoden?
- **P2:** Notes-Umbau braucht möglicherweise Update aller Referenzen
- **P3:** Memory-Test braucht echten Restart-Simulator
- **P4:** Auto-Doc-Generator könnte Overhead werden

### Optimizations Applied
1. **Backup zuerst** → kein Risiko
2. **Symlinks statt verschieben** → pfade bleiben, nur Archiv-Flag
3. **Monitoring bevor Automation** → erst validieren, dann auto-generieren
4. **Incremental not Big-Bang** → jede Phase einzeln verifizierbar

---

## 🛡️ Backup & Rollback Strategy

### Vor Phase 1: Full Backup
```bash
# Timestamp: 2026-04-17_0625
cp -r /workspace /workspace_backup_20260417_0625
```

### Rollback Points
| After Phase | Rollback Command |
|-------------|------------------|
| Phase 1 | `rm -rf /workspace/SCRIPTS/_ARCHIVE && mv /workspace_backup_YYYYMMDD_HHMM/SCRIPTS/_ARCHIVE/* /workspace/SCRIPTS/` |
| Phase 2 | `mv /workspace/notes /workspace/notes_NEW && mv /workspace_backup/notes /workspace/` |
| Phase 3 | Kein Rollback nötig (nur Test-Scripts) |
| Phase 4 | `git checkout HEAD -- memory/notes/` |

### Checkpoints
- [ ] Nach P1: Alle Crons laufen noch?
- [ ] Nach P2: Alle Docs erreichbar via _index.md?
- [ ] Nach P3: `memory/long_term/facts.md` nach Restart vorhanden?
- [ ] Nach P4: SCRIPT_KATALOG.md zeigt aktiven Stand?

---

## 🚀 Execute Order

```
NOW     → Backup erstellen
PHASE 1 → Archiv-Scripts aufräumen
PHASE 2 → Notes strukturieren  
PHASE 3 → Memory validieren
PHASE 4 → Self-Maintaining_docs
```

---

*Sir HazeClaw — Structure Master Plan*
*Basierend auf: Mem0, AgentCore, AddyOsmani, Oracle, Databricks, IBM, Claude Code Docs Research*
