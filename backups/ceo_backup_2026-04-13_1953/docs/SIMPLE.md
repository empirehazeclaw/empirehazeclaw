# 🦞 SIR HAZECLAW — OPERATOR GUIDE

**Version:** Phase 3 (Simplified Docs)
**Last Updated:** 2026-04-12 08:12 UTC
**For:** Nico + future operators

---

## WHAT IS THIS?

Sir HazeClaw is an autonomous AI agent that:
- ✅ Manages its own infrastructure (gateway, crons, memory)
- ✅ Continuously improves itself (learns from errors, updates strategies)
- ✅ Handles operational tasks for Nico (reports, research, backups)
- ✅ Self-heals when things break (cron healer, gateway recovery)

**You don't need to tell it what to do.** It runs 24/7 and handles things autonomously.

---

## QUICK START

### Talk to Me
- **Telegram:** Message me directly (ID: 5392634979)
- **Commands:** Just tell me what you need in natural language

### Check Status
```bash
openclaw status                    # Gateway + sessions
openclaw tasks                     # Active background tasks
python3 scripts/health_check.py    # Full health check
```

### Common Tasks
| What | How |
|------|-----|
| System health | `python3 scripts/health_check.py --full` |
| Cron status | `python3 scripts/cron_watchdog.py --report` |
| KG stats | `python3 scripts/kg_updater.py stats` |
| Error analysis | `python3 scripts/error_rate_monitor.py` |
| Learning loop | `python3 scripts/learning_coordinator.py --full` |

---

## HOW IT WORKS

### Core Loop (Every Hour)
```
1. HEARTBEAT → Check system status
2. LEARN → Analyze recent errors + successes
3. IMPROVE → Update strategies, KG, scripts
4. HEAL → Fix broken crons, restart gateway if needed
5. REPORT → Log learnings, update memory
```

### Daily Rhythm
| Time (UTC) | What Runs |
|------------|-----------|
| 03:00 | Auto Backup (commits to Git) |
| 08:00 | Security Scan |
| 11:00 | Morning Brief → Telegram |
| 14:00 | Innovation Research |
| 21:00 | Evening Capture + Review |

### Every Hour
- Learning Coordinator (analyze errors)
- Continuous Improver (autonomous experiments)
- Gateway Recovery Check
- Health Check (every 3h)

---

## KEY SCRIPTS

### System Health
```bash
python3 scripts/health_check.py --full    # Full diagnostic
python3 scripts/quick_check.py           # Quick status
python3 scripts/health_monitor.py        # Continuous monitoring
```

### Cron Management
```bash
python3 scripts/cron_watchdog.py --report       # Status report
python3 scripts/cron_watchdog.py watchdog       # Watch mode
python3 scripts/cron_watchdog.py --format json  # JSON output
python3 scripts/cron_error_healer.py           # Auto-fix failures
```

### Knowledge Graph
```bash
python3 scripts/kg_updater.py stats            # Entity stats
python3 scripts/kg_updater.py enhance         # Bulk add
python3 scripts/kg_updater.py lifecycle        # Lifecycle management
python3 scripts/kg_updater.py clean-relations  # Clean relations
```

### Memory
```bash
python3 scripts/memory_cleanup.py show        # Show cleanup info
python3 scripts/memory_freshness.py           # Freshness check
python3 scripts/stale_memory_cleanup.py        # Remove stale entries
python3 scripts/MEMORY_API.py                 # Unified memory interface
```

### Learning & Improvement
```bash
python3 scripts/learning_coordinator.py --full  # Full learning cycle
python3 scripts/error_rate_monitor.py            # Error analysis
python3 scripts/error_reducer.py                  # Reduce errors
python3 scripts/continuous_improver.py            # Autonomous improvements
```

### Backups
```bash
python3 scripts/auto_backup.py              # Run backup
python3 scripts/backup_verify.py             # Verify backup
```

---

## IMPORTANT FILES

| File | Purpose |
|------|---------|
| `ceo/HEARTBEAT.md` | **START HERE** — current system status |
| `ceo/SOUL.md` | Who I am, my personality |
| `ceo/USER.md` | About Nico (you) |
| `scripts/MEMORY_API.py` | Unified interface to all memory systems |
| `scripts/cron_error_healer.py` | Self-healing for broken crons |
| `data/gateway_recovery_state.json` | Gateway health state |
| `memory/session_metrics_history.json` | Historical metrics |

---

## IF SOMETHING BREAKS

### Cron Failing?
→ `cron_error_healer.py` auto-fixes most issues
→ Check: `python3 scripts/cron_watchdog.py --report`

### Gateway Down?
→ Auto-restart within 5 minutes
→ Check: `openclaw status`

### Wrong Delivery (message not going through)?
→ Check cron config: `delivery: {mode: "announce", channel: "telegram", to: "5392634979"}`

### Memory Issues?
→ Check: `memory/session_metrics_history.json`
→ Run: `python3 scripts/memory_cleanup.py show`

### Script won't run (exec preflight)?
→ This happens when command is complex. Use direct python:
  `python3 scripts/<script>.py` instead of shell复杂 commands

---

## ARCHIVED SCRIPTS

If you need a script that was archived (Phase 2 consolidation):
```bash
# Find it
ls scripts/_archive/phase2/
ls scripts/_archive/phase2b/

# Restore
mv scripts/_archive/phase2/<script>.py scripts/
```

**Phase 2 archived 37 scripts** — all safely stored if needed.

---

## SKILLS (14 Active)

| Skill | What it does |
|-------|--------------|
| `self-improvement` | Learns from errors, improves continuously |
| `system-manager` | Health, backup, security |
| `research` | Web search + knowledge acquisition |
| `capability-evolver` | Self-testing + validation |
| `loop-prevention` | Detects infinite loops |
| `semantic-search` | Memory search |
| `voice-agent` | German TTS |
| `coding` | Code generation |
| `content-creator` | Content pipeline |
| `qa-enforcer` | Quality enforcement |
| `backup-advisor` | Backup recommendations |
| `backend-api` | API development |
| `frontend` | UI development |

---

## CURRENT STATUS

```
Gateway:     ✅ Healthy
Error Rate:  ✅ ~1.4% (target: <1%)
KG:          ✅ 209 entities, 816 relations
Memory:      ✅ Clean structure
Crons:       ✅ 20/45 active
Scripts:     ✅ 62 (consolidated from 99)
Test Suite:  ✅ 369/369 passing
```

---

## PHASE HISTORY

| Phase | What | Status |
|-------|------|--------|
| 1 | Critical fixes (CEO briefing, crons) | ✅ Done |
| 2 | Script consolidation (99→62) | ✅ Done |
| 3 | Docs simplification | 🔄 In Progress |
| 4 | KG integration fix | 📋 Planned |
| 5 | Self-improvement loops | 📋 Planned |
| 6 | Full validation | 📋 Planned |

---

## NOTES FOR OPERATORS

1. **I wake up fresh each session** — I read SOUL.md, USER.md, HEARTBEAT.md, and today's memory
2. **I handle things autonomously** — You don't need to micromanage
3. **I self-heal most issues** — Let the healer try first before manual intervention
4. **Your privacy matters** — I don't share your data in group chats
5. **Backup runs at 03:00 UTC** — Everything commits to Git automatically

---

*🦞 Sir HazeClaw — Running since 2026-04-08*
*Version: Phase 3 — Simplified for operators*
*For questions: Check HEARTBEAT.md first*