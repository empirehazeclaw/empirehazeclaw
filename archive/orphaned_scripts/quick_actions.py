#!/usr/bin/env python3
"""
Quick Actions - One-command shortcuts for complex flows
"""

import json
import os
from pathlib import Path

ACTIONS_FILE = "/home/clawbot/.openclaw/workspace/.quick_actions.json"

DEFAULT_ACTIONS = {
    "pod": {
        "description": "Print-on-Demand Research + Upload",
        "steps": [
            "python3 scripts/pod_research.py",
            "python3 scripts/printify_upload.py"
        ]
    },
    "backup": {
        "description": "Full system backup",
        "steps": [
            "bash scripts/nightly_bundle.sh"
        ]
    },
    "report": {
        "description": "Daily report generation",
        "steps": [
            "python3 scripts/daily_report.py"
        ]
    },
    "status": {
        "description": "System status overview",
        "steps": [
            "openclaw status",
            "python3 scripts/api_monitor.py"
        ]
    }
}

def list_actions():
    """Liste alle Quick Actions"""
    if os.path.exists(ACTIONS_FILE):
        with open(ACTIONS_FILE) as f:
            actions = json.load(f)
    else:
        actions = DEFAULT_ACTIONS
        save_actions(actions)
    
    print("⚡ Quick Actions:")
    for name, data in actions.items():
        print(f"  /{name}: {data['description']}")
    return actions

def save_actions(actions):
    """Speichere Actions"""
    os.makedirs(os.path.dirname(ACTIONS_FILE), exist_ok=True)
    with open(ACTIONS_FILE, "w") as f:
        json.dump(actions, f, indent=2)

def run_action(name):
    """Führe eine Quick Action aus"""
    actions = list_actions()
    
    if name not in actions:
        print(f"❌ Unknown action: {name}")
        return
    
    action = actions[name]
    print(f"⚡ Running: {name}")
    print(f"   {action['description']}")
    print(f"   Steps: {len(action['steps'])}")
    
    # Would execute steps here
    return action["steps"]

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        run_action(sys.argv[1])
    else:
        list_actions()
