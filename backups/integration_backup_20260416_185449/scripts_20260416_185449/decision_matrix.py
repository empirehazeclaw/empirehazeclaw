#!/usr/bin/env python3
"""
Decision Matrix — Sir HazeClaw Autonomy Engine
Categorizes actions and determines backup/test/approval requirements
"""

import json
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
AUTONOMY_DIR = WORKSPACE / "memory" / "autonomy"
BACKUP_DIR = Path("/home/clawbot/.openclaw/workspace/backups/autonomy")

# Categories with their requirements
CATEGORIES = {
    "TINY": {
        "backup": False,
        "test": False,
        "approval": False,
        "examples": [
            "temp file cleanup < 100 files",
            "log rotation",
            "health check pings",
            "memory consolidation (read-only)"
        ]
    },
    "SMALL": {
        "backup": True,
        "backup_type": "copy",
        "test": False,
        "approval": False,
        "examples": [
            "KG entity add/update (non-critical)",
            "memory file edits (learnings, notes)",
            "script fixes (known patterns)",
            "cron re-trigger (same job)",
            "threshold updates in config"
        ]
    },
    "MEDIUM": {
        "backup": True,
        "backup_type": "git_snapshot",
        "test": True,
        "test_timeout": 30,
        "approval": False,
        "examples": [
            "new cron job creation",
            "script modifications (code changes)",
            "config value changes",
            "new tool/skill registration",
            "dependency updates"
        ]
    },
    "LARGE": {
        "backup": True,
        "backup_type": "full_snapshot",
        "test": True,
        "test_timeout": 60,
        "approval": True,
        "approval_type": "ask_nico",
        "examples": [
            "new systems/services",
            "architecture changes",
            "multiple script changes at once",
            "external integrations",
            "security policy changes"
        ]
    },
    "CRITICAL": {
        "backup": True,
        "backup_type": "full_verified",
        "test": True,
        "test_timeout": 120,
        "approval": True,
        "approval_type": "explicit_nico",
        "examples": [
            "gateway config changes",
            "user-facing communications",
            "financial transactions",
            "destructive operations (delete, truncate)",
            "permission changes"
        ]
    }
}

# Action type mapping
ACTION_PATTERNS = {
    "temp_cleanup": "TINY",
    "log_rotation": "TINY",
    "health_check": "TINY",
    "read_only": "TINY",
    "kg_update": "SMALL",
    "memory_edit": "SMALL",
    "script_fix": "SMALL",
    "cron_retrigger": "SMALL",
    "config_change": "SMALL",
    "new_cron": "MEDIUM",
    "script_modify": "MEDIUM",
    "config_modify": "MEDIUM",
    "new_tool": "MEDIUM",
    "new_system": "LARGE",
    "architecture_change": "LARGE",
    "external_integration": "LARGE",
    "security_change": "LARGE",
    "gateway_change": "CRITICAL",
    "external_message": "CRITICAL",
    "destructive": "CRITICAL",
    "permission_change": "CRITICAL"
}

def get_timestamp():
    return datetime.utcnow().strftime("%Y%m%d-%H%M")

def get_sequence(category):
    """Get next sequence number for category"""
    action_log = AUTONOMY_DIR / "action_log.md"
    if not action_log.exists():
        return 1
    
    content = action_log.read_text()
    count = content.count(f"-{category}-")
    return count + 1

def generate_transaction_id(category):
    ts = get_timestamp()
    seq = get_sequence(category)
    return f"AUTONOMY-{ts}-{category}-{seq:03d}"

