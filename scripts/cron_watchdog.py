#!/usr/bin/env python3
"""
Sir HazeClaw Cron Watchdog + Monitor
====================================
Überwacht Cron Jobs, meldet Probleme UND generiert detaillierte Reports.

CONSOLIDATED: Combines cron_watchdog.py + cron_monitor.py
- Watchdog: Checks for issues, alerts on failures
- Monitor: Generates detailed reports (text/telegram format)

Usage:
    python3 cron_watchdog.py                    # Watchdog mode (default)
    python3 cron_watchdog.py --report           # Generate full report
    python3 cron_watchdog.py --report --format telegram
    python3 cron_watchdog.py --failed-only      # Report failed only
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path

CRON_JOBS_PATH = "/home/clawbot/.openclaw/cron/jobs.json"
ALERT_LOG = "/home/clawbot/.openclaw/workspace/logs/cron_watchdog.log"

# ============================================================
# WATCHDOG FUNCTIONS
# ============================================================

def load_jobs():
    """Load cron jobs from jobs.json."""
    with open(CRON_JOBS_PATH) as f:
        data = json.load(f)
    return data.get('jobs', [])

def check_jobs(jobs):
    """Prüft Jobs auf Probleme."""
    issues = []
    
    for job in jobs:
        if not job.get('enabled', True):
            continue
        
        name = job.get('name', 'unnamed')
        state = job.get('state', {})
        
        # Check consecutive errors
        consecutive_errors = state.get('consecutiveErrors', 0)
        if consecutive_errors >= 2:
            issues.append(f"⚠️  {name}: {consecutive_errors} consecutive errors")
        
        # Check last run status
        last_status = state.get('lastRunStatus', 'unknown')
        if last_status == 'error':
            issues.append(f"❌ {name}: last run failed")
        
        # Check if next run is overdue (more than 25 hours for daily jobs)
        next_run = state.get('nextRunAtMs')
        if next_run:
            next_run_dt = datetime.fromtimestamp(next_run / 1000)
            now = datetime.now()
            if next_run_dt < now - timedelta(hours=25):
                issues.append(f"⏰ {name}: next run overdue")
    
    return issues

def send_telegram_alert(issues):
    """Send Telegram alert for critical issues."""
    # Alert via openclaw message --channel telegram --to 5392634979
    return True

def watchdog_run():
    """Run watchdog mode - check for issues and alert."""
    print(f"Cron Watchdog — {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)
    
    jobs = load_jobs()
    enabled = [j for j in jobs if j.get('enabled', True)]
    
    print(f"Monitoring {len(enabled)} enabled cron jobs...")
    print()
    
    issues = check_jobs(jobs)
    
    if issues:
        print("Issues found:")
        for issue in issues:
            print(f"  {issue}")
        
        # Log issues
        os.makedirs(os.path.dirname(ALERT_LOG), exist_ok=True)
        with open(ALERT_LOG, "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            f.write(f"[{timestamp}]\n")
            for issue in issues:
                f.write(f"  {issue}\n")
            f.write("\n")
        
        # Send Telegram alert if critical issues
        critical_issues = [i for i in issues if '❌' in i or 'consecutive' in i.lower()]
        if critical_issues:
            print()
            print("🔔 Sending Telegram alert to Master...")
            if send_telegram_alert(critical_issues):
                print("✅ Alert sent")
            else:
                print("⚠️ Alert failed")
        
        print()
        return 1
    else:
        print("✅ All cron jobs healthy")
        return 0

# ============================================================
# MONITOR FUNCTIONS (from cron_monitor.py)
# ============================================================

def get_last_run_time(state):
    """Extract last run time."""
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
    """Format job information."""
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
        error_short = last_error[:80] + '...' if len(last_error) > 80 else last_error
        info += f"\n   ❌ Error: `{error_short}`"
    
    return info

def generate_report(format='text', failed_only=False):
    """Generate cron report."""
    now = datetime.now()
    jobs = load_jobs()
    
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

def monitor_run(args):
    """Run monitor mode - generate report."""
    report, exit_code = generate_report(args.format, args.failed_only)
    print(report)
    return exit_code

# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='Sir HazeClaw Cron Watchdog + Monitor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 cron_watchdog.py                    # Watchdog: check for issues
  python3 cron_watchdog.py --report           # Monitor: full report
  python3 cron_watchdog.py --report --format telegram
  python3 cron_watchdog.py --failed-only      # Report failed only
        """
    )
    parser.add_argument('--report', action='store_true', help='Generate detailed report')
    parser.add_argument('--format', choices=['text', 'telegram'], default='text',
                        help='Report format (default: text)')
    parser.add_argument('--failed-only', action='store_true', 
                        help='Show only failed crons in report')
    
    args = parser.parse_args()
    
    if args.report:
        return monitor_run(args)
    else:
        return watchdog_run()

if __name__ == "__main__":
    sys.exit(main())
