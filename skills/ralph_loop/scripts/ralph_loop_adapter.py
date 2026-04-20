#!/usr/bin/env python3
"""
Ralph Loop Adapter für Sir HazeClaw

Wendet Ralph Loop Prinzipien auf bestehende iterative Systeme an:
- Completion Promise Detection
- Learnings Persistence  
- Max-Iteration Safety
- Stop Hook Pattern

Usage:
    python3 ralph_loop_adapter.py <task_name> --check <condition_script> --action <action_script>
    python3 ralph_loop_adapter.py learning_loop --check "python3 score_checker.py" --action "python3 learning_step.py"
    python3 ralph_loop_adapter.py --help
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Config
WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
LEARNINGS_FILE = WORKSPACE / "memory/ralph_learnings.md"
MAX_ITERATIONS_DEFAULT = 20
Ralph_MARKER = "<promise>COMPLETE</promise>"

def log(msg):
    print(f"[Ralph] {msg}", file=sys.stderr)

def load_learnings():
    """Load existing learnings from file."""
    if not LEARNINGS_FILE.exists():
        return []
    content = LEARNINGS_FILE.read_text()
    entries = []
    for line in content.split('\n'):
        if line.startswith('- '):
            entries.append(line[2:])
    return entries

def append_learning(task_name, iteration, finding):
    """Append a learning to the learnings file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"- [{timestamp}] [{task_name}] iter={iteration}: {finding}"
    
    if LEARNINGS_FILE.exists():
        content = LEARNINGS_FILE.read_text()
    else:
        content = "# Ralph Loop Learnings\n\n"
    
    content += entry + "\n"
    LEARNINGS_FILE.write_text(content)
    log(f"Learning saved: {finding[:60]}...")

def run_check(check_script, timeout=60):
    """Run a check script, return True if it reports COMPLETE."""
    try:
        result = subprocess.run(
            check_script, shell=True, capture_output=True, text=True, timeout=timeout
        )
        output = result.stdout + result.stderr
        
        # Check for completion promise
        if Ralph_MARKER in output:
            return True, "COMPLETE"
        
        # Parse JSON status if available
        if result.returncode == 0:
            return True, output[:200]
        
        return False, output[:200]
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except Exception as e:
        return False, f"ERROR: {e}"

def run_action(action_script, timeout=300):
    """Run an action script."""
    try:
        result = subprocess.run(
            action_script, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except Exception as e:
        return False, f"ERROR: {e}"

def ralph_loop(task_name, check_script, action_script, max_iterations=None, learn=True):
    """
    Execute a Ralph Loop until completion or max iterations.
    
    Args:
        task_name: Name of the task for learnings
        check_script: Script that returns True when task is complete
        action_script: Script that performs one iteration
        max_iterations: Safety limit (default: MAX_ITERATIONS_DEFAULT)
        learn: Whether to document learnings
    """
    if max_iterations is None:
        max_iterations = MAX_ITERATIONS_DEFAULT
    
    log(f"Starting Ralph Loop: {task_name} (max_iterations={max_iterations})")
    
    for iteration in range(1, max_iterations + 1):
        log(f"Iteration {iteration}/{max_iterations}")
        
        # Run one iteration
        success, action_output = run_action(action_script)
        
        if not success:
            log(f"Action failed: {action_output[:100]}")
            if learn:
                append_learning(task_name, iteration, f"Action failed: {action_output[:80]}")
        
        # Check completion
        complete, check_output = run_check(check_script)
        
        if complete:
            log(f"COMPLETE after {iteration} iterations")
            if learn:
                append_learning(task_name, iteration, f"Completed successfully")
            return True, iteration
        
        if iteration < max_iterations:
            log(f"Not complete yet, continuing...")
    
    log(f"Max iterations ({max_iterations}) reached without completion")
    if learn:
        append_learning(task_name, max_iterations, f"Max iterations reached")
    return False, max_iterations

def check_mode(check_script):
    """Just run the check and exit."""
    complete, output = run_check(check_script)
    if complete:
        print(Ralph_MARKER)
        print(f"Status: COMPLETE")
    else:
        print(f"Status: NOT_COMPLETE")
        print(f"Output: {output}")
    return 0 if complete else 1

def main():
    parser = argparse.ArgumentParser(description="Ralph Loop Adapter")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Ralph loop command
    loop_parser = subparsers.add_parser("loop", help="Run a Ralph Loop")
    loop_parser.add_argument("task_name", help="Name of the task")
    loop_parser.add_argument("--check", required=True, help="Check script (returns True when complete)")
    loop_parser.add_argument("--action", required=True, help="Action script (performs one iteration)")
    loop_parser.add_argument("--max-iterations", type=int, default=MAX_ITERATIONS_DEFAULT, help=f"Max iterations (default: {MAX_ITERATIONS_DEFAULT})")
    loop_parser.add_argument("--no-learn", action="store_true", help="Disable learning persistence")
    
    # Check-only command
    check_parser = subparsers.add_parser("check", help="Run check and exit")
    check_parser.add_argument("--check", required=True, help="Check script")
    
    # Learnings command
    learnings_parser = subparsers.add_parser("learnings", help="Show learnings")
    learnings_parser.add_argument("--task", help="Filter by task name")
    
    args = parser.parse_args()
    
    if args.command == "loop":
        success, iterations = ralph_loop(
            args.task_name,
            args.check,
            args.action,
            args.max_iterations,
            learn=not args.no_learn
        )
        sys.exit(0 if success else 1)
    
    elif args.command == "check":
        sys.exit(check_mode(args.check))
    
    elif args.command == "learnings":
        learnings = load_learnings()
        if args.task:
            learnings = [l for l in learnings if f"[{args.task}]" in l]
        
        if not learnings:
            print("No learnings found.")
        else:
            for learning in learnings[-20:]:  # Last 20
                print(learning)
        sys.exit(0)
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
