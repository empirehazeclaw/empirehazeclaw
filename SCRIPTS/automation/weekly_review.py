#!/usr/bin/env python3
"""
Sir HazeClaw Weekly Review Generator
Erstellt eine wöchentliche Zusammenfassung für den CEO.

Usage:
    python3 weekly_review.py
    python3 weekly_review.py --week 2026-W15
    python3 weekly_review.py --format telegram
"""

import os
import sys
import json
import glob
import psutil
import socket
from datetime import datetime, timedelta
from pathlib import Path

# Config
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
CEO_DIR = WORKSPACE / "ceo"
KG_PATH = WORKSPACE / "core_ultralight/memory/knowledge_graph.json"
CRON_PATH = WORKSPACE.parent / "cron/jobs.json"

def get_week_boundaries(week_str=None):
    """Holt Start und Ende der Woche."""
    if week_str is None:
        # Aktuelle Woche
        today = datetime.now()
    else:
        # Parse ISO week string (2026-W15)
        year, week = week_str.split('-W')
        today = datetime.strptime(f"{year}-W{week}-1", "%Y-W%W-%w")
    
    # Start of week (Monday)
    start = today - timedelta(days=today.weekday())
    # End of week (Sunday)
    end = start + timedelta(days=6)
    
    return start, end

def get_git_commits_week(start, end):
    """Holt Git Commits für die Woche."""
    import subprocess
    
    start_str = start.strftime('%Y-%m-%d')
    end_str = end.strftime('%Y-%m-%d')
    
    result = subprocess.run(
        ["git", "log", "--oneline", f"--since={start_str}T00:00:00Z", f"--until={end_str}T23:59:59Z", "--format=%H %s"],
        cwd=str(WORKSPACE),
        capture_output=True,
        text=True,
        timeout=15
    )
    
    commits = []
    for line in result.stdout.strip().split('\n'):
        if line:
            parts = line.split(' ', 1)
            if len(parts) == 2:
                commits.append({"hash": parts[0][:8], "msg": parts[1]})
    return commits

def get_memory_notes_week(start, end):
    """Holt Memory Notes für die Woche."""
    notes_count = 0
    total_chars = 0
    days_with_notes = set()
    
    current = start
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        notes_file = MEMORY_DIR / f"{date_str}.md"
        
        if notes_file.exists():
            content = notes_file.read_text()
            notes_count += 1
            total_chars += len(content)
            days_with_notes.add(date_str)
        
        current += timedelta(days=1)
    
    return notes_count, total_chars, len(days_with_notes)

def get_kg_stats():
    """Holt KG Stats."""
    if not KG_PATH.exists():
        return None
    
    with open(KG_PATH) as f:
        kg = json.load(f)
    
    return {
        'entities': len(kg.get('entities', {})),
        'relations': len(kg.get('relations', []))
    }

def get_cron_summary():
    """Holt Cron Zusammenfassung für die Woche."""
    if not CRON_PATH.exists():
        return 0, 0, 0, 0
    
    with open(CRON_PATH) as f:
        data = json.load(f)
    
    jobs = data.get('jobs', [])
    enabled = [j for j in jobs if j.get('enabled', True)]
    failed = [j for j in enabled if j.get('state', {}).get('lastRunStatus') == 'error']
    
    # Calculate total runs from state
    total_runs = 0
    total_errors = 0
    for job in enabled:
        state = job.get('state', {})
        if state.get('lastRunAtMs'):
            total_runs += 1
        if state.get('lastRunStatus') == 'error':
            total_errors += 1
    
    return len(jobs), len(enabled), len(failed), total_runs

def get_learning_loop_stats():
    """Holt Learning Loop Stats."""
    ll_file = CEO_DIR / "memory" / "learning_loop.json"
    
    if ll_file.exists():
        with open(ll_file) as f:
            data = json.load(f)
        return {
            'score': data.get('current_score', 'N/A'),
            'runs': data.get('total_runs', 0),
            'improvements': data.get('improvements_this_week', 0)
        }
    return None

