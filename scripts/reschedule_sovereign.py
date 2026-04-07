#!/usr/bin/env python3
"""
Phoenix Automation — Self-Rescheduling for Sovereign Agents
=========================================================

This script automatically reschedules Sovereign Agent jobs for the next day
after a successful task completion.

Usage:
    python3 reschedule_sovereign.py <agent_name> <report_file.json>
    
Example:
    python3 reschedule_sovereign.py security /home/clawbot/.../task_reports/security_daily.json

The script:
1. Reads the task report to determine status
2. If status == "done" → schedules next day at same time
3. If status == "warning" → schedules follow-up in 4 hours
4. If status == "error" → schedules retry in 2 hours
"""

import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Agent configurations — adjust times as needed
AGENT_CONFIGS = {
    "security": {
        "script": "DU BIST DER SOVEREIGN SECURITY OFFICER.\n\nSTARTE DEINE TÄGLICHE SECURITY MISSION:\n\n1. LIES DEINE SOUL.md: cat /home/clawbot/.openclaw/workspace/security/SOUL.md\n2. ARBEITSVERZEICHNIS: cd /home/clawbot/.openclaw/workspace/security\n3. FÜHRE SECURITY AUDIT DURCH:\n   - Scanne nach neuen API Keys / Secrets\n   - Prüfe /home/clawbot/.openclaw/secrets/SECURITY_ROTATION.md Status\n   - Prüfe offene Security-Probleme\n   - .gitignore PRÜFEN: cat /home/clawbot/.openclaw/workspace/.gitignore (RICHTIGER PFAD!)\n4. SCHREIBE ERGEBNIS NACH: /home/clawbot/.openclaw/workspace/ceo/task_reports/security_daily.json\n\nDas JSON muss haben:\n{\n  \"agent\": \"security_officer\",\n  \"timestamp\": \"ISO8601\",\n  \"status\": \"done|warning|error\",\n  \"findings\": [...],\n  \"next_actions\": [...]\n}\n\nABSCHLIESSEND: Sende keine Nachricht. Schreibe nur die Datei.",
        "report": "security_daily.json",
        "schedule_hour": 10,
        "schedule_minute": 0,
    },
    "data": {
        "script": "DU BIST DER SOVEREIGN DATA MANAGER.\n\nSTARTE DEINE TÄGLICHE DATA MISSION:\n\n1. LIES DEINE SOUL.md: cat /home/clawbot/.openclaw/workspace/memory/SOUL.md\n2. ARBEITSVERZEICHNIS: cd /home/clawbot/.openclaw/workspace/memory\n3. FÜHRE DATA CHECK DURCH:\n   - Prüfe MEMORY.md Größe (>500KB? → Komprimieren)\n   - Prüfe memory/archive/完整性\n   - Prüfe neue Dokumentation im /skills/ Verzeichnis\n4. SCHREIBE ERGEBNIS NACH: /home/clawbot/.openclaw/workspace/ceo/task_reports/data_daily.json\n\nDas JSON muss haben:\n{\n  \"agent\": \"data_manager\",\n  \"timestamp\": \"ISO8601\",\n  \"status\": \"done|warning|error\",\n  \"memory_size_kb\": NNN,\n  \"findings\": [...],\n  \"next_actions\": [...]\n}\n\nABSCHLIESSEND: Sende keine Nachricht. Schreibe nur die Datei.",
        "report": "data_daily.json",
        "schedule_hour": 11,
        "schedule_minute": 30,
    },
    "builder": {
        "script": "DU BIST DER SOVEREIGN BUILDER.\n\nSTARTE DEINE TÄGLICHE BUILDER MISSION:\n\n1. LIES DEINE SOUL.md: cat /home/clawbot/.openclaw/workspace/builder/SOUL.md\n2. ARBEITSVERZEICHNIS: cd /home/clawbot/.openclaw/workspace/builder\n3. FÜHRE BUILDER CHECK DURCH:\n   - Prüfe Workspace auf verwaiste Files\n   - Prüfe offene TODOs / Issues\n   - Prüfe /home/clawbot/.openclaw/workspace/todos/MASTER_TODO.md\n   - System-Gesundheitscheck (Gateway, Backups)\n4. SCHREIBE ERGEBNIS NACH: /home/clawbot/.openclaw/workspace/ceo/task_reports/builder_daily.json\n\nDas JSON muss haben:\n{\n  \"agent\": \"builder\",\n  \"timestamp\": \"ISO8601\",\n  \"status\": \"done|warning|error\",\n  \"findings\": [...],\n  \"next_actions\": [...]\n}\n\nABSCHLIESSEND: Sende keine Nachricht. Schreibe nur die Datei.",
        "report": "builder_daily.json",
        "schedule_hour": 12,
        "schedule_minute": 0,
    },
    "research": {
        "script": "DU BIST DER SOVEREIGN RESEARCH AGENT.\n\nSTARTE DEINE TÄGLICHE RESEARCH MISSION:\n\n1. LIES DEINE SOUL.md: cat /home/clawbot/.openclaw/workspace/research/SOUL.md\n2. ARBEITSVERZEICHNIS: cd /home/clawbot/.openclaw/workspace/research\n3. FÜHRE RESEARCH CHECK DURCH:\n   - Prüfe offene Recherchen\n   - Prüfe Trends / neue Quellen\n   - Scan /home/clawbot/.openclaw/skills/ nach neuen Skills\n4. SCHREIBE ERGEBNIS NACH: /home/clawbot/.openclaw/workspace/ceo/task_reports/research_daily.json\n\nDas JSON muss haben:\n{\n  \"agent\": \"research\",\n  \"timestamp\": \"ISO8601\",\n  \"status\": \"done|warning|error\",\n  \"findings\": [...],\n  \"next_actions\": [...]\n}\n\nABSCHLIESSEND: Sende keine Nachricht. Schreibe nur die Datei.",
        "report": "research_daily.json",
        "schedule_hour": 13,
        "schedule_minute": 0,
    },
    "qc": {
        "script": "DU BIST DER SOVEREIGN QC OFFICER.\n\nSTARTE DEINE WÖCHENTLICHE QC REVIEW:\n\n1. LIES DEINE SOUL.md: cat /home/clawbot/.openclaw/workspace/qc/SOUL.md\n2. ARBEITSVERZEICHNIS: cd /home/clawbot/.openclaw/workspace/qc\n3. PRÜFE ALLE TASK REPORTS:\n   - /home/clawbot/.openclaw/workspace/ceo/task_reports/security_daily.json\n   - /home/clawbot/.openclaw/workspace/ceo/task_reports/data_daily.json\n   - /home/clawbot/.openclaw/workspace/ceo/task_reports/builder_daily.json\n   - /home/clawbot/.openclaw/workspace/ceo/task_reports/research_daily.json\n4. FÜHRE QUALITÄTSVALIDIERUNG DURCH:\n5. SCHREIBE ERGEBNIS NACH: /home/clawbot/.openclaw/workspace/ceo/task_reports/qc_weekly.json\n\nDas JSON muss haben:\n{\n  \"agent\": \"qc_officer\",\n  \"timestamp\": \"ISO8601\",\n  \"reports_checked\": [\"security\", \"data\", \"builder\", \"research\"],\n  \"quality_score\": 1-10,\n  \"issues\": [...],\n  \"recommendations\": [...]\n}\n\nABSCHLIESSEND: Sende keine Nachricht. Schreibe nur die Datei.",
        "report": "qc_weekly.json",
        "schedule_hour": 14,
        "schedule_minute": 0,
    },
}


