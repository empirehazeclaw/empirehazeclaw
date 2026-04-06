#!/usr/bin/env python3
"""
🤖 AUTO-DELEGATE v3 - Autonomous Agent Manager
==============================================
Runs hourly, assigns tasks to OpenClaw agents.
"""

import os
import json
import subprocess
import requests
from datetime import datetime

AGENTS = {
    "dev": "Development & Bug Fixes",
    "researcher": "Research & Analysis",
    "content": "Content Creation",
    "pod": "Print on Demand",
    "social": "Social Media",
    "outreach": "Customer Outreach"
}

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")

def check_openclaw():
    """Check if OpenClaw API is available"""
    try:
        result = subprocess.run(
            ["curl", "-s", "http://127.0.0.1:18789/health"],
            capture_output=True, timeout=3
        )
        return result.returncode == 0
    except:
        return False

def get_curl_command(agent_id, task):
    """Build curl command to spawn agent"""
    return [
        "curl", "-s", "-X", "POST",
        "http://127.0.0.1:18789/api/sessions",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({
            "runtime": "subagent",
            "agentId": agent_id,
            "task": task,
            "mode": "run"
        })
    ]

def run_agent(agent_id, task):
    """Spawn an agent to do a task"""
    try:
        cmd = get_curl_command(agent_id, task)
        result = subprocess.run(cmd, capture_output=True, timeout=10)
        if result.returncode == 0:
            log(f"   ✅ {agent_id} gestartet: {task}")
            return True
        else:
            log(f"   ❌ {agent_id} fehlgeschlagen")
            return False
    except Exception as e:
        log(f"   ❌ {agent_id} Error: {e}")
        return False

def check_services():
    """Check if SaaS services are running"""
    services = {}
    ports = {"trading": 8001, "discord": 8892, "chatbot": 8896}
    for name, port in ports.items():
        try:
            result = subprocess.run(
                ["curl", "-sI", f"http://127.0.0.1:{port}"],
                capture_output=True, timeout=3
            )
            services[name] = "✅" if result.returncode == 0 else "❌"
        except:
            services[name] = "❌"
    return services

def main():
    log("🤖 Auto-Delegate v3 startet...")
    
    # 1. Check Services
    log("📊 Check Services...")
    services = check_services()
    for name, status in services.items():
        log(f"   {name}: {status}")
    
    # 2. Determine task based on hour
    hour = datetime.now().hour
    
    tasks_by_hour = {
        7: [("researcher", "Recherchiere aktuelle AI Trends")],
        8: [("dev", "Check alle Websites auf Fehler")],
        9: [("outreach", "Sende 5 Outreach Emails an potenzielle Kunden")],
        10: [("content", "Erstelle Blog Post für diese Woche")],
        11: [("researcher", "Finde neue Produktideen")],
        12: [("social", "Erstelle Social Media Content")],
        14: [("pod", "Check Etsy Orders und erstelle neues Design")],
        15: [("outreach", "Follow-up mit vorherigen Leads")],
        16: [("dev", "Optimiere Chatbot V2")],
        17: [("content", "Update Website Inhalte")],
        18: [("social", "Post auf Twitter/LinkedIn")],
        19: [("researcher", "Competitor Analysis")],
        20: [("content", "Newsletter vorbereiten")],
    }
    
    # 3. Run tasks for current hour
    if hour in tasks_by_hour:
        log(f"🕐 Hour {hour} - Starte Agenten...")
        for agent_id, task in tasks_by_hour[hour]:
            log(f"   → {agent_id}: {task}")
            run_agent(agent_id, task)
    else:
        # Random task every hour for idle agents
        log(f"🕐 Hour {hour} - Maintenance Task...")
        if hour % 2 == 0:
            run_agent("dev", "Check System Health und Services")
        else:
            run_agent("researcher", "Recherchiere neue KI-Nachrichten")
    
    log("✅ Auto-Delegate fertig!")

if __name__ == "__main__":
    main()
