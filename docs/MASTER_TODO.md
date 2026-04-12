# 📋 MASTER TODO — Sir HazeClaw
**Erstellt:** 2026-04-11 12:30 UTC
**Status:** KONSOLIDIERT aus 8+ TODO Files
**Letzte Änderung:** 2026-04-11 12:30 UTC

---

## ✅ BEREITS ERLEDIGT (2026-04-11)

| # | Task | Wer | Wann |
|---|------|-----|------|
| 1 | Cron Error Healer | Sir HazeClaw | 12:25 UTC |
| 2 | Learning Loop v2 | Sir HazeClaw | 12:15 UTC |
| 3 | Workspace Cleanup | Sir HazeClaw | 11:00 UTC |
| 4 | Memory Reranker | Sir HazeClaw | 11:00 UTC |
| 5 | Gateway Auto-Recovery | Sir HazeClaw | 10:00 UTC |
| 6 | Secrets Location Dokumentiert | Sir HazeClaw | 10:00 UTC |
| 7 | System Documentation | Sir HazeClaw | 11:00 UTC |
| 8 | P1: Script Konsolidierung (82→55) | Sir HazeClaw | 12:38 UTC |
| 9 | P2: Doku Konsolidierung (75→19) | Sir HazeClaw | 12:45 UTC |
| 10 | P3: Cost Budgeting | Sir HazeClaw | 12:52 UTC |
| 11 | P4: KG Lifecycle | Sir HazeClaw | 12:52 UTC |
| 12 | M1: Old Cron Jobs | Sir HazeClaw | 12:52 UTC |
| 13 | M3: Session Cleanup Cron | Sir HazeClaw | 12:52 UTC |

---

## 🔴 OFFENE TASKS — Nach Priorität

### P1: Script Konsolidierung (82 → 20)
**Problem:** 82 Scripts, meisten ungenutzt
**Owner:** Sir HazeClaw
**Deadline:** 2026-04-14

| # | Sub-Task | Status |
|---|----------|--------|
| 1 | Identifizieren welche Scripts aktiv genutzt werden | ⏳ OFFEN |
| 2 | Ungenutzte Scripts archivieren | ⏳ OFFEN |
| 3 | Dokumentation pro Script (Usage, Inputs, Outputs) | ⏳ OFFEN |

**Kriterien für Beibehalten:**
- [ ] Wird von mindestens 1 Cron genutzt
- [ ] Hat klare Dokumentation
- [ ] Wurde in den letzten 30 Tagen ausgeführt

---

### P2: Dokumentation Konsolidierung
**Problem:** Duplizierte Dokus (HEARTBEAT, DEEP_ANALYSIS, DUAL_LAYER...)
**Owner:** Sir HazeClaw
**Deadline:** 2026-04-12

| # | Sub-Task | Status |
|---|----------|--------|
| 1 | Alle Dokus identifizieren | ⏳ OFFEN |
| 2 | Duplikate zusammenführen | ⏳ OFFEN |
| 3 | Single-Source-Regel durchsetzen | ⏳ OFFEN |

**Doku-Struktur (eine Quelle pro Topic):**
```
HEARTBEAT.md      → Aktiver Status, Quick View
SYSTEM_ARCHITECTURE.md → Komplette Architektur
LEARNING_LOOP_OPTIMIZATION.md → Lern-Regeln
IMPROVEMENT_TODO.md     → Priorisierte Tasks
```

---

### P3: Cost Budgeting Implementieren
**Problem:** 5.1M Tokens/Month ohne Kontrolle
**Owner:** Sir HazeClaw
**Deadline:** 2026-04-13

| # | Sub-Task | Status |
|---|----------|--------|
| 1 | Token Tracking in Learning Coordinator | ⏳ OFFEN |
| 2 | Alert bei 80% Budget | ⏳ OFFEN |
| 3 | Auto-Disable bei 95% | ⏳ OFFEN |

**Budget:**
```
MONTHLY_BUDGET = 5_000_000 tokens
ALERT_80% = 4_000_000 tokens
CRITICAL_95% = 4_750_000 tokens
```

---

### P4: Knowledge Graph Lifecycle
**Problem:** KG wächst unbegrenzt (1.7MB, 180 Entities)
**Owner:** Sir HazeClaw
**Deadline:** 2026-04-15

