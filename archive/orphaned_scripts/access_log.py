#!/usr/bin/env python3
"""
Access Log - Track who accesses what
"""

import os
import json
from datetime import datetime
from functools import wraps
import time

LOG_FILE = "/home/clawbot/.openclaw/logs/access.json"

def log_access(user, action, details=""):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "user": user,
        "action": action,
        "details": details
    }
    
    # Load existing
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            data = json.load(f)
    else:
        data = []
    
    # Add entry
    data.append(entry)
    
    # Keep last 1000
    data = data[-1000:]
    
    # Save
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_recent(limit=10):
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            data = json.load(f)
        return data[-limit:]
    return []

if __name__ == "__main__":
    print("📊 Letzte Zugriffe:")
    for entry in get_recent(5):
        print(f"{entry['timestamp'][:19]} | {entry['user']} | {entry['action']}")