def read_report(report_path: str) -> dict:
    """Read and parse a task report JSON file."""
    try:
        with open(report_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading report: {e}")
        return None


def get_next_run_time(agent: str, status: str) -> datetime:
    """Calculate the next run time based on agent and status."""
    config = AGENT_CONFIGS.get(agent, {})
    now = datetime.utcnow()
    
    if status == "done":
        # Schedule for same time tomorrow
        next_run = now.replace(
            hour=config.get("schedule_hour", 10),
            minute=config.get("schedule_minute", 0),
            second=0,
            microsecond=0
        ) + timedelta(days=1)
    elif status == "warning":
        # Schedule follow-up in 4 hours
        next_run = now + timedelta(hours=4)
    else:  # error
        # Schedule retry in 2 hours
        next_run = now + timedelta(hours=2)
    
    return next_run


def reschedule_job(agent: str, next_run: datetime) -> bool:
    """Create a new at-job for the next run time using openclaw CLI."""
    import subprocess
    
    config = AGENT_CONFIGS.get(agent, {})
    job_name = f"{agent.title()} - Phoenix Reschedule"
    
    # Format: YYYY-MM-DDTHH:MM:SSZ
    schedule_time = next_run.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Build the openclaw cron add command
    cmd = [
        "openclaw", "cron", "add",
        "--name", job_name,
        "--session", "isolated",
        "--message", config.get("script", ""),
        "--timeout", "1800",
        "--deliver", "announce",
        "--channel", "telegram",
        "--at", schedule_time,
        "--delete-after-run"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ Job rescheduled for {agent}: {schedule_time}")
            return True
        else:
            print(f"❌ Failed to reschedule: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running openclaw CLI: {e}")
        return False


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 reschedule_sovereign.py <agent_name> <report_path>")
        print(f"Available agents: {list(AGENT_CONFIGS.keys())}")
        sys.exit(1)
    
    agent = sys.argv[1].lower()
    report_path = sys.argv[2]
    
    if agent not in AGENT_CONFIGS:
        print(f"Unknown agent: {agent}")
        print(f"Available: {list(AGENT_CONFIGS.keys())}")
        sys.exit(1)
    
    # Read the report
    report = read_report(report_path)
    if not report:
        print(f"Could not read report: {report_path}")
        sys.exit(1)
    
    status = report.get("status", "error")
    print(f"📊 Report status: {status}")
    
    # Calculate next run time
    next_run = get_next_run_time(agent, status)
    print(f"📅 Next run: {next_run.strftime('%Y-%m-%d %H:%M UTC')}")
    
    # Reschedule
    success = reschedule_job(agent, next_run)
    
    if success:
        print(f"🔄 {agent} will run again at {next_run.isoformat()}")
    else:
        print(f"⚠️ Could not auto-reschedule. Manual intervention required.")


if __name__ == "__main__":
    main()
