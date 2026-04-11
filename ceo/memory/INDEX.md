# 📚 CEO Memory Index

**Last Updated:** 2026-04-11 21:10 UTC

## 📁 Structure

```
ceo/memory/
├── INDEX.md                    # This file
├── todo-tomorrow.md           # Tomorrow's priorities
├── daily/                      # Daily session logs (33 files)
│   ├── 2026-04-07*.md
│   ├── 2026-04-08*.md
│   ├── 2026-04-09*.md
│   ├── 2026-04-10*.md
│   ├── 2026-04-11.md
│   └── 2026-04-11.md.archived # Merged from dual daily
├── learnings/                 # Extracted learnings
├── projects/                  # Project-specific memories
│   ├── evolver/
│   ├── heartbeat/
│   └── capability/
└── .dreams/                   # Short-term recall
```

## 📊 Statistics

| Folder | Files | Description |
|--------|-------|-------------|
| daily/ | 33 | Session logs organized by date |
| learnings/ | ? | Extracted learnings from sessions |
| projects/ | 0 | Project-specific memories (empty, to use) |
| .dreams/ | ? | Short-term recall |

## 🔄 Consolidation Status

| Date | Status |
|------|--------|
| 2026-04-07 | ✅ Moved to daily/ |
| 2026-04-08 | ✅ Moved to daily/ (8 files) |
| 2026-04-09 | ✅ Moved to daily/ (8 files) |
| 2026-04-10 | ✅ Moved to daily/ (16 files) |
| 2026-04-11 | ✅ Merged + Archived |

## 💡 Usage

**Adding new memories:**
1. Daily logs → auto-created by system
2. Learnings → extracted by `extract_experiences.py`
3. Projects → create folder in `projects/`

**Finding information:**
1. Search memory: `memory_hybrid_search.py "query"`
2. Search KG: Check `core_ultralight/memory/knowledge_graph.json`
3. Browse daily: `ls ceo/memory/daily/`
