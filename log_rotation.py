#!/usr/bin/env python3
"""
Log Rotation - Already handled by nightly_bundle
This script is a placeholder for backwards compatibility
"""

import os
from datetime import datetime

LOG_FILE = "/home/clawbot/.openclaw/logs/log_rotation.log"

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")
    print(msg)

if __name__ == "__main__":
    log("Log rotation is handled by nightly_bundle.sh")
    log("✅ No action needed")
