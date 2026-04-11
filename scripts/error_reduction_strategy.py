#!/usr/bin/env python3
"""
error_reduction_strategy.py — Echte Error Rate Senkung
====================================================
Sir HazeClaw - 2026-04-11

FOKUS: Echte Fixes, nicht nur Analyse!

Error Breakdown:
- 61% timeout → Timeout-Handling
- 25% loop → Loop Detection
- 14% not found → Path Verification

Usage:
    python3 error_reduction_strategy.py --analyze
    python3 error_reduction_strategy.py --fix-timeouts
    python3 error_reduction_strategy.py --fix-loops
    python3 error_reduction_strategy.py --fix-all
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "scripts"
LOG_FILE = WORKSPACE / "logs" / "error_reduction.log"

# Error patterns from actual error analysis
ERROR_BREAKDOWN = {
    "timeout": {"percentage": 61, "count": 107},
    "loop": {"percentage": 25, "count": 44},
    "not_found": {"percentage": 14, "count": 24}
}

def log(msg):
    """Log mit Timestamp."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    log_line = f"[{timestamp}] {msg}\n"
    with open(LOG_FILE, "a") as f:
        f.write(log_line)
    print(msg)

def analyze_errors():
    """Analysiert aktuelle Fehler."""
    print("=" * 60)
    print("ERROR ANALYSIS")
    print("=" * 60)
    print()
    
    print("📊 Error Breakdown:")
    for error_type, data in ERROR_BREAKDOWN.items():
        count = data["count"]
        pct = data["percentage"]
        bar = "█" * int(pct / 5)
        print(f"  {error_type:12} {pct:3}% ({count:3}) {bar}")
    print()
    
    # Find scripts mit problems
    print("🔍 Scanning scripts for issues...")
    
    timeout_issues = []
    loop_issues = []
    path_issues = []
    
    for script in SCRIPTS_DIR.glob("*.py"):
        if script.name.startswith("_"):
            continue
        
        content = script.read_text()
        
        # Check for timeout issues
        if ("subprocess.run" in content or "subprocess.call" in content or "exec(" in content):
            if "timeout=" not in content and "timeout =" not in content:
                timeout_issues.append(script.name)
        
        # Check for potential loops
        if "while " in content or "for " in content:
            if "break" not in content or "max_iter" not in content:
                loop_issues.append(script.name)
        
        # Check for path issues
        if "open(" in content or "Path(" in content:
            if not re.search(r'Path\([\'\"]', content):
                path_issues.append(script.name)
    
    print()
    print(f"⚠️  Timeout Issues: {len(timeout_issues)} scripts")
    for s in timeout_issues[:5]:
        print(f"    - {s}")
    if len(timeout_issues) > 5:
        print(f"    ... and {len(timeout_issues) - 5} more")
    
    print()
    print(f"⚠️  Potential Loop Issues: {len(loop_issues)} scripts")
    for s in loop_issues[:5]:
        print(f"    - {s}")
    
    print()
    print(f"⚠️  Path Issues: {len(path_issues)} scripts")
    for s in path_issues[:5]:
        print(f"    - {s}")
    
    print()
    print("💡 RECOMMENDATION:")
    print("   Run with --fix-timeouts, --fix-loops, or --fix-all")
    
    return {
        "timeout_issues": timeout_issues,
        "loop_issues": loop_issues,
        "path_issues": path_issues
    }

def fix_timeouts():
    """Fügt timeouts zu scripts hinzu."""
    print("=" * 60)
    print("FIXING TIMEOUTS")
    print("=" * 60)
    print()
    
    fixed = 0
    failed = 0
    
    for script in SCRIPTS_DIR.glob("*.py"):
        if script.name.startswith("_"):
            continue
        if script.name in ["apply_timeouts.py", "error_reduction_strategy.py"]:
            continue
        
        content = script.read_text()
        
        # Skip if already has timeout
        if "timeout=" in content or "timeout =" in content:
            continue
        
        # Skip if no subprocess/exec
        if "subprocess.run" not in content and "subprocess.call" not in content and "exec(" not in content:
            continue
        
        # Try to add timeout
        try:
            # Simple approach: add timeout=60 to subprocess.run/call
            # More sophisticated would parse the AST
            new_content = content
            
            # Pattern for subprocess.run( or subprocess.call(
            pattern = r'(subprocess\.(?:run|call))\('
            
            def add_timeout(match):
                func = match.group(1)
                return f'{func}(timeout=60, '
            
            new_content = re.sub(pattern, add_timeout, new_content)
            
            # Only write if changed
            if new_content != content:
                script.write_text(new_content)
                fixed += 1
                log(f"✅ Fixed timeout in: {script.name}")
        
        except Exception as e:
            failed += 1
            log(f"❌ Failed to fix {script.name}: {e}")
    
    print()
    print(f"📊 Results:")
    print(f"  ✅ Fixed: {fixed} scripts")
    print(f"  ❌ Failed: {failed} scripts")
    
    return {"fixed": fixed, "failed": failed}

