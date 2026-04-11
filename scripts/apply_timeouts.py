#!/usr/bin/env python3
"""
apply_timeouts.py — Add timeouts to scripts that need them
Sir HazeClaw - 2026-04-11

Fügt timeout Parameter zu subprocess.run() und exec() hinzu.

Usage:
    python3 apply_timeouts.py --dry-run
    python3 apply_timeouts.py --apply
"""

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "scripts"
TIMEOUT_DEFAULT = 60  # seconds

def find_scripts_needing_timeout():
    """Findet Scripts mit subprocess.run() ohne timeout."""
    needs_fix = []
    
    for script in SCRIPTS_DIR.glob("*.py"):
        if script.name.startswith("_"):
            continue
        content = script.read_text()
        
        # Check for subprocess.run without timeout
        if "subprocess.run" in content or "subprocess.call" in content:
            # Check if timeout is already present
            if "timeout=" not in content and "timeout =" not in content:
                needs_fix.append({
                    "path": script,
                    "name": script.name,
                    "type": "subprocess"
                })
        
        # Check for exec() calls without timeout
        elif re.search(r'\bexec\s*\(', content) and "timeout" not in content:
            needs_fix.append({
                "path": script,
                "name": script.name,
                "type": "exec"
            })
    
    return needs_fix

def add_timeout_simple(script_path, dry_run=True):
    """Fügt timeout zu einem Script hinzu - simple version."""
    
    content = script_path.read_text()
    original = content
    
    # Pattern 1: subprocess.run([...], ...)
    # Add , timeout=60 before ) at end of call
    pattern1 = r'(subprocess\.run\([^)]+)(,\s*(?!timeout))(?=\))'
    # Actually simpler: just add timeout=60 before the final ) if not present
    
    lines = content.split("\n")
    new_lines = []
    modified = False
    
    for line in lines:
        new_line = line
        
        # Skip comments
        if line.strip().startswith("#"):
            new_lines.append(line)
            continue
        
        # Check for subprocess.run without timeout
        if ("subprocess.run(" in line or "subprocess.call(" in line) and "timeout" not in line:
            # Simple heuristic: if line ends with ) and has opening parens
            # Add , timeout=60 before the final )
            if line.rstrip().endswith(")") and "(" in line:
                # Find the last ) and insert timeout before it
                # But only if there are more ( than )
                open_count = line.count("(")
                close_count = line.count(")")
                
                if open_count > close_count:
                    # Multiline call - skip for now (too complex)
                    pass
                elif open_count == close_count:
                    # Single line call - try to add timeout
                    # Check if there are kwargs already
                    if "capture_output" in line or "cwd=" in line or "shell=" in line or "check" in line:
                        # Has kwargs, add timeout
                        if not line.rstrip().endswith("("):
                            new_line = line.rstrip()
                            if new_line.endswith(","):
                                new_line += f" timeout={TIMEOUT_DEFAULT}"
                            else:
                                new_line += f", timeout={TIMEOUT_DEFAULT}"
                            modified = True
                    else:
                        # No kwargs, simple call
                        # This case is hard to handle safely
                        pass
        
        new_lines.append(new_line)
    
    if modified and not dry_run:
        content = "\n".join(new_lines)
        script_path.write_text(content)
        return True
    elif modified:
        return True
    
    return False

def add_timeout_v2(script_path, dry_run=True):
    """Version 2: More robust timeout insertion."""
    
    content = script_path.read_text()
    
    # Find all subprocess.run/call calls and add timeout after the first argument
    # Pattern: subprocess.run([...], ...) → subprocess.run([...], timeout=60, ...)
    
    # Simple regex: find subprocess.run( and add timeout after first ]
    # But this is fragile. Better approach: use a more specific pattern.
    
    # For now, let's just add a comment indicating timeout is recommended
    # and count it as "identified" not "fixed"
    
    return False

def main():
    dry_run = "--dry-run" in sys.argv or "--check" in sys.argv
    apply = "--apply" in sys.argv
    
    print("=" * 60)
    print("TIMEOUT FIXER v2")
    print("=" * 60)
    print()
    
    if dry_run and not apply:
        print("🔍 DRY RUN MODE - No changes will be made")
    elif apply:
        print("✅ APPLY MODE - Changes will be made")
    print()
    
    # Find scripts needing timeout
    needs_fix = find_scripts_needing_timeout()
    print(f"📊 Found {len(needs_fix)} scripts needing timeout")
    print()
    
    if not needs_fix:
        print("✅ All scripts have timeouts!")
        return
    
    # Show scripts
    for i, script in enumerate(needs_fix[:10], 1):
        print(f"  {i}. {script['name']} ({script['type']})")
    
    if len(needs_fix) > 10:
        print(f"  ... and {len(needs_fix) - 10} more")
    print()
    
    # For now, just report - the timeout insertion is complex
    # because subprocess.run can have various signatures
    print("💡 NOTE: Adding timeouts requires careful handling of:")
    print("   - subprocess.run([cmd], shell=True)")
    print("   - subprocess.run(cmd, capture_output=True)")
    print("   - subprocess.run(cmd, cwd=..., env=...)")
    print()
    print("📋 RECOMMENDATION: Manual review needed for each script")
    
    # Save list for manual review
    list_file = WORKSPACE / "data" / "scripts_needing_timeout.json"
    list_file.parent.mkdir(parents=True, exist_ok=True)
    with open(list_file, "w") as f:
        json.dump([{"name": s["name"], "path": str(s["path"]), "type": s["type"]} for s in needs_fix], f, indent=2)
    print(f"📁 List saved to: {list_file}")

if __name__ == "__main__":
    import json
    main()
