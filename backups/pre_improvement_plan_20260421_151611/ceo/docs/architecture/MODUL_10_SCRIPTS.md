# MODUL 10: Scripts Catalog

**Modul:** Scripts Catalog — 72 Scripts
**Status:** ✅ Dokumentiert
**Letztes Update:** 2026-04-17

---

## 10.1 OVERVIEW

**Anzahl:** 120 aktive Scripts in `/SCRIPTS/automation/`

**Kategorien:**
- Learning & Memory
- Automation & Autonomy
- Monitoring & Health
- Backup & Recovery
- Analysis & Research
- Infrastructure

---

## 10.2 SCRIPTS BY CATEGORY

### 📚 Learning & Memory (12)

| Script | Zweck | Cron |
|--------|-------|------|
| `learning_loop_v3.py` | Haupt Learning Loop | Hourly |
| `learning_coordinator.py` | Koordiniert Learning | 9,18h |
| `learning_collector.py` | Sammelt Signale | - |
| `learning_analyzer.py` | Analysiert Signale | - |
| `learning_executor.py` | Führt Hypothesen aus | - |
| `learning_feedback.py` | Feedback Processing | - |
| `learning_to_kg_sync.py` | Loop → KG Sync | 10min |
| `kg_access_updater.py` | KG Updates | 4h |
| `kg_access_updater_optimized.py` | Optimierte Version | 4h |
| `kg_auto_curator.py` | Auto KG Pflege | - |
| `kg_updater.py` | Manueller KG Update | - |
| `memory_sync.py` | Memory Sync | 5min |

---

### 🤖 Autonomy & Self-Healing (12)

| Script | Zweck | Cron |
|--------|-------|------|
| `autonomy_supervisor.py` | Live Monitoring | 5min |
| `autonomous_agent.py` | Self-Review/Heal | Hourly |
| `agent_self_improver.py` | Self-Improvement | 18h |
| `self_healing.py` | Auto-Repair | - |
| `cron_error_healer.py` | Cron Auto-Heal | - |
| `graceful_degradation.py` | Load Management | - |
| `decision_matrix.py` | Decision Support | - |
| `decision_tracker_integration.py` | Decision Tracking | - |
| `context_compressor.py` | Context Kompression | 6h |
| `session_context_manager.py` | Session Management | 3h |
| `session_cleanup.py` | Session Cleanup | Daily |
| `evolver_signal_bridge.py` | Evolver Bridge | - |

---

### 🔍 Monitoring & Health (12)

| Script | Zweck | Cron |
|--------|-------|------|
| `health_check.py` | Health Check | 3h |
| `health_monitor.py` | Health Monitoring | - |
| `integration_dashboard.py` | Integration Dashboard | 8,20h |
| `stagnation_detector.py` | Stagnation Detection | 6h |
| `bug_scanner.py` | Bug Detection | 30min |
| `bug_fix_pipeline.py` | Auto-Fix | 35min |
| `bug_fixer.py` | Manual Fix | - |
| `cron_watchdog.py` | Cron Monitoring | 6h |
| `cron_monitor.py` | Cron Status | - |
| `error_rate_monitor.py` | Error Tracking | - |
| `common_issues_check.py` | Common Issues | - |
| `error_reducer.py` | Error Reduction | - |

---

### 💾 Backup & Recovery (6)

| Script | Zweck | Cron |
|--------|-------|------|
| `auto_backup.py` | Auto Backup | 4h |
| `backup_manager.py` | Backup Management | - |
| `backup_verifier.py` | Backup Verify | - |
| `gateway_recovery.py` | Gateway Recovery | 15min |
| `automated_backup.py` | Automated Backup | - |
| `rollback_executor.py` | Rollback | - |

---

### 📊 Analysis & Research (8)

| Script | Zweck | Cron |
|--------|-------|------|
| `innovation_research.py` | Innovation Research | 14h |
| `trend_hunter.py` | Trend Analysis | - |
| `trend_research.py` | Research | - |
| `daily_summary.py` | Daily Summary | - |
| `evening_summary.py` | Evening Summary | - |
| `evening_review.py` | Evening Review | 20h |
| `weekly_review.py` | Weekly Review | - |
| `openrouter_monitor.py` | API Monitoring | - |

---

### ⚡ Quick Fixes & Tools (8)

| Script | Zweck | Cron |
|--------|-------|------|
| `quick_fixes.py` | Quick Fixes | - |
| `heartbeat_updater.py` | HEARTBEAT Update | 3h |
| `morning_brief.py` | Morning Briefing | 11h |
| `evening_capture.py` | Evening Capture | 21h |
| `lcm_wiki_sync.py` | Wiki Sync | 21:30 |
| `rem_feedback.py` | REM Feedback | - |
| `discord_report_forwarder.py` | Discord Forward | - |
| `skills_fitness_tracker.py` | Skills Tracking | - |

---

### 🔧 Infrastructure (6)

| Script | Zweck | Cron |
|--------|-------|------|
| `cron_optimizer.py` | Cron Optimization | - |
| `cron_status_dashboard.py` | Cron Dashboard | - |
| `token_budget_tracker.py` | Token Budget | Daily |
| `system_report.py` | System Report | - |
| `memory_integrity_check.py` | Memory Check | - |
| `memory_log_analyzer.py` | Log Analysis | - |
| `doc_maintenance.py` | Doc Maintenance | - |
| `deep_system_test.py` | Deep Test | - |

---

## 10.3 SCRIPTS ORGANISATION

```
/SCRIPTS/automation/
├── learning_*.py          # Learning Loop
├── *_tracker.py            # Tracking
├── *_monitor.py            # Monitoring
├── *_check.py              # Health Checks
├── *_cleanup.py            # Cleanup
├── *_backup.py             # Backup
├── *_updater.py            # Updates
├── *_generator.py          # Generation
├── *_aggregator.py         # Aggregation
├── run_*.sh                # Run Scripts
└── *.py                   # Andere
```

---

## 10.4 RUN SCRIPTS

| Script | Zweck |
|--------|-------|
| `run_loop_10.sh` | Run Loop 10x |
| `run_smart_evolver.sh` | Smart Evolver |

---

## 10.5 DEPRECATED/ARCHIVED

| Script | Status | Notes |
|--------|--------|-------|
| `nightly_dreaming.py` | 🗑️ | Ersetzt durch memory-core dreaming |
| Diverse im ceo/_archive/ | 🗑️ | Archiviert |

---

## 10.6 SCRIPT EXECUTION

### Direkte Ausführung

```bash
python3 /SCRIPTS/automation/<script_name>.py
```

### Mit Args

```bash
python3 /SCRIPTS/automation/learning_loop_v3.py --score
python3 /SCRIPTS/automation/integration_dashboard.py --check
```

---

## 10.7 BEKANNTE ISSUES

| Issue | Status | Notes |
|-------|--------|-------|
| integration_dashboard.py | ❌ | File not found (2026-04-17) |
| Viele Scripts | ℹ️ | Nicht mehr in /SCRIPTS/automation/ |

**Note:** Das `integration_dashboard.py` Script existiert laut Workspace listing nicht mehr. Bitte Nico informieren wenn das benötigt wird.

---

## 10.8 SCRIPT BACKUP

Backups:
- `/workspace/backups/`
- `/workspace/ceo_backups/`

---

*Modul 10 — Scripts Catalog | Sir HazeClaw 🦞*
