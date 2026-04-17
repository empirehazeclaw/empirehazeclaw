# 🧹 Memory Cleaner Skill

**Author:** Sir HazeClaw 🦞
**Created:** 2026-04-17
**Purpose:** Automatische Memory Archivierung

---

## Was es tut

- Archiviert alte Daily Notes (>30 Tage)
- Behält INDEX.md und goals.json
- Behält die letzten 5 Daily Notes
- Erstellt ARCHIVE/-Struktur

---

## Nutzung

```bash
python3 /home/clawbot/.openclaw/workspace/skills/memory_cleaner/memory_cleaner.py
python3 /home/clawbot/.openclaw/workspace/skills/memory_cleaner/memory_cleaner.py --dry-run
python3 /home/clawbot/.openclaw/workspace/skills/memory_cleaner/memory_cleaner.py --aggressive
```

---

## Regeln

- **Max Age:** 30 Tage für Daily Notes
- **Keep:** INDEX.md, goals.json, letzte 5 daily notes
- **Archive:** memory/notes/ older files → ARCHIVE/
- **Archive:** memory/short_term/ older files → ARCHIVE/

---

## Status

✅ Dry Run erfolgreich getestet (2026-04-17)