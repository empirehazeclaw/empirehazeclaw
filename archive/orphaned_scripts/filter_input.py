#!/usr/bin/env python3
"""
Prompt Shield - Input Filter Wrapper
Nutzung: python3 filter_input.py "zu prüfender Text"
"""

import sys
import subprocess

def filter_input(text: str) -> bool:
    """Prüfe Input - True wenn sicher, False wenn blockiert"""
    result = subprocess.run(
        ["python3", "/home/clawbot/.openclaw/workspace/scripts/prompt_injection_shield.py"],
        input=text,
        capture_output=True,
        text=True,
        timeout=10
    )
    
    return result.returncode == 0

if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = sys.stdin.read()
    
    if filter_input(text):
        print("✅ SAFE")
        sys.exit(0)
    else:
        print("❌ BLOCKED")
        sys.exit(1)
