# 🚀 SIR HAZECLAW — QUICK REFERENCE

**Last Updated:** 2026-04-12 08:10 UTC
**Version:** Phase 2 Complete (Simplified System)

---

## 🏠 WHAT IS THIS?

Sir HazeClaw is an autonomous AI agent that continuously improves itself, manages its own infrastructure, and handles operational tasks for Nico — without needing to be told what to do.

**Core Loop:** Learn → Improve → Heal → Repeat (every hour)

---

## 📡 HOW TO TALK TO ME

| Channel | Address | Notes |
|---------|---------|-------|
| **Telegram** | @Nico (ID: 5392634979) | Primary — use this |
| **Session** | `agent:ceo:telegram:direct:5392634979` | For internal use |

---

## ⏰ WHAT RUNS AUTOMATICALLY

### Daily Rhythm
| Time (UTC) | What | Description |
|------------|------|-------------|
| 03:00 | Auto Backup | Backs up workspace to Git |
| 08:00 | Security Scan | Scans for issues, logs only |
| 10:00 | CEO Weekly Review | Monday only |
| 11:00 | **Morning Brief** 🌅 | Summary to Telegram |
| 14:00 | Innovation Research | Web research, logs insights |
| 21:00 | Evening Capture + Review | Fleeting notes + summary |

### Every Hour
| What | Purpose |
|------|---------|
| Learning Coordinator | Analyze errors, improve strategies |
| Continuous Improver | Autonomous experiments |
| Gateway Recovery Check | Auto-restart if down |
| Health Check (every 3h) | System health |

### Every 6 Hours
| What | Purpose |
|------|---------|
| Cron Error Healer | Auto-fix failed cron jobs |
| Cron Watchdog | Monitor cron health |

---

## 🎮 COMMON COMMANDS

```bash
# Check system status
openclaw status

# View active tasks
openclaw tasks

# Run health check manually
python3 scripts/health_check.py --full

# Run learning coordinator
python3 scripts/learning_coordinator.py --full

# Run cron watchdog
python3 scripts/cron_watchdog.py --report

# View recent logs
tail -20 logs/gateway_recovery.log
tail -20 logs/cron_healer.log
```

---

## 📁 KEY FILES

| File | Purpose |
|------|---------|
| `ceo/HEARTBEAT.md` | Current system status at a glance |
| `ceo/docs/DEEP_AUDIT.md` | Full system audit + issues |
| `ceo/docs/CONSOLIDATION_REPORT.md` | Phase 2 documentation |
| `ceo/docs/EXECUTION_PLAN.md` | 6-phase improvement plan |
| `scripts/MEMORY_API.py` | Unified memory interface |
| `scripts/cron_error_healer.py` | Self-healing for crons |
| `scripts/cron_watchdog.py` | Cron monitoring (consolidated) |
| `scripts/kg_updater.py` | KG management (consolidated) |

---

## 🔧 SKILLS (14 Active)

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

## 📊 CURRENT STATUS

```
Gateway:     ✅ Healthy
Error Rate:  ✅ ~1.4% (target: <1%)
KG:          ✅ 209 entities, 816 relations
Memory:      ✅ Clean structure
Crons:       ✅ 20/45 active (rest are old fleet/discord)
Scripts:     ✅ 62 (consolidated from 99 in Phase 2)
```

---

## 🔄 PHASE 2 CONSOLIDATION SUMMARY

### Scripts: 99 → 62 ✅

**KG Scripts (4 → 1):**
```bash
python3 scripts/kg_updater.py stats        # Entity stats
python3 scripts/kg_updater.py enhance     # Bulk add
python3 scripts/kg_updater.py lifecycle   # Lifecycle
python3 scripts/kg_updater.py clean-relations  # Relations
```

**Cron Scripts (2 → 1):**
```bash
python3 scripts/cron_watchdog.py --report       # Status report
python3 scripts/cron_watchdog.py watchdog      # Continuous watch
python3 scripts/cron_watchdog.py --format json  # JSON output
```

**Archived:** 37 scripts in `scripts/_archive/phase2/` and `scripts/_archive/phase2b/`

---

## 🆘 IF SOMETHING BREAKS

1. **Cron failing?** → `cron_error_healer.py` auto-fixes most issues
2. **Gateway down?** → Auto-restart kicks in within 5 minutes
3. **Wrong delivery config?** → Check cron `delivery: {mode, channel, to}`
4. **Memory issues?** → Check `memory/session_metrics_history.json`
5. **Need to restore archived script?** → `mv scripts/_archive/phase2/<script>.py scripts/`

---

## 📝 NOTES FOR NICO

- **Session Start:** I read SOUL.md, USER.md, HEARTBEAT.md, and today's memory
- **Learning:** I extract learnings hourly and log to KG + daily memory
- **Errors:** I self-heal most issues automatically
- **Privacy:** Your private data stays private — I'm careful in group chats
- **Backup:** Everything commits to Git automatically at 03:00 UTC

---

*🦞 Sir HazeClaw — Running since 2026-04-08*
*Phase 2 Complete: System simplified, documented, tested*