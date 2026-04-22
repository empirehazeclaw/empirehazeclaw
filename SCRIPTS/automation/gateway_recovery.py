#!/usr/bin/env python3
"""
Sir HazeClaw Gateway Auto-Recovery

Gateway's /health endpoint (port 18789) returns {"ok":true,"status":"live"}
EVEN during draining — it never shows a "draining" status.

Therefore the only reliable way to detect restart-in-progress is:
  1. Old gateway PID is still alive  → drain/restart in progress (DON'T restart again)
  2. Old gateway PID is gone + no new health → truly DOWN (restart needed)
  3. Old gateway PID is gone + new health → recovered

Usage:
    python3 gateway_recovery.py
    python3 gateway_recovery.py --check-only
    python3 gateway_recovery.py --force-restart
    python3 gateway_recovery.py --status
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
RETRY_DELAY = 10  # seconds between restart attempts
ALERT_THRESHOLD = 3
DRAIN_TIMEOUT = 90  # seconds to wait for old gateway to exit


def log(message, level="INFO"):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat()
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] [{level}] {message}\n")


def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "consecutive_failures": 0,
        "last_check": None,
        "last_restart": None,
        "recovery_count_today": 0,
        "alert_sent": False,
        "restart_in_progress": False,
    }


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def get_openclaw_pids():
    """Get all openclaw gateway PIDs. Returns list of ints."""
    try:
        result = subprocess.run(
            ['pgrep', '-f', 'openclaw-gateway'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return [int(p) for p in result.stdout.strip().split('\n') if p]
    except (subprocess.CalledProcessError, ValueError, OSError):
        pass
    return []


def is_gateway_healthy():
    """Check if gateway is responding to /health."""
    try:
        result = subprocess.run(
            ['curl', '-s', '-f', HEALTH_URL],
            capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0 and 'ok' in result.stdout.lower()
    except (subprocess.CalledProcessError, OSError, FileNotFoundError):
        return False


def wait_for_pid_gone(pid, timeout=90, interval=3):
    """Wait for a specific PID to exit. Returns True if gone, False if timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            subprocess.run(['kill', '-0', str(pid)], capture_output=True, timeout=2)
        except (subprocess.CalledProcessError, OSError):
            return True
        time.sleep(interval)
    return False


