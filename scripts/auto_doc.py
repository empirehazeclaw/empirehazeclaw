#!/usr/bin/env python3
"""
Sir HazeClaw Auto Script Documentation
Automatisch Scripts dokumentieren und README.md pflegen.

Usage:
    python3 auto_doc.py                 # Scan all scripts
    python3 auto_doc.py --check <file> # Check single script
    python3 auto_doc.py --update       # Update all docs
    python3 auto_doc.py --report       # Show undocumented scripts
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "scripts"
DOCS_DIR = WORKSPACE / "docs"
README = WORKSPACE / "scripts" / "README.md"

# Patterns to detect documentation
HAS_USAGE = re.compile(r'"""[^"]*Usage:', re.MULTILINE)
HAS_MAIN = re.compile(r'if __name__.*main', re.MULTILINE)
HAS_DESCRIPTION = re.compile(r'""".*\n.*\n.*"""', re.MULTILINE)
FUNCTION_DOCSTRING = re.compile(r'def \w+\([^)]*\):\s*"""[^"]*"""', re.MULTILINE)

# Status colors
COLOR_GREEN = '\033[92m'
COLOR_YELLOW = '\033[93m'
COLOR_RED = '\033[91m'
COLOR_RESET = '\033[0m'

def scan_script(script_path):
    """Scan a single script for documentation status."""
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        filename = script_path.name
        size = len(content)
        lines = len(content.split('\n'))
        
        # Check documentation coverage
        has_usage = bool(HAS_USAGE.search(content))
        has_main_block = bool(HAS_MAIN.search(content))
        has_description = bool(HAS_DESCRIPTION.search(content))
        
        # Calculate score
        score = 0
        if has_description:
            score += 40
        if has_usage:
            score += 30
        if has_main_block:
            score += 15
        # Check for function-level docs
        func_docs = len(FUNCTION_DOCSTRING.findall(content))
        score += min(func_docs * 5, 15)
        
        # Status
        if score >= 80:
            status = "well-documented"
            color = COLOR_GREEN
        elif score >= 50:
            status = "partial"
            color = COLOR_YELLOW
        else:
            status = "needs-doc"
            color = COLOR_RED
        
        return {
            "file": filename,
            "path": str(script_path),
            "size": size,
            "lines": lines,
            "score": score,
            "status": status,
            "color": color,
            "has_usage": has_usage,
            "has_main": has_main_block,
            "func_docs": func_docs
        }
    except Exception as e:
        return {
            "file": script_path.name,
            "error": str(e)
        }

def scan_all_scripts():
    """Scan all Python scripts in scripts directory."""
    scripts = []
    
    for py_file in SCRIPTS_DIR.glob("*.py"):
        if py_file.name.startswith("_"):
            continue  # Skip private modules
        result = scan_script(py_file)
        scripts.append(result)
    
    return sorted(scripts, key=lambda x: x.get("score", 0))

def generate_report(scripts):
    """Generate documentation report."""
    total = len(scripts)
    well_doc = sum(1 for s in scripts if s.get("status") == "well-documented")
    partial = sum(1 for s in scripts if s.get("status") == "partial")
    needs_doc = sum(1 for s in scripts if s.get("status") == "needs-doc")
    
    avg_score = sum(s.get("score", 0) for s in scripts) / total if total else 0
    
    print("📄 **Auto Script Documentation Report**")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print()
    print(f"   **Total Scripts:** {total}")
    print(f"   ✅ Well-documented: {well_doc} ({well_doc/total*100:.0f}%)")
    print(f"   🟡 Partial: {partial} ({partial/total*100:.0f}%)")
    print(f"   ❌ Needs documentation: {needs_doc} ({needs_doc/total*100:.0f}%)")
    print()
    print(f"   **Average Documentation Score:** {avg_score:.0f}/100")
    print()
    
    # Show scripts needing attention
    needs_attention = [s for s in scripts if s.get("score", 0) < 50]
    if needs_attention:
        print("   **⚠️ Scripts needing documentation:**")
        for s in needs_attention[:10]:  # Top 10
            print(f"     - {s['file']} ({s.get('score', 0)}/100)")
        if len(needs_attention) > 10:
            print(f"     ... and {len(needs_attention) - 10} more")
    else:
        print("   ✅ All scripts are well-documented!")

def update_readme(scripts):
    """Update scripts/README.md with documentation status."""
    lines = []
    lines.append("# Scripts Directory")
    lines.append("")
    lines.append(f"*Auto-generated documentation - {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*")
    lines.append("")
    lines.append("## Documentation Status")
    lines.append("")
    lines.append("| Script | Score | Status | Lines |")
    lines.append("|--------|-------|--------|-------|")
    
    for s in scripts:
        score = s.get("score", 0)
        status = s.get("status", "unknown")
        
        status_icon = "✅" if status == "well-documented" else "🟡" if status == "partial" else "❌"
        
        lines.append(f"| `{s['file']}` | {score}/100 | {status_icon} | {s.get('lines', 0)} |")
    
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    
    total = len(scripts)
    well_doc = sum(1 for s in scripts if s.get("status") == "well-documented")
    
    lines.append(f"- Total: {total} scripts")
    lines.append(f"- Well-documented: {well_doc} ({well_doc/total*100:.0f}%)" if total else "- No scripts found")
    
    content = "\n".join(lines)
    
    # Create docs directory if needed
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    
    output_file = DOCS_DIR / "scripts_index.md"
    with open(output_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Documentation updated: {output_file}")
    return output_file

def check_single(script_path):
    """Check and show documentation for a single script."""
    if not Path(script_path).exists:
        print(f"❌ Script not found: {script_path}")
        return
    
    result = scan_script(Path(script_path))
    
    print(f"📄 **Documentation Check: {result['file']}**")
    print()
    print(f"   Score: {result.get('score', 0)}/100")
    print(f"   Status: {result.get('status', 'unknown')}")
    print(f"   Lines: {result.get('lines', 0)}")
    print()
    
    checks = [
        ("Has docstring/description", result.get('score', 0) >= 40),
        ("Has Usage section", result.get('has_usage', False)),
        ("Has main block", result.get('has_main', False)),
        ("Has function docs", result.get('func_docs', 0) > 0)
    ]
    
    print("   **Checks:**")
    for check, passed in checks:
        icon = "✅" if passed else "❌"
        print(f"   {icon} {check}")

def suggest_improvements(script_path):
    """Suggest documentation improvements for a script."""
    if not Path(script_path).exists:
        print(f"❌ Script not found: {script_path}")
        return
    
    with open(script_path, 'r') as f:
        content = f.read()
    
    suggestions = []
    
    if not HAS_USAGE.search(content):
        suggestions.append("Add Usage section in docstring")
    if not HAS_DESCRIPTION.search(content):
        suggestions.append("Add description at the top of docstring")
    if not HAS_MAIN.search(content):
        suggestions.append("Add if __name__ == '__main__' block")
    
    if suggestions:
        print(f"💡 **Suggestions for {Path(script_path).name}:**")
        for s in suggestions:
            print(f"   - {s}")
    else:
        print(f"✅ {Path(script_path).name} looks well-documented!")

def main():
    if len(sys.argv) < 2:
        # Default: scan all and show report
        scripts = scan_all_scripts()
        generate_report(scripts)
    elif sys.argv[1] == "--report":
        scripts = scan_all_scripts()
        generate_report(scripts)
    elif sys.argv[1] == "--update":
        scripts = scan_all_scripts()
        update_readme(scripts)
    elif sys.argv[1] == "--check" and len(sys.argv) > 2:
        check_single(sys.argv[2])
    elif sys.argv[1] == "--suggest" and len(sys.argv) > 2:
        suggest_improvements(sys.argv[2])
    elif sys.argv[1] == "--help":
        print(__doc__)
    else:
        print(__doc__)

if __name__ == "__main__":
    sys.exit(main() or 0)