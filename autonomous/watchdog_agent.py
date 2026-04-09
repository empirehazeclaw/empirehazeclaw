#!/usr/bin/env python3
"""
🐕 Watchdog Agent
Dead Man's Switch für autonomous_loop.py

Prüft ob autonomous_loop noch lebt:
- Checkt Process ID
- Checkt Letzte Log-Aktivität
- Wenn tot: Restart via subprocess
- Wenn Restart fehlschlägt: Alert

Usage:
    python3 watchdog_agent.py [--status] [--force-restart] [--test]
    --status       : Zeigt aktuellen Status
    --force-restart: Erzwingt Neustart
    --test         : Testet nur, kein Actual

Crontab:
    */5 * * * * /home/clawbot/.openclaw/workspace/scripts/watchdog.sh
"""

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# === CONFIG ===
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
LOGS_DIR = WORKSPACE / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

AUTONOMOUS_LOOP_SCRIPT = WORKSPACE / "autonomous_loop.py"
HEARTBEAT_FILE = LOGS_DIR / "heartbeat.log"  # We'll create this for monitoring
LOG_FILE = LOGS_DIR / "watchdog.log"
ALERT_LOG = LOGS_DIR / "watchdog_alerts.log"

DEFAULT_THRESHOLD_SECONDS = 15 * 60  # 15 minutes
PROCESS_NAME = "autonomous_loop.py"


def log(msg: str, file: Path = LOG_FILE):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(file, "a") as f:
        f.write(line + "\n")


def alert(msg: str):
    """Log alert to dedicated alert file"""
    log(f"🚨 ALERT: {msg}", file=ALERT_LOG)
    
    # Try webhook alert
    try:
        webhook = os.environ.get("ALERT_WEBHOOK_URL")
        if webhook:
            import requests
            alert_msg = f"🤖 Watchdog Alert:\n{msg}"
            requests.post(webhook, json={"text": alert_msg}, timeout=5)
    except Exception as e:
        log(f"   (Webhook failed: {e})")


def get_process_pids():
    """Find all PIDs of autonomous_loop.py"""
    try:
        result = subprocess.run(
            ["pgrep", "-f", PROCESS_NAME],
            capture_output=True, text=True
        )
        pids = [int(p) for p in result.stdout.strip().split("\n") if p]
        return pids
    except Exception:
        return []


def is_process_running():
    """Check if autonomous_loop.py process is running"""
    return len(get_process_pids()) > 0


def get_last_log_time():
    """Get timestamp of last log entry in autonomous_loop.log"""
    log_path = LOGS_DIR / "autonomous_loop.log"
    if not log_path.exists():
        return None
    
    try:
        # Check file modification time as proxy
        mtime = log_path.stat().st_mtime
        return datetime.fromtimestamp(mtime)
    except Exception:
        return None


def get_last_log_entry():
    """Get the last log line from autonomous_loop.log"""
    log_path = LOGS_DIR / "autonomous_loop.log"
    if not log_path.exists():
        return None
    
    try:
        with open(log_path, "r") as f:
            lines = f.readlines()
            if lines:
                return lines[-1].strip()
    except Exception:
        pass
    return None


def get_heartbeat_time():
    """Get timestamp from dedicated heartbeat file if exists"""
    if not HEARTBEAT_FILE.exists():
        return None
    
    try:
        with open(HEARTBEAT_FILE, "r") as f:
            content = f.read().strip()
            if content:
                return datetime.fromisoformat(content)
    except Exception:
        pass
    return None


def write_heartbeat():
    """Write current timestamp to heartbeat file"""
    with open(HEARTBEAT_FILE, "w") as f:
        f.write(datetime.now().isoformat())


def is_stale(threshold_seconds: int = DEFAULT_THRESHOLD_SECONDS):
    """Check if autonomous_loop is stale (heartbeat too old)"""
    now = datetime.now()
    
    # Check heartbeat file first (if autonomous_loop creates one)
    hb_time = get_heartbeat_time()
    if hb_time:
        age = (now - hb_time).total_seconds()
        return age > threshold_seconds
    
    # Fallback: check log file modification time
    last_log = get_last_log_time()
    if last_log is None:
        return True  # No heartbeat, no log = definitely stale
    
    age = (now - last_log).total_seconds()
    return age > threshold_seconds


def restart_autonomous_loop():
    """Attempt to restart autonomous_loop.py"""
    log("Attempting to restart autonomous_loop.py...")
    
    try:
        # Start the script in background
        proc = subprocess.Popen(
            [sys.executable, str(AUTONOMOUS_LOOP_SCRIPT)],
            cwd=str(WORKSPACE),
            stdout=open(LOGS_DIR / "autonomous_loop.log", "a"),
            stderr=subprocess.STDOUT,
            start_new_session=True
        )
        
        # Wait a moment to see if it crashes immediately
        time.sleep(2)
        
        # Check if still running
        if is_process_running():
            log("✅ autonomous_loop.py restarted successfully")
            return True
        else:
            log("❌ autonomous_loop.py started but crashed")
            return False
            
    except Exception as e:
        log(f"❌ Failed to restart: {e}")
        return False


