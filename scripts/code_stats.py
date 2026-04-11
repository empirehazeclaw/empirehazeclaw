#!/usr/bin/env python3
"""
code_stats.py — Repository Complexity Analysis
Sir HazeClaw - 2026-04-11

FIXED: shell=True removed for security
"""

import subprocess
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")

def count_files(extension):
    """Count files matching extension (e.g., '*.py')."""
    cmd = ["find", str(WORKSPACE), "-type", "f", "-name", extension]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    lines = [l for l in result.stdout.strip().split("\n") if l]
    return len(lines)

def count_lines(extension):
    """Count total lines for files matching extension."""
    cmd = ["find", str(WORKSPACE), "-type", "f", "-name", extension, "-exec", "wc", "-l", "{}", "+"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.stdout.strip():
        lines = result.stdout.strip().split("\n")
        if lines:
            last = lines[-1]
            parts = last.strip().split()
            if len(parts) >= 2:
                return int(parts[-2])
    return 0

def deep_nesting_count():
    """Count files with deep nesting (4+ if statements)."""
    cmd = ["grep", "-r", "-E", "if.*if.*if.*if", f"{WORKSPACE}/scripts/", "-l"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    files = [l for l in result.stdout.strip().split("\n") if l]
    return len(files)

def main():
    print("📊 CODE STATS — Repository Complexity")
    print("=" * 50)
    print()
    
    # File counts (using list args instead of shell=True)
    py_files = count_files("*.py")
    md_files = count_files("*.md")
    js_files = count_files("*.js")
    json_files = count_files("*.json")
    
    print("📁 Files by Type:")
    print(f"   Python: {py_files}")
    print(f"   Markdown: {md_files}")
    print(f"   JavaScript: {js_files}")
    print(f"   JSON: {json_files}")
    print()
    
    # Line counts
    py_lines = count_lines("*.py")
    md_lines = count_lines("*.md")
    
    print("📝 Lines of Code:")
    print(f"   Python: {py_lines:,}")
    print(f"   Markdown: {md_lines:,}")
    print(f"   Total: {py_lines + md_lines:,}")
    print()
    
    # Complexity indicators
    print("🧠 Complexity Indicators:")
    avg_py = py_lines / py_files if py_files > 0 else 0
    print(f"   Avg Python file: {avg_py:.0f} lines")
    
    # Deep nesting detection
    nesting_count = deep_nesting_count()
    print(f"   Deep nesting (4+ levels): {nesting_count} files")
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
    
    print()
    print("🔒 Security: shell=True removed ✅")

if __name__ == "__main__":
    main()
