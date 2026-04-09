#!/usr/bin/env python3
"""
Audit Logging - Complete activity tracking
"""
import json
from datetime import datetime
from functools import wraps

AUDIT_LOG = "logs/audit.jsonl"

def audit(action, details):
    """Log an action"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details,
        "user": "system"
    }
    with open(AUDIT_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")

def track(func):
    """Decorator to track function calls"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        audit(func.__name__, {"args": str(args)[:100]})
        return result
    return wrapper