def wait_for_health(timeout=90, interval=3):
    """Wait for /health to return OK. Returns True if healthy, False if timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if is_gateway_healthy():
            return True
        time.sleep(interval)
    return False


def kill_gateway_processes():
    """Force-kill all openclaw gateway processes. Returns number killed."""
    pids = get_openclaw_pids()
    killed = 0
    for pid in pids:
        try:
            subprocess.run(['kill', '-9', str(pid)], capture_output=True, timeout=5)
            killed += 1
        except (subprocess.CalledProcessError, OSError):
            pass
    return killed


def restart_gateway_service():
    """Restart openclaw-gateway via systemctl. Returns True if command succeeded."""
    try:
        result = subprocess.run(
            ['systemctl', '--user', 'restart', 'openclaw-gateway'],
            capture_output=True, timeout=30
        )
        return result.returncode == 0
    except (subprocess.CalledProcessError, OSError):
        return False


def run_recovery():
    """
    Recovery logic based on PID + health, NOT health-status string.

    State machine:
      - PIDs > 0 AND health = True  → healthy, reset counters
      - PIDs > 0 AND health = False → draining/restarting (wait, don't restart)
      - PIDs = 0 AND health = True  → new gateway just started (wait for stable)
      - PIDs = 0 AND health = False → DOWN, restart needed
    """
    state = load_state()
    state["last_check"] = datetime.now().isoformat()

    print("🔍 Checking Gateway...")
    log("Running gateway health check")

    pids = get_openclaw_pids()
    healthy = is_gateway_healthy()

    if pids and healthy:
        # Normal: gateway running and healthy
        print(f"✅ Gateway healthy (PID(s): {pids})")
        log(f"Gateway healthy, PIDs={pids}")
        state["consecutive_failures"] = 0
        state["alert_sent"] = False
        state["restart_in_progress"] = False
        save_state(state)
        return True

    if pids and not healthy:
        # Gateway process running but not responding — likely restarting/draining
        # DON'T kill or restart — wait for it to finish
        print(f"⏳ Gateway PID(s) {pids} alive but not responding — drain in progress...")
        log(f"Gateway draining, PIDs={pids}, waiting up to {DRAIN_TIMEOUT}s")
        state["restart_in_progress"] = True
        save_state(state)

        # Wait for old PIDs to exit
        all_gone = all(wait_for_pid_gone(pid, timeout=DRAIN_TIMEOUT) for pid in pids)
        if all_gone:
            print("✅ Old gateway exited, waiting for new gateway to start...")
            log("Old gateway exited, waiting for new gateway")
            # Now wait for new gateway to come up
            if wait_for_health(timeout=DRAIN_TIMEOUT):
                print("✅ New gateway is healthy!")
                log("New gateway healthy after restart")
                state["consecutive_failures"] = 0
                state["restart_in_progress"] = False
                save_state(state)
                return True
            else:
                print("❌ New gateway did not start in time")
                log("New gateway failed to start within timeout", "ERROR")
        else:
            print("⚠️ Old gateway still running after drain timeout — force killing")
            log("Old gateway did not exit, force killing", "WARN")
            killed = kill_gateway_processes()
            log(f"Force killed {killed} process(es)")
            time.sleep(2)

        # Fall through to restart
        save_state(state)

    if not pids and healthy:
        # No PID but healthy — new gateway starting up (orphan from previous attempt?)
        print("⏳ Gateway starting up (no PID tracked)...")
        log("Gateway starting, waiting for stable PID")
        if wait_for_health(timeout=DRAIN_TIMEOUT):
            pids_new = get_openclaw_pids()
            print(f"✅ Gateway stable (PID(s): {pids_new})")
            log(f"Gateway stable, PIDs={pids_new}")
            state["consecutive_failures"] = 0
            state["restart_in_progress"] = False
            save_state(state)
            return True

    # DOWN: no PID and not healthy
    print(f"❌ Gateway DOWN (PIDs={pids}, healthy={healthy})")
    log(f"Gateway DOWN, PIDs={pids}", "WARN")
    state["consecutive_failures"] += 1
    state["restart_in_progress"] = True

    # Ensure old PIDs are gone before restarting
    if pids:
        print(f"🔪 Killing stale PIDs: {pids}")
        log(f"Killing stale PIDs: {pids}")
        kill_gateway_processes()
        time.sleep(2)

    # Try restart
    print(f"🔄 Restarting (attempt {state['consecutive_failures']}/{MAX_RETRIES})...")
    log(f"Restart attempt {state['consecutive_failures']}")

    if restart_gateway_service():
        state["last_restart"] = datetime.now().isoformat()
        state["recovery_count_today"] += 1
        save_state(state)

        print("✅ Restart command sent, waiting for new gateway...")
        if wait_for_health(timeout=DRAIN_TIMEOUT):
            pids_new = get_openclaw_pids()
            print(f"✅ Gateway recovered (PID(s): {pids_new})")
            log(f"Gateway recovered, PIDs={pids_new}")
            state["consecutive_failures"] = 0
            state["restart_in_progress"] = False
            save_state(state)
            return True

        print(f"⚠️ Gateway still not healthy after {DRAIN_TIMEOUT}s")
        log("Restart command sent but gateway not healthy within timeout", "ERROR")
    else:
        log("Restart command failed", "ERROR")

    # Still failing
    if state["consecutive_failures"] >= ALERT_THRESHOLD and not state.get("alert_sent"):
        print("🚨 Sending alert to Master...")
        msg = (f"Gateway DOWN: {state['consecutive_failures']} consecutive failures. "
               f"Last restart: {state.get('last_restart', 'never')}")
        send_telegram_alert(msg)
        state["alert_sent"] = True
        log("Alert sent to Master", "WARN")

    save_state(state)
    return False


def send_telegram_alert(message):
    try:
        subprocess.run(
            ['openclaw', 'message', 'send', '--to', '5392634979', '--message', f"🚨 {message}"],
            capture_output=True, timeout=15
        )
        return True
    except (subprocess.CalledProcessError, OSError, FileNotFoundError):
        return False


def check_only():
    pids = get_openclaw_pids()
    healthy = is_gateway_healthy()
    if pids and healthy:
        print(f"✅ Gateway: HEALTHY (PIDs: {pids})")
    elif pids:
        print(f"⏳ Gateway: ALIVE but not responding (PIDs: {pids}) — draining/restarting")
    else:
        print(f"❌ Gateway: DOWN (no PID, healthy={healthy})")
    return bool(pids and healthy)


def force_restart():
    print("🔄 Force restarting gateway...")
    pids = get_openclaw_pids()
    if pids:
        print(f"   Killing PIDs: {pids}")
        kill_gateway_processes()
        time.sleep(2)

    print("   Sending restart command...")
    if restart_gateway_service():
        print("   ✅ Restart command sent, waiting...")
        if wait_for_health(timeout=DRAIN_TIMEOUT):
            pids_new = get_openclaw_pids()
            print(f"✅ Gateway recovered (PIDs: {pids_new})")
            return True

    print("❌ Restart failed or timeout")
    return False


def show_status():
    state = load_state()
    pids = get_openclaw_pids()
    healthy = is_gateway_healthy()

    print("📊 Gateway Auto-Recovery Status")
    print(f"   Gateway PIDs:   {pids or 'none'}")
    print(f"   /health:       {'✅ OK' if healthy else '❌ FAIL'}")
    print(f"   Consecutive Failures: {state['consecutive_failures']}")
    print(f"   Last Check:    {state['last_check'] or 'never'}")
    print(f"   Last Restart:  {state['last_restart'] or 'never'}")
    print(f"   Recovery Count Today: {state['recovery_count_today']}")
    print(f"   Restart In Progress:  {state.get('restart_in_progress', False)}")
    print(f"   Alert Sent:    {state['alert_sent']}")
    print()
    if pids and healthy:
        print("   Gateway: ✅ LIVE")
    elif pids and not healthy:
        print("   Gateway: ⏳ DRAINING/RESTARTING")
    else:
        print("   Gateway: ❌ DOWN")


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
