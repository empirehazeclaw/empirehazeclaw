# 📚 Sir HazeClaw Documentation

**Agent:** Sir HazeClaw (CEO)
**Workspace:** `/home/clawbot/.openclaw/workspace/`
**Last Updated:** 2026-04-12 19:12 UTC

---

## 🎯 Quick Navigation

### System Overview
| Doc | Purpose |
|-----|---------|
| **[SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)** | Complete system architecture (4 tiers, components) |
| **[SYSTEM_ANALYSIS.md](SYSTEM_ANALYSIS.md)** | Deep system analysis and recommendations |
| **[CONSOLIDATION_PLAN.md](CONSOLIDATION_PLAN.md)** | Active consolidation plan (Phases 1-4) |

### Memory Systems
| Doc | Purpose |
|-----|---------|
| **[MEMORY_ARCHITECTURE.md](MEMORY_ARCHITECTURE.md)** | All memory systems (KG, SQLite, Files) |
| **[MEMORY_DREAMING.md](MEMORY_DREAMING.md)** | Memory-Core plugin dreaming |
| **[MEMORY_GUIDE.md](MEMORY_GUIDE.md)** | Quick reference for memory usage |
| **[MEMORY_SYSTEMS_MAP.md](MEMORY_SYSTEMS_MAP.md)** | Visual map of memory system |

### Operations
| Doc | Purpose |
|-----|---------|
| **[CRON_INDEX.md](CRON_INDEX.md)** | All 45 cron jobs documented (20 active) |
| **[QMD.md](QMD.md)** | QMD search tool usage |
| **[SCRIPT_INDEX.md](SCRIPT_INDEX.md)** | All scripts organized (66 in SCRIPTS/) |

### Learning & Improvement
| Doc | Purpose |
|-----|---------|
| **[SELF_IMPROVEMENT_SPRINT.md](SELF_IMPROVEMENT_SPRINT.md)** | Current improvement sprint |
| **[LEARNING_LOOP.md](LEARNING_LOOP.md)** | Learning loop architecture |
| **[OPTIMIZATION_TODO.md](OPTIMIZATION_TODO.md)** | Optimization backlog |

### Analysis & Reports
| Doc | Purpose |
|-----|---------|
| **[KG_ANALYSIS.md](KG_ANALYSIS.md)** | Knowledge Graph analysis |
| **[FILE_ANALYSIS.md](FILE_ANALYSIS.md)** | Workspace file analysis |
| **[AUTONOMOUS_LEARNING_PLAN.md](AUTONOMOUS_LEARNING_PLAN.md)** | Learning plan |

---

## 📊 Current System Status

| Metric | Value |
|--------|-------|
| KG Entities | 331 |
| KG Relations | 523 |
| Sessions | 446 (39MB) |
| Scripts | 66 in SCRIPTS/ |
| Active Crons | 20/45 |
| Error Rate | ~1.4% |
| Task Issues | 0 (65 audit errors - OpenClaw limitation) |

### Active Directories
| Directory | Contents |
|-----------|----------|
| `docs/` | This documentation (47 .md files) |
| `ceo/docs/` | CEO-specific reports (23 files) |
| `skills/` | 12 skills + _library/ |
| `SCRIPTS/` | 66 scripts (4 categories) |
| `ARCHIVE/` | Archived docs (43 files) |

---

## 📁 Directory Structure

```
workspace/
├── docs/                    # Main documentation (47 files)
│   ├── README.md           # This file (central index)
│   ├── SYSTEM_*.md        # Architecture & analysis
│   ├── MEMORY_*.md        # Memory systems
│   ├── *_ANALYSIS.md      # Various analyses
│   ├── LEARNING_*.md      # Learning systems
│   └── patterns/          # ⚠️ DELETED (merged to skills/_library/)
├── ceo/
│   ├── HEARTBEAT.md       # Status tracking
│   ├── SOUL.md            # Persona definition
│   ├── PROMPT_COACH.md    # Coaching behavior
│   └── docs/              # CEO reports (23 files)
│       ├── RECAP_*.md     # Recaps
│       ├── PERIOD_*.md    # Period reviews
│       └── *_INDEX.md     # Various indexes
├── skills/
│   ├── _library/          # 27 patterns (canonical)
│   ├── prompt-coach/      # Prompt coach skill
│   ├── self-improvement/  # Self-improvement
│   └── research/          # Research skills
├── SCRIPTS/
│   ├── automation/        # 16 automation scripts
│   ├── analysis/         # 8 analysis scripts
│   ├── self_healing/     # Self-healing scripts
│   └── tools/            # Tool scripts
└── ARCHIVE/              # Archived docs (43 files)
```

---

## 🔗 External Resources

- **OpenClaw Docs:** `/home/clawbot/.npm-global/lib/node_modules/openclaw/docs/`
- **Skills:** `/workspace/skills/`
- **Scripts:** `/workspace/SCRIPTS/` (symlinked to `/workspace/scripts/`)
- **Logs:** `/workspace/logs/`

---

## 🚀 Recent Improvements (2026-04-12)

| Improvement | Status |
|-------------|--------|
| F1: @heartbeat Bug Fix | ✅ DONE |
| F2: CEO Daily Briefing Fix | ✅ DONE |
| F3: Security Token (64-char) | ✅ DONE |
| F4: Task-Backlog Maintenance | ✅ DONE |
| Session Cleanup (203MB→39MB) | ✅ DONE |
| Cron Fixes (4 crons) | ✅ DONE |
| docs/patterns/ Duplicates | ✅ DELETED (25 files) |

---

## 📝 Adding New Documentation

When adding new documentation:
1. Add entry to appropriate table above
2. Keep alphabetically sorted within table
3. Include brief purpose in description column
4. If CEO-specific, put in `ceo/docs/` instead

---

*Maintained by: Sir HazeClaw*
*Auto-updated during improvement phases*
