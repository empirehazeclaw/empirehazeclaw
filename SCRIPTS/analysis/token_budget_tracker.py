#!/usr/bin/env python3
"""
token_budget_tracker.py - Track and control monthly token usage
Sir HazeClaw - 2026-04-11

Usage:
    python3 token_budget_tracker.py              # Check current usage
    python3 token_budget_tracker.py --alert     # Send alert if needed
    python3 token_budget_tracker.py --disable   # Disable non-critical crons
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Budget Configuration
MONTHLY_BUDGET = 5_000_000  # 5M tokens
ALERT_THRESHOLD = 0.80  # 80% = Alert
CRITICAL_THRESHOLD = 0.95  # 95% = Disable non-critical crons

# State file
STATE_FILE = Path("/home/clawbot/.openclaw/workspace/memory/token_budget.json")

# Non-critical crons (can be disabled if budget critical)
NON_CRITICAL_CRONS = [
    "f701b751-a2f0-422f-bf1b-0bd52dff2e01",  # Nightly Dreaming
    "235439f7-67b0-4ffe-a15d-6306afca36aa",  # Security Audit
    "cb2ae8d6-7439-459d-a9c7-4f6042408bc4",  # Evening Capture
]

# Critical crons (never disable)
CRITICAL_CRONS = [
    "c0060c0e-f315-4b07-8b4c-09ee2d571a9b",  # Gateway Recovery
    "21b1dcba-b0ce-489e-9a04-f11636ace430",  # Learning Coordinator
    "6b09e638-52ef-4705-b310-1bb4ad9bba39",  # Health Check
]


def get_current_month() -> str:
    """Get current month in YYYY-MM format."""
    return datetime.now().strftime("%Y-%m")


def load_state() -> Dict:
    """Load state from file."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "current_month": get_current_month(),
        "usage": 0,
        "alerts_sent": [],
        "critical_disabled": False
    }


def save_state(state: Dict):
    """Save state to file."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get_cron_usage() -> Dict[str, int]:
    """Get token usage from cron runs this month."""
    usage = {}
    current_month = get_current_month()
    
    try:
        result = subprocess.run(
            ["openclaw", "cron", "runs", "--limit", "100"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            for entry in data.get('entries', []):
                ts = entry.get('ts', 0)
                run_time = datetime.fromtimestamp(ts/1000)
                
                # Only count this month
                if run_time.strftime("%Y-%m") == current_month:
                    job_id = entry.get('jobId', 'unknown')
                    tokens = entry.get('usage', {}).get('total_tokens', 0)
                    usage[job_id] = usage.get(job_id, 0) + tokens
                    
    except Exception as e:
        print(f"Error getting cron usage: {e}")
    
    return usage


def calculate_total_usage() -> int:
    """Calculate total tokens used this month."""
    usage = get_cron_usage()
    return sum(usage.values())


def check_budget() -> Dict:
    """Check current budget status."""
    state = load_state()
    current_month = get_current_month()
    
    # Reset if new month
    if state.get("current_month") != current_month:
        state = {
            "current_month": current_month,
            "usage": 0,
            "alerts_sent": [],
            "critical_disabled": False
        }
        save_state(state)
    
    # Update usage
    total_usage = calculate_total_usage()
    state["usage"] = total_usage
    
    percentage = total_usage / MONTHLY_BUDGET
    remaining = MONTHLY_BUDGET - total_usage
    
    return {
        "month": current_month,
        "usage": total_usage,
        "budget": MONTHLY_BUDGET,
        "percentage": percentage,
        "remaining": remaining,
        "alerts_sent": state.get("alerts_sent", []),
        "critical_disabled": state.get("critical_disabled", False),
        "status": "OK" if percentage < ALERT_THRESHOLD else 
                  "WARNING" if percentage < CRITICAL_THRESHOLD else 
                  "CRITICAL"
    }


def send_alert(status: Dict):
    """Send alert to master if needed."""
    percentage = status["percentage"]
    
    if percentage >= CRITICAL_THRESHOLD:
        message = f"🚨 TOKEN BUDGET CRITICAL: {percentage:.0%} used ({status['usage']:,}/{status['budget']:,})"
        message += f"\n⚠️ Non-critical crons will be disabled."
    elif percentage >= ALERT_THRESHOLD:
        message = f"⚠️ TOKEN BUDGET WARNING: {percentage:.0%} used ({status['usage']:,}/{status['budget']:,})"
        message += f"\n💡 {status['remaining']:,} tokens remaining"
    else:
        return  # No alert needed
    
    # Send message
    try:
        subprocess.run([
            "openclaw", "send", "--channel", "telegram", 
            "--to", "5392634979", "--message", message
        ], check=True)
        print(f"Alert sent: {message}")
    except Exception as e:
        print(f"Failed to send alert: {e}")


def disable_non_critical():
    """Disable non-critical crons to save budget."""
    print("🚨 Disabling non-critical crons...")
    
    for cron_id in NON_CRITICAL_CRONS:
        try:
            subprocess.run([
                "openclaw", "cron", "disable", cron_id
            ], check=True)
            print(f"  Disabled: {cron_id}")
        except Exception as e:
            print(f"  Failed to disable {cron_id}: {e}")
    
    # Update state
    state = load_state()
    state["critical_disabled"] = True
    state["alerts_sent"].append("critical_disabled")
    save_state(state)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Token Budget Tracker")
    parser.add_argument("--alert", action="store_true", help="Send alert if needed")
    parser.add_argument("--disable", action="store_true", help="Disable non-critical crons")
    parser.add_argument("--status", action="store_true", help="Show current status")
    args = parser.parse_args()
    
    status = check_budget()
    
    print("=" * 50)
    print("🦞 TOKEN BUDGET TRACKER")
    print("=" * 50)
    print(f"Month:          {status['month']}")
    print(f"Usage:          {status['usage']:,} tokens")
    print(f"Budget:         {status['budget']:,} tokens")
    print(f"Percentage:     {status['percentage']:.1%}")
    print(f"Remaining:      {status['remaining']:,} tokens")
    print(f"Status:         {status['status']}")
    
    if args.status:
        return
    
    if args.disable:
        disable_non_critical()
        return
    
    if args.alert:
        send_alert(status)
        
        # Auto-disable if critical
        if status["percentage"] >= CRITICAL_THRESHOLD:
            disable_non_critical()


if __name__ == "__main__":
    main()