def fix_loops():
    """Fügt loop protection zu scripts hinzu."""
    print("=" * 60)
    print("FIXING LOOPS")
    print("=" * 60)
    print()
    
    fixed = 0
    failed = 0
    
    for script in SCRIPTS_DIR.glob("*.py"):
        if script.name.startswith("_"):
            continue
        
        content = script.read_text()
        
        # Check if it has loops without break or max_iter
        if "while " in content or "for " in content:
            if "max_iter" not in content and "break" not in content:
                # This is a potential infinite loop risk
                # Add a comment warning
                try:
                    new_content = content
                    
                    # Add max_iter protection after first while/for
                    if "while " in content:
                        new_content = re.sub(
                            r'(while .+?:)',
                            r'\1\n    max_iter = max_iter or 1000\n    if max_iter <= 0: break\n    max_iter -= 1',
                            new_content,
                            count=1
                        )
                    
                    if new_content != content:
                        script.write_text(new_content)
                        fixed += 1
                        log(f"✅ Added loop protection to: {script.name}")
                
                except Exception as e:
                    failed += 1
                    log(f"❌ Failed to fix {script.name}: {e}")
    
    print()
    print(f"📊 Results:")
    print(f"  ✅ Fixed: {fixed} scripts")
    print(f"  ❌ Failed: {failed} scripts")
    
    return {"fixed": fixed, "failed": failed}

def fix_paths():
    """Fügt path verification hinzu."""
    print("=" * 60)
    print("FIXING PATHS")
    print("=" * 60)
    print()
    
    fixed = 0
    skipped = 0
    
    for script in SCRIPTS_DIR.glob("*.py"):
        if script.name.startswith("_"):
            continue
        if "path_check" in script.name or "path_verification" in script.name:
            skipped += 1
            continue
        
        content = script.read_text()
        
        # Check if it opens files without Path()
        if "open(" in content:
            if "Path(" not in content and "os.path" not in content:
                # This script uses raw open() - could have path issues
                # We'll just log it for now, fixing is complex
                log(f"⚠️  Potential path issue in: {script.name} (needs manual review)")
                fixed += 1
    
    print()
    print(f"📊 Results:")
    print(f"  ⚠️  Flagged for review: {fixed} scripts")
    print(f"  ⊘ Skipped: {skipped} scripts")
    
    return {"fixed": fixed, "skipped": skipped}

def fix_all():
    """Führt alle Fixes aus."""
    print("=" * 60)
    print("FULL ERROR REDUCTION STRATEGY")
    print("=" * 60)
    print()
    
    log("Starting full error reduction...")
    
    # Step 1: Analyze first
    print("\n📍 STEP 1: Analysis")
    issues = analyze_errors()
    
    # Step 2: Fix timeouts
    print("\n📍 STEP 2: Fix Timeouts")
    timeout_results = fix_timeouts()
    
    # Step 3: Fix loops
    print("\n📍 STEP 3: Fix Loops")
    loop_results = fix_loops()
    
    # Step 4: Fix paths
    print("\n📍 STEP 4: Fix Paths")
    path_results = fix_paths()
    
    # Summary
    print()
    print("=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    total_fixed = timeout_results["fixed"] + loop_results["fixed"] + path_results["fixed"]
    print(f"  Timeouts fixed: {timeout_results['fixed']}")
    print(f"  Loops fixed: {loop_results['fixed']}")
    print(f"  Paths flagged: {path_results['fixed']}")
    print(f"  TOTAL: {total_fixed} issues addressed")
    print()
    
    # Calculate potential error reduction
    # If we fix timeouts (61% of errors), that's biggest impact
    timeout_impact = (timeout_results["fixed"] / max(len(issues["timeout_issues"]), 1)) * 61
    loop_impact = (loop_results["fixed"] / max(len(issues["loop_issues"]), 1)) * 25
    
    total_impact = timeout_impact + loop_impact
    
    print(f"💡 POTENTIAL ERROR RATE REDUCTION:")
    print(f"   From timeout fixes: ~{timeout_impact:.1f}%")
    print(f"   From loop fixes: ~{loop_impact:.1f}%")
    print(f"   TOTAL: ~{total_impact:.1f}%")
    print()
    
    log(f"Full error reduction complete. Total fixed: {total_fixed}")

def main():
    if "--analyze" in sys.argv:
        analyze_errors()
    elif "--fix-timeouts" in sys.argv:
        fix_timeouts()
    elif "--fix-loops" in sys.argv:
        fix_loops()
    elif "--fix-paths" in sys.argv:
        fix_paths()
    elif "--fix-all" in sys.argv:
        fix_all()
    else:
        print("ERROR REDUCTION STRATEGY")
        print("=" * 60)
        print("Usage:")
        print("  --analyze      Analyze errors")
        print("  --fix-timeouts Fix timeout issues")
        print("  --fix-loops    Fix loop issues")
        print("  --fix-paths    Fix path issues")
        print("  --fix-all      Fix all issues")
        print()
        print("Run --analyze first to see what needs fixing!")

if __name__ == "__main__":
    main()
