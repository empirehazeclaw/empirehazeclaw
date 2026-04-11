#!/usr/bin/env python3
"""
code_stats.py — Repository Complexity Analysis
Sir HazeClaw - 2026-04-11

Usage:
    python3 code_stats.py
"""

import subprocess
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")

def count_files(pattern):
    """Count files matching pattern."""
    result = subprocess.run(
        f"find {WORKSPACE} -type f {pattern} 2>/dev/null | wc -l",
        shell=True, capture_output=True, text=True
    )
    return int(result.stdout.strip())

def count_lines(pattern):
    """Count total lines matching pattern."""
    result = subprocess.run(
        f"find {WORKSPACE} -type f {pattern} -exec wc -l {{}} + 2>/dev/null | tail -1",
        shell=True, capture_output=True, text=True
    )
    if result.stdout.strip():
        return int(result.stdout.strip().split()[-2])
    return 0

def main():
    print("📊 CODE STATS — Repository Complexity")
    print("=" * 50)
    print()
    
    # File counts
    py_files = count_files("-name '*.py'")
    md_files = count_files("-name '*.md'")
    js_files = count_files("-name '*.js'")
    json_files = count_files("-name '*.json'")
    
    print("📁 Files by Type:")
    print(f"   Python: {py_files}")
    print(f"   Markdown: {md_files}")
    print(f"   JavaScript: {js_files}")
    print(f"   JSON: {json_files}")
    print()
    
    # Line counts
    py_lines = count_lines("-name '*.py'")
    md_lines = count_lines("-name '*.md'")
    
    print("📝 Lines of Code:")
    print(f"   Python: {py_lines:,}")
    print(f"   Markdown: {md_lines:,}")
    print(f"   Total: {py_lines + md_lines:,}")
    print()
    
    # Complexity indicators
    print("🧠 Complexity Indicators:")
    # Average file size
    avg_py = py_lines / py_files if py_files > 0 else 0
    print(f"   Avg Python file: {avg_py:.0f} lines")
    
    # Deep nesting detection (rough)
    deep_nesting = subprocess.run(
        f"grep -r 'if.*if.*if.*if' {WORKSPACE}/scripts/*.py 2>/dev/null | wc -l",
        shell=True, capture_output=True, text=True
    )
    nesting_count = int(deep_nesting.stdout.strip() if deep_nesting.stdout.strip() else 0)
    print(f"   Deep nesting (< 4 levels): {nesting_count} occurrences")
    print()
    
    # Health assessment
    print("🟢 Repository Health:")
    if avg_py < 200:
        print("   File sizes: ✅ Good (< 200 lines avg)")
    elif avg_py < 500:
        print("   File sizes: 🟡 Medium (200-500 lines avg)")
    else:
        print("   File sizes: 🔴 Large (> 500 lines avg)")
    
    if nesting_count < 10:
        print("   Nesting: ✅ Good")
    elif nesting_count < 30:
        print("   Nesting: 🟡 Medium")
    else:
        print("   Nesting: 🔴 High complexity")

if __name__ == "__main__":
    main()
