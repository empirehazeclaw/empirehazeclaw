#!/usr/bin/env python3
"""
🔍 AUTONOMOUS TASK SCANNER
==========================
Scans for new tasks and creates events automatically.
"""

import sys
import os
import json
import re
from datetime import datetime, timedelta

# Fix import path
sys.path.insert(0, '/home/clawbot/.openclaw/workspace/scripts')

# Try importing task manager
try:
    from task_manager_v4 import TaskManagerRedis
    HAS_REDIS = True
except:
    HAS_REDIS = False

SCAN_DIRS = [
    "/home/clawbot/.openclaw/workspace/TODO.md",
    "/home/clawbot/.openclaw/workspace/memory/",
    "/home/clawbot/.openclaw/workspace/projects/"
]

def scan_for_tasks():
    """Scan directories for tasks"""
    tasks = []
    
    # Scan TODO
    try:
        with open("/home/clawbot/.openclaw/workspace/TODO.md") as f:
            content = f.read()
            # Extract tasks (lines starting with - [ ] or - [x])
            for line in content.split('\n'):
                if '- [ ]' in line:
                    tasks.append({"text": line, "status": "open"})
                elif '- [x]' in line:
                    tasks.append({"text": line, "status": "done"})
    except:
        pass
    
    return tasks

def run():
    """Run scanner"""
    print("🔍 Task Scanner running...")
    tasks = scan_for_tasks()
    print(f"   Found {len(tasks)} tasks")
    
    # If Redis available, save to Redis
    if HAS_REDIS:
        try:
            tm = TaskManagerRedis()
            for task in tasks:
                tm.add_task(task["text"], priority=5)
            print("   ✅ Saved to Redis")
        except:
            print("   ⚠️ Redis not available")
    else:
        # Save to file
        with open("/tmp/task_scanner.json", "w") as f:
            json.dump(tasks, f)
        print("   ✅ Saved to file")

if __name__ == "__main__":
    run()
