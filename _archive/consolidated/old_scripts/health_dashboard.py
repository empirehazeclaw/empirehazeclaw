#!/usr/bin/env python3
"""
🏥 Health Dashboard — EmpireHazeClaw System Health Check

Checkt:
- Gateway Status (RPC, Prozess)
- Cron Jobs Status
- Disk/Memory Usage
- OpenClaw Prozesse

Output: Kompakter Status-Report für Builder/CEO
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Config
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
CRON_JOBS_FILE = Path("/home/clawbot/.openclaw/cron/jobs.json")

# Thresholds
DISK_WARN = 80  # %
DISK_CRIT = 90  # %
MEM_WARN = 80   # %
MEM_CRIT = 90   # %

def check_gateway():
    """Check Gateway Status."""
    result = {
        'name': 'Gateway',
        'status': 'UNKNOWN',
        'details': []
    }
    
    # Check process
    try:
        ps = subprocess.run(['pgrep', '-f', 'openclaw'], capture_output=True, text=True)
        if ps.returncode == 0 and ps.stdout.strip():
            pids = ps.stdout.strip().split('\n')
            result['details'].append(f"Process: {len(pids)} found")
            result['status'] = 'OK'
        else:
            result['status'] = 'DOWN'
            result['details'].append("No process found")
    except:
        result['details'].append("ps command failed")
    
    # Check RPC (try to read port)
    try:
        # Try to connect to gateway RPC
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result_gw = sock.connect_ex(('localhost', 18789))
        sock.close()
        if result_gw == 0:
            result['details'].append("RPC: Connected (port 18789)")
        else:
            result['details'].append("RPC: Port not reachable")
    except Exception as e:
        result['details'].append(f"RPC: Error ({e})")
    
    return result

def check_disk():
    """Check Disk Usage."""
    result = {
        'name': 'Disk',
        'status': 'OK',
        'details': []
    }
    
    try:
        stat = os.statvfs('/')
        total = stat.f_blocks * stat.f_frsize
        free = stat.f_bavail * stat.f_frsize
        used = total - free
        used_pct = (used / total) * 100
        
        result['details'].append(f"Used: {used_pct:.1f}% ({used // (1024**3)}GB / {total // (1024**3)}GB)")
        
        if used_pct >= DISK_CRIT:
            result['status'] = 'CRITICAL'
        elif used_pct >= DISK_WARN:
            result['status'] = 'WARN'
        
    except Exception as e:
        result['details'].append(f"Error: {e}")
        result['status'] = 'UNKNOWN'
    
    return result

def check_memory():
    """Check Memory Usage."""
    result = {
        'name': 'Memory',
        'status': 'OK',
        'details': []
    }
    
    try:
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
        
        mem = {}
        for line in lines:
            if ':' in line:
                key, val = line.split(':', 1)
                mem[key.strip()] = int(val.strip().split()[0])
        
        total = mem.get('MemTotal', 0)
        available = mem.get('MemAvailable', 0)
        used = total - available
        used_pct = (used / total) * 100 if total > 0 else 0
        
        result['details'].append(f"Used: {used_pct:.1f}% ({used // (1024**2)}MB / {total // (1024**2)}MB)")
        
        if used_pct >= MEM_CRIT:
            result['status'] = 'CRITICAL'
        elif used_pct >= MEM_WARN:
            result['status'] = 'WARN'
            
    except Exception as e:
        result['details'].append(f"Error: {e}")
        result['status'] = 'UNKNOWN'
    
    return result

def check_crons():
    """Check Cron Jobs Status."""
    result = {
        'name': 'Crons',
        'status': 'OK',
        'details': [],
        'errors': []
    }
    
    if not CRON_JOBS_FILE.exists():
        result['details'].append("No cron jobs file found")
        return result
    
    try:
        with open(CRON_JOBS_FILE, 'r') as f:
            data = json.load(f)
        
        jobs = data.get('jobs', [])
        enabled = [j for j in jobs if j.get('enabled', False)]
        errors = [j for j in jobs if j.get('state', {}).get('lastRunStatus') == 'error']
        
        result['details'].append(f"Total: {len(jobs)} | Enabled: {len(enabled)}")
        
        if errors:
            result['status'] = 'WARN'
            for j in errors[:3]:  # Show max 3 errors
                name = j.get('name', 'unknown')[:30]
                err = j.get('state', {}).get('lastError', 'unknown')[:50]
                result['errors'].append(f"  - {name}: {err}")
        else:
            result['details'].append("No errors")
            
    except Exception as e:
        result['details'].append(f"Error: {e}")
        result['status'] = 'UNKNOWN'
    
    return result

def check_processes():
    """Check wichtige Prozesse."""
    result = {
        'name': 'Processes',
        'status': 'OK',
        'details': []
    }
    
    processes = ['openclaw', 'node', 'python3']
    found = {}
    
    for proc in processes:
        try:
            ps = subprocess.run(['pgrep', '-c', '-f', proc], capture_output=True, text=True)
            if ps.returncode == 0:
                count = int(ps.stdout.strip())
                found[proc] = count
        except:
            pass
    
    if found:
        result['details'].append(", ".join([f"{k}: {v}" for k, v in found.items()]))
    else:
        result['details'].append("No monitored processes")
    
    return result

def check_openclaw_json():
    """Check ob openclaw.json valid ist."""
    result = {
        'name': 'Config',
        'status': 'OK',
        'details': []
    }
    
    config = Path("/home/clawbot/.openclaw/openclaw.json")
    if config.exists():
        try:
            with open(config, 'r') as f:
                json.load(f)
            result['details'].append("openclaw.json: Valid JSON")
        except json.JSONDecodeError as e:
            result['status'] = 'ERROR'
            result['details'].append(f"openclaw.json: INVALID - Line {e.lineno}")
    else:
        result['status'] = 'WARN'
        result['details'].append("openclaw.json not found")
    
    return result

def print_status(checks):
    """Printet formatierten Status."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    print("=" * 60)
    print(f"🏥 HEALTH DASHBOARD — {now}")
    print("=" * 60)
    
    all_ok = True
    any_warn = False
    any_error = False
    
    for check in checks:
        status = check['status']
        name = check['name']
        details = check.get('details', [])
        errors = check.get('errors', [])
        
        if status == 'CRITICAL' or status == 'ERROR':
            all_ok = False
            any_error = True
            icon = '🔴'
        elif status == 'WARN':
            all_ok = False
            any_warn = True
            icon = '🟡'
        elif status == 'DOWN':
            all_ok = False
            any_error = True
            icon = '🔴'
        else:
            icon = '✅'
        
        print(f"\n{icon} {name}: {status}")
        for d in details:
            print(f"   {d}")
        for e in errors:
            print(f"   {e}")
    
    print("\n" + "=" * 60)
    
    if any_error:
        print("🔴 STATUS: CRITICAL — Action required!")
    elif any_warn:
        print("🟡 STATUS: WARN — Monitor closely")
    else:
        print("✅ STATUS: ALL OK")
    
    print("=" * 60)
    
    return 0 if all_ok else (1 if any_error else 2)

def main():
    """Main Health Check."""
    print("🔍 Running health checks...\n")
    
    checks = [
        check_gateway(),
        check_disk(),
        check_memory(),
        check_crons(),
        check_processes(),
        check_openclaw_json(),
    ]
    
    exit_code = print_status(checks)
    
    # Exit codes: 0=OK, 1=CRITICAL, 2=WARN
    return exit_code

if __name__ == "__main__":
    exit(main())