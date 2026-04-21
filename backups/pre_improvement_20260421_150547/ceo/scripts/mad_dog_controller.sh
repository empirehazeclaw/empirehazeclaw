#!/bin/bash
# Mad-Dog Evolver Controller
# Runs with BRIDGE OFF - but injects our signals via signal_bridge

EVOLVER_DIR="/home/clawbot/.openclaw/workspace/skills/capability-evolver"
PID_FILE="$EVOLVER_DIR/evolver.pid"
LOG_FILE="/home/clawbot/.openclaw/workspace/ceo/logs/mad_dog.log"

is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
            return 0  # running
        fi
    fi
    return 1  # not running
}

inject_signals() {
    # Translate our Learning Loop signals → Evolver signals and inject
    python3 /home/clawbot/.openclaw/workspace/ceo/scripts/signal_bridge.py --inject 2>/dev/null
}

start_mad_dog() {
    # Remove stale lock
    rm -f "$PID_FILE"
    
    echo "[$(date -Iseconds)] Starting mad-dog (BRIDGE OFF + signal injection)..." >> "$LOG_FILE"
    cd "$EVOLVER_DIR"
    export A2A_NODE_ID=node_39c27b8ba346
    export EVOLVE_STRATEGY=innovate
    export EVOLVE_BRIDGE=false  # BRIDGE OFF - use our injected signals instead
    export EVOLVE_VERBOSE=false
    
    # Start in background with setsid for proper daemonization
    setsid node index.js --mad-dog >> "$LOG_FILE" 2>&1 &
    
    # Wait briefly and check
    sleep 2
    
    if [ -f "$PID_FILE" ]; then
        NEW_PID=$(cat "$PID_FILE" 2>/dev/null)
        echo "[$(date -Iseconds)] Started with PID $NEW_PID (BRIDGE OFF + signal injection)" >> "$LOG_FILE"
    else
        echo "[$(date -Iseconds)] Started (BRIDGE OFF + signal injection)" >> "$LOG_FILE"
    fi
    
    # Inject signals after start
    sleep 2
    inject_signals
}

# Main
if is_running; then
    echo "[$(date -Iseconds)] Mad-dog running, injecting translated signals..." >> "$LOG_FILE"
    inject_signals
else
    echo "[$(date -Iseconds)] Mad-dog not running, starting..." >> "$LOG_FILE"
    start_mad_dog
fi