def get_system_health():
    """Holt System Health."""
    checks = []
    
    # Gateway
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(("127.0.0.1", 18789))
        sock.close()
        checks.append(('gateway', result == 0, "Gateway OK" if result == 0 else "Gateway DOWN"))
    except:
        checks.append(('gateway', False, "Gateway check failed"))
    
    # Disk
    disk = psutil.disk_usage('/')
    free_pct = 100 - disk.percent
    checks.append(('disk', free_pct > 15, f"Disk {free_pct:.0f}% free"))
    
    # Memory
    mem = psutil.virtual_memory()
    free_mem = 100 - mem.percent
    checks.append(('memory', free_mem > 20, f"Memory {free_mem:.0f}% free"))
    
    # Load
    load = os.getloadavg()[0]
    checks.append(('load', load < 4.0, f"Load {load:.2f}"))
    
    return checks

def get_scripts_created():
    """Zählt neue Scripts diese Woche."""
    scripts_dir = WORKSPACE / "SCRIPTS" / "automation"
    today = datetime.now()
    week_ago = today - timedelta(days=7)
    
    new_scripts = []
    if scripts_dir.exists():
        for f in scripts_dir.glob("*.py"):
            try:
                # Skip symlinks to avoid circular references
                if f.is_symlink():
                    continue
                if datetime.fromtimestamp(f.stat().st_mtime) > week_ago:
                    new_scripts.append(f.name)
            except OSError:
                continue
    
    return new_scripts

