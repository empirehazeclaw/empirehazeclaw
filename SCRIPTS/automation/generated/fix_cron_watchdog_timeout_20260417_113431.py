```python
#!/usr/bin/env python3
"""
Cron Watchdog - Fix timeout error in cron_watchdog script
Monitors cron service and restarts if needed
"""

import subprocess
import sys
import time
import os
import signal
import argparse
from datetime import datetime
from pathlib import Path

# Configuration
LOG_FILE = "/var/log/cron_watchdog.log"
DEFAULT_TIMEOUT = 300  # 5 minutes
MAX_RESTART_ATTEMPTS = 3
CHECK_INTERVAL = 60


def log(message: str, level: str = "INFO"):
    """Log message to file and stdout"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    print(log_entry)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(log_entry + "\n")
    except Exception as e:
        print(f"Warning: Could not write to log file: {e}")


def run_command(cmd: list, timeout: int = 30) -> tuple:
    """Run system command with timeout and error handling"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        log(f"Command timed out: {' '.join(cmd)}", "ERROR")
        return False, "", "Command timed out"
    except FileNotFoundError:
        log(f"Command not found: {cmd[0]}", "ERROR")
        return False, "", f"Command not found: {cmd[0]}"
    except Exception as e:
        log(f"Error running command: {e}", "ERROR")
        return False, "", str(e)


def check_cron_status() -> bool:
    """Check if cron service is running"""
    log("Checking cron service status...")
    
    # Try different methods based on init system
    for cmd in [
        ["systemctl", "is-active", "cron"],
        ["systemctl", "is-active", "crond"],
        ["service", "cron", "status"],
        ["pgrep", "-x", "cron"],
        ["pgrep", "-x", "crond"]
    ]:
        success, stdout, stderr = run_command(cmd, timeout=10)
        if success or (stdout and "active" in stdout.lower()):
            log("Cron service is running")
            return True
        if success and stdout.strip():
            log("Cron service appears active")
            return True
    
    log("Cron service is NOT running", "WARNING")
    return False


def get_cron_processes() -> list:
    """Get list of running cron processes"""
    success, stdout, _ = run_command(["pgrep", "-a", "cron"], timeout=10)
    if success and stdout:
        processes = []
        for line in stdout.strip().split("\n"):
            if line:
                parts = line.split(None, 1)
                if len(parts) >= 1:
                    processes.append({
                        "pid": parts[0],
                        "cmd": parts[1] if len(parts) > 1 else ""
                    })
        return processes
    return []


def kill_stale_process(pid: str, timeout: int = 10) -> bool:
    """Kill a stale cron process"""
    log(f"Attempting to kill stale process: {pid}", "WARNING")
    
    try:
        # Try graceful termination first
        run_command(["kill", pid], timeout=5)
        time.sleep(2)
        
        # Check if still running
        success, _, _ = run_command(["kill", "-0", pid], timeout=5)
        if not success:
            log(f"Process {pid} terminated successfully")
            return True
        
        # Force kill if still running
        log(f"Force killing process {pid}", "WARNING")
        run_command(["kill", "-9", pid], timeout=5)
        time.sleep(1)
        
        # Verify termination
        success, _, _ = run_command(["kill", "-0", pid], timeout=5)
        return not success
        
    except Exception as e:
        log(f"Error killing process {pid}: {e}", "ERROR")
        return False


def restart_cron_service(restart_count: int) -> bool:
    """Restart the cron service"""
    log(f"Attempting to restart cron service (attempt {restart_count}/{MAX_RESTART_ATTEMPTS})", "WARNING")
    
    # Try different restart methods
    restart_methods = [
        ["systemctl", "restart", "cron"],
        ["systemctl", "restart", "crond"],
        ["service", "cron", "restart"],
        ["service", "crond", "restart"],
        ["/etc/init.d/cron", "restart"],
        ["/etc/init.d/crond", "restart"]
    ]
    
    for cmd in restart_methods:
        success, stdout, stderr = run_command(cmd, timeout=30)
        if success:
            log(f"Cron service restarted successfully using: {' '.join(cmd)}")
            time.sleep(5)  # Wait for service to initialize
            return check_cron_status()
        else:
            log(f"Restart method failed: {' '.join(cmd)} - {stderr}", "WARNING")
    
    log("All restart methods failed", "ERROR")
    return False


def check_cron_log_for_errors() -> list:
    """Check cron logs for timeout or error messages"""
    log("Checking cron logs for errors...")
    errors = []
    
    # Common log locations
    log_locations = [
        "/var/log/cron",
        "/var/log/cron.log",
        "/var/log/syslog",
        "/var/log/system.log"
    ]
    
    for log_file in log_locations:
        if os.path.exists(log_file):
            try:
                # Get last 100 lines for errors
                success, stdout, _ = run_command(
                    ["tail", "-n", "100", log_file],
                    timeout=10
                )
                if success:
                    for line in stdout.split("\n"):
                        if any(keyword in line.lower() for keyword in 
                               ["timeout", "error", "failed", "dead", "stale"]):
                            errors.append(line.strip())
            except Exception as e:
                log(f"Error reading log {log_file}: {e}", "WARNING")
    
    if errors:
        log(f"Found {len(errors)} potential issues in logs", "WARNING")
        for error in errors[:5]:  # Log first 5 errors
            log(f"  {error}", "WARNING")
    
    return errors


def fix_watchdog_timeout(timeout_value: int = DEFAULT_TIMEOUT) -> bool:
    """
    Main function to fix cron watchdog timeout issues
    """
    log("=" * 50)
    log("Starting Cron Watchdog Fix")
    log("=" * 50)
    
    try:
        # Step 1: Check current cron status
        if not check_cron_status():
            log("Cron not running, attempting to start...", "WARNING")
            if not restart_cron_service(0):
                log("Failed to start cron service", "ERROR")
                return False
        
        # Step 2: Check for stale processes
        processes = get_cron_processes()
        log(f"Found {len(processes)} cron processes running")
        
        # Step 3: Check logs for errors
        errors = check_cron_log_for_errors()
        
        # Step 4: Restart if needed based on findings
        if not processes or errors:
            restart_count = 1
            while restart_count <= MAX_RESTART_ATTEMPTS:
                if restart_cron_service(restart_count):
                    log("Cron service successfully restarted and verified")
                    return True
                restart_count += 1
                time.sleep(5)
            
            log("Failed to restart cron after maximum attempts", "ERROR")
            return False
        
        log("Cron watchdog fix completed successfully")
        return True
        
    except Exception as e:
        log(f"Unexpected error in watchdog fix: {e}", "ERROR")
        return False


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    log("Received shutdown signal, cleaning up...", "WARNING")
    sys.exit(0)


def main():
    """Main entry point with CLI argument handling"""
    parser = argparse.ArgumentParser(
        description="Cron Watchdog - Fix timeout errors in cron service"
    )
    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Timeout value in seconds (default: {DEFAULT_TIMEOUT})"
    )
    parser.add_argument(