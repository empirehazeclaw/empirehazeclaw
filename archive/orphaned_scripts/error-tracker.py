#!/usr/bin/env python3
"""
🔍 Error Tracker - EmpireHazeClaw
Lightweight error tracking without Sentry

Features:
- Capture and log errors
- Group similar errors
- Track error frequency
- Email alerts for new errors

Usage:
    from error_tracker import track_error, capture_exception
    
    try:
        risky_operation()
    except Exception as e:
        capture_exception(e, context={"user": "john"})
"""

import json
import traceback
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict

ERRORS_DIR = Path("/home/clawbot/.openclaw/workspace/data/errors")
ERRORS_DIR.mkdir(parents=True, exist_ok=True)

ERRORS_FILE = ERRORS_DIR / "errors.json"
ALERTS_FILE = ERRORS_DIR / "alerts.json"

# Error grouping window (group errors with same fingerprint in this time window)
GROUP_WINDOW = 3600  # 1 hour

def error_fingerprint(error_type, message, traceback_str):
    """Generate a fingerprint to group similar errors"""
    data = f"{error_type}:{message}:{len(traceback_str)}"
    return hashlib.md5(data.encode()).hexdigest()[:16]

def capture_exception(exc, context=None, severity="error"):
    """Capture an exception with context"""
    tb_str = traceback.format_exc()
    
    error_data = {
        "id": hashlib.md5(str(datetime.now()).encode()).hexdigest()[:12],
        "type": type(exc).__name__,
        "message": str(exc),
        "traceback": tb_str,
        "fingerprint": error_fingerprint(type(exc).__name__, str(exc), tb_str),
        "severity": severity,
        "context": context or {},
        "timestamp": datetime.now().isoformat(),
        "count": 1,
        "resolved": False
    }
    
    # Load existing errors
    errors = load_errors()
    
    # Check if similar error exists recently (grouping)
    grouped = False
    for err in errors:
        if err["fingerprint"] == error_data["fingerprint"]:
            # Check if within grouping window
            last_seen = datetime.fromisoformat(err["last_seen"])
            if (datetime.now() - last_seen).seconds < GROUP_WINDOW:
                err["count"] += 1
                err["last_seen"] = error_data["timestamp"]
                if context:
                    err["context"].update(context)
                grouped = True
                error_id = err["id"]
                break
    
    if not grouped:
        error_data["first_seen"] = error_data["timestamp"]
        error_data["last_seen"] = error_data["timestamp"]
        errors.append(error_data)
        error_id = error_data["id"]
    
    # Save errors
    save_errors(errors)
    
    # Check if we should alert
    check_alert(error_data)
    
    return error_id

def capture_message(message, context=None, severity="warning"):
    """Capture a log message as an error"""
    tb_str = traceback.format_stack()
    
    error_data = {
        "id": hashlib.md5(str(datetime.now()).encode()).hexdigest()[:12],
        "type": "Message",
        "message": message,
        "traceback": "".join(tb_str[-5:]),
        "fingerprint": hashlib.md5(message.encode()).hexdigest()[:16],
        "severity": severity,
        "context": context or {},
        "timestamp": datetime.now().isoformat(),
        "count": 1,
        "resolved": False
    }
    
    errors = load_errors()
    errors.append(error_data)
    save_errors(errors)
    
    return error_data["id"]

def load_errors():
    """Load errors from file"""
    if not ERRORS_FILE.exists():
        return []
    with open(ERRORS_FILE) as f:
        return json.load(f)

def save_errors(errors):
    """Save errors to file"""
    # Keep only last 1000 errors
    errors = errors[-1000:]
    with open(ERRORS_FILE, 'w') as f:
        json.dump(errors, f, indent=2)

def check_alert(error_data):
    """Check if we should send an alert for this error"""
    # Don't alert for warnings
    if error_data["severity"] in ("info", "warning"):
        return
    
    # Alert if same error occurred 3+ times
    errors = load_errors()
    count = sum(1 for e in errors if e["fingerprint"] == error_data["fingerprint"] and not e.get("resolved"))
    
    if count >= 3:
        send_alert(error_data, count)

