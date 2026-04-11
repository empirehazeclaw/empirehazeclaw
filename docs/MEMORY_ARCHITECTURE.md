# 🏗️ MEMORY ARCHITECTURE
## Sir HazeClaw Memory Systems

**Version:** 2.0
**Last Updated:** 2026-04-11
**Status:** Documented & Consolidated

---

## 📊 OVERVIEW

```
┌─────────────────────────────────────────────────────────────┐
│                    MEMORY SYSTEMS                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────┐     ┌─────────────────┐             │
│   │  Knowledge      │     │  Daily Notes     │             │
│   │  Graph          │◄────│  (memory/)      │             │
│   │  (1.7MB)        │     │  388KB           │             │
│   └────────┬────────┘     └────────┬────────┘             │
│            │                       │                       │
│            ▼                       ▼                       │
│   ┌─────────────────────────────────────────┐             │
│   │         Unified API (MEMORY_API.py)     │             │
│   └─────────────────────────────────────────┘             │
│                       │                                    │
│            ┌──────────┴──────────┐                        │
│            ▼                      ▼                        │
│   ┌─────────────────┐     ┌─────────────────┐             │
│   │  CEO Memory     │     │  Experience     │             │
│   │  (ceo/memory/)  │     │  Bank           │             │
│   │  468KB          │     │  (experience_)  │             │
│   └─────────────────┘     └─────────────────┘             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 SYSTEM 1: Knowledge Graph

**Location:** `/workspace/core_ultralight/memory/knowledge_graph.json`
**Size:** 1.7MB
**Type:** Entity-Relation Graph

### Structure
```json
{
  "entities": [
    {
      "id": "entity_1",
      "title": "Error Rate Reduction",
      "type": "pattern",
      "created": "2026-04-11T...",
      ...
    }
  ],
  "relations": [
    {
      "from": "entity_1",
      "to": "entity_2",
      "type": "related_to",
      "strength": 0.8
    }
  ],
  "last_updated": "2026-04-11T...",
  "created": "2026-04-09T..."
}
```

### Stats
| Metric | Value |
|--------|-------|
| Entities | 209 |
| Relations | 4659 |
| Load Time | ~15ms |
| Update Frequency | On new learnings |

### Related Files
- `semantic_index.json` — Search index (51 docs)
- `MASTER_INDEX.json` — File tracking (47 files)
- `CHRONOLOGY_ANONYMIZED.md` — Timeline view
- `MEMORY_ANONYMIZED.md` — Anonymized dump

### Scripts
| Script | Purpose |
|--------|---------|
| `kg_updater.py` | Add/update entities |
| `kg_enhancer.py` | Enrich with metadata |
| `kg_lifecycle_manager.py` | Weekly maintenance |
| `knowledge_graph.json.backup` | Auto-backup |

---

## 📓 SYSTEM 2: Daily Notes

**Location:** `/workspace/memory/`
**Size:** 388KB total
**Purpose:** Session logs, metrics, operational data

### Files
| File | Purpose |
|------|---------|
| `YYYY-MM-DD.md` | Daily session log |
| `session_metrics_history.json` | Session stats (28 entries) |
| `habit_tracker.json` | Habit tracking |
| `skill_metrics.json` | Skill performance |
| `evolution/` | Evolution tracking |
| `notes/fleeting/` | Fleeting notes |
| `research/` | Research data |

### Daily Log Format
```markdown
# 2026-04-11 — Daily Session Log

## Session Highlights
[Major events, decisions, learnings]

## Metrics
- Sessions: X
- Errors: Y
- Token Usage: Z

## Notes
[Additional observations]
```

---

## 👤 SYSTEM 3: CEO Memory

**Location:** `/workspace/ceo/memory/`
**Size:** 468KB
**Purpose:** Personal agent memory, session-specific data

### Structure
```
ceo/memory/
├── INDEX.md              # Navigation
├── daily/                # Session logs (33 files)
│   ├── 2026-04-07*.md
│   ├── 2026-04-08*.md
│   └── ...
├── learnings/           # Extracted learnings
├── projects/            # Project-specific (empty, ready to use)
└── .dreams/            # Short-term recall
```

### Purpose of Each Folder
| Folder | Purpose | Auto-created |
|--------|---------|--------------|
| `daily/` | Session logs by date | Yes |
| `learnings/` | Extracted patterns | Weekly |
| `projects/` | Project memories | Manual |
| `.dreams/` | Short-term recall | Yes |

---

## 🎓 SYSTEM 4: Experience Bank

**Location:** `/workspace/ceo/experience_bank/`
**Size:** 60KB
**Purpose:** Structured learned experiences

### Files
| File | Purpose |
|------|---------|
| `EXPERIENCE_BANK.md` | Documentation |
| `experience_2026-04.json` | Extracted experiences |
| `experience_index.json` | Index |
| `extract_experiences.py` | Extraction script |

### Experience Format
```json
{
  "experiences": [
    {
      "id": "exp_session_123",
      "source": "2026-04-11 session",
      "type": "learned_pattern",
      "extracted": "2026-04-11T...",
      "content": "..."
    }
  ]
}
```

---

## 🔍 SYSTEM 5: Memory Pipeline

**Location:** `/workspace/scripts/`
**Purpose:** Search, cleanup, maintenance

### Scripts

| Script | Purpose |
|--------|---------|
| `MEMORY_API.py` | Unified interface (NEW!) |
| `memory_hybrid_search.py` | Semantic + keyword search |
| `memory_reranker.py` | Result ranking |
| `memory_cleanup.py` | Consolidation + cleanup (v2) |

### Search Pipeline
```
Query → memory_hybrid_search.py
          │
          ├── Semantic Search (embeddings)
          │
          └── Keyword Search (BM25)
          
          ↓ (merged + ranked)
          
       memory_reranker.py
          
          ↓
       
       Results (ranked)
