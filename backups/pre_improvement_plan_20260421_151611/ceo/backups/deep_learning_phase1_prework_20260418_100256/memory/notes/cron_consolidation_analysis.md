# Cron Consolidation Analysis
**Datum:** 2026-04-17

---

## 🔴 Redundante Crons (können zusammengelegt werden)

### 1. Morning Crons (06:00 - 10:00) — 5 Crons
| Cron | Zeit | Überlappend? |
|------|------|--------------|
| Morning Data Kitchen | 06:00 | ❌ Einzigartig |
| Morning Status Check | 09:00 | ⚠️ Goal Tracker Daily = 09:00 |
| Goal Tracker Daily | 09:00 | ⚠️ Morning Status Check = 09:00 |
| Learning Coordinator | 09:00 | ⚠️ 3x 09:00 |
| Goal Alerts Daily | 10:00, 18:00 | ⚠️ Overlap mit Learning Coordinator |
| CEO Weekly Review | 10:00 | ⚠️ Goal Alerts = 10:00 |

**Vorschlag:** Morning Status Check + Goal Tracker Daily + Learning Coordinator (Morning) zu **einem** "Morning Briefing" Cron zusammenfassen.

---

### 2. 6-Stunden Crons — 3 Crons
| Cron | Intervall | Überlappend? |
|------|-----------|--------------|
| Stagnation Detector | 6h | ⚠️ Gleiche Zeit |
| Context Compressor | 6h | ⚠️ Gleiche Zeit |
| Cron Watchdog | 6h | ⚠️ Gleiche Zeit |

**Vorschlag:** Zu **einem** "System Maintenance" Cron zusammenfassen (führt alle 3 aus).

---

### 3. Learning-bezogene — 2 Crons mit Overlap
| Cron | Zeit | Überlappend? |
|------|------|--------------|
| Learning Core Hourly | Hourly | ❌ Einzigartig |
| Learning Coordinator | 09:00, 18:00 | ⚠️ Learning Core = stündlich |
| Goal Alerts Daily | 10:00, 18:00 | ⚠️ Learning Coordinator = 18:00 |

**Vorschlag:** Learning Coordinator 18:00 + Goal Alerts 18:00 = **ein** Evening Cron.

---

## 🟡 Potentielle Verbesserungen

### 1. 15-Minuten Crons — 3 Crons
- Gateway Recovery: alle 15min
- Agent Delegation Cron: alle 15min
- Autonomy Supervisor: alle 5min

**Analyse:** Diese sind verschieden — Gateway Recovery checkt Gateway, Agent Delegation delegiert Tasks, Autonomy Supervisor überwacht整个 System. **Kein Overlap.**

---

### 2. Daily Crons am selben Tag
- GitHub Backup: 23:00
- Evening Capture: 21:00
- KG Auto-Prune: 02:00
- Memory Dreaming: 04:40

**Analyse:** Alle unterschiedliche Zeiten, **kein Overlap.**

---

## 📊 Consolidation Plan

### Zusammenfassen (MED Impact):
1. **Morning Briefing Cron** (NEW)
   - Führt aus: Morning Status Check + Goal Tracker Daily + Learning Coordinator (09:00)
   - Schedule: 09:00 daily
   - Crons to disable: Morning Status Check, Goal Tracker Daily, Learning Coordinator (morning part)

2. **System Maintenance Cron** (NEW)
   - Führt aus: Stagnation Detector + Context Compressor + Cron Watchdog
   - Schedule: 6h interval (00:00, 06:00, 12:00, 18:00)
   - Crons to disable: Stagnation Detector, Context Compressor, Cron Watchdog

3. **Evening Learning Cron** (NEW)
   - Führt aus: Learning Coordinator (18:00) + Goal Alerts (18:00)
   - Schedule: 18:00 daily
   - Crons to disable: Goal Alerts Daily (da 10:00 erhalten bleibt)

---

## ⚠️ Risks

- Neue Crons könnten Bugs haben
- Zusammengelegte Crons brauchen längere timeout
- Nico bekommt weniger granular Reports

---

## ✅ Empfohlene Action

**Erst: System Maintenance Cron testen** (geringstes Risk)
- Zusammenlegung von 3 identischen 6h Crons
- Timeout muss erhöht werden (~60s → ~180s)

**Dann: Morning Briefing Cron** (mittleres Risk)
- 3 Crons um 09:00 zusammen
- Report consolidation

**Letzt: Evening Learning Cron** (höchstes Risk)
- Learning Coordinator ist komplex
- erst wenn andere stabil laufen

---

## Einsparungen

| Consolidation | Crons Gespart | Neue Crons |
|--------------|----------------|-------------|
| System Maintenance | 3 → 1 | 1 |
| Morning Briefing | 3 → 1 | 1 |
| Evening Learning | 2 → 1 | 1 |
| **Total** | **8 → 3** | **3** |

**Netto: 5 Crons weniger** (29 → 24)
