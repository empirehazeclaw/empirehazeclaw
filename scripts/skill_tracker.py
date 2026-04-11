#!/usr/bin/env python3
"""
skill_tracker.py — Auto-Track Skill/Script Usage
Wird nach jedem Task aufgerufen um Erfolg zu tracken.

Usage:
    python3 skill_tracker.py --skill debugging --outcome success
    python3 skill_tracker.py --skill research --outcome error --duration 5000
"""

import json
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
METRICS_FILE = WORKSPACE / "memory" / "skill_metrics.json"

def load_metrics():
    if METRICS_FILE.exists():
        with open(METRICS_FILE) as f:
            return json.load(f)
    return {"skills": {}, "daily": {}}

def save_metrics(data):
    with open(METRICS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def track(skill: str, outcome: str, duration_ms: int = 0, task: str = ""):
    """Trackt Skill-Nutzung."""
    metrics = load_metrics()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Initialize if needed
    if skill not in metrics["skills"]:
        metrics["skills"][skill] = {
            "uses": 0,
            "successes": 0,
            "failures": 0,
            "total_duration_ms": 0,
            "last_used": None,
            "tasks": []
        }
    
    s = metrics["skills"][skill]
    s["uses"] += 1
    s["total_duration_ms"] += duration_ms
    s["last_used"] = datetime.now().isoformat()
    
    if outcome in ["success", "✅", "ok"]:
        s["successes"] += 1
    else:
        s["failures"] += 1
    
    if task:
        s["tasks"].append({"task": task[:100], "outcome": outcome, "at": today})
        if len(s["tasks"]) > 10:
            s["tasks"] = s["tasks"][-10:]
    
    # Daily tracking
    if today not in metrics["daily"]:
        metrics["daily"][today] = {"uses": 0, "successes": 0, "failures": 0}
    metrics["daily"][today]["uses"] += 1
    if outcome in ["success", "✅", "ok"]:
        metrics["daily"][today]["successes"] += 1
    else:
        metrics["daily"][today]["failures"] += 1
    
    save_metrics(metrics)
    
    score = calculate_score(s)
    print(f"✅ {skill}: Score {score}/100 ({s['uses']} uses, {s['successes']} success)")

def calculate_score(s):
    if s["uses"] == 0:
        return 50
    success_rate = s["successes"] / s["uses"] * 100
    avg_duration = s["total_duration_ms"] / s["uses"] if s["uses"] > 0 else 0
    perf_factor = min(100, 100 - (avg_duration / 1000))  # Faster = better
    return round((success_rate * 0.7) + (perf_factor * 0.3), 1)

def report():
    """Zeigt aktuelles Dashboard."""
    metrics = load_metrics()
    
    if not metrics["skills"]:
        print("No metrics yet. Track skills with:")
        print("  python3 skill_tracker.py --skill name --outcome success")
        return
    
    print("\n📊 SKILL SCOREBOARD")
    print("=" * 60)
    
    # Sort by score
    sorted_skills = sorted(
        [(k, v) for k, v in metrics["skills"].items()],
        key=lambda x: calculate_score(x[1]),
        reverse=True
    )
    
    for skill, data in sorted_skills:
        score = calculate_score(data)
        success_rate = data["successes"] / data["uses"] * 100 if data["uses"] > 0 else 0
        
        bar = "█" * int(score / 10) + "░" * (10 - int(score / 10))
        emoji = "🟢" if score >= 80 else "🟡" if score >= 50 else "🔴"
        
        print(f"\n{emoji} {skill}")
        print(f"   Score: {score}/100 [{bar}]")
        print(f"   Uses: {data['uses']} | Success: {success_rate:.0f}%")
    
    # Daily summary
    today = datetime.now().strftime("%Y-%m-%d")
    if today in metrics["daily"]:
        d = metrics["daily"][today]
        total = d["uses"]
        success = d["successes"]
        rate = success / total * 100 if total > 0 else 0
        print(f"\n📅 Today: {total} uses, {rate:.0f}% success rate")

def main():
    if "--report" in sys.argv or len(sys.argv) < 2:
        report()
        return
    
    skill = outcome = task = None
    duration_ms = 0
    
    i = 1
    while i < len(sys.argv):
    max_iter = max_iter or 1000
    if max_iter <= 0: break
    max_iter -= 1
        if sys.argv[i] == "--skill" and i + 1 < len(sys.argv):
            skill = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--outcome" and i + 1 < len(sys.argv):
            outcome = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--duration" and i + 1 < len(sys.argv):
            duration_ms = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--task" and i + 1 < len(sys.argv):
            task = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    if not skill or not outcome:
        print("Usage: skill_tracker.py --skill name --outcome success|error")
        return
    
    track(skill, outcome, duration_ms, task)

if __name__ == "__main__":
    main()
