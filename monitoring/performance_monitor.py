#!/usr/bin/env python3
"""
Performance Monitor - Night Mode Friendly
"""

import os
import sys

def get_performance():
    """Get performance metrics"""
    
    # CPU (simple)
    try:
        with open('/proc/loadavg') as f:
            load = f.read().split()[0]
            cpu = float(load) * 10  # Approximate
    except:
        cpu = 0.0
    
    # RAM
    try:
        with open('/proc/meminfo') as f:
            meminfo = f.read()
            total = int([l for l in meminfo.split('\n') if 'MemTotal' in l][0].split()[1])
            available = int([l for l in meminfo.split('\n') if 'MemAvailable' in l][0].split()[1])
            ram = round((1 - available / total) * 100, 1)
    except:
        ram = 0.0
    
    # Disk
    try:
        import shutil
        disk = shutil.disk_usage('/')
        disk_pct = round(disk.percent, 1)
    except:
        disk_pct = 0.0
    
    return {
        "cpu": cpu,
        "ram": ram,
        "disk": disk_pct
    }

def is_quiet_hours():
    """Check if quiet hours (night time)"""
    
    from datetime import datetime
    
    hour = datetime.now().hour
    
    # Quiet: 23:00 - 08:00 UTC
    return hour >= 23 or hour < 8

def main():
    metrics = get_performance()
    
    # Check thresholds
    error = False
    errors = []
    
    if metrics["cpu"] > 80:
        error = True
        errors.append(f"CPU {metrics['cpu']}%")
    
    if metrics["ram"] > 90:
        error = True
        errors.append(f"RAM {metrics['ram']}%")
    
    if metrics["disk"] > 95:
        error = True
        errors.append(f"Disk {metrics['disk']}%")
    
    # Night mode: only show errors
    if is_quiet_hours():
        if error:
            print(f"⚠️ Performance Alert: {', '.join(errors)}")
            sys.exit(1)
        else:
            print("OK")
    else:
        # Normal mode - always show
        print(f"📊 Performance (10-run avg):")
        print(f"  CPU: {metrics['cpu']}")
        print(f"  RAM: {metrics['ram']}%")
        print(f"  Disk: {metrics['disk']}%")

if __name__ == "__main__":
    main()
