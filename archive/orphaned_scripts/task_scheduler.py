#!/usr/bin/env python3
"""
📅 TASK SCHEDULER
================
Schedules tasks for autonomous execution
"""

import json
import os
from datetime import datetime, timedelta

QUEUE_FILE = "data/task_queue.json"
SCHEDULE_FILE = "data/scheduled_tasks.json"

def add_task(task, agent=None, delay_minutes=0, schedule_time=None):
    """Add task to queue or schedule"""
    task_obj = {
        "id": f"task_{datetime.now().timestamp()}",
        "task": task,
        "agent": agent,
        "created_at": datetime.now().isoformat(),
        "status": "pending"
    }
    
    if schedule_time:
        # Add to scheduled
        with open(SCHEDULE_FILE, "r") as f:
            scheduled = json.load(f)
        task_obj["due"] = schedule_time
        scheduled.append(task_obj)
        with open(SCHEDULE_FILE, "w") as f:
            json.dump(scheduled, f, indent=2)
        return f"Scheduled: {task} at {schedule_time}"
    
    # Add to queue
    with open(QUEUE_FILE, "r") as f:
        queue = json.load(f)
    
    if delay_minutes > 0:
        task_obj["execute_after"] = (datetime.now() + timedelta(minutes=delay_minutes)).isoformat()
    
    queue["pending"].append(task_obj)
    
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=2)
    
    return f"Queued: {task}"

def get_next_task():
    """Get next task to execute"""
    with open(QUEUE_FILE, "r") as f:
        queue = json.load(f)
    
    now = datetime.now().isoformat()
    
    for task in queue["pending"]:
        execute_after = task.get("execute_after", now)
        if execute_after <= now:
            return task
    
    return None

def mark_complete(task_id):
    """Mark task as complete"""
    with open(QUEUE_FILE, "r") as f:
        queue = json.load(f)
    
    queue["pending"] = [t for t in queue["pending"] if t["id"] != task_id]
    queue["completed"].append({
        "id": task_id,
        "completed_at": datetime.now().isoformat()
    })
    
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=2)

# CLI
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 task_scheduler.py add <task> [--agent <agent>] [--delay <min>]")
        print("       python3 task_scheduler.py next")
        print("       python3 task_scheduler.py list")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "add":
        task = sys.argv[2] if len(sys.argv) > 2 else "Default task"
        agent = None
        delay = 0
        
        if "--agent" in sys.argv:
            agent = sys.argv[sys.argv.index("--agent") + 1]
        if "--delay" in sys.argv:
            delay = int(sys.argv[sys.argv.index("--delay") + 1])
        
        print(add_task(task, agent, delay))
    
    elif cmd == "next":
        task = get_next_task()
        print(json.dumps(task, indent=2) if task else "No tasks")
    
    elif cmd == "list":
        with open(QUEUE_FILE, "r") as f:
            print(f.read())
