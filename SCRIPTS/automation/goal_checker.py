#!/usr/bin/env python3
"""
🦞 Sir HazeClaw — Goal Checker Skill
Proaktiv checkt Goals und warnt bei Deadlines

Usage:
    python3 goal_checker.py              # Check all goals
    python3 goal_checker.py --urgent    # Only urgent warnings
    python3 goal_checker.py --report    # Full report for Nico
"""

import os
import sys
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
GOALS_FILE = WORKSPACE / "memory" / "goals.json"
LOG_FILE = WORKSPACE.parent / "logs" / "goal_checker.log"

def log(msg: str, level: str = "INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] [{level}] {msg}\n")

def load_goals():
    if not GOALS_FILE.exists():
        return []
    with open(GOALS_FILE) as f:
        return json.load(f)

def get_urgency(goal: dict) -> tuple:
    """Returns (urgency_level, message, days_left)"""
    deadline = goal.get("deadline")
    if not deadline:
        return (None, None, None)
    
    try:
        dl = datetime.fromisoformat(deadline).replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        days = (dl - now).days
        hours = (dl - now).total_seconds() / 3600
        
        priority = goal.get("priority", "MEDIUM")
        
        if days < 0:
            return ("OVERDUE", f"⚠️ OVERDUE by {abs(days)} days!", days)
        if days == 0:
            return ("TODAY", f"🔴 Deadline TODAY ({hours:.0f}h left)", days)
        if days == 1:
            return ("TOMORROW", f"🟠 Deadline TOMORROW", days)
        if days == 2:
            return ("SOON", f"🟡 Deadline in {days} days", days)
        if days <= 3:
            return ("WARNING", f"⚡ Deadline in {days} days", days)
        if priority == "HIGH":
            return ("INFO", f"🔵 High priority, {days} days", days)
        return (None, None, days)
    except:
        return (None, None, None)

def check_goals():
    goals = load_goals()
    active = [g for g in goals if g.get("status") == "in_progress"]
    
    urgent = []
    info = []
    
    for g in active:
        urgency, message, days = get_urgency(g)
        if urgency in ["OVERDUE", "TODAY", "TOMORROW", "SOON", "WARNING"]:
            pending = [m["text"] for m in g.get("milestones", []) if not m.get("done")]
            urgent.append({
                "title": g["title"],
                "id": g["id"],
                "urgency": urgency,
                "message": message,
                "days": days,
                "pending": pending[:2]
            })
        elif urgency == "INFO":
            info.append({
                "title": g["title"],
                "id": g["id"],
                "message": message,
                "days": days
            })
    
    return urgent, info

def main():
    mode = "check"
    if "--urgent" in sys.argv:
        mode = "urgent"
    elif "--report" in sys.argv:
        mode = "report"
    
    urgent, info = check_goals()
    
    if mode == "urgent":
        if urgent:
            print(f"🚨 {len(urgent)} urgent goal(s):")
            for g in urgent:
                print(f"   {g['message']} - {g['title']}")
        else:
            print("✅ No urgent goals")
        return 0
    
    if mode == "report":
        print("🎯 Goal Status Report")
        print("=" * 50)
        if urgent:
            print(f"\n🚨 URGENT ({len(urgent)}):")
            for g in urgent:
                print(f"   {g['message']}")
                print(f"   → {g['title']}")
                if g.get("pending"):
                    print(f"     Next: {g['pending'][0]}")
        if info:
            print(f"\n📋 Other High-Priority ({len(info)}):")
            for g in info:
                print(f"   {g['message']} - {g['title']}")
        if not urgent and not info:
            print("✅ All goals on track!")
        print("=" * 50)
        return 0
    
    # Default: check + log
    log(f"Goal Check: {len(urgent)} urgent, {len(info)} info")
    
    if urgent:
        print(f"🚨 {len(urgent)} goal(s) need attention:")
        for g in urgent[:3]:
            print(f"   {g['urgency']}: {g['title']} ({g['message']})")
    
    return 0 if not urgent else 1

if __name__ == "__main__":
    sys.exit(main())