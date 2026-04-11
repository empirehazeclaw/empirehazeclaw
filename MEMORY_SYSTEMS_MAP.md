# 🗺️ MEMORY SYSTEMS MAP
## Comprehensive Documentation of All Memory Systems
**Generated:** 2026-04-11 21:03 UTC
**Author:** Sir HazeClaw

---

## 📊 EXECUTIVE SUMMARY

| System | Location | Size | Purpose | Status |
|--------|----------|------|---------|--------|
| Knowledge Graph | `core_ultralight/memory/` | 1.7MB | Main semantic memory | ✅ Active |
| Daily Notes | `memory/` | 388KB | Session logs & daily records | ✅ Active |
| CEO Memory | `ceo/memory/` | 468KB | Personal agent memory | ⚠️ Scattered |
| Experience Bank | `ceo/experience_bank/` | 60KB | Extracted learnings | ⚠️ Underused |
| Semantic Index | `core_ultralight/memory/` | 460KB | Search index | ❌ Empty |
| Master Index | `core_ultralight/memory/` | 9KB | Master reference | ❌ Empty |

---

## 🏛️ SYSTEM 1: Knowledge Graph (KG)

**Location:** `/workspace/core_ultralight/memory/`

**Files:**
```
knowledge_graph.json     (1.7MB)  - Main graph database
semantic_index.json      (460KB) - Search index (EMPTY!)
MASTER_INDEX.json        (9KB)   - Master reference (EMPTY!)
CHRONOLOGY_ANONYMIZED.md (3KB)   - Timeline view
MEMORY_ANONYMIZED.md     (24KB)  - Anonymized memory dump
META_SCHEMA_ANONYMIZED.md (9KB) - Schema documentation
notes/                   - Additional notes
```

**Structure:**
```json
{
  "entities": [...],      // 209 entities
  "relations": [...],      // 4659 relations  
  "relationships": [...], // Redundant
  "last_updated": "...",
  "created": "..."
}
```

**Scripts:**
- `kg_updater.py` - Updates knowledge graph
- `kg_enhancer.py` - Enhances KG with new data
- `kg_lifecycle_manager.py` - Manages entity lifecycle

**Purpose:** Central semantic memory for facts, entities, and relationships

**Status:** ⚠️ Semantic Index and Master Index are EMPTY - not being populated

---

## 📒 SYSTEM 2: Daily Notes

**Location:** `/workspace/memory/`

**Files:**
```
2026-04-10.md              - Yesterday's session log
2026-04-11.md              - Today's session log (12KB)
Daily_Review.md            - Daily review template
session_metrics_history.json - Session statistics (28 entries)
habit_tracker.json          - Habit tracking data
skill_metrics.json          - Skill performance metrics
github_stats.json           - Git statistics
timeout_rules.json          - Timeout configurations
session_analysis_*.json     - Session analysis reports
security_hardening_*.md    - Security documentation
evolution/                  - Evolution tracking data
notes/fleeting/            - Fleeting notes
research/                   - Research data
shared/                     - Shared data
vault.enc.json             - Encrypted vault
```

**Purpose:** Daily session logs, metrics, and operational data

**Status:** ✅ Active - being written to daily

---

## 👤 SYSTEM 3: CEO Memory

**Location:** `/workspace/ceo/memory/`

**Files:**
```
2026-04-07.md              - Earliest CEO memory
2026-04-08.md              - Multiple sessions
2026-04-09-*.md            - Various sessions (11 files)
2026-04-10-*.md            - Various sessions (16 files)
2026-04-11.md              - Today (20KB!)
learnings/                 - Extracted learnings
.dreams/                   - Dream/short-term recall
todo-tomorrow.md           - Tomorrow's todo
```

**Purpose:** Personal agent memory, session-specific data

**Status:** ⚠️ Fragmented - too many files, no clear structure

---

## 🎓 SYSTEM 4: Experience Bank

**Location:** `/workspace/ceo/experience_bank/`

**Files:**
```
EXPERIENCE_BANK.md         - Documentation
experience_2026-04.json    - Extracted experiences (24KB)
experience_index.json      - Index of experiences
extract_experiences.py     - Extraction script
```

**Purpose:** Structured learned experiences for reuse

**Status:** ⚠️ Underused - exists but rarely queried

---

## 🔍 SYSTEM 5: Memory Pipeline Scripts

**Location:** `/workspace/scripts/`

