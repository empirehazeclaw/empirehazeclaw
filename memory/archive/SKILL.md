---
name: knowledge-brain
description: Second Brain System - Unified mit memory/. Zettelkasten-Methode: Atomic Notes, Backlinks, Tags, und Reviews.
---

# 🧠 Knowledge Brain - Second Brain Skill

**Symbiose aus chronologischen memory/ + Zettelkasten-Methode**

## Unified Structure

```
memory/
├── MEMORY.md              ← Haupt-Kontext
├── daily/                 ← Tägliche Logs
├── decisions/              ← Entscheidungen
├── learnings/              ← Lessons
├── projects/                ← Projekte
│
├── notes/                  ← ATOMIC NOTES (Zettelkasten)
│   ├── ideas/              ← Neue Ideen
│   ├── insights/            ← Erkenntnisse
│   ├── concepts/            ← Know-How
│   └── learnings/           ← Learnings
│
├── tags/                    ← TAG HIERARCHIE
│   └── README.md            ← Tag-Dokumentation
│
├── backlinks/               ← BACKLINK INDEX
│
└── scripts/                ← AUTOMATION
    ├── quick_capture.py     💡
    ├── add_link.py          🔗
    ├── suggest_links.py      🤝 (NEU)
    ├── weekly_review.py      📅
    └── daily_review.py       ⏰ (NEU)
```

## Scripts

| Script | Nutzung | Wann |
|--------|---------|------|
| `quick_capture.py` | Idee notieren | Täglich |
| `suggest_links.py` | Verbindungs-Vorschläge | Vor Review |
| `daily_review.py` | 5-Min Daily Review | Täglich |
| `weekly_review.py` | Vollständiges Weekly Review | Wöchentlich |
| `add_link.py` | Backlink hinzufügen | Bei Bedarf |

## Tag Hierarchy

```bash
#idea               - Neue Ideen
  #idea-marketing   - Marketing Ideen
  #idea-product     - Produkt Ideen
#learning          - Gelernte Lektionen
#project           - Projektbezogen
```

## Usage

```bash
# Idee notieren
python3 memory/scripts/quick_capture.py "Neue Idee" --tags idea,marketing

# Verbindungen vorschlagen lassen
python3 memory/scripts/suggest_links.py

# Daily Review (5 min)
python3 memory/scripts/daily_review.py

# Weekly Review
python3 memory/scripts/weekly_review.py
```

## Workflow

1. **Capture** → Schnell Idee notieren mit `quick_capture.py`
2. **Suggest** → `suggest_links.py` findet Verbindungen
3. **Link** → Mit `add_link.py` verlinken
4. **Review** → Täglich `daily_review.py`, Wöchentlich `weekly_review.py`

## Obsidian-Kompatibel

Alle Notes sind Plain Markdown mit `[[Wiki-Links]]` und `#Tags`.
Du kannst das direkt in Obsidian öffnen.

---

*Unified System - Built 2026-03-29*
