#!/usr/bin/env python3
"""
Night Shift Automation
Runs every night to improve the business
"""
import os
import subprocess
import fcntl
import sys
from datetime import datetime
from pathlib import Path

LOG_FILE = "/home/clawbot/.openclaw/logs/night_shift.log"
LOCK_FILE = "/home/clawbot/.openclaw/workspace/data/.night_shift.lock"

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    line = f"[{timestamp}] [{level}] {msg}"
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass  # Don't fail on log errors
    print(line)

def run(cmd, critical=False):
    """Run command with error handling"""
    log(f"Running: {cmd}")
    try:
        result = os.system(cmd)
        if result != 0:
            log(f"Command failed with exit code {result}", "WARN")
            if critical:
                raise Exception(f"Critical command failed: {cmd}")
        return result
    except Exception as e:
        log(f"Exception running command: {e}", "ERROR")
        if critical:
            raise
        return -1

def acquire_lock():
    """Acquire exclusive file lock to prevent race conditions"""
    lock_path = Path(LOCK_FILE)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_fd = open(lock_path, 'w')
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock_fd.write(str(os.getpid()))
        return lock_fd
    except BlockingIOError:
        log("Another instance is running. Exiting.")
        sys.exit(0)

def release_lock(lock_fd):
    """Release the file lock"""
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()
    except Exception:
        pass

def main():
    lock_fd = None
    try:
        lock_fd = acquire_lock()
        log("=" * 50)
        log("NIGHT SHIFT STARTED")
        
        # 1. System health check
        log("1. Checking system health...")
        try:
            result = subprocess.run(
                ["curl", "-sI", "https://empirehazeclaw.com"],
                capture_output=True, text=True, timeout=30
            )
            status = "UP" if result.returncode == 0 else "DOWN"
            log(f"System health: {status}")
        except Exception as e:
            log(f"Health check failed: {e}", "WARN")
        
        # 2. Regenerate blog posts
        log("2. Regenerating blog posts...")
        blog_dir = Path("/home/clawbot/.openclaw/workspace/projects/blog-generator")
        if blog_dir.exists():
            try:
                result = subprocess.run(
                    ["python3", "generate.py"],
                    capture_output=True, text=True, timeout=120,
                    cwd=str(blog_dir)
                )
                if result.returncode == 0:
                    log("Blog posts generated successfully")
                else:
                    log(f"Blog generation failed: {result.stderr[:100]}", "WARN")
            except subprocess.TimeoutExpired:
                log("Blog generation timed out", "WARN")
            except Exception as e:
                log(f"Blog generation error: {e}", "WARN")
        else:
            log("Blog generator directory not found, skipping", "WARN")
        
        # 3. Commit changes to git
        log("3. Backing up to git...")
        ws = Path("/home/clawbot/.openclaw/workspace")
        try:
            subprocess.run(["git", "add", "-A"], cwd=ws, capture_output=True, timeout=30)
            subprocess.run(
                ["git", "commit", "-m", f"Night shift {datetime.now().strftime('%Y-%m-%d')}"],
                cwd=ws, capture_output=True, timeout=30
            )
            subprocess.run(["git", "push", "origin", "main"], cwd=ws, capture_output=True, timeout=60)
            log("Git backup completed")
        except subprocess.TimeoutExpired:
            log("Git operation timed out", "WARN")
        except Exception as e:
            log(f"Git backup failed: {e}", "WARN")
        
        log("NIGHT SHIFT COMPLETED")
        log("=" * 50)
        
    except Exception as e:
        log(f"CRITICAL ERROR in night_shift: {e}", "ERROR")
        sys.exit(1)
    finally:
        if lock_fd:
            release_lock(lock_fd)

if __name__ == "__main__":
    main()
