#!/usr/bin/env python3
"""
Task Delegation Tracker - Auto-Tracking für alle Anfragen
"""

import json
import os
from datetime import datetime
from pathlib import Path

TRACKER_FILE = "/home/clawbot/.openclaw/workspace/data/delegation_tracker.json"

def init_tracker():
    """Initialize tracker file"""
    Path(TRACKER_FILE).parent.mkdir(parents=True, exist_ok=True)
    if not os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, 'w') as f:
            json.dump({"tasks": [], "agents": {}, "delegations": []}, f)

def log_task(user_id: str, task: str, agent: str, result: str = ""):
    """Log a task delegation"""
    init_tracker()
    with open(TRACKER_FILE, 'r') as f:
        data = json.load(f)
    
    task_entry = {
        "id": len(data["tasks"]) + 1,
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "task": task[:100],
        "agent": agent,
        "status": "completed" if result else "processing",
        "result": result[:200] if result else ""
    }
    
    data["tasks"].append(task_entry)
    
    # Update agent stats
    if agent not in data["agents"]:
        data["agents"][agent] = {"tasks": 0, "last_active": ""}
    data["agents"][agent]["tasks"] += 1
    data["agents"][agent]["last_active"] = datetime.now().isoformat()
    
    # Log delegation
    data["delegations"].append({
        "from": "Main Agent",
        "to": agent,
        "task": task[:50],
        "time": datetime.now().isoformat()
    })
    
    # Keep only last 50 delegations
    data["delegations"] = data["delegations"][-50:]
    data["tasks"] = data["tasks"][-100:]
    
    with open(TRACKER_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    return task_entry

def get_delegations():
    """Get recent delegations"""
    init_tracker()
    with open(TRACKER_FILE, 'r') as f:
        data = json.load(f)
    return data.get("delegations", [])[-10:]

def get_agent_stats():
    """Get agent statistics"""
    init_tracker()
    with open(TRACKER_FILE, 'r') as f:
        data = json.load(f)
    return data.get("agents", {})

def get_tasks():
    """Get all tasks"""
    init_tracker()
    with open(TRACKER_FILE, 'r') as f:
        data = json.load(f)
    return data.get("tasks", [])[-20:]

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "log":
            # log <user_id> <task> <agent>
            user_id = sys.argv[2] if len(sys.argv) > 2 else "telegram"
            task = sys.argv[3] if len(sys.argv) > 3 else "Unknown"
            agent = sys.argv[4] if len(sys.argv) > 4 else "main"
            log_task(user_id, task, agent)
            print(f"✅ Logged: {agent}")
        elif sys.argv[1] == "delegations":
            print(json.dumps(get_delegations(), indent=2))
        elif sys.argv[1] == "stats":
            print(json.dumps(get_agent_stats(), indent=2))
        elif sys.argv[1] == "tasks":
            print(json.dumps(get_tasks(), indent=2))
    else:
        print("Usage: delegation_tracker.py [log|delegations|stats|tasks]")
