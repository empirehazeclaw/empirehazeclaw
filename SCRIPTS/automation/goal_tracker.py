#!/usr/bin/env python3
"""
🦞 Sir HazeClaw — Goal Tracker
Phase 3: Intention Engine — Core Component

Tracks goals with deadlines, milestones, and priorities.

Usage:
    python3 goal_tracker.py list
    python3 goal_tracker.py add "Title" --deadline 2026-04-20 --priority HIGH
    python3 goal_tracker.py update <goal_id> --done
    python3 goal_tracker.py next
"""

import os
import sys
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
GOALS_FILE = WORKSPACE / "memory" / "goals.json"
LOG_FILE = WORKSPACE.parent / "logs" / "goal_tracker.log"

def log(msg: str, level: str = "INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_goals() -> List[Dict]:
    if not GOALS_FILE.exists():
        return []
    try:
        with open(GOALS_FILE) as f:
            return json.load(f)
    except:
        return []

def save_goals(goals: List[Dict]):
    with open(GOALS_FILE, "w") as f:
        json.dump(goals, f, indent=2)

def create_goal_id() -> str:
    goals = load_goals()
    max_id = 0
    for g in goals:
        if g.get("id", "").startswith("goal_"):
            try:
                num = int(g["id"].split("_")[1])
                max_id = max(max_id, num)
            except:
                pass
    return f"goal_{max_id + 1:03d}"

def add_goal(title: str, deadline: Optional[str] = None, priority: str = "MEDIUM", context: str = "") -> str:
    goals = load_goals()
    
    goal = {
        "id": create_goal_id(),
        "title": title,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "deadline": deadline,
        "priority": priority,
        "status": "in_progress",
        "context": context,
        "milestones": [],
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    goals.append(goal)
    save_goals(goals)
    log(f"Added goal: {title} ({goal['id']})")
    return goal["id"]

def list_goals(status: Optional[str] = None) -> List[Dict]:
    goals = load_goals()
    if status:
        goals = [g for g in goals if g.get("status") == status]
    # Sort by deadline
    goals.sort(key=lambda g: g.get("deadline", "9999-12-31"))
    return goals

def get_next_goal() -> Optional[Dict]:
    """Get the most urgent goal based on deadline and priority."""
    goals = [g for g in load_goals() if g.get("status") == "in_progress"]
    if not goals:
        return None
    
    # Sort by priority then deadline
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    goals.sort(key=lambda g: (
        priority_order.get(g.get("priority", "MEDIUM"), 2),
        g.get("deadline", "9999-12-31")
    ))
    
    # Calculate days_left for display
    now = datetime.now(timezone.utc)
    for g in goals:
        deadline = g.get("deadline")
        if deadline:
            try:
                dt = datetime.fromisoformat(deadline).replace(tzinfo=timezone.utc)
                g["days_left"] = (dt - now).days
            except:
                g["days_left"] = "?"
        else:
            g["days_left"] = "?"
    
    return goals[0]

def update_goal(goal_id: str, **kwargs) -> bool:
    goals = load_goals()
    for g in goals:
        if g["id"] == goal_id:
            for key, value in kwargs.items():
                if key in ["title", "deadline", "priority", "status", "context"]:
                    g[key] = value
            g["updated_at"] = datetime.now(timezone.utc).isoformat()
            save_goals(goals)
            log(f"Updated goal {goal_id}: {kwargs}")
            return True
    return False

def add_milestone(goal_id: str, text: str) -> bool:
    goals = load_goals()
    for g in goals:
        if g["id"] == goal_id:
            g.setdefault("milestones", []).append({"text": text, "done": False})
            g["updated_at"] = datetime.now(timezone.utc).isoformat()
            save_goals(goals)
            return True
    return False

def mark_milestone(goal_id: str, milestone_text: str, done: bool = True) -> bool:
    goals = load_goals()
    for g in goals:
        if g["id"] == goal_id:
            for m in g.get("milestones", []):
                if m["text"] == milestone_text:
                    m["done"] = done
                    g["updated_at"] = datetime.now(timezone.utc).isoformat()
                    save_goals(goals)
                    return True
    return False

def get_upcoming(limit: int = 3) -> List[Dict]:
    """Get upcoming goals sorted by urgency."""
    goals = [g for g in load_goals() if g.get("status") == "in_progress"]
    
    # Calculate urgency score
    now = datetime.now(timezone.utc)
    for g in goals:
        deadline = g.get("deadline")
        if deadline:
            try:
                dt = datetime.fromisoformat(deadline).replace(tzinfo=timezone.utc)
                days_left = (dt - now).days
                g["days_left"] = days_left
                # Urgency score: negative = overdue
                priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
                g["urgency"] = days_left + priority_order.get(g.get("priority", "MEDIUM"), 2)
            except:
                g["days_left"] = 999
                g["urgency"] = 999
        else:
            g["days_left"] = 999
            g["urgency"] = 999
    
    goals.sort(key=lambda g: g.get("urgency", 999))
    return goals[:limit]

def format_goal(g: Dict) -> str:
    deadline = g.get("deadline", "No deadline")
    days_left = g.get("days_left", "?")
    priority = g.get("priority", "MEDIUM")
    
    emoji = "🔴" if priority == "CRITICAL" else "🟠" if priority == "HIGH" else "🟡" if priority == "MEDIUM" else "🟢"
    
    status_icon = "✅" if g.get("status") == "completed" else "🔄" if g.get("status") == "in_progress" else "⏸️"
    
    return f"{emoji} {status_icon} **{g['title']}** ({g['id']})\n   Deadline: {deadline} ({days_left} days)\n   Priority: {priority}"

def show_status():
    goals = load_goals()
    active = [g for g in goals if g.get("status") == "in_progress"]
    completed = [g for g in goals if g.get("status") == "completed"]
    
    print(f"\n📊 GOAL STATUS")
    print(f"   Active: {len(active)}")
    print(f"   Completed: {len(completed)}")
    
    if active:
        print(f"\n📋 UPCOMING ({len(active)} goals):")
        for g in get_upcoming(5):
            print(format_goal(g))
            print()

def main():
    if len(sys.argv) < 2:
        show_status()
        return
    
    cmd = sys.argv[1]
    
    if cmd == "list":
        for g in list_goals():
            print(format_goal(g))
            print()

    elif cmd == "status":
        show_status()
    
    elif cmd == "add":
        title = sys.argv[2] if len(sys.argv) > 2 else "Untitled Goal"
        deadline = None
        priority = "MEDIUM"
        context = ""
        
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--deadline" and i+1 < len(sys.argv):
                deadline = sys.argv[i+1]
                i += 2
            elif sys.argv[i] == "--priority" and i+1 < len(sys.argv):
                priority = sys.argv[i+1]
                i += 2
            elif sys.argv[i] == "--context" and i+1 < len(sys.argv):
                context = sys.argv[i+1]
                i += 2
            else:
                i += 1
        
        goal_id = add_goal(title, deadline, priority, context)
        print(f"✅ Created goal: {goal_id}")
    
    elif cmd == "update":
        if len(sys.argv) < 3:
            print("Usage: update <goal_id> [--done] [--status STATUS]")
            return
        
        goal_id = sys.argv[2]
        kwargs = {}
        
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--done":
                kwargs["status"] = "completed"
                i += 1
            elif sys.argv[i] == "--status" and i+1 < len(sys.argv):
                kwargs["status"] = sys.argv[i+1]
                i += 2
            elif sys.argv[i] == "--priority" and i+1 < len(sys.argv):
                kwargs["priority"] = sys.argv[i+1]
                i += 2
            else:
                i += 1
        
        if update_goal(goal_id, **kwargs):
            print(f"✅ Updated {goal_id}")
        else:
            print(f"❌ Goal {goal_id} not found")
    
    elif cmd == "next":
        g = get_next_goal()
        if g:
            print("🎯 NEXT PRIORITY:")
            print(format_goal(g))
        else:
            print("✅ No active goals!")
    
    elif cmd == "milestone":
        if len(sys.argv) < 4:
            print("Usage: milestone <goal_id> <text> [--done]")
            return
        
        goal_id = sys.argv[2]
        text = sys.argv[3]
        
        if "--done" in sys.argv:
            mark_milestone(goal_id, text, True)
            print(f"✅ Milestone done: {text}")
        else:
            add_milestone(goal_id, text)
            print(f"✅ Added milestone: {text}")
    
    elif cmd == "upcoming":
        for g in get_upcoming(5):
            print(format_goal(g))
            print()
    
    else:
        print(f"Unknown command: {cmd}")
        print("Available: list, add, update, next, milestone, upcoming, status")

if __name__ == "__main__":
    main()