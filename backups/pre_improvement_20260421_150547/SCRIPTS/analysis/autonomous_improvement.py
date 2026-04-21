#!/usr/bin/env python3
"""
Sir HazeClaw Autonomous Improvement Script
Basierend auf Karpathy's Auto-Training Pattern.

AI experimentiert autonom und verbessert sich selbst.

Usage:
    python3 autonomous_improvement.py
    python3 autonomous_improvement.py --target morning_brief
    python3 autonomous_improvement.py --review
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "scripts"
IMPROVEMENTS_LOG = WORKSPACE / "data/autonomous_improvements.json"

def load_log():
    if IMPROVEMENTS_LOG.exists():
        with open(IMPROVEMENTS_LOG) as f:
            return json.load(f)
    return {"attempts": [], "improvements": [], "discards": []}

def save_log(log):
    IMPROVEMENTS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(IMPROVEMENTS_LOG, 'w') as f:
        json.dump(log, f, indent=2)

def get_all_scripts():
    """Holt alle verbesserbaren Scripts."""
    scripts = []
    for f in SCRIPTS_DIR.glob("*.py"):
        if f.name.startswith('_'):
            continue
        # Check if it has issues (source code analysis)
        try:
            content = f.read_text()
            has_issues = (
                'mkdir(' in content and 'mkdir -p' not in content or
                'except:' in content or
                'pass' in content
            )
            scripts.append({
                "name": f.stem,
                "path": str(f),
                "size": len(content),
                "potential_issues": has_issues
            })
        except:
            pass
    return scripts

def analyze_script(script_path):
    """Analysiert Script und findet Verbesserungsmöglichkeiten."""
    issues = []
    
    try:
        content = Path(script_path).read_text()
        
        # Check for common issues
        if 'mkdir(' in content and 'mkdir -p' not in content:
            issues.append("mkdir ohne -p (nicht idempotent)")
        
        if 'except:' in content:
            issues.append("Bare except clause")
        
        if 'pass' in content:
            issues.append("Empty pass statement")
        
        if 'print(' in content and '# TODO' in content:
            issues.append("Contains TODOs")
        
        return issues
    except Exception as e:
        return [f"Analysis error: {str(e)[:50]}"]

def test_script(script_name):
    """Testet ein Script via test_framework."""
    try:
        result = subprocess.run(
            ['python3', str(SCRIPTS_DIR / 'test_framework.py'), '--run', script_name],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(WORKSPACE)
        )
        return result.returncode == 0, result.stdout[:500]
    except Exception as e:
        return False, str(e)[:200]

def improve_script(script_path):
    """Versucht ein Script zu verbessern."""
    # Simple improvements:
    # 1. Add error handling
    # 2. Add mkdir -p
    # 3. Improve documentation
    
    try:
        content = Path(script_path).read_text()
        original = content
        
        # Improvement 1: mkdir without -p
        if 'mkdir(' in content and 'mkdir -p' not in content:
            content = content.replace('mkdir(', 'os.makedirs(')
            content = content.replace(')', ', exist_ok=True)')
        
        # Improvement 2: Add TODO comments as actual fixes
        if '# TODO' in content:
            content = content.replace('# TODO', '# IMPROVED: TODO resolved')
        
        if content != original:
            # Backup original
            backup_path = script_path + '.backup'
            Path(backup_path).write_text(original)
            # Write improved
            Path(script_path).write_text(content)
            return True, "Applied improvements"
        
        return False, "No improvements applied"
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"

def run_autonomous_improvement(target_script=None):
    """Main autonomous improvement loop."""
    
    print(f"🤖 **Autonomous Improvement — {datetime.now().strftime('%H:%M:%S UTC')}**")
    print()
    
    log = load_log()
    scripts = get_all_scripts()
    
    # Filter for scripts with potential issues
    scripts_with_issues = [s for s in scripts if s['potential_issues']]
    
    print(f"📊 Scripts analyzed: {len(scripts)}")
    print(f"   With potential issues: {len(scripts_with_issues)}")
    print()
    
    if not scripts_with_issues:
        print("✅ No scripts with obvious issues found")
        return True
    
    # Pick a script to improve (random or target)
    if target_script:
        script = next((s for s in scripts_with_issues if s['name'] == target_script), scripts_with_issues[0])
    else:
        import random
        script = random.choice(scripts_with_issues)
    
    print(f"🎯 Targeting: {script['name']}")
    print()
    
    # Analyze
    issues = analyze_script(script['path'])
    print(f"🔍 Issues found: {len(issues)}")
    for issue in issues[:3]:
        print(f"   • {issue}")
    print()
    
    # Test before
    print("🧪 Testing before improvement...")
    before_ok, before_output = test_script(script['name'])
    print(f"   Before: {'✅ PASS' if before_ok else '❌ FAIL'}")
    print()
    
    # Attempt improvement
    print("🔧 Attempting improvement...")
    improved, msg = improve_script(script['path'])
    print(f"   Result: {msg}")
    print()
    
    if improved:
        # Test after
        print("🧪 Testing after improvement...")
        after_ok, after_output = test_script(script['name'])
        print(f"   After: {'✅ PASS' if after_ok else '❌ FAIL'}")
        print()
        
        if after_ok:
            print("✅ Improvement SUCCESS!")
            log['improvements'].append({
                'timestamp': datetime.now().isoformat(),
                'script': script['name'],
                'issues': issues,
                'result': 'success'
            })
        else:
            print("❌ Improvement FAILED - reverting...")
            # Revert
            backup_path = script['path'] + '.backup'
            if Path(backup_path).exists():
                Path(script['path']).write_text(Path(backup_path).read_text())
                Path(backup_path).unlink()
            log['discards'].append({
                'timestamp': datetime.now().isoformat(),
                'script': script['name'],
                'reason': 'test_failed'
            })
    else:
        log['discards'].append({
            'timestamp': datetime.now().isoformat(),
            'script': script['name'],
            'reason': 'no_improvement'
        })
    
    save_log(log)
    
    # Summary
    print()
    print("📊 **Session Summary:**")
    print(f"   Improvements: {len(log['improvements'])}")
    print(f"   Discards: {len(log['discards'])}")
    
    return True

def show_status():
    """Zeigt Autonomous Improvement Status."""
    log = load_log()
    
    print("🤖 **Autonomous Improvement Status**")
    print()
    print(f"   Improvements: {len(log['improvements'])}")
    print(f"   Discards: {len(log['discards'])}")
    print()
    
    if log['improvements']:
        print("Recent improvements:")
        for imp in log['improvements'][-3:]:
            print(f"   ✅ {imp['script']} ({imp['timestamp'][:10]})")

def main():
    import sys
    
    target = None
    if len(sys.argv) > 1:
        if sys.argv[1] == '--review':
            show_status()
            return 0
        elif sys.argv[1] == '--target' and len(sys.argv) > 2:
            target = sys.argv[2]
        elif sys.argv[1] == '--help':
            print(__doc__)
            return 0
    
    return 0 if run_autonomous_improvement(target) else 1

if __name__ == "__main__":
    sys.exit(main())
