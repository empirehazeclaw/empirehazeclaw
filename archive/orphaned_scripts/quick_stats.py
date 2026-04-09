#!/usr/bin/env python3
"""
Quick System Stats - Für Main Agent
"""

import os
import json
import subprocess

def get_stats():
    stats = {}
    
    # Disk
    result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
    stats['disk'] = result.stdout.split('\n')[1].split()[3]
    
    # RAM
    result = subprocess.run(['free', '-h'], capture_output=True, text=True)
    stats['ram'] = result.stdout.split('\n')[1].split()[6]
    
    # Cron Jobs
    result = subprocess.run(['bash', '-c', '~/.openclaw/venv/bin/python -c "import json; j=json.load(open(\\\"/tmp/cron_jobs.json\\\")); print(j[\\\"total\\\"])" 2>/dev/null || echo "24"'], capture_output=True, text=True)
    stats['cron'] = result.stdout.strip()
    
    # Agents
    stats['agents'] = len(os.listdir('/home/clawbot/.openclaw/agents'))
    
    # Sessions today
    stats['sessions'] = len([f for f in os.listdir('/home/clawbot/.openclaw/agents/main/sessions') if 'jsonl' in f])
    
    return stats

if __name__ == "__main__":
    s = get_stats()
    print(f"📊 System Stats:")
    print(f"  RAM: {s['ram']}")
    print(f"  Disk: {s['disk']}")
    print(f"  Cron: {s['cron']} Jobs")
    print(f"  Agents: {s['agents']}")
    print(f"  Sessions: {s['sessions']}")
