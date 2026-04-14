#!/usr/bin/env python3
"""
output_guardrail.py — Post-LLM Self-Correction Validator

Self-check after actions to detect hallucinations or false inferences.
Implements the self-correction loop: error → feedback → revise → retry.

Usage:
    python3 output_guardrail.py --action "<what you did>"
    python3 output_guardrail.py --check-trigger "<action>" "<trigger>"
    python3 output_guardrail.py --correct "<wrong_action>" "<reason>"
"""

import sys
import json
from datetime import datetime, timezone
from pathlib import Path

LOG_FILE = Path("/home/clawbot/.openclaw/workspace/logs/guardrail_interceptions.log")

CORRECTION_PATTERNS = [
    ("assumed", "assumed without evidence"),
    ("maybe", "inference without proof"),
    ("probably", "unconfirmed assumption"),
    ("i noticed", "no actual evidence"),
    ("seems", "unverified perception"),
    ("i thought", "speculative without input"),
]


def log_correction(action: str, correction_type: str, details: str):
    """Log self-correction event."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": "post-llm",
        "action": action,
        "correction_type": correction_type,
        "details": details
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def check_trigger_alignment(action: str, trigger: str) -> tuple:
    """
    Verify action was properly aligned with its trigger.
    
    Returns:
        (status, details)
    """
    trigger_lower = trigger.lower()
    action_lower = action.lower()
    
    # Parse trigger type
    is_file = "file" in trigger_lower and ("received" in trigger_lower or "exists" in trigger_lower)
    is_message = any(w in trigger_lower for w in ["message", "wrote", "said", "told"])
    is_cron = "cron" in trigger_lower or "completed" in trigger_lower
    is_command = any(w in trigger_lower for w in ["check", "run", "do", "execute", "fix"])
    
    # Check alignment
    aligned = True
    issues = []
    
    if is_file and "file" not in action_lower:
        aligned = False
        issues.append("Action doesn't match file trigger")
    
    if is_message and not any(w in action_lower for w in ["respond", "reply", "message", "transcribe"]):
        if "respond" not in action_lower and "reply" not in action_lower:
            issues.append("Action doesn't match message trigger")
    
    if is_cron and "cron" not in action_lower and "check" not in action_lower:
        if "report" not in action_lower:
            issues.append("Action doesn't match cron trigger")
    
    if aligned:
        return ("OK", "Action properly aligned with trigger")
    else:
        return ("MISALIGNED", "; ".join(issues))


def detect_inference(action: str) -> tuple:
    """
    Detect if action was based on inference rather than evidence.
    
    Returns:
        (has_inference, issues[])
    """
    action_lower = action.lower()
    issues = []
    
    for pattern, desc in CORRECTION_PATTERNS:
        if pattern in action_lower:
            issues.append(f"'{pattern}' — {desc}")
    
    # Check for phantom triggers
    phantom_patterns = [
        ("i saw", "saw what? evidence?"),
        ("i heard", "heard how? from where?"),
        ("they said", "who said? when?"),
        ("it arrived", "what confirmed arrival?"),
    ]
    
    for pattern, desc in phantom_patterns:
        if pattern in action_lower:
            issues.append(f"'{pattern}': {desc}")
    
    return (len(issues) > 0, issues)


def self_correct(action: str, reason: str) -> str:
    """
    Generate corrected version of action description.
    """
    corrected = action
    
    # Remove inference language
    for pattern, _ in CORRECTION_PATTERNS:
        corrected = corrected.replace(pattern, "")
    
    log_correction(action, "self_correction", f"Reason: {reason}")
    
    return corrected.strip()


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  output_guardrail.py --action '<what you did>'")
        print("  output_guardrail.py --check-trigger '<action>' '<trigger>'")
        print("  output_guardrail.py --correct '<wrong>' '<reason>'")
        sys.exit(2)
    
    cmd = sys.argv[1]
    
    if cmd == "--action":
        action = " ".join(sys.argv[2:])
        
        has_inf, issues = detect_inference(action)
        
        if has_inf:
            print(f"⚠️ SELF-CHECK FAILED")
            print(f"   Action: {action}")
            print(f"   Issues:")
            for issue in issues:
                print(f"   - {issue}")
            print(f"\n💡 Suggestion: {self_correct(action, '; '.join(issues))}")
            log_correction(action, "inference_detected", "; ".join(issues))
            sys.exit(1)
        else:
            print(f"✅ SELF-CHECK PASSED")
            print(f"   Action: {action}")
            log_correction(action, "passed", "No issues detected")
            sys.exit(0)
    
    elif cmd == "--check-trigger":
        if len(sys.argv) < 4:
            print("Usage: --check-trigger '<action>' '<trigger>'")
            sys.exit(2)
        action = sys.argv[2]
        trigger = sys.argv[3]
        
        status, details = check_trigger_alignment(action, trigger)
        
        print(f"{status}: {details}")
        print(f"   Action: {action}")
        print(f"   Trigger: {trigger}")
        
        sys.exit(0 if status == "OK" else 1)
    
    elif cmd == "--correct":
        if len(sys.argv) < 4:
            print("Usage: --correct '<wrong>' '<reason>'")
            sys.exit(2)
        wrong = sys.argv[2]
        reason = sys.argv[3]
        
        corrected = self_correct(wrong, reason)
        print(f"✅ Corrected: {corrected}")
        sys.exit(0)
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(2)


if __name__ == "__main__":
    main()
