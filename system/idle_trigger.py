#!/usr/bin/env python3
"""
Idle Trigger System — CEO Autonomous System
Läuft: Nach jedem Heartbeat-Check (alle 15min)
Erkennt: Idle Agents + weist Tasks zu
Output: Log + Discord Report wenn Task assigned
"""

import json
import os
from datetime import datetime

WORKSPACE = "/home/clawbot/.openclaw/workspace"
HEARTBEAT_DIR = f"{WORKSPACE}/system/heartbeats"
IDLE_QUEUE = f"{WORKSPACE}/shared/IDLE_QUEUE.md"
IDLE_LOG = f"{WORKSPACE}/system/heartbeats/idle_trigger.log"

# Agents die geprüft werden
AGENTS = ["security", "builder", "qc", "data", "research"]

# Threshold: idle wenn Heartbeat älter als X Minuten
IDLE_THRESHOLD_MINUTES = 30

def check_idle_agents():
    idle_agents = []
    
    for agent in AGENTS:
        heartbeat_file = f"{HEARTBEAT_DIR}/{agent}.json"
        
        if not os.path.exists(heartbeat_file):
            idle_agents.append({"agent": agent, "reason": "no_heartbeat_file"})
            continue
        
        mtime = os.path.getmtime(heartbeat_file)
        age_minutes = (datetime.utcnow().timestamp() - mtime) / 60
        
        if age_minutes > IDLE_THRESHOLD_MINUTES:
            idle_agents.append({
                "agent": agent,
                "idle_minutes": int(age_minutes),
                "reason": "heartbeat_stale"
            })
    
    return idle_agents

def get_pending_tasks():
    """Liest IDLE_QUEUE.md für ausstehende Tasks."""
    if not os.path.exists(IDLE_QUEUE):
        return []
    
    tasks = []
    with open(IDLE_QUEUE, "r") as f:
        content = f.read()
        # Parsing: Tasks sind in ### X. [type] sections
        lines = content.split("\n")
        current_task = None
        
        for line in lines:
            if line.startswith("### "):
                # New task
                parts = line.replace("### ", "").split(". ", 1)
                if len(parts) > 1:
                    task_type = parts[1].strip("[]")
                    current_task = {"type": task_type}
            elif current_task and "- **Action:**" in line:
                action = line.replace("- **Action:**", "").strip()
                current_task["action"] = action
                tasks.append(current_task)
                current_task = None
    
    return tasks

def assign_task(agent, task):
    """Weist einen Task an einen idle Agenten."""
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    log_entry = f"[{timestamp}] ASSIGNED: {agent} -> {task['type']}: {task['action']}\n"
    
    with open(IDLE_LOG, "a") as f:
        f.write(log_entry)
    
    return f"Task '{task['type']}' assigned to {agent}"

def run():
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # 1. Check für idle Agents
    idle_agents = check_idle_agents()
    
    # 2. Check für pending Tasks
    pending_tasks = get_pending_tasks()
    
    # 3. Wenn idle Agent + Tasks → assign
    assignments = []
    if idle_agents and pending_tasks:
        for idle in idle_agents[:len(pending_tasks)]:  # First-come-first-serve
            task = pending_tasks[len(assignments)]
            result = assign_task(idle["agent"], task)
            assignments.append({
                "agent": idle["agent"],
                "task": task,
                "result": result
            })
    
    # 4. Summary
    print(f"✅ Idle Trigger Run: {len(idle_agents)} idle, {len(pending_tasks)} tasks, {len(assignments)} assigned")
    
    return {
        "timestamp": timestamp,
        "idle_agents": idle_agents,
        "pending_tasks": len(pending_tasks),
        "assignments": assignments
    }

if __name__ == "__main__":
    run()