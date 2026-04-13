#!/bin/bash
#==============================================================================
# KILL DAY - Agent Consolidation Script
#==============================================================================
# Usage:
#   ./kill_day.sh --dry-run    # Shows what would be deleted (SAFE)
#   ./kill_day.sh --execute   # Actually deletes (requires confirmation)
#   ./kill_day.sh --list      # Lists all agents to be killed
#
# Backup location: /home/clawbot/.openclaw/workspace/archive/agents_backup/
#==============================================================================

set -uo pipefail

AGENTS_DIR="/home/clawbot/.openclaw/workspace/agents"
BACKUP_DIR="/home/clawbot/.openclaw/workspace/archive/agents_backup"
PLAN_FILE="/home/clawbot/.openclaw/workspace/AGENT_CONSOLIDATION_PLAN.md"
LOG_FILE="/home/clawbot/.openclaw/workspace/logs/kill_day.log"

#------------------------------------------------------------------------------
# Agents to KILL (from AGENT_CONSOLIDATION_PLAN.md)
# These are organized by category
#------------------------------------------------------------------------------
KILL_LIST=(
    #=== TINY STUBS (<20 lines) ===
    "gardening_agent.py"
    "petcare_agent.py"
    "photography_agent.py"
    "home_agent.py"
    "support_agent.py"
    "translation_agent.py"

    #=== DEPRECATED _llm.py VARIANTS ===
    "cold_outreach_llm.py"
    "lead_qualifier_llm.py"
    "content_production_llm.py"
    "sales_executor_llm.py"

    #=== INFRASTRUCTURE WRAPPERS ===
    "agent_hub.py"
    "agent_wrapper.py"
    "agent-dashboard.js"
    "shared_memory.py"
    "shared-memory.js"
    "event-bus.js"
    "error-handler.js"
    "auto-scaler.js"
    "auto-learn.js"
    "multi-agent.js"
    "escalation.py"
    "learning.py"

    #=== VERTICAL-SPECIFIC AGENTS ===
    "access_auditor_agent.py"
    "accounts_payable_agent.py"
    "blockchain_analyst_agent.py"
    "book_writer_agent.py"
    "clinical_notes_agent.py"
    "commercial_re_agent.py"
    "compensation_benchmarker_agent.py"
    "curriculum_designer_agent.py"
    "essay_grader_agent.py"
    "exit_interview_agent.py"
    "family_coordinator_agent.py"
    "flashcard_generator_agent.py"
    "flight_scraper_agent.py"
    "fraud_detector_agent.py"
    "game_designer_agent.py"
    "habit_tracker_agent.py"
    "inventory_forecaster_agent.py"
    "inventory_tracker_agent.py"
    "invoice_manager_agent.py"
    "job_applicant_agent.py"
    "language_tutor_agent.py"
    "legal_brief_writer_agent.py"
    "meal_planner_agent.py"
    "medical_checker_agent.py"
    "medication_checker_agent.py"
    "nda_generator_agent.py"
    "patent_analyzer_agent.py"
    "patient_intake_agent.py"
    "performance_reviewer_agent.py"
    "phishing_detector_agent.py"
    "portfolio_rebalancer_agent.py"
    "property_video_agent.py"
    "recruiter_agent.py"
    "resume_optimizer_agent.py"
    "resume_screener_agent.py"
    "route_optimizer_agent.py"
    "study_planner_agent.py"
    "symptom_triage_agent.py"
    "tax_preparer_agent.py"
    "telemarketer_agent.py"
    "threat_monitor_agent.py"
    "travel_planner_agent.py"
    "tutor_agent.py"
    "upwork_proposal_agent.py"
    "voicemail_transcriber_agent.py"
    "wellness_coach_agent.py"
    "workout_tracker_agent.py"
    "dropshipping_researcher_agent.py"
    "listing_scout_agent.py"
    "product_lister_agent.py"
    "contract_reviewer_agent.py"
    "roi_tracker_agent.py"
    "survey_analyzer_agent.py"
    "transcription_agent.py"
    "audio_producer_agent.py"
    "thumbnail_designer_agent.py"
    "storyboard_writer_agent.py"
    "brand_designer_agent.py"
    "podcast_producer_agent.py"
    "ugc_video_agent.py"
    "video_scripter_agent.py"
    "brand_monitor_agent.py"
    "influencer_finder_agent.py"
    "review_responder_agent.py"
    "youtube_seo_agent.py"

    #=== DUPLICATE/SIMILAR AGENTS ===
    "ab_testing_agent.py"
    "code_reviewer_agent.py"
    "daily_standup_agent.py"
    "dashboard_builder_agent.py"
    "data_entry_agent.py"
    "deploy_guardian_agent.py"
    "deployment_agent_agent.py"
    "price_monitor_agent.py"
    "competitor_watch_agent.py"
    "competitor_pricing_agent.py"
    "churn_predictor_agent.py"
    "funnel_analysis_agent.py"
    "linkedin_content_agent.py"
    "multi_account_social_agent.py"
    "x_twitter_growth_agent.py"
    "reddit_scout_agent.py"

    #=== FRAMEWORK/UTILITY NON-AGENTS ===
    "learning-agent.js"
    "llm_agent.py"
    "example_llm_agent.py"
    "scheduler.py"
    "stripe_check.py"
    "consolidated_agents.py"
)

