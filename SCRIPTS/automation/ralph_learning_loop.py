#!/usr/bin/env python3
"""
Ralph Loop Wrapper for Learning Loop v3
========================================
Enhances Learning Loop with Ralph Loop principles:
- Completion Promise: <promise>COMPLETE</promise> when score stable
- Ralph Learnings: Append discoveries to ralph_learnings.md
- Max-Iteration Safety: Track iterations per goal
- Stop Hook Pattern: Explicit completion criteria

This wraps learning_loop_v3.py and adds Ralph Layer on top.

Usage:
    python3 ralph_learning_loop.py              # Full Ralph Loop
    python3 ralph_learning_loop.py --status     # Show status only
    python3 ralph_learning_loop.py --check      # Check if complete
"""

import os
import sys
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
RALPH_LEARNINGS = WORKSPACE / "ceo/memory/ralph_learnings.md"
RALPH_STATE = WORKSPACE / "data/ralph_learning_state.json"

# Ralph Loop constants
RALPH_MARKER = "<promise>COMPLETE</promise>"
MAX_ITERATIONS_PER_GOAL = 20  # Safety limit
SCORE_TARGET = 0.80  # Target score for completion
SCORE_STABLE_THRESHOLD = 0.005  # Score variation threshold for stability
STABLE_RUNS = 3  # Number of stable runs to confirm completion

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[Ralph Learning] [{ts}] {msg}", file=sys.stderr)

def load_ralph_state():
    if RALPH_STATE.exists():
        return json.loads(RALPH_STATE.read_text())
    return {
        "iterations": 0,
        "goal": "learning_loop",
        "started_at": None,
        "last_score": 0,
        "stable_runs": 0,
        "completed": False
    }

def save_ralph_state(state):
    RALPH_STATE.write_text(json.dumps(state, indent=2))

def append_learning(category, finding):
    """Append a learning to the ralph learnings file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"- [{timestamp}] [{category}] {finding}"
    
    if not RALPH_LEARNINGS.exists():
        content = "# Ralph Loop Learnings\n\n"
    else:
        content = RALPH_LEARNINGS.read_text()
    
    content += entry + "\n"
    RALPH_LEARNINGS.write_text(content)
    log(f"Learning: [{category}] {finding[:80]}...")

def run_learning_loop():
    """Run the actual learning loop (v3)."""
    log("Running Learning Loop v3...")
    try:
        result = subprocess.run(
            ["python3", str(WORKSPACE / "SCRIPTS/automation/learning_loop_v3.py")],
            capture_output=True, text=True, timeout=300
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def parse_score(output):
    """Extract score from learning loop output."""
    match = re.search(r"Score:\s*(\d+\.\d+)", output)
    if match:
        return float(match.group(1))
    
    # Try JSON state
    state_file = WORKSPACE / "data/learning_loop_state.json"
    if state_file.exists():
        state = json.loads(state_file.read_text())
        return state.get("score", 0)
    
    return None

def check_completion(score):
    """Check if Ralph Loop completion criteria are met."""
    if score is None:
        return False
    
    state = load_ralph_state()
    state["last_score"] = score
    
    # Score target reached?
    if score >= SCORE_TARGET:
        state["stable_runs"] += 1
        log(f"Stable run {state['stable_runs']}/{STABLE_RUNS} (score={score:.3f})")
        
        if state["stable_runs"] >= STABLE_RUNS:
            state["completed"] = True
            # Note: caller saves state
            return True
    else:
        state["stable_runs"] = 0
        log(f"Score {score:.3f} < target {SCORE_TARGET}, reset stable_runs")
    
    # Note: caller saves state via run_ralph_cycle
    return False

def run_ralph_cycle():
    """Run one Ralph cycle (iteration)."""
    state = load_ralph_state()
    
    # Safety check
    if state["iterations"] >= MAX_ITERATIONS_PER_GOAL:
        log(f"MAX ITERATIONS ({MAX_ITERATIONS_PER_GOAL}) reached!")
        append_learning("safety", f"Max iterations reached without completion (score={state['last_score']:.3f})")
        return False, state["iterations"]
    
    # Run learning loop
    success, output = run_learning_loop()
    state["iterations"] += 1
    
    if not success:
        log(f"Learning loop failed: {output[:200]}")
        append_learning("error", f"Iteration {state['iterations']}: Learning loop failed")
    
    # Parse score
    score = parse_score(output)
    
    if score is not None:
        log(f"Iteration {state['iterations']}: Score={score:.3f}")
        
        # Learning: record improvements
        if "improvement" in output.lower() or "applied" in output.lower():
            improvements = re.findall(r"Applied: (.+)", output)
            for imp in improvements[:3]:
                append_learning("improvement", imp.strip())
        
        # Check completion
        if check_completion(score):
            log("COMPLETE! Ralph Loop succeeded.")
            append_learning("success", f"Completed after {state['iterations']} iterations (score={score:.3f})")
            print(f"\n{RALPH_MARKER}\n")
            return True, state["iterations"]
    else:
        log(f"Could not parse score from output")
    
    save_ralph_state(state)
    return False, state["iterations"]

def show_status():
    """Show Ralph Loop status."""
    state = load_ralph_state()
    print(f"=== Ralph Learning Loop Status ===")
    print(f"Iterations: {state['iterations']}/{MAX_ITERATIONS_PER_GOAL}")
    print(f"Last Score: {state['last_score']:.3f}")
    print(f"Stable Runs: {state['stable_runs']}/{STABLE_RUNS}")
    print(f"Completed: {state['completed']}")
    print(f"Target: {SCORE_TARGET}")
    
    # Also show learning loop state
    ll_state = WORKSPACE / "data/learning_loop_state.json"
    if ll_state.exists():
        ll = json.loads(ll_state.read_text())
        print(f"\n=== Learning Loop State ===")
        print(f"Score: {ll.get('score', 0):.3f}")
        print(f"Iteration: {ll.get('iteration', 'N/A')}")
        print(f"Learning Rate: {ll.get('learning_rate', 'N/A')}")

def main():
    if "--status" in sys.argv:
        show_status()
        return
    
    if "--check" in sys.argv:
        score = None
        state_file = WORKSPACE / "data/learning_loop_state.json"
        if state_file.exists():
            state = json.loads(state_file.read_text())
            score = state.get("score", 0)
        
        if check_completion(score):
            print(RALPH_MARKER)
            print("Status: COMPLETE")
        else:
            print("Status: NOT_COMPLETE")
        return
    
    # Full Ralph Loop
    log("Starting Ralph Learning Loop")
    state = load_ralph_state()
    
    if state["started_at"] is None:
        state["started_at"] = datetime.now().isoformat()
        state["iterations"] = 0
        state["completed"] = False
        save_ralph_state(state)
    
    success, iterations = run_ralph_cycle()
    
    if success:
        print(f"\n{RALPH_MARKER}\n")
        print(f"Success after {iterations} iterations!")
        sys.exit(0)
    else:
        print(f"Not yet complete after {iterations} iterations.")
        sys.exit(1)

if __name__ == "__main__":
    main()
