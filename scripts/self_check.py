#!/usr/bin/env python3
"""
Sir HazeClaw Self-Check — IMPROVED
Überprüft System Health, Patterns und Workflow.

Usage:
    python3 self_check.py
"""

import os
import sys
import glob
import socket
import subprocess
from datetime import datetime
from pathlib import Path

# Paths
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
KG_PATH = WORKSPACE / "core_ultralight/memory/knowledge_graph.json"
CRON_PATH = WORKSPACE.parent / "cron/jobs.json"

# Bad patterns to avoid
BAD_PATTERNS = [
    {
        'name': 'Warten nach Zusammenfassung',
        'pattern': 'Ich warte auf deine Antwort',
        'reason': 'Sollte nicht warten, sondern weitermachen'
    },
    {
        'name': 'Annahme nach Sprint',
        'pattern': 'Sprint abgeschlossen - soll ich weitermachen',
        'reason': 'Sollte einfach weitermachen bis Master Stop sagt'
    },
    {
        'name': 'Quality Check vergessen',
        'pattern': 'Script als fertig markiert ohne Test',
        'reason': 'Jedes Script muss getestet werden'
    },
    {
        'name': 'Triviales KG-Füllen',
        'pattern': 'person_nico, skill_loop_detection',
        'reason': 'Nur echtes, nützliches Wissen in KG speichern'
    },
    {
        'name': 'Backup-Paranoia',
        'pattern': 'Backup nach jeder Kleinigkeit',
        'reason': 'Backup NACH wichtigen Änderungen, nicht alle 2 Minuten'
    },
    {
        'name': 'Task-Hopping',
        'pattern': 'Viele kleine Tasks, nichts tief gemacht',
        'reason': 'Eine Aufgabe tief machen, nicht 10 anfangen'
    },
    {
        'name': 'Halbfertige Scripts',
        'pattern': 'Script ohne Test als fertig markiert',
        'reason': '1 perfektes Script > 10 halbfertige'
    }
]