def generate_weekly_summary(format='telegram', week_str=None):
    """Generiert wöchentlichen Summary."""
    start, end = get_week_boundaries(week_str)
    today_str = datetime.now().strftime("%Y-%m-%d")
    week_str = start.strftime("%Y-W%W")
    
    # Gather data
    commits_week = get_git_commits_week(start, end)
    memory_count, memory_chars, days_with_notes = get_memory_notes_week(start, end)
    kg = get_kg_stats()
    system_checks = get_system_health()
    total_crons, enabled_crons, failed_crons, cron_runs = get_cron_summary()
    ll_stats = get_learning_loop_stats()
    new_scripts = get_scripts_created()
    
    # Week-over-week comparison
    last_week_start = start - timedelta(days=7)
    last_week_end = end - timedelta(days=7)
    commits_last_week = get_git_commits_week(last_week_start, last_week_end)
    
    if len(commits_last_week) > 0:
        trend = ((len(commits_week) - len(commits_last_week)) / len(commits_last_week)) * 100
        trend_str = f"+{trend:.0f}%" if trend >= 0 else f"{trend:.0f}%"
    else:
        trend_str = "N/A"
    
    # System status
    all_system_ok = all(c[1] for c in system_checks)
    failed_items = [c for c in system_checks if not c[1]]
    
    if format == 'telegram':
        lines = []
        lines.append(f"📅 **Weekly Review — {week_str}**")
        lines.append(f"📆 {start.strftime('%d.%m')} - {end.strftime('%d.%m.%Y')}")
        lines.append("")
        
        # System Health Summary
        lines.append("**🖥️ SYSTEM:**")
        for name, ok, msg in system_checks:
            emoji = '✅' if ok else '❌'
            lines.append(f"  {emoji} {msg}")
        lines.append("")
        
        # Development
        lines.append("**📊 DEVELOPMENT:**")
        lines.append(f"  • Commits: {len(commits_week)} ({trend_str} vs last week)")
        lines.append(f"  • Scripts Created: {len(new_scripts)}")
        if new_scripts:
            for s in new_scripts[:5]:
                lines.append(f"    - `{s}`")
        lines.append(f"  • Memory Notes: {memory_count} entries, {days_with_notes}/7 days")
        lines.append("")
        
        # KG
        if kg:
            lines.append("**🧠 KNOWLEDGE GRAPH:**")
            lines.append(f"  • {kg['entities']} entities (+new)")
            lines.append(f"  • {kg['relations']} relations")
            lines.append("")
        
        # Learning Loop
        if ll_stats:
            lines.append("**📚 LEARNING LOOP:**")
            lines.append(f"  • Score: {ll_stats.get('score', 'N/A')}")
            lines.append(f"  • Runs: {ll_stats.get('runs', 0)}")
            lines.append("")
        
        # Crons
        lines.append("**⏰ CRONS:**")
        lines.append(f"  • {enabled_crons}/{total_crons} enabled")
        if failed_crons > 0:
            lines.append(f"  • ❌ {failed_crons} failed")
        else:
            lines.append(f"  • ✅ 0 failed")
        lines.append("")
        
        # Commits Summary
        if commits_week:
            lines.append("**🔥 TOP COMMITS:**")
            # Group by day or show top 8
            recent = commits_week[-8:] if len(commits_week) > 8 else commits_week
            for c in recent:
                msg_short = c['msg'][:45] + '…' if len(c['msg']) > 45 else c['msg']
                lines.append(f"  • `{c['hash']}` {msg_short}")
        
        lines.append("")
        lines.append("━" * 20)
        lines.append("🦞 *Sir HazeClaw Weekly*")
        
        return "\n".join(lines)
    
    else:
        lines = []
        lines.append(f"# Weekly Review — {week_str}")
        lines.append(f"\n📆 {start.strftime('%Y-%m-%d')} - {end.strftime('%Y-%m-%d')}")
        lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
        lines.append("\n" + "=" * 50)
        
        # System Health
        lines.append("\n## 🖥️ System Health")
        lines.append("| Check | Status |")
        lines.append("|-------|--------|")
        for name, ok, msg in system_checks:
            emoji = '✅' if ok else '❌'
            lines.append(f"| {name.capitalize()} | {emoji} {msg} |")
        
        # Development
        lines.append("\n## 📊 Development")
        lines.append(f"- Commits this week: {len(commits_week)} ({trend_str} vs last week)")
        lines.append(f"- Scripts Created: {len(new_scripts)}")
        if new_scripts:
            for s in new_scripts:
                lines.append(f"  - {s}")
        lines.append(f"- Memory Notes: {memory_count} entries across {days_with_notes}/7 days")
        
        # KG
        if kg:
            lines.append("\n## 🧠 Knowledge Graph")
            lines.append(f"- Entities: {kg['entities']}")
            lines.append(f"- Relations: {kg['relations']}")
        
        # Learning Loop
        if ll_stats:
            lines.append("\n## 📚 Learning Loop")
            lines.append(f"- Score: {ll_stats.get('score', 'N/A')}")
            lines.append(f"- Total Runs: {ll_stats.get('runs', 0)}")
        
        # Crons
        lines.append("\n## ⏰ Crons")
        lines.append(f"- Enabled: {enabled_crons}/{total_crons}")
        lines.append(f"- Failed: {failed_crons}")
        lines.append(f"- Total Runs Tracked: {cron_runs}")
        
        # Commits
        if commits_week:
            lines.append("\n## 🔥 Commits This Week")
            for c in commits_week:
                lines.append(f"- `{c['hash']}` {c['msg']}")
        
        lines.append("\n" + "=" * 50)
        lines.append("\n*Generated by Sir HazeClaw Weekly Review*")
        
        return "\n".join(lines)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Weekly Review Generator')
    parser.add_argument('--week', help='Week string (e.g., 2026-W15)')
    parser.add_argument('--format', choices=['text', 'telegram'], default='telegram')
    parser.add_argument('--output', help='Output file')
    args = parser.parse_args()
    
    summary = generate_weekly_summary(args.format, args.week)
    
    if args.output:
        Path(args.output).write_text(summary)
        print(f"✅ Weekly Review written to {args.output}")
    else:
        print(summary)

if __name__ == "__main__":
    main()
