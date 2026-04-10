#!/usr/bin/env python3
"""
Sir HazeClaw Health Monitor — IMPROVED
Prüft System-Gesundheit und alarmiert bei Problemen.

Usage:
    python3 health_monitor.py [--report]
    python3 health_monitor.py [--check-gateway] [--check-disk] [--check-crons]
"""

import os
import sys
import sqlite3
import json
import psutil
import socket
import subprocess
from datetime import datetime
from pathlib import Path

# Config
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
KG_PATH = WORKSPACE / "core_ultralight/memory/knowledge_graph.json"
CRON_PATH = WORKSPACE.parent / "cron/jobs.json"

GATEWAY_PORT = 18789
GATEWAY_HOST = "127.0.0.1"
DISK_THRESHOLD = 15  # %
MEMORY_THRESHOLD = 85  # %
LOAD_THRESHOLD = 4.0

def check_gateway():
    """Prüft ob Gateway läuft."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((GATEWAY_HOST, GATEWAY_PORT))
        sock.close()
        
        if result == 0:
            return True, "Gateway responding"
        else:
            return False, f"Gateway not responding on port {GATEWAY_PORT}"
    except Exception as e:
        return False, f"Gateway check failed: {e}"

def check_disk():
    """Prüft Disk Space."""
    usage = psutil.disk_usage('/')
    free_pct = 100 - usage.percent
    free_gb = usage.free / (1024**3)
    
    if free_pct < DISK_THRESHOLD:
        return False, f"Disk critically low: {free_pct:.1f}% free ({free_gb:.1f}GB)"
    else:
        return True, f"Disk OK: {free_pct:.1f}% free ({free_gb:.1f}GB)"

def check_memory():
    """Prüft Memory Usage."""
    mem = psutil.virtual_memory()
    free_pct = 100 - mem.percent
    used_gb = mem.used / (1024**3)
    
    if mem.percent > MEMORY_THRESHOLD:
        return False, f"Memory high: {mem.percent:.1f}% used ({used_gb:.1f}GB)"
    else:
        return True, f"Memory OK: {free_pct:.1f}% free"

def check_load():
    """Prüft System Load."""
    load = os.getloadavg()
    
    if load[0] > LOAD_THRESHOLD:
        return False, f"Load high: {load[0]:.2f} (1m), {load[1]:.2f} (5m), {load[2]:.2f} (15m)"
    else:
        return True, f"Load OK: {load[0]:.2f} (1m), {load[1]:.2f} (5m), {load[2]:.2f} (15m)"

def check_kg():
    """Prüft Knowledge Graph Health."""
    if not KG_PATH.exists():
        return False, "KG not found"
    
    try:
        with open(KG_PATH) as f:
            kg = json.load(f)
        
        entities = len(kg.get('entities', {}))
        relations = len(kg.get('relations', []))
        
        if entities < 5:
            return False, f"KG sparse: {entities} entities"
        
        if entities > 100 and relations < entities:
            return True, f"KG OK: {entities} entities, {relations} relations (low connectivity)"
        
        return True, f"KG OK: {entities} entities, {relations} relations"
    except Exception as e:
        return False, f"KG error: {e}"

def check_databases():
    """Prüft Database Integrity."""
    dbs = {
        'main.sqlite': WORKSPACE.parent / 'memory/main.sqlite',
        'ceo.sqlite': WORKSPACE.parent / 'memory/ceo.sqlite',
    }
    
    results = []
    for name, path in dbs.items():
        if not os.path.exists(path):
            results.append((name, False, "DB not found"))
            continue
            
        try:
            conn = sqlite3.connect(str(path))
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            
            # Get size
            size_mb = os.path.getsize(path) / (1024*1024)
            
            # Get table count
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchone()[0]
            
            conn.close()
            
            if result == "ok":
                results.append((name, True, f"OK ({size_mb:.1f}MB, {tables} tables)"))
            else:
                results.append((name, False, f"Integrity issue: {result}"))
        except Exception as e:
            results.append((name, False, f"Error: {e}"))
    
    return results

def check_crons():
    """Prüft Cron Jobs Status."""
    if not CRON_PATH.exists():
        return True, [], "No cron config"
    
    try:
        with open(CRON_PATH) as f:
            data = json.load(f)
        
        jobs = data.get('jobs', [])
        enabled = [j for j in jobs if j.get('enabled', True)]
        failed = [j for j in enabled if j.get('state', {}).get('lastRunStatus') == 'error']
        
        failed_info = []
        for j in failed[:3]:  # Top 3
            failed_info.append(f"{j.get('name', 'unknown')}: {j.get('state', {}).get('lastError', 'unknown error')}")
        
        if failed:
            return False, failed_info, f"{len(failed)} failed of {len(enabled)} enabled"
        
        return True, [], f"{len(enabled)}/{len(jobs)} enabled, 0 failed"
    except Exception as e:
        return True, [], f"Cron check skipped: {e}"

def check_backup():
    """Prüft ob Backups existieren."""
    backup_dir = WORKSPACE.parent / "backups"
    today = datetime.now().strftime("%Y%m%d")
    
    backups_today = list(backup_dir.glob(f"backup_{today}_*.tar.gz"))
    
    if backups_today:
        latest = max(backups_today, key=os.path.getmtime)
        age_mins = (datetime.now().timestamp() - os.path.getmtime(latest)) / 60
        return True, f"{len(backups_today)} today, latest {age_mins:.0f}m ago"
    else:
        return False, "No backup today"

def check_git_activity():
    """Prüft Git Activity."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "--since='today 00:00'", "--format=%H"],
            cwd=str(WORKSPACE),
            capture_output=True,
            text=True,
            timeout=10
        )
        commits = [c for c in result.stdout.strip().split('\n') if c]
        
        if len(commits) < 1:
            return False, f"No commits today"
        
        return True, f"{len(commits)} commits today"
    except:
        return True, "Git check skipped"