def check_gateway():
    """Check if gateway is responding."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(("127.0.0.1", 18789))
        sock.close()
        return result == 0, "Gateway responding" if result == 0 else "Gateway not responding"
    except:
        return False, "Gateway check failed"

def check_disk():
    """Check disk space."""
    try:
        import psutil
        disk = psutil.disk_usage('/')
        free_pct = 100 - disk.percent
        free_gb = disk.free / (1024**3)
        return free_pct > 15, f"{free_pct:.0f}% free ({free_gb:.1f}GB)"
    except:
        return True, "Disk check skipped"

def check_memory():
    """Check memory usage."""
    try:
        import psutil
        mem = psutil.virtual_memory()
        free_pct = 100 - mem.percent
        return free_pct > 20, f"{free_pct:.0f}% free"
    except:
        return True, "Memory check skipped"

def check_load():
    """Check system load."""
    load = os.getloadavg()[0]
    return load < 4.0, f"{load:.2f}"

def check_kg():
    """Check Knowledge Graph health."""
    if not KG_PATH.exists():
        return False, "KG not found"
    
    try:
        import json
        with open(KG_PATH) as f:
            kg = json.load(f)
        
        entities = len(kg.get('entities', {}))
        relations = len(kg.get('relations', []))
        
        if entities < 10:
            return False, f"KG sparse: {entities} entities"
        
        return True, f"{entities} entities, {relations} relations"
    except Exception as e:
        return False, f"KG error: {e}"

def check_crons():
    """Check cron health."""
    if not CRON_PATH.exists():
        return True, "Cron file not found"
    
    try:
        with open(CRON_PATH) as f:
            import json
            data = json.load(f)
        
        jobs = data.get('jobs', [])
        enabled = [j for j in jobs if j.get('enabled', True)]
        failed = [j for j in enabled if j.get('state', {}).get('lastRunStatus') == 'error']
        
        if failed:
            return False, f"{len(failed)} failed of {len(enabled)} enabled"
        
        return True, f"{len(enabled)}/{len(jobs)} enabled, 0 failed"
    except Exception as e:
        return True, f"Cron check skipped: {e}"

def check_workflow():
    """Check workflow compliance."""
    issues = []
    
    # Check backup/commit ratio
    backup_dir = Path("/home/clawbot/.openclaw/backups")
    today = datetime.now().strftime("%Y%m%d")
    backups_today = sorted(backup_dir.glob(f"backup_{today}_*.tar.gz"))
    
    result = subprocess.run(
        ["git", "log", "--oneline", "--since='today 00:00'", "--format=%H"],
        cwd=str(WORKSPACE),
        capture_output=True,
        text=True,
        timeout=10
    )
    commits = [c for c in result.stdout.strip().split('\n') if c]
    
    # Backup-Paranoia: >5 backups, <3 commits
    if len(backups_today) > 5 and len(commits) < 3:
        issues.append(f"⚠️  Backup-Paranoia: {len(backups_today)} backups, {len(commits)} commits")
    
    # No backup today
    if not backups_today:
        issues.append("⚠️  Kein Backup heute")
    
    # Loop detection: many backups, few commits, low activity
    if len(backups_today) > 8 and len(commits) < 5:
        result2 = subprocess.run(
            ["git", "log", "--oneline", "--since='1 hour ago'"],
            cwd=str(WORKSPACE),
            capture_output=True,
            text=True,
            timeout=10
        )
        recent = [c for c in result2.stdout.strip().split('\n') if c]
        if len(recent) < 2:
            issues.append('⚠️  Loop erkannt: Keine echten Änderungen')
    
    # Check for very few commits (might be stuck)
    if len(commits) < 3:
        issues.append(f"⚠️  Nur {len(commits)} Commits heute")
    
    return issues

def check_patterns():
    """Check if any bad patterns are present."""
    # This would analyze conversation logs
    # For now, just list the patterns to be aware of
    return BAD_PATTERNS

def generate_report():
    """Generate full self-check report."""
    now = datetime.now()
    lines = []
    
    lines.append(f"Sir HazeClaw Self-Check — {now.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append("=" * 60)
    
    # System Health
    lines.append("\n## 🖥️ SYSTEM HEALTH")
    
    gw_ok, gw_msg = check_gateway()
    lines.append(f"  {'✅' if gw_ok else '❌'} Gateway: {gw_msg}")
    
    disk_ok, disk_msg = check_disk()
    lines.append(f"  {'✅' if disk_ok else '⚠️'} Disk: {disk_msg}")
    
    mem_ok, mem_msg = check_memory()
    lines.append(f"  {'✅' if mem_ok else '⚠️'} Memory: {mem_msg}")
    
    load_ok, load_msg = check_load()
    lines.append(f"  {'✅' if load_ok else '⚠️'} Load: {load_msg}")
    
    # Knowledge Graph
    lines.append("\n## 🧠 KNOWLEDGE GRAPH")
    kg_ok, kg_msg = check_kg()
    lines.append(f"  {'✅' if kg_ok else '⚠️'} KG: {kg_msg}")
    
    # Crons
    lines.append("\n## ⏰ CRONS")
    cron_ok, cron_msg = check_crons()
    lines.append(f"  {'✅' if cron_ok else '❌'} Crons: {cron_msg}")
    
    # Workflow
    lines.append("\n## 📋 WORKFLOW")
    workflow_issues = check_workflow()
    if workflow_issues:
        for issue in workflow_issues:
            lines.append(f"  {issue}")
    else:
        lines.append("  ✅ Workflow OK")
    
    # Activity
    lines.append("\n## 📊 ACTIVITY")
    backup_dir = Path("/home/clawbot/.openclaw/backups")
    today = datetime.now().strftime("%Y%m%d")
    backups = sorted(backup_dir.glob(f"backup_{today}_*.tar.gz"))
    
    result = subprocess.run(
        ["git", "log", "--oneline", "--since='today 00:00'"],
        cwd=str(WORKSPACE),
        capture_output=True,
        text=True,
        timeout=10
    )
    commits = [c for c in result.stdout.strip().split('\n') if c]
    
    lines.append(f"  📦 Backups heute: {len(backups)}")
    lines.append(f"  📝 Commits heute: {len(commits)}")
    
    # Bad Patterns (awareness list)
    lines.append("\n## ⚠️ PATTERNS ZU VERMEIDEN")
    for bp in check_patterns()[:4]:  # Show top 4
        lines.append(f"  • {bp['name']}")
    
    lines.append("\n" + "=" * 60)
    
    return "\n".join(lines)

def main():
    report = generate_report()
    print(report)

if __name__ == "__main__":
    main()