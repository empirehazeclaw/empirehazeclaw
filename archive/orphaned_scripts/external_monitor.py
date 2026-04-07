#!/usr/bin/env python3
"""
External Monitor - Night Mode Friendly
"""

import os
import sys
import subprocess

def check_external():
    """Check external services"""
    
    # Check various services
    results = []
    
    # Check internet
    try:
        import requests
        r = requests.get("https://www.google.com", timeout=5)
        if r.status_code == 200:
            results.append(("internet", True, "OK"))
        else:
            results.append(("internet", False, f"Status {r.status_code}"))
    except Exception as e:
        results.append(("internet", False, str(e)[:50]))
    
    return results

def is_quiet_hours():
    """Check if quiet hours (night time)"""
    
    from datetime import datetime
    
    hour = datetime.now().hour
    
    # Quiet: 23:00 - 08:00 UTC
    return hour >= 23 or hour < 8

def main():
    results = check_external()
    
    # Check for errors
    errors = []
    for name, status, msg in results:
        if not status:
            errors.append(f"{name}: {msg}")
    
    # Night mode: only show errors
    if is_quiet_hours():
        if errors:
            print(f"⚠️ External Alert: {', '.join(errors)}")
            sys.exit(1)
        else:
            # Silent - no output at night
            print("OK")
    else:
        # Normal mode
        if errors:
            print(f"⚠️ External Issues:")
            for e in errors:
                print(f"   {e}")
            sys.exit(1)
        else:
            print("✅ Alles OK")

if __name__ == "__main__":
    main()
