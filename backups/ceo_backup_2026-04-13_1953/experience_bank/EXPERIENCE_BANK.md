# 🧠 Erfahrungs-Bank — ExpeL Style
*Erstellt: 2026-04-09 23:01 UTC*

---

## 📋 Konzept

Aus Erfolgen UND Fehlern lernen:
- Jeder Task wird dokumentiert mit Erfolg/Fehler
- Errors werden mit Solutions gepaart
- Erfahrungen fließen in Knowledge Graph ein

---

## 📊 Erfahrungs-Template

```json
{
  "experience_id": "exp_YYYYMMDD_XXX",
  "date": "2026-04-09",
  "agent": "Builder",
  "task_type": "script_creation",
  "outcome": "success|failed",
  "error": {
    "type": "timeout|permission|config|...",
    "message": "Error message",
    "root_cause": "Warum ist der Fehler passiert?"
  },
  "solution": {
    "action": "Was haben wir getan?",
    "result": "Hat es funktioniert?",
    "learned": "Was haben wir gelernt?"
  },
  "knowledge_graph_entries": [
    {
      "entity": "error_type",
      "relation": "solved_by",
      "target": "solution"
    }
  ]
}
```

---

## 🔄 Workflow

```
Task abgeschlossen
    ↓
QC validiert
    ↓
Erfahrungs-Dokumentation
    ↓
Error + Solution → Erfahrungs-Bank
    ↓
KG Update (wenn relevant)
```

---

## 📁 Speicherort

- `/workspace/ceo/experience_bank/`
- Pro Monat: `experience_YYYY_MM.json`
- Index: `experience_index.json`

---

## 🔍 Query-Möglichkeiten

- "Wie haben wir X gelöst?"
- "Welche Errors gibt es häufig?"
- "Was ist die Lösung für Error-Type Y?"

---

## 💡 Integration mit Knowledge Graph

Wenn eine Erfahrung dokumentiert wird:
1. Prüfe ob Entity für Error-Type existiert
2. Falls nicht: Erstelle Entity
3. Füge Relation hinzu: `error_type -solved_by→ solution`

---

*Erstellt: 2026-04-09 — ExpeL-inspired Experience Bank v1*