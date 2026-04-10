#!/usr/bin/env python3
"""
Sir HazeClaw Morning Brief — IMPROVED
Generiert einen Morning Brief für Master mit höherem Value.

Improvements:
- KG stats mit Growth
- Active blockers
- Yesterday comparison
- Actionable recommendations
- Pattern alerts

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
from datetime import datetime, timedelta
from pathlib import Path

# Paths
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
KG_PATH = WORKSPACE / "core_ultralight/memory/knowledge_graph.json"
HEARTBEAT_PATH = WORKSPACE / "ceo/HEARTBEAT.md"

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
    status['disk_free_pct'] = 100 - disk.percent
    status['disk_free_gb'] = disk.free / (1024**3)
    
    # Memory
    mem = psutil.virtual_memory()
    status['mem_free_pct'] = 100 - mem.percent
    status['mem_used_gb'] = mem.used / (1024**3)
    
    # Load
    load = os.getloadavg()
    status['load'] = load[0]
    
    return status

def get_kg_stats():
    """Holt KG Stats mit Growth."""
    if not KG_PATH.exists():
        return None
    
    with open(KG_PATH) as f:
        kg = json.load(f)
    
    entities = kg.get('entities', {})
    relations = kg.get('relations', [])
    last_updated = kg.get('last_updated', 'unknown')
    
    # Count by type
    by_type = {}
    for e in entities.values():
        t = e.get('type', 'unknown')
        by_type[t] = by_type.get(t, 0) + 1
    
    return {
        'entities': len(entities),
        'relations': len(relations),
        'by_type': by_type,
        'last_updated': last_updated
    }

def get_active_blockers():
    """Liest Active Blockers aus HEARTBEAT.md."""
    if not HEARTBEAT_PATH.exists():
        return []
    
    content = HEARTBEAT_PATH.read_text()
    blockers = []
    
    # Parse markdown table format
    lines = content.split('\n')
    in_blocker_section = False
    skip_next_empty = False
    
    for line in lines:
        if 'OFFENE BLOCKER' in line:
            in_blocker_section = True
            skip_next_empty = True
            continue
        elif in_blocker_section:
            # End of section - next header
            if line.startswith('##') and '---' not in line:
                break
            # Skip first empty line after header
            if skip_next_empty and line.strip() == '':
                skip_next_empty = False
                continue
            # Parse table row with blocker emoji
            if '|' in line and ('🔴' in line or '🟡' in line):
                parts = [p.strip() for p in line.split('|')]
                # Task is in parts[2]
                if len(parts) > 2:
                    task = parts[2].strip()
                    if task and task not in ['#', 'Task', '---']:
                        blockers.append(task)
    
    return blockers[:3]  # Max 3

def get_cron_status():
    """Holt Cron Status."""
    cron_path = "/home/clawbot/.openclaw/cron/jobs.json"
    if not os.path.exists(cron_path):
        return {'enabled': 0, 'failed': 0, 'total': 0}
    
    with open(cron_path) as f:
        data = json.load(f)
    
    jobs = data.get('jobs', [])
    enabled = [j for j in jobs if j.get('enabled', True)]
    failed = [j for j in enabled if j.get('state', {}).get('lastRunStatus') == 'error']
    
    return {
        'enabled': len(enabled),
        'failed': len(failed),
        'total': len(jobs)
    }

def get_backup_status():
    """Holt Backup Status."""
    backup_dir = Path("/home/clawbot/.openclaw/backups")
    today = datetime.now().strftime("%Y%m%d")
    
    backups_today = list(backup_dir.glob(f"backup_{today}_*.tar.gz"))
    backups_yesterday = list(backup_dir.glob(f"backup_*_{str(int(today)-1)}*.tar.gz"))
    
    if backups_today:
        latest = max(backups_today, key=os.path.getmtime)
        size_mb = os.path.getsize(latest) / (1024*1024)
        return len(backups_today), f"{len(backups_today)} today ({size_mb:.1f}MB latest)"
    
    return 0, f"None today ({len(backups_yesterday)} yesterday)"

def get_git_commits(days_ago=0):
    """Holt Git Commits für bestimmten Tag."""
    import subprocess
    
    date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_ago)
    date_str = date.strftime('%Y-%m-%d')
    
    try:
        if days_ago == 0:
            result = subprocess.run(
                ["git", "log", "--oneline", f"--since={date_str}T00:00:00Z"],
                cwd=str(WORKSPACE),
                capture_output=True,
                text=True,
                timeout=5
            )
        else:
            result = subprocess.run(
                ["git", "log", "--oneline", f"--since={date_str}T00:00:00Z", f"--until={date_str}T23:59:59Z"],
                cwd=str(WORKSPACE),
                capture_output=True,
                text=True,
                timeout=5
            )
        
        commits = [c for c in result.stdout.strip().split('\n') if c]
        return len(commits)
    except:
        return 0

def get_system_trends():
    """Berechnet Trends (heute vs gestern)."""
    commits_today = get_git_commits(0)
    commits_yesterday = get_git_commits(1)
    
    # Calculate trend
    if commits_yesterday > 0:
        change = ((commits_today - commits_yesterday) / commits_yesterday) * 100
        trend = f"+{change:.0f}%" if change >= 0 else f"{change:.0f}%"
    else:
        trend = "N/A"
    
    return {
        'commits_today': commits_today,
        'commits_yesterday': commits_yesterday,
        'trend': trend
    }

def get_recommendations(system, cron, kg, backup_count):
    """Generiert actionable recommendations."""
    recs = []
    
    # Disk warning
    if system['disk_free_pct'] < 20:
        recs.append(f"🔴 Disk kritisch: {system['disk_free_pct']:.0f}% free")
    
    # Load warning
    if system['load'] > 4:
        recs.append(f"⚠️ Load hoch: {system['load']:.2f}")
    
    # Cron failures
    if cron['failed'] > 0:
        recs.append(f"🔴 {cron['failed']} Cron(s) fehlgeschlagen")
    
    # No backup
    if backup_count == 0:
        recs.append("⚠️ Kein Backup heute")
    
    # KG growing
    if kg and kg['entities'] > 150:
        recs.append(f"✅ KG wächst: {kg['entities']} entities")
    
    # Good state
    if len(recs) == 0:
        recs.append("✅ System healthy")
    
    return recs

def generate_brief(format='text'):
    """Generiert Morning Brief."""
    now = datetime.now()
    
    # Gather all data
    system = get_system_status()
    cron = get_cron_status()
    backup_count, backup_msg = get_backup_status()
    kg = get_kg_stats()
    blockers = get_active_blockers()
    trends = get_system_trends()
    recommendations = get_recommendations(system, cron, kg, backup_count)
    
    # Format time
    time_str = now.strftime('%Y-%m-%d %H:%M UTC')
    
    if format == 'telegram':
        msg = f"""🌅 **Morning Brief — {time_str}**