# Directories to KILL (entire subdirectories)
KILL_DIRS=(
    "agriculture"
    "automotive"
    "civic"
    "construction"
    "education"
    "energy"
    "entertainment"
    "fitness"
    "food"
    "gardening"
    "government"
    "grant"
    "healthcare"
    "insurance"
    "legal"
    "manufacturing"
    "hospitality"
)

#==============================================================================
# Functions
#==============================================================================

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo "$msg"
    echo "$msg" >> "$LOG_FILE"
}

init_backup() {
    if [[ ! -d "$BACKUP_DIR" ]]; then
        mkdir -p "$BACKUP_DIR"
        log "Created backup directory: $BACKUP_DIR"
    fi
}

backup_and_remove() {
    local file="$1"
    local full_path="$AGENTS_DIR/$file"
    local backup_path="$BACKUP_DIR/$file"

    if [[ -f "$full_path" ]]; then
        # If backup already exists, add timestamp
        if [[ -f "$backup_path" ]]; then
            backup_path="${BACKUP_DIR}/${file}.$(date +%Y%m%d%H%M%S)"
        fi

        mv "$full_path" "$backup_path"
        log "MOVED: $file → $backup_path"
        echo "  ✅ $file → archived"
    else
        echo "  ⚠️  $file not found (already removed?)"
    fi
}

backup_dir_and_remove() {
    local dir="$1"
    local full_path="$AGENTS_DIR/$dir"
    local backup_path="$BACKUP_DIR/${dir}.$(date +%Y%m%d%H%M%S)"

    if [[ -d "$full_path" ]]; then
        mv "$full_path" "$backup_path"
        log "MOVED DIR: $dir/ → $backup_path/"
        echo "  ✅ $dir/ → archived/"
    else
        echo "  ⚠️  $dir/ not found (already removed?)"
    fi
}

dry_run() {
    log "=== DRY RUN MODE - No files will be deleted ==="
    echo ""
    echo "🗑️  KILL DAY - Dry Run"
    echo "======================"
    echo ""

    local count=0
    local dir_count=0

    echo "📄 FILES TO KILL (${#KILL_LIST[@]} files):"
    echo "-------------------------------------------"
    for agent in "${KILL_LIST[@]}"; do
        local full_path="$AGENTS_DIR/$agent"
        if [[ -f "$full_path" ]]; then
            echo "  🔴 $agent"
            count=$((count + 1))
        else
            echo "  ⚠️  $agent (not found)"
        fi
    done
    echo ""

    echo "📁 DIRECTORIES TO KILL (${#KILL_DIRS[@]} dirs):"
    echo "----------------------------------------------"
    for dir in "${KILL_DIRS[@]}"; do
        local full_path="$AGENTS_DIR/$dir"
        if [[ -d "$full_path" ]]; then
            echo "  🔴 $dir/"
        else
            echo "  ⚠️  $dir/ (not found)"
        fi
    done
    echo ""

    echo "=========================================="
    echo "Total files found: $count"
    echo "Total directories found: ${#KILL_DIRS[@]} (${#KILL_DIRS[@]} dirs)"
    echo ""
    echo "To execute: $0 --execute"
}

