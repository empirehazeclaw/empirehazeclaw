#!/usr/bin/env python3
"""
Sir HazeClaw Weekly Review
Generiert einen wöchentlichen Review.

Usage:
    python3 weekly_review.py
    python3 weekly_review.py --week 2026-W15
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE_DIR = Path("/home/clawbot/.openclaw/workspace")
MEMORY_DIR = WORKSPACE_DIR / "memory"

def get_week_commits():
    """Holt Git Commits der Woche."""
    # Calculate week start
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    date_str = week_start.strftime('%Y-%m-%d')
    
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", f"--since='{date_str} 00:00'"],
            cwd=WORKSPACE_DIR,
            capture_output=True,
            text=True
        )
        commits = [c for c in result.stdout.strip().split('\n') if c]
        return len(commits), commits
    except Exception as e:
        return 0, []

def get_weekly_memory():
    """Holt Memory Notes der Woche."""
    notes = []
    
    today = datetime.now()
    week_start = today - timedelta(days=7)
    
    for i in range(7):
        date = week_start + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        note_file = MEMORY_DIR / f"{date_str}.md"
        
        if note_file.exists():
            notes.append({
                'date': date_str,
                'exists': True
            })
    
    return notes

def get_script_stats():
    """Holt Script Statistiken."""
    scripts_dir = WORKSPACE_DIR / "scripts"
    
    if not scripts_dir.exists():
        return 0
    
    py_files = list(scripts_dir.glob("*.py"))
    sh_files = list(scripts_dir.glob("*.sh"))
    
    return len(py_files) + len(sh_files)

def get_cron_stats():
    """Holt Cron Statistiken."""
    cron_path = Path("/home/clawbot/.openclaw/cron/jobs.json")
    
    if not cron_path.exists():
        return 0, 0
    
    with open(cron_path) as f:
        data = json.load(f)
    
    jobs = data.get('jobs', [])
    enabled = len([j for j in jobs if j.get('enabled', True)])
    
    return len(jobs), enabled

def generate_review():
    """Generiert Weekly Review."""
    today = datetime.now()
    week_num = today.isocalendar()[1]
    
    commits, commit_list = get_week_commits()
    memory_notes = get_weekly_memory()
    script_count = get_script_stats()
    total_crons, enabled_crons = get_cron_stats()
    
    review = f"""# 📊 Weekly Review — Week {week_num}

**Generated:** {today.strftime('%Y-%m-%d %H:%M UTC')}

---

## 📈 ACTIVITY

### Git Commits
- **Total:** {commits} this week
"""
    
    if commit_list:
        review += "\nRecent Commits:\n"
        for c in commit_list[:10]:
            review += f"- `{c[:8]}` {c[9:]}\n"
    
    review += f"""

### Memory Notes
- **Days with notes:** {sum(1 for n in memory_notes if n.get('exists'))}/7

"""
    
    review += f"""## 📁 SYSTEM STATS

### Scripts
- **Total Scripts:** {script_count}

### Crons
- **Total Jobs:** {total_crons}
- **Enabled:** {enabled_crons}

---

## 🎯 GESETZTE ZIELE (diese Woche)

1. ⏳ OpenRouter API Key erneuern
2. ⏳ Solo Fighter Mode optimieren
3. ⏳ Health Monitoring einrichten

---

## 📝 LERNINGS

- Workflow für größere Tasks befolgen
- Quality Checks vor "fertig" 
- Nicht aufhören wenn nicht gestoppt

---

## 🔴 OFFENE ISSUES

1. OpenRouter API Key invalide
2. Solo Fighter Mode - weitere Optimierungen nötig

---

*Sir HazeClaw — Weekly Review*"""

    return review

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Weekly Review')
    parser.add_argument('--week', help='Week (e.g., 2026-W15)')
    parser.add_argument('--output', help='Output file')
    args = parser.parse_args()
    
    review = generate_review()
    
    if args.output:
        Path(args.output).write_text(review)
        print(f"✅ Review written to {args.output}")
    else:
        print(review)

if __name__ == "__main__":
    main()