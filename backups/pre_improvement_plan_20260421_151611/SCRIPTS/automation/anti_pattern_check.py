#!/usr/bin/env python3
"""
🦞 Sir HazeClaw — Anti-Pattern Check
Pre-Flight Safety Check vor Coding Tasks

Liest:
- memory/long_term/patterns.md → Anti-Patterns
- memory/autonomy/error_log.md → Bekannte Fehler

Gibt:
- Warnungen für aktuelle Patterns
- Check-Liste für Coding Tasks

Usage:
    python3 anti_pattern_check.py
    python3 anti_pattern_check.py --strict
    python3 anti_pattern_check.py --task "timezone handling"
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime, timezone

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
PATTERNS_FILE = WORKSPACE / "memory" / "long_term" / "patterns.md"
ERROR_LOG = WORKSPACE / "memory" / "autonomy" / "error_log.md"
LOG_FILE = WORKSPACE.parent / "logs" / "anti_pattern_check.log"

# Anti-Patterns aus patterns.md extrahiert
ANTI_PATTERNS = [
    {
        "pattern": r"timezone|datetime\.now\(\)",
        "warning": "⚠️ TIMEZONE: Nutze .replace(tzinfo=timezone.utc) bei offset-aware datetimes",
        "fix": "datetime.fromisoformat(dl).replace(tzinfo=timezone.utc)"
    },
    {
        "pattern": r"\.sort\(.*reverse.*\)",
        "warning": "⚠️ SORT: Bei complex types brauchst du key=lambda x: x[0]",
        "fix": "scored.sort(reverse=True, key=lambda x: x[0])"
    },
    {
        "pattern": r"for .* in .*\.items\(\)",
        "warning": "⚠️ DICT/JSON: Check ob dict ODER list — nutze isinstance()",
        "fix": "if isinstance(data, dict): for k,v in data.items()"
    },
    {
        "pattern": r"subprocess\.run|exec|system\(",
        "warning": "⚠️ SHELL: Prüfe security + timeout",
        "fix": "timeout=30 + shell=False wenn möglich"
    },
    {
        "pattern": r"rm -rf|del.*recursive",
        "warning": "🚫 DESTRUCTIVE: NIEMALS ohne Bestätigung!",
        "fix": "Erst fragen, trash nutzen statt rm"
    }
]

def log(msg: str, level: str = "INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def check_file_for_patterns(filepath: Path) -> list:
    """Check a file for anti-patterns."""
    findings = []
    if not filepath.exists():
        return findings
    
    content = filepath.read_text()
    for ap in ANTI_PATTERNS:
        matches = re.findall(ap["pattern"], content, re.IGNORECASE)
        if matches:
            findings.append({
                "pattern": ap["warning"],
                "fix": ap["fix"],
                "count": len(matches)
            })
    
    return findings

def get_recent_errors() -> list:
    """Hole die letzten Fehler aus error_log.md"""
    errors = []
    if not ERROR_LOG.exists():
        return errors
    
    lines = ERROR_LOG.read_text().split("\n")
    for line in lines[-50:]:  # Letzte 50 Zeilen
        if "ERROR" in line or "FAIL" in line:
            errors.append(line.strip())
    
    return errors[-5:]  # Nur letzte 5

def run_check(strict: bool = False):
    """Run anti-pattern check."""
    print("🦞 Sir HazeClaw — Anti-Pattern Check")
    print("=" * 50)
    
    # Check patterns.md
    print("\n📋 Checking patterns.md...")
    patterns = check_file_for_patterns(PATTERNS_FILE)
    if patterns:
        print(f"  ⚠️ {len(patterns)} patterns found in patterns.md (might be documentation)")
        for p in patterns[:3]:
            print(f"     - {p['pattern']}")
    
    # Get recent errors
    print("\n🚨 Recent Errors:")
    errors = get_recent_errors()
    if errors:
        for e in errors[:3]:
            print(f"     - {e[:80]}")
    else:
        print("     ✅ No recent errors in log")
    
    # Check für neue Coding Tasks
    if len(sys.argv) > 1 and "--task" in sys.argv:
        task_idx = sys.argv.index("--task") + 1
        if task_idx < len(sys.argv):
            task = sys.argv[task_idx]
            print(f"\n🔍 Checking Task: {task}")
            
            task_lower = task.lower()
            for ap in ANTI_PATTERNS:
                if re.search(ap["pattern"], task_lower, re.IGNORECASE):
                    print(f"  {ap['warning']}")
                    if not strict:
                        print(f"     Fix: {ap['fix']}")
            
            # Check gegen recent errors
            for e in errors:
                if any(w in e.lower() for w in ["timezone", "typeerror", "dict", "list", "sort"]):
                    print(f"  ⚠️ Similar error seen before: {e[:60]}...")
    
    print("\n✅ Anti-Pattern Check complete")
    print("\n💡 Remember:")
    print("   - Timezone: .replace(tzinfo=timezone.utc)")
    print("   - Dict/List: isinstance() check")
    print("   - Sort: key=lambda x: x[0]")
    print("   - Shell: timeout + shell=False")
    
    return 0

if __name__ == "__main__":
    strict = "--strict" in sys.argv
    sys.exit(run_check(strict))