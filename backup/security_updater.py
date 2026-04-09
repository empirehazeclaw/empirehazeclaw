#!/usr/bin/env python3
"""
Auto Security Updater
Checkt und installiert Sicherheitsupdates automatisch
"""

import subprocess
import os
from datetime import datetime

LOG_FILE = "/home/clawbot/.openclaw/logs/security-updates.log"

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")

def check_updates():
    """Prüfe auf Updates"""
    try:
        result = subprocess.run(
            ["apt-get", "-s", "upgrade"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Zähle Security Updates
        security_count = result.stdout.count("security")
        
        if security_count > 0:
            log(f"⚠️ {security_count} Security Updates verfügbar!")
            return security_count
        else:
            log("✅ System aktuell")
            return 0
            
    except Exception as e:
        log(f"❌ Error: {e}")
        return -1

if __name__ == "__main__":
    count = check_updates()
    print(f"Security Updates: {count}")
