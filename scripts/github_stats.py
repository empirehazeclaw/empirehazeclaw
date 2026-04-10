#!/usr/bin/env python3
"""
Sir HazeClaw GitHub Stats Tracker
Trackt GitHub Activity über Zeit.
"""

import subprocess
import json
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")

def get_git_stats():
    """Holt Git Statistics."""
    stats = {}
    
    # Today
    result = subprocess.run(
        ["git", "log", "--oneline", "--since='today 00:00'"],
        cwd=str(WORKSPACE),
        capture_output=True,
        text=True
    )
    stats['today'] = len([c for c in result.stdout.strip().split('\n') if c])
    
    # Yesterday
    result = subprocess.run(
        ["git", "log", "--oneline", "--since='yesterday 00:00' --until='today 00:00'"],
        cwd=str(WORKSPACE),
        capture_output=True,
        text=True
    )
    stats['yesterday'] = len([c for c in result.stdout.strip().split('\n') if c])
    
    # This week
    result = subprocess.run(
        ["git", "log", "--oneline", "--since='7 days ago'"],
        cwd=str(WORKSPACE),
        capture_output=True,
        text=True
    )
    stats['week'] = len([c for c in result.stdout.strip().split('\n') if c])
    
    # This month
    result = subprocess.run(
        ["git", "log", "--oneline", "--since='30 days ago'"],
        cwd=str(WORKSPACE),
        capture_output=True,
        text=True
    )
    stats['month'] = len([c for c in result.stdout.strip().split('\n') if c])
    
    # Files changed today
    result = subprocess.run(
        ["git", "diff", "--stat", "--since='today 00:00'"],
        cwd=str(WORKSPACE),
        capture_output=True,
        text=True
    )
    stats['files_changed_today'] = len([l for l in result.stdout.split('\n') if '|' in l])
    
    return stats

def get_branch_info():
    """Holt Branch Information."""
    result = subprocess.run(
        ["git", "branch", "-v"],
        cwd=str(WORKSPACE),
        capture_output=True,
        text=True
    )
    
    branches = []
    for line in result.stdout.split('\n'):
        if line.strip():
            branches.append(line.strip())
    
    return branches

def generate_report():
    """Generiert GitHub Stats Report."""
    stats = get_git_stats()
    branches = get_branch_info()
    
    # Calculate trends
    if stats['yesterday'] > 0:
        trend = ((stats['today'] - stats['yesterday']) / stats['yesterday']) * 100
        trend_str = f"{trend:+.0f}%" if trend else "0%"
    else:
        trend_str = "N/A"
    
    lines = []
    lines.append("📊 **GITHUB STATS**")
    lines.append(f"_Generated: {datetime.now().strftime('%H:%M UTC')}_")
    lines.append("")
    lines.append("**📈 Commits:**")
    lines.append(f"  - Heute: {stats['today']}")
    lines.append(f"  - Gestern: {stats['yesterday']}")
    lines.append(f"  - Trend: {trend_str}")
    lines.append(f"  - Woche: {stats['week']}")
    lines.append(f"  - Monat: {stats['month']}")
    lines.append("")
    lines.append("**📁 Changes:**")
    lines.append(f"  - Files geändert (heute): {stats['files_changed_today']}")
    lines.append("")
    lines.append("**🌿 Branches:**")
    for branch in branches[:5]:
        lines.append(f"  - {branch}")
    
    return "\n".join(lines)

def save_stats():
    """Speichert Stats als JSON für Historie."""
    stats_file = WORKSPACE / "memory" / "github_stats.json"
    stats_file.parent.mkdir(parents=True, exist_ok=True)
    
    stats = get_git_stats()
    stats['timestamp'] = datetime.now().isoformat()
    
    # Load existing
    if stats_file.exists():
        with open(stats_file) as f:
            history = json.load(f)
    else:
        history = []
    
    # Append today
    history.append(stats)
    
    # Keep last 30 days
    history = history[-30:]
    
    with open(stats_file, 'w') as f:
        json.dump(history, f, indent=2)
    
    return stats

def main():
    print(generate_report())
    
    # Save for history
    save_stats()

if __name__ == "__main__":
    main()
