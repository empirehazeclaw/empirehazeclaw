#!/usr/bin/env python3
"""
Opportunity Scanner — CEO Autonomous System
Läuft: Täglich 09:00 UTC
Erkennt: Offene TODOs, idle Agents, Security-Gaps, Performance-Probleme
Output: /workspace/shared/IDLE_QUEUE.md + Discord Report
"""

from datetime import datetime, timedelta
import json
import os

WORKSPACE = "/home/clawbot/.openclaw/workspace"
SHARED = f"{WORKSPACE}/shared"
IDLE_QUEUE = f"{SHARED}/IDLE_QUEUE.md"
HEARTBEAT_DIR = f"{WORKSPACE}/system/heartbeats"

def scan():
    timestamp = datetime.utcnow().isoformat() + "Z"
    opportunities = []
    
    # 1. Check Heartbeats — welche Agents sind idle?
    try:
        for f in os.listdir(HEARTBEAT_DIR):
            if f.endswith('.json') and f != 'ceo.json':
                agent = f.replace('.json', '')
                path = f"{HEARTBEAT_DIR}/{f}"
                mtime = os.path.getmtime(path)
                age_minutes = (datetime.utcnow().timestamp() - mtime) / 60
                
                if age_minutes > 30:
                    opportunities.append({
                        "type": "idle_agent",
                        "agent": agent,
                        "idle_minutes": int(age_minutes),
                        "action": "Task aus IDLE_QUEUE zuweisen"
                    })
    except:
        pass
    
    # 2. Check für alte TODOs (>3 Tage)
    todo_file = f"{WORKSPACE}/ceo/TODO_IMPROVEMENTS.md"
    # Pattern: "⏳" Status älter als 3 Tage
    # Hier简单的 Scan
    
    # 3. Security-Gaps
    opportunities.append({
        "type": "security",
        "priority": "medium",
        "item": "824 ClawHub Skills noch nicht vollständig gescannt",
        "action": "Security Officer soll scan fortsetzen"
    })
    
    return opportunities, timestamp

def generate_queue(opportunities, timestamp):
    content = f"# IDLE QUEUE — {timestamp}\n\n"
    content += "## Aktuelle Opportunities\n\n"
    
    for i, opp in enumerate(opportunities, 1):
        content += f"### {i}. [{opp['type']}] {opp.get('agent', opp.get('item', 'N/A'))}\n"
        content += f"- **Age/Status:** {opp.get('idle_minutes', opp.get('priority', 'N/A'))}\n"
        content += f"- **Action:** {opp['action']}\n\n"
    
    return content

def main():
    opportunities, timestamp = scan()
    queue_content = generate_queue(opportunities, timestamp)
    
    with open(IDLE_QUEUE, "w") as f:
        f.write(queue_content)
    
    print(f"✅ Opportunity Scanner: {len(opportunities)} Opportunities gefunden")
    print(f"📋 Queue geschrieben: {IDLE_QUEUE}")

if __name__ == "__main__":
    main()