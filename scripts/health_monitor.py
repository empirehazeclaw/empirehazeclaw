#!/usr/bin/env python3
"""
Sir HazeClaw Health Monitor
Prüft System-Gesundheit und alarmiert bei Problemen.

Usage:
    python3 health_monitor.py [--report]
    python3 health_monitor.py [--check-gateway] [--check-disk] [--check-crons]
"""

import os
import sys
import sqlite3
import psutil
from datetime import datetime
from pathlib import Path

# Config
GATEWAY_PORT = 18789
GATEWAY_HOST = "127.0.0.1"
DISK_THRESHOLD = 10  # %
MEMORY_THRESHOLD = 90  # %
LOAD_THRESHOLD = 4.0

def check_gateway():
    """Prüft ob Gateway läuft."""
    import socket
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((GATEWAY_HOST, GATEWAY_PORT))
        sock.close()
        
        if result == 0:
            return True, "Gateway responding"
        else:
            return False, f"Gateway not responding on port {GATEWAY_PORT}"
    except Exception as e:
        return False, f"Gateway check failed: {e}"

def check_disk():
    """Prüft Disk Space."""
    usage = psutil.disk_usage('/')
    percent_free = usage.percent
    
    if percent_free < DISK_THRESHOLD:
        return False, f"Disk critically low: {percent_free:.1f}% free"
    else:
        return True, f"Disk OK: {percent_free:.1f}% free"

def check_memory():
    """Prüft Memory Usage."""
    mem = psutil.virtual_memory()
    percent_used = mem.percent
    
    if percent_used > MEMORY_THRESHOLD:
        return False, f"Memory high: {percent_used:.1f}% used"
    else:
        return True, f"Memory OK: {percent_used:.1f}% used"

def check_load():
    """Prüft System Load."""
    load = os.getloadavg()[0]
    
    if load > LOAD_THRESHOLD:
        return False, f"Load high: {load:.2f}"
    else:
        return True, f"Load OK: {load:.2f}"

def check_databases():
    """Prüft Database Integrity."""
    dbs = {
        'main.sqlite': '/home/clawbot/.openclaw/memory/main.sqlite',
        'ceo.sqlite': '/home/clawbot/.openclaw/memory/ceo.sqlite',
        'data.sqlite': '/home/clawbot/.openclaw/memory/data.sqlite'
    }
    
    results = []
    for name, path in dbs.items():
        if not os.path.exists(path):
            results.append((name, False, "DB not found"))
            continue
            
        try:
            conn = sqlite3.connect(path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            conn.close()
            
            if result == "ok":
                results.append((name, True, "OK"))
            else:
                results.append((name, False, f"Integrity issue: {result}"))
        except Exception as e:
            results.append((name, False, f"Error: {e}"))
    
    return results

def check_crons():
    """Prüft ob Crons laufen (via openclaw cron list)."""
    # Hier würde ein subprocess call kommen
    # Vereinfacht: Nur prüfen ob cron Datei existiert
    cron_path = Path('/home/clawbot/.openclaw/cron/jobs.json')
    if cron_path.exists():
        return True, "Cron config exists"
    else:
        return False, "No cron config"

def generate_report():
    """Generiert vollständigen Health Report."""
    print("=" * 50)
    print("Sir HazeClaw Health Report")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 50)
    print()
    
    # System Health
    print("[SYSTEM]")
    disk_ok, disk_msg = check_disk()
    mem_ok, mem_msg = check_memory()
    load_ok, load_msg = check_load()
    
    print(f"  Disk:  {'✅' if disk_ok else '❌'} {disk_msg}")
    print(f"  Memory: {'✅' if mem_ok else '❌'} {mem_msg}")
    print(f"  Load:  {'✅' if load_ok else '❌'} {load_msg}")
    print()
    
    # Gateway
    print("[GATEWAY]")
    gw_ok, gw_msg = check_gateway()
    print(f"  Gateway: {'✅' if gw_ok else '❌'} {gw_msg}")
    print()
    
    # Databases
    print("[DATABASES]")
    db_results = check_databases()
    for name, ok, msg in db_results:
        print(f"  {name}: {'✅' if ok else '❌'} {msg}")
    print()
    
    # Overall
    all_ok = disk_ok and mem_ok and load_ok and gw_ok and all(r[1] for r in db_results)
    
    print("=" * 50)
    if all_ok:
        print("✅ SYSTEM HEALTHY")
    else:
        print("❌ ISSUES DETECTED")
    print("=" * 50)
    
    return all_ok

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Sir HazeClaw Health Monitor')
    parser.add_argument('--report', action='store_true', help='Full health report')
    parser.add_argument('--check-gateway', action='store_true', help='Check gateway only')
    parser.add_argument('--check-disk', action='store_true', help='Check disk only')
    parser.add_argument('--check-memory', action='store_true', help='Check memory only')
    
    args = parser.parse_args()
    
    if args.check_gateway:
        ok, msg = check_gateway()
        print(f"Gateway: {'✅' if ok else '❌'} {msg}")
    elif args.check_disk:
        ok, msg = check_disk()
        print(f"Disk: {'✅' if ok else '❌'} {msg}")
    elif args.check_memory:
        ok, msg = check_memory()
        print(f"Memory: {'✅' if ok else '❌'} {msg}")
    else:
        # Full report
        generate_report()

if __name__ == "__main__":
    main()