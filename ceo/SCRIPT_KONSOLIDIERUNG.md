# 📋 SCRIPT KONSOLIDIERUNG — 2026-04-11 12:35 UTC

## 📊 IST-ZUSTAND

| Kategorie | Anzahl |
|-----------|--------|
| Total Scripts | 83 |
| Cron-Referenziert | 12 |
| Non-Cron | 71 |

---

## 🔴 KEEP (Critical - Cron Used)

Diese Scripts werden aktiv von Cron Jobs verwendet:

| Script | Cron | Zweck |
|--------|------|-------|
| `auto_backup.py` | Daily Backup | Workspace Backup |
| `auto_doc.py` | Weekly Doc | Auto Documentation |
| `cron_watchdog.py` | 6h | Cron Monitoring |
| `discord_report_forwarder.py` | ? | Discord Reports |
| `evening_capture.py` | 21h | Evening Memory |
| `gateway_recovery.py` | 5min | Gateway Restart |
| `innovation_research.py` | 14h | Innovation Research |
| `lcm_wiki_sync.py` | ? | Wiki Sync |
| `learning_coordinator.py` | Hourly | Learning Loop |
| `morning_brief.py` | 11h Berlin | Morning Brief |
| `quick_check.py` | 3h | Health Check |
| `weekly_review.py` | Weekly | Weekly Review |

**Anzahl: 12** ✅

---

## 🟡 KEEP (Utility - Important Tools)

Diese Scripts werden von anderen Scripts/Tools verwendet:

| Script | Verwendet von | Zweck |
|--------|--------------|-------|
| `memory_reranker.py` | memory_hybrid_search | Memory Search Ranking |
| `memory_hybrid_search.py` | Learning Coordinator | Hybrid Search |
| `session_cleanup.py` | Cron/Cleanup | Session Maintenance |
| `self_check.py` | On-Demand | Self Health Check |
| `test_framework.py` | Development | Testing |
| `git_maintenance.py` | Weekly Cron | Git Cleanup |
| `cron_error_healer.py` | On-Demand | Cron Error Healing |
| `cron_monitor.py` | Monitoring | Cron Status |
| `health_monitor.py` | On-Demand | Health Monitoring |
| `trend_analysis.py` | Dashboard | Performance Trends |
| `token_tracker.py` | Learning Coordinator | Token Tracking |

**Anzahl: 11** ✅

---

## 🟢 ARCHIVE (Redundant/Unused)

Diese Scripts sind redundant oder werden nie verwendet:

| Script | Grund |
|--------|-------|
| `deep_reflection.py` | Veraltet, nightly_dreaming.py besser |
| `demo_scheduler.py` | Wurde nie verwendet |
| `evolve.py` | Veraltet, capability_evolution.py |
| `loop_check.py` | NO SPAM Policy - nicht mehr nötig |
| `idempotency_check.py` | Veraltet |
| `quick_outreach.py` | Duplikat von automated_outreach.py |
| `improved_outreach.py` | Duplikat |
| `llm_outreach.py` | Duplikat |
| `email_sequence.py` | Wurde nie verwendet |
| `lead_generator.py` | CRM Manager besser |
| `priority_filter.py` | Veraltet |
| `reschedule_sovereign.py` | Alte Architektur |
| `revenue_forecaster.py` | Wurde nie verwendet |
| `semantic_search.py` | Duplikat memory_hybrid_search.py |
| `session_memory_manager.py` | Duplikat memory_reranker.py |
| `skill_creator.py` | Nicht verwendet |
| `skill_loader.py` | Nicht verwendet |
| `subagent_health_check.py` | Nicht verwendet |
| `telegram_alert.py` | Duplikat health_alert.py |
| `telegram_memory_extractor.py` | Nicht verwendet |
| `telegram_parser.py` | Chat History Import - wird nicht mehr verwendet |
| `weekly_review_zettel.py` | Duplikat weekly_review.py |
| `verify_delivery.py` | Nicht verwendet |
| `vercel_monitor.py` | Nicht verwendet |
| `vault.py` | Nicht verwendet |
| `morning_check.py` | Duplikat quick_check.py |
| `morning_routine.py` | Duplikat morning_brief.py |
| `evening_routine.py` | Duplikat evening_capture.py |
| `evening_summary.py` | Duplikat |
| `health_dashboard.py` | Nicht verwendet |
| `kgml_summary.py` | Nicht verwendet |
| `batch_exec.py` | Nicht verwendet |
| `autonomous_improvement.py` | Duplikat learning_coordinator.py |
| `deploy_safety.py` | Nicht verwendet |
| `learning_tracker.py` | Nicht verwendet |
| `response_tracker.py` | Nicht verwendet |
| `openrouter_monitor.py` | Nicht verwendet |
| `outreach_optimizer.py` | Nicht verwendet |
| `common_issues_check.py` | Nicht verwendet |
| `auto_session_capture.py` | Nicht verwendet |
| `security_audit.py` | Cron mit error, nicht fix |
| `crm_manager.py` | Nicht verwendet |
| `model_config.py` | Nicht verwendet |
| `github_stats.py` | Nicht verwendet |
| `habit_tracker.py` | Nicht verwendet |
| `reflection_loop.py` | Nicht verwendet |
| `kg_enhancer.py` | Nicht verwendet |
| `kg_updater.py` | Nicht verwendet |

**Anzahl: 50** 🚫 ZU ARCHIVIEREN

---

## 📋 AKTIONSPLAN

### SOFORT (1h):

| # | Action | Scripts |
|---|--------|--------|
| 1 | Archiviere 50 redundante Scripts | Batch Move |
| 2 | Behalte 23 wichtige Scripts | 12 cron + 11 utility |
| 3 | Prüfe remaining 10 Scripts | ob sie useful sind |

### ERGEBNIS:

| Vorher | Nachher |
|--------|---------|
| 83 Scripts | **23 Scripts** (28%) |
| 50 Archiviert | **50 Archiviert** |
| Redundanz | **-72%** |

---

## ⏳ OFFEN: Remaining 10 Scripts

Diese müssen noch kategorisiert werden:

```
auto_session_capture.py
batch_exec.py
common_issues_check.py
crm_manager.py
github_stats.py
habit_tracker.py
openrouter_monitor.py
outreach_optimizer.py
security_audit.py (error cron)
tool_usage_analytics.py
```

---

*Erstellt: 2026-04-11 12:35 UTC*
*Status: ⏳ OFFEN - Archivierung erfordert Approval*
