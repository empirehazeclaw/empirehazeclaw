#!/usr/bin/env python3
"""
pre-commit-hook.py - OpenClaw Workspace Pre-Commit Hook
Sir HazeClaw - 2026-04-12

Runs before git commit to:
1. Check for exposed API keys
2. Validate workspace structure
3. Auto-cleanup TEMPORARY if needed

Install: ln -s pre-commit-hook.py .git/hooks/pre-commit
"""

import re
import sys
import subprocess
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")

# Patterns that indicate API keys or secrets
SECRET_PATTERNS = [
    (r"OPENAI_API_KEY\s*=\s*['\"]sk-[A-Za-z0-9]{20,}['\"]", "OpenAI API Key"),
    (r"OPENROUTER_API_KEY\s*=\s*['\"]sk-or-[A-Za-z0-9]{20,}['\"]", "OpenRouter API Key"),
    (r"MINIMAX_API_KEY\s*=\s*['\"][^'\"]{20,}['\"]", "MiniMax API Key"),
    (r"STRIPE_API_KEY\s*=\s*['\"]sk_live_[A-Za-z0-9]{20,}['\"]", "Stripe Live Key"),
    (r"sk_live_[A-Za-z0-9]{24,}", "Stripe Live Key"),
    (r"ghp_[A-Za-z0-9]{36}", "GitHub Personal Token"),
    (r"gho_[A-Za-z0-9]{36}", "GitHub OAuth Token"),
    (r"AKIA[A-Z0-9]{16}", "AWS Access Key"),
    (r"[\w.-]+@[\w.-]+\.\w+.*(?:password|passwd|pwd)[\s]*[=:]\s*['\"][^'\"]{8,}['\"]", "Password in config"),
]

# Files that should NOT be committed
FORBIDDEN_PATTERNS = [
    r"\.env$",
    r"secrets\.env$",
    r"\.pem$",
    r"\.key$",
    r"passwords?\.txt$",
]


def check_for_secrets(staged_files: list) -> tuple:
    """Check staged files for exposed secrets."""
    issues = []
    
    for file_path in staged_files:
        path = Path(file_path)
        if not path.exists():
            continue
            
        # Skip files in backup directories (they contain old session data)
        if '_backup' in str(path) or '.backup' in str(path):
            continue
        
        # Skip binary files
        if path.suffix in ['.pyc', '.png', '.jpg', '.gif', '.pdf']:
            continue
            
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            continue
            
        for pattern, name in SECRET_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"⚠️  {file_path}: Possible {name} exposed")
    
    return issues


def check_forbidden_files(staged_files: list) -> list:
    """Check for files that should never be committed."""
    issues = []
    
    for file_path in staged_files:
        path = Path(file_path)
        filename = path.name.lower()
        
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, filename):
                issues.append(f"🚫 {file_path}: Forbidden file type ({pattern})")
    
    return issues


def validate_workspace_structure() -> list:
    """Validate workspace structure is clean."""
    issues = []
    
    # Check root has no stray Python files
    root_py = list(WORKSPACE.glob("*.py"))
    if root_py:
        issues.append(f"⚠️  Root Python files: {[p.name for p in root_py]}")
    
    # Check TEMPORARY doesn't have too many files
    temp_dir = WORKSPACE / "TEMPORARY"
    if temp_dir.exists():
        total_files = sum(1 for _ in temp_dir.rglob("*") if _.is_file())
        if total_files > 1000:
            issues.append(f"⚠️  TEMPORARY has {total_files} files - consider cleanup")
    
    return issues


def run_cleanup():
    """Run cleanup script if TEMPORARY needs it."""
    cleanup_script = WORKSPACE / "SCRIPTS" / "self_healing" / "cleanup_temporary.py"
    if cleanup_script.exists():
        try:
            result = subprocess.run(
                ["python3", str(cleanup_script)],
                capture_output=True,
                text=True,
                timeout=30
            )
            if "Nothing to clean" not in result.stdout:
                return result.stdout
        except Exception as e:
            return f"Cleanup failed: {e}"
    return None


def main():
    print("🔍 OpenClaw Pre-Commit Hook")
    print("=" * 40)
    
    # Get staged files
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            cwd=WORKSPACE,
            timeout=10
        )
        staged_files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
    except Exception as e:
        print(f"⚠️  Could not get staged files: {e}")
        staged_files = []
    
    if not staged_files:
        print("✅ No files to check")
        return 0
    
    print(f"📁 Checking {len(staged_files)} staged files...\n")
    
    all_issues = []
    
    # Check for secrets
    print("🔐 Checking for secrets...")
    secret_issues = check_for_secrets(staged_files)
    if secret_issues:
        all_issues.extend(secret_issues)
        for issue in secret_issues:
            print(f"   {issue}")
    else:
        print("   ✅ No secrets detected")
    
    # Check forbidden files
    print("\n🚫 Checking forbidden files...")
    forbidden_issues = check_forbidden_files(staged_files)
    if forbidden_issues:
        all_issues.extend(forbidden_issues)
        for issue in forbidden_issues:
            print(f"   {issue}")
    else:
        print("   ✅ No forbidden files")
    
    # Validate structure
    print("\n🏗️  Validating workspace structure...")
    structure_issues = validate_workspace_structure()
    if structure_issues:
        all_issues.extend(structure_issues)
        for issue in structure_issues:
            print(f"   {issue}")
    else:
        print("   ✅ Structure is clean")
    
    # Summary
    print("\n" + "=" * 40)
    if all_issues:
        print(f"❌ {len(all_issues)} issue(s) found")
        print("\nCommit ABORTED. Fix issues before committing.")
        return 1
    else:
        print("✅ All checks passed")
        print("🚀 Ready to commit")
        return 0


if __name__ == "__main__":
    sys.exit(main())
