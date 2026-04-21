#!/usr/bin/env python3
"""
Cron Status Dashboard Generator
Updates /workspace/logs/cron_status.json with current cron health
CEO Daily Briefing reads this for status overview
"""

import json
import sys
from datetime import datetime

def generate_status(crons_data):
    """Generate status JSON from cron list"""
    total = crons_data.get("total", 0)
    jobs = crons_data.get("jobs", [])
    
    enabled = [j for j in jobs if j.get("enabled", False)]
    disabled = [j for j in jobs if not j.get("enabled", False)]
    
    healthy = []
    degraded = []
    failed = []
    
    for job in enabled:
        state = job.get("state", {})
        last_status = state.get("lastStatus", "unknown")
        consecutive_errors = state.get("consecutiveErrors", 0)
        
        job_info = {
            "id": job.get("id"),
            "name": job.get("name", "Unknown"),
            "lastRun": state.get("lastRunAtMs"),
            "lastStatus": last_status,
            "consecutiveErrors": consecutive_errors,
            "lastError": state.get("lastError"),
            "nextRun": state.get("nextRunAtMs")
        }
        
        if consecutive_errors >= 3:
            failed.append(job_info)
        elif last_status == "error":
            degraded.append(job_info)
        else:
            healthy.append(job_info)
    
    # Generate summary
    summary = {
        "generated": datetime.utcnow().isoformat() + "Z",
        "total": total,
        "enabled": len(enabled),
        "disabled": len(disabled),
        "healthy": len(healthy),
        "degraded": len(degraded),
        "failed": len(failed),
        "error_rate": round((len(degraded) + len(failed)) / len(enabled) * 100, 1) if enabled else 0
    }
    
    # Detailed status
    status = {
        "summary": summary,
        "healthy": healthy,
        "degraded": degraded,
        "failed": failed,
        "disabled": [{"id": j.get("id"), "name": j.get("name", "Unknown")} for j in disabled]
    }
    
    return status

def main():
    # Read cron list from file or stdin
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as f:
            crons_data = json.load(f)
    else:
        # Read from stdin
        crons_data = json.load(sys.stdin)
    
    status = generate_status(crons_data)
    
    # Write to status file
    output_path = "/home/clawbot/.openclaw/workspace/logs/cron_status.json"
    with open(output_path, "w") as f:
        json.dump(status, f, indent=2)
    
    print(f"Updated {output_path}")
    print(f"Summary: {status['summary']}")

if __name__ == "__main__":
    main()