def send_critical_alert(reason: str):
    """Send critical alert when watchdog can't recover"""
    msg = f"WATCHDOG FAILURE: {reason}\n"
    msg += f"Time: {datetime.now().isoformat()}\n"
    msg += f"Action: Manual intervention required!"
    alert(msg)


def status():
    """Show current status without taking action"""
    print("\n" + "="*50)
    print("🐕 WATCHDOG STATUS")
    print("="*50)
    
    # Process status
    pids = get_process_pids()
    if pids:
        print(f"✅ Process running: PIDs {pids}")
    else:
        print("❌ Process NOT running")
    
    # Heartbeat
    hb_time = get_heartbeat_time()
    if hb_time:
        print(f"📝 Heartbeat file: {hb_time.isoformat()}")
    else:
        print("📝 Heartbeat file: NOT FOUND")
    
    # Last log
    last_log = get_last_log_entry()
    if last_log:
        print(f"📄 Last log entry: {last_log[:80]}...")
    
    last_log_time = get_last_log_time()
    if last_log_time:
        age = (datetime.now() - last_log_time).total_seconds()
        age_min = age / 60
        print(f"📄 Log age: {age_min:.1f} minutes")
        
        if age_min > 15:
            print(f"⚠️  WARNING: Log is {age_min:.1f} min old (>15 min threshold)")
        else:
            print(f"✅ Log is fresh ({age_min:.1f} min old)")
    
    # Threshold
    print(f"⚙️  Threshold: {DEFAULT_THRESHOLD_SECONDS/60} minutes")
    
    # Staleness
    stale = is_stale()
    if stale:
        print("🔴 STATUS: STALE (action needed)")
    else:
        print("🟢 STATUS: HEALTHY")
    
    print("="*50 + "\n")
    
    return 0 if not stale else 1


def test_mode():
    """Test watchdog logic without taking action"""
    log("TEST MODE - No actions will be taken")
    
    stale = is_stale()
    log(f"Stale check: {stale}")
    log(f"Process running: {is_process_running()}")
    
    pids = get_process_pids()
    for pid in pids:
        log(f"  PID {pid}: running")
    
    log(f"Last log entry: {get_last_log_entry()}")
    log(f"Heartbeat time: {get_heartbeat_time()}")
    
    return 0


def watch():
    """Main watchdog check and recovery logic"""
    log("🐕 Watchdog check started")
    
    # Write our own heartbeat first (we're alive)
    write_heartbeat()
    
    # Check if autonomous_loop is running
    if not is_process_running():
        log("❌ autonomous_loop.py is NOT running!")
        
        # Try to restart
        if restart_autonomous_loop():
            alert("autonomous_loop.py was dead - WATCHDOG RESTORED IT")
            log("✅ Recovery successful")
            return 0
        else:
            # Restart failed
            alert("CRITICAL: autonomous_loop.py is DEAD and RESTART FAILED!")
            send_critical_alert("Restart failed - manual intervention required")
            return 2
    
    # Check if heartbeat is stale (even if running, it might be hung)
    if is_stale():
        log("⚠️ autonomous_loop.py is STALE (no recent activity)")
        
        # Force restart
        if restart_autonomous_loop():
            alert("autonomous_loop.py was stale - WATCHDOG RESTORED IT")
            log("✅ Recovery successful (was stale)")
            return 0
        else:
            alert("CRITICAL: autonomous_loop.py restart on stale FAILED!")
            return 2
    
    log("✅ autonomous_loop.py is healthy")
    return 0


def force_restart():
    """Force restart autonomous_loop.py"""
    log("FORCE RESTART requested")
    
    # Kill existing processes
    pids = get_process_pids()
    for pid in pids:
        try:
            log(f"Killing PID {pid}")
            os.kill(pid, 9)
        except Exception as e:
            log(f"  Could not kill {pid}: {e}")
    
    time.sleep(1)
    
    # Restart
    if restart_autonomous_loop():
        log("✅ Force restart successful")
        return 0
    else:
        log("❌ Force restart failed")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Watchdog for autonomous_loop.py")
    parser.add_argument("--status", action="store_true", help="Show status only")
    parser.add_argument("--force-restart", action="store_true", help="Force restart")
    parser.add_argument("--test", action="store_true", help="Test mode (no actions)")
    
    args = parser.parse_args()
    
    if args.status:
        return status()
    elif args.test:
        return test_mode()
    elif args.force_restart:
        return force_restart()
    else:
        return watch()


if __name__ == "__main__":
    sys.exit(main())
