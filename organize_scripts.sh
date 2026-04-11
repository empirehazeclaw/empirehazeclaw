#!/bin/bash
# Script Organization - Phase 1
# Moving scripts to categorized folders

SCRIPTS_DIR="/home/clawbot/.openclaw/workspace/scripts"

# CORE - Critical scripts used by system
mv $SCRIPTS_DIR/MEMORY_API.py $SCRIPTS_DIR/core/
mv $SCRIPTS_DIR/cron_error_healer.py $SCRIPTS_DIR/core/
mv $SCRIPTS_DIR/learning_coordinator.py $SCRIPTS_DIR/core/
mv $SCRIPTS_DIR/memory_cleanup.py $SCRIPTS_DIR/maintenance/
mv $SCRIPTS_DIR/memory_hybrid_search.py $SCRIPTS_DIR/analysis/
mv $SCRIPTS_DIR/error_reducer.py $SCRIPTS_DIR/analysis/
mv $SCRIPTS_DIR/error_rate_monitor.py $SCRIPTS_DIR/analysis/

# AUTOMATION - Cron jobs
mv $SCRIPTS_DIR/morning_brief.py $SCRIPTS_DIR/automation/
mv $SCRIPTS_DIR/evening_summary.py $SCRIPTS_DIR/automation/
mv $SCRIPTS_DIR/evening_review.py $SCRIPTS_DIR/automation/
mv $SCRIPTS_DIR/evening_capture.py $SCRIPTS_DIR/automation/
mv $SCRIPTS_DIR/daily_summary.py $SCRIPTS_DIR/automation/
mv $SCRIPTS_DIR/weekly_review.py $SCRIPTS_DIR/automation/
mv $SCRIPTS_DIR/heartbeat_updater.py $SCRIPTS_DIR/automation/
mv $SCRIPTS_DIR/auto_backup.py $SCRIPTS_DIR/automation/
mv $SCRIPTS_DIR/session_cleanup.py $SCRIPTS_DIR/automation/
mv $SCRIPTS_DIR/auto_doc.py $SCRIPTS_DIR/automation/
mv $SCRIPTS_DIR/token_budget_tracker.py $SCRIPTS_DIR/automation/
mv $SCRIPTS_DIR/kg_lifecycle_manager.py $SCRIPTS_DIR/automation/
mv $SCRIPTS_DIR/auto_session_capture.py $SCRIPTS_DIR/automation/

# HEALING - Self-healing related
mv $SCRIPTS_DIR/auto_fixer.py $SCRIPTS_DIR/healing/
mv $SCRIPTS_DIR/quick_fixes.py $SCRIPTS_DIR/healing/
mv $SCRIPTS_DIR/cron_monitor.py $SCRIPTS_DIR/healing/
mv $SCRIPTS_DIR/cron_watchdog.py $SCRIPTS_DIR/healing/
mv $SCRIPTS_DIR/security_audit.py $SCRIPTS_DIR/healing/
mv $SCRIPTS_DIR/common_issues_check.py $SCRIPTS_DIR/healing/

# ANALYSIS - Monitoring and analysis
mv $SCRIPTS_DIR/health_monitor.py $SCRIPTS_DIR/analysis/
mv $SCRIPTS_DIR/self_check.py $SCRIPTS_DIR/analysis/
mv $SCRIPTS_DIR/quick_check.py $SCRIPTS_DIR/analysis/
mv $SCRIPTS_DIR/session_analyzer.py $SCRIPTS_DIR/analysis/
mv $SCRIPTS_DIR/quality_metrics.py $SCRIPTS_DIR/analysis/
mv $SCRIPTS_DIR/trend_analysis.py $SCRIPTS_DIR/analysis/
mv $SCRIPTS_DIR/code_stats.py $SCRIPTS_DIR/analysis/
mv $SCRIPTS_DIR/habit_tracker.py $SCRIPTS_DIR/analysis/
mv $SCRIPTS_DIR/skill_metrics.py $SCRIPTS_DIR/analysis/
mv $SCRIPTS_DIR/token_tracker.py $SCRIPTS_DIR/analysis/
mv $SCRIPTS_DIR/skill_tracker.py $SCRIPTS_DIR/analysis/
mv $SCRIPTS_DIR/tool_usage_analytics.py $SCRIPTS_DIR/analysis/
mv $SCRIPTS_DIR/efficiency_tracker.py $SCRIPTS_DIR/analysis/
mv $SCRIPTS_DIR/performance_dashboard.py $SCRIPTS_DIR/analysis/
mv $SCRIPTS_DIR/github_stats.py $SCRIPTS_DIR/analysis/
mv $SCRIPTS_DIR/openrouter_monitor.py $SCRIPTS_DIR/analysis/
mv $SCRIPTS_DIR/error_reduction_strategy.py $SCRIPTS_DIR/analysis/
mv $SCRIPTS_DIR/error_reduction_plan.py $SCRIPTS_DIR/analysis/

