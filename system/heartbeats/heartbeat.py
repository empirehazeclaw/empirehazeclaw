#!/usr/bin/env python3
"""
Agent Heartbeat Script
Creates/updates heartbeat files for monitoring agent liveness.
"""

import os
import json
import sys
from datetime import datetime

HEARTBEAT_DIR = "/home/clawbot/.openclaw/workspace/system/heartbeats"

def update_heartbeat(agent_id: str, status: str = "alive", details: dict = None):
    """Update heartbeat file for an agent."""
    filepath = os.path.join(HEARTBEAT_DIR, f"{agent_id}.json")
    
    data = {
        "agent_id": agent_id,
        "status": status,
        "last_heartbeat": datetime.utcnow().isoformat(),
        "details": details or {}
    }
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✓ Heartbeat updated for {agent_id}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: heartbeat.py <agent_id> [status]")
        sys.exit(1)
    
    agent_id = sys.argv[1]
    status = sys.argv[2] if len(sys.argv) > 2 else "alive"
    
    update_heartbeat(agent_id, status)