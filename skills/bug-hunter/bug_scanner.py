#!/usr/bin/env python3
"""
Bug Hunter — Refined Bug Scanner
=================================
Scans ONLY real exceptions and stack traces — no INFO false positives.
Runs as cron every 30 minutes, feeds Learning Loop on new bugs.

Usage:
    python3 bug_scanner.py --scan
    python3 bug_scanner.py --status

False Positive Filters:
    ❌ "Error: Starting..." (INFO messages)
    ❌ "Error: All models failed" (log lines)
    ❌ "❌" status reports
    ❌ "Error:" in non-exception contexts

Real Bugs We Catch:
    ✓ Python Traceback (exception + stack)
    ✓ Unhandled Exception keywords
    ✓ Connection refused/timeout (real errors)
    ✓ Permission denied / OOM / Killed
"""

import os
import re
import json
import hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

# Paths
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
LOG_DIR = WORKSPACE / "logs"
BUG_KNOWLEDGE = WORKSPACE / "ceo" / "memory" / "notes" / "bug_knowledge.json"
BUG_REPORTS_DIR = LOG_DIR / "bug_hunter"
ALERT_LOG = BUG_REPORTS_DIR / "alerts.json"

# Time window for scanning (last 30 minutes by default)
SCAN_WINDOW_MINUTES = 30

# FALSE POSITIVES — patterns we actively IGNORE
# These look like errors but aren't
FALSE_POSITIVES = [
    r'^.*\[INFO\].*error.*$',           # INFO level logs mentioning "error"
    r'^.*Error: Starting',              # "Error: Starting..." 
    r'^.*Error: All models failed',     # Log lines, not exceptions
    r'^.*Error: All providers failed',  # Same
    r'^.*❌.*status.*report',           # Watchdog status emojis
    r'^.*\[\d{4}-\d{2}-\d{2}.*\] Error:',  # Bracketed timestamps with Error:
    r'.*status report.*❌',             # Cron watchdog reports
    r'.*watchdog.*❌',                  # Watchdog logs
]

# Combined false positive regex
FALSE_POSITIVE_RE = re.compile('|'.join(f'({p})' for p in FALSE_POSITIVES), re.IGNORECASE)

# REAL ERROR patterns — things that indicate actual bugs
REAL_ERROR_PATTERNS = [
    # Stack traces and exceptions
    (r'Traceback \(most recent call last\)', 'Python Traceback'),
    (r'Exception:\s*', 'Python Exception'),
    (r'raise \w+Error', 'Raised Error'),
    (r'\w+Error:\s*', 'Error Type'),
    
    # System errors
    (r'ECONNREFUSED', 'Connection Refused'),
    (r'ETIMEDOUT', 'Connection Timeout'),
    (r'ENOTFOUND', 'DNS Lookup Failed'),
    (r'EACCES', 'Permission Denied'),
    (r'ENOENT', 'File Not Found'),
    (r'out of memory', 'OOM'),
    (r'OOMKiller', 'OOM Killed'),
    (r'Killed\s+process', 'Process Killed'),
    
    # Node/JS errors
    (r'TypeError:', 'JavaScript TypeError'),
    (r'ReferenceError:', 'JavaScript ReferenceError'),
    (r'SyntaxError:', 'JavaScript SyntaxError'),
    (r'UnhandledPromiseRejection', 'Unhandled Promise Rejection'),
    
    # Process failures
    (r'child_process.*failed', 'Child Process Failed'),
    (r'exec.*failed', 'Execution Failed'),
    
    # OpenClaw specific
    (r'gateway.*error', 'Gateway Error'),
    (r'session.*error', 'Session Error'),
    (r'tool.*failed', 'Tool Failed'),
]

# Build real error matcher
REAL_ERROR_RE = re.compile('|'.join(f'({p})' for p, _ in REAL_ERROR_PATTERNS), re.IGNORECASE)


