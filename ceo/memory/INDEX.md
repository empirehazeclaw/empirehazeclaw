# 🧠 MEMORY INDEX — [NAME_REDACTED]

## System Overview
- **Letzte Aktualisierung:** 2026-04-13
- **Struktur:** 4-Typen System (Short-term, Long-term, Episodes, Procedural)
- **Backup Location:** `/workspace/ceo_backup_2026-04-13_1953/`

---

## 📁 Memory Struktur

```
ceo/memory/
├── INDEX.md              ← Diese Datei (Übersicht)
├── short_term/           # Context Window — aktuelle Sessions
│   ├── current.md        # Aktuelle Session
│   └── recent_sessions.md # Letzte 7 Tage
├── long_term/            # Semantic Memory — Fakten & Learnings
│   ├── facts.md          # Fakten über [NAME_REDACTED], System, Business
│   ├── preferences.md    # Preferences & Learnings
│   └── patterns.md       # Erkannte Patterns
├── episodes/             # Episodic Memory — Key Events
│   └── timeline.md        # Key Events Timeline
├── procedural/           # Procedural Memory — Workflows & Regeln
│   ├── workflows.md       # Workflows & Prozesse
│   ├── rules.md          # Regeln & Richtlinien
│   └── skills.md         # Skills & Capabilities
├── kg/                   # Knowledge Graph
│   └── knowledge_graph.json  # 354 entities, 523 relations
├── search/               # Hybrid Search Engine
│   ├── memory_hybrid_search.py
│   └── memory_reranker.py
└── notes/                # Permanent Notes (aus core_ultralight)
    ├── 2026-03-29-final-test-note.md
    ├── 2026-03-29-test-note.md
    ├── 2026-04-07-RECOVERED-memory-system.md
    ├── 2026-04-08-daily-operations.md
    ├── 2026-04-08-weekly-reflection.md
    ├── 2026-04-08-wiki-growth-workflow.md
    ├── 2026-04-09-lcm-wiki.md
    └── 2026-04-09-weekly-reflection.md
```

---

## 🔍 Access Patterns

| Frage | Lese aus |
|-------|----------|
| "Was ist gerade passiert?" | `short_term/current.md` |
| "Was haben wir letzte Woche gemacht?" | `short_term/recent_sessions.md` |
| "Was weiß ich über [NAME_REDACTED]?" | `long_term/facts.md` |
| "Was habe ich gelernt?" | `long_term/preferences.md` |
| "Welche Patterns gibt es?" | `long_term/patterns.md` |
| "Was ist wichtiges passiert?" | `episodes/timeline.md` |
| "Wie machen wir X?" | `procedural/workflows.md` |
| "Was sind die Regeln?" | `procedural/rules.md` |
| "Welche Skills habe ich?" | `procedural/skills.md` |
| "Suche nach Konzept X" | `search/memory_hybrid_search.py` |
| "Was weiß ich über Y?" | `kg/knowledge_graph.json` |
| "Permanente Notes zu X?" | `notes/*.md` |

---

## 🔄 Migration Info

- **Datum:** 2026-04-13 19:53 UTC
- **Backup:** `/workspace/ceo_backup_2026-04-13_1953/`
- **Migriert von:**
  - `/workspace/MEMORY.md` → `long_term/facts.md`
  - `/ceo/MEMORY.md` → `long_term/preferences.md`
  - `/core_ultralight/memory/notes/` → `notes/`
  - `/core_ultralight/memory/kg.json` → `kg/`

---

## 📊 System Stats

| Metric | Value |
|--------|-------|
| KG Entities | 354 |
| KG Relations | 523 |
| Permanent Notes | 8 |
| Scripts | 47 |
| Active Crons | 27 |

---

*This index is the single source of truth for our memory system.*