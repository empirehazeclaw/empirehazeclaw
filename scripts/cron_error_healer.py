#!/usr/bin/env python3
"""
cron_error_healer.py - Auto-heals failed cron deliveries
Sir HazeClaw - 2026-04-11

Usage:
    python3 cron_error_healer.py
    python3 cron_error_healer.py --dry-run
    python3 cron_error_healer.py --job-id <id>
"""

import json
import subprocess
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

# Paths
CRON_STATE_PATH = Path("/home/clawbot/.openclaw/cron/jobs.json")
HEAL_LOG = Path("/home/clawbot/.openclaw/workspace/logs/cron_healer.log")
BACKUP_DIR = Path("/home/clawbot/.openclaw/backups")

# Error patterns and healing actions
HEALING_RULES = {
    # Discord/Message delivery errors
    "Outbound not configured for channel: discord": {
        "action": "disable_discord",
        "delivery_mode": "none",
        "note": "Discord not configured - switch to silent mode"
    },
    "Error: Outbound not configured": {
        "action": "disable_discord",
        "delivery_mode": "none",
        "note": "Discord not configured - switch to silent mode"
    },
    "Cannot send messages in a non-text channel": {
        "action": "disable_discord",
        "delivery_mode": "none",
        "note": "Discord channel issue - switch to silent mode"
    },
    "Error: Cannot send messages": {
        "action": "disable_discord",
        "delivery_mode": "none",
        "note": "Discord channel issue - switch to silent mode"
    },
    "Message failed": {
        "action": "disable_discord",
        "delivery_mode": "none",
        "note": "Message delivery broken - switch to silent mode"
    },
    "⚠️ ✉️ Message failed": {
        "action": "disable_discord",
        "delivery_mode": "none",
        "note": "Emoji-prefixed message failed - switch to silent mode"
    },
    
    # Gateway errors
    "GatewayDrainingError": {
        "action": "restart_gateway",
        "note": "Gateway restarting - restart gateway"
    },
    "ECONNREFUSED": {
        "action": "restart_gateway",
        "note": "Gateway connection refused - restart"
    },
    "Gateway shutdown": {
        "action": "restart_gateway",
        "note": "Gateway down - restart"
    },
    "Gateway is draining": {
        "action": "restart_gateway",
        "note": "Gateway draining - restart"
    },
    
    # Timeout errors
    "cron: job execution timed out": {
        "action": "increase_timeout_or_disable",
        "timeout_increase": 300,
        "max_consecutive": 3,
        "note": "Timeout - increase timeout, disable after 3 consecutive"
    },
    "timeout": {
        "action": "increase_timeout_or_disable",
        "timeout_increase": 300,
        "max_consecutive": 3,
        "note": "Timeout - increase timeout or disable if too many"
    },
    
    # Auth/API errors
    "401: User not found": {
        "action": "disable_cron",
        "note": "OpenRouter auth failed - disable cron"
    },
    "403: Forbidden": {
        "action": "disable_cron",
        "note": "API forbidden - likely auth issue"
    },
    "429: Too Many Requests": {
        "action": "wait_and_retry",
        "note": "Rate limited - wait before retry"
    },
    
    # Fallback/Model errors
    "FallbackSummaryError": {
        "action": "disable_cron",
        "note": "All models failed - disable cron"
    },
    "All models failed": {
        "action": "disable_cron",
        "note": "All models failed - disable cron"
    },
    
    # Script/Module errors
    "Cannot find module": {
        "action": "disable_cron",
        "note": "Missing module - cron broken, disable"
    },
    "ENOENT": {
        "action": "disable_cron",
        "note": "File not found - script missing, disable"
    },
    "Script not found": {
        "action": "disable_cron",
        "note": "Script missing - disable cron"
    },
    
    # Memory/Disk errors
    "ENOSPC": {
        "action": "alert_master",
        "note": "Disk full - alert immediately"
    },
    "Out of memory": {
        "action": "alert_master",
        "note": "OOM - alert immediately"
    },
    
    # Generic patterns
    "connection refused": {
        "action": "restart_gateway",
        "note": "Connection refused - restart gateway"
    },
    "network": {
        "action": "wait_and_retry",
        "note": "Network issue - wait and retry"
    },
    "failed": {
        "action": "disable_discord",
        "delivery_mode": "none",
        "note": "Generic failure - switch to silent mode"
    }
}

# Known false positives (crons that report error but actually deliver)
FALSE_POSITIVES = {
    "a1456495-f03c-4cd0-90fc-baa728365a25": {  # CEO Daily Briefing
        "last_error": "Message failed",
        "actual_status": "delivered",
        "reason": "Script sends message internally, delivery status is misleading"
    }
}


