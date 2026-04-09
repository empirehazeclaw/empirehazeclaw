#!/usr/bin/env python3
"""
⚡ SYSTEM OPTIMIZER
=================
Automated system improvements
"""

import os
import json
from datetime import datetime

def check_issues():
    issues = []
    
    # Check stuck processes
    import subprocess
    result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
    for line in result.stdout.split("\n"):
        if "python3 scripts" in line and "S " in line:
            parts = line.split()
            if len(parts) > 2:
                try:
                    cpu = float(parts[2])
                    if cpu > 50:
                        issues.append(f"High CPU process: {parts[-1]} ({cpu}%)")
                except:
                    pass
    
    # Check disk space
    result = subprocess.run(["df", "-h", "/"], capture_output=True, text=True)
    usage = result.stdout.split("\n")[1].split()[4]
    if int(usage.rstrip("%")) > 80:
        issues.append(f"Disk usage high: {usage}")
    
    # Check memory
    result = subprocess.run(["free", "-m"], capture_output=True, text=True)
    mem_line = result.stdout.split("\n")[-2]
    parts = mem_line.split()
    available = int(parts[6])
    if available < 500:
        issues.append(f"Low memory: {available}MB available")
    
    return issues

def optimize():
    issues = check_issues()
    
    if issues:
        print("⚠️ Issues found:")
        for i in issues:
            print(f"  - {i}")
    else:
        print("✅ System healthy")
    
    return issues

if __name__ == "__main__":
    optimize()
