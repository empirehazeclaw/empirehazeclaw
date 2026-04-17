#!/usr/bin/env python3
"""
🦞 Sir HazeClaw — Goal Alert System
Phase 4: Intention Engine — Alert Component

Alerts when:
- Deadline is within 48h
- Goal is overdue
- Milestone completion

Usage:
    python3 goal_alerts.py check
    python3 goal_alerts.py --urgent
"""

import os
import sys
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
GOALS_FILE = WORKSPACE / "memory" / "goals.json"
LAST_ALERT_FILE = WORKSPACE / "memory" / "goal_alerts_state.json"
LOG_FILE = WORKSPACE.parent / "logs" / "goal_alerts.log"

def log(msg: str, level: str = "INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_goals():
    if not GOALS_FILE.exists():
        return []
    try:
        with open(GOALS_FILE) as f:
            return json.load(f)
    except:
        return []

def load_alert_state():
    if not LAST_ALERT_FILE.exists():
        return {}
    try:
        with open(LAST_ALERT_FILE) as f:
            return json.load(f)
    except:
        return {}

def save_alert_state(state):
    with open(LAST_ALERT_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_urgency(goal: dict) -> tuple:
    """Returns (urgency_level, message)"""
    deadline = goal.get("deadline")
    if not deadline:
        return (None, None)
    
    try:
        deadline_dt = datetime.fromisoformat(deadline).replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        days_left = (deadline_dt - now).days
        hours_left = (deadline_dt - now).total_seconds() / 3600
        
        if days_left < 0:
            return ("OVERDUE", f"OVERDUE by {abs(days_left)} days!")
        
        if days_left == 0:
            if hours_left < 0:
                return ("OVERDUE", "OVERDUE (today)")
            return ("TODAY", f"Deadline today! ({hours_left:.0f}h left)")
        
        if days_left == 1:
            return ("TOMORROW", f"Deadline tomorrow ({hours_left:.0f}h left)")
        
        if days_left <= 2:
            return ("SOON", f"Deadline in {days_left} days")
        
        if days_left <= 7:
            return ("WEEK", f"Deadline in {days_left} days")
        
        return (None, None)
    
    except:
        return (None, None)

def check_goals():
    """Check all goals and return alerts."""
    goals = load_goals()
    alerts = []
    
    for g in goals:
        if g.get("status") == "completed":
            continue
        
        urgency, message = get_urgency(g)
        if not urgency:
            continue
        
        # Check if we already alerted recently
        last_alert = load_alert_state()
        last_time = last_alert.get(g["id"], {}).get(urgency)
        
        if last_time:
            try:
                last_dt = datetime.fromisoformat(last_time)
                hours_since = (datetime.now(timezone.utc) - last_dt).total_seconds() / 3600
                
                # Don't repeat alerts within 24h (for WEEK) or 6h (for others)
                min_interval = 6 if urgency in ["OVERDUE", "TODAY", "TOMORROW"] else 24
                if hours_since < min_interval:
                    continue
            except:
                pass
        
        alerts.append({
            "goal_id": g["id"],
            "title": g["title"],
            "urgency": urgency,
            "message": message,
            "priority": g.get("priority", "MEDIUM"),
            "milestones": g.get("milestones", [])
        })
        
        # Update alert state
        state = load_alert_state()
        if g["id"] not in state:
            state[g["id"]] = {}
        state[g["id"]][urgency] = datetime.now(timezone.utc).isoformat()
        save_alert_state(state)
    
    return alerts

def format_alert(a: dict) -> str:
    emoji = "🚨" if a["urgency"] == "OVERDUE" else "⚠️" if a["urgency"] in ["TODAY", "TOMORROW"] else "📅"
    priority_emoji = "🔴" if a["priority"] == "CRITICAL" else "🟠" if a["priority"] == "HIGH" else "🟡"
    
    lines = [
        f"{emoji} {priority_emoji} **{a['title']}**",
        f"   {a['message']}"
    ]
    
    pending = [m["text"] for m in a.get("milestones", []) if not m.get("done")]
    if pending:
        lines.append(f"   Next: {pending[0]}")
    
    return "\n".join(lines)

def main():
    mode = "check"
    if "--urgent" in sys.argv:
        mode = "urgent"
    
    alerts = check_goals()
    
    if not alerts:
        print("✅ No urgent alerts")
        return
    
    # Sort: OVERDUE > TODAY > TOMORROW > SOON > WEEK
    order = {"OVERDUE": 0, "TODAY": 1, "TOMORROW": 2, "SOON": 3, "WEEK": 4}
    alerts.sort(key=lambda a: order.get(a["urgency"], 5))
    
    if mode == "urgent":
        # Only show the most urgent
        a = alerts[0]
        print(format_alert(a))
    else:
        print(f"🚨 {len(alerts)} Alert(s):")
        for a in alerts:
            print(format_alert(a))
            print()

if __name__ == "__main__":
    main()