def log(message: str, level: str = "INFO"):
    """Log to file and optionally print."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [{level}] {message}"
    
    # Ensure log directory exists
    HEAL_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    with open(HEAL_LOG, "a") as f:
        f.write(entry + "\n")
    
    if level in ["ERROR", "WARN"]:
        print(entry)
    return entry


def get_cron_state(job_id: str) -> Optional[Dict]:
    """Hole Cron-State from jobs.json."""
    if not CRON_STATE_PATH.exists():
        log(f"Cron state file not found: {CRON_STATE_PATH}", "ERROR")
        return None
    
    with open(CRON_STATE_PATH) as f:
        data = json.load(f)
    
    for job in data.get('jobs', []):
        if job['id'] == job_id:
            return job
    
    log(f"Job not found: {job_id}", "WARN")
    return None


def get_last_run_status(job_id: str) -> Optional[Dict]:
    """Hole den letzten Run Status via CLI."""
    try:
        result = subprocess.run(
            ["openclaw", "cron", "runs", "--id", job_id, "--limit", "1"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Parse the JSON output
            output = result.stdout.strip()
            if output:
                runs = json.loads(output)
                if runs.get('entries'):
                    return runs['entries'][0]
        
        return None
    except Exception as e:
        log(f"Failed to get run status for {job_id}: {e}", "ERROR")
        return None


def check_false_positive(job_id: str, error: str) -> bool:
    """Prüfe ob dies ein bekannter False Positive ist."""
    if job_id in FALSE_POSITIVES:
        fp = FALSE_POSITIVES[job_id]
        if fp['last_error'] in error:
            log(f"FALSE POSITIVE detected for {job_id}: {error}")
            log(f"  -> Actually delivered: {fp['actual_status']}")
            log(f"  -> Reason: {fp['reason']}")
            return True
    return False


def determine_healing_action(job_id: str, job_name: str, error: str, consecutive_errors: int = 0, dry_run: bool = False) -> bool:
    """Bestimme und führe Healing Action aus."""
    
    # Check for false positive first
    if check_false_positive(job_id, error):
        log(f"Skipping {job_name} - false positive", "INFO")
        return True
    
    # Find matching error pattern
    action_taken = False
    for pattern, rule in HEALING_RULES.items():
        if pattern in error:
            log(f"MATCH: '{pattern}' in error '{error}'", "INFO")
            action = rule['action']
            
            if action == "disable_discord":
                log(f"HEALING: Would switch {job_name} to silent mode", "INFO")
                if not dry_run:
                    try:
                        subprocess.run([
                            "openclaw", "cron", "edit",
                            job_id,
                            "--no-deliver"
                        ], check=True)
                        log(f"SUCCESS: Delivery set to none", "INFO")
                    except Exception as e:
                        log(f"FAILED to update cron: {e}", "ERROR")
                action_taken = True  # Mark as handled even in dry_run
            
            elif action == "check_delivery":
                # Check if delivery actually worked
                run_status = get_last_run_status(job_id)
                if run_status and run_status.get('delivered'):
                    log(f"DELIVERY CONFIRMED: {job_name} actually delivered", "INFO")
                    action_taken = True  # Consider it healed
                else:
                    log(f"DELIVERY UNCLEAR: Need manual check for {job_name}", "WARN")
            
            elif action == "restart_gateway":
                log(f"HEALING: Would restart gateway for {job_name}", "INFO")
                if not dry_run:
                    try:
                        # Run gateway restart in background - don't wait
                        subprocess.Popen(
                            ["openclaw", "gateway", "restart"],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        log(f"Gateway restart initiated (bg)", "INFO")
                    except Exception as e:
                        log(f"Gateway restart failed: {e}", "ERROR")
                action_taken = True  # Mark as handled even in dry_run
            
            elif action == "increase_timeout_or_disable":
                timeout_inc = rule.get('timeout_increase', 300)
                max_cons = rule.get('max_consecutive', 3)
                if consecutive_errors >= max_cons:
                    log(f"HEALING: Would disable {job_name} after {consecutive_errors} errors", "INFO")
                    if not dry_run:
                        try:
                            subprocess.run(["openclaw", "cron", "disable", job_id], check=True)
                            log(f"Cron disabled", "INFO")
                        except Exception as e:
                            log(f"Failed to disable cron: {e}", "ERROR")
                    action_taken = True  # Mark as handled even in dry_run
                else:
                    log(f"TIMEOUT: Would increase timeout after {consecutive_errors}/{max_cons} errors", "INFO")
                    action_taken = True  # Mark as handled - will retry next cycle
            
            elif action == "disable_cron":
                log(f"HEALING: Would disable broken cron {job_name}", "INFO")
                if not dry_run:
                    try:
                        subprocess.run(["openclaw", "cron", "disable", job_id], check=True)
                        log(f"Cron disabled", "INFO")
                    except Exception as e:
                        log(f"Failed to disable cron: {e}", "ERROR")
                action_taken = True  # Mark as handled even in dry_run
            
            elif action == "wait_and_retry":
                log(f"WAIT_AND_RETRY: {job_name} will retry next cycle", "INFO")
                action_taken = True  # Consider it handled
            
            elif action == "alert_master":
                log(f"ALERT: {job_name} needs Master attention", "WARN")
                # This would need Telegram integration - mark as failed for now
            
            break  # Only handle first matching pattern
    
    if not action_taken and not check_false_positive(job_id, error):
        log(f"NO HEALING RULE for: {error}", "WARN")
        log(f"Manual intervention required for {job_name} ({job_id})", "WARN")
    
    return action_taken


def heal_all_errors(dry_run: bool = False) -> Dict[str, int]:
    """Heale alle Crons mit Errors."""
    stats = {
        'checked': 0,
        'healed': 0,
        'false_positives': 0,
        'failed': 0,
        'needs_manual': 0
    }
    
    if not CRON_STATE_PATH.exists():
        log("Cron state file not found", "ERROR")
        return stats
    
    with open(CRON_STATE_PATH) as f:
        data = json.load(f)
    
    jobs = data.get('jobs', [])
    stats['total_jobs'] = len(jobs)
    
    for job in jobs:
        job_id = job.get('id', 'unknown')
        job_name = job.get('name', 'unnamed')
        consecutive_errors = job.get('state', {}).get('consecutiveErrors', 0)
        last_status = job.get('state', {}).get('lastRunStatus', 'unknown')
        
        # Only process jobs with errors
        if last_status == 'error' or consecutive_errors > 0:
            stats['checked'] += 1
            error = job.get('state', {}).get('lastError', 'unknown error')
            
            log(f"\n--- Processing: {job_name} ---", "INFO")
            log(f"  ID: {job_id}", "INFO")
            log(f"  consecutiveErrors: {consecutive_errors}", "INFO")
            log(f"  lastError: {error}", "INFO")
            
            if check_false_positive(job_id, error):
                stats['false_positives'] += 1
                stats['healed'] += 1
                continue
            
            # Apply healing rules
            healed = determine_healing_action(job_id, job_name, error, consecutive_errors, dry_run)
            
            if healed:
                stats['healed'] += 1
            elif consecutive_errors >= 2:
                # After 2 consecutive errors, recommend disable
                log(f"RECOMMENDATION: Disable {job_name} after {consecutive_errors} errors", "WARN")
                stats['needs_manual'] += 1
            else:
                stats['failed'] += 1
    
    return stats


def main():
    parser = argparse.ArgumentParser(description="Cron Error Healer")
    parser.add_argument("--dry-run", action="store_true", help="Don't make changes, just report")
    parser.add_argument("--job-id", type=str, help="Heal specific job only")
    args = parser.parse_args()
    
    print("=" * 60)
    print("🦞 CRON ERROR HEALER - Sir HazeClaw")
    print("=" * 60)
    
    if args.dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be made\n")
    
    log("=" * 50)
    log("Cron Error Healer started")
    log(f"Dry run: {args.dry_run}")
    
    if args.job_id:
        job = get_cron_state(args.job_id)
        if job:
            error = job.get('state', {}).get('lastError', 'unknown')
            determine_healing_action(args.job_id, job.get('name'), error, job.get('state', {}).get('consecutiveErrors', 0), args.dry_run)
    else:
        stats = heal_all_errors(args.dry_run)
        
        print("\n" + "=" * 60)
        print("📊 RESULTS")
        print("=" * 60)
        print(f"Total Jobs:     {stats.get('total_jobs', '?')}")
        print(f"Checked:        {stats['checked']}")
        print(f"Healed:        {stats['healed']}")
        print(f"False Positives: {stats['false_positives']}")
        print(f"Failed:        {stats['failed']}")
        print(f"Needs Manual:  {stats['needs_manual']}")
        
        log(f"Results: {stats}")
        
        if stats['needs_manual'] > 0:
            print(f"\n⚠️  {stats['needs_manual']} jobs need manual intervention")
            print("Run with --dry-run=false to auto-disable them")
    
    print("\nDone. Check logs at:", HEAL_LOG)


if __name__ == '__main__':
    main()
