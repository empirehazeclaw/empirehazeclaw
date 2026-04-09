#!/usr/bin/env python3
"""
Night Mode - Reduziert Systemaktivität nachts
23:00 - 08:00 UTC: Nur kritische Jobs
"""

import subprocess
import json
from datetime import datetime

CRON_LIST_CMD = ["openclaw", "cron", "list"]
NIGHT_START = 23  # UTC
NIGHT_END = 8     # UTC

def get_current_hour_utc():
    return datetime.utcnow().hour

def is_night_time():
    hour = get_current_hour_utc()
    return hour >= NIGHT_START or hour < NIGHT_END

def get_night_jobs():
    """Jobs die nachts laufen dürfen (kritisch)"""
    return [
        "Security",
        "Backup",
        "Cache Cleanup",
        "Memory Cleanup"
    ]

def adjust_crons():
    """Passe Cron-Jobs an Nachtmodus an"""
    hour = get_current_hour_utc()
    
    if is_night_time():
        print(f"🌙 Night Mode aktiv ({hour} UTC)")
        print("   Nur kritische Jobs laufen lassen...")
        # Job adjustment logic would go here
        # For now just log
        return {"mode": "night", "hour": hour}
    else:
        print(f"☀️ Day Mode aktiv ({hour} UTC)")
        print("   Alle Jobs normal...")
        return {"mode": "day", "hour": hour}

if __name__ == "__main__":
    result = adjust_crons()
    print(f"Status: {result}")
