#!/usr/bin/env python3
"""
Sir HazeClaw Morning Brief
Generiert einen Morning Brief für Master.

Usage:
    python3 morning_brief.py
    python3 morning_brief.py --format telegram
"""

import os
import sys
import json
import sqlite3
import psutil
import socket
from datetime import datetime
from pathlib import Path

def get_system_status():
    """Holt System Status."""
    status = {}
    
    # Gateway
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(("127.0.0.1", 18789))
        sock.close()
        status['gateway'] = result == 0
    except:
        status['gateway'] = False
    
    # Disk
    disk = psutil.disk_usage('/')
    status['disk_free'] = f"{100-disk.percent:.0f}%"
    
    # Memory
    mem = psutil.virtual_memory()
    status['mem_free'] = f"{100-mem.percent:.0f}%"
    
    # Load
    status['load'] = os.getloadavg()[0]
    
    return status

def get_cron_status():
    """Holt Cron Status."""
    cron_path = "/home/clawbot/.openclaw/cron/jobs.json"
    if not os.path.exists(cron_path):
        return {}, "Cron not found"
    
    with open(cron_path) as f:
        data = json.load(f)
    
    jobs = data.get('jobs', [])
    enabled = [j for j in jobs if j.get('enabled', True)]
    
    # Check for failed crons
    failed = []
    for job in enabled:
        state = job.get('state', {})
        if state.get('lastRunStatus') == 'error':
            failed.append(job.get('name', 'unknown'))
    
    return {'enabled': len(enabled), 'failed': len(failed)}, None

def get_backup_status():
    """Holt Backup Status."""
    backup_dir = Path("/home/clawbot/.openclaw/backups")
    today = datetime.now().strftime("%Y%m%d")
    backups = list(backup_dir.glob(f"backup_{today}_*.tar.gz"))
    
    if backups:
        latest = max(backups, key=os.path.getmtime)
        size_mb = os.path.getsize(latest) / (1024*1024)
        return True, f"{latest.name} ({size_mb:.1f}MB)"
    
    # Check yesterday
    yesterday = (datetime.now().replace(hour=0, minute=0, second=0)).strftime("%Y%m%d")
    backups = list(backup_dir.glob(f"backup_{yesterday}_*.tar.gz"))
    if backups:
        return True, f"Yesterday only"
    
    return False, "No backup today"

def get_git_commits_today():
    """Holt Git Commits von heute."""
    import subprocess
    
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    date_str = today.strftime('%Y-%m-%d')
    
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", f"--since={date_str}T00:00:00Z"],
            cwd="/home/clawbot/.openclaw/workspace",
            capture_output=True,
            text=True,
            timeout=5
        )
        commits = [c for c in result.stdout.strip().split('\n') if c]
        return len(commits)
    except:
        return 0

def get_git_commits_yesterday():
    """Holt Git Commits von gestern."""
    import subprocess
    from datetime import timedelta
    
    yesterday = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    date_str = yesterday.strftime('%Y-%m-%d')
    
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", f"--since={date_str}T00:00:00Z", f"--until={date_str}T23:59:59Z"],
            cwd="/home/clawbot/.openclaw/workspace",
            capture_output=True,
            text=True,
            timeout=5
        )
        commits = [c for c in result.stdout.strip().split('\n') if c]
        return len(commits)
    except:
        return 0

def generate_brief(format='text'):
    """Generiert Morning Brief."""
    now = datetime.now()
    
    system = get_system_status()
    cron, cron_error = get_cron_status()
    backup_ok, backup_msg = get_backup_status()
    commits_today = get_git_commits_today()
    commits_yesterday = get_git_commits_yesterday()
    
    if format == 'telegram':
        msg = f"""🌅 **Morning Brief — {now.strftime('%Y-%m-%d %H:%M')}**

**System:**
• Gateway: {'✅' if system['gateway'] else '❌'}
• Disk: {system['disk_free']} free
• Memory: {system['mem_free']} free
• Load: {system['load']:.2f}

**Crons:**
• Active: {cron.get('enabled', '?')}
• Failed: {cron.get('failed', 0)}

**Backup:**
• {'✅' if backup_ok else '❌'} {backup_msg}

**Commits:**
• Heute: {commits_today}
• Gestern: {commits_yesterday}

---
🦞 Sir HazeClaw"""
    else:
        msg = f"""# 🌅 Morning Brief

**{now.strftime('%Y-%m-%d %H:%M')}**

## System
- Gateway: {'OK' if system['gateway'] else 'DOWN'}
- Disk: {system['disk_free']} free
- Memory: {system['mem_free']} free
- Load: {system['load']:.2f}

## Crons
- Active: {cron.get('enabled', '?')}
- Failed: {cron.get('failed', 0)}

## Backup
- {backup_msg}

## Commits
- Heute: {commits_today}
- Gestern: {commits_yesterday}

---
Sir HazeClaw"""
    
    return msg

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Morning Brief')
    parser.add_argument('--format', choices=['text', 'telegram'], default='telegram')
    parser.add_argument('--output', help='Output file')
    args = parser.parse_args()
    
    brief = generate_brief(args.format)
    
    if args.output:
        Path(args.output).write_text(brief)
        print(f"✅ Brief written to {args.output}")
    else:
        print(brief)

if __name__ == "__main__":
    main()