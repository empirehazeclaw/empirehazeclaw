#!/usr/bin/env python3
"""
🌙 Evening Summary Agent
Wird täglich um 20:00 ausgeführt.
Erstellt eine Zusammenfassung des Tages.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.file_lock import locked_read

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")

def generate_summary():
    """Erstellt Tageszusammenfassung"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    summary = {
        "date": today,
        "generated_at": datetime.now().isoformat(),
        "metrics": {},
        "alerts": [],
        "next_actions": []
    }
    
    # Emails sent today
    sent_file = WORKSPACE / "data/sent_emails.json"
    if sent_file.exists():
        sent = locked_read(str(sent_file), {})
        today_sent = [
            e for e in sent.values() 
            if e.get("sent_at", "").startswith(today)
        ]
        summary["metrics"]["emails_sent"] = len(today_sent)
    else:
        summary["metrics"]["emails_sent"] = 0
    
    # Check watchdog alerts
    watchdog_log = WORKSPACE / "logs/watchdog.log"
    if watchdog_log.exists():
        with open(watchdog_log) as f:
            lines = f.readlines()
            today_lines = [l for l in lines if today in l]
            alerts = [l for l in today_lines if "ISSUE" in l or "ERROR" in l]
            summary["alerts"] = alerts[-5:]  # Last 5
    
    # Check outreach log
    outreach_log = WORKSPACE / "logs/outreach.log"
    if outreach_log.exists():
        with open(outreach_log) as f:
            lines = f.readlines()
            summary["metrics"]["outreach_log_lines"] = len(lines)
    
    return summary

def main():
    print(f"🌙 Evening Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*50)
    
    summary = generate_summary()
    
    print(f"\n📊 HEUTE:")
    print(f"   Emails gesendet: {summary['metrics'].get('emails_sent', 0)}")
    print(f"   Outreach Log: {summary['metrics'].get('outreach_log_lines', 0)} Zeilen")
    
    if summary['alerts']:
        print(f"\n⚠️ ALERTS:")
        for alert in summary['alerts'][-3:]:
            print(f"   {alert.strip()[:80]}")
    else:
        print(f"\n✅ Keine Alerts")
    
    # Save summary
    summary_file = WORKSPACE / f"data/daily_summary_{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n💾 Summary gespeichert: {summary_file.name}")
    print("="*50)

if __name__ == "__main__":
    main()
