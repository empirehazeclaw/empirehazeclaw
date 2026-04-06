#!/bin/bash
# Capability Evolver - Auto Mode (Mad Dog Mode)

cd /home/clawbot/.openclaw/workspace/skills/capability-evolver

# Load environment
source .env

# Export
export A2A_NODE_ID
export A2A_HUB_URL
export GITHUB_TOKEN
export EVOLVE_STRATEGY
export EVOLVE_ALLOW_SELF_MODIFY
export EVOLVE_LOAD_MAX
export EVOLVER_ROLLBACK_MODE

# Check critical security setting
if [ "$EVOLVE_ALLOW_SELF_MODIFY" != "false" ]; then
    echo "⚠️ SECURITY WARNING: EVOLVE_ALLOW_SELF_MODIFY is not false!"
    echo "Exiting for safety."
    exit 1
fi

echo "🧬 Starting in AUTO mode..."
echo "   Strategy: $EVOLVE_STRATEGY"
echo "   Self-Modify: $EVOLVE_ALLOW_SELF_MODIFY"

# Run in auto mode (no --review flag)
node index.js
