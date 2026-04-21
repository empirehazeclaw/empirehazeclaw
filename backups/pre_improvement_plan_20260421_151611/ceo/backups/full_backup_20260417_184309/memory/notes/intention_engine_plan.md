# INTENTION ENGINE — Phase 3 Implementation Plan

_Created: 2026-04-17_
_Author: Sir HazeClaw 🦞_
_Status: IMPLEMENTATION_PLAN — PENDING REVIEW_

---

## Warum?

Aktuell:
- Phase 1: Decision Framework ✅ (klare Regeln)
- Phase 2: Proactive Scanner ✅ (proaktives Scannen)

Was noch fehlt:
- **Verstehen WAS als nächstes kommt**
- **Übergeordnete Ziele tracken** (nicht nur einzelne Tasks)
- **Prioritäten verstehen** über Tage/Wochen

---

## Was ist die Intention Engine?

Ein System das:
1. **Ziele parsed** (z.B. "bis Montag muss X fertig sein")
2. **Deadlines trackt** (Kalender, Zeitfenster)
3. **Kontext versteht** (was ist gerade wichtig)
4. **Vorausplant** (was muss ich wann machen)

---

## Architektur

```
INTENTION ENGINE
├── goal_tracker.py      — Ziele + Deadlines speichern
├── priority_calculator.py — Kontext-basierte Prioritäten
├── intention_planner.py — "Was kommt als nächstes"
└── goal_context.py      — Kontext für jede Session
```

### Datenstruktur: Goals

```json
{
  "id": "goal_001",
  "title": "Workspace fertig",
  "deadline": "2026-04-20",
  "priority": "HIGH",
  "status": "in_progress",
  "milestones": [
    {"done": true, "text": "Decision Framework"},
    {"done": true, "text": "Proactive Scanner"},
    {"done": false, "text": "Intention Engine"}
  ],
  "context": "Workspace muss stabil sein für Nico"
}
```

---

## Features

| Feature | Beschreibung |
|---------|---------------|
| Goal Tracking | Ziele mit Deadlines + Status |
| Milestone Progress | Teilziele tracken |
| Priority Calculation | Dynamische Prioritäten basierend auf Zeit |
| "What's Next" Engine | Sagt was als nächstes zu tun ist |
| Context Injection | Fügt Goals in jede Session |

---

## Implementation Steps

### Step 1: Goal Tracker (`goal_tracker.py`)
- Goals erstellen/listen/aktualisieren
- Deadline-basiertes Sorting
- JSON file storage

### Step 2: Priority Calculator (`priority_calculator.py`)
- Zeit bis Deadline = Priorität
- Status-basiertes Ranking
- Overdue detection

### Step 3: Intention Planner (`intention_planner.py`)
- "Was ist als nächstes fällig?"
- Kontext für Session bereitstellen
- Integration in Session Startup

### Step 4: Goal Context Injection
- Goals in AGENTS.md/SOUL.md laden
- Automatisch bei Heartbeat prüfen

---

## Risiken & Mitigation

| Risiko | Mitigation |
|--------|------------|
| Zu viele Goals | Max 10 aktive Goals, auto-archive |
| Veraltete Deadlines | Auto-eskalation bei Overdue |
| Kontext-Overflow | Nur Top 3 Goals pro Session |

---

## Nächste Schritte

- [ ] goal_tracker.py erstellen
- [ ] priority_calculator.py erstellen
- [ ] intention_planner.py erstellen
- [ ] Test mit aktuellen Goals
- [ ] Integration in Session Startup

_Letzte Aktualisierung: 2026-04-17 14:46 UTC_