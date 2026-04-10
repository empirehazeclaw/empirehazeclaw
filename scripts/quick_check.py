#!/usr/bin/env python3
"""
Sir HazeClaw Quick Check
Schneller System-Check für tägliche Verwendung.

Usage:
    python3 quick_check.py
"""

import os
import sys
import sqlite3
import psutil
import socket
from datetime import datetime

def check(name, ok, msg=""):
    symbol = "✅" if ok else "❌"
    print(f"{symbol} {name}: {msg}" if msg else f"{symbol} {name}")
    return ok

def main():
    print(f"Sir HazeClaw Quick Check — {datetime.now().strftime('%H:%M:%S UTC')}")
    print("=" * 50)
    
    all_ok = True
    
    # Gateway
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(("127.0.0.1", 18789))
        sock.close()
        all_ok &= check("Gateway", result == 0, "responding" if result == 0 else "DOWN")
    except:
        all_ok &= check("Gateway", False, "ERROR")
    
    # Disk
    disk = psutil.disk_usage('/')
    all_ok &= check("Disk", disk.percent < 90, f"{100-disk.percent:.0f}% free")
    
    # Memory  
    mem = psutil.virtual_memory()
    all_ok &= check("Memory", mem.percent < 90, f"{100-mem.percent:.0f}% free")
    
    # Load
    load = os.getloadavg()[0]
    all_ok &= check("Load", load < 4.0, f"{load:.2f}")
    
    # Databases
    for db_name in ['main.sqlite', 'ceo.sqlite', 'data.sqlite']:
        db_path = f"/home/clawbot/.openclaw/memory/{db_name}"
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()[0]
                conn.close()
                all_ok &= check(f"DB {db_name}", result == "ok", result)
            except:
                all_ok &= check(f"DB {db_name}", False, "ERROR")
        else:
            check(f"DB {db_name}", False, "NOT FOUND")
            all_ok = False
    
    # Backups
    backup_dir = "/home/clawbot/.openclaw/backups"
    today = datetime.now().strftime("%Y%m%d")
    import glob
    backups = glob.glob(f"{backup_dir}/backup_{today}_*.tar.gz")
    all_ok &= check("Backup", len(backups) > 0, f"{len(backups)} today")
    
    print("=" * 50)
    if all_ok:
        print("✅ ALL CHECKS PASSED")
    else:
        print("❌ SOME CHECKS FAILED")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())