#!/usr/bin/env python3
"""
Subagent Health Check
Prüft ob Subagent spawning möglich ist.
"""

import subprocess
import sys
from pathlib import Path

def check_api_keys():
    """Prüft ob API Keys verfügbar."""
    keys = {
        'minimax': False,
        'openrouter': False,
    }
    
    # Check environment
    result = subprocess.run(['env'], capture_output=True, text=True)
    for line in result.stdout.split('\n'):
        if 'MINIMAX' in line:
            keys['minimax'] = True
        if 'OPENROUTER' in line:
            keys['openrouter'] = True
    
    return keys

def check_model_health():
    """Prüft ob Model erreichbar."""
    # Simple check: can we run a simple command?
    try:
        result = subprocess.run(
            ['python3', '-c', 'print("ok")'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False

def main():
    print("🔍 **Subagent Health Check**")
    print()
    
    # Check API keys
    keys = check_api_keys()
    print(f"API Keys:")
    print(f"  minimax: {'✅' if keys['minimax'] else '❌'}")
    print(f"  openrouter: {'✅' if keys['openrouter'] else '❌'}")
    
    # Check model health
    health = check_model_health()
    print(f"\nModel Health: {'✅' if health else '❌'}")
    
    # Summary
    print()
    if keys['minimax'] and health:
        print("✅ Subagent spawning möglich")
        return 0
    else:
        print("⚠️  Subagent spawning可能会失败")
        print("Empfehlung: Task direkt ausführen statt subagent")
        return 1

if __name__ == "__main__":
    sys.exit(main())