def load_bug_knowledge() -> Dict:
    """Load known bugs from knowledge base."""
    if BUG_KNOWLEDGE.exists():
        try:
            with open(BUG_KNOWLEDGE) as f:
                return json.load(f)
        except:
            pass
    return {"known_bugs": [], "last_updated": None}


def save_bug_knowledge(knowledge: Dict):
    """Save known bugs to knowledge base."""
    BUG_KNOWLEDGE.parent.mkdir(parents=True, exist_ok=True)
    knowledge["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(BUG_KNOWLEDGE, "w") as f:
        json.dump(knowledge, f, indent=2)


def get_error_hash(error_line: str) -> str:
    """Generate stable hash for error similarity matching."""
    # Normalize: lowercase, remove numbers, shorten
    normalized = re.sub(r'[0-9]', '', error_line.lower())[:100]
    return hashlib.md5(normalized.encode()).hexdigest()[:12]


def is_false_positive(line: str) -> bool:
    """Check if this line looks like an error but isn't."""
    return bool(FALSE_POSITIVE_RE.match(line))


def is_real_error(line: str) -> Optional[str]:
    """Check if this line is a real error. Returns error type if yes, None if no."""
    if is_false_positive(line):
        return None
    match = REAL_ERROR_RE.search(line)
    if match:
        # Find which pattern matched
        for pattern, error_type in REAL_ERROR_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                return error_type
        return "Unknown Real Error"
    return None


def scan_log_file(filepath: Path, window_minutes: int = SCAN_WINDOW_MINUTES) -> List[Dict]:
    """Scan a single log file for REAL errors only."""
    errors = []
    
    if not filepath.exists():
        return errors
    
    try:
        # Read last 500 lines (or less if file is smaller)
        with open(filepath, 'r', errors='ignore') as f:
            lines = f.readlines()[-500:]
        
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
        
        for line in lines:
            # Try to extract timestamp
            ts_match = re.match(r'\[?(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})', line)
            if ts_match:
                try:
                    ts = datetime.fromisoformat(ts_match.group(1).replace(' ', 'T'))
                    if ts < cutoff:
                        continue  # Too old
                except:
                    pass
            
            # Check for REAL error (not false positive)
            error_type = is_real_error(line)
            if error_type:
                errors.append({
                    "line": line.strip(),
                    "file": str(filepath),
                    "timestamp": ts_match.group(1) if ts_match else None,
                    "hash": get_error_hash(line),
                    "error_type": error_type
                })
    
    except Exception as e:
        pass
    
    return errors


def scan_all_logs(window_minutes: int = SCAN_WINDOW_MINUTES) -> List[Dict]:
    """Scan all relevant log files."""
    all_errors = []
    
    # Scan workspace logs
    if LOG_DIR.exists():
        for log_file in LOG_DIR.glob("*.log"):
            if log_file.name in ['guardrail_interceptions.log']:
                continue  # Skip our own logs
            all_errors.extend(scan_log_file(log_file, window_minutes))
    
    return all_errors


def is_known_error(error_hash: str, knowledge: Dict) -> bool:
    """Check if error is in known bug database."""
    return any(b.get("hash") == error_hash for b in knowledge.get("known_bugs", []))


def classify_error(error_line: str) -> Tuple[str, str, str]:
    """
    Classify error into category, cause, and suggested fix.
    Returns: (category, cause, suggestion)
    """
    for pattern, error_type in REAL_ERROR_PATTERNS:
        if re.search(pattern, error_line, re.IGNORECASE):
            cause = error_type
            suggestion = f"Pattern matched: {pattern}"
            return ("REAL_ERROR", cause, suggestion)
    
    # Unknown — needs investigation
    return ("UNKNOWN", "Unclassified error", "Investigate manually")


def report_new_bug(error: Dict, knowledge: Dict) -> str:
    """Add new bug to knowledge base and return report."""
    bug_entry = {
        "hash": error["hash"],
        "first_seen": datetime.now(timezone.utc).isoformat(),
        "line": error["line"][:200],  # Truncate
        "file": error["file"],
        "count": 1,
        "category": classify_error(error["line"])[0],
        "status": "NEW"
    }
    
    knowledge["known_bugs"].append(bug_entry)
    
    return f"""🚨 NEW BUG DETECTED

File: {error['file']}
Time: {error.get('timestamp', 'unknown')}
Error: {error['line'][:150]}...

Category: {classify_error(error['line'])[0]}
Cause: {classify_error(error['line'])[1]}

Added to bug knowledge base.
"""


def run_bug_hunt() -> Dict:
    """Run full bug hunt cycle."""
    print(f"Bug Hunter — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    # Load knowledge
    knowledge = load_bug_knowledge()
    print(f"Known bugs in database: {len(knowledge.get('known_bugs', []))}")
    
    # Scan logs
    print("Scanning logs...")
    errors = scan_all_logs(SCAN_WINDOW_MINUTES)
    print(f"Errors found: {len(errors)}")
    
    if not errors:
        print("✅ No errors found")
        return {"status": "clean", "errors": [], "new_bugs": []}
    
    # Deduplicate by hash
    unique_hashes: Set[str] = set()
    unique_errors = []
    for err in errors:
        if err["hash"] not in unique_hashes:
            unique_hashes.add(err["hash"])
            unique_errors.append(err)
    
    print(f"Unique errors: {len(unique_errors)}")
    
    # Check for new bugs
    new_bugs = []
    known_bugs = []
    
    for err in unique_errors:
        if is_known_error(err["hash"], knowledge):
            known_bugs.append(err)
        else:
            new_bugs.append(err)
    
    # Report new bugs
    reports = []
    if new_bugs:
        print(f"\n🚨 {len(new_bugs)} NEW BUGS DETECTED!")
        for err in new_bugs:
            report = report_new_bug(err, knowledge)
            reports.append(report)
            print(report[:200])
    else:
        print("\n✅ All errors are known issues")
    
    # Save updated knowledge
    save_bug_knowledge(knowledge)
    
    # Log alert
    BUG_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    alert = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "errors_found": len(errors),
        "unique_errors": len(unique_errors),
        "new_bugs": len(new_bugs),
        "known_bugs": len(known_bugs),
        "reports": reports
    }
    with open(ALERT_LOG, "w") as f:
        json.dump(alert, f, indent=2)
    
    return {
        "status": "bugs_found" if new_bugs else "clean",
        "errors": unique_errors,
        "new_bugs": new_bugs,
        "known_bugs": known_bugs,
        "reports": reports
    }


def show_status():
    """Show current bug knowledge status."""
    knowledge = load_bug_knowledge()
    bugs = knowledge.get("known_bugs", [])
    
    print("Bug Knowledge Base Status")
    print("=" * 60)
    print(f"Total known bugs: {len(bugs)}")
    print(f"Last updated: {knowledge.get('last_updated', 'never')}")
    
    if bugs:
        # Group by status
        by_status = {}
        for b in bugs:
            status = b.get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1
        
        print("\nBy status:")
        for status, count in by_status.items():
            print(f"  {status}: {count}")
        
        # Show recent new bugs
        new = [b for b in bugs if b.get("status") == "NEW"][:5]
        if new:
            print("\nRecent NEW bugs:")
            for b in new:
                print(f"  - {b.get('first_seen', '?')}: {b.get('line', '')[:80]}...")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Bug Hunter — Autonomous Bug Scanner")
    parser.add_argument("--scan", action="store_true", help="Run bug scan")
    parser.add_argument("--status", action="store_true", help="Show knowledge base status")
    parser.add_argument("--window", type=int, default=SCAN_WINDOW_MINUTES, 
                        help=f"Scan window in minutes (default: {SCAN_WINDOW_MINUTES})")
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
    elif args.scan:
        result = run_bug_hunt()
        print(f"\nResult: {result['status']}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
