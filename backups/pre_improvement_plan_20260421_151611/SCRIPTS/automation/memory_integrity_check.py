#!/usr/bin/env python3
"""
Memory Integrity Check — Phase 3
================================
Validates that long_term/ memory persists correctly.
Tests file existence, readability, and basic structure.

Usage:
    python3 memory_integrity_check.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
LONG_TERM = WORKSPACE / "memory/long_term"
MEMORY_MD = WORKSPACE / "ceo/MEMORY.md"

def check_long_term_memory():
    """Check long_term/ memory structure and content."""
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "passed": True
    }
    
    # Test 1: Directory exists
    exists = LONG_TERM.exists() and LONG_TERM.is_dir()
    results["tests"].append({
        "name": "long_term_dir_exists",
        "passed": exists,
        "message": f"Directory exists: {exists}"
    })
    if not exists:
        results["passed"] = False
        return results
    
    # Test 2: Required files exist
    required_files = ["facts.md", "preferences.md", "patterns.md"]
    for fname in required_files:
        fpath = LONG_TERM / fname
        file_exists = fpath.exists()
        results["tests"].append({
            "name": f"file_exists_{fname}",
            "passed": file_exists,
            "message": f"{fname}: {file_exists}"
        })
        if not file_exists:
            results["passed"] = False
    
    # Test 3: Files are readable and non-empty
    for fname in required_files:
        fpath = LONG_TERM / fname
        if fpath.exists():
            try:
                content = fpath.read_text()
                non_empty = len(content) > 100
                results["tests"].append({
                    "name": f"file_valid_{fname}",
                    "passed": non_empty,
                    "message": f"{fname}: {len(content)} chars, valid: {non_empty}"
                })
            except Exception as e:
                results["tests"].append({
                    "name": f"file_read_error_{fname}",
                    "passed": False,
                    "message": f"{fname}: {str(e)}"
                })
                results["passed"] = False
    
    # Test 4: MEMORY.md references long_term
    if MEMORY_MD.exists():
        content = MEMORY_MD.read_text()
        has_reference = "long_term" in content.lower()
        results["tests"].append({
            "name": "memory_md_references_long_term",
            "passed": has_reference,
            "message": f"MEMORY.md references long_term: {has_reference}"
        })
    
    return results

def check_notes_structure():
    """Check notes/ directory structure."""
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "passed": True
    }
    
    notes_dir = WORKSPACE / "memory/notes"
    
    # Required subdirs
    required_dirs = ["SYSTEM", "SCRIPTS", "LEARNING", "OPERATIONS", "ARCHIVE"]
    for dname in required_dirs:
        dpath = notes_dir / dname
        exists = dpath.exists() and dpath.is_dir()
        results["tests"].append({
            "name": f"dir_exists_{dname}",
            "passed": exists,
            "message": f"notes/{dname}: {exists}"
        })
    
    # Required index file
    index_exists = (notes_dir / "_index.md").exists()
    results["tests"].append({
        "name": "index_exists",
        "passed": index_exists,
        "message": f"_index.md: {index_exists}"
    })
    
    # Count docs
    doc_count = len(list(notes_dir.rglob("*.md")))
    results["tests"].append({
        "name": "doc_count",
        "passed": doc_count >= 4,
        "message": f"Total docs: {doc_count}"
    })
    
    return results

def main():
    print("🔍 MEMORY INTEGRITY CHECK")
    print("=" * 50)
    
    all_passed = True
    
    # Check long_term
    print("\n📂 long_term/ Memory:")
    lt_results = check_long_term_memory()
    for test in lt_results["tests"]:
        status = "✅" if test["passed"] else "❌"
        print(f"  {status} {test['message']}")
    if not lt_results["passed"]:
        all_passed = False
    
    # Check notes
    print("\n📚 notes/ Structure:")
    notes_results = check_notes_structure()
    for test in notes_results["tests"]:
        status = "✅" if test["passed"] else "❌"
        print(f"  {status} {test['message']}")
    if not notes_results["passed"]:
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
