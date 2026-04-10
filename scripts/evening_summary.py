#!/usr/bin/env python3
"""
Sir HazeClaw Evening Summary
Generiert einen Abend-Zusammenfassung.

Usage:
    python3 evening_summary.py
    python3 evening_summary.py --format telegram
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE_DIR = Path("/home/clawbot/.openclaw/workspace")
MEMORY_DIR = WORKSPACE_DIR / "memory"

def get_today_commits():
    """Holt Git Commits von heute."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "--since='today 00:00'"],
            cwd=WORKSPACE_DIR,
            capture_output=True,
            text=True
        )
        commits = [c for c in result.stdout.strip().split('\n') if c]
        return len(commits), commits
    except:
        return 0, []

def get_today_memory():
    """Holt Memory Notes von heute."""
    today = datetime.now().strftime("%Y-%m-%d")
    note_file = MEMORY_DIR / f"{today}.md"
    
    if note_file.exists():
        content = note_file.read_text()
        return len(content), content[:200]
    return 0, ""

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
    except:
        gateway = False
    
    # Load
    load = os.getloadavg()[0]
    
    # Memory
    mem = psutil.virtual_memory()
    mem_free = f"{100-mem.percent:.0f}%"
    
    # Disk
    disk = psutil.disk_usage('/')
    disk_free = f"{100-disk.percent:.0f}%"
    
    return gateway, load, mem_free, disk_free

def generate_summary(format='text'):
    """Generiert Evening Summary."""
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    
    commits, commit_list = get_today_commits()
    memory_size, memory_preview = get_today_memory()
    gateway, load, mem_free, disk_free = get_system_status()
    
    if format == 'telegram':
        msg = f"""🌙 **Evening Summary — {now.strftime('%H:%M')}**

**System:**
• Gateway: {'✅' if gateway else '❌'}
• Load: {load:.2f}
• Memory: {mem_free} free
• Disk: {disk_free} free

**Heute:**
• {commits} Git Commits
• Memory: {memory_size} chars

"""
        if commit_list:
            msg += "**Letzte Commits:**\n"
            for c in commit_list[-3:]:
                msg += f"• `{c[:8]}` {c[9:]}\n"
        
        msg += """
🦞 Gute Nacht!"""
    else:
        msg = f"""# 🌙 Evening Summary

**{now.strftime('%Y-%m-%d %H:%M')}**

## System
- Gateway: {'OK' if gateway else 'DOWN'}
- Load: {load:.2f}
- Memory: {mem_free} free
- Disk: {disk_free} free

## Heute
- {commits} Git Commits
- Memory: {memory_size} chars

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
    
    parser = argparse.ArgumentParser(description='Evening Summary')
    parser.add_argument('--format', choices=['text', 'telegram'], default='telegram')
    parser.add_argument('--save', action='store_true', help='Save to memory')
    args = parser.parse_args()
    
    summary = generate_summary(args.format)
    print(summary)
    
    if args.save:
        save_to_memory()

if __name__ == "__main__":
    main()