#!/usr/bin/env python3
"""
🦞 Sir HazeClaw — Intention Planner
Phase 3: Intention Engine — Context Provider

Provides "What's Next" context for each session.
Integrates with AGENTS.md startup sequence.

Usage:
    python3 intention_planner.py next
    python3 intention_planner.py context
    python3 intention_planner.py inject
"""

import os
import sys
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
GOALS_FILE = WORKSPACE / "memory" / "goals.json"
LOG_FILE = WORKSPACE.parent / "logs" / "intention_planner.log"

def load_goals():
    if not GOALS_FILE.exists():
        return []
    try:
        with open(GOALS_FILE) as f:
            return json.load(f)
    except:
        return []

def get_next_action() -> str:
    """Get the most urgent next action."""
    goals = [g for g in load_goals() if g.get("status") == "in_progress"]
    if not goals:
        return "No active goals. System running normally."
    
    # Sort by priority then deadline
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    goals.sort(key=lambda g: (
        priority_order.get(g.get("priority", "MEDIUM"), 2),
        g.get("deadline", "9999-12-31")
    ))
    
    top = goals[0]
    deadline = top.get("deadline", "No deadline")
    
    # Check milestones
    pending_milestones = [m for m in top.get("milestones", []) if not m.get("done")]
    
    if pending_milestones:
        next_milestone = pending_milestones[0]["text"]
        return f"🎯 **{top['title']}**: {next_milestone}\n   Deadline: {deadline}"
    
    return f"🎯 **{top['title']}** — {top.get('context', '')}\n   Deadline: {deadline}"

def get_context_block() -> str:
    """Get context block for session injection."""
    goals = [g for g in load_goals() if g.get("status") == "in_progress"]
    if not goals:
        return ""
    
    # Only top 3 goals
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    goals.sort(key=lambda g: (
        priority_order.get(g.get("priority", "MEDIUM"), 2),
        g.get("deadline", "9999-12-31")
    ))
    
    lines = ["## 🎯 Active Goals"]
    for g in goals[:3]:
        deadline = g.get("deadline", "No deadline")
        priority = g.get("priority", "MEDIUM")
        emoji = "🔴" if priority == "CRITICAL" else "🟠" if priority == "HIGH" else "🟡"
        
        lines.append(f"{emoji} **{g['title']}**")
        lines.append(f"   Deadline: {deadline}")
        
        pending = [m["text"] for m in g.get("milestones", []) if not m.get("done")]
        if pending:
            lines.append(f"   Next: {pending[0]}")
    
    return "\n".join(lines)

def get_upcoming_deadlines() -> list:
    """Get upcoming deadlines within 7 days."""
    goals = [g for g in load_goals() if g.get("status") == "in_progress" and g.get("deadline")]
    
    now = datetime.now(timezone.utc)
    upcoming = []
    
    for g in goals:
        try:
            deadline = datetime.fromisoformat(g["deadline"])
            days_left = (deadline - now).days
            
            if days_left <= 7:
                upcoming.append({
                    "title": g["title"],
                    "deadline": g["deadline"],
                    "days_left": days_left,
                    "priority": g.get("priority", "MEDIUM")
                })
        except:
            pass
    
    upcoming.sort(key=lambda x: x["days_left"])
    return upcoming

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "next"
    
    if cmd == "next":
        print(get_next_action())
    
    elif cmd == "context":
        ctx = get_context_block()
        if ctx:
            print(ctx)
        else:
            print("✅ No active goals")
    
    elif cmd == "upcoming":
        upcoming = get_upcoming_deadlines()
        if upcoming:
            print("📅 Deadlines in next 7 days:")
            for u in upcoming:
                days = u["days_left"]
                warning = "⚠️ OVERDUE" if days < 0 else f"{days} days"
                print(f"  - {u['title']}: {warning}")
        else:
            print("✅ No deadlines in next 7 days")
    
    elif cmd == "inject":
        ctx = get_context_block()
        if ctx:
            print(ctx)
            print("\n[SESSION CONTEXT - Intention Engine]")
        else:
            print("# No active goals")
    
    else:
        print(f"Unknown command: {cmd}")
        print("Available: next, context, upcoming, inject")

if __name__ == "__main__":
    main()