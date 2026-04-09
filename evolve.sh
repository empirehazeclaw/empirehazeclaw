#!/bin/bash
# Capability Evolver - Wrapper Script

cd /home/clawbot/.openclaw/workspace/skills/capability-evolver

# Load environment
source .env

# Export variables
export A2A_NODE_ID
export A2A_HUB_URL
export GITHUB_TOKEN
export EVOLVE_STRATEGY
export EVOLVE_ALLOW_SELF_MODIFY
export EVOLVE_LOAD_MAX
export EVOLVER_ROLLBACK_MODE
export EVOLVER_LLM_REVIEW
export EVOLVER_AUTO_ISSUE

# Check critical setting
if [ "$EVOLVE_ALLOW_SELF_MODIFY" != "false" ]; then
    echo "⚠️ WARNING: EVOLVE_ALLOW_SELF_MODIFY is not set to false!"
    echo "This is dangerous! Set EVOLVE_ALLOW_SELF_MODIFY=false"
    exit 1
fi

# Run mode
MODE=${1:-"--review"}

echo "🧬 Starting Capability Evolver..."
echo "   Mode: $MODE"
echo "   Strategy: $EVOLVE_STRATEGY"
echo "   Self-Modify: $EVOLVE_ALLOW_SELF_MODIFY"

node index.js $MODE
