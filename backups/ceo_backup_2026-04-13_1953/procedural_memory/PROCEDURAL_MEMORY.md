# 🧠 Procedural Memory — Mem^p Style
*Erstellt: 2026-04-09 23:01 UTC*

---

## 📋 Konzept

Automatisch repetitive Tasks erkennen:
- Wenn Task X >3x vorkommt → Pattern erkannt
- Vorschlag: Automatisierung oder Skill erstellen
- "Procedural Memory" — Agent weiß was er tun muss

---

## 🔍 Erkannte Patterns

| Pattern | Threshold | Aktion |
|---------|-----------|--------|
| Gleicher Task-Type >3x | 3 | Skill-Vorschlag |
| Gleicher Error >2x | 2 | Error-Solution paaren |
| Gleiche Sequence >2x | 2 | Workflow vorschlagen |
| Cron läuft >5x fehl | 5 | Debug-Vorschlag |

---

## 📊 Pattern-Template

```json
{
  "pattern_id": "pat_XXXXX",
  "type": "task_sequence|error_repeat|workflow",
  "occurrences": 5,
  "first_seen": "2026-04-09",
  "last_seen": "2026-04-09",
  "suggestion": {
    "action": "automation|skill|script",
    "description": "Was wir vorschlagen",
    "priority": "high|medium|low"
  },
  "evidence": [
    {"task": "X", "date": "2026-04-09"},
    {"task": "X", "date": "2026-04-10"}
  ]
}
```

---

## 🔄 Pattern Detection Loop

```
Täglich ( Opportunity Scanner ):
    ↓
Analysiere Task History
    ↓
Suche nach Patterns:
    ↓
Gefunden → Pattern Dokument
    ↓
Schwelle überschritten?
    ↓
Ja → Skill/Automation vorschlagen
Nein → Beobachten
```

---

## 📁 Speicherort

- `/workspace/ceo/procedural_memory/patterns/`
- `/workspace/ceo/procedural_memory/suggestions/`

---

*Erstellt: 2026-04-09 — Procedural Memory v1*