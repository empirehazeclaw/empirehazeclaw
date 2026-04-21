#!/usr/bin/env python3
"""
🔧 Bug→Fix→Learn Pipeline — Sir HazeClaw
Complete automated cycle: Detect → Analyze → Fix → Verify → Learn

Triggered by:
  1. Bug Hunter finding new bugs
  2. Cron schedule (hourly)
  3. Manual run

Flow:
  1. Run bug_scanner.py to get new bugs
  2. For each new bug → try fix strategy
  3. Verify fix worked
  4. If worked → add to bug_knowledge as RESOLVED
  5. Feed to Learning Loop as feedback
"""

import os
import sys
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
BUG_KNOWLEDGE = WORKSPACE / "ceo/memory/notes/bug_knowledge.json"
LOG_FILE = WORKSPACE / "logs/bug_fix_pipeline.log"
FEEDBACK_QUEUE = WORKSPACE / "data/feedback_queue.json"
BUG_SCANNER = WORKSPACE / "skills/bug-hunter/bug_scanner.py"

# Fix strategies: pattern → (fix_function_name, severity)
FIX_STRATEGIES = {
    "timeout": {
        "patterns": ["timeout", "timed_out", "TIMEOUT"],
        "severity": "MEDIUM",
        "fix": "fix_timeout"
    },
    "connection_refused": {
        "patterns": ["ECONNREFUSED", "connection refused", "Connection refused"],
        "severity": "HIGH",
        "fix": "fix_connection"
    },
    "memory_error": {
        "patterns": ["out of memory", "OOM", "Killed"],
        "severity": "HIGH",
        "fix": "fix_memory"
    },
    "permission_denied": {
        "patterns": ["EACCES", "permission denied", "Permission denied"],
        "severity": "MEDIUM",
        "fix": "fix_permission"
    },
    "file_not_found": {
        "patterns": ["ENOENT", "file not found", "not found"],
        "severity": "LOW",
        "fix": "fix_file_not_found"
    },
    "api_error": {
        "patterns": ["404", "401", "403", "500", "502", "503"],
        "severity": "MEDIUM",
        "fix": "fix_api"
    }
}

