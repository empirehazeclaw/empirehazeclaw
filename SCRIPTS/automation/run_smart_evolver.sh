#!/bin/bash
# run_smart_evolver.sh — CEO Phase 4
# Runs Capability Evolver with fresh signals from Event Bus + KG

echo "=== CEO SMART EVOLVER RUN ==="
echo "Timestamp: $(date -Iseconds)"
echo ""

# Step 1: Analyze current system state
echo "[1/4] Analyzing system state..."
python3 /home/clawbot/.openclaw/workspace/SCRIPTS/automation/evolver_signal_bridge.py --check-stagnation > /tmp/evolver_analysis.json
cat /tmp/evolver_analysis.json

# Extract signals
SIGNALS=$(python3 -c "import json; d=json.load(open('/tmp/evolver_analysis.json')); print(','.join(d.get('signals', [])))")
echo ""
echo "Signals: $SIGNALS"

# Step 2: Check if stagnation - if so, force repair strategy
STAGNANT=$(python3 -c "import json; d=json.load(open('/tmp/evolver_analysis.json')); print('yes' if len(d.get('signals', [])) > 0 else 'no')")

if [ "$STAGNANT" = "yes" ] && [[ "$SIGNALS" == *"stagnation"* ]]; then
    echo ""
    echo "[BREAK] Stagnation detected! Forcing repair strategy..."
    export EVOLVE_STRATEGY="repair"
else
    echo ""
    echo "[OK] Running with innovate strategy..."
    export EVOLVE_STRATEGY="innovate"
fi

# Step 3: Run the actual Evolver
cd /home/clawbot/.openclaw/workspace/skills/capability-evolver
export A2A_NODE_ID=node_39c27b8ba346

echo ""
echo "[2/4] Running Capability Evolver (strategy: $EVOLVE_STRATEGY)..."
node index.js 2>&1 | tail -30

# Step 4: Post results to Event Bus
echo ""
echo "[3/4] Posting results to Event Bus..."
python3 /home/clawbot/.openclaw/workspace/SCRIPTS/automation/evolver_signal_bridge.py --post-evolver-results 2>&1

# Step 5: Run stagnation breaker to ensure diversity
echo ""
echo "[4/4] Running stagnation breaker check..."
python3 /home/clawbot/.openclaw/workspace/SCRIPTS/automation/evolver_stagnation_breaker.py --check 2>&1

echo ""
echo "=== EVOLVER RUN COMPLETE ==="
