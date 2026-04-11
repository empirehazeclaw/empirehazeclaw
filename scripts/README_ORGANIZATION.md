# 📁 SCRIPTS ORGANIZATION
## Sir HazeClaw — Logical Structure
**Created:** 2026-04-11 21:44 UTC
**Updated:** 2026-04-11 23:10 UTC

---

## 🎯 GOAL: 83 → ~40 Scripts

### Current Status: 96 scripts (after adding new patterns)
### Target: ~40 scripts (50% reduction)

---

## ✅ CONSOLIDATION PROGRESS

### DONE:
- [x] **health_check.py** — Consolidated from 4 scripts
  - Replaces: health_monitor.py, health_alert.py, quick_check.py, self_check.py
  - Modes: --quick, --full, --gateway, --disk, --memory, --crons, --kg, --alert

### Pending:
- [ ] error_analysis scripts (3 → 1)
- [ ] metrics scripts (3 → 1)
- [ ] Archive 14 unused scripts

---

---

## 📂 LOGICAL FOLDER STRUCTURE

```
scripts/
│
├── 📦 CORE (Critical - Must Keep)
│   ├── MEMORY_API.py              # Unified memory interface
│   ├── learning_coordinator.py     # Main learning loop
│   ├── meta_improver.py           # Self-improvement
│   ├── self_play_improver.py      # Self-play pattern
│   ├── self_eval.py              # Self-evaluation
│   ├── cron_error_healer.py      # Self-healing (v2!)
│   ├── memory_reranker.py        # Memory search
│   ├── kg_updater.py             # Knowledge graph
│   ├── kg_enhancer.py            # KG enrichment
│   └── session_compressor.py      # Session compression
│
├── 🔄 AUTOMATION (Cron Jobs)
│   ├── morning_brief.py          # Daily briefing
│   ├── evening_summary.py         # Evening summary
│   ├── evening_review.py          # Evening review
│   ├── evening_capture.py         # Fleeting notes
│   ├── daily_summary.py           # Daily summary
│   ├── weekly_review.py          # Weekly review
│   ├── heartbeat_updater.py       # HEARTBEAT update
│   ├── auto_backup.py            # Backup
│   ├── session_cleanup.py         # Session cleanup
│   ├── auto_doc.py               # Documentation
│   ├── token_budget_tracker.py   # Token monitoring
│   ├── kg_lifecycle_manager.py   # KG maintenance
│   ├── gateway_recovery.py       # Gateway auto-restart
│   ├── health_alert.py          # Health alerts
│   └── auto_session_capture.py   # Session capture
│
├── 📊 ANALYSIS (Monitoring & Tools)
│   ├── memory_hybrid_search.py   # Memory search
│   ├── error_reducer.py          # Error analysis
│   ├── error_rate_monitor.py     # Error tracking
│   ├── error_reduction_strategy.py
│   ├── error_reduction_plan.py
│   ├── health_monitor.py        # System health
│   ├── self_check.py            # Self-check
│   ├── quick_check.py           # Quick health check
│   ├── session_analyzer.py      # Session analysis
│   ├── quality_metrics.py       # Quality tracking
│   ├── trend_analysis.py        # Trend analysis
│   ├── code_stats.py            # Code statistics
│   ├── habit_tracker.py         # Habit tracking
│   ├── skill_metrics.py         # Skill metrics
│   ├── token_tracker.py         # Token tracking
│   ├── skill_tracker.py         # Skill tracking
│   ├── tool_usage_analytics.py  # Tool usage
│   ├── efficiency_tracker.py     # Efficiency
│   ├── performance_dashboard.py # Dashboard
│   ├── github_stats.py          # GitHub stats
│   ├── openrouter_monitor.py    # API monitoring
│   ├── innovation_research.py   # Innovation
│   ├── self_improvement_monitor.py
│   ├── learning_tracker.py       # Learning tracking
│   ├── system_report.py         # System reports
│   └── memory_cleanup.py        # Memory cleanup
│
├── 🏥 HEALING (Self-Healing)
│   ├── auto_fixer.py            # Auto-fix
│   ├── quick_fixes.py           # Quick fixes
│   ├── cron_monitor.py          # Cron monitoring
│   ├── cron_watchdog.py         # Cron watchdog
│   ├── security_audit.py        # Security
│   └── common_issues_check.py   # Common issues
│
├── 🔬 EXPERIMENTAL (One-offs, Tests)
│   ├── deep_reflection.py
│   ├── reflection_loop.py
│   ├── pattern_extractor.py
│   ├── evolve.py
│   ├── gene_diversity_tracker.py
│   ├── blast_radius_estimator.py
│   ├── skill_creator.py
│   ├── fast_test.py
│   └── test_framework.py
│
└── 📦 ARCHIVE (Unused, Legacy)
    ├── llm_outreach.py          # Outreach (unused)
    ├── email_sequence.py         # Email (unused)
    ├── automated_outreach.py     # Outreach (unused)
    ├── improved_outreach.py     # Outreach (unused)
    ├── quick_outreach.py         # Outreach (unused)
    ├── crm_manager.py          # CRM (unused)
    ├── discord_report_forwarder.py
    ├── mcp_server.py
    ├── apply_timeouts.py
    ├── batch_exec.py
    ├── backup_verify.py
    ├── session_analysis_cron.py
    ├── git_maintenance.py
    └── autonomous_improvement.py
```

---

## 📊 COUNTS

| Folder | Count | Status |
|--------|-------|--------|
| Core | 12 | Keep |
| Automation | 15 | Keep |
| Analysis | 27 | Keep (some can merge) |
| Healing | 6 | Keep |
| Experimental | 9 | Review |
| Archive | 14 | Can delete |

**Total: 83 scripts**

---

## 🎯 CONSOLIDATION OPPORTUNITIES

### Merge into Analysis (~10 scripts saved):
- health_monitor.py + self_check.py + quick_check.py → health_check.py
- error_reducer.py + error_rate_monitor.py + error_reduction_*.py → error_analysis.py
- quality_metrics.py + efficiency_tracker.py + performance_dashboard.py → metrics.py
- skill_tracker.py + skill_metrics.py + tool_usage_analytics.py → skill_analytics.py

### Archive (14 scripts):
- All outreach scripts (6) — not used
- crm_manager.py — not used
- mcp_server.py — not integrated
- batch_exec.py, backup_verify.py — one-offs
- autonomous_improvement.py — merged into continuous_improver

---

## ✅ RECOMMENDED ACTIONS

### Week 1:
1. [ ] Merge 4 health check scripts → 1
2. [ ] Merge 3 error scripts → 1
3. [ ] Merge 3 metrics scripts → 1
4. [ ] Archive 14 unused scripts

### Result: 83 - 10 = **73 scripts** (closer to 40)

### Week 2:
5. [ ] Further consolidation where possible
6. [ ] Add README to each folder
7. [ ] Update cron references if needed

---

## ⚠️ CAUTION

Before moving files:
1. Check all cron jobs reference correct paths
2. Check all imports in other scripts
3. Test after each move

**Recommendation:** Don't physically move files until all references are updated.

---

*This is a logical organization. Physical moves require careful reference updates.*
