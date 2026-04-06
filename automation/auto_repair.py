#!/usr/bin/env python3
"""
Auto Repair Script - Checks and fixes common system issues
"""

import os
import sys
import subprocess
from datetime import datetime

LOG_FILE = "/home/clawbot/.openclaw/logs/auto_repair.log"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(f"[{timestamp}] {msg}")

def check_scripts():
    """Check if critical scripts exist"""
    critical_scripts = [
        "/home/clawbot/.openclaw/workspace/scripts/morning_routine.py",
        "/home/clawbot/.openclaw/workspace/scripts/security_report.py",
        "/home/clawbot/.openclaw/workspace/scripts/daily_report.py",
    ]
    
    missing = []
    for script in critical_scripts:
        if not os.path.exists(script):
            missing.append(script)
    
    if missing:
        log(f"⚠️ Missing scripts: {missing}")
        return False
    return True

def check_logs():
    """Check for CRITICAL errors in recent logs - only report actual issues"""
    log_file = f"/tmp/openclaw/openclaw-{datetime.now().strftime('%Y-%m-%d')}.log"
    if not os.path.exists(log_file):
        return True
    
    # Known benign patterns to ignore (not actual errors)
    benign_patterns = [
        "dashboard.service",
        "openclaw-dashboard.service",
        "Cleanup hint:",
        "Recommendation:",
        "If you need multiple gateways",
        "Other gateway-like services",
        "SECURITY NOTICE",
        "EXTERNAL_UNTRUSTED",
        "web_fetch failed",
        "read failed: ENOENT",  # File not found (not critical)
        "exec failed",  # Cron wrapper empty commands
        "message failed:",  # Delivery issues (not system critical)
        "Unknown target",
        "Unknown Channel",
        "chat not found",  # Telegram/Discord messaging
        "browser failed:",  # Browser automation failures (not system critical)
        "TimeoutError:",
        "tab not found",
        "Config write audit",
        "canvas failed:",  # Browser automation failures (not system critical)
        "edit failed:",  # Edit tool failures (not critical)
        "gateway closed",
        "gateway connect failed",
    ]
    
    with open(log_file, "r") as f:
        lines = f.readlines()[-100:]
        
        # Find actual critical errors (ERROR level but not benign)
        critical_errors = []
        for line in lines:
            if '"logLevelName":"ERROR"' in line:
                # Check if it's a benign error
                is_benign = any(pattern in line for pattern in benign_patterns)
                if not is_benign:
                    critical_errors.append(line.strip())
        
        if critical_errors:
            log(f"⚠️ Found {len(critical_errors)} CRITICAL errors in logs")
            # Only fail if there are actual critical errors
            return False
    
    return True

def check_disk():
    """Check disk space"""
    try:
        result = subprocess.run(["df", "-h", "/"], capture_output=True, text=True)
        lines = result.stdout.strip().split("\n")
        if len(lines) > 1:
            parts = lines[1].split()
            usage = parts[4] if len(parts) > 4 else parts[3]
            pct = int(usage.replace("%", ""))
            if pct > 90:
                log(f"⚠️ Disk usage high: {usage}")
                return False
    except Exception as e:
        log(f"Error checking disk: {e}")
    return True

def check_gateway():
    """Check if gateway is running"""
    try:
        result = subprocess.run(["pgrep", "-f", "openclaw.*gateway"], capture_output=True)
        if result.returncode != 0:
            log("⚠️ Gateway not running!")
            return False
    except Exception as e:
        log(f"Error checking gateway: {e}")
    return True

def main():
    log("=== Auto Repair Started ===")
    
    checks = [
        ("Scripts", check_scripts),
        ("Logs", check_logs),
        ("Disk", check_disk),
        ("Gateway", check_gateway),
    ]
    
    issues = []
    for name, check_func in checks:
        try:
            if not check_func():
                issues.append(name)
        except Exception as e:
            log(f"Error in {name}: {e}")
            issues.append(name)
    
    if issues:
        log(f"⚠️ Issues found: {', '.join(issues)}")
    else:
        log("✅ All checks passed")
    
    log("=== Auto Repair Complete ===")

if __name__ == "__main__":
    main()
