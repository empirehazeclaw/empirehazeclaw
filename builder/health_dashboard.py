#!/usr/bin/env python3
"""
🏥 Health Dashboard v2 — Builder Agent
Enhanced Health Check für EmpireHazeClaw Fleet

Features:
- Gateway Status (PID, Version, RPC)
- Cron-Status aller aktiven Crons
- Disk/Memory Usage
- Todo-Tracker aus TODOS.md
- QC RED ALERT falls vorhanden
- JSON Output für automatisierte Alerts
- Human-readable Output für CEO

Output: /home/clawbot/.openclaw/workspace/builder/health_dashboard.py
"""

import os
import sys
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path

# Config Paths
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
OPENCLAW_CONFIG = Path("/home/clawbot/.openclaw/openclaw.json")
TODOS_FILE = Path("/home/clawbot/.openclaw/workspace/builder/TODOS.md")
QC_REPORT_FILE = Path("/home/clawbot/.openclaw/workspace/qc/officer/task_reports/qc_daily.json")
CRON_JOBS_FILE = Path("/home/clawbot/.openclaw/cron/jobs.json")

# Thresholds
DISK_WARN = 80
DISK_CRIT = 90
MEM_WARN = 80
MEM_CRIT = 90

# State for collecting all checks
checks = []
warnings = []
errors = []

def log(category, status, message, details=None):
    """Collect check result."""
    entry = {
        'category': category,
        'status': status,
        'message': message,
        'details': details or []
    }
    checks.append(entry)
    return entry

# === GATEWAY CHECKS ===

def check_gateway():
    """Check Gateway Status."""
    details = []
    status = 'OK'
    
    # Check process
    try:
        ps = subprocess.run(['pgrep', '-f', 'openclaw'], capture_output=True, text=True)
        if ps.returncode == 0 and ps.stdout.strip():
            pids = ps.stdout.strip().split('\n')
            details.append(f"PIDs: {', '.join(pids)}")
        else:
            status = 'DOWN'
            details.append("No process found")
    except Exception as e:
        status = 'ERROR'
        details.append(f"ps failed: {e}")
    
    # Check RPC
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 18789))
        sock.close()
        if result == 0:
            details.append("RPC: Connected (port 18789)")
        else:
            status = 'WARN'
            details.append("RPC: Port not reachable")
    except Exception as e:
        details.append(f"RPC check failed: {e}")
    
    # Get version from config
    version = None
    try:
        if OPENCLAW_CONFIG.exists():
            with open(OPENCLAW_CONFIG, 'r') as f:
                data = json.load(f)
            version = data.get('meta', {}).get('lastTouchedVersion', 'unknown')
    except:
        pass
    
    if version:
        details.append(f"Version: {version}")
    
    log('gateway', status, f"Gateway: {status}", details)

# === CRON CHECKS ===

def check_crons():
    """Check alle aktiven Cron Jobs."""
    details = []
    cron_errors = []
    
    if not CRON_JOBS_FILE.exists():
        log('crons', 'WARN', "Cron jobs file not found", ["No /cron/jobs.json"])
        return
    
    try:
        with open(CRON_JOBS_FILE, 'r') as f:
            data = json.load(f)
        
        jobs = data.get('jobs', [])
        enabled = [j for j in jobs if j.get('enabled', False)]
        error_jobs = [j for j in jobs if j.get('state', {}).get('lastRunStatus') == 'error']
        
        details.append(f"Total: {len(jobs)} | Enabled: {len(enabled)} | Errors: {len(error_jobs)}")
        
        # List enabled crons with their schedules
        for j in enabled[:10]:
            name = j.get('name', 'unknown')[:35]
            sched = j.get('schedule', {}).get('expr', j.get('schedule', {}).get('kind', '?'))
            last_status = j.get('state', {}).get('lastRunStatus', '?')
            details.append(f"  • {name} [{sched}] → {last_status}")
        
        if error_jobs:
            for j in error_jobs[:3]:
                name = j.get('name', 'unknown')[:30]
                err = j.get('state', {}).get('lastError', 'unknown')[:60]
                cron_errors.append(f"  • {name}: {err}")
        
        status = 'ERROR' if len(error_jobs) >= 3 else ('WARN' if error_jobs else 'OK')
        log('crons', status, f"Crons: {len(enabled)} enabled, {len(error_jobs)} errors", details + cron_errors)
        
    except Exception as e:
        log('crons', 'ERROR', f"Failed to read cron jobs: {e}")

