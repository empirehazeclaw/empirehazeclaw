#!/usr/bin/env python3
"""
⏰ Cron Optimizer — Sir HazeClaw
Analyzes cron schedule overlaps and optimizes timing.

Goals:
1. Spread CPU load evenly
2. Avoid overlapping jobs
3. Prioritize important jobs
4. Reduce redundant runs

Reports overlaps and suggests optimizations.

Usage:
    python3 cron_optimizer.py      # Analyze and suggest
    python3 cron_optimizer.py --apply  # Apply optimizations
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
CRON_JOBS_FILE = Path("/home/clawbot/.openclaw/cron/jobs.json")
LOG_FILE = WORKSPACE / "logs/cron_optimizer.log"

def log(msg: str, level: str = "INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_jobs() -> List[Dict]:
    with open(CRON_JOBS_FILE) as f:
        return json.load(f).get("jobs", [])

def save_jobs(jobs: List[Dict]):
    with open(CRON_JOBS_FILE, "w") as f:
        json.dump({"jobs": jobs}, f, indent=2)

def parse_cron_expr(expr: str) -> Dict:
    """Parse simple cron expressions like '*/5 * * * *' or '0 9 * * *'."""
    parts = expr.strip().split()
    if len(parts) != 5:
        return None
    
    minute, hour, day, month, dow = parts
    
    return {
        "minute": minute,
        "hour": hour,
        "day": day,
        "month": month,
        "dow": dow,
        "is_hourly": minute.startswith("*") and hour == "*",
        "is_daily": minute.startswith("*") == False and hour != "*" and day == "*",
        "is_weekly": dow != "*"
    }

def get_cron_frequency(jobs: List[Dict]) -> Dict[str, List[str]]:
    """Group jobs by frequency."""
    groups = {
        "every_5m": [],
        "every_10m": [],
        "every_15m": [],
        "every_30m": [],
        "hourly": [],
        "daily": [],
        "weekly": [],
        "other": []
    }
    
    for job in jobs:
        if not job.get("enabled", False):
            continue
        
        schedule = job.get("schedule", {})
        expr = schedule.get("expr", "")
        
        if "*/5" in expr:
            groups["every_5m"].append(job["name"])
        elif "*/10" in expr:
            groups["every_10m"].append(job["name"])
        elif "*/15" in expr:
            groups["every_15m"].append(job["name"])
        elif "*/30" in expr:
            groups["every_30m"].append(job["name"])
        elif "hourly" in job.get("name", "").lower():
            groups["hourly"].append(job["name"])
        elif "daily" in job.get("name", "").lower():
            groups["daily"].append(job["name"])
        elif "weekly" in job.get("name", "").lower():
            groups["weekly"].append(job["name"])
        else:
            groups["other"].append(job["name"])
    
    return groups

def find_overlaps(jobs: List[Dict]) -> List[Dict]:
    """Find jobs that might run simultaneously."""
    overlaps = []
    
    # Get jobs with their intervals
    rapid_jobs = []
    for job in jobs:
        if not job.get("enabled", False):
            continue
        
        every_ms = job.get("schedule", {}).get("everyMs")
        if every_ms and every_ms < 600000:  # Less than 10 min
            rapid_jobs.append({
                "name": job["name"],
                "id": job["id"],
                "interval_ms": every_ms
            })
    
    # Check if any rapid jobs have the same interval
    by_interval = {}
    for job in rapid_jobs:
        interval = job["interval_ms"]
        if interval not in by_interval:
            by_interval[interval] = []
        by_interval[interval].append(job["name"])
    
    for interval, names in by_interval.items():
        if len(names) > 1:
            minutes = interval / 60000
            overlaps.append({
                "type": "same_interval",
                "interval_min": minutes,
                "jobs": names,
                "suggestion": f"Spread these {minutes}min jobs to reduce peaks"
            })
    
    return overlaps

def suggest_optimizations(jobs: List[Dict]) -> List[Dict]:
    """Suggest specific optimizations."""
    suggestions = []
    
    # Check for too many rapid jobs
    rapid_count = 0
    for job in jobs:
        if not job.get("enabled", False):
            continue
        every_ms = job.get("schedule", {}).get("everyMs", 0)
        if 0 < every_ms < 300000:  # Less than 5 min
            rapid_count += 1
    
    if rapid_count > 3:
        suggestions.append({
            "type": "too_many_rapid",
            "count": rapid_count,
            "suggestion": f"{rapid_count} jobs running <5min — consider increasing intervals"
        })
    
    # Check for redundant checks
    gateway_checks = [j for j in jobs if "gateway" in j.get("name", "").lower() and j.get("enabled")]
    if len(gateway_checks) > 1:
        suggestions.append({
            "type": "redundant_checks",
            "jobs": [j["name"] for j in gateway_checks],
            "suggestion": "Multiple gateway monitoring jobs — consolidate to 1"
        })
    
    return suggestions

def main():
    log("=== Cron Optimizer Run ===")
    
    jobs = load_jobs()
    log(f"Analyzing {len(jobs)} cron jobs ({sum(1 for j in jobs if j.get('enabled'))} enabled)")
    
    # Frequency analysis
    freq = get_cron_frequency(jobs)
    log("Frequency distribution:")
    for freq_name, job_names in freq.items():
        if job_names:
            log(f"  {freq_name}: {len(job_names)} jobs")
    
    # Find overlaps
    overlaps = find_overlaps(jobs)
    if overlaps:
        log(f"Found {len(overlaps)} overlap issues:")
        for overlap in overlaps:
            log(f"  - {overlap['suggestion']}")
    
    # Suggestions
    suggestions = suggest_optimizations(jobs)
    if suggestions:
        log(f"Found {len(suggestions)} optimization opportunities:")
        for s in suggestions:
            log(f"  - {s['suggestion']}")
    
    if not overlaps and not suggestions:
        log("No optimization opportunities found ✅")
    
    # Apply if requested
    if "--apply" in sys.argv:
        log("Apply not implemented — use manual review", "WARN")
    
    return len(suggestions) + len(overlaps)

if __name__ == "__main__":
    main()
