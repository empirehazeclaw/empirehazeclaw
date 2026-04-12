# 📋 MEMORY SYSTEM DOCUMENTATION
## Sir HazeClaw - Memory Architecture v2
**Updated:** 2026-04-12 17:30 UTC

---

## 🎯 MEMORY LAYERS (Tiered Architecture)

### Layer 1: PERSISTENT (Long-Term)
| File | Purpose | Retention |
|------|---------|-----------|
| `MEMORY.md` | Curated core context, decisions, learnings | Permanent |
| `HEARTBEAT.md` | Daily status updates | Until next day |
| `SOUL.md` | Personality definition | Permanent |
| `AGENTS.md` | Agent identity | Permanent |

### Layer 2: SEMI-PERSISTENT (Workspace Context)
| File | Purpose | Retention |
|------|---------|-----------|
| `CEO/AGENTS.md` | CEO-specific identity | Permanent |
| `CEO/HEARTBEAT.md` | CEO daily status | Until next day |
| `skills/*/` | Skill definitions | Until updated |

### Layer 3: TEMPORARY (Auto-Cleanup)
| Directory | Purpose | Retention |
|-----------|---------|-----------|
| `TEMPORARY/memory/` | Daily notes from sessions | 30 days |
| `TEMPORARY/logs/` | Session logs, error logs | 14 days |
| `TEMPORARY/audio/` | Audio transcriptions | 7 days |
| `TEMPORARY/task_reports/` | Cron job reports | 7 days |

---

## 🔄 MEMORY FLOW

```
Session Start:
    HEARTBEAT.md ← Read (daily status)
    MEMORY.md ← Read (long-term context)

During Session:
    HEARTBEAT.md ← Update (status changes)
    memory/YYYY-MM-DD.md ← New daily notes (via compaction)

Session End:
    HEARTBEAT.md ← Final status
    memory/YYYY-MM-DD.md ← Compaction (if any)

Periodic (Weekly):
    memory_consolidator.py ← Extract key info → MEMORY.md
    cleanup_temporary.py ← Auto-cleanup old temp files
```

---

## 📋 KEY SCRIPTS

| Script | Purpose | Schedule |
|--------|---------|----------|
| `memory_consolidator.py` | Extract key learnings to MEMORY.md | Weekly |
| `cleanup_temporary.py` | Auto-cleanup TEMPORARY/ | Daily |

### memory_consolidator.py Usage
```bash
# List daily notes
python3 SCRIPTS/analysis/memory_consolidator.py --list

# Show what would be consolidated (dry run)
python3 SCRIPTS/analysis/memory_consolidator.py --dry-run

# Actually consolidate
python3 SCRIPTS/analysis/memory_consolidator.py --consolidate
```

### cleanup_temporary.py Usage
```bash
# Run cleanup
python3 SCRIPTS/self_healing/cleanup_temporary.py
```

---

## 📊 CURRENT STATE (2026-04-12)

| Category | Count | Location |
|----------|-------|----------|
| Daily notes | 6 | TEMPORARY/memory/ |
| Session transcripts | ? | TEMPORARY/memory/sessions/ |
| Memory metrics | 1 | memory/session_metrics_history.json |

### Before Restructuring:
- Daily notes mixed with persistent memory files
- No clear separation
- risk of important docs being deleted

### After Restructuring:
- Clear separation PERSISTENT vs TEMPORARY
- Auto-cleanup prevents accumulation
- memory_consolidator preserves key learnings

---

## 🎯 BEST PRACTICES

1. **Daily Notes**: Write to `memory/YYYY-MM-DD.md` during session
2. **Key Learnings**: Add to MEMORY.md at session end
3. **Weekly Consolidation**: Run `memory_consolidator.py --consolidate`
4. **Never** store secrets, credentials, or sensitive data in memory files

---

## 🔗 RELATED DOCS

- `SYSTEM_ARCHITECTURE.md` - Overall system design
- `MEMORY_SYSTEMS_MAP.md` - Detailed memory systems map
- `RESTRUCTURING_PLAN.md` - Restructuring plan details

---

*Sir HazeClaw - Memory Architecture v2*
