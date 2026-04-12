# 🚀 SIR HAZECLAW — QUICK REFERENCE

**Last Updated:** 2026-04-12 07:45 UTC

---

## 🏠 WHAT IS THIS?

Sir HazeClaw is an autonomous AI agent that continuously improves itself, manages its own infrastructure, and handles operational tasks for Nico — without needing to be told what to do.

**Core Loop:** Learn → Improve → Heal → Repeat (every hour)

---

## 📡 HOW TO TALK TO ME

| Channel | Address | Notes |
|---------|---------|-------|
| **Telegram** | @Nico (5392634979) | Primary — use this |
| **Session** | `agent:ceo:telegram:direct:5392634979` | For internal use |

---

## ⏰ WHAT RUNS AUTOMATICALLY

### Daily Rhythm
| Time (UTC) | What | Description |
|------------|------|-------------|
| 03:00 | Auto Backup | Backs up workspace to Git |
| 08:00 | Security Audit | Scans for issues, logs only |
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

```
# Check system status
openclaw status

# View active tasks
openclaw tasks

# Run health check manually
python3 scripts/health_check.py --full

# Run learning coordinator
python3 scripts/learning_coordinator.py --full

# View recent logs
tail -20 logs/gateway_recovery.log
tail -20 logs/cron_healer.log
```

---

## 📁 KEY FILES

| File | Purpose |
|------|---------|
| `HEARTBEAT.md` | Current system status at a glance |
| `docs/DEEP_AUDIT.md` | Full system audit + issues |
| `docs/SYSTEM_ARCHITECTURE.md` | How everything fits together |
| `scripts/MEMORY_API.py` | Unified memory interface |
| `scripts/cron_error_healer.py` | Self-healing for crons |

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
Gateway:     ✅ Healthy (71ms response)
Error Rate:  ✅ 1.48% (target: <1%)
KG:          ✅ 209 entities, 816 relations
Memory:      ✅ 33 files, 191 vector chunks
Crons:       ✅ 17 active, 3 re-enabled today
Scripts:     ⚠️  99 (consolidation in progress → target: ~40)
```

---

## 🆘 IF SOMETHING BREAKS

1. **Cron failing?** → `cron_error_healer.py` auto-fixes most issues
2. **Gateway down?** → Auto-restart kicks in within 5 minutes
3. **Wrong delivery config?** → Check cron `delivery: {mode, channel, to}`
4. **Memory issues?** → Check `memory/session_metrics_history.json`

---

## 📝 NOTES FOR NICO

- **Session Start:** I read SOUL.md, USER.md, HEARTBEAT.md, and today's memory
- **Learning:** I extract learnings hourly and log to KG + daily memory
- **Errors:** I self-heal most issues automatically
- **Privacy:** Your private data stays private — I'm careful in group chats
- **Backup:** Everything commits to Git automatically at 03:00 UTC

---

*🦞 Sir HazeClaw — Running since 2026-04-08*