def categorize_action(action_description):
    """
    Analyze action description and return category.
    Returns (category, confidence, reasoning)
    """
    action_lower = action_description.lower()
    
    # Check exact patterns first
    for pattern, category in ACTION_PATTERNS.items():
        if pattern in action_lower:
            return category, 0.9, f"Matched pattern: {pattern}"
    
    # Check keywords
    critical_keywords = ["gateway", "external", "delete", "permission", "financial"]
    large_keywords = ["new system", "architecture", "security", "external"]
    medium_keywords = ["cron", "script", "config", "dependency"]
    small_keywords = ["kg", "memory", "learnings", "fix", "threshold"]
    
    if any(kw in action_lower for kw in critical_keywords):
        if any(kw in action_lower for kw in ["delete", "truncate", "drop"]):
            return "CRITICAL", 0.8, "Contains destructive keyword"
        return "LARGE", 0.7, "Contains large-change keyword"
    
    if any(kw in action_lower for kw in large_keywords):
        return "LARGE", 0.7, "Contains large-change keyword"
    
    if any(kw in action_lower for kw in medium_keywords):
        return "MEDIUM", 0.7, "Contains medium-change keyword"
    
    if any(kw in action_lower for kw in small_keywords):
        return "SMALL", 0.7, "Contains small-change keyword"
    
    # Default - ask for clarification
    return "UNKNOWN", 0.0, "Cannot categorize - needs manual review"

def needs_approval(category):
    return CATEGORIES.get(category, {}).get("approval", False)

def needs_backup(category):
    return CATEGORIES.get(category, {}).get("backup", False)

def needs_test(category):
    return CATEGORIES.get(category, {}).get("test", False)

def get_backup_type(category):
    return CATEGORIES.get(category, {}).get("backup_type", None)

def execute_backup(category, target_path=None):
    """Create backup based on category"""
    if not needs_backup(category):
        return None
    
    backup_type = get_backup_type(category)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    if backup_type == "copy":
        # Simple copy to backup dir
        if target_path:
            import shutil
            dest = BACKUP_DIR / f"{target_path.name}_{timestamp}"
            shutil.copy2(target_path, dest)
            return str(dest)
    
    elif backup_type == "git_snapshot":
        # Git commit as snapshot
        import subprocess
        try:
            subprocess.run(["git", "add", "-A"], cwd=WORKSPACE, capture_output=True)
            subprocess.run(["git", "commit", "-m", f"autonomy-backup-{timestamp}"], 
                         cwd=WORKSPACE, capture_output=True)
            return f"git-snapshot:{timestamp}"
        except Exception as e:
            return f"backup-failed:{e}"
    
    return None

def log_action(transaction_id, category, action, trigger, result, notes=""):
    """Log action to action_log.md"""
    action_log = AUTONOMY_DIR / "action_log.md"
    
    entry = f"""
### {transaction_id}
- **Timestamp:** {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC
- **Category:** {category}
- **Action:** {action}
- **Trigger:** {trigger}
- **Backup:** {'Yes' if needs_backup(category) else 'No'}
- **Result:** {result}
- **Actor:** PRIMARY
- **Notes:** {notes}
"""
    
    with open(action_log, "a") as f:
        f.write(entry)

def log_error(error_id, error_type, message, context, attempted_fix, result, related_action=None):
    """Log error to error_log.md"""
    error_log = AUTONOMY_DIR / "error_log.md"
    
    entry = f"""
### {error_id}
- **Timestamp:** {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC
- **Type:** {error_type}
- **Error Message:** {message}
- **Context:** {context}
- **Attempted Fix:** {attempted_fix}
- **Result:** {result}
- **Related Action:** {related_action or 'N/A'}
"""
    
    with open(error_log, "a") as f:
        f.write(entry)

def get_category_info(category):
    """Get requirements for category"""
    return CATEGORIES.get(category, {})

def should_auto_execute(category):
    """Check if action can auto-execute"""
    if category == "UNKNOWN":
        return False
    if needs_approval(category):
        return False
    return True

# CLI interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: decision_matrix.py <action_description>")
        print("\nCategories: TINY, SMALL, MEDIUM, LARGE, CRITICAL")
        sys.exit(1)
    
    action = " ".join(sys.argv[1:])
    category, confidence, reasoning = categorize_action(action)
    
    print(f"Action: {action}")
    print(f"Category: {category}")
    print(f"Confidence: {confidence}")
    print(f"Reasoning: {reasoning}")
    print(f"\nRequirements:")
    print(f"  Backup: {needs_backup(category)}")
    print(f"  Test: {needs_test(category)}")
    print(f"  Approval: {needs_approval(category)}")
    print(f"\nAuto-execute: {should_auto_execute(category)}")
    
    if not should_auto_execute(category) and category != "UNKNOWN":
        print(f"\n⚠️  Manual approval required for {category} actions")