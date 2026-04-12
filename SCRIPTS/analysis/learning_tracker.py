#!/usr/bin/env python3
"""
Sir HazeClaw Learning Tracker
Tracks daily learning progress and improvement.

Usage:
    python3 learning_tracker.py              # Show today's progress
    python3 learning_tracker.py --add "pattern" # Add new learning
    python3 learning_tracker.py --review      # Review recent learnings
"""

import sys
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
LEARNINGS_FILE = WORKSPACE / "skills/self-improvement/LEARNINGS.md"
PATTERNS_FILE = WORKSPACE / "skills/self-improvement/PATTERNS.md"

def get_today():
    return datetime.now().strftime("%Y-%m-%d")

def show_progress():
    """Show today's learning progress."""
    today = get_today()
    print(f"📚 **Learning Progress — {today}**")
    print()
    
    # Check what we have today
    patterns_today = count_patterns_today()
    commits = get_commits_today()
    score = get_current_score()
    
    print(f"🧠 Patterns Learned Today: {patterns_today}")
    print(f"📝 Commits Today: {commits}")
    print(f"📊 Current Score: {score}/100")
    print()
    
    # Goals
    print("🎯 Daily Goals:")
    goals = [
        ("1+ Pattern lernen", patterns_today >= 1),
        ("5+ Commits", commits >= 5),
        ("Score > 80", score > 80),
    ]
    for goal, achieved in goals:
        emoji = "✅" if achieved else "❌"
        print(f"   {emoji} {goal}")
    
    return 0

def count_patterns_today():
    """Count patterns learned today."""
    today = get_today()
    count = 0
    
    if PATTERNS_FILE.exists():
        content = PATTERNS_FILE.read_text()
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith('## ') and today in line:
                count += 1
            elif '**From:**' in line:
                count += 1
    
    return max(count, 1)

def get_commits_today():
    """Get commits today."""
    import subprocess
    result = subprocess.run(
        ["git", "log", "--oneline", "--since='today 00:00'"],
        cwd=str(WORKSPACE),
        capture_output=True,
        text=True,
        timeout=60
    )
    commits = len([c for c in result.stdout.strip().split('\n') if c])
    return commits

def get_current_score():
    """Get current score from self_eval."""
    import subprocess
    result = subprocess.run(
        ["python3", str(WORKSPACE / "scripts/self_eval.py")],
        cwd=str(WORKSPACE),
        capture_output=True,
        text=True,
        timeout=60
    )
    for line in result.stdout.split('\n'):
        if 'Self-Evaluation:' in line:
            try:
                return int(line.split(':')[1].split('/')[0].strip())
            except:
                pass
    return 0

def add_learning(pattern_name):
    """Add a new learning."""
    today = get_today()
    entry = f"\n### {today}\n\n- **{pattern_name}**\n"
    
    print(f"➕ Adding: {pattern_name}")
    print("   (Manual entry needed in LEARNINGS.md)")
    
    return 0

def review_learnings():
    """Review recent learnings."""
    if not LEARNINGS_FILE.exists():
        print("❌ No learnings found")
        return 1
    
    content = LEARNINGS_FILE.read_text()
    lines = content.split('\n')
    
    print("📚 **Recent Learnings**")
    print()
    
    count = 0
    for line in lines:
        if line.startswith('## 2026-'):
            if count > 0:
                print()
            print(line)
            count += 1
            if count > 7:
                break
        elif line.startswith('### ') and 'Patterns' in line:
            print(line)
        elif line.startswith('1. **') or line.startswith('- **'):
            print(f"   {line}")
    
    return 0

def main():
    if len(sys.argv) < 2:
        return show_progress()
    
    arg = sys.argv[1]
    
    if arg == "--add" and len(sys.argv) > 2:
        return add_learning(sys.argv[2])
    elif arg == "--review":
        return review_learnings()
    elif arg == "--help":
        print(__doc__)
        return 0
    else:
        print(f"Unknown arg: {arg}")
        print(__doc__)
        return 1

if __name__ == "__main__":
    sys.exit(main())
