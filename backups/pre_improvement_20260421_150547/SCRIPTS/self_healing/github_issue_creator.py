#!/usr/bin/env python3
"""
github_issue_creator.py - GitHub Issue Creator for System Failures
Sir HazeClaw - 2026-04-12

Erstellt GitHub Issues wenn Crons dauerhaft fehlen.
Kann von cron_error_healer aufgerufen werden.

Usage:
    python3 github_issue_creator.py --create --title "Cron failed" --body "..."
    python3 github_issue_creator.py --list    # List recent issues
    python3 github_issue_creator.py --test    # Test API connection
"""

import json
import argparse
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

# Paths
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
STATE_FILE = WORKSPACE / "memory" / "github_issue_state.json"
CONFIG_FILE = Path("/home/clawbot/.openclaw/openclaw.json")

# GitHub config
GITHUB_REPO = "empirehazeclaw/empirehazeclaw"  # Default
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}/issues"

# Cooldown to prevent spam (seconds)
ISSUE_COOLDOWN = 21600  # 6 hours

def load_state() -> Dict:
    """Lädt Issue State."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"created_issues": [], "cooldowns": {}}

def save_state(state: Dict):
    """Speichert Issue State."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_github_token() -> Optional[str]:
    """Holt GitHub Token aus Secrets."""
    secrets_file = WORKSPACE / "secrets.env"
    if secrets_file.exists():
        with open(secrets_file) as f:
            for line in f:
                if line.startswith("GITHUB_TOKEN="):
                    return line.split("=", 1)[1].strip()
    
    # Fallback: Check environment
    import os
    return os.environ.get("GITHUB_TOKEN")

def check_cooldown(issue_key: str, state: Dict) -> bool:
    """Prüft ob Issue cooldown aktiv ist."""
    cooldowns = state.get("cooldowns", {})
    last_issue = cooldowns.get(issue_key)
    
    if not last_issue:
        return False
    
    last_time = datetime.fromisoformat(last_issue)
    elapsed = (datetime.now() - last_time).total_seconds()
    
    if elapsed < ISSUE_COOLDOWN:
        remaining = int((ISSUE_COOLDOWN - elapsed) / 3600)
        print(f"⏳ Cooldown active for '{issue_key}': {remaining}h remaining")
        return True
    
    return False

def create_issue(title: str, body: str, labels: List[str] = None, issue_key: str = None) -> Optional[str]:
    """Erstellt ein GitHub Issue."""
    if issue_key and check_cooldown(issue_key, load_state()):
        return None
    
    token = get_github_token()
    if not token:
        print("❌ No GitHub token found")
        return None
    
    import urllib.request
    import urllib.error
    
    url = GITHUB_API
    data = {
        "title": title,
        "body": body,
        "labels": labels or ["automated", "bug"]
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode(),
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.load(resp)
            issue_url = result.get("html_url")
            issue_number = result.get("number")
            
            # Update state
            state = load_state()
            state["created_issues"].append({
                "key": issue_key or title[:50],
                "number": issue_number,
                "url": issue_url,
                "created": datetime.now().isoformat(),
                "title": title
            })
            state["created_issues"] = state["created_issues"][-50:]  # Keep last 50
            
            if issue_key:
                state["cooldowns"][issue_key] = datetime.now().isoformat()
            
            save_state(state)
            
            print(f"✅ Issue created: #{issue_number}")
            print(f"   {issue_url}")
            
            return issue_url
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"❌ HTTP Error {e.code}: {error_body}")
        return None
    except Exception as e:
        print(f"❌ Error creating issue: {e}")
        return None

def create_cron_failure_issue(cron_name: str, cron_id: str, error: str, consecutive: int) -> Optional[str]:
    """Erstellt ein Issue für Cron Failure."""
    title = f"🔴 Cron Failure: {cron_name}"
    
    body = f"""## Cron Failure Detected

**Cron:** {cron_name}
**ID:** `{cron_id}`
**Consecutive Errors:** {consecutive}

### Last Error
```
{error[:500]}
```

### Action Required
1. Check cron logs
2. Fix underlying issue
3. Re-enable cron after fix

---
*Auto-created by Sir HazeClaw - {datetime.now().isoformat()} UTC*
"""
    
    labels = ["automated", "cron-failure", "needs-attention"]
    issue_key = f"cron_{cron_id}"
    
    return create_issue(title, body, labels, issue_key)

def list_recent_issues():
    """Listet kürzlich erstellte Issues."""
    state = load_state()
    
    print("\n📋 RECENT GITHUB ISSUES")
    print("=" * 60)
    print(f"Repository: {GITHUB_REPO}")
    print(f"Total created: {len(state.get('created_issues', []))}")
    print()
    
    issues = state.get("created_issues", [])
    if not issues:
        print("No issues created yet.")
        return
    
    for issue in issues[-10:]:
        created = issue.get("created", "")[:19]
        number = issue.get("number", "?")
        title = issue.get("title", "")[:50]
        print(f"#{number:<6} {created}  {title}")

def test_connection():
    """Testet GitHub API Verbindung."""
    token = get_github_token()
    if not token:
        print("❌ No GitHub token found")
        return False
    
    import urllib.request
    
    url = f"https://api.github.com/repos/{GITHUB_REPO}"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"token {token}"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.load(resp)
            print(f"✅ Connected to GitHub")
            print(f"   Repo: {result.get('full_name')}")
            print(f"   Stars: {result.get('stargazers_count')}")
            return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="GitHub Issue Creator")
    parser.add_argument("--create", action="store_true", help="Create issue")
    parser.add_argument("--title", help="Issue title")
    parser.add_argument("--body", help="Issue body")
    parser.add_argument("--labels", nargs="*", help="Labels")
    parser.add_argument("--key", help="Issue key for cooldown tracking")
    parser.add_argument("--list", action="store_true", help="List recent issues")
    parser.add_argument("--test", action="store_true", help="Test connection")
    parser.add_argument("--cron", nargs=4, metavar=("NAME", "ID", "ERROR", "COUNT"),
                        help="Create cron failure issue")
    
    args = parser.parse_args()
    
    if args.test:
        test_connection()
    elif args.list:
        list_recent_issues()
    elif args.create:
        if not args.title:
            print("❌ --title required for --create")
            sys.exit(1)
        url = create_issue(
            args.title,
            args.body or "",
            args.labels,
            args.key
        )
        if url:
            print(f"Issue: {url}")
    elif args.cron:
        name, id_, error, count = args.cron
        url = create_cron_failure_issue(name, id_, error, int(count))
        if url:
            print(f"Issue: {url}")
    else:
        parser.print_help()

if __name__ == "__main__":
    sys.exit(main())