# === DISK/MEMORY CHECKS ===

def check_disk():
    """Check Disk Usage."""
    try:
        stat = os.statvfs('/')
        total = stat.f_blocks * stat.f_frsize
        free = stat.f_bavail * stat.f_frsize
        used = total - free
        used_pct = (used / total) * 100
        
        details = [f"{used_pct:.1f}% used ({used // (1024**3)}GB / {total // (1024**3)}GB)"]
        
        if used_pct >= DISK_CRIT:
            status = 'CRITICAL'
        elif used_pct >= DISK_WARN:
            status = 'WARN'
        else:
            status = 'OK'
        
        log('disk', status, f"Disk: {used_pct:.1f}%", details)
    except Exception as e:
        log('disk', 'ERROR', f"Disk check failed: {e}")

def check_memory():
    """Check Memory Usage."""
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
        
        details = [f"{used_pct:.1f}% used ({used // (1024**2)}MB / {total // (1024**2)}MB)"]
        
        if used_pct >= MEM_CRIT:
            status = 'CRITICAL'
        elif used_pct >= MEM_WARN:
            status = 'WARN'
        else:
            status = 'OK'
        
        log('memory', status, f"Memory: {used_pct:.1f}%", details)
    except Exception as e:
        log('memory', 'ERROR', f"Memory check failed: {e}")

# === TODOS CHECK ===

def check_todos():
    """Check Todo-Tracker aus TODOS.md."""
    try:
        if not TODOS_FILE.exists():
            log('todos', 'WARN', "TODOS.md not found")
            return
        
        with open(TODOS_FILE, 'r') as f:
            content = f.read()
        
        # Parse todos from markdown table
        # Look for state badges like [WORKING], [BLOCKED], etc.
        working = len(re.findall(r'\[WORKING\]', content, re.IGNORECASE))
        blocked = len(re.findall(r'\[BLOCKED\]', content, re.IGNORECASE))
        pending = len(re.findall(r'\[RECEIVED\]', content, re.IGNORECASE))
        done = len(re.findall(r'\[DONE\]', content, re.IGNORECASE)) + len(re.findall(r'\[VERIFIED\]', content, re.IGNORECASE))
        
        details = [
            f"Working: {working}",
            f"Blocked: {blocked}",
            f"Pending: {pending}",
            f"Done/Verified: {done}"
        ]
        
        if blocked > 0:
            status = 'WARN'
        elif working > 3:
            status = 'BUSY'
        else:
            status = 'OK'
        
        log('todos', status, f"Todos: {working} working, {blocked} blocked, {done} done", details)
        
    except Exception as e:
        log('todos', 'ERROR', f"Todo check failed: {e}")

# === QC RED ALERT CHECK ===

def check_qc_alerts():
    """Check QC Officer reports for RED ALERT."""
    try:
        if not QC_REPORT_FILE.exists():
            log('qc', 'OK', "QC report not found (normal if QC not active)")
            return
        
        with open(QC_REPORT_FILE, 'r') as f:
            report = json.load(f)
        
        overall = report.get('overall_status', 'UNKNOWN')
        critical = report.get('critical_issues', [])
        
        # Parse overall status
        if 'RED' in overall or 'CRITICAL' in overall:
            status = 'RED'
        elif 'YELLOW' in overall or 'WARN' in overall:
            status = 'WARN'
        elif 'GREEN' in overall:
            status = 'OK'
        else:
            status = 'UNKNOWN'
        
        details = [f"Overall: {overall}"]
        
        if critical:
            for iss in critical[:3]:
                details.append(f"  • [{iss.get('priority', '?')}] {iss.get('title', 'unknown')}")
        
        if status == 'RED':
            errors.append(f"QC RED ALERT: {overall}")
        
        log('qc', status, f"QC Status: {overall}", details)
        
    except Exception as e:
        log('qc', 'ERROR', f"QC check failed: {e}")

