# 📋 SCRIPT INVENTORY — 2026-04-11 12:35 UTC

**Total Scripts:** 83
**Cron-Referenziert:** 13
**Standalone Utility:** 70

---

## 🔴 KEEP — Cron Referenziert (13)

| Script | Lines | Zweck | Status |
|--------|-------|-------|--------|
| `auto_backup.py` | 250 | Workspace Backup (Daily) | ✅ CRON |
| `auto_doc.py` | 250 | Auto Documentation (Weekly) | ✅ CRON |
| `cron_watchdog.py` | 104 | Cron Job Monitoring (6h) | ✅ CRON |
| `discord_report_forwarder.py` | 161 | Discord → Telegram Forwarder | ✅ CRON |
| `evening_capture.py` | 62 | Evening Memory Capture (21h) | ✅ CRON |
| `gateway_recovery.py` | 211 | Gateway Auto-Recovery (5min) | ✅ CRON |
| `innovation_research.py` | 188 | Innovation Research (14h) | ✅ CRON |
| `lcm_wiki_sync.py` | 432 | Wiki Sync | ✅ CRON |
| `learning_coordinator.py` | 342 | Learning Loop Coordinator (Hourly) | ✅ CRON |
| `morning_brief.py` | 389 | Morning Brief (11h Berlin) | ✅ CRON |
| `quick_check.py` | 83 | Health Check (3h) | ✅ CRON |
| `weekly_review.py` | 362 | Weekly Review | ✅ CRON |
| `lcm_memory_sync.py` | ? | Memory Sync (in cron but not found) | ⚠️ |

---

## 🟡 KEEP — Wichtige Standalone Tools (26)

Diese Scripts werden von mir oder anderen Tools aktiv verwendet:

| Script | Lines | Zweck | Verwendung |
|--------|-------|-------|------------|
| `memory_reranker.py` | 301 | Memory Search Ranking | memory_hybrid_search.py |
| `memory_hybrid_search.py` | 342 | Hybrid Memory Search | Learning Coordinator |
| `session_cleanup.py` | 213 | Session Maintenance | Cron/Cleanup |
| `cron_error_healer.py` | 302 | Auto-Heal Cron Errors | On-Demand |
| `cron_monitor.py` | 184 | Cron Status Monitor | Monitoring |
| `health_monitor.py` | 335 | Health Monitoring | On-Demand |
| `self_check.py` | 275 | Self Health Check | On-Demand |
| `self_eval.py` | 375 | Self Evaluation | Weekly |
| `test_framework.py` | 656 | Test Framework | Development |
| `git_maintenance.py` | 218 | Git Cleanup | Weekly Cron |
| `trend_analysis.py` | 216 | Performance Trends | Dashboard |
| `token_tracker.py` | 149 | Token Tracking | Learning Coordinator |
| `mcp_server.py` | 258 | MCP Server | Tools |
| `security_audit.py` | 91 | Security Audit | Cron (error) |
| `memory_cleanup.py` | 400 | Memory Cleanup | Maintenance |
| `kg_enhancer.py` | 191 | KG Enhancement | Learning |
| `kg_updater.py` | 287 | KG Update | Maintenance |
| `daily_summary.py` | 310 | Daily Summary | Evening |
| `auto_session_capture.py` | 238 | Session Capture | Automation |
| `system_report.py` | 188 | System Report | On-Demand |
| `health_alert.py` | 161 | Health Alerts | Monitoring |
| `backup_verify.py` | 196 | Backup Verification | Maintenance |
| `fast_test.py` | 105 | Fast Test Runner | Development |
| `lcm_memory_sync.py` | ? | Memory Sync | ? |
| `evening_summary.py` | 304 | Evening Summary | Cron (idle) |
| `deep_reflection.py` | 369 | Deep Reflection | Idle |

---

## 🟢 NEEDS REVIEW — Unklar ob benötigt (19)

