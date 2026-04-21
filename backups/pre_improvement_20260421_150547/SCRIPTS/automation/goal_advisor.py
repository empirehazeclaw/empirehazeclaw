#!/usr/bin/env python3
"""
🦞 Sir HazeClaw — Goal Advisor Skill
Proaktiv schlägt nächste Actions für Goals vor

Usage:
    python3 goal_advisor.py              # Recommend next actions
    python3 goal_advisor.py --top        # Only top priority
"""

import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
GOALS_FILE = WORKSPACE / "memory" / "goals.json"

def load_goals():
    if not GOALS_FILE.exists():
        return []
    with open(GOALS_FILE) as f:
        return json.load(f)

def get_next_action(goal: dict) -> str:
    """Bestimme nächste Action für ein Goal."""
    pending = [m for m in goal.get("milestones", []) if not m.get("done")]
    if pending:
        return f"→ {pending[0]['text']}"
    
    deadline = goal.get("deadline", "No deadline")
    context = goal.get("context", "")
    
    if context:
        return f"Focus: {context[:50]}"
    return f"Deadline: {deadline}"

def prioritize_goals(goals: list) -> list:
    """Sortiere Goals nach Dringlichkeit."""
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    
    now = datetime.now(timezone.utc)
    scored = []
    
    for g in goals:
        if g.get("status") == "completed":
            continue
        
        deadline = g.get("deadline")
        days_left = 999
        if deadline:
            try:
                dt = datetime.fromisoformat(deadline).replace(tzinfo=timezone.utc)
                days_left = (dt - now).days
            except:
                pass
        
        priority = priority_order.get(g.get("priority", "MEDIUM"), 2)
        
        # Score: lower is better (days_left + priority)
        score = days_left + priority * 10
        scored.append((score, g))
    
    scored.sort()
    return [g for _, g in scored]

def recommend():
    goals = load_goals()
    active = [g for g in goals if g.get("status") == "in_progress"]
    
    if not active:
        print("✅ Keine aktiven Goals. System ist clean!")
        return 0
    
    prioritized = prioritize_goals(active)
    
    print("🎯 Goal Advisor — Nächste Actions")
    print("=" * 50)
    
    for i, g in enumerate(prioritized[:3], 1):
        deadline = g.get("deadline", "No deadline")
        days_left = "?"
        if deadline:
            try:
                dt = datetime.fromisoformat(deadline).replace(tzinfo=timezone.utc)
                days = (dt - datetime.now(timezone.utc)).days
                days_left = f"{days}d"
            except:
                days_left = "?"
        
        emoji = "🔴" if g.get("priority") == "HIGH" else "🟡"
        next_action = get_next_action(g)
        
        print(f"{i}. {emoji} **{g['title']}**")
        print(f"   Deadline: {deadline} ({days_left})")
        print(f"   {next_action}")
        print()
    
    return 0

def main():
    if "--top" in sys.argv:
        goals = load_goals()
        active = [g for g in goals if g.get("status") == "in_progress"]
        if active:
            prioritized = prioritize_goals(active)
            top = prioritized[0]
            print(f"🎯 Top Priority: {top['title']}")
            print(f"   {get_next_action(top)}")
        return 0
    
    return recommend()

if __name__ == "__main__":
    sys.exit(main())