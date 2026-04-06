#!/usr/bin/env python3
"""
⚡ PERFORMANCE MONITOR
====================
"""

import psutil
import time
from datetime import datetime

def check_performance():
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "cpu": cpu,
        "memory_percent": mem.percent,
        "memory_available_gb": round(mem.available / (1024**3), 2),
        "disk_percent": disk.percent,
        "disk_free_gb": round(disk.free / (1024**3), 2),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    stats = check_performance()
    print(f"CPU: {stats['cpu']}%")
    print(f"RAM: {stats['memory_percent']}% ({stats['memory_available_gb']}GB free)")
    print(f"Disk: {stats['disk_percent']}% ({stats['disk_free_gb']}GB free)")
