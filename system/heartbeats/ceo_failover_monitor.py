#!/usr/bin/env python3
"""
CEO Failover Monitor
Checks CEO heartbeat and triggers failover if CEO is down.
"""

import os
import json
import sys
from datetime import datetime, timedelta

HEARTBEAT_DIR = "/home/clawbot/.openclaw/workspace/system/heartbeats"
FAILOVER_STATE = "/home/clawbot/.openclaw/workspace/system/heartbeats/failover_state.json"
MISSED_THRESHOLD = 3  # 3 missed heartbeats = failover

# Backup chain: CEO → Security → Builder → Data Manager
BACKUP_CHAIN = [
    "security_officer",
    "builder", 
    "data_manager"
]

def get_heartbeat(agent_id: str) -> dict:
    """Get heartbeat data for an agent."""
    filepath = os.path.join(HEARTBEAT_DIR, f"{agent_id}.json")
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return None

def get_last_heartbeat_age(agent_id: str) -> float:
    """Get age of last heartbeat in minutes."""
    heartbeat = get_heartbeat(agent_id)
    if not heartbeat or "last_heartbeat" not in heartbeat:
        return float('inf')
    
    last = datetime.fromisoformat(heartbeat["last_heartbeat"])
    age = (datetime.utcnow() - last).total_seconds() / 60
    return age

def check_ceo_status() -> dict:
    """Check CEO heartbeat status."""
    ceo_age = get_last_heartbeat_age("ceo")
    
    return {
        "ceo_alive": ceo_age < 20,  # CEO should heartbeat every 15min
        "ceo_age_minutes": ceo_age,
        "missed_beats": int(ceo_age / 15) if ceo_age != float('inf') else 999
    }

def get_current_backup() -> str:
    """Get current backup agent based on missed heartbeats."""
    state = load_failover_state()
    missed = state.get("missed_beats", 0)
    
    if missed < MISSED_THRESHOLD:
        return None
    
    # Map missed beats to backup chain index
    backup_idx = min(missed - MISSED_THRESHOLD, len(BACKUP_CHAIN) - 1)
    return BACKUP_CHAIN[backup_idx]

def load_failover_state() -> dict:
    """Load failover state."""
    if os.path.exists(FAILOVER_STATE):
        with open(FAILOVER_STATE, 'r') as f:
            return json.load(f)
    return {"missed_beats": 0, "backup_active": None, "last_check": None}

def save_failover_state(state: dict):
    """Save failover state."""
    state["last_check"] = datetime.utcnow().isoformat()
    with open(FAILOVER_STATE, 'w') as f:
        json.dump(state, f, indent=2)

def trigger_failover(backup_agent: str):
    """Trigger failover to backup agent."""
    state = load_failover_state()
    
    if state.get("backup_active") == backup_agent:
        print(f"Backup {backup_agent} already active, skipping")
        return
    
    state["backup_active"] = backup_agent
    state["failover_time"] = datetime.utcnow().isoformat()
    save_failover_state(state)
    
    print(f"🚨 FAILOVER TRIGGERED: {backup_agent} now acting CEO")
    print(f"   Failed over at: {state['failover_time']}")

def clear_failover():
    """Clear failover state when CEO recovers."""
    state = load_failover_state()
    
    if state.get("backup_active"):
        print(f"✅ CEO RECOVERED: {state['backup_active']} released acting CEO duties")
    
    state["missed_beats"] = 0
    state["backup_active"] = None
    state["recovery_time"] = datetime.utcnow().isoformat()
    save_failover_state(state)

def run_monitor():
    """Main monitoring loop."""
    status = check_ceo_status()
    state = load_failover_state()
    
    if status["ceo_alive"]:
        # CEO is alive
        if state.get("backup_active"):
            # CEO recovered while backup was active
            clear_failover()
        else:
            # Reset missed beats if CEO is responding
            state["missed_beats"] = 0
            save_failover_state(state)
            print("✓ CEO heartbeat OK")
    else:
        # CEO might be down
        missed = int(status["ceo_age_minutes"] / 15) + 1 if status["ceo_age_minutes"] != float('inf') else 999
        state["missed_beats"] = missed
        save_failover_state(state)
        
        print(f"⚠️ CEO heartbeat missed ({missed} beats)")
        
        if missed >= MISSED_THRESHOLD:
            backup = get_current_backup()
            if backup:
                trigger_failover(backup)

if __name__ == "__main__":
    run_monitor()