def generate_report(format='text'):
    """Generiert vollständigen Health Report."""
    now = datetime.now()
    
    # Run all checks
    gw_ok, gw_msg = check_gateway()
    disk_ok, disk_msg = check_disk()
    mem_ok, mem_msg = check_memory()
    load_ok, load_msg = check_load()
    kg_ok, kg_msg = check_kg()
    db_results = check_databases()
    cron_ok, cron_failed, cron_msg = check_crons()
    backup_ok, backup_msg = check_backup()
    git_ok, git_msg = check_git_activity()
    
    # Overall
    db_all_ok = all(r[1] for r in db_results)
    all_ok = (gw_ok and disk_ok and mem_ok and load_ok and 
              kg_ok and db_all_ok and cron_ok and backup_ok)
    
    if format == 'telegram':
        lines = []
        lines.append(f"🏥 **Health Report — {now.strftime('%H:%M')}**")
        lines.append("")
        
        # System
        lines.append("**🖥️ SYSTEM:**")
        lines.append(f"  Gateway: {'✅' if gw_ok else '❌'} {gw_msg}")
        lines.append(f"  Disk: {'✅' if disk_ok else '❌'} {disk_msg}")
        lines.append(f"  Memory: {'✅' if mem_ok else '❌'} {mem_msg}")
        lines.append(f"  Load: {'✅' if load_ok else '❌'} {load_msg}")
        lines.append("")
        
        # KG
        lines.append("**🧠 KNOWLEDGE GRAPH:**")
        lines.append(f"  {'✅' if kg_ok else '❌'} {kg_msg}")
        lines.append("")
        
        # Databases
        lines.append("**💾 DATABASES:**")
        for name, ok, msg in db_results:
            lines.append(f"  {name}: {'✅' if ok else '❌'} {msg}")
        lines.append("")
        
        # Crons
        lines.append("**⏰ CRONS:**")
        lines.append(f"  {'✅' if cron_ok else '❌'} {cron_msg}")
        if cron_failed:
            for f in cron_failed:
                lines.append(f"    • {f}")
        lines.append("")
        
        # Activity
        lines.append("**📊 ACTIVITY:**")
        lines.append(f"  {'✅' if backup_ok else '⚠️'} {backup_msg}")
        lines.append(f"  {'✅' if git_ok else '⚠️'} {git_msg}")
        lines.append("")
        
        # Overall
        lines.append("━" * 20)
        if all_ok:
            lines.append("✅ **SYSTEM HEALTHY**")
        else:
            lines.append("⚠️ **ISSUES DETECTED**")
        
        return "\n".join(lines)
    
    else:
        lines = []
        lines.append("=" * 50)
        lines.append(f"Sir HazeClaw Health Report — {now.strftime('%Y-%m-%d %H:%M UTC')}")
        lines.append("=" * 50)
        
        lines.append("\n[SYSTEM]")
        lines.append(f"  Gateway: {'✅' if gw_ok else '❌'} {gw_msg}")
        lines.append(f"  Disk:    {'✅' if disk_ok else '❌'} {disk_msg}")
        lines.append(f"  Memory:  {'✅' if mem_ok else '❌'} {mem_msg}")
        lines.append(f"  Load:    {'✅' if load_ok else '❌'} {load_msg}")
        
        lines.append("\n[KNOWLEDGE GRAPH]")
        lines.append(f"  {'✅' if kg_ok else '❌'} {kg_msg}")
        
        lines.append("\n[DATABASES]")
        for name, ok, msg in db_results:
            lines.append(f"  {name}: {'✅' if ok else '❌'} {msg}")
        
        lines.append("\n[CRONS]")
        lines.append(f"  {'✅' if cron_ok else '❌'} {cron_msg}")
        if cron_failed:
            for f in cron_failed:
                lines.append(f"    • {f}")
        
        lines.append("\n[ACTIVITY]")
        lines.append(f"  Backup: {'✅' if backup_ok else '⚠️'} {backup_msg}")
        lines.append(f"  Git: {'✅' if git_ok else '⚠️'} {git_msg}")
        
        lines.append("\n" + "=" * 50)
        if all_ok:
            lines.append("✅ SYSTEM HEALTHY")
        else:
            lines.append("⚠️ ISSUES DETECTED")
        lines.append("=" * 50)
        
        return "\n".join(lines)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Sir HazeClaw Health Monitor - Improved')
    parser.add_argument('--report', action='store_true', help='Full health report')
    parser.add_argument('--format', choices=['text', 'telegram'], default='text')
    parser.add_argument('--check-gateway', action='store_true', help='Check gateway only')
    parser.add_argument('--check-disk', action='store_true', help='Check disk only')
    parser.add_argument('--check-memory', action='store_true', help='Check memory only')
    parser.add_argument('--check-crons', action='store_true', help='Check crons only')
    parser.add_argument('--check-kg', action='store_true', help='Check KG only')
    
    args = parser.parse_args()
    
    if args.check_gateway:
        ok, msg = check_gateway()
        print(f"Gateway: {'✅' if ok else '❌'} {msg}")
    elif args.check_disk:
        ok, msg = check_disk()
        print(f"Disk: {'✅' if ok else '❌'} {msg}")
    elif args.check_memory:
        ok, msg = check_memory()
        print(f"Memory: {'✅' if ok else '❌'} {msg}")
    elif args.check_crons:
        ok, failed, msg = check_crons()
        print(f"Crons: {'✅' if ok else '❌'} {msg}")
        for f in failed:
            print(f"  • {f}")
    elif args.check_kg:
        ok, msg = check_kg()
        print(f"Knowledge Graph: {'✅' if ok else '❌'} {msg}")
    else:
        # Full report
        print(generate_report(args.format))

if __name__ == "__main__":
    main()