**Scripts:**
```
memory_hybrid_search.py    - Hybrid search (semantic + keyword)
memory_reranker.py         - Reranks search results
memory_cleanup.py          - Cleanup and maintenance
kg_updater.py             - Updates knowledge graph
kg_enhancer.py            - Enhances KG
kg_lifecycle_manager.py   - Manages KG lifecycle
```

**Pipeline Flow:**
```
Query → memory_hybrid_search.py → memory_reranker.py → Results
                ↓
        Knowledge Graph Query
```

---

## 🚨 PROBLEMS IDENTIFIED

### 1. **Semantic Index EMPTY**
   - File exists (460KB) but has 0 entries
   - Hybrid search can't use it properly
   - **Fix:** Rebuild semantic index from KG

### 2. **Master Index EMPTY**
   - File exists (9KB) but has 0 entries
   - No master reference being maintained
   - **Fix:** Implement master index population

### 3. **Dual Daily Notes**
   - `/workspace/memory/2026-04-11.md` (12KB)
   - `/workspace/ceo/memory/2026-04-11.md` (20KB)
   - Same day, different locations!
   - **Fix:** Consolidate to ONE location

### 4. **Multiple notes/ directories**
   - `/workspace/core_ultralight/memory/notes/`
   - `/workspace/memory/notes/`
   - Purpose unclear, possible duplication
   - **Fix:** Audit and consolidate

### 5. **CEO Memory Fragmentation**
   - 30+ dated .md files in `ceo/memory/`
   - No clear structure or indexing
   - **Fix:** Implement proper CEO memory organization

---

## ✅ RECOMMENDATIONS

### Immediate Actions:
1. **Rebuild Semantic Index** - Populate from knowledge_graph.json
2. **Consolidate Daily Notes** - Choose ONE location for daily.md
3. **Audit notes/ directories** - Remove duplicates

### Short-term:
4. **Implement Master Index population** - Automated updates
5. **Organize CEO memory** - Folders by category, not date

### Long-term:
6. **Unified Memory API** - Single interface for all memory systems
7. **Automated cleanup** - Regular maintenance of all systems

---

## 📁 FILE TREE

```
/home/clawbot/.openclaw/workspace/
├── core_ultralight/
│   └── memory/
│       ├── knowledge_graph.json    (1.7MB) ← MAIN KG
│       ├── semantic_index.json     (EMPTY!)
│       ├── MASTER_INDEX.json       (EMPTY!)
│       ├── CHRONOLOGY_ANONYMIZED.md
│       ├── MEMORY_ANONYMIZED.md
│       ├── META_SCHEMA_ANONYMIZED.md
│       └── notes/
│
├── memory/                          ← DAILY OPERATIONS
│   ├── 2026-04-10.md
│   ├── 2026-04-11.md               ← Daily log
│   ├── session_metrics_history.json
│   ├── habit_tracker.json
│   ├── evolution/
│   ├── notes/fleeting/
│   └── research/
│
├── ceo/
│   ├── memory/                      ← CEO PERSONAL (FRAGMENTED!)
│   │   ├── 2026-04-07.md
│   │   ├── 2026-04-08*.md (multiple)
│   │   ├── 2026-04-09*.md (multiple)
│   │   ├── 2026-04-10*.md (multiple)
│   │   ├── 2026-04-11.md
│   │   ├── learnings/
│   │   ├── .dreams/
│   │   └── todo-tomorrow.md
│   │
│   └── experience_bank/            ← EXPERIENCES (UNDERUSED)
│       ├── EXPERIENCE_BANK.md
│       ├── experience_2026-04.json
│       ├── experience_index.json
│       └── extract_experiences.py
│
└── scripts/
    ├── memory_hybrid_search.py
    ├── memory_reranker.py
    ├── memory_cleanup.py
    ├── kg_updater.py
    ├── kg_enhancer.py
    └── kg_lifecycle_manager.py
```

---

## 📈 USAGE STATISTICS

| System | Files | Total Size | Entries |
|--------|-------|------------|---------|
| Knowledge Graph | 1 | 1.7MB | 209 entities, 4659 relations |
| Semantic Index | 1 | 460KB | 0 entries ❌ |
| Master Index | 1 | 9KB | 0 entries ❌ |
| Daily Notes | 2 | 18KB | 2 files |
| CEO Memory | 30+ | 468KB | 30+ files |
| Experience Bank | 4 | 60KB | ~50 experiences |

---

*Last Updated: 2026-04-11 21:03 UTC*
*Next Review: After consolidation*