def send_alert(error_data, count):
    """Send an alert (placeholder - would integrate with email/telegram)"""
    print(f"🚨 ALERT: {error_data['type']} x{count}")
    print(f"   {error_data['message'][:100]}")
    
    # Load alerts
    alerts = []
    if ALERTS_FILE.exists():
        with open(ALERTS_FILE) as f:
            alerts = json.load(f)
    
    # Add alert
    alert = {
        "error_id": error_data["id"],
        "type": error_data["type"],
        "message": error_data["message"],
        "count": count,
        "timestamp": datetime.now().isoformat(),
        "sent": False
    }
    
    alerts.append(alert)
    
    # Keep only recent alerts
    alerts = alerts[-50:]
    
    with open(ALERTS_FILE, 'w') as f:
        json.dump(alerts, f, indent=2)

def track_error(error_type, message, context=None, severity="error"):
    """Track a manually created error"""
    error_data = {
        "id": hashlib.md5(str(datetime.now()).encode()).hexdigest()[:12],
        "type": error_type,
        "message": message,
        "traceback": "",
        "fingerprint": hashlib.md5(f"{error_type}:{message}".encode()).hexdigest()[:16],
        "severity": severity,
        "context": context or {},
        "timestamp": datetime.now().isoformat(),
        "count": 1,
        "resolved": False
    }
    
    errors = load_errors()
    errors.append(error_data)
    save_errors(errors)
    
    return error_data["id"]

def list_errors(limit=20, unresolved_only=False, severity=None):
    """List recent errors"""
    errors = load_errors()
    
    # Filter
    if unresolved_only:
        errors = [e for e in errors if not e.get("resolved")]
    if severity:
        errors = [e for e in errors if e.get("severity") == severity]
    
    # Sort by timestamp
    errors.sort(key=lambda x: x["timestamp"], reverse=True)
    errors = errors[:limit]
    
    print(f"\n{'='*70}")
    print(f"🔍 ERROR TRACKER - {len(errors)} errors shown")
    print(f"{'='*70}\n")
    
    severity_icons = {
        "error": "🔴",
        "warning": "🟡",
        "info": "🔵"
    }
    
    for err in errors:
        icon = severity_icons.get(err.get("severity"), "❓")
        resolved = "✅" if err.get("resolved") else "❌"
        
        print(f"{icon} {err['type']} {resolved} (x{err.get('count', 1)})")
        print(f"   {err['message'][:60]}...")
        print(f"   📅 {err['timestamp'][:19]}")
        if err.get("context"):
            print(f"   📎 {list(err['context'].keys())}")
        print()
    
    return errors

def resolve_error(error_id):
    """Mark an error as resolved"""
    errors = load_errors()
    for err in errors:
        if err["id"] == error_id:
            err["resolved"] = True
            err["resolved_at"] = datetime.now().isoformat()
            save_errors(errors)
            print(f"✅ Resolved: {error_id}")
            return
    print(f"❌ Not found: {error_id}")

def stats():
    """Show error statistics"""
    errors = load_errors()
    
    total = len(errors)
    unresolved = sum(1 for e in errors if not e.get("resolved"))
    resolved = total - unresolved
    
    by_severity = defaultdict(int)
    by_type = defaultdict(int)
    
    for err in errors:
        by_severity[err.get("severity", "unknown")] += 1
        by_type[err.get("type", "Unknown")] += 1
    
    print(f"\n📊 ERROR STATS")
    print(f"{'='*40}")
    print(f"Total errors: {total}")
    print(f"Resolved: {resolved}")
    print(f"Unresolved: {unresolved}")
    print(f"\nBy Severity:")
    for sev, count in sorted(by_severity.items(), key=lambda x: -x[1]):
        print(f"  {sev}: {count}")
    print(f"\nBy Type:")
    for typ, count in sorted(by_type.items(), key=lambda x: -x[1])[:5]:
        print(f"  {typ}: {count}")

# ═══════════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nCommands:")
        print("  list          - List recent errors")
        print("  stats         - Show error statistics")
        print("  resolve <id>  - Mark error as resolved")
        print("  test          - Create a test error")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "list":
        unresolved = "--unresolved" in sys.argv
        list_errors(unresolved_only=unresolved)
    
    elif cmd == "stats":
        stats()
    
    elif cmd == "resolve" and len(sys.argv) >= 3:
        resolve_error(sys.argv[2])
    
    elif cmd == "test":
        # Create a test error
        try:
            1/0
        except ZeroDivisionError as e:
            capture_exception(e, context={"user": "test_user", "action": "division"})
    
    else:
        print(f"Unknown command: {cmd}")
