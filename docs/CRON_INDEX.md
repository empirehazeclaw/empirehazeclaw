# Active Crons Index — 2026-04-11 11:14 UTC

**Purpose:** Klare Übersicht über alle aktiven Crons

---

## 📊 OVERVIEW

| Total Crons | Active | Errors |
|-------------|--------|--------|
| 15 | 15 | 4 (teilweise) |

---

## 🚨 CRITICAL CRONS

### 1. Gateway Auto-Recovery
```
ID: c0060c0e-f315-4b07-8b4c-09ee2d571a9b
Interval: Every 5 min
Status: ✅ OK
Last Run: 11:11 UTC
Script: gateway_recovery.py
Action: Check health → Restart if down → Alert if 3 failures
```

### 2. Learning Coordinator Hourly
```
ID: 21b1dcba-b0ce-489e-9a04-f11636ace430
Interval: Every hour (0 * * * *)
Status: ✅ OK
Last Run: 11:07 UTC (Duration: 38s)
Script: learning_coordinator.py --full
Action: System Check → Research → Quality Gates → Learning Track
```

---

## ⚠️ CRONS MIT ISSUES

### 3. CEO Daily Briefing
```
ID: a1456495-f03c-4cd0-90fc-baa728365a25
Interval: 11:00 Berlin (0 11 * * *)
Status: ⚠️ 2 consecutive errors
Last Run: 11:00 UTC (Duration: 75s)
Script: morning_brief.py
Error: "⚠️ ✉️ Message failed"
Issue: Delivery problem
```

### 4. Memory-Core Dreaming
```
Type: OpenClaw memory-core plugin (built-in)
Interval: 04:40 UTC (40 4 * * *)
Status: ✅ ACTIVE
Script: memory-core plugin internal
Features: Light → REM → Deep Phase
Output: MEMORY.md, DREAMS.md, memory/dreaming/
```

**Hinweis:** Custom nightly_dreaming.py wurde durch memory-core dreaming ersetzt (2026-04-12)

### 5. Security Audit
```
ID: 235439f7-67b0-4ffe-a15d-6306afca36aa
Interval: 08:00 UTC (0 8 * * *)
Status: ⚠️ 1 error
Last Run: 08:00 UTC (Duration: 129s)
Script: security-audit.sh
Error: "⚠️ ✉️ Message failed"
Issue: Delivery problem
```

---

## 📋 HEALTH + MONITORING

### 6. Health Check Hourly
```
ID: 6b09e638-52ef-4705-b310-1bb4ad9bba39
Interval: Every 3 hours (0 */3 * * *)
Status: ✅ OK
Last Run: 10:30 UTC
Script: quick_check.py
Delivery: None (silent)
```

### 7. Cron Watchdog
```
ID: 8e36de41-6a20-46dc-97aa-8ddad038ec12
Interval: Every 6 hours (0 */6 * * *)
Status: ✅ OK
Last Run: 06:00 UTC
Script: cron_watchdog.py
Delivery: None (silent)
```

### 8. Proactive Loop Check
```
ID: 06110d1f-fb1b-4076-93c5-046bb23be64c
Interval: Every 15 min
Status: ✅ OK
Last Run: 11:09 UTC
Script: loop_check.py
Action: Check loops → Alert if issues
Delivery: Telegram (bei Issues nur)
```

---

## 📚 RESEARCH + LEARNING

### 9. Innovation Research Daily
```
ID: 15690b13-3f3f-443f-affe-98b1abeb8593
Interval: 14:00 UTC (0 14 * * *)
Status: ✅ Scheduled
Next Run: 14:00 UTC
Script: innovation_research.py --daily
Action: Web search → KG Update
```

### 10. Learning Loop Status in 5min
```
ID: b25f72c4-a0d2-4682-8099-c96182b7c77d
Interval: Every 5 min
Status: ✅ OK
Last Run: 11:09 UTC
Action: Check subagent status
Delivery: Telegram
```

---

## 🧹 MAINTENANCE

### 11. Daily Auto Backup
```
ID: b8698d8d-4d1e-4970-ab59-8242c65c6fa0
Interval: 03:00 UTC (0 3 * * *)
Status: ✅ OK
Last Run: 09:00 UTC (Duration: 31s)
Script: auto_backup.py
Delivery: None (silent)
```

### 12. Auto Documentation Update
```
ID: bcdfba01-1a74-4b09-bb53-bd4cdbfe7d6f
Interval: Monday 09:00 UTC (0 9 * * 1)
Status: ✅ Scheduled
Next Run: Monday 09:00 UTC
Script: auto_doc.py --update
Action: Update docs/scripts_index.md
```

