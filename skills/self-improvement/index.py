#!/usr/bin/env python3
"""
Self-Improvement Skill for Sir HazeClaw
Provides tools for continuous self-improvement.
"""

import sys
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "scripts"

def run_self_eval(args=None):
    """Run self-evaluation."""
    import subprocess
    cmd = [sys.executable, str(SCRIPTS_DIR / "self_eval.py")]
    if args:
        cmd.extend(args)
    return subprocess.run(cmd, cwd=str(WORKSPACE))

def run_test_framework(args=None):
    """Run test framework."""
    import subprocess
    cmd = [sys.executable, str(SCRIPTS_DIR / "test_framework.py")]
    if args:
        cmd.extend(args)
    return subprocess.run(cmd, cwd=str(WORKSPACE))

def run_quality_metrics(args=None):
    """Run quality metrics."""
    import subprocess
    cmd = [sys.executable, str(SCRIPTS_DIR / "quality_metrics.py")]
    if args:
        cmd.extend(args)
    return subprocess.run(cmd, cwd=str(WORKSPACE))

def run_deep_reflection(args=None):
    """Run deep reflection."""
    import subprocess
    cmd = [sys.executable, str(SCRIPTS_DIR / "deep_reflection.py")]
    if args:
        cmd.extend(args)
    return subprocess.run(cmd, cwd=str(WORKSPACE))

def main():
    if len(sys.argv) < 2:
        print("Self-Improvement Skill")
        print("Usage: self-improvement <command>")
        print("Commands: self-eval, test, metrics, reflection")
        return 1
    
    cmd = sys.argv[1]
    
    if cmd == "self-eval":
        return run_self_eval(sys.argv[2:]).returncode
    elif cmd == "test":
        return run_test_framework(sys.argv[2:]).returncode
    elif cmd == "metrics":
        return run_quality_metrics(sys.argv[2:]).returncode
    elif cmd == "reflection":
        return run_deep_reflection(sys.argv[2:]).returncode
    else:
        print(f"Unknown command: {cmd}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
