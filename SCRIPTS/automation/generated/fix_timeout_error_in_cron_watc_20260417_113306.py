#!/usr/bin/env python3
"""
Cron Watchdog Script - Handles timeout errors for slow cron jobs.
"""

import subprocess
import argparse
import logging
import sys
import os
from datetime import datetime
from pathlib import Path

# Configuration
SCRIPT_DIR = Path("/workspace/SCRIPTS/automation")
LOG_DIR = Path("/workspace/SCRIPTS/logs")

# Default timeout in seconds
DEFAULT_TIMEOUT = 300

def setup_logging(log_file=None):
    """Setup logging configuration."""
    if log_file is None:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        log_file = LOG_DIR / f"cron_watchdog_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def check_cron_status(timeout=DEFAULT_TIMEOUT):
    """Check cron service status with timeout handling."""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Checking cron service status...")
        result = subprocess.run(
            ["systemctl", "is-active", "cron"],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            logger.info("Cron service is active")
            return True
        else:
            logger.warning(f"Cron service status: {result.stdout.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout expired while checking cron status (timeout={timeout}s)")
        return False
    except subprocess.SubprocessError as e:
        logger.error(f"Subprocess error checking cron status: {e}")
        return False
    except FileNotFoundError:
        logger.warning("systemctl not found, checking alternative method...")
        return check_cron_alternative(timeout)

def check_cron_alternative(timeout=DEFAULT_TIMEOUT):
    """Alternative method to check cron using ps command."""
    logger = logging.getLogger(__name__)
    
    try:
        result = subprocess.run(
            ["ps", "-C", "cron", "-o", "pid="],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.stdout.strip():
            logger.info("Cron process found running")
            return True
        else:
            logger.warning("No cron process found running")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout expired checking cron process (timeout={timeout}s)")
        return False
    except Exception as e:
        logger.error(f"Error in alternative cron check: {e}")
        return False

def get_running_crons(timeout=DEFAULT_TIMEOUT):
    """Get list of running cron jobs."""
    logger = logging.getLogger(__name__)
    running_crons = []
    
    try:
        logger.info("Checking for running cron jobs...")
        result = subprocess.run(
            ["ps", "-eo", "pid,etime,cmd", "--no-headers"],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if "cron" in line.lower() or "/cron" in line:
                    running_crons.append(line.strip())
                    logger.info(f"Found cron job: {line.strip()}")
        
    except subprocess.TimeoutExpired:
        logger.error("Timeout while getting running crons")
    except Exception as e:
        logger.error(f"Error getting running crons: {e}")
    
    return running_crons

def check_cron_jobs(timeout=DEFAULT_TIMEOUT):
    """Check cron table entries with timeout handling."""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Checking cron jobs configuration...")
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            jobs = result.stdout.strip().split('\n')
            logger.info(f"Found {len(jobs)} cron job entries")
            return jobs
        else:
            logger.warning(f"No crontab entries or error: {result.stderr.strip()}")
            return []
            
    except subprocess.TimeoutExpired:
        logger.error("Timeout while reading crontab")
        return []
    except FileNotFoundError:
        logger.error("crontab command not found")
        return []
    except Exception as e:
        logger.error(f"Error reading crontab: {e}")
        return []

def restart_cron_service(timeout=30):
    """Attempt to restart cron service."""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Attempting to restart cron service...")
        result = subprocess.run(
            ["systemctl", "restart", "cron"],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            logger.info("Cron service restarted successfully")
            return True
        else:
            logger.error(f"Failed to restart cron: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("Timeout while restarting cron")
        return False
    except Exception as e:
        logger.error(f"Error restarting cron: {e}")
        return False

def main():
    """Main function with CLI argument handling."""
    parser = argparse.ArgumentParser(
        description="Cron Watchdog - Monitor and manage cron jobs with timeout handling"
    )
    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Timeout in seconds for commands (default: {DEFAULT_TIMEOUT})"
    )
    parser.add_argument(
        "-l", "--log-file",
        type=str,
        default=None,
        help="Path to log file"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check status, don't take action"
    )
    parser.add_argument(
        "--restart",
        action="store_true",
        help="Attempt to restart cron if not responding"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.log_file)
    
    logger.info("=" * 50)
    logger.info("Cron Watchdog started")
    logger.info(f"Timeout setting: {args.timeout}s")
    logger.info("=" * 50)
    
    try:
        # Check cron service status
        cron_active = check_cron_status(args.timeout)
        
        if cron_active:
            logger.info("Cron service is running normally")
        else:
            logger.warning("Cron service issues detected")
            if args.restart and not args.check_only:
                restart_cron_service()
        
        # Check cron jobs
        jobs = check_cron_jobs(args.timeout)
        if jobs:
            logger.info(f"Active cron jobs: {len(jobs)}")
        
        # Check running processes
        running = get_running_crons(args.timeout)
        if running:
            logger.info(f"Running cron processes: {len(running)}")
        
        logger.info("Cron watchdog check completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())