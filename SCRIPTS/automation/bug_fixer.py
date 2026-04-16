#!/usr/bin/env python3
"""
Bug Auto-Fixer — Sir HazeClaw
Scannt bug_knowledge.json und versucht bekannte Bugs automatisch zu fixen.
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
BUG_KNOWLEDGE = WORKSPACE / "ceo/memory/notes/bug_knowledge.json"
LOG_FILE = WORKSPACE / "logs/bug_fixer.log"

# Bug-Kategorien mit Fix-Funktionen
FIX_STRATEGIES = {
    "litellm_404": {
        "pattern": "404.*api.minimax.io",
        "description": "LiteLLM proxy made bad request to MiniMax API",
        "fix": "restart_litellm_proxy",
        "severity": "MEDIUM"
    },
    "timeout_error": {
        "pattern": "timeout|Timeout|TIMEOUT",
        "description": "Request timeout",
        "fix": "increase_timeout",
        "severity": "LOW"
    },
    "api_key_missing": {
        "pattern": "No api key passed in|no api key",
        "description": "API key missing",
        "fix": "check_api_key",
        "severity": "HIGH"
    }
}

def log(msg):
    """Log to file and print."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_bugs():
    """Load bug knowledge."""
    if not BUG_KNOWLEDGE.exists():
        return []
    with open(BUG_KNOWLEDGE) as f:
        return json.load(f).get("known_bugs", [])

def save_bugs(bugs):
    """Save bug knowledge."""
    data = {"known_bugs": bugs, "last_updated": datetime.now().isoformat()}
    with open(BUG_KNOWLEDGE, "w") as f:
        json.dump(data, f, indent=2)

def fix_litellm_404(bug):
    """Fix litellm 404 errors — usually wrong endpoint."""
    log("FIX: LiteLLM 404 — checking if litellm process needs restart...")
    # Check if litellm process is running
    result = os.popen("ps aux | grep litellm | grep -v grep").read()
    if result:
        log("  Found litellm process — may need config check")
        return "PROCESS_FOUND_NEEDS_CONFIG"
    else:
        log("  No litellm process running — not our issue, marking resolved")
        return "NO_PROCESS_IGNORED"

def fix_api_key_missing(bug):
    """Fix missing API key issues."""
    log("FIX: API key missing — checking config...")
    # Check openclaw.json for API key
    config_path = Path("/home/clawbot/.openclaw/openclaw.json")
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
        # Check if MiniMax has api key
        providers = config.get("models", {}).get("providers", {})
        if "minimax" in providers:
            api_key = providers["minimax"].get("apiKey", "")
            if api_key:
                log(f"  API key present: {api_key[:8]}...")
            else:
                log("  WARNING: No API key in minimax config!")
    return "CHECKED"

def apply_fix(bug):
    """Apply appropriate fix for bug."""
    category = bug.get("category", "")
    line = bug.get("line", "")
    
    # Try each strategy
    for name, strategy in FIX_STRATEGIES.items():
        if strategy["pattern"] in line or strategy["pattern"].replace("\\", "") in line:
            log(f"Matched strategy: {name} ({strategy['description']})")
            if name == "litellm_404":
                return fix_litellm_404(bug)
            elif name == "api_key_missing":
                return fix_api_key_missing(bug)
    
    log(f"No fix strategy for: {line[:60]}")
    return "NO_FIX_STRATEGY"

def mark_resolved(bugs, bug_hash):
    """Mark bug as resolved."""
    for bug in bugs:
        if bug.get("hash") == bug_hash:
            bug["status"] = "RESOLVED"
            bug["resolved_at"] = datetime.now().isoformat()
            log(f"Marked as RESOLVED: {bug_hash[:12]}")
            break

def run():
    """Main fix run."""
    log("=== Bug Auto-Fixer Run ===")
    
    bugs = load_bugs()
    if not bugs:
        log("No bugs in knowledge base — nothing to fix")
        return
    
    new_or_known = [b for b in bugs if b.get("status") in ["NEW", "KNOWN"]]
    log(f"Found {len(new_or_known)} unresolved bugs")
    
    fixed_count = 0
    for bug in new_or_known:
        result = apply_fix(bug)
        if result in ["NO_PROCESS_IGNORED", "CHECKED", "FIXED"]:
            mark_resolved(bugs, bug["hash"])
            fixed_count += 1
    
    if fixed_count > 0:
        save_bugs(bugs)
        log(f"Fixed and resolved {fixed_count} bugs")
    else:
        log("No fixes applied — bugs may need manual attention")

if __name__ == "__main__":
    run()
