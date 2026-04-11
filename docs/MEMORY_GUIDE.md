# 📋 MEMORY QUICK REFERENCE
## Sir HazeClaw — Fast Access Guide

**Quick access to all memory operations**

---

## 🔍 SEARCH

```bash
# Global search (all systems)
python3 scripts/MEMORY_API.py search "query"

# Hybrid search (semantic + keyword)
python3 scripts/memory_hybrid_search.py "query"

# Knowledge Graph entities only
python3 scripts/MEMORY_API.py entities

# Filtered entities
python3 scripts/MEMORY_API.py entities error
```

---

## 📊 STATUS

```bash
# All systems status
python3 scripts/MEMORY_API.py status

# KG details
python3 scripts/MEMORY_API.py entities | wc -l

# Check cleanup status
python3 scripts/memory_cleanup.py --report
```

---

## 📝 DAILY NOTES

```bash
# Read today's daily
cat memory/YYYY-MM-DD.md

# CEO daily notes
ls ceo/memory/daily/

# Append to today's notes (via API)
python3 -c "
from scripts.MEMORY_API import MemoryAPI
api = MemoryAPI()
api.append_daily_note('New entry here')
"
```

---

## 🧠 KNOWLEDGE GRAPH

```bash
# Add entity
python3 -c "
from scripts.MEMORY_API import MemoryAPI
api = MemoryAPI()
api.add_knowledge('New Pattern', {'type': 'pattern', 'data': {...}})
"

# Get KG stats
python3 scripts/MEMORY_API.py status | grep -A5 knowledge_graph
```

---

## 🎓 EXPERIENCES

```bash
# List experiences
python3 scripts/MEMORY_API.py experiences

# View experience bank
cat ceo/experience_bank/experience_2026-04.json | head -50
```

---

## 🧹 CLEANUP

```bash
# Run cleanup (dry-run first!)
python3 scripts/memory_cleanup.py --dry-run

# Full cleanup (live)
python3 scripts/memory_cleanup.py

# Extract experiences only
python3 scripts/memory_cleanup.py --extract-experiences
```

---

## 📁 FILE LOCATIONS

| System | Path |
|--------|------|
| Daily Notes | `/workspace/memory/YYYY-MM-DD.md` |
| CEO Memory | `/workspace/ceo/memory/daily/` |
| Knowledge Graph | `/workspace/core_ultralight/memory/knowledge_graph.json` |
| Semantic Index | `/workspace/core_ultralight/memory/semantic_index.json` |
| Experience Bank | `/workspace/ceo/experience_bank/` |
| Scripts | `/workspace/scripts/` |

---

## ⚡ COMMON TASKS

### Add to Knowledge Graph
```python
from scripts.MEMORY_API import MemoryAPI
api = MemoryAPI()
api.add_knowledge("My Pattern", {"type": "pattern", "data": {...}})
```

### Search and Get Full Content
```python
from scripts.MEMORY_API import MemoryAPI
api = MemoryAPI()
results = api.search("error rate")
for r in results:
    print(r['title'], r['type'])
```

### Get Specific Entity
```python
from scripts.MEMORY_API import MemoryAPI
api = MemoryAPI()
kg = api.get_kg()
entity = [e for e in kg['entities'] if e.get('title') == 'Error Rate'][0]
```

### Read CEO Daily Notes
```python
from scripts.MEMORY_API import MemoryAPI
api = MemoryAPI()
notes = api.get_ceo_daily_notes("2026-04-11")
```

---

## 🚨 ALERTS

| Alert | Meaning | Action |
|-------|---------|--------|
| "DUAL DAILY NOTES" | Duplicate log files | Run cleanup |
| "Semantic Index EMPTY" | No search index | Rebuild index |
| "KG > 5MB" | Too large | Run lifecycle manager |
| "Orphaned CEO files" | Files outside structure | Run cleanup |

---

## 📅 AUTOMATED CRONS

| Cron | When | What |
|------|------|------|
| Weekly Memory Cleanup | Sun 04:00 UTC | Full cleanup + experiences |
| KG Lifecycle Manager | Sun 02:00 UTC | KG maintenance |
| Daily Auto Backup | Daily 03:00 UTC | Backup memory systems |

---

## 📚 DOCUMENTATION

| Doc | Location | Purpose |
|-----|----------|---------|
| ARCHITECTURE | `docs/MEMORY_ARCHITECTURE.md` | Full system docs |
| SYSTEMS MAP | `MEMORY_SYSTEMS_MAP.md` | Inventory + issues |
| CONSOLIDATION PLAN | `MEMORY_CONSOLIDATION_PLAN.md` | 4-phase roadmap |

---

*Last Updated: 2026-04-11*
