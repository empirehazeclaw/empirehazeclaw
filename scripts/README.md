# Sir HazeClaw Scripts

**Total:** 61 scripts | **Tested:** 21 | **Coverage:** 34%

## Daily Scripts

### Morning & Evening
| Script | Purpose | Test Status |
|--------|---------|-------------|
| `morning_brief.py` | Daily 09:00 UTC briefing | ✅ |
| `morning_routine.py` | Automated morning checklist | ✅ |
| `evening_summary.py` | Evening summary generator | ✅ |
| `evening_routine.py` | Automated evening workflow | ✅ |

### Health & Monitoring
| Script | Purpose | Test Status |
|--------|---------|-------------|
| `health_monitor.py` | Full system health report | ✅ |
| `quick_check.py` | Fast 6-point check | ✅ |
| `health_alert.py` | Alert system | ✅ |
| `cron_monitor.py` | Cron job monitoring | ✅ |

### Backup & Recovery
| Script | Purpose | Test Status |
|--------|---------|-------------|
| `backup_verify.py` | Verify backup integrity | ✅ |
| `auto_backup.py` | Automated backup system | ✅ |

### Quality & Improvement
| Script | Purpose | Test Status |
|--------|---------|-------------|
| `self_eval.py` | Self-evaluation (70/100) | ✅ |
| `quality_metrics.py` | Quality tracking | ✅ |
| `test_framework.py` | Test suite (21 tests) | ✅ |
| `deep_reflection.py` | 10 deep questions | ✅ |
| `habit_tracker.py` | Habit tracking (8 habits) | ✅ |
| `kg_enhancer.py` | Knowledge graph enhancement | ✅ |

### Memory & Knowledge
| Script | Purpose | Test Status |
|--------|---------|-------------|
| `memory_cleanup.py` | Memory cleanup | ✅ |
| `memory_hybrid_search.py` | Hybrid search | ✅ |
| `kg_updater.py` | KG management | ✅ |

## Test Suite

Run all tests:
```bash
python3 scripts/test_framework.py
```

Run specific test:
```bash
python3 scripts/test_framework.py --run morning_brief
```

List all tests:
```bash
python3 scripts/test_framework.py --list
```

## Routines

### Morning Routine
```bash
python3 scripts/morning_routine.py
```
Runs: Health → Backup → Cron → Habits → Quality → Self-Eval

### Evening Routine
```bash
python3 scripts/evening_routine.py
```
Runs: Self-Eval → Quality → Habits → Reflection (Sundays)

## Skill Directory

Skills are in `/skills/`:
- `self-improvement/` — Self-improvement tools
- `system-manager/` — System health & management
- `capability-evolver/` — Evolution engine

## Notes

- All scripts are in `/home/clawbot/.openclaw/workspace/scripts/`
- Scripts return structured data for programmatic use
- CLI-only scripts print to stdout
- Test coverage goal: >80%
