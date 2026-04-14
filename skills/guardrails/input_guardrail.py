#!/usr/bin/env python3
"""
input_guardrail.py — Pre-LLM Input Validator

Validates that actions have explicit triggers before execution.
Prevents over-active inference (acting on assumed inputs).

Usage:
    python3 input_guardrail.py --check "<action_description>"
    python3 input_guardrail.py --log-block "<trigger>"

Returns:
    PASS (0) — Real trigger confirmed
    BLOCK (1) — No trigger, action blocked
    UNCERTAIN (2) — Partial trigger, needs clarification
"""

import sys
import json
from datetime import datetime, timezone
from pathlib import Path

LOG_FILE = Path("/home/clawbot/.openclaw/workspace/logs/guardrail_interceptions.log")

TRIGGER_KEYWORDS = [
    "file received", "message received", "command received",
    "cron completed", "webhook received", "explicit request",
    "user said", "user asked", "user told", "file created",
    "error detected", "alert triggered"
]

INFERENCE_INDICATORS = [
    "maybe", "probably", "i think", "i assume", "possibly",
    "might have", "seems to", "looks like", "perhaps",
    "i noticed", "i saw", "i heard"  # without evidence
]


def log_interception(action: str, trigger: str, result: str, reason: str):
    """Log guardrail interception to file."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": "pre-llm",
        "action": action,
        "trigger": trigger,
        "result": result,
        "reason": reason
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def check_action_for_trigger(action_desc: str) -> tuple:
    """
    Check if action has an explicit trigger.
    
    Returns:
        (status, reason) — status is PASS/BLOCK/UNCERTAIN
    """
    action_lower = action_desc.lower()
    
    # Check for explicit trigger keywords
    has_trigger = any(kw in action_lower for kw in TRIGGER_KEYWORDS)
    
    # Check for inference indicators (bad)
    has_inference = any(ind in action_lower for ind in INFERENCE_INDICATORS)
    
    # Check for explicit user request patterns
    explicit_patterns = [
        "nico said", "nico wrote", "nico asked", "nico told",
        "user said", "user wrote", "user asked",
        "i received", "received file", "received message",
        "check", "run", "fix", "do", "execute"
    ]
    has_explicit = any(p in action_lower for p in explicit_patterns)
    
    if has_trigger and has_explicit:
        return ("PASS", "Explicit trigger confirmed")
    elif has_inference and not has_trigger:
        return ("BLOCK", "Inference detected without evidence")
    elif has_explicit and not has_trigger:
        return ("PASS", "Explicit command confirmed")
    elif not has_trigger and not has_explicit:
        return ("UNCERTAIN", "No clear trigger — needs confirmation")
    else:
        return ("UNCERTAIN", "Ambiguous — needs human check")


def main():
    if len(sys.argv) < 3 or sys.argv[1] != "--check":
        print("Usage: input_guardrail.py --check '<action description>'")
        sys.exit(2)
    
    action = " ".join(sys.argv[2:])
    status, reason = check_action_for_trigger(action)
    
    log_interception(action, "cli", status, reason)
    
    if status == "PASS":
        print(f"✅ PASS: {reason}")
        sys.exit(0)
    elif status == "BLOCK":
        print(f"🚫 BLOCK: {reason}")
        print(f"   Action: {action}")
        sys.exit(1)
    else:
        print(f"⚠️ UNCERTAIN: {reason}")
        print(f"   Action: {action}")
        sys.exit(2)


if __name__ == "__main__":
    main()
