#!/usr/bin/env python3
"""
Sir HazeClaw Master System Report
Generiert einen umfassenden System-Report.

Usage:
    python3 system_report.py
    python3 system_report.py --format markdown
"""

import os
import sys
import json
import sqlite3
import psutil
import socket
from datetime import datetime
from pathlib import Path

def check_gateway():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(("127.0.0.1", 18789))
        sock.close()
        return result == 0, "responding" if result == 0 else "DOWN"
    except Exception as e:
        return False, f"ERROR: {e}"

def check_disk():
    usage = psutil.disk_usage('/')
    return usage.percent < 90, f"{100-usage.percent:.0f}% free"

def check_memory():
    mem = psutil.virtual_memory()
    return mem.percent < 90, f"{100-mem.percent:.0f}% free"

def check_load():
    load = os.getloadavg()[0]
    return load < 4.0, f"{load:.2f}"

def check_databases():
    results = []
    for db_name in ['main.sqlite', 'ceo.sqlite', 'data.sqlite']:
        db_path = f"/home/clawbot/.openclaw/memory/{db_name}"
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()[0]
                conn.close()
                results.append((db_name, result == "ok", result))
            except Exception as e:
                results.append((db_name, False, str(e)))
        else:
            results.append((db_name, False, "NOT FOUND"))
    return results

def get_cron_status():
    cron_path = "/home/clawbot/.openclaw/cron/jobs.json"
    if not os.path.exists(cron_path):
        return [], "Cron file not found"
    try:
        with open(cron_path) as f:
            data = json.load(f)
        jobs = data.get('jobs', [])
        return jobs, None
    except Exception as e:
        return [], str(e)

def get_git_commits_today():
    import subprocess
    try:
        result = subprocess.run( 
            ["git", "log", "--oneline", "--since='today 00:00'"], timeout=60,
            cwd="/home/clawbot/.openclaw/workspace",
            capture_output=True,
            text=True
        )
        commits = []
        for line in result.stdout.strip().split('\n'):
            if line:
                commits.append(line)
        return commits
    except:
        return []

def get_backup_status():
    backup_dir = Path("/home/clawbot/.openclaw/backups")
    today = datetime.now().strftime("%Y%m%d")
    backups = list(backup_dir.glob(f"backup_{today}_*.tar.gz"))
    if backups:
        latest = max(backups, key=os.path.getmtime)
        size_mb = os.path.getsize(latest) / (1024*1024)
        return True, f"{latest.name} ({size_mb:.1f}MB)"
    return False, "No backup today"

def generate_report():
    now = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    
    report = f"""# 📊 Sir HazeClaw System Report

**Generated:** {now}

---

## 🖥️ System Health

| Check | Status |
|-------|--------|
"""
    
    # System checks
    gw_ok, gw_msg = check_gateway()
    report += f"| Gateway | {'✅' if gw_ok else '❌'} {gw_msg} |\n"
    
    disk_ok, disk_msg = check_disk()
    report += f"| Disk | {'✅' if disk_ok else '❌'} {disk_msg} |\n"
    
    mem_ok, mem_msg = check_memory()
    report += f"| Memory | {'✅' if mem_ok else '❌'} {mem_msg} |\n"
    
    load_ok, load_msg = check_load()
    report += f"| Load | {'✅' if load_ok else '❌'} {load_msg} |\n"
    
    report += "\n## 🗄️ Databases\n\n"
    db_results = check_databases()
    for name, ok, msg in db_results:
        report += f"| {name} | {'✅' if ok else '❌'} {msg} |\n"
    
    report += "\n## 💾 Backup\n\n"
    backup_ok, backup_msg = get_backup_status()
    report += f"| Server Backup | {'✅' if backup_ok else '❌'} {backup_msg} |\n"
    
    report += "\n## ⏰ Active Crons\n\n"
    jobs, error = get_cron_status()
    if error:
        report += f"❌ Error: {error}\n"
    else:
        enabled = [j for j in jobs if j.get('enabled', True)]
        report += f"Total: {len(jobs)} | Enabled: {len(enabled)}\n\n"
        for job in enabled:
            name = job.get('name', 'unknown')
            schedule = job.get('schedule', {})
            cron_expr = schedule.get('expr', '?')
            state = job.get('state', {})
            last_run = state.get('lastRunStatus', '?')
            
            if last_run == 'ok':
                status = '✅'
            elif last_run == 'error':
                status = '❌'
            else:
                status = '⚠️'
            
            report += f"{status} {name}: {cron_expr}\n"
    
    report += "\n## 📝 Git Commits Today\n\n"
    commits = get_git_commits_today()
    if commits:
        for c in commits[:5]:
            report += f"- `{c[:8]}` {c[9:]}\n"
    else:
        report += "_No commits today_\n"
    
    report += "\n---\n*Sir HazeClaw System Report*\n"
    
    return report

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Sir HazeClaw System Report')
    parser.add_argument('--format', choices=['text', 'markdown'], default='markdown')
    parser.add_argument('--output', help='Output file')
    args = parser.parse_args()
    
    report = generate_report()
    
    if args.output:
        Path(args.output).write_text(report)
        print(f"✅ Report written to {args.output}")
    else:
        print(report)

if __name__ == "__main__":
    main()