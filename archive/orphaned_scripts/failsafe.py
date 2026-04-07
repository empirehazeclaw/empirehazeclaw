#!/usr/bin/env python3
"""
Failsafe System - Prevent system crashes
"""
import sys
import traceback
from datetime import datetime

def safe_execute(func):
    """Wrapper mit Failsafe"""
    try:
        return func()
    except Exception as e:
        error_log = {
            "time": datetime.now().isoformat(),
            "error": str(e),
            "trace": traceback.format_exc()
        }
        print(f"⚠️ Failsafe caught: {e}")
        return {"error": str(e), "handled": True}

# Auto-save on crash
def crash_protect(func):
    """Save state before crash"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            # Save state
            with open("data/crash_recovery.json", "w") as f:
                f.write(json.dumps({"last_task": str(func)}))
            raise
    return wrapper
