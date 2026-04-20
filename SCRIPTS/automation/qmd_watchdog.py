#!/usr/bin/env python3
"""QMD Watchdog — prüft ob QMD läuft."""

import subprocess
import sys

def check_qmd():
    try:
        result = subprocess.run(["qmd", "collection", "list"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("QMD: running")
            return True
        else:
            print("QMD: not responding")
            return False
    except FileNotFoundError:
        print("QMD: not found")
        return False
    except Exception as e:
        print(f"QMD: error — {e}")
        return False

if __name__ == "__main__":
    check_qmd()