list_only() {
    echo "📄 FILES TO KILL (${#KILL_LIST[@]} files):"
    echo "-------------------------------------------"
    for agent in "${KILL_LIST[@]}"; do
        echo "  $agent"
    done
    echo ""

    echo "📁 DIRECTORIES TO KILL (${#KILL_DIRS[@]} dirs):"
    echo "----------------------------------------------"
    for dir in "${KILL_DIRS[@]}"; do
        echo "  $dir/"
    done
}

execute() {
    init_backup
    log "=== EXECUTE MODE - Starting deletion ==="

    echo ""
    echo "🗑️  KILL DAY - EXECUTE"
    echo "======================"
    echo ""
    echo "⚠️  WARNING: This will permanently remove agents!"
    echo ""
    echo "Files to delete: ${#KILL_LIST[@]}"
    echo "Directories to delete: ${#KILL_DIRS[@]}"
    echo "Backup location: $BACKUP_DIR"
    echo ""
    read -p "Type 'YES-DELETE' to confirm: " confirm

    if [[ "$confirm" != "YES-DELETE" ]]; then
        echo "❌ Aborted. No files were deleted."
        log "ABORTED by user"
        exit 0
    fi

    echo ""
    echo "🚀 Moving agents to archive..."
    echo ""

    local deleted=0
    local skipped=0

    # Backup and remove files
    for agent in "${KILL_LIST[@]}"; do
        if [[ -f "$AGENTS_DIR/$agent" ]]; then
            backup_and_remove "$agent"
            deleted=$((deleted + 1))
        else
            skipped=$((skipped + 1))
        fi
    done

    # Backup and remove directories
    for dir in "${KILL_DIRS[@]}"; do
        if [[ -d "$AGENTS_DIR/$dir" ]]; then
            backup_dir_and_remove "$dir"
            deleted=$((deleted + 1))
        else
            skipped=$((skipped + 1))
        fi
    done

    echo ""
    echo "=========================================="
    echo "✅ DONE! Deleted: $deleted, Skipped (not found): $skipped"
    echo "📦 Backup location: $BACKUP_DIR"
    echo ""
    log "COMPLETED. Deleted: $deleted, Skipped: $skipped"

    # Show remaining agents count
    local remaining
    remaining=$(find "$AGENTS_DIR" -maxdepth 1 -type f \( -name "*.py" -o -name "*.js" -o -name "*.md" \) | wc -l)
    echo "📊 Remaining agents in $AGENTS_DIR: $remaining"
}

#==============================================================================
# Main
#==============================================================================

mkdir -p "$(dirname "$LOG_FILE")"

case "${1:-}" in
    --dry-run|-d)
        dry_run
        ;;
    --list|-l)
        list_only
        ;;
    --execute|-e)
        execute
        ;;
    --help|-h)
        echo "Usage: $0 [OPTION]"
        echo ""
        echo "Options:"
        echo "  --dry-run, -d   Show what would be deleted (default)"
        echo "  --list, -l      List all agents that would be killed"
        echo "  --execute, -e   Actually delete (requires confirmation)"
        echo "  --help, -h      Show this help"
        echo ""
        echo "Examples:"
        echo "  $0 --dry-run    # Preview"
        echo "  $0 --execute    # Delete for real"
        ;;
    *)
        dry_run
        ;;
esac
