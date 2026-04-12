#!/usr/bin/env python3
"""
Sir HazeClaw Token Tracker
Tracks token usage for efficiency optimization.

Based on OpenSpace research: 46% token reduction possible through pattern reuse.

Usage:
    python3 token_tracker.py              # Show today's usage
    python3 token_tracker.py --week      # Show weekly stats
    python3 token_tracker.py --add <tokens> <task>  # Log usage
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
TOKEN_LOG = WORKSPACE / "data/token_log.json"

def load_log():
    """Load token log."""
    if TOKEN_LOG.exists():
        with open(TOKEN_LOG) as f:
            return json.load(f)
    return {"entries": [], "total_tokens": 0}

def save_log(log):
    """Save token log."""
    TOKEN_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(TOKEN_LOG, 'w') as f:
        json.dump(log, f, indent=2)

def add_entry(tokens, task, model="minimax/MiniMax-M2.7"):
    """Add a token usage entry."""
    log = load_log()
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "tokens": tokens,
        "task": task,
        "model": model
    }
    
    log["entries"].append(entry)
    log["total_tokens"] += tokens
    
    save_log(log)
    return entry

def show_today():
    """Show today's token usage."""
    log = load_log()
    today = datetime.now().strftime("%Y-%m-%d")
    
    today_entries = [e for e in log["entries"] if e["timestamp"].startswith(today)]
    
    print("📊 **Token Usage — Today**")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print()
    
    if not today_entries:
        print("   No entries yet today")
        return
    
    total = sum(e["tokens"] for e in today_entries)
    avg = total / len(today_entries)
    
    print(f"   **Total:** {total:,} tokens")
    print(f"   **Average/Task:** {avg:,.0f} tokens")
    print(f"   **Tasks:** {len(today_entries)}")
    print()
    
    # By task type
    by_task = {}
    for e in today_entries:
        task = e["task"].split("/")[0]  # First part of path
        by_task[task] = by_task.get(task, 0) + e["tokens"]
    
    print("   **By Category:**")
    for task, tokens in sorted(by_task.items(), key=lambda x: -x[1])[:5]:
        print(f"     {task}: {tokens:,}")

def show_week():
    """Show weekly token usage."""
    log = load_log()
    week_ago = datetime.now() - timedelta(days=7)
    
    week_entries = [
        e for e in log["entries"]
        if datetime.fromisoformat(e["timestamp"]) > week_ago
    ]
    
    print("📊 **Token Usage — Last 7 Days**")
    print()
    
    if not week_entries:
        print("   No entries this week")
        return
    
    total = sum(e["tokens"] for e in week_entries)
    avg = total / len(week_entries)
    
    print(f"   **Total:** {total:,} tokens")
    print(f"   **Average/Task:** {avg:,.0f} tokens")
    print(f"   **Tasks:** {len(week_entries)}")
    print(f"   **Daily Average:** {total/7:,.0f} tokens")
    
    # By day
    by_day = {}
    for e in week_entries:
        day = e["timestamp"][:10]
        by_day[day] = by_day.get(day, 0) + e["tokens"]
    
    print()
    print("   **Daily:**")
    for day, tokens in sorted(by_day.items()):
        bars = min(tokens // 1000, 50)
        print(f"     {day}: {'█' * bars} {tokens:,}")

def main():
    if len(sys.argv) < 2:
        return show_today()
    
    arg = sys.argv[1]
    
    if arg == "--add" and len(sys.argv) > 3:
        try:
            tokens = int(sys.argv[2])
            task = sys.argv[3]
            entry = add_entry(tokens, task)
            print(f"✅ Logged: {tokens} tokens for {task}")
        except ValueError:
            print("❌ Usage: token_tracker.py --add <tokens> <task>")
        return 0
    elif arg == "--week":
        return show_week()
    elif arg == "--help":
        print(__doc__)
        return 0
    else:
        print(f"Unknown: {arg}")
        print(__doc__)
        return 1

if __name__ == "__main__":
    sys.exit(main())
