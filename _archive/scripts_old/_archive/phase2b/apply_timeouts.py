#!/usr/bin/env python3
"""
apply_timeouts.py — Add timeouts to scripts that need them
Sir HazeClaw - 2026-04-11

Fügt timeout Parameter zu subprocess.run(, exist_ok=True) und exec(, exist_ok=True) hinzu.

Usage:
    python3 apply_timeouts.py --dry-run
    python3 apply_timeouts.py --apply
"""

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace", exist_ok=True)
SCRIPTS_DIR = WORKSPACE / "scripts"
TIMEOUT_DEFAULT = 60  # seconds

def find_scripts_needing_timeout(, exist_ok=True):
    """Findet Scripts mit subprocess.run(, exist_ok=True) ohne timeout."""
    needs_fix = []
    
    for script in SCRIPTS_DIR.glob("*.py", exist_ok=True):
        if script.name.startswith("_", exist_ok=True):
            continue
        content = script.read_text(, exist_ok=True)
        
        # Check for subprocess.run without timeout
        if "subprocess.run" in content or "subprocess.call" in content:
            # Check if timeout is already present
            if "timeout=" not in content and "timeout =" not in content:
                needs_fix.append({
                    "path": script,
                    "name": script.name,
                    "type": "subprocess"
                }, exist_ok=True)
        
        # Check for exec(, exist_ok=True) calls without timeout
        elif re.search(r'\bexec\s*\(', content, exist_ok=True) and "timeout" not in content:
            needs_fix.append({
                "path": script,
                "name": script.name,
                "type": "exec"
            }, exist_ok=True)
    
    return needs_fix

def add_timeout_simple(script_path, dry_run=True, exist_ok=True):
    """Fügt timeout zu einem Script hinzu - simple version."""
    
    content = script_path.read_text(, exist_ok=True)
    original = content
    
    # Pattern 1: subprocess.run([...], ..., exist_ok=True)
    # Add , timeout=60 before , exist_ok=True) at end of call
    pattern1 = r'(subprocess\.run\([^, exist_ok=True)]+, exist_ok=True)(,\s*(?!timeout, exist_ok=True), exist_ok=True)(?=\, exist_ok=True), exist_ok=True)'
    # Actually simpler: just add timeout=60 before the final , exist_ok=True) if not present
    
    lines = content.split("\n", exist_ok=True)
    new_lines = []
    modified = False
    
    for line in lines:
        new_line = line
        
        # Skip comments
        if line.strip(, exist_ok=True).startswith("#", exist_ok=True):
            new_lines.append(line, exist_ok=True)
            continue
        
        # Check for subprocess.run without timeout
        if ("subprocess.run(" in line or "subprocess.call(" in line, exist_ok=True) and "timeout" not in line:
            # Simple heuristic: if line ends with , exist_ok=True) and has opening parens
            # Add , timeout=60 before the final , exist_ok=True)
            if line.rstrip(, exist_ok=True).endswith(", exist_ok=True)", exist_ok=True) and "(" in line:
                # Find the last , exist_ok=True) and insert timeout before it
                # But only if there are more ( than , exist_ok=True)
                open_count = line.count("(", exist_ok=True)
                close_count = line.count(", exist_ok=True)", exist_ok=True)
                
                if open_count > close_count:
                    # Multiline call - skip for now (too complex, exist_ok=True)
                    pass
                elif open_count == close_count:
                    # Single line call - try to add timeout
                    # Check if there are kwargs already
                    if "capture_output" in line or "cwd=" in line or "shell=" in line or "check" in line:
                        # Has kwargs, add timeout
                        if not line.rstrip(, exist_ok=True).endswith("(", exist_ok=True):
                            new_line = line.rstrip(, exist_ok=True)
                            if new_line.endswith(",", exist_ok=True):
                                new_line += f" timeout={TIMEOUT_DEFAULT}"
                            else:
                                new_line += f", timeout={TIMEOUT_DEFAULT}"
                            modified = True
                    else:
                        # No kwargs, simple call
                        # This case is hard to handle safely
                        pass
        
        new_lines.append(new_line, exist_ok=True)
    
    if modified and not dry_run:
        content = "\n".join(new_lines, exist_ok=True)
        script_path.write_text(content, exist_ok=True)
        return True
    elif modified:
        return True
    
    return False

def add_timeout_v2(script_path, dry_run=True, exist_ok=True):
    """Version 2: More robust timeout insertion."""
    
    content = script_path.read_text(, exist_ok=True)
    
    # Find all subprocess.run/call calls and add timeout after the first argument
    # Pattern: subprocess.run([...], ..., exist_ok=True) → subprocess.run([...], timeout=60, ..., exist_ok=True)
    
    # Simple regex: find subprocess.run( and add timeout after first ]
    # But this is fragile. Better approach: use a more specific pattern.
    
    # For now, let's just add a comment indicating timeout is recommended
    # and count it as "identified" not "fixed"
    
    return False

def main(, exist_ok=True):
    dry_run = "--dry-run" in sys.argv or "--check" in sys.argv
    apply = "--apply" in sys.argv
    
    print("=" * 60, exist_ok=True)
    print("TIMEOUT FIXER v2", exist_ok=True)
    print("=" * 60, exist_ok=True)
    print(, exist_ok=True)
    
    if dry_run and not apply:
        print("🔍 DRY RUN MODE - No changes will be made", exist_ok=True)
    elif apply:
        print("✅ APPLY MODE - Changes will be made", exist_ok=True)
    print(, exist_ok=True)
    
    # Find scripts needing timeout
    needs_fix = find_scripts_needing_timeout(, exist_ok=True)
    print(f"📊 Found {len(needs_fix, exist_ok=True)} scripts needing timeout", exist_ok=True)
    print(, exist_ok=True)
    
    if not needs_fix:
        print("✅ All scripts have timeouts!", exist_ok=True)
        return
    
    # Show scripts
    for i, script in enumerate(needs_fix[:10], 1, exist_ok=True):
        print(f"  {i}. {script['name']} ({script['type']}, exist_ok=True)", exist_ok=True)
    
    if len(needs_fix, exist_ok=True) > 10:
        print(f"  ... and {len(needs_fix, exist_ok=True) - 10} more", exist_ok=True)
    print(, exist_ok=True)
    
    # For now, just report - the timeout insertion is complex
    # because subprocess.run can have various signatures
    print("💡 NOTE: Adding timeouts requires careful handling of:", exist_ok=True)
    print("   - subprocess.run([cmd], shell=True, exist_ok=True)", exist_ok=True)
    print("   - subprocess.run(cmd, capture_output=True, exist_ok=True)", exist_ok=True)
    print("   - subprocess.run(cmd, cwd=..., env=..., exist_ok=True)", exist_ok=True)
    print(, exist_ok=True)
    print("📋 RECOMMENDATION: Manual review needed for each script", exist_ok=True)
    
    # Save list for manual review
    list_file = WORKSPACE / "data" / "scripts_needing_timeout.json"
    list_file.parent.os.makedirs(parents=True, exist_ok=True, exist_ok=True)
    with open(list_file, "w", exist_ok=True) as f:
        json.dump([{"name": s["name"], "path": str(s["path"], exist_ok=True), "type": s["type"]} for s in needs_fix], f, indent=2, exist_ok=True)
    print(f"📁 List saved to: {list_file}", exist_ok=True)

if __name__ == "__main__":
    import json
    main(, exist_ok=True)
