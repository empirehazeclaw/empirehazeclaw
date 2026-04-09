#!/usr/bin/env python3
"""
🔄 FEEDBACK LOOP SYSTEM
=====================
Automatically learns from successes and failures
"""

import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

FEEDBACK_FILE = DATA_DIR / "feedback_loop.json"

def load_feedback():
    if FEEDBACK_FILE.exists():
        return json.load(open(FEEDBACK_FILE))
    return {"successes": [], "failures": [], "insights": []}

def save_feedback(data):
    json.dump(data, open(FEEDBACK_FILE, "w"), indent=2)

def add_success(action, result, revenue=0):
    data = load_feedback()
    data["successes"].append({
        "date": datetime.now().isoformat(),
        "action": action,
        "result": result,
        "revenue": revenue
    })
    save_feedback(data)
    return f"✅ Success logged: {action}"

def add_failure(action, error, lesson=""):
    data = load_feedback()
    data["failures"].append({
        "date": datetime.now().isoformat(),
        "action": action,
        "error": error,
        "lesson": lesson
    })
    save_feedback(data)
    return f"❌ Failure logged: {action}"

def get_insights():
    data = load_feedback()
    successes = len(data["successes"])
    failures = len(data["failures"])
    
    insights = []
    
    # Calculate success rate
    total = successes + failures
    if total > 0:
        rate = (successes / total) * 100
        insights.append(f"Success Rate: {rate:.1f}%")
    
    # Revenue insights
    total_revenue = sum(s["revenue"] for s in data["successes"])
    insights.append(f"Total Revenue: €{total_revenue}")
    
    return insights

# CLI
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("🔄 Feedback Loop System")
        print("Usage:")
        print("  python3 feedback_loop.py success 'action' 'result' €revenue")
        print("  python3 feedback_loop.py failure 'action' 'error' 'lesson'")
        print("  python3 feedback_loop.py insights")
        print("")
        for i in get_insights():
            print(f"  {i}")
    elif sys.argv[1] == "success":
        action = sys.argv[2] if len(sys.argv) > 2 else "unknown"
        result = sys.argv[3] if len(sys.argv) > 3 else "ok"
        revenue = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        print(add_success(action, result, revenue))
    elif sys.argv[1] == "failure":
        action = sys.argv[2] if len(sys.argv) > 2 else "unknown"
        error = sys.argv[3] if len(sys.argv) > 3 else "unknown"
        lesson = sys.argv[4] if len(sys.argv) > 4 else ""
        print(add_failure(action, error, lesson))
    elif sys.argv[1] == "insights":
        for i in get_insights():
            print(i)
