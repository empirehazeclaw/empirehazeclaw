#!/usr/bin/env python3
"""
Sir HazeClaw Common Issues Check
Prüft auf häufige Probleme.

Usage:
    python3 common_issues_check.py
"""

import os
import sys
import sqlite3
from datetime import datetime

def check_issues():
    """Prüft auf häufige Issues."""
    issues = []
    
    # 1. Check database sizes
    db_dir = "/home/clawbot/.openclaw/memory"
    for db in ['main.sqlite', 'ceo.sqlite', 'data.sqlite']:
        path = f"{db_dir}/{db}"
        if os.path.exists(path):
            size_mb = os.path.getsize(path) / (1024*1024)
            if size_mb > 500:
                issues.append(f"⚠️  {db}: {size_mb:.0f}MB (sehr groß)")
    
    # 2. Check empty files
    workspace = "/home/clawbot/.openclaw/workspace"
    empty_files = []
    for root, dirs, files in os.walk(workspace):
        # Skip .git and node_modules
        if '.git' in root or 'node_modules' in root:
            continue
        for f in files:
            path = os.path.join(root, f)
            try:
                size = os.path.getsize(path)
            except (OSError, FileNotFoundError):
                # File access failed - skip
                continue
            if size == 0:
                empty_files.append(path.replace(workspace + '/', ''))
    
    if empty_files:
        issues.append(f"⚠️  {len(empty_files)} empty files found: {empty_files[:3]}...")
    
    # 3. Check session file sizes
    session_dir = "/home/clawbot/.openclaw/agents/ceo/sessions"
    if os.path.exists(session_dir):
        large_sessions = []
        for f in os.listdir(session_dir):
            if f.endswith('.jsonl'):
                path = os.path.join(session_dir, f)
                size_mb = os.path.getsize(path) / (1024*1024)
                if size_mb > 10:
                    large_sessions.append(f"{f}: {size_mb:.1f}MB")
        
        if large_sessions:
            issues.append(f"⚠️  Large sessions: {', '.join(large_sessions[:3])}")
    
    # 4. Check cron jobs
    cron_path = "/home/clawbot/.openclaw/cron/jobs.json"
    if os.path.exists(cron_path):
        try:
            import json
            with open(cron_path) as f:
                data = json.load(f)
            jobs = data.get('jobs', [])
            disabled = [j for j in jobs if not j.get('enabled', True)]
            if disabled:
                issues.append(f"ℹ️  {len(disabled)} disabled cron jobs")
        except (IOError, json.JSONDecodeError):
            # File read or JSON parse failed - ignore
            pass
    
    # 5. Check recent errors in logs
    log_dir = "/home/clawbot/.openclaw/workspace/logs"
    if os.path.exists(log_dir):
        for log in ['heartbeat.log', 'self_healing.log']:
            path = f"{log_dir}/{log}"
            if os.path.exists(path) and os.path.getsize(path) > 0:
                with open(path) as f:
                    lines = f.readlines()
                    errors = [l for l in lines if 'ERROR' in l or 'FAIL' in l]
                    if errors:
                        issues.append(f"⚠️  {log}: {len(errors)} errors")
    
    return issues

def main():
    print(f"Sir HazeClaw Common Issues Check — {datetime.now().strftime('%H:%M:%S UTC')}")
    print("=" * 60)
    
    issues = check_issues()
    
    if not issues:
        print("✅ No common issues found")
    else:
        print(f"Found {len(issues)} potential issues:\n")
        for issue in issues:
            print(f"  {issue}")
    
    print("=" * 60)
    return 0 if len(issues) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())