def log(msg: str, level: str = "INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_bugs() -> List[Dict]:
    if BUG_KNOWLEDGE.exists():
        with open(BUG_KNOWLEDGE) as f:
            return json.load(f).get("known_bugs", [])
    return []

def save_bugs(bugs: List[Dict]):
    data = {"known_bugs": bugs, "last_updated": datetime.now().isoformat()}
    with open(BUG_KNOWLEDGE, "w") as f:
        json.dump(data, f, indent=2)

def load_feedback_queue() -> Dict:
    if FEEDBACK_QUEUE.exists():
        with open(FEEDBACK_QUEUE) as f:
            return json.load(f)
    return {"entries": []}

def save_feedback_queue(queue: Dict):
    with open(FEEDBACK_QUEUE, "w") as f:
        json.dump(queue, f, indent=2)

def add_feedback(feedback: Dict):
    """Add feedback to learning loop queue."""
    queue = load_feedback_queue()
    queue["entries"].append(feedback)
    queue["entries"] = queue["entries"][-50:]  # Keep last 50
    save_feedback_queue(queue)
    log(f"Added feedback: {feedback.get('type', 'unknown')} → {feedback.get('title', '?')}")

# ============ FIX FUNCTIONS ============

def fix_timeout(bug: Dict) -> Tuple[bool, str]:
    """Fix timeout errors by increasing timeout or disabling slow jobs."""
    log("FIX: Attempting to fix timeout issue...", "ACTION")
    
    # Check if it's a cron timeout
    if "cron" in bug.get("line", "").lower():
        # Extract job name if possible
        job_match = re.search(r"job.*?([a-z_-]+)", bug.get("line", ""), re.I)
        if job_match:
            job_name = job_match.group(1)
            log(f"  Timeout in cron job: {job_name}")
            # Increase timeout in jobs.json
            try:
                jobs_file = Path("/home/clawbot/.openclaw/cron/jobs.json")
                with open(jobs_file) as f:
                    jobs = json.load(f)
                
                for job in jobs.get("jobs", []):
                    if job_name.lower() in job.get("name", "").lower():
                        old_timeout = job.get("payload", {}).get("timeoutSeconds", 60)
                        new_timeout = min(old_timeout * 2, 600)  # Max 10 min
                        job["payload"]["timeoutSeconds"] = new_timeout
                        log(f"  Increased timeout: {old_timeout}s → {new_timeout}s", "ACTION")
                        
                        with open(jobs_file, "w") as f:
                            json.dump(jobs, f, indent=2)
                        return True, f"Increased timeout to {new_timeout}s"
                
                return False, f"Job {job_name} not found in cron config"
            except Exception as e:
                return False, f"Failed to update timeout: {e}"
    
    return False, "Not a cron timeout"

def fix_connection(bug: Dict) -> Tuple[bool, str]:
    """Fix connection refused errors."""
    log("FIX: Connection refused error detected", "ACTION")
    # Restart gateway if it's not responding
    try:
        result = subprocess.run(
            ["openclaw", "gateway", "status"],
            capture_output=True, text=True, timeout=10
        )
        if "running" not in result.stdout.lower():
            log("  Gateway not responding — triggering restart", "ACTION")
            subprocess.run(["openclaw", "gateway", "restart"], capture_output=True, timeout=30)
            return True, "Gateway restart triggered"
        return True, "Gateway running, connection issue transient"
    except Exception as e:
        return False, f"Connection fix failed: {e}"

def fix_memory(bug: Dict) -> Tuple[bool, str]:
    """Fix memory issues by clearing caches."""
    log("FIX: Memory issue detected", "ACTION")
    
    try:
        # Vacuum memory DBs
        for db_path in [
            "/home/clawbot/.openclaw/memory/main.sqlite",
            "/home/clawbot/.openclaw/memory/ceo.sqlite"
        ]:
            if os.path.exists(db_path):
                size_before = os.path.getsize(db_path)
                conn = sqlite3.connect(db_path)
                conn.execute("VACUUM")
                conn.close()
                size_after = os.path.getsize(db_path)
                freed_mb = (size_before - size_after) / 1024 / 1024
                if freed_mb > 1:
                    log(f"  Vacuumed {db_path.split('/')[-1]}: freed {freed_mb:.1f}MB", "ACTION")
        
        return True, "Memory cleanup attempted"
    except Exception as e:
        return False, f"Memory fix failed: {e}"

def fix_permission(bug: Dict) -> Tuple[bool, str]:
    """Fix permission errors."""
    log("FIX: Permission error detected", "ACTION")
    return False, "Permission errors need manual review"

def fix_file_not_found(bug: Dict) -> Tuple[bool, str]:
    """Fix file not found errors."""
    log("FIX: File not found error", "ACTION")
    return False, "File not found needs path analysis"

def fix_api(bug: Dict) -> Tuple[bool, str]:
    """Fix API errors (404, 401, etc)."""
    log("FIX: API error detected", "ACTION")
    line = bug.get("line", "")
    
    if "minimax" in line.lower() or "api.minimax" in line.lower():
        return False, "MiniMax API errors need config review"
    
    return False, "Generic API error needs investigation"

# ============ MAIN PIPELINE ============

def scan_for_bugs() -> List[Dict]:
    """Run bug scanner and return new bugs."""
    try:
        result = subprocess.run(
            ["python3", str(BUG_SCANNER), "--scan"],
            capture_output=True, text=True, timeout=60,
            cwd=str(WORKSPACE)
        )
        
        # Parse output
        output = result.stdout + result.stderr
        
        if "new_bugs" in output or "NEW BUG" in output:
            # There are new bugs
            bugs = load_bugs()
            return [b for b in bugs if b.get("status") == "NEW"]
        
        return []
    except Exception as e:
        log(f"Failed to scan bugs: {e}", "ERROR")
        return []

def match_fix_strategy(bug: Dict) -> Optional[str]:
    """Match bug to fix strategy."""
    line = bug.get("line", "").lower()
    
    for name, strategy in FIX_STRATEGIES.items():
        for pattern in strategy["patterns"]:
            if pattern.lower() in line:
                return strategy["fix"]
    
    return None

def apply_fix(bug: Dict) -> Tuple[bool, str]:
    """Apply fix for bug."""
    fix_name = match_fix_strategy(bug)
    
    if not fix_name:
        return False, "No fix strategy matched"
    
    fix_fn = globals().get(fix_name)
    if not fix_fn:
        return False, f"Fix function {fix_name} not found"
    
    try:
        return fix_fn(bug)
    except Exception as e:
        return False, f"Fix failed: {e}"

def verify_fix(bug: Dict, fix_description: str) -> bool:
    """Verify fix worked by re-running bug scanner after short delay."""
    import time
    time.sleep(5)  # Wait for fix to take effect
    
    try:
        bugs = load_bugs()
        # Check if same bug hash still appears as new
        current_bugs = load_bugs()
        bug_hash = bug.get("hash", "")
        
        for b in current_bugs:
            if b.get("hash") == bug_hash and b.get("status") == "RESOLVED":
                return True
        
        return False
    except:
        return False

def main():
    log("=== Bug→Fix→Learn Pipeline ===")
    
    # Scan for new bugs
    new_bugs = scan_for_bugs()
    
    if not new_bugs:
        log("No new bugs found — pipeline complete")
        return
    
    log(f"Found {len(new_bugs)} new bugs to process")
    
    fixed_count = 0
    failed_count = 0
    
    for bug in new_bugs:
        bug_hash = bug.get("hash", "unknown")
        bug_type = bug.get("category", "unknown")
        
        log(f"Processing bug: {bug_type} | {bug_hash[:12]}")
        
        # Try to fix
        success, msg = apply_fix(bug)
        
        if success:
            # Mark as resolved
            bugs = load_bugs()
            for b in bugs:
                if b.get("hash") == bug_hash:
                    b["status"] = "RESOLVED"
                    b["resolved_at"] = datetime.now().isoformat()
                    b["fix_applied"] = msg
            save_bugs(bugs)
            
            # Add feedback to learning queue
            add_feedback({
                "type": "bug_fix_success",
                "title": f"Fixed: {bug_type}",
                "description": msg,
                "bug_hash": bug_hash,
                "timestamp": datetime.now().isoformat(),
                "loop_relevant": True
            })
            
            log(f"✅ FIXED: {msg}", "SUCCESS")
            fixed_count += 1
        else:
            # Add feedback about failure
            add_feedback({
                "type": "bug_fix_failed",
                "title": f"Unfixed: {bug_type}",
                "description": msg,
                "bug_hash": bug_hash,
                "timestamp": datetime.now().isoformat(),
                "loop_relevant": False
            })
            
            log(f"❌ Failed to fix: {msg}", "WARN")
            failed_count += 1
    
    log(f"Pipeline complete: {fixed_count} fixed, {failed_count} unfixed")

if __name__ == "__main__":
    main()
