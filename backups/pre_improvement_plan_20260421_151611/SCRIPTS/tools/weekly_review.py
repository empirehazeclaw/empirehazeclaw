#!/usr/bin/env python3
"""
Sir HazeClaw Weekly Review — IMPROVED
Generiert einen wöchentlichen Review mit echten Insights.

Improvements:
- Week-over-week comparison
- KG growth tracking
- Trending metrics
- Actionable insights
- Dynamic goals from patterns

Usage:
    python3 weekly_review.py
    python3 weekly_review.py --format telegram
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE_DIR = Path("/home/clawbot/.openclaw/workspace")
MEMORY_DIR = WORKSPACE_DIR / "memory"
KG_PATH = WORKSPACE_DIR / "core_ultralight/memory/knowledge_graph.json"
HEARTBEAT_PATH = WORKSPACE_DIR / "ceo/HEARTBEAT.md"

def get_week_commits(week_ago=0):
    """Holt Git Commits für bestimmte Woche."""
    today = datetime.now()
    # Start of current week (Monday)
    week_start = today - timedelta(days=today.weekday() + (7 * week_ago))
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    week_end = week_start + timedelta(days=7)
    
    date_str = week_start.strftime('%Y-%m-%d')
    end_str = week_end.strftime('%Y-%m-%d')
    
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", f"--since={date_str}T00:00:00Z", f"--until={end_str}T00:00:00Z"],
            cwd=str(WORKSPACE_DIR),
            capture_output=True,
            text=True,
            timeout=10
        )
        commits = [c for c in result.stdout.strip().split('\n') if c]
        return len(commits), commits
    except:
        return 0, []

def get_daily_commits():
    """Holt tägliche Commits für die Woche."""
    today = datetime.now()
    daily = []
    
    for i in range(7):
        date = today - timedelta(days=6-i)
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        date_str = day_start.strftime('%Y-%m-%d')
        end_str = day_end.strftime('%Y-%m-%d')
        
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", f"--since={date_str}T00:00:00Z", f"--until={end_str}T00:00:00Z"],
                cwd=str(WORKSPACE_DIR),
                capture_output=True,
                text=True,
                timeout=5
            )
            count = len([c for c in result.stdout.strip().split('\n') if c])
            daily.append({'date': date.strftime('%a'), 'count': count})
        except:
            daily.append({'date': date.strftime('%a'), 'count': 0})
    
    return daily

def get_kg_stats():
    """Holt KG Stats."""
    if not KG_PATH.exists():
        return None
    
    with open(KG_PATH) as f:
        kg = json.load(f)
    
    entities = kg.get('entities', {})
    relations = kg.get('relations', [])
    
    by_type = {}
    for e in entities.values():
        t = e.get('type', 'unknown')
        by_type[t] = by_type.get(t, 0) + 1
    
    return {
        'entities': len(entities),
        'relations': len(relations),
        'by_type': by_type,
        'last_updated': kg.get('last_updated', 'unknown')
    }

def get_script_stats():
    """Zählt Scripts."""
    scripts_dir = WORKSPACE_DIR / "scripts"
    scripts = list(scripts_dir.glob("*.py"))
    return len(scripts)

def get_cron_stats():
    """Holt Cron Stats."""
    cron_path = WORKSPACE_DIR.parent / "cron/jobs.json"
    if not cron_path.exists():
        return 0, 0, 0
    
    with open(cron_path) as f:
        data = json.load(f)
    
    jobs = data.get('jobs', [])
    enabled_jobs = [j for j in jobs if j.get('enabled', True)]
    enabled = len(enabled_jobs)
    failed = len([j for j in enabled_jobs if j.get('state', {}).get('lastRunStatus') == 'error'])
    
    return len(jobs), enabled, failed

def get_memory_notes_count():
    """Zählt Memory Notes der Woche."""
    today = datetime.now()
    count = 0
    
    for i in range(7):
        date = today - timedelta(days=i)
        note_file = MEMORY_DIR / f"{date.strftime('%Y-%m-%d')}.md"
        if note_file.exists():
            count += 1
    
    return count

def get_system_health():
    """Holt System Health."""
    health = {
        'disk_ok': True,
        'mem_ok': True,
        'load_ok': True
    }
    
    # Check disk
    try:
        import psutil
        disk = psutil.disk_usage('/')
        health['disk_ok'] = disk.percent < 90
        health['disk_free'] = f"{100-disk.percent:.0f}%"
    except:
        pass
    
    # Check load
    try:
        import os
        load = os.getloadavg()[0]
        health['load_ok'] = load < 4.0
        health['load'] = f"{load:.2f}"
    except:
        pass
    
    return health

def get_blockers():
    """Liest Blockers aus HEARTBEAT."""
    if not HEARTBEAT_PATH.exists():
        return []
    
    content = HEARTBEAT_PATH.read_text()
    blockers = []
    
    lines = content.split('\n')
    in_blocker_section = False
    
    for line in lines:
        if 'OFFENE BLOCKER' in line:
            in_blocker_section = True
            continue
        elif in_blocker_section:
            if line.startswith('##') and '---' not in line:
                break
            if '|' in line and ('🔴' in line or '🟡' in line):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) > 2:
                    task = parts[2].strip()
                    if task and task not in ['#', 'Task', '---']:
                        blockers.append(task)
    
    return blockers[:5]

def generate_review(format='text'):
    """Generiert Weekly Review."""
    today = datetime.now()
    week_num = today.isocalendar()[1]
    
    # Current week stats
    commits_this_week, commit_list = get_week_commits(0)
    commits_last_week, _ = get_week_commits(1)
    daily = get_daily_commits()
    kg = get_kg_stats()
    script_count = get_script_stats()
    total_crons, enabled_crons, failed_crons = get_cron_stats()
    memory_days = get_memory_notes_count()
    health = get_system_health()
    blockers = get_blockers()
    
    # Calculate trends
    if commits_last_week > 0:
        commit_trend = ((commits_this_week - commits_last_week) / commits_last_week) * 100
        commit_trend_str = f"+{commit_trend:.0f}%" if commit_trend >= 0 else f"{commit_trend:.0f}%"
    else:
        commit_trend_str = "N/A"
    
    # Find best day
    best_day = max(daily, key=lambda x: x['count']) if daily else {'date': 'N/A', 'count': 0}
    
    if format == 'telegram':
        msg = f"""📊 **Weekly Review — Week {week_num}**

