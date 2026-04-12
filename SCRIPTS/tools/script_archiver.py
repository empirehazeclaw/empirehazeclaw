#!/usr/bin/env python3
"""
script_archiver.py — Archive Unused Scripts Safely
==================================================
Archives scripts that are no longer used, with reference checking.

Usage:
    python3 script_archiver.py --list          # Show scripts to archive
    python3 script_archiver.py --archive <name>  # Archive specific script
    python3 script_archiver.py --check <name>    # Check if script is referenced
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "scripts"
ARCHIVE_DIR = WORKSPACE / "scripts" / "_archive"


# Scripts known to be unused or redundant
UNUSED_SCRIPTS = {
    # Outreach scripts (never used based on grep)
    "llm_outreach.py": "Outreach functionality - not used",
    "email_sequence.py": "Email outreach - not used", 
    "automated_outreach.py": "Outreach automation - not used",
    "improved_outreach.py": "Outreach - not used",
    "quick_outreach.py": "Outreach - not used",
    
    # Overlapping daily scripts
    "daily_summary.py": "Duplicates morning_brief/evening_summary",
    "evening_capture.py": "Duplicates evening_summary",
    
    # Experimental/one-off
    "deep_reflection.py": "Experimental - not in active use",
    "reflection_loop.py": "Experimental - merged into meta_improver",
    "session_analysis_cron.py": "Duplicates session_analyzer",
    
    # Overlapping with health_check
    "common_issues_check.py": "Functionality in health_check.py",
}

# Patterns that indicate a script is referenced
REFERENCE_PATTERNS = [
    r"from scripts\.{}",           # import
    r"import scripts\.{}",         # import
    r"scripts/{}\.py",            # direct reference
    r"python.*scripts/{}\.py",     # exec call
    r"\"{}\"",                    # string reference
    r"'{}'",                      # string reference
]


def check_references(script_name: str) -> Tuple[bool, List[str]]:
    """
    Check if a script is referenced elsewhere.
    
    Returns:
        Tuple of (is_referenced, list_of_files_that_reference)
    """
    references = []
    pattern = REFERENCE_PATTERNS[0].format(re.escape(script_name.replace(".py", "")))
    
    for py_file in WORKSPACE.rglob("*.py"):
        if script_name in py_file.name:
            continue  # Skip the script itself
        
        try:
            content = py_file.read_text(errors="ignore")
            base_name = script_name.replace(".py", "")
            
            # Check various reference patterns
            for ref_pattern in REFERENCE_PATTERNS:
                if ref_pattern.format(base_name) in content:
                    references.append(str(py_file.relative_to(WORKSPACE)))
                    break
        except Exception:
            pass
    
    return len(references) > 0, references


def archive_script(script_name: str, force: bool = False) -> Dict:
    """
    Archive a script safely.
    
    Returns:
        Dict with result
    """
    script_path = SCRIPTS_DIR / script_name
    
    if not script_path.exists():
        return {"success": False, "error": f"Script not found: {script_name}"}
    
    # Check if referenced
    is_refd, refs = check_references(script_name)
    
    if is_refd and not force:
        return {
            "success": False, 
            "error": f"Script is referenced by {len(refs)} files",
            "references": refs
        }
    
    # Create archive dir if needed
    ARCHIVE_DIR.mkdir(exist_ok=True)
    
    # Move to archive
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"{script_name.replace('.py', '')}_{timestamp}.py"
    archive_path = ARCHIVE_DIR / archive_name
    
    shutil.move(str(script_path), str(archive_path))
    
    return {
        "success": True,
        "archived_to": str(archive_path.relative_to(WORKSPACE)),
        "was_referenced": is_refd,
        "references": refs if is_refd else []
    }


def list_unused_scripts() -> List[Dict]:
    """List all scripts that appear unused."""
    results = []
    
    for script_name, reason in UNUSED_SCRIPTS.items():
        script_path = SCRIPTS_DIR / script_name
        
        if not script_path.exists():
            continue
        
        is_refd, refs = check_references(script_name)
        
        results.append({
            "script": script_name,
            "reason": reason,
            "exists": True,
            "referenced": is_refd,
            "ref_count": len(refs),
            "refs": refs[:3] if refs else []
        })
    
    return results


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Script Archiver")
    parser.add_argument("--list", action="store_true", help="List unused scripts")
    parser.add_argument("--check", metavar="SCRIPT", help="Check if script is referenced")
    parser.add_argument("--archive", metavar="SCRIPT", help="Archive a specific script")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually archive")
    parser.add_argument("--force", action="store_true", help="Force archive even if referenced")
    
    args = parser.parse_args()
    
    if args.check:
        is_refd, refs = check_references(args.check)
        if is_refd:
            print(f"❌ {args.check} IS referenced by {len(refs)} files:")
            for r in refs:
                print(f"   - {r}")
        else:
            print(f"✅ {args.check} is NOT referenced - safe to archive")
    
    elif args.archive:
        if args.dry_run:
            print(f"🔍 DRY RUN: Would archive {args.archive}")
            is_refd, refs = check_references(args.archive)
            if is_refd:
                print(f"   Warning: Referenced by {len(refs)} files")
        else:
            result = archive_script(args.archive, force=args.force)
            if result["success"]:
                print(f"✅ Archived: {result['archived_to']}")
                if result["was_referenced"]:
                    print(f"   Note: Was referenced by {len(result['references'])} files")
            else:
                print(f"❌ Failed: {result['error']}")
                if "references" in result:
                    print("   Referenced by:")
                    for r in result["references"]:
                        print(f"   - {r}")
    
    elif args.list:
        unused = list_unused_scripts()
        
        print(f"📋 Unused Scripts Analysis ({len(unused)} found)")
        print("=" * 60)
        
        safe_to_archive = [s for s in unused if not s["referenced"]]
        still_linked = [s for s in unused if s["referenced"]]
        
        print(f"\n🗑️  Safe to archive ({len(safe_to_archive)}):")
        for s in safe_to_archive:
            print(f"   - {s['script']}: {s['reason']}")
        
        if still_linked:
            print(f"\n⚠️  Still referenced ({len(still_linked)}):")
            for s in still_linked:
                print(f"   - {s['script']}: {s['ref_count']} refs")
        
        print(f"\n💡 To archive safe scripts:")
        print(f"   python3 script_archiver.py --archive <name>")
        print(f"\n💡 To archive even if referenced:")
        print(f"   python3 script_archiver.py --archive <name> --force")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