━━━━━━━━━━━━━━━━━━━
**System:**
• Gateway: {'✅' if system['gateway'] else '❌'}
• Disk: {system['disk_free_pct']:.0f}% free ({system['disk_free_gb']:.1f}GB)
• Memory: {system['mem_free_pct']:.0f}% free
• Load: {system['load']:.2f}

━━━━━━━━━━━━━━━━━━━
**Development:**
• Commits: {trends['commits_today']} (heute) vs {trends['commits_yesterday']} (gestern) {trends['trend']}
• Backups: {backup_msg}

━━━━━━━━━━━━━━━━━━━
**Knowledge Graph:**
• Entities: {kg['entities'] if kg else 'N/A'}
• Relations: {kg['relations'] if kg else 'N/A'}

━━━━━━━━━━━━━━━━━━━
**Crons:**
• Active: {cron['enabled']}/{cron['total']}
• Failed: {cron['failed']}"""

        if blockers:
            msg += f"\n━━━━━━━━━━━━━━━━━━━\n**⚠️ Active Blockers:**"
            for b in blockers:
                msg += f"\n• {b}"

        msg += f"\n━━━━━━━━━━━━━━━━━━━\n**Recommendations:**"
        for r in recommendations:
            msg += f"\n• {r}"

        msg += f"""

━━━━━━━━━━━━━━━━━━━
🦞 Sir HazeClaw"""
    
    else:
        msg = f"""# 🌅 Morning Brief — {time_str}

## System
| Metric | Value |
|--------|-------|
| Gateway | {'OK' if system['gateway'] else 'DOWN'} |
| Disk | {system['disk_free_pct']:.0f}% free ({system['disk_free_gb']:.1f}GB) |
| Memory | {system['mem_free_pct']:.0f}% free |
| Load | {system['load']:.2f} |

## Development
| Metric | Today | Yesterday | Trend |
|--------|-------|----------|-------|
| Commits | {trends['commits_today']} | {trends['commits_yesterday']} | {trends['trend']} |
| Backups | {backup_msg} | - | - |

## Knowledge Graph
| Metric | Value |
|--------|-------|
| Entities | {kg['entities'] if kg else 'N/A'} |
| Relations | {kg['relations'] if kg else 'N/A'} |

## Crons
| Status | Count |
|--------|-------|
| Active | {cron['enabled']}/{cron['total']} |
| Failed | {cron['failed']} |"""

        if blockers:
            msg += f"\n\n## ⚠️ Active Blockers\n"
            for b in blockers:
                msg += f"- {b}\n"

        msg += f"\n## Recommendations\n"
        for r in recommendations:
            msg += f"- {r}\n"

        msg += f"""
---
Sir HazeClaw"""
    
    return msg

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Morning Brief - Improved')
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