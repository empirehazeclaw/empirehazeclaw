#!/usr/bin/env python3
"""GitHub Auto - Create issues automatically"""
import subprocess
import json
import sys

REPO = "empirehazeclaw/empirehazeclaw"  # Adjust as needed

def gh(command):
    """Run gh CLI command"""
    result = subprocess.run(command.split(), capture_output=True, text=True)
    return result.stdout.strip(), result.returncode

def create_issue(title, body, labels=None):
    """Create GitHub issue"""
    cmd = f'gh issue create --title "{title}" --body "{body}"'
    if labels:
        cmd += f' --label {labels}'
    
    out, code = gh(cmd)
    if code == 0:
        return f"✅ Created: {out}"
    return f"❌ Error: {out}"

def list_issues(state="open"):
    """List issues"""
    out, code = gh(f'gh issue list --state {state}')
    return out

# Test
if __name__ == "__main__":
    print("=== 🐙 GH AUTO TEST ===")
    print(create_issue("Test Issue", "Created by AI", "bug"))
