#!/usr/bin/env python3
"""
🔒 Cron Scheduler with Resource Protection
Prevents concurrent heavy job execution.
Uses file locks to ensure only one heavy job runs at a time.

Usage:
    python3 cron_scheduler.py --job night_shift
    python3 cron_scheduler.py --status
"""

import os
import sys
import fcntl
import time
import subprocess
from pathlib import Path
from datetime import datetime

LOCK_DIR = Path("/home/clawbot/.openclaw/workspace/.locks")
LOCK_DIR.mkdir(exist_ok=True)

JOBS = {
    "night_shift": {
        "script": "night_shift.py",
        "lock": "night_shift.lock",
        "max_duration": 3600,  # 1 hour
        "heavy": True,
        "log": "logs/night_shift.log"
    },
    "daily_report": {
        "script": "daily_report.py",
        "lock": "daily_report.lock",
        "max_duration": 600,  # 10 min
        "heavy": False,
        "log": "logs/daily_report.log"
    },
    "daily_outreach": {
        "script": "daily_outreach.py",
        "lock": "daily_outreach.lock",
        "max_duration": 1800,  # 30 min
        "heavy": True,
        "log": "logs/outreach.log"
    },
    "morning_routine": {
        "script": "morning_routine.py",
        "lock": "morning_routine.lock",
        "max_duration": 300,  # 5 min
        "heavy": False,
        "log": "logs/morning.log"
    },
    "autonomous_loop": {
        "script": "autonomous_loop.py",
        "lock": "autonomous_loop.lock",
        "max_duration": 300,  # 5 min
        "heavy": False,
        "log": "logs/autonomous_loop.log"
    },
    "evening_summary": {
        "script": "autonomous/evening_summary.py",
        "lock": "evening_summary.lock",
        "max_duration": 600,
        "heavy": False,
        "log": "logs/evening.log"
    }
}

def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")

def acquire_lock(lock_name: str, timeout: int = 0) -> tuple:
    """Acquire exclusive lock with optional timeout. Returns (success, lock_file)"""
    lock_path = LOCK_DIR / lock_name
    
    try:
        lock_file = open(lock_path, 'w')
        
        if timeout > 0:
            # Wait for lock with timeout
            start = time.time()
            while time.time() - start < timeout:
                try:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    lock_file.write(f"{os.getpid()}\n{datetime.now().isoformat()}")
                    lock_file.flush()
                    return True, lock_file
                except BlockingIOError:
                    time.sleep(1)
            return False, lock_file
        else:
            # Blocking acquire
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            lock_file.write(f"{os.getpid()}\n{datetime.now().isoformat()}")
            lock_file.flush()
            return True, lock_file
            
    except Exception as e:
        log(f"Lock error: {e}")
        return False, None

def release_lock(lock_file):
    """Release lock and close file"""
    if lock_file:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            lock_file.close()
        except:
            pass

def check_heavy_jobs_running() -> list:
    """Check which heavy jobs are currently running"""
    running = []
    for name, job in JOBS.items():
        lock_path = LOCK_DIR / job["lock"]
        if lock_path.exists():
            try:
                with open(lock_path, 'r') as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB)
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    # Lock is free
            except BlockingIOError:
                # Lock is held
                if job.get("heavy"):
                    running.append(name)
    return running

def run_job(job_name: str) -> bool:
    """Run a job with resource protection"""
    if job_name not in JOBS:
        log(f"Unknown job: {job_name}")
        return False
    
    job = JOBS[job_name]
    lock_name = job["lock"]
    script = job["script"]
    max_duration = job["max_duration"]
    
    log(f"Starting job: {job_name}")
    log(f"Script: {script}")
    
    # Check for running heavy jobs
    if job.get("heavy"):
        running = check_heavy_jobs_running()
        if running:
            log(f"Blocked: Heavy jobs running: {', '.join(running)}")
            return False
    
    # Acquire lock
    success, lock_file = acquire_lock(lock_name, timeout=60)
    if not success:
        log(f"Could not acquire lock: {job_name} is already running")
        return False
    
    try:
        start_time = time.time()
        
        # Run the script
        workspace = Path("/home/clawbot/.openclaw/workspace")
        script_path = workspace / script
        log_path = workspace / job["log"]
        
        # Redirect output to log file
        with open(log_path, 'a') as log_file:
            log_file.write(f"\n{'='*50}\n")
            log_file.write(f"[{datetime.now().isoformat()}] Starting: {job_name}\n")
            
            result = subprocess.run(
                ["python3", str(script_path)],
                cwd=str(workspace),
                stdout=log_file,
                stderr=subprocess.STDOUT,
                timeout=max_duration
            )
            
            log_file.write(f"[{datetime.now().isoformat()}] Finished: exit={result.returncode}\n")
        
        duration = time.time() - start_time
        log(f"Completed: {job_name} in {duration:.1f}s (exit={result.returncode})")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        log(f"Timeout: {job_name} exceeded {max_duration}s")
        return False
    except Exception as e:
        log(f"Error: {job_name} - {e}")
        return False
    finally:
        release_lock(lock_file)

def status():
    """Show status of all jobs"""
    print("\n" + "="*50)
    print("CRON SCHEDULER STATUS")
    print("="*50)
    
    for name, job in JOBS.items():
        lock_path = LOCK_DIR / job["lock"]
        heavy = "🔥" if job.get("heavy") else "⚡"
        
        if lock_path.exists():
            try:
                with open(lock_path, 'r') as f:
                    content = f.read().strip().split('\n')
                    pid = content[0] if content else "?"
                    start = content[1] if len(content) > 1 else "?"
                    # Try to acquire
                    fcntl.flock(f.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB)
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    status_icon = "✅"
                    status_text = "free"
            except BlockingIOError:
                status_icon = "🔒"
                # Check if process still alive
                try:
                    pid = int(open(lock_path).read().strip().split('\n')[0])
                    os.kill(pid, 0)  # Check if alive
                    status_text = f"running (PID {pid})"
                except:
                    status_text = "orphaned lock"
            except:
                status_icon = "❓"
                status_text = "unknown"
        else:
            status_icon = "✅"
            status_text = "never run"
        
        print(f"{status_icon} {heavy} {name:20} - {status_text}")
    
    print("="*50 + "\n")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Cron Scheduler with Resource Protection")
    parser.add_argument("--job", "-j", choices=list(JOBS.keys()), help="Job to run")
    parser.add_argument("--status", "-s", action="store_true", help="Show status")
    parser.add_argument("--list", "-l", action="store_true", help="List all jobs")
    
    args = parser.parse_args()
    
    if args.status or (not args.job and not args.list):
        status()
        return
    
    if args.list:
        print("\nAvailable Jobs:")
        for name, job in JOBS.items():
            heavy = "🔥 HEAVY" if job.get("heavy") else "⚡ light"
            print(f"  {name}: {job['script']} ({heavy})")
        print()
        return
    
    if args.job:
        success = run_job(args.job)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