| Script | Lines | Docstring | Notes |
|--------|-------|-----------|-------|
| `automated_outreach.py` | 210 | Outreach Automation | CRM related |
| `batch_exec.py` | 52 | Batch Execution | Minimal |
| `common_issues_check.py` | 106 | Common Issues | Monitoring |
| `crm_manager.py` | 207 | CRM Management | Outreach related |
| `email_sequence.py` | 289 | Email Sequences | Outreach |
| `evolve.py` | 169 | Evolution | Old capability |
| `github_stats.py` | 146 | GitHub Stats | Stats |
| `habit_tracker.py` | 286 | Habit Tracking | Personal |
| `improved_outreach.py` | 156 | Improved Outreach | Duplikat? |
| `llm_outreach.py` | 325 | LLM Outreach | Outreach |
| `meeting_scheduler.py` | 191 | Meeting Scheduler | Outreach |
| `openrouter_monitor.py` | 90 | OpenRouter Monitor | API Monitor |
| `outreach_optimizer.py` | 218 | Outreach Optimizer | Outreach |
| `priority_filter.py` | 185 | Priority Filter | Outreach |
| `quick_outreach.py` | 141 | Quick Outreach | Outreach |
| `reflection_loop.py` | 154 | Reflection Loop | Learning |
| `response_tracker.py` | 154 | Response Tracker | Outreach |
| `revenue_forecaster.py` | 205 | Revenue Forecast | Business |
| `skill_creator.py` | 201 | Skill Creator | Skill Dev |

---

## 🔵 LOW VALUE — Wahrscheinlich Archivieren (15)

| Script | Lines | Problem |
|--------|-------|---------|
| `demo_scheduler.py` | 148 | Wurde nie verwendet |
| `deploy_safety.py` | 172 | Nicht verwendet |
| `idempotency_check.py` | 63 | Veraltet |
| `kgml_summary.py` | 110 | Nicht verwendet |
| `lead_generator.py` | 145 | Duplikat CRM |
| `loop_check.py` | 109 | NO SPAM Policy → nicht nötig |
| `model_config.py` | 69 | Nicht verwendet |
| `morning_check.py` | 67 | Duplikat quick_check.py |
| `morning_routine.py` | 124 | Duplikat morning_brief.py |
| `evening_routine.py` | 129 | Duplikat evening_capture.py |
| `semantic_search.py` | 113 | Duplikat memory_hybrid_search.py |
| `session_memory_manager.py` | 133 | Duplikat memory_reranker.py |
| `skill_loader.py` | 137 | Nicht verwendet |
| `subagent_health_check.py` | 67 | Nicht verwendet |
| `telegram_alert.py` | 65 | Duplikat health_alert.py |
| `telegram_memory_extractor.py` | 273 | Nicht verwendet |
| `telegram_parser.py` | 140 | Chat Import, nicht mehr nötig |
| `tool_usage_analytics.py` | 169 | Analytics |
| `vault.py` | 184 | Nicht verwendet |
| `vercel_monitor.py` | 175 | Nicht verwendet |
| `verify_delivery.py` | 95 | Nicht verwendet |
| `weekly_review_zettel.py` | 123 | Duplikat weekly_review.py |

---

## 📊 ZUSAMMENFASSUNG

| Kategorie | Anzahl | Aktion |
|-----------|--------|--------|
| Cron Referenziert | 13 | ✅ Behalten |
| Standalone Wichtig | 26 | ✅ Behalten |
| Needs Review | 19 | ⏳ Prüfen |
| Low Value | 22 | 🚫 Archivieren |

**Total Behalten:** 39 (47%)
**Total Archivieren:** 22 (27%)
**Total Review:** 19 (23%)

---

## ⏳ OFFENE FRAGEN

1. **Outreach Scripts (8):** `automated_outreach`, `improved_outreach`, `llm_outreach`, `quick_outreach`, `email_sequence`, `crm_manager`, `outreach_optimizer`, `lead_generator`
   - Werden diese für QMD/Akquise benötigt?

2. **Learning Scripts (4):** `reflection_loop`, `evolve`, `skill_creator`, `learning_tracker`
   - Sind diese Teil des Learning Loop?

3. **Stats/Monitor (6):** `github_stats`, `openrouter_monitor`, `tool_usage_analytics`, `priority_filter`, `response_tracker`, `revenue_forecaster`
   - Werden Stats überhaupt genutzt?

4. **Telegram (3):** `telegram_parser`, `telegram_memory_extractor`, `telegram_alert`
   - telegram_alert ist Duplikat, andere 2?

---

*Erstellt: 2026-04-11 12:35 UTC*
*Status: ⏳ REVIEW REQUIRED - 19 scripts need manual review*
