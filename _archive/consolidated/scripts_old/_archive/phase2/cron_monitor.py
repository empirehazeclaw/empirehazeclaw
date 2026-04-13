#!/usr/bin/env python3
"""
Sir HazeClaw Cron Monitor — IMPROVED
Prüft Status der Cron Jobs mit detaillierten Informationen.

Usage:
    python3 cron_monitor.py
    python3 cron_monitor.py --format telegram
    python3 cron_monitor.py --failed-only
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

CRON_PATH = Path("/home/clawbot/.openclaw/cron/jobs.json")

def get_cron_status():
    """Liest Cron Jobs aus jobs.json."""
    if not CRON_PATH.exists():
        return [], "Cron file not found"
    
    try:
        with open(CRON_PATH) as f:
            data = json.load(f)
        return data.get('jobs', []), None
    except Exception as e:
        return [], str(e)

def get_last_run_time(state):
    """Extrahiert Letzte Laufzeit."""
    if not state:
        return None
    
    last_run = state.get('lastRun')
    if last_run:
        try:
            dt = datetime.fromisoformat(last_run.replace('Z', '+00:00'))
            age_mins = (datetime.now().timestamp() - dt.timestamp()) / 60
            if age_mins < 60:
                return f"{age_mins:.0f}m ago"
            elif age_mins < 1440:
                return f"{age_mins/60:.1f}h ago"
            else:
                return f"{age_mins/1440:.1f}d ago"
        except:
            return last_run[:16]
    return None

def format_job_info(job, verbose=False):
    """Formatiert Job Information."""
    name = job.get('name', 'unnamed')
    schedule = job.get('schedule', {})
    cron_expr = schedule.get('expr', '?')
    state = job.get('state', {})
    last_status = state.get('lastRunStatus', '?')
    last_error = state.get('lastError', '')
    last_run = get_last_run_time(state)
    
    # Status emoji
    if last_status == 'ok':
        status = '✅'
    elif last_status == 'error':
        status = '❌'
    else:
        status = '⚠️'
    
    info = f"{status} **{name}**"
    info += f"\n   Schedule: `{cron_expr}`"
    
    if last_run:
        info += f"\n   Last run: {last_run}"
    
    if last_status == 'error' and last_error:
        # Truncate error message
        error_short = last_error[:80] + '...' if len(last_error) > 80 else last_error
        info += f"\n   ❌ Error: `{error_short}`"
    
    return info

def generate_report(format='text', failed_only=False):
    """Generiert Cron Report."""
    now = datetime.now()
    jobs, error = get_cron_status()
    
    if error:
        return f"❌ Error: {error}", 1
    
    enabled = [j for j in jobs if j.get('enabled', True)]
    disabled = [j for j in jobs if not j.get('enabled', True)]
    failed = [j for j in enabled if j.get('state', {}).get('lastRunStatus') == 'error']
    
    if format == 'telegram':
        lines = []
        lines.append(f"⏰ **Cron Monitor — {now.strftime('%H:%M')}**")
        lines.append("")
        
        lines.append(f"**📊 OVERVIEW:**")
        lines.append(f"• Total: {len(jobs)}")
        lines.append(f"• Enabled: {len(enabled)}")
        lines.append(f"• Disabled: {len(disabled)}")
        lines.append(f"• Failed: {len(failed)}")
        lines.append("")
        
        # Failed jobs
        if failed:
            lines.append("**❌ FAILED JOBS:**")
            for job in failed:
                lines.append(format_job_info(job))
                lines.append("")
        
        # If not failed_only, show all enabled
        if not failed_only and enabled:
            lines.append("**✅ ACTIVE JOBS:**")
            for job in enabled:
                if job.get('state', {}).get('lastRunStatus') != 'error':
                    lines.append(format_job_info(job))
                    lines.append("")
        
        # Disabled
        if disabled and not failed_only:
            lines.append("**❌ DISABLED:**")
            for job in disabled:
                lines.append(f"   • {job.get('name', 'unnamed')}")
        
        # Summary
        lines.append("━" * 20)
        if len(failed) == 0:
            lines.append("✅ All crons healthy")
        else:
            lines.append(f"⚠️ {len(failed)} cron(s) failed")
        
        return "\n".join(lines), len(failed)
    
    else:
        lines = []
        lines.append("=" * 60)
        lines.append(f"Sir HazeClaw Cron Monitor — {now.strftime('%H:%M:%S UTC')}")
        lines.append("=" * 60)
        
        lines.append(f"\nTotal Jobs: {len(jobs)}")
        lines.append(f"  ✅ Enabled: {len(enabled)}")
        lines.append(f"  ❌ Disabled: {len(disabled)}")
        lines.append(f"  ⚠️ Failed: {len(failed)}")
        
        if failed:
            lines.append("\n❌ FAILED JOBS:")
            for job in failed:
                lines.append(format_job_info(job))
                lines.append("")
        
        if not failed_only and enabled:
            lines.append("\n✅ ACTIVE JOBS:")
            for job in enabled:
                if job.get('state', {}).get('lastRunStatus') != 'error':
                    lines.append(format_job_info(job))
                    lines.append("")
        
        if disabled and not failed_only:
            lines.append("\n❌ DISABLED:")
            for job in disabled:
                lines.append(f"   - {job.get('name', 'unnamed')}")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines), len(failed)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Sir HazeClaw Cron Monitor - Improved')
    parser.add_argument('--format', choices=['text', 'telegram'], default='text')
    parser.add_argument('--failed-only', action='store_true', help='Show only failed crons')
    args = parser.parse_args()
    
    report, exit_code = generate_report(args.format, args.failed_only)
    print(report)
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())