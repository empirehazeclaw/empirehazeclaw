#!/usr/bin/env python3
"""
Sir HazeClaw Gateway Auto-Recovery
Automatisch Gateway neu starten wenn down.

Prüft Gateway Health → Restart wenn FAIL → Alert wenn persistiert.

Usage:
    python3 gateway_recovery.py
    python3 gateway_recovery.py --check-only
    python3 gateway_recovery.py --force-restart
"""

import subprocess
import sys
import time
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
LOG_FILE = WORKSPACE / "logs/gateway_recovery.log"
STATE_FILE = WORKSPACE / "data/gateway_recovery_state.json"

HEALTH_URL = "http://127.0.0.1:18789/health"
MAX_RETRIES = 3
RETRY_DELAY = 10  # seconds
ALERT_THRESHOLD = 3  # Alert after 3 consecutive failures

def log(message, level="INFO"):
    """Log to file."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat()
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] [{level}] {message}\n")

def load_state():
    """Load recovery state."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "consecutive_failures": 0,
        "last_check": None,
        "last_restart": None,
        "recovery_count_today": 0,
        "alert_sent": False
    }

def save_state(state):
    """Save recovery state."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def check_gateway_health():
    """Check if gateway is healthy."""
    try:
        result = subprocess.run(
            ['curl', '-s', '-f', HEALTH_URL],
            capture_output=True,
            text=True,
            timeout=5
        )
        return 'ok' in result.stdout.lower() or 'live' in result.stdout.lower()
    except (subprocess.CalledProcessError, OSError, FileNotFoundError):
        # curl command failed - gateway likely down
        return False

def restart_gateway():
    """Restart gateway service."""
    try:
        # Try openclaw gateway restart first
        result = subprocess.run(
            ['openclaw', 'gateway', 'restart'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return True
    except (subprocess.CalledProcessError, OSError, FileNotFoundError):
        # openclaw gateway restart failed - try systemctl fallback
        pass
    
    # Fallback: systemctl restart
    try:
        subprocess.run(
            ['systemctl', '--user', 'restart', 'openclaw-gateway'],
            capture_output=True,
            timeout=30
        )
        return True
    except (subprocess.CalledProcessError, OSError, FileNotFoundError):
        # systemctl restart failed
        return False

def send_telegram_alert(message):
    """Send alert via Telegram."""
    try:
        import os
        # Use openclaw message tool
        subprocess.run(
            ['openclaw', 'message', 'send', '--to', '5392634979', '--message', f"🚨 {message}"],
            capture_output=True,
            timeout=15
        )
        return True
    except (subprocess.CalledProcessError, OSError, FileNotFoundError):
        # openclaw message send failed
        return False

def run_recovery():
    """Run full recovery check + action."""
    state = load_state()
    state["last_check"] = datetime.now().isoformat()
    
    print("🔍 Checking Gateway Health...")
    log("Running gateway health check")
    
    healthy = check_gateway_health()
    
    if healthy:
        print("✅ Gateway is healthy")
        log("Gateway healthy")
        state["consecutive_failures"] = 0
        state["alert_sent"] = False
        save_state(state)
        return True
    
    # Gateway is DOWN
    print("❌ Gateway is DOWN")
    log("Gateway DOWN", "WARN")
    state["consecutive_failures"] += 1
    
    # Try restart
    print(f"🔄 Attempting restart (attempt {state['consecutive_failures']}/{MAX_RETRIES})...")
    log(f"Restart attempt {state['consecutive_failures']}")
    
    if restart_gateway():
        print("✅ Gateway restart initiated")
        log("Restart initiated")
        state["last_restart"] = datetime.now().isoformat()
        state["recovery_count_today"] += 1
        
        # Wait and verify
        time.sleep(RETRY_DELAY)
        if check_gateway_health():
            print("✅ Gateway recovered!")
            log("Gateway recovered after restart")
            state["consecutive_failures"] = 0
            save_state(state)
            return True
    
    # Still failing
    print(f"⚠️ Restart failed or gateway still down")
    log("Restart failed or gateway still down", "ERROR")
    
    # Check if we need to alert
    if state["consecutive_failures"] >= ALERT_THRESHOLD and not state.get("alert_sent"):
        print("🚨 Sending alert to Master...")
        message = f"Gateway Auto-Recovery: {state['consecutive_failures']} consecutive failures. Last restart: {state.get('last_restart', 'never')}"
        send_telegram_alert(message)
        state["alert_sent"] = True
        log("Alert sent to Master", "WARN")
    
    save_state(state)
    return False

def check_only():
    """Just check health, no action."""
    healthy = check_gateway_health()
    if healthy:
        print("✅ Gateway: HEALTHY")
    else:
        print("❌ Gateway: DOWN")
    return healthy

def force_restart():
    """Force restart without health check."""
    print("🔄 Force restarting gateway...")
    if restart_gateway():
        time.sleep(RETRY_DELAY)
        if check_gateway_health():
            print("✅ Gateway recovered!")
            return True
    print("❌ Restart failed")
    return False

def show_status():
    """Show recovery status."""
    state = load_state()
    
    print("📊 Gateway Auto-Recovery Status")
    print(f"   Consecutive Failures: {state['consecutive_failures']}")
    print(f"   Last Check: {state['last_check'] or 'never'}")
    print(f"   Last Restart: {state['last_restart'] or 'never'}")
    print(f"   Recovery Count Today: {state['recovery_count_today']}")
    print(f"   Alert Sent: {state['alert_sent']}")
    print()
    print(f"   Gateway: {'✅ HEALTHY' if check_gateway_health() else '❌ DOWN'}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        run_recovery()
    elif sys.argv[1] == "--check-only":
        check_only()
    elif sys.argv[1] == "--force-restart":
        force_restart()
    elif sys.argv[1] == "--status":
        show_status()
    elif sys.argv[1] == "--help":
        print(__doc__)
    else:
        print(__doc__)