| # | Sub-Task | Status |
|---|----------|--------|
| 1 | KG Deduplication Script | ⏳ OFFEN |
| 2 | Aging Policy (30 Tage ohne Zugriff → stale) | ⏳ OFFEN |
| 3 | Max 500 Entities Limit | ⏳ OFFEN |
| 4 | KG Lifecycle Cron (wöchentlich) | ⏳ OFFEN |

---

## 🟡 MITTLERE PRIORITÄT

### M1: Old Cron Jobs Aufräumen
**Problem:** Deaktivierte/verwaiste Cron-Jobs verursachen Confusion
**Owner:** Sir HazeClaw
**Status:** ⏳ OFFEN

**Zu entfernende Jobs:**
- Security - Phoenix Reschedule (b204feb7-...)
- Data - Phoenix Reschedule (f87c47dd-...)
- Builder - Sovereign One-Shot (90d83804-...)
- Research - Phoenix Reschedule (9416fd63-...)
- Data Manager - Sovereign One-Shot (70bde24b-...)
- Security Officer - Sovereign Daily (584f6e16-...)

---

### M2: Security Vetting Process
**Problem:** 824 ClawHub Skills 需要 Security Check
**Owner:** Security Officer
**Status:** 🔄 In Progress
**Details:**
- Vetting Scanner: `security/skill_vetting_rules.md`
- Blocklist: bereits erstellt

---

### M3: Opportunity Scanner
**Problem:** Kein automatischer Task-Finder
**Owner:** Sir HazeClaw (when Security Officer done)
**Status:** 💡 Idee
**Details:**
- Daily 09:00 UTC Scan
- Erkennt offene TODOs, idle Agents, Security-Gaps
- Report an CEO

---

## 🟢 NIEDRIGE PRIORITÄT

### N1: Adventure Engine Integration
**Problem:** Gamification fehlt
**Owner:** Builder
**Status:** ⏳ Offen
**Details:**
- Adventure Engine + Quiz bereits vorhanden
- Integration mit Team-Mechanics
- Agent-Stats: Tasks completed, Streaks, XP

### N2: MCP Protocol Evaluierung
**Problem:** Unknown if useful für Flotte
**Owner:** Builder
**Status:** ⏳ Offen

### N3: Session Cleanup Automation
**Problem:** 74 Sessions, 9 orphaned
**Owner:** Sir HazeClaw
**Status:** ✅ Script existiert (`session_cleanup.py`)
**Next:** Cron einrichten (täglich 03:00 UTC)

---

## 📊 KONSOLIDIERUNGS-ZUSAMMENFASSUNG

| Quelle | Alter Name | Neuer Status |
|--------|-----------|--------------|
| IMPROVEMENT_TODO.md | 20 Tasks | ✅ 12 done, 8 consolidated |
| TODO_IMPROVEMENTS.md | 8 Tasks | 🟡 2 done, 6 consolidated |
| BUILDER_AGENT_IMPROVEMENTS.md | 3 Tasks | 🟡 0 done, 3 consolidated |
| TIMEOUT_IMPROVEMENTS.md | 2 Tasks | 🟢 Custom Lanes blocked, Fire-and-Forget open |
| TODO.md | Security Audit | ✅ ALLES DONE |
| MASTER_TODO.md | Archivierung | ✅ ALLES DONE |
| RESEARCH_TODO.md | Research | 🟡 In Progress |
| memory/todo-tomorrow.md | Tomorrow | ⏳ Backlog |

---

## 📅 WOCHENPLAN

| Woche | Fokus |
|-------|-------|
| **KW15 (2026-04-07-13)** | Cleanup, Consolidation, Fix Errors |
| **KW16 (2026-04-14-20)** | Cost Budgeting, KG Lifecycle, Testing |
| **KW17 (2026-04-21-27)** | Adventure Engine, MCP Evaluation |

---

## ✅ FERTIG-MARKER

Wenn eine Task DONE ist:
1. In HEARTBEAT.md als ✅ markieren
2. Hier als ✅ markieren
3. Commit mit "DONE: <task name>"

---

*Konsolidiert: 2026-04-11 12:30 UTC*
*Sir HazeClaw — Solo Fighter*
