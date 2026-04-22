#!/usr/bin/env python3
"""
Sir HazeClaw Gateway Auto-Recovery

Gateway's /health endpoint returns {"ok":true,"status":"live"|"draining"|"stopped"}.
The `status` field is the authoritative drain indicator — "draining" means a restart
is in progress and we should NOT intervene.

The only reliable way to detect restart-in-progress is:
  1. Old gateway PID is still alive + status='draining' → restart in progress (DON'T restart)
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


def get_gateway_status():
    """
    Returns ('live'|'draining'|'stopped'|None, full_response_dict|None).
    The /health endpoint NEVER lies — "ok" is always true during drain.
    The status field is the authoritative drain indicator.
    """
    try:
        result = subprocess.run(
            ['curl', '-s', HEALTH_URL],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            return 'stopped', None
        data = json.loads(result.stdout)
        status = data.get('status', 'live')
        return status, data
    except (subprocess.CalledProcessError, OSError, FileNotFoundError, json.JSONDecodeError):
        return 'stopped', None


def is_gateway_live():
    """Returns True only if gateway is LIVE (not draining, not stopped)."""
    status, _ = get_gateway_status()
    return status == 'live'


def is_gateway_draining():
    """Returns True if gateway is in the process of draining/restarting."""
    status, _ = get_gateway_status()
    return status == 'draining'


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


def wait_for_live(timeout=90, interval=3):
    """Wait for /health to return status='live'. Returns True if live, False if timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        status, _ = get_gateway_status()
        if status == 'live':
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
    Recovery logic based on PID + explicit status field from /health.

    State machine:
      - PIDs > 0 AND status='live' → healthy, reset counters
      - PIDs > 0 AND status='draining' → restart in progress (wait, DON'T restart)
      - PIDs > 0 AND health fails → draining/restarting (wait, don't restart)
      - PIDs = 0 AND status='live' → new gateway starting (wait for stable)
      - PIDs = 0 AND health fails → DOWN, restart needed
    """
    state = load_state()
    state["last_check"] = datetime.now().isoformat()

    print("🔍 Checking Gateway...")
    log("Running gateway health check")

    pids = get_openclaw_pids()
    status, health_data = get_gateway_status()
    draining = is_gateway_draining()

    if pids and status == 'live':
        # Normal: gateway running and LIVE
        print(f"✅ Gateway LIVE (PID(s): {pids})")
        log(f"Gateway live, PIDs={pids}")
        state["consecutive_failures"] = 0
        state["alert_sent"] = False
        state["restart_in_progress"] = False
        save_state(state)
        return True

    if pids and draining:
        # Gateway is draining — restart in progress, DON'T interfere
        print(f"⏳ Gateway PID(s) {pids} — status='draining' (restart in progress, waiting)")
        log(f"Gateway draining, PIDs={pids}, waiting up to {DRAIN_TIMEOUT}s")
        state["restart_in_progress"] = True
        save_state(state)

        # Wait for old PIDs to exit
        all_gone = all(wait_for_pid_gone(pid, timeout=DRAIN_TIMEOUT) for pid in pids)
        if all_gone:
            print("✅ Old gateway exited, waiting for new gateway to start...")
            log("Old gateway exited, waiting for new gateway")
            if wait_for_live(timeout=DRAIN_TIMEOUT):
                pids_new = get_openclaw_pids()
                print(f"✅ New gateway is LIVE (PID(s): {pids_new})")
                log(f"New gateway live after restart, PIDs={pids_new}")
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
        save_state(state)

    if not pids:
        # No PID tracked — check if a new gateway started without us noticing
        if status == 'live':
            print("⏳ Gateway starting up (no PID tracked yet)...")
            log("Gateway starting, waiting for stable PID")
            if wait_for_live(timeout=DRAIN_TIMEOUT):
                pids_new = get_openclaw_pids()
                print(f"✅ Gateway stable (PID(s): {pids_new})")
                log(f"Gateway stable, PIDs={pids_new}")
                state["consecutive_failures"] = 0
                state["restart_in_progress"] = False
                save_state(state)
                return True
        # DOWN: no PID and not live
        print(f"❌ Gateway DOWN (PIDs={pids}, status={status})")
        log(f"Gateway DOWN, PIDs={pids}, status={status}", "WARN")
        state["consecutive_failures"] += 1
        state["restart_in_progress"] = True

        if pids:
            print(f"🔪 Killing stale PIDs: {pids}")
            log(f"Killing stale PIDs: {pids}")
            kill_gateway_processes()
            time.sleep(2)

        print(f"🔄 Restarting (attempt {state['consecutive_failures']}/{MAX_RETRIES})...")
        log(f"Restart attempt {state['consecutive_failures']}")

        if restart_gateway_service():
            state["last_restart"] = datetime.now().isoformat()
            state["recovery_count_today"] += 1
            save_state(state)

            print("✅ Restart command sent, waiting for new gateway...")
            if wait_for_live(timeout=DRAIN_TIMEOUT):
                pids_new = get_openclaw_pids()
                print(f"✅ Gateway recovered (PID(s): {pids_new})")
                log(f"Gateway recovered, PIDs={pids_new}")
                state["consecutive_failures"] = 0
                state["restart_in_progress"] = False
                save_state(state)
                return True

            print(f"⚠️ Gateway still not live after {DRAIN_TIMEOUT}s")
            log("Restart command sent but gateway not live within timeout", "ERROR")
        else:
            log("Restart command failed", "ERROR")

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
    status, data = get_gateway_status()
    if status == 'live' and pids:
        print(f"✅ Gateway: LIVE (PIDs: {pids})")
    elif status == 'draining':
        print(f"⏳ Gateway: DRAINING (PIDs: {pids}) — restart in progress, do NOT干预")
    elif pids:
        print(f"⚠️ Gateway: UNKNOWN status={status} (PIDs: {pids})")
    else:
        print(f"❌ Gateway: DOWN (no PID, status={status})")
    return status == 'live' and bool(pids)


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
        if wait_for_live(timeout=DRAIN_TIMEOUT):
            pids_new = get_openclaw_pids()
            print(f"✅ Gateway recovered (PIDs: {pids_new})")
            return True

    print("❌ Restart failed or timeout")
    return False


def show_status():
    state = load_state()
    pids = get_openclaw_pids()
    status, data = get_gateway_status()

    print("📊 Gateway Auto-Recovery Status")
    print(f"   Gateway PIDs:   {pids or 'none'}")
    print(f"   /health status: {status}")
    print(f"   Consecutive Failures: {state['consecutive_failures']}")
    print(f"   Last Check:    {state['last_check'] or 'never'}")
    print(f"   Last Restart:  {state['last_restart'] or 'never'}")
    print(f"   Recovery Count Today: {state['recovery_count_today']}")
    print(f"   Restart In Progress:  {state.get('restart_in_progress', False)}")
    print(f"   Alert Sent:    {state['alert_sent']}")
    print()
    if status == 'live' and pids:
        print("   Gateway: ✅ LIVE")
    elif status == 'draining':
        print("   Gateway: ⏳ DRAINING (restart in progress)")
    elif pids:
        print(f"   Gateway: ⚠️ UNKNOWN ({status})")
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
