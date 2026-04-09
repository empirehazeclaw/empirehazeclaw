#!/usr/bin/env python3
"""
📊 Agent Dashboard - Real-time overview
"""
import os
import json
from datetime import datetime, timedelta

DATA_DIR = "/home/clawbot/.openclaw/workspace/data"
REPORTS_DIR = f"{DATA_DIR}/agent_reports"
HUB_DIR = f"{DATA_DIR}/agent_hub"

def get_agent_status(agent_name):
    """Check last run status"""
    report_file = f"{REPORTS_DIR}/{agent_name}_{datetime.now().strftime('%Y%m%d')}.json"
    if os.path.exists(report_file):
        with open(report_file) as f:
            data = json.load(f)
            return {"status": "✅", "tasks": len(data.get("tasks", []))}
    return {"status": "⏳", "tasks": 0}

def get_messages(agent_name):
    """Check inbox"""
    inbox_file = f"{HUB_DIR}/{agent_name}_inbox.json"
    if os.path.exists(inbox_file):
        with open(inbox_file) as f:
            return json.load(f)
    return []

def show_dashboard():
    agents = ["revenue", "operations", "content", "research", "support"]
    
    print("\n" + "="*60)
    print("🤖 EMPIREHAZECLAW AGENT DASHBOARD")
    print("="*60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("")
    
    # Agent Status
    print("📊 AGENT STATUS:")
    for agent in agents:
        status = get_agent_status(agent)
        print(f"  {status['status']} {agent:12} - {status['tasks']} tasks")
    
    # Messages
    print("")
    print("📬 RECENT MESSAGES:")
    for agent in agents:
        msgs = get_messages(agent)
        if msgs:
            for msg in msgs[-2:]:
                print(f"  → {msg['from']:12} → {msg['to']:12}: {msg['message'][:40]}...")
    
    # Escalations
    esc_file = f"{DATA_DIR}/escalations.json"
    if os.path.exists(esc_file):
        with open(esc_file) as f:
            escalations = json.load(f)
            open_esc = [e for e in escalations if e.get("status") == "open"]
            if open_esc:
                print("")
                print(f"⚠️  ESCALATIONS: {len(open_esc)}")
    
    print("")
    print("="*60)

if __name__ == "__main__":
    show_dashboard()
