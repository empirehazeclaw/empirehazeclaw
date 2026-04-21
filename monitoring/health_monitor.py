#!/usr/bin/env python3
"""
System Health Monitor
Sendet Alerts bei Problemen
"""

import os
import sys
import requests
import subprocess
from datetime import datetime
from pathlib import Path

# Learnings Service
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
sys.path.insert(0, str(WORKSPACE / 'SCRIPTS/automation'))
try:
    from learnings_service import LearningsService
except:
    LearningsService = None

TELEGRAM_CHAT_ID = "5392634979"
TELEGRAM_TOKEN = "8397732232:AAEK9VmvNz1gtlBfeiogP8_bDIFWnfZq-HM"

def send_alert(message, urgent=False):
    """Send Telegram Alert"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    emoji = "🚨" if urgent else "⚠️"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"{emoji} *System Alert*\n\n{message}",
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=data, timeout=10)
    except:
        pass

def check_gateway():
    """Prüfe ob Gateway läuft"""
    try:
        result = subprocess.run(
            ["curl", "-s", "localhost:18789/status"],
            capture_output=True, timeout=5
        )
        return result.returncode == 0
    except:
        return False

def check_disk():
    """Prüfe Disk Space"""
    result = subprocess.run(
        ["df", "-h", "/"],
        capture_output=True, text=True, timeout=5
    )
    line = result.stdout.split("\n")[1]
    used = int(line.split()[4].replace("%", ""))
    return used < 90  # OK wenn unter 90%

def check_cron():
    """Prüfe Cron Jobs"""
    try:
        result = subprocess.run(
            ["/home/clawbot/.npm-global/bin/openclaw", "cron", "status"],
            capture_output=True, timeout=10
        )
        return "error" not in result.stdout.lower()
    except:
        return True  # Assume OK if can't check

def record_health_learning(issue: str, alert_sent: bool):
    """Record health-related learnings and share with all agents."""
    if not LearningsService:
        return
    try:
        ls = LearningsService()
        
        # Record the learning
        category = "health_issue" if not alert_sent else "health_alert"
        outcome = "resolved" if not alert_sent else "alert_sent"
        
        ls.record_learning(
            source="Health Monitor",
            category=category,
            learning=issue,
            context="system_health",
            outcome=outcome
        )
        
        # Share with all agents via federation
        for target_agent in ["Ralph Learning", "Capability Evolver", "Meta Learning", "Sir HazeClaw"]:
            ls.record_cross_agent_learning(
                source_agent="Health Monitor",
                target_agent=target_agent,
                category=category,
                learning=issue,
                context="system_health"
            )
        
    except Exception as e:
        print(f"Warning: Failed to record health learning: {e}")

def run_health_check():
    """Haupt-Check"""
    issues = []
    
    # Gateway
    if not check_gateway():
        issues.append("Gateway nicht erreichbar!")
        record_health_learning("Gateway down detected", alert_sent=True)
    
    # Disk
    if not check_disk():
        issues.append("Disk über 90%!")
        record_health_learning("Disk space > 90%", alert_sent=True)
    
    # Cron (nur wichtige)
    # Hier könnten wir mehr Checks machen
    
    if issues:
        msg = "\n".join(issues)
        send_alert(msg, urgent=True)
        print(f"ALERT: {msg}")
    else:
        record_health_learning("Health check passed", alert_sent=False)
        print(f"✅ Alles OK - {datetime.now().isoformat()}")

if __name__ == "__main__":
    run_health_check()
