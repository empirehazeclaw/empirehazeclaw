#!/usr/bin/env python3
"""
Sir HazeClaw Evening Summary — IMPROVED
Generiert einen Abend-Zusammenfassung mit echten Highlights.

Usage:
    python3 evening_summary.py
    python3 evening_summary.py --format telegram
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

def get_today_commits():
    """Holt Git Commits von heute."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "--since='today 00:00'", "--format=%H %s"],
            cwd=str(WORKSPACE_DIR),
            capture_output=True,
            text=True,
            timeout=10
        )
        commits = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split(' ', 1)
                if len(parts) == 2:
                    commits.append({'hash': parts[0][:8], 'msg': parts[1]})
                else:
                    commits.append({'hash': line[:8], 'msg': ''})
        return len(commits), commits
    except (subprocess.CalledProcessError, OSError, FileNotFoundError):
        # Git command failed - return empty
        return 0, []

def get_yesterday_commits():
    """Holt Git Commits von gestern."""
    try:
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime('%Y-%m-%d')
        result = subprocess.run(
            ["git", "log", "--oneline", f"--since={date_str}T00:00:00Z", f"--until={date_str}T23:59:59Z"],
            cwd=str(WORKSPACE_DIR),
            capture_output=True,
            text=True,
            timeout=10
        )
        return len([c for c in result.stdout.strip().split('\n') if c])
    except (subprocess.CalledProcessError, OSError, FileNotFoundError):
        # Git command failed - return 0
        return 0

def get_today_memory():
    """Holt Memory Notes von heute."""
    today = datetime.now().strftime("%Y-%m-%d")
    note_file = MEMORY_DIR / f"{today}.md"
    
    if note_file.exists():
        content = note_file.read_text()
        lines = [l for l in content.split('\n') if l.strip()]
        return len(content), lines[-5:] if len(lines) > 5 else lines
    return 0, []

def get_kg_today():
    """Holt KG Stats und Änderungen heute."""
    if not KG_PATH.exists():
        return None
    
    try:
        with open(KG_PATH) as f:
            kg = json.load(f)
        
        entities = len(kg.get('entities', {}))
        relations = len(kg.get('relations', []))
        
        return {
            'entities': entities,
            'relations': relations
        }
    except (IOError, json.JSONDecodeError):
        # KG file read or JSON parse failed
        return None

def get_system_status():
    """Holt aktuellen System Status."""
    import psutil
    import socket
    
    # Gateway
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(("127.0.0.1", 18789))
        sock.close()
        gateway = result == 0
    except (OSError, ConnectionError):
        # Socket operations failed
        gateway = False
    
    # Load
    load = os.getloadavg()[0]
    
    # Memory
    mem = psutil.virtual_memory()
    mem_pct = 100 - mem.percent
    
    # Disk
    disk = psutil.disk_usage('/')
    disk_pct = 100 - disk.percent
    
    return {
        'gateway': gateway,
        'load': load,
        'mem_pct': mem_pct,
        'disk_pct': disk_pct
    }

def get_blockers():
    """Liest Blockers aus HEARTBEAT."""
    if not HEARTBEAT_PATH.exists():
        return []
    
    content = HEARTBEAT_PATH.read_text()
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

def get_highlights(commits):
    """Extrahiert Highlights aus Commits."""
    if not commits:
        return []
    
    # Keywords that indicate significant work
    keywords = ['improve', 'fix', 'add', 'create', 'implement', 'update', 'enhance', 'optimize']
    highlights = []
    
    for c in commits[-10:]:  # Last 10 commits
        msg = c.get('msg', '').lower()
        for kw in keywords:
            if kw in msg:
                highlights.append(c)
                break
    
    return highlights[-3:]  # Top 3

def generate_summary(format='text'):
    """Generiert Evening Summary."""
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    
    # Gather data
    commits_today, commit_list = get_today_commits()
    commits_yesterday = get_yesterday_commits()
    memory_size, memory_lines = get_today_memory()
    system = get_system_status()
    kg = get_kg_today()
    blockers = get_blockers()
    highlights = get_highlights(commit_list)
    
    # Calculate trends
    if commits_yesterday > 0:
        trend = ((commits_today - commits_yesterday) / commits_yesterday) * 100
        trend_str = f"+{trend:.0f}%" if trend >= 0 else f"{trend:.0f}%"
    else:
        trend_str = "N/A"
    
    if format == 'telegram':
        msg = f"""🌙 **Evening Summary — {now.strftime('%H:%M')}**

━━━━━━━━━━━━━━━━━━━
**📊 HEUTE**
• {commits_today} Commits ({trend_str} vs gestern: {commits_yesterday})
• Memory: {memory_size} chars"""

        if highlights:
            msg += f"\n\n**🔥 Highlights:**"
            for h in highlights:
                msg += f"\n• `{h['hash']}` {h['msg'][:50]}"

        msg += f"""

━━━━━━━━━━━━━━━━━━━
**🖥️ SYSTEM**
• Gateway: {'✅' if system['gateway'] else '❌'}
• Load: {system['load']:.2f}
• Memory: {system['mem_pct']:.0f}% free
• Disk: {system['disk_pct']:.0f}% free"""

        if kg:
            msg += f"""

━━━━━━━━━━━━━━━━━━━
**🧠 KNOWLEDGE GRAPH**
• {kg['entities']} entities
• {kg['relations']} relations"""

        if blockers:
            msg += f"""

━━━━━━━━━━━━━━━━━━━
**⚠️ AKTIVE BLOCKER**"""
            for b in blockers:
                msg += f"\n• {b}"

        msg += """

━━━━━━━━━━━━━━━━━━━
🦞 Gute Nacht!"""
    
    else:
        msg = f"""# 🌙 Evening Summary — {now.strftime('%Y-%m-%d %H:%M')}

## 📊 Today
| Metric | Value |
|--------|-------|
| Commits | {commits_today} ({trend_str} vs yesterday: {commits_yesterday}) |
| Memory Notes | {memory_size} chars |
"""

        if highlights:
            msg += "### 🔥 Highlights\n"
            for h in highlights:
                msg += f"- `{h['hash']}` {h['msg']}\n"
            msg += "\n"

        msg += f"""## 🖥️ System
| Metric | Status |
|--------|--------|
| Gateway | {'✅ OK' if system['gateway'] else '❌ DOWN'} |
| Load | {system['load']:.2f} |
| Memory | {system['mem_pct']:.0f}% free |
| Disk | {system['disk_pct']:.0f}% free |
"""

        if kg:
            msg += f"""## 🧠 Knowledge Graph
- Entities: {kg['entities']}
- Relations: {kg['relations']}
"""

        if blockers:
            msg += "## ⚠️ Active Blockers\n"
            for b in blockers:
                msg += f"- {b}\n"

        msg += """
---
🦞 Sir HazeClaw"""
    
    return msg

def save_to_memory():
    """Speichert Summary in Memory."""
    today = datetime.now().strftime("%Y-%m-%d")
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    
    note_file = MEMORY_DIR / f"{today}.md"
    summary = generate_summary('text')
    
    with open(note_file, "a") as f:
        f.write(f"\n\n## Evening Summary {datetime.now().strftime('%H:%M')}\n\n")
        f.write(summary)
    
    print(f"✅ Summary saved to {note_file}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Evening Summary - Improved')
    parser.add_argument('--format', choices=['text', 'telegram'], default='telegram')
    parser.add_argument('--save', action='store_true', help='Save to memory')
    args = parser.parse_args()
    
    summary = generate_summary(args.format)
    print(summary)
    
    if args.save:
        save_to_memory()

if __name__ == "__main__":
    main()