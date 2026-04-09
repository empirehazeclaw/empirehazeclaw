#!/usr/bin/env python3
"""
Discord Report Forwarder
Posts agent reports to Discord channels/threads
Run after cron jobs complete (e.g., via cron or manually)
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
import urllib.error

# Discord config
DISCORD_TOKEN = "DISCORD_BOT_TOKEN"
BASE_URL = "https://discord.com/api/v10"

# Channel/Thread IDs
CHANNELS = {
    "security": {
        "channel": "1491780127951032380",
        "thread": "1491783102509617152"
    },
    "data": {
        "channel": "1491780129586810952", 
        "thread": "1491783105336578230"
    },
    "builder": {
        "channel": "1491780131101085837",
        "thread": "1491783108813652071"
    },
    "research": {
        "channel": "1491780132552315010",
        "thread": "1491783112001323148"
    },
    "qc": {
        "channel": "1491780133730652431",
        "thread": "1491783121752817697"
    }
}

# Report paths (agent workspace → task_reports)
REPORT_PATHS = {
    "security": "/home/clawbot/.openclaw/workspace/security/task_reports/security_daily.json",
    "data": "/home/clawbot/.openclaw/workspace/data/task_reports/data_daily.json",
    "builder": "/home/clawbot/.openclaw/workspace/builder/task_reports/builder_daily.json",
    "research": "/home/clawbot/.openclaw/workspace/research/task_reports/research_daily.json",
    "qc": "/home/clawbot/.openclaw/workspace/qc/task_reports/qc_daily.json"
}

def send_discord(channel_id, message):
    """Send message to Discord channel/thread"""
    url = f"{BASE_URL}/channels/{channel_id}/messages"
    data = json.dumps({"content": message}).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bot {DISCORD_TOKEN}")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "DiscordBot (https://github.com/empirehazeclaw, 1.0)")
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode(), "code": e.code}

def format_status(emoji, text):
    """Format status with emoji"""
    return f"{emoji} {text}"

def load_report(path):
    """Load a JSON report file"""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return None

def generate_report_message(agent, report):
    """Generate a Discord-formatted report message"""
    if not report:
        return f"❌ **{agent.upper()}** — Kein Report verfügbar"
    
    status = report.get("status") or report.get("overall_status", "UNKNOWN")
    status_emoji = {
        "GREEN": "🟢", "YELLOW": "🟡", "RED": "🔴",
        "✅": "🟢", "⚠️": "🟡", "❌": "🔴"
    }.get(status, "⚪")
    
    now = datetime.now(timezone.utc)
    timestamp = report.get("last_updated") or report.get("date") or now.strftime("%Y-%m-%d %H:%M UTC")
    
    lines = [
        f"📊 **{agent.upper()} DAILY REPORT** — {timestamp}",
        "",
        f"{status_emoji} Status: `{status}`",
        ""
    ]
    
    # Add summary if present
    if "summary" in report:
        lines.append(report["summary"])
        lines.append("")
    
    # Add key findings based on agent type
    if agent == "security":
        if "keys_status" in report:
            lines.append(f"**Keys Status:** {report['keys_status']}")
        if "clawhub_vetting" in report:
            lines.append(f"**ClawHub Vetting:** {report['clawhub_vetting']}")
        if "issues_resolved" in report:
            lines.append(f"**Issues Resolved:** {report['issues_resolved']}")
    elif agent == "data":
        if "kg_entities" in report:
            lines.append(f"**KG Entities:** {report['kg_entities']}")
        if "kg_relations" in report:
            lines.append(f"**KG Relations:** {report['kg_relations']}")
    elif agent == "builder":
        if "new_scripts" in report:
            lines.append(f"**New Scripts:** {report['new_scripts']}")
        if "open_tasks" in report:
            lines.append(f"**Open Tasks:** {report['open_tasks']}")
    elif agent == "research":
        if "topics_researched" in report:
            lines.append(f"**Topics:** {report['topics_researched']}")
    elif agent == "qc":
        if "validation_results" in report:
            lines.append(f"**Validation:** {report['validation_results']}")
    
    # Add recommendations
    if "recommendations" in report and report["recommendations"]:
        lines.append("")
        lines.append("**Recommendations:**")
        for rec in (report["recommendations"] if isinstance(report["recommendations"], list) else [report["recommendations"]]):
            lines.append(f"  • {rec}")
    
    return "\n".join(lines)

def main():
    """Main function - post all reports to Discord"""
    print("🔄 Discord Report Forwarder gestartet...")
    
    for agent in CHANNELS:
        report_path = REPORT_PATHS.get(agent)
        if not report_path:
            continue
            
        report = load_report(report_path)
        message = generate_report_message(agent, report)
        
        # Post to thread
        result = send_discord(CHANNELS[agent]["thread"], message)
        
        if "id" in result:
            print(f"✅ {agent}: Report posted to thread")
        else:
            print(f"❌ {agent}: Failed - {result.get('error', 'unknown error')[:80]}")
    
    print("✅ Discord Report Forwarder fertig!")

if __name__ == "__main__":
    main()