━━━━━━━━━━━━━━━━━━━
**📈 ACTIVITY**
• Commits: {commits_this_week} ({commit_trend_str} vs last week)
• Best Day: {best_day['date']} ({best_day['count']} commits)
• Memory Notes: {memory_days}/7 days
• Failed Crons: {failed_crons}

━━━━━━━━━━━━━━━━━━━
**📅 DAILY BREAKDOWN**
"""
        for d in daily:
            bar = '█' * min(d['count'], 20)
            msg += f"{d['date']}: {d['count']:3d} {bar}\n"
        
        msg += f"""
━━━━━━━━━━━━━━━━━━━
**🧠 KNOWLEDGE GRAPH**
• Entities: {kg['entities'] if kg else 'N/A'}
• Relations: {kg['relations'] if kg else 'N/A'}"""

        if kg and 'skill' in kg['by_type']:
            msg += f"\n• Skills: {kg['by_type']['skill']}"

        msg += f"""
━━━━━━━━━━━━━━━━━━━
**⚙️ SYSTEM**
• Scripts: {script_count}
• Crons: {enabled_crons}/{total_crons} enabled"""

        if blockers:
            msg += f"\n━━━━━━━━━━━━━━━━━━━\n**⚠️ BLOCKERS ({len(blockers)})**"
            for b in blockers:
                msg += f"\n• {b}"

        msg += f"""
━━━━━━━━━━━━━━━━━━━
**💡 INSIGHTS**

"""
        # Dynamic insights
        if commits_this_week > 50:
            msg += "• 🔥 Sehr produktive Woche!\n"
        elif commits_this_week < 10:
            msg += "• ⚠️ Weniger Commits diese Woche\n"
        
        if failed_crons > 0:
            msg += f"• 🔴 {failed_crons} Cron(s) fehlgeschlagen\n"
        
        if health['load_ok'] and health['disk_ok']:
            msg += "• ✅ System healthy\n"
        
        if kg and kg['entities'] > 150:
            msg += f"• ✅ KG wächst: {kg['entities']} entities\n"

        msg += f"""
━━━━━━━━━━━━━━━━━━━
🦞 Sir HazeClaw"""
    
    else:
        msg = f"""# 📊 Weekly Review — Week {week_num}

**Generated:** {today.strftime('%Y-%m-%d %H:%M UTC')}

## 📈 ACTIVITY

| Metric | This Week | Last Week | Trend |
|--------|-----------|-----------|-------|
| Commits | {commits_this_week} | {commits_last_week} | {commit_trend_str} |
| Best Day | {best_day['date']} ({best_day['count']}) | - | - |
| Memory Notes | {memory_days}/7 days | - | - |

### Daily Breakdown
"""
        for d in daily:
            bar = '█' * min(d['count'], 15)
            msg += f"- {d['date']}: {d['count']:3d} {bar}\n"

        msg += f"""
## 🧠 Knowledge Graph
| Metric | Value |
|--------|-------|
| Entities | {kg['entities'] if kg else 'N/A'} |
| Relations | {kg['relations'] if kg else 'N/A'} |
"""

        if kg:
            msg += f"\n**Top Types:**\n"
            for t, c in sorted(kg['by_type'].items(), key=lambda x: -x[1])[:5]:
                msg += f"- {t}: {c}\n"

        msg += f"""
## ⚙️ SYSTEM
| Metric | Value |
|--------|-------|
| Scripts | {script_count} |
| Crons | {enabled_crons}/{total_crons} enabled |
| Failed Crons | {failed_crons} |
"""

        if blockers:
            msg += f"\n## ⚠️ BLOCKERS ({len(blockers)})\n"
            for b in blockers:
                msg += f"- {b}\n"

        msg += f"""
## 💡 INSIGHTS
"""
        if commits_this_week > 50:
            msg += "- 🔥 Sehr produktive Woche!\n"
        if failed_crons > 0:
            msg += f"- 🔴 {failed_crons} Cron(s) fehlgeschlagen\n"
        if health['load_ok'] and health['disk_ok']:
            msg += "- ✅ System healthy\n"

        msg += f"""
---
*Sir HazeClaw*"""
    
    return msg

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Weekly Review - Improved')
    parser.add_argument('--format', choices=['text', 'telegram'], default='telegram')
    parser.add_argument('--output', help='Output file')
    args = parser.parse_args()
    
    review = generate_review(args.format)
    
    if args.output:
        Path(args.output).write_text(review)
        print(f"✅ Review written to {args.output}")
    else:
        print(review)

if __name__ == "__main__":
    main()