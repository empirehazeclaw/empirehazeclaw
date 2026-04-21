# DEPRECATED - Use health_check.py
#!/usr/bin/env python3
"""
Sir HazeClaw Health Alert Script
Sendet Alerts wenn System Probleme hat.

Usage:
    python3 health_alert.py
    python3 health_alert.py --test  # Test alert only
"""

import os
import sys
import sqlite3
import psutil
import socket
from datetime import datetime

# Config
GATEWAY_PORT = 18789
GATEWAY_HOST = "127.0.0.1"
DISK_THRESHOLD = 10  # %
MEMORY_THRESHOLD = 90  # %
LOAD_THRESHOLD = 4.0
ALERT_COOLDOWN = 3600  # 1 hour between alerts

# Alert log
ALERT_LOG = "/home/clawbot/.openclaw/workspace/logs/health_alerts.log"

def log_alert(alert_type, message):
    """Loggt Alert zu Datei."""
    os.makedirs(os.path.dirname(ALERT_LOG), exist_ok=True)
    
    with open(ALERT_LOG, "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        f.write(f"[{timestamp}] {alert_type}: {message}\n")

def should_alert(alert_type):
    """Prüft ob Alert gesendet werden soll (cooldown)."""
    if not os.path.exists(ALERT_LOG):
        return True
    
    try:
        with open(ALERT_LOG, "r") as f:
            lines = f.readlines()
        
        # Find last alert of this type
        for line in reversed(lines):
            if f"[{alert_type}]" in line:
                # Extract timestamp
                try:
                    ts_str = line.split("]")[0].replace("[", "")
                    last_alert = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S UTC")
                    age_seconds = (datetime.now() - last_alert).seconds
                    
                    if age_seconds < ALERT_COOLDOWN:
                        return False
                except:
                    pass
                break
        
        return True
    except:
        return True

def check_gateway():
    """Prüft Gateway."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((GATEWAY_HOST, GATEWAY_PORT))
        sock.close()
        return result == 0, "Gateway responding" if result == 0 else "Gateway down"
    except Exception as e:
        return False, f"Gateway error: {e}"

def check_disk():
    """Prüft Disk."""
    usage = psutil.disk_usage('/')
    percent_free = usage.percent
    
    if percent_free < DISK_THRESHOLD:
        return False, f"Disk critically low: {percent_free:.1f}% free"
    return True, f"Disk OK: {percent_free:.1f}% free"

def check_memory():
    """Prüft Memory."""
    mem = psutil.virtual_memory()
    percent_used = mem.percent
    
    if percent_used > MEMORY_THRESHOLD:
        return False, f"Memory high: {percent_used:.1f}% used"
    return True, f"Memory OK: {percent_used:.1f}% used"

def check_load():
    """Prüft Load."""
    load = os.getloadavg()[0]
    
    if load > LOAD_THRESHOLD:
        return False, f"Load high: {load:.2f}"
    return True, f"Load OK: {load:.2f}"

def send_alert(alert_type, component, message):
    """Sendet Alert via OpenClaw message."""
    if not should_alert(component):
        print(f"⏳ [{component}] Cooldown active, skipping alert")
        return
    
    log_alert(component, message)
    
    # Hier würde eine OpenClaw message oder cron notification kommen
    print(f"🚨 ALERT [{component}]: {message}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Health Alert')
    parser.add_argument('--test', action='store_true', help='Send test alert')
    args = parser.parse_args()
    
    if args.test:
        print("Sending test alert...")
        send_alert("TEST", "test", "This is a test alert")
        return
    
    print(f"Health Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()
    
    issues = []
    
    # Gateway
    ok, msg = check_gateway()
    if not ok:
        issues.append(("GATEWAY", msg))
    
    # Disk
    ok, msg = check_disk()
    if not ok:
        issues.append(("DISK", msg))
    
    # Memory
    ok, msg = check_memory()
    if not ok:
        issues.append(("MEMORY", msg))
    
    # Load
    ok, msg = check_load()
    if not ok:
        issues.append(("LOAD", msg))
    
    if issues:
        print("❌ ISSUES DETECTED:")
        for component, msg in issues:
            print(f"  - {component}: {msg}")
            send_alert("CRITICAL", component, msg)
        
        sys.exit(1)
    else:
        print("✅ All checks passed")

if __name__ == "__main__":
    main()