#!/usr/bin/env python3
"""
Sir HazeClaw Daily Summary Generator — IMPROVED
Erstellt eine tägliche Zusammenfassung der Aktivitäten.

Usage:
    python3 daily_summary.py
    python3 daily_summary.py --date 2026-04-10
    python3 daily_summary.py --format telegram
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

def get_git_commits(days_ago=0):
    """Holt Git Commits für bestimmten Tag."""
    import subprocess
    
    if days_ago == 0:
        date_str = datetime.now().strftime('%Y-%m-%d')
        result = subprocess.run(
            ["git", "log", "--oneline", f"--since={date_str}T00:00:00Z", "--format=%H %s"],
            cwd=str(WORKSPACE),
            capture_output=True,
            text=True,
            timeout=10
        )
    else:
        date = datetime.now() - timedelta(days=days_ago)
        date_str = date.strftime('%Y-%m-%d')
        result = subprocess.run(
            ["git", "log", "--oneline", f"--since={date_str}T00:00:00Z", f"--until={date_str}T23:59:59Z", "--format=%H %s"],
            cwd=str(WORKSPACE),
            capture_output=True,
            text=True,
            timeout=10
        )
    
    commits = []
    for line in result.stdout.strip().split('\n'):
        if line:
            parts = line.split(' ', 1)
            if len(parts) == 2:
                commits.append({"hash": parts[0][:8], "msg": parts[1]})
    return commits

def get_memory_notes_today():
    """Holt Memory Notes von heute."""
    today = datetime.now().strftime("%Y-%m-%d")
    notes_file = MEMORY_DIR / f"{today}.md"
    
    if notes_file.exists():
        content = notes_file.read_text()
        lines = [l for l in content.split('\n') if l.strip()]
        return len(content), lines[-5:] if len(lines) > 5 else lines
    return 0, []

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
    except (OSError, ConnectionError):
        # Socket operations failed
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
    try:
        load = os.getloadavg()[0]
        checks.append(('load', load < 4.0, f"Load {load:.2f}"))
    except (OSError, AttributeError):
        # getloadavg not available on this platform
        checks.append(('load', True, "Load N/A"))
    checks.append(('load', load < 4.0, f"Load {load:.2f}"))
    
    return checks

def get_cron_summary():
    """Holt Cron Zusammenfassung."""
    if not CRON_PATH.exists():
        return 0, 0, 0
    
    with open(CRON_PATH) as f:
        data = json.load(f)
    
    jobs = data.get('jobs', [])
    enabled = [j for j in jobs if j.get('enabled', True)]
    failed = [j for j in enabled if j.get('state', {}).get('lastRunStatus') == 'error']
    
    return len(jobs), len(enabled), len(failed)

def get_backup_summary():
    """Holt Backup Zusammenfassung."""
    backup_dir = WORKSPACE.parent / "backups"
    today = datetime.now().strftime("%Y%m%d")
    backups_today = list(backup_dir.glob(f"backup_{today}_*.tar.gz"))
    
    return len(backups_today)

def get_blockers():
    """Liest Blockers aus HEARTBEAT."""
    heartbeat = CEO_DIR / "HEARTBEAT.md"
    if not heartbeat.exists():
        return []
    
    content = heartbeat.read_text()
    blockers = []
    
    lines = content.split('\n')
    in_blocker = False
    
    for line in lines:
        if 'OFFENE BLOCKER' in line:
            in_blocker = True
            continue
        elif in_blocker:
            if line.startswith('##') and '---' not in line:
                break
            if '|' in line and ('🔴' in line or '🟡' in line):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) > 2:
                    task = parts[2].strip()
                    if task and task not in ['#', 'Task', '---']:
                        blockers.append(task)
    
    return blockers[:3]

def generate_summary(format='text'):
    """Generiert täglichen Summary."""
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    
    # Gather data
    commits_today = get_git_commits(0)
    commits_yesterday = get_git_commits(1)
    memory_size, memory_lines = get_memory_notes_today()
    kg = get_kg_stats()
    system_checks = get_system_health()
    total_crons, enabled_crons, failed_crons = get_cron_summary()
    backups_today = get_backup_summary()
    blockers = get_blockers()
    
    # Trends
    if len(commits_yesterday) > 0:
        trend = ((len(commits_today) - len(commits_yesterday)) / len(commits_yesterday)) * 100
        trend_str = f"+{trend:.0f}%" if trend >= 0 else f"{trend:.0f}%"
    else:
        trend_str = "N/A"
    
    # System status
    all_system_ok = all(c[1] for c in system_checks)
    
    if format == 'telegram':
        lines = []
        lines.append(f"📅 **Daily Summary — {today_str}**")
        lines.append("")
        
        # System Health
        lines.append("**🖥️ SYSTEM:**")
        for name, ok, msg in system_checks:
            emoji = '✅' if ok else '❌'
            lines.append(f"  {emoji} {msg}")
        lines.append("")
        
        # Development
        lines.append("**📊 DEVELOPMENT:**")
        lines.append(f"  • Commits: {len(commits_today)} ({trend_str} vs yesterday: {len(commits_yesterday)})")
        lines.append(f"  • Backups: {backups_today}")
        lines.append(f"  • Memory: {memory_size} chars")
        lines.append("")
        
        # KG
        if kg:
            lines.append("**🧠 KNOWLEDGE GRAPH:**")
            lines.append(f"  • {kg['entities']} entities")
            lines.append(f"  • {kg['relations']} relations")
            lines.append("")
        
        # Crons
        lines.append("**⏰ CRONS:**")
        lines.append(f"  • {enabled_crons}/{total_crons} enabled")
        if failed_crons > 0:
            lines.append(f"  • ❌ {failed_crons} failed")
        else:
            lines.append(f"  • ✅ 0 failed")
        lines.append("")
        
        # Blockers
        if blockers:
            lines.append("**⚠️ BLOCKERS:**")
            for b in blockers:
                lines.append(f"  • {b}")
            lines.append("")
        
        # Highlights
        if commits_today:
            lines.append("**🔥 TOP COMMITS:**")
            for c in commits_today[-5:]:
                msg_short = c['msg'][:50] + '...' if len(c['msg']) > 50 else c['msg']
                lines.append(f"  • `{c['hash']}` {msg_short}")
        
        lines.append("")
        lines.append("━" * 20)
        lines.append("🦞 *Sir HazeClaw*")
        
        return "\n".join(lines)
    
    else:
        lines = []
        lines.append(f"# Daily Summary — {today_str}")
        lines.append(f"\nGenerated: {now.strftime('%Y-%m-%d %H:%M UTC')}")
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
        lines.append(f"- Commits: {len(commits_today)} ({trend_str} vs yesterday: {len(commits_yesterday)})")
        lines.append(f"- Backups: {backups_today}")
        lines.append(f"- Memory: {memory_size} chars")
        
        # KG
        if kg:
            lines.append("\n## 🧠 Knowledge Graph")
            lines.append(f"- Entities: {kg['entities']}")
            lines.append(f"- Relations: {kg['relations']}")
        
        # Crons
        lines.append("\n## ⏰ Crons")
        lines.append(f"- Enabled: {enabled_crons}/{total_crons}")
        lines.append(f"- Failed: {failed_crons}")
        
        # Blockers
        if blockers:
            lines.append("\n## ⚠️ Blockers")
            for b in blockers:
                lines.append(f"- {b}")
        
        # Top Commits
        if commits_today:
            lines.append("\n## 🔥 Top Commits")
            for c in commits_today[-5:]:
                lines.append(f"- `{c['hash']}` {c['msg']}")
        
        lines.append("\n" + "=" * 50)
        lines.append("\n*Generated by Sir HazeClaw*")
        
        return "\n".join(lines)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Daily Summary Generator - Improved')
    parser.add_argument('--date', help='Date (YYYY-MM-DD)')
    parser.add_argument('--format', choices=['text', 'telegram'], default='text')
    parser.add_argument('--output', help='Output file')
    args = parser.parse_args()
    
    summary = generate_summary(args.format)
    
    if args.output:
        Path(args.output).write_text(summary)
        print(f"✅ Summary written to {args.output}")
    else:
        print(summary)

if __name__ == "__main__":
    main()