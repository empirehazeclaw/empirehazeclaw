# KG & Memory Cleanup — Sir HazeClaw

## ⚠️ Wichtig: Cleanup-Regeln

Beim Bereinigen von KG und Memory IMMER diese Regeln beachten:

---

## ❌ DARF ENTFERNT WERDEN

### 1. Internal Signals (keine echten Fakten)

| Pattern | Warum | Beispiel |
|---------|-------|----------|
| `rem_theme_*` | Rein interne Traffic-Tracker. Enthalten keineuser Information. | `rem_theme_home/clawbot` mit "recalled 1242 times" |
| `rem_*` patterns | Ebenfalls nur interne Signale | `rem_...` |

### 2. Orphan Garbage

| Condition | Warum |
|-----------|-------|
| Entity hat 0 facts | Keine Information vorhanden |
| Entity ist orphan (keine relations) | Unverbunden |

→ **AUCH wenn** das Entity einen "echten" Namen hat, aber weder Fakten noch Relations hat → es ist nutzloser Datenmüll.

---

## ❌ DARF NICHT ENTFERNT WERDEN

### 1. Learning Loop Learnings

| Pattern | Warum | Enthält |
|---------|-------|---------|
| `success_improvement_cycle_*` | Learning Loop History | Echte Learnings aus 5 Kontexten |
| `failure_pattern_*` | Failure History | Echte Failure-Analysen |
| `improvement_*` | Self-Improvement Results | Verbesserungs-Tracking |

### 2. Meta-Learning Patterns

| Pattern | Warum | Enthält |
|---------|-------|---------|
| `meta_pattern_*` | Meta-Learning Data | Generalization Scores, Pattern IDs |
| `LearningPattern_*` | Echte Pattern | Erkannte Patterns mit Confidence |

### 3. Business Knowledge

| Pattern | Warum | Enthält |
|---------|-------|---------|
| `KI-Mitarbeiter` | Real business entity | Produkt-Kategorie |
| `Zielgruppe-KMU` | Business fact | Customer insight |
| `OpenClaw-Gateway` | Real entity | System-Wissen |
| `Stripe-Integration` | Real entity | Integration fact |

### 4. Research Knowledge

| Pattern | Warum | Enthält |
|---------|-------|---------|
| `research_*` | Echte Research | Knowledge gaps, topics |
| `innovation_*` | Innovation tracking | Research results |

### 5. System Patterns

| Pattern | Warum | Enthält |
|---------|-------|---------|
| `error_*` | Error tracking | Error patterns, solutions |
| `success_*` | Success patterns | Working approaches |
| `concept_*` | Konzepte | Abstract knowledge |
| `skill_*` | Skills | Capability information |
| `script_*` | Script-Wissen | Script-Evaluationen |
| `system_*` | System facts | System-Information |

---

## 📋 Cleanup-Checkliste (vor jedem Cleanup)

```
1. Hat das Entity Fakten?
   - NEIN + kein Business-Wissen → → ENTFERNEN
   - JA → weiter zu 2

2. Ist es ein Learning Loop / Meta-Learning Pattern?
   - JA (success_improvement_cycle_*, meta_pattern_*, etc.) → KEEP
   - NEIN → weiter zu 3

3. Ist es ein echtes Business/System/Research Fact?
   - JA → KEEP
   - NEIN → weiter zu 4

4. Hat es Relations (oder orphan mit 0 facts)?
   - orphan + 0 facts → ENTFERNEN
   - hat relations → KEEP
```

---

## 🔄 Automatisierte Cleanup-Crons

| Cron | Zeit | Funktion |
|------|------|----------|
| KG Orphan Cleaner Daily | 03:00 UTC | Entfernt Orphans >50% |
| Weekly Maintenance | Sunday 04:00 UTC | KG Backup + Cleanup |
| System Maintenance | every 6h | Stagnation + Context |

---

## 📊 KG Qualitäts-Metriken

| Metric | Gut | Schlecht |
|--------|-----|----------|
| Orphan % | <33% | >50% |
| Entity Count | stabil oder wachsend | plötzliche Einbrüche |
| Facts/Entity | >0.5 avg | <0.3 avg |

---

## ⚠️ Warnsignale für zu aggressives Cleanup

- Learning Loop Score sinkt plötzlich
- improvement_* entities verschwinden
- Meta-patterns verschwinden
- Error/Success Patterns verschwinden

→ In diesem Fall: Backup wiederherstellen und Cleanup-Regeln überprüfen.

---

## 🛡️ Backup-Strategie

Vor jedem Cleanup:
1. Automatisches Backup wird erstellt (via KGCleaner)
2. Backup-Path: `memory/kg/knowledge_graph_backup_YYYYMMDD_HHMMSS.json`
3. Im Notfall: Backup zurückspielen

---

_Letzt aktualisiert: 2026-04-20_
_Fehler gemacht: success_improvement_cycle_* wurde versehentlich gelöscht → wiederhergestellt_