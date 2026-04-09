#!/bin/bash
# Run all Codex Subagents during night

echo "=== 🌙 START: CODEX SUBAGENTS ===" $(date)

BASE=~/.codex/agents
LOG=logs/subagents_$(date +%Y%m%d).log

# Categories to process
CATEGORIES=(
    "01-core-development"
    "02-language-specialists"
    "03-infrastructure"
    "04-quality-security"
    "05-data-ai"
    "06-developer-experience"
    "07-specialized-domains"
    "08-business-product"
    "09-meta-orchestration"
    "10-research-analysis"
)

total=0
for cat in "${CATEGORIES[@]}"; do
    echo "Processing: $cat" | tee -a $LOG
    
    count=$(ls $BASE/$cat/*.toml 2>/dev/null | wc -l)
    echo "  Found: $count subagents"
    total=$((total + count))
    
    # Just document them - full execution would need sessions_spawn
    for agent in $BASE/$cat/*.toml; do
        name=$(basename $agent .toml)
        echo "  - $name" | tee -a $LOG
    done
done

echo "" | tee -a $LOG
echo "=== ✅ TOTAL: $total SUBAGENTS SCANNED ===" | tee -a $LOG

# Note: Actual execution via sessions_spawn would need individual runs
echo "Note: Use sessions_spawn for actual agent execution"
