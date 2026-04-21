# MODUL 07: Cron System

**Modul:** Cron System — Task Scheduling & Monitoring
**Status:** ✅ Dokumentiert
**Letztes Update:** 2026-04-17

---

## 7.1 OVERVIEW

Das Cron System ist das **Scheduling-System** von Sir HazeClaw. Es verwaltet 40+ Jobs.

### Stats

| Metric | Count |
|--------|-------|
| Total Crons | 65 |
| Enabled | 40 |
| Disabled | 17 |
| Unknown | ~3 |

---

## 7.2 ACTIVE CRONS (40)

### 🟢 Health & Monitoring

| Cron | Schedule | Script | Status |
|------|----------|--------|--------|
| Autonomy Supervisor | 5min | `autonomy_supervisor.py` | ✅ OK |
| Gateway Recovery | 15min | `gateway_recovery.py` | ✅ OK |
| Health Check Hourly | 3h | `health_check.py` | ✅ OK |
| Integration Health Check | 8,20h | `integration_dashboard.py` | ✅ OK |
| Cron Watchdog | 6h | `cron_watchdog.py` | ✅ OK |
| Bug Hunter | 30min | `bug_scanner.py` | ✅ OK |
| Bug Fix Pipeline | 35min | `bug_fix_pipeline.py` | ✅ OK |

### 🟢 Learning & Memory

| Cron | Schedule | Script | Status |
|------|----------|--------|--------|
| Learning Loop Hourly | hourly | `learning_loop_v3.py` | ✅ OK |
| Learning Loop → KG | 10min | `learning_to_kg_sync.py` | ✅ OK |
| Learning Coordinator | 9,18h | `learning_coordinator.py` | ✅ OK |
| Memory Sync | 5min | `memory_sync.py` | ✅ OK |
| HEARTBEAT Auto-Update | 3h | `heartbeat_updater.py` | ✅ OK |
| Context Compressor | 6h | `context_compressor.py` | ✅ OK |
| Session Context Manager | 3h | `session_context_manager.py` | ✅ OK |
| Memory Dreaming | 4:40h | promotion cron | ✅ OK |

### 🟢 Self-Improvement

| Cron | Schedule | Script | Status |
|------|----------|--------|--------|
| Agent Self-Improver | 18h | `agent_self_improver.py` | ✅ OK |
| Smart Evolver Run | 3h | `run_smart_evolver.sh` | ✅ OK |
| Stagnation Detector | 6h | `stagnation_detector.py` | ✅ OK |

### 🟢 Operations

| Cron | Schedule | Script | Status |
|------|----------|--------|--------|
| CEO Daily Briefing | 11h (Berlin) | `morning_brief.py` | ✅ OK |
| Evening Capture | 21h | `evening_capture.py` | ✅ OK |
| Evening Review | 20h | `evening_review.py` | ✅ OK |
| Token Budget Tracker | 0h | `token_budget_tracker.py` | ✅ OK |
| Session Cleanup Daily | 3h | `session_cleanup.py` | ✅ OK |
| Daily Auto Backup | 4h | `auto_backup.py` | ✅ OK |
| GitHub Backup Daily | 23h | `github_backup.sh` | ✅ OK |

### 🟢 Analysis & Research

| Cron | Schedule | Script | Status |
|------|----------|--------|--------|
| Innovation Research Daily | 14h | `innovation_research.py` | ✅ OK |
| Opportunity Scanner Daily | 9h | `opportunity_scanner.py` | ⚠️ 2x fail |
| CEO Weekly Review | ? | ? | ⚠️ fail |

### 🟢 KG & Data

| Cron | Schedule | Script | Status |
|------|----------|--------|--------|
| KG Access Updater | 4h | `kg_access_updater_optimized.py` | ⚠️ timeout |
| Daily Summary | ? | `daily_summary.py` | ✅ OK |

### 🟢 Security

| Cron | Schedule | Script | Status |
|------|----------|--------|--------|
| Security Audit | 8h | `security-audit.sh` | ✅ OK |
| Security Officer Daily | 10:30 | security session | ✅ OK |

---

## 7.3 DISABLED CRONS (17)

Meist Discord-bezogen weil Discord nicht aktiv:

| Cron | Reason |
|------|--------|
| LCM Wiki Sync | Discord disabled |
| Nightly Dreaming | Disabled (memory-core dreaming stattdessen) |
| Security Officer Discord Report | Discord disabled |
| Diverse Discord Crons | Discord not configured |

---

## 7.4 CRON ERROR HEALER

**Script:** `/SCRIPTS/automation/cron_error_healer.py`

### Was es tut

1. Erkennt fehlgeschlagene Crons
2. Analysiert Error Type
3. Versucht Auto-Repair
4. Disablet Crons bei false positives
5. Lost Tasks Management

### ⚠️ Issue: 65 Lost Tasks

**Status:** Altlast — Threshold bei 70

Der Cron Error Healer hat einige Tasks als "lost" markiert, die nicht gecancelt werden konnten.

---

## 7.5 CRON WATCHDOG

**Script:** `/SCRIPTS/automation/cron_watchdog.py`

**Schedule:** Every 6 hours

**Was es tut:**
1. List all Cron Jobs
2. Check for overdue jobs
3. Log issues
4. Alert if critical

---

## 7.6 CRON SCHEDULER

### OpenClaw Cron Management

```bash
# List all crons
openclaw crons list

# Cron details
openclaw crons get <jobId>

# Manual run
openclaw crons run <jobId>

# Cron runs history
openclaw crons runs <jobId>
```

### Job Schema

```json
{
  "id": "uuid",
  "name": "Job Name",
  "schedule": {
    "kind": "cron",
    "expr": "0 * * * *"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "..."
  },
  "sessionTarget": "isolated",
  "enabled": true
}
```

---

## 7.7 CRON DELIVERY MODES

| Mode | Bedeutung |
|------|----------|
| `none` | Kein Delivery (intern) |
| `announce` | An channel senden |
| `webhook` | HTTP POST |

---

## 7.8 CRON TIMEOUTS

| Cron | Timeout |
|------|---------|
| Learning Loop | 180s |
| Agent Self-Improver | 600s |
| Bug Fix Pipeline | 300s |
| Most others | 60-120s |

---

## 7.9 BEKANNTE ISSUES

| Issue | Status | Notes |
|-------|--------|-------|
| 65 Lost Tasks | ⚠️ | Threshold 70, passiv beobachten |
| KG Access Updater Timeout | ⚠️ | Script OK, nur Cron timeout |
| Opportunity Scanner fail | ⚠️ | Script OK, delivery fail |
| CEO Weekly Review fail | ⚠️ | Delivery failed |

---

## 7.10 STAGGERED EXECUTION

Einige Crons haben `staggerMs` für Jitter:

```json
{
  "schedule": {
    "kind": "cron",
    "expr": "0 * * * *",
    "staggerMs": 300000
  }
}
```

**Bedeutung:** +0-5 min random delay

---

*Modul 07 — Cron System | Sir HazeClaw 🦞*