---

## 📅 WEEKLY

### 13. CEO Weekly Review
```
ID: a31329c1-8e92-4bb0-973e-456823fd54e4
Interval: Monday 10:00 UTC (0 10 * * 1)
Status: ✅ Scheduled
Next Run: Monday 10:00 UTC
Script: weekly_review.py
Delivery: Telegram
```

---

## 🔧 SYSTEM CRONS

### 14. Evening Capture
```
ID: cb2ae8d6-7439-459d-a9c7-4f6042408bc4
Interval: 21:00 UTC (0 21 * * *)
Status: ✅ OK
Last Run: Yesterday 21:00 UTC
Script: evening_capture.py
Action: Fleeting notes + Wiki sync queue
Delivery: Telegram
```

### 15. Memory Dreaming Promotion
```
ID: d1fa7ce7-1902-4e7e-8830-b8d74f313c38
Interval: 04:40 UTC (40 4 * * *)
Status: ✅ Scheduled (SYSTEM)
Next Run: 04:40 UTC tomorrow
Type: systemEvent (not agentTurn)
Action: Short-term → Long-term memory promotion
```

---

## 📊 CRON SUMMARY BY INTERVAL

| Interval | Crons |
|----------|-------|
| Every 5 min | 2 (Gateway, Loop Status) |
| Every 15 min | 1 (Loop Check) |
| Hourly | 1 (Learning Coordinator) |
| Every 3 hours | 1 (Health Check) |
| Every 6 hours | 1 (Cron Watchdog) |
| Daily 03:00 | 1 (Auto Backup) |
| Daily 08:00 | 1 (Security Audit) |
| Daily 11:00 | 1 (CEO Briefing) ⚠️ |
| Daily 14:00 | 1 (Innovation Research) |
| Daily 21:00 | 1 (Evening Capture) |
| Weekly Mon 09:00 | 1 (Auto Doc) |
| Weekly Mon 10:00 | 1 (Weekly Review) |
| 02:00 UTC | 1 (Nightly Dreaming) ⚠️ |
| 04:40 UTC | 1 (Memory Promotion) |

---

## 🚨 ISSUES TO FIX

| Cron | Issue | Priority |
|------|-------|----------|
| CEO Daily Briefing | Message failed (2x) | 🔴 HIGH |
| Security Audit | Message failed (1x) | 🟡 MED |
| ~~Nightly Dreaming~~ | ✅ **DISABLED** - Replaced by memory-core dreaming | — |

**Update 2026-04-12:** Custom nightly_dreaming.py deleted. Using memory-core plugin dreaming instead.---

*Erstellt: 2026-04-11 11:14 UTC*
*Quelle: cron list*
*Status: COMPLETE*
---

## 📋 ADDITIONAL SYSTEMS

### QMD (Query Markdown)
```
Status: ✅ READY (On-Demand CLI, not a daemon)
Usage: qmd query "search term" -c memory
Index: 58 files, 1692 vectors
Location: ~/.cache/qmd/
Note: No process needed - runs on-demand
```

### Memory Sessions Directory
```
Path: memory/sessions/
Status: ✅ Created 2026-04-12
Purpose: OpenClaw session memory persistence (via session-memory hook)
Hook: session-memory (enabled)
```


---

## 🆕 NEW SHELL TOOL CRONS (2026-04-13)

### 16. SQLite Vacuum Weekly
```
ID: 4d51210d-9f08-42dc-9032-5a424b99c4b9
Interval: Sunday 04:00 UTC (0 4 * * 0)
Status: ✅ Active
Script: sqlite_vacuum.sh
Action: VACUUM + ANALYZE all *.sqlite in memory/
Delivery: Telegram (announce)
Log: logs/sqlite_vacuum.log
```

### 17. GitHub Backup Daily
```
ID: 55208aae-9e3a-41ec-93da-951a2e0b69a1
Interval: 23:00 UTC (0 23 * * *)
Status: ✅ Active
Script: github_backup.sh
Action: git add → commit → push workspace changes
Delivery: Telegram (announce)
Log: logs/github_backup.log
```

### 18. Kill Day Agent Cleanup
```
ID: 822d0b84-ddd4-4531-87a1-e7eac5bfcbc8
Interval: First Sunday of month 03:00 UTC (0 3 1-7 * 0)
Status: ❌ DISABLED (manual trigger)
Script: kill_day.sh
Action: --dry-run only via cron; manual --execute required
Delivery: Telegram (announce)
Log: logs/kill_day.log
Safety: Requires YES-DELETE confirmation to execute
```

---

*Updated: 2026-04-13 07:27 UTC*
