# 🧠 Skill Library Index
**Created:** 2026-04-11
**Purpose:** Wiederverwendbare Workflow-Templates

---

## Verfügbare Skills

| Skill | Category | Beschreibung |
|-------|----------|---------------|
| [debugging_workflow.md](debugging_workflow.md) | debugging | Error Debugging流程 |
| [research_workflow.md](research_workflow.md) | research | Recherche流程 |
| [coding_workflow.md](coding_workflow.md) | coding | Script Erstellung |

---

## Usage

### Nach einem Task:
```bash
python3 scripts/pattern_extractor.py \
    --task "Was ich getan habe" \
    --outcome "✅ Erfolg" \
    --category debugging
```

### Skill laden:
Beim Debugging: Nutze `debugging_workflow.md` als Checkliste

---

## Pattern Checkliste

Nach jedem Task frage ich mich:
1. ✅ Was habe ich gelernt?
2. ✅ Was könnte ich wiederverwenden?
3. ✅ Was sollte ich beim nächsten Mal anders machen?

→ Falls wichtig: `pattern_extractor.py` mit Learnings

---

## Neue Skills hinzufügen

1. Neues `.md` File in `/skills/_library/`
2. Index hier aktualisieren
3. Pattern nach Template dokumentieren
