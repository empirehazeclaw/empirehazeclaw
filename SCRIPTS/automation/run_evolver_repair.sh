#!/bin/bash
# run_evolver_repair.sh — CEO Capability Evolver with REPAIR strategy

echo "=== CEO CAPABILITY EVOLVER — REPAIR STRATEGY ==="
echo "Timestamp: $(date -Iseconds)"
echo ""

cd /home/clawbot/.openclaw/workspace/skills/capability-evolver
export A2A_NODE_ID=node_39c27b8ba346
export EVOLVE_STRATEGY=repair

echo "[1/3] Running Capability Evolver with REPAIR strategy..."
node index.js 2>&1 | tail -50

echo ""
echo "[2/3] Solidifying patches..."
node index.js solidify 2>&1 | tail -20

echo ""
echo "[3/3] Posting results to Event Bus..."
python3 /home/clawbot/.openclaw/workspace/scripts/evolver_signal_bridge.py --post-evolver-results 2>&1

echo ""
echo "=== REPAIR STRATEGY COMPLETE ==="