# === PROCESS CHECK ===

def check_processes():
    """Check wichtige Prozesse."""
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
        details = [f"{k}: {v}" for k, v in found.items()]
        log('processes', 'OK', f"Processes: {', '.join(details)}", details)
    else:
        log('processes', 'WARN', "No monitored processes found")

# === CONFIG CHECK ===

def check_config():
    """Check openclaw.json validity."""
    try:
        if OPENCLAW_CONFIG.exists():
            with open(OPENCLAW_CONFIG, 'r') as f:
                json.load(f)
            log('config', 'OK', "openclaw.json: Valid JSON")
        else:
            log('config', 'ERROR', "openclaw.json: NOT FOUND")
    except json.JSONDecodeError as e:
        log('config', 'ERROR', f"openclaw.json: INVALID - Line {e.lineno}", [str(e)])

# === OUTPUT ===

def print_human_readable():
    """Print human-readable report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    
    print("=" * 70)
    print(f"🏥 HEALTH DASHBOARD — {now}")
    print("=" * 70)
    
    # Group by category
    categories = {}
    for c in checks:
        cat = c['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(c)
    
    for cat, items in categories.items():
        print(f"\n[{cat.upper()}]")
        for item in items:
            status_icon = {
                'OK': '✅',
                'GREEN': '✅',
                'WARN': '🟡',
                'YELLOW': '🟡',
                'BUSY': '🔵',
                'ERROR': '🔴',
                'CRITICAL': '🔴',
                'RED': '🔴',
                'DOWN': '🔴',
                'UNKNOWN': '❓'
            }.get(item['status'], '?')
            
            print(f"  {status_icon} {item['message']}")
            for detail in item.get('details', []):
                print(f"      {detail}")
    
    # Summary
    print("\n" + "=" * 70)
    
    has_critical = any(c['status'] in ['ERROR', 'CRITICAL', 'DOWN', 'RED'] for c in checks)
    has_warn = any(c['status'] in ['WARN', 'YELLOW'] for c in checks)
    
    if has_critical:
        print("🔴 STATUS: CRITICAL — Action required immediately!")
    elif has_warn:
        print("🟡 STATUS: WARN — Monitor closely")
    else:
        print("✅ STATUS: ALL OK — Fleet healthy")
    
    print("=" * 70)

def get_json_output():
    """Return JSON-serializable dict for automated alerts."""
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    has_critical = any(c['status'] in ['ERROR', 'CRITICAL', 'DOWN', 'RED'] for c in checks)
    has_warn = any(c['status'] in ['WARN', 'YELLOW'] for c in checks)
    
    if has_critical:
        overall = 'CRITICAL'
    elif has_warn:
        overall = 'WARN'
    else:
        overall = 'OK'
    
    return {
        'timestamp': now,
        'overall_status': overall,
        'checks': checks,
        'summary': {
            'total': len(checks),
            'ok': len([c for c in checks if c['status'] in ['OK', 'GREEN']]),
            'warn': len([c for c in checks if c['status'] in ['WARN', 'YELLOW', 'BUSY']]),
            'error': len([c for c in checks if c['status'] in ['ERROR', 'CRITICAL', 'DOWN', 'RED']])
        }
    }

def main():
    """Run all checks and output."""
    # Run all checks
    check_gateway()
    check_crons()
    check_disk()
    check_memory()
    check_todos()
    check_qc_alerts()
    check_processes()
    check_config()
    
    # Determine output format
    if '--json' in sys.argv:
        output = get_json_output()
        print(json.dumps(output, indent=2))
        return 0 if output['overall_status'] == 'OK' else (1 if output['overall_status'] == 'CRITICAL' else 2)
    else:
        print_human_readable()
        has_critical = any(c['status'] in ['ERROR', 'CRITICAL', 'DOWN', 'RED'] for c in checks)
        has_warn = any(c['status'] in ['WARN', 'YELLOW'] for c in checks)
        return 0 if not has_critical and not has_warn else (1 if has_critical else 2)

if __name__ == "__main__":
    sys.exit(main())