# LEARNING - Self-improvement
mv $SCRIPTS_DIR/meta_improver.py $SCRIPTS_DIR/core/
mv $SCRIPTS_DIR/self_play_improver.py $SCRIPTS_DIR/core/
mv $SCRIPTS_DIR/self_eval.py $SCRIPTS_DIR/core/
mv $SCRIPTS_DIR/deep_reflection.py $SCRIPTS_DIR/experimental/
mv $SCRIPTS_DIR/reflection_loop.py $SCRIPTS_DIR/experimental/
mv $SCRIPTS_DIR/autonomous_improvement.py $SCRIPTS_DIR/core/
mv $SCRIPTS_DIR/continuous_improver.py $SCRIPTS_DIR/core/
mv $SCRIPTS_DIR/innovation_research.py $SCRIPTS_DIR/analysis/
mv $SCRIPTS_DIR/self_improvement_monitor.py $SCRIPTS_DIR/analysis/
mv $SCRIPTS_DIR/learning_tracker.py $SCRIPTS_DIR/analysis/
mv $SCRIPTS_DIR/pattern_extractor.py $SCRIPTS_DIR/experimental/
mv $SCRIPTS_DIR/evolve.py $SCRIPTS_DIR/experimental/
mv $SCRIPTS_DIR/gene_diversity_tracker.py $SCRIPTS_DIR/experimental/
mv $SCRIPTS_DIR/blast_radius_estimator.py $SCRIPTS_DIR/experimental/

# MEMORY - Memory related
mv $SCRIPTS_DIR/memory_reranker.py $SCRIPTS_DIR/core/
mv $SCRIPTS_DIR/kg_updater.py $SCRIPTS_DIR/core/
mv $SCRIPTS_DIR/kg_enhancer.py $SCRIPTS_DIR/core/
mv $SCRIPTS_DIR/session_compressor.py $SCRIPTS_DIR/core/

# COMMUNICATION - Outreach
mv $SCRIPTS_DIR/llm_outreach.py $SCRIPTS_DIR/archive/
mv $SCRIPTS_DIR/email_sequence.py $SCRIPTS_DIR/archive/
mv $SCRIPTS_DIR/automated_outreach.py $SCRIPTS_DIR/archive/
mv $SCRIPTS_DIR/improved_outreach.py $SCRIPTS_DIR/archive/
mv $SCRIPTS_DIR/quick_outreach.py $SCRIPTS_DIR/archive/
mv $SCRIPTS_DIR/crm_manager.py $SCRIPTS_DIR/archive/
mv $SCRIPTS_DIR/discord_report_forwarder.py $SCRIPTS_DIR/archive/

# SYSTEM - System utilities
mv $SCRIPTS_DIR/gateway_recovery.py $SCRIPTS_DIR/automation/
mv $SCRIPTS_DIR/health_alert.py $SCRIPTS_DIR/automation/
mv $SCRIPTS_DIR/mcp_server.py $SCRIPTS_DIR/archive/
mv $SCRIPTS_DIR/lcm_wiki_sync.py $SCRIPTS_DIR/automation/
mv $SCRIPTS_DIR/system_report.py $SCRIPTS_DIR/analysis/

# ONE-OFF / EXPERIMENTAL
mv $SCRIPTS_DIR/apply_timeouts.py $SCRIPTS_DIR/archive/
mv $SCRIPTS_DIR/batch_exec.py $SCRIPTS_DIR/archive/
mv $SCRIPTS_DIR/backup_verify.py $SCRIPTS_DIR/archive/
mv $SCRIPTS_DIR/skill_creator.py $SCRIPTS_DIR/experimental/
mv $SCRIPTS_DIR/session_analysis_cron.py $SCRIPTS_DIR/archive/
mv $SCRIPTS_DIR/git_maintenance.py $SCRIPTS_DIR/archive/
mv $SCRIPTS_DIR/fast_test.py $SCRIPTS_DIR/experimental/
mv $SCRIPTS_DIR/test_framework.py $SCRIPTS_DIR/experimental/

echo "Done. Check structure:"
ls -la $SCRIPTS_DIR/
echo ""
for dir in core automation maintenance analysis healing experimental archive; do
    count=$(ls $SCRIPTS_DIR/$dir/*.py 2>/dev/null | wc -l)
    echo "$dir: $count files"
done
