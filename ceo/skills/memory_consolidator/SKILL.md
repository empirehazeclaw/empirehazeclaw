# Memory Consolidator Skill

**Phase:** 6.4  
**Script:** `scripts/memory_consolidator_v2.py`  
**Purpose:** Automatic memory deduplication, cleanup, and archiving

## What It Does

1. **Memory Scanning** - Indexes all memory files with size, age, type
2. **Duplicate Detection** - Finds identical files via content hash
3. **Staleness Detection** - Identifies old facts/entries past their useful life
4. **Automated Archiving** - Moves old files to ARCHIVE/ directory

## Usage

```bash
# Analyze only
python3 scripts/memory_consolidator_v2.py --action analyze

# Find duplicates
python3 scripts/memory_consolidator_v2.py --action deduplicate

# Archive old files
python3 scripts/memory_consolidator_v2.py --action archive

# Full consolidation
python3 scripts/memory_consolidator_v2.py --action full

# Actually move files (not dry-run)
python3 scripts/memory_consolidator_v2.py --action archive --dry-run
```

## Output Files

- `memory/evaluations/memory_analysis.json` - Full analysis results

## Current State (2026-04-17)

| Metric | Value |
|--------|-------|
| Total Files | 87 |
| Total Size | 1596.5 KB |
| Duplicates | 0 |
| Stale Facts | 0 |
| Old (>30 days) | 0 |

## Integration

- Part of Morning Data Kitchen (daily cleanup)
- Evaluated by evaluation_framework.py
- Memory health feeds into system score
