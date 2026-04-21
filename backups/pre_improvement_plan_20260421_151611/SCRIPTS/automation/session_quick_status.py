#!/usr/bin/env python3
"""
🦞 Sir HazeClaw — Session Quick Status
Fast status check for session startup

Checks:
- Gateway status
- Active crons
- KG health
- Today's goals
- Last heartbeat

Usage:
    python3 session_quick_status.py
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
GOALS_FILE = WORKSPACE / "memory" / "goals.json"
HEARTBEAT_FILE = WORKSPACE / "memory" / "heartbeat-state.json"
KG_FILE = WORKSPACE / "memory" / "kg" / "knowledge_graph.json"

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except:
        return "ERROR"

def get_goals():
    if not GOALS_FILE.exists():
        return []
    goals = json.loads(GOALS_FILE.read_text())
    active = [g for g in goals if g.get("status") == "in_progress"]
    return active

def get_deadlines(goals):
    now = datetime.now(timezone.utc)
    urgent = []
    for g in goals:
        dl = g.get("deadline")
        if dl:
            try:
                dt = datetime.fromisoformat(dl).replace(tzinfo=timezone.utc)
                days = (dt - now).days
                if days <= 3:
                    urgent.append(f"⚠️ {g['title']}: {days}d")
            except:
                pass
    return urgent

def get_kg_health():
    if not KG_FILE.exists():
        return "KG: not found"
    try:
        kg = json.loads(KG_FILE.read_text())
        entities = len(kg.get("entities", {}))
        return f"KG: {entities} entities"
    except:
        return "KG: error"

def get_heartbeat():
    if not HEARTBEAT_FILE.exists():
        return "No heartbeat"
    try:
        state = json.loads(HEARTBEAT_FILE.read_text())
        ts = state.get("last_check", "unknown")
        return f"Heartbeat: {ts[:16]}"
    except:
        return "Heartbeat: error"

def main():
    print("🦞 Session Quick Status")
    print("=" * 40)
    
    # Gateway
    gateway = run_cmd("openclaw gateway status | grep -E 'running|down' | head -1")
    if "running" in gateway.lower():
        print("✅ Gateway: Running")
    else:
        print("⚠️ Gateway: Check needed")
    
    # Crons
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list"],
            capture_output=True, text=True, timeout=15
        )
        count = sum(1 for l in result.stdout.split("\n") if " ok " in l)
        print(f"📅 Active Crons: {count}")
    except:
        print("📅 Active Crons: ?")
    
    # KG
    print(f"   {get_kg_health()}")
    
    # Goals
    goals = get_goals()
    urgent = get_deadlines(goals)
    print(f"🎯 Active Goals: {len(goals)}")
    for u in urgent[:3]:
        print(f"   {u}")
    
    # Heartbeat
    print(f"   {get_heartbeat()}")
    
    print("=" * 40)

if __name__ == "__main__":
    main()