```

---

## 🗓️ AUTOMATION

### Crons
| Cron | Schedule | Purpose |
|------|----------|---------|
| Weekly Memory Cleanup | Sun 04:00 UTC | Consolidation + extraction |
| KG Lifecycle Manager | Sun 02:00 UTC | KG maintenance |
| Daily Auto Backup | Daily 03:00 UTC | Backup all memory |

### Health Checks
| Check | Frequency | Action |
|-------|-----------|--------|
| Dual daily notes | Weekly | Prevent duplication |
| CEO structure | Weekly | Validate organization |
| KG health | Weekly | Check size + entities |
| Semantic Index | Weekly | Validate populate |

---

## 📈 USAGE EXAMPLES

### Using MEMORY_API.py

```bash
# Check status
python3 scripts/MEMORY_API.py status

# Search
python3 scripts/MEMORY_API.py search "error rate"

# List entities
python3 scripts/MEMORY_API.py entities

# Get experiences
python3 scripts/MEMORY_API.py experiences
```

### Using memory_cleanup.py

```bash
# Run full cleanup
python3 scripts/memory_cleanup.py

# Dry run
python3 scripts/memory_cleanup.py --dry-run

# Extract experiences only
python3 scripts/memory_cleanup.py --extract-experiences
```

### Using memory_hybrid_search.py

```bash
# Search
python3 scripts/memory_hybrid_search.py "pattern"

# Search with filter
python3 scripts/memory_hybrid_search.py "learning" --limit 20
```

---

## 🔄 DATA FLOW

```
┌──────────────┐
│   Session    │
│   Activity   │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────┐
│     memory_cleanup.py (v2)       │
│  - Validates structure           │
│  - Extracts experiences           │
│  - Updates KG                     │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│       Knowledge Graph            │
│  - Entities (209)               │
│  - Relations (4659)             │
│  - Semantic Index (51 docs)     │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│       MEMORY_API.py             │
│  - Unified access               │
│  - Caching layer               │
│  - Search + retrieval          │
└──────────────────────────────────┘
```

---

## 🚨 TROUBLESHOOTING

### Problem: Dual Daily Notes
**Symptom:** Two files with same date in different locations
**Solution:** 
```bash
python3 scripts/memory_cleanup.py
```
Auto-detects and flags duplicates.

### Problem: Semantic Index Empty
**Symptom:** Search returns no results
**Solution:** Rebuild via `memory_hybrid_search.py` or run cleanup

### Problem: KG Too Large
**Symptom:** Slow load times (>1s)
**Solution:** `kg_lifecycle_manager.py` weekly cron handles this

### Problem: CEO Memory Messy
**Symptom:** Too many files in root
**Solution:**
```bash
# Check structure
python3 scripts/memory_cleanup.py

# Files auto-move to daily/ on consolidation
```

---

## 📝 MAINTENANCE

### Weekly Tasks (Auto-run)
1. Memory cleanup (`memory_cleanup.py`)
2. KG lifecycle (`kg_lifecycle_manager.py`)
3. Backup (`auto_backup.py`)

### Monthly Tasks (Manual)
1. Review experience bank
2. Clean up orphaned entities
3. Archive old daily notes (>90 days)

---

## 🎯 SUCCESS METRICS

| Metric | Target | Current |
|--------|--------|---------|
| Memory Systems | 3 unified | ✅ 3 |
| CEO Memory Files | <10 in root | ✅ 0 |
| KG Load Time | <100ms | ✅ 15ms |
| Search Latency | <500ms | ✅ ~200ms |
| Experience Reuse | 10+/week | 📋 Tracking |

---

*Document Version: 2.0*
*Last Major Update: 2026-04-11 (Consolidation Phase 2)*
