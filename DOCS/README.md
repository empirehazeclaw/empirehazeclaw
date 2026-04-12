# 📚 WORKSPACE DOCUMENTATION INDEX
**Sir HazeClaw - 2026-04-12**

---

## 🎯 QUICK NAVIGATION

| Looking for... | Go to... |
|----------------|---------|
| System overview | `SYSTEM_ARCHITECTURE.md` |
| Current status | `HEARTBEAT.md` |
| Todo list | `TODO.md` |
| Script inventory | `scripts/` |
| Cron jobs | `CRON_INDEX.md` |
| Knowledge Graph | `KG_INDEX.md` |
| Self-healing | `SCRIPTS/self_healing/` |
| Restructuring plan | `RESTRUCTURING_PLAN.md` |

---

## 📁 DIRECTORY STRUCTURE

```
workspace/
├── CONFIG/                  ← AGENTS.md, USER.md, TOOLS.md (identity & config)
├── CORE/                    ← MEMORY.md, HEARTBEAT.md (persistent state)
├── SCRIPTS/
│   ├── automation/          ← Cron-triggered scripts
│   ├── analysis/            ← Auditing & improvement scripts
│   ├── self_healing/        ← Error recovery scripts
│   └── tools/               ← Utility scripts
├── DOCS/                    ← All documentation
│   ├── ARCHITECTURE.md      ← System design
│   ├── SCRIPTS.md           ← Script inventory
│   ├── CRONS.md             ← Cron job inventory  
│   ├── PATTERNS.md          ← Best practices
│   └── KNOWLEDGE/           ← KG documentation
├── TEMPORARY/               ← Auto-cleanup directory
│   ├── logs/                ← Session logs (14d retention)
│   ├── memory/              ← Daily notes (30d retention)
│   ├── task_reports/        ← Cron reports (7d retention)
│   └── audio/               ← Audio files (7d retention)
├── ARCHIVE/                 ← Inactive projects
├── CEO/                     ← Personal workspace for Nico
├── skills/                  ← OpenClaw skills
└── README.md                ← This file
```

---

## 📊 KEY METRICS (2026-04-12)

| Metric | Value |
|--------|-------|
| Error Rate | ~1.4% |
| KG Entities | 316 |
| Active Crons | 20/45 |
| Scripts | ~50 in SCRIPTS/ |
| System Score | 91/100 |

---

## 🔧 ACTIVE SCRIPTS

### Self-Healing (SCRIPTS/self_healing/)
| Script | Purpose |
|--------|---------|
| `cron_error_healer.py` | Auto-heals failed crons (4-stage loop) |
| `model_health_checker.py` | Health probe for all models |
| `model_cooldown_manager.py` | Cooldown after rate limits |
| `session_pin_manager.py` | Session failover management |
| `config_backup_manager.py` | Auto-backup before changes |
| `github_issue_creator.py` | GitHub issues for failures |
| `cleanup_temporary.py` | Auto-cleanup old temp files |

### Automation (SCRIPTS/automation/)
| Script | Purpose |
|--------|---------|
| `cron_watchdog.py` | Watchdog for cron health |
| `health_monitor.py` | System health monitoring |
| `kg_updater.py` | Knowledge graph updates |
| `gateway_recovery.py` | Gateway restart recovery |

### Analysis (SCRIPTS/analysis/)
| Script | Purpose |
|--------|---------|
| `autonomous_improvement.py` | Self-improvement loop |
| `continuous_improver.py` | Continuous improvement |
| `gene_diversity_tracker.py` | Track genetic diversity |

---

## 📖 DOCUMENTATION

### Architecture
- `SYSTEM_ARCHITECTURE.md` - Complete system design
- `SYSTEM_INVENTORY.md` - Component inventory
- `MEMORY_SYSTEMS_MAP.md` - Memory architecture

### Planning
- `TODO.md` - Master todo list (Week 1-4)
- `EXECUTION_PLAN.md` - Monthly execution plan
- `RESTRUCTURING_PLAN.md` - Workspace reorganization

### Research
- `OPTIMIZATION_RESEARCH.md` - Research findings
- `LEARNING_LOOP.md` - Learning methodology

---

## 🧪 TESTING

Run test suite:
```bash
cd /home/clawbot/.openclaw/workspace
python3 scripts/fast_test.py
```

---

## 📝 NOTES

- **TEMPORARY/** files are auto-deleted per retention policy
- **CEO/** is personal workspace (audio, memory, task_reports moved to TEMPORARY/)
- All scripts committed to GitHub: `empirehazeclaw/empirehazeclaw`

---

*Last updated: 2026-04-12 17:20 UTC*
*Sir HazeClaw 🚀*
