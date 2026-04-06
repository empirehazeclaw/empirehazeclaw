#!/usr/bin/env python3
"""
Bug Hunter Agent - OpenClaw Development Suite
Tracks, prioritizes, and investigates bugs in projects.
Reads/Writes: /home/clawbot/.openclaw/workspace/data/bugs/bugs.json
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "bugs"
DATA_FILE = DATA_DIR / "bugs.json"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "bug_hunter.log"

LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("BugHunter")


def load_bugs() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        initial = {"bugs": [], "last_updated": datetime.utcnow().isoformat()}
        save_bugs(initial)
        return initial
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        log.error(f"Failed to load bugs: {e}")
        return {"bugs": [], "last_updated": datetime.utcnow().isoformat()}


def save_bugs(data: dict) -> None:
    data["last_updated"] = datetime.utcnow().isoformat()
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        log.error(f"Failed to save bugs: {e}")
        raise


def generate_id(bugs: list) -> int:
    return max((b.get("id", 0) for b in bugs), default=0) + 1


def severity_score(severity: str) -> int:
    scores = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    return scores.get(severity, 4)


def age_days(created: str) -> int:
    try:
        return (datetime.utcnow() - datetime.fromisoformat(created)).days
    except ValueError:
        return 0


def cmd_add(args) -> None:
    """Report a new bug."""
    bugs_data = load_bugs()
    bug = {
        "id": generate_id(bugs_data["bugs"]),
        "title": args.title,
        "description": args.description or "",
        "severity": args.severity,
        "status": "open",
        "project": args.project or "general",
        "steps_to_reproduce": args.steps or "",
        "expected": args.expected or "",
        "actual": args.actual or "",
        "error_log": args.error_log or "",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "resolved_at": None,
        "assigned_to": args.assignee or "",
        "tags": args.tags.split(",") if args.tags else [],
    }
    bugs_data["bugs"].append(bug)
    save_bugs(bugs_data)
    log.info(f"Bug reported: #{bug['id']} - {bug['title']}")
    print(f"🐛 Bug #{bug['id']} reported: {bug['title']}")
    print(f"   Severity: {bug['severity'].upper()} | Project: {bug['project']}")


def cmd_list(args) -> None:
    """List bugs with filters."""
    bugs_data = load_bugs()
    bugs = bugs_data["bugs"]

    if args.status:
        bugs = [b for b in bugs if b.get("status") == args.status]
    if args.severity:
        bugs = [b for b in bugs if b.get("severity") == args.severity]
    if args.project:
        bugs = [b for b in bugs if b.get("project") == args.project]
    if args.tag:
        bugs = [b for b in bugs if args.tag in b.get("tags", [])]

    # Sort: open first, then by severity, then by age
    bugs.sort(key=lambda b: (b.get("status") != "open", severity_score(b.get("severity", "medium")), age_days(b.get("created_at", ""))))

    if not bugs:
        print("🐛 No bugs found matching filters.")
        return

    print(f"\n🐛 Bugs ({len(bugs)} found)\n{'─'*70}")
    for b in bugs:
        sev = b.get("severity", "medium").upper()
        sev_icon = {"CRITICAL": "💥", "HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(sev, "⚪")
        status_icon = {"open": "📬", "investigating": "🔍", "fixing": "🔧", "resolved": "✅", "wontfix": "🚫"}.get(b.get("status"), "❓")
        age = age_days(b.get("created_at", ""))
        age_str = f"{age}d ago" if age < 30 else f"{age//30}mo ago"
        print(f"  {sev_icon} #{b['id']:4d} {status_icon} {sev:8s} | {b['title'][:40]}")
        print(f"           Project: {b.get('project')} | Age: {age_str} | Status: {b.get('status')}")
    print()


def cmd_show(args) -> None:
    """Show detailed bug info."""
    bugs_data = load_bugs()
    for b in bugs_data["bugs"]:
        if b["id"] == args.bug_id:
            print(f"\n{'─'*60}")
            print(f"  🐛 Bug #{b['id']}: {b['title']}")
            print(f"{'─'*60}")
            print(f"  Severity:   {b.get('severity', 'N/A').upper()}")
            print(f"  Status:     {b.get('status')}")
            print(f"  Project:    {b.get('project')}")
            print(f"  Assigned:   {b.get('assigned_to') or 'Unassigned'}")
            print(f"  Created:    {b.get('created_at')}")
            print(f"  Updated:    {b.get('updated_at')}")
            print(f"  Tags:       {', '.join(b.get('tags', [])) or 'None'}")
            if b.get("description"):
                print(f"\n  Description:\n    {b['description']}")
            if b.get("steps_to_reproduce"):
                print(f"\n  Steps to Reproduce:\n    {b['steps_to_reproduce']}")
            if b.get("expected"):
                print(f"  Expected:    {b['expected']}")
            if b.get("actual"):
                print(f"  Actual:      {b['actual']}")
            if b.get("error_log"):
                print(f"  Error Log:\n    {b['error_log'][:300]}")
            print()
            return
    print(f"❌ Bug #{args.bug_id} not found.")


def cmd_update(args) -> None:
    """Update bug fields."""
    bugs_data = load_bugs()
    for b in bugs_data["bugs"]:
        if b["id"] == args.bug_id:
            if args.status:
                b["status"] = args.status
                if args.status == "resolved":
                    b["resolved_at"] = datetime.utcnow().isoformat()
            if args.severity:
                b["severity"] = args.severity
            if args.assignee is not None:
                b["assigned_to"] = args.assignee
            if args.title:
                b["title"] = args.title
            if args.description is not None:
                b["description"] = args.description
            b["updated_at"] = datetime.utcnow().isoformat()
            save_bugs(bugs_data)
            log.info(f"Bug #{args.bug_id} updated to status={b['status']}")
            print(f"✏️  Bug #{args.bug_id} updated: status={b['status']}, severity={b['severity']}")
            return
    print(f"❌ Bug #{args.bug_id} not found.")


def cmd_stats(args) -> None:
    """Show bug statistics."""
    bugs_data = load_bugs()
    bugs = bugs_data["bugs"]
    total = len(bugs)
    open_bugs = [b for b in bugs if b.get("status") == "open"]
    investigating = sum(1 for b in bugs if b.get("status") == "investigating")
    fixing = sum(1 for b in bugs if b.get("status") == "fixing")
    resolved = sum(1 for b in bugs if b.get("status") == "resolved")
    critical = sum(1 for b in bugs if b.get("severity") == "critical" and b.get("status") != "resolved")
    high = sum(1 for b in bugs if b.get("severity") == "high" and b.get("status") != "resolved")
    projects = set(b.get("project") for b in bugs)
    avg_age = sum(age_days(b.get("created_at", "")) for b in open_bugs) / max(len(open_bugs), 1)

    print(f"\n📊 Bug Statistics\n{'─'*40}")
    print(f"  Total Bugs:     {total}")
    print(f"  Open:           {len(open_bugs)} 🐛")
    print(f"  Investigating:  {investigating} 🔍")
    print(f"  Fixing:         {fixing} 🔧")
    print(f"  Resolved:       {resolved} ✅")
    print(f"  Critical Open:  {critical} 💥")
    print(f"  High Open:      {high} 🔴")
    print(f"  Projects:        {len(projects)}")
    print(f"  Avg Open Age:   {avg_age:.1f} days")
    print()


def cmd_stale(args) -> None:
    """Show stale bugs not updated in N days."""
    bugs_data = load_bugs()
    days = args.days
    cutoff = datetime.utcnow() - timedelta(days=days)
    stale = []
    for b in bugs_data["bugs"]:
        if b.get("status") in ("resolved", "wontfix"):
            continue
        try:
            updated = datetime.fromisoformat(b.get("updated_at", b.get("created_at", "")))
            if updated < cutoff:
                stale.append((b, (datetime.utcnow() - updated).days))
        except ValueError:
            pass

    if not stale:
        print(f"✅ No bugs stale for more than {days} days.")
        return
    stale.sort(key=lambda x: x[1], reverse=True)
    print(f"\n🕐 Stale Bugs (> {days} days since update, {len(stale)} found)\n{'─'*70}")
    for b, days_stale in stale:
        print(f"  #{b['id']:4d} | {b['title'][:45]} | {b.get('severity').upper():8s} | {days_stale}d stale | {b.get('status')}")
    print()


def cmd_delete(args) -> None:
    """Delete a bug."""
    bugs_data = load_bugs()
    original = len(bugs_data["bugs"])
    bugs_data["bugs"] = [b for b in bugs_data["bugs"] if b["id"] != args.bug_id]
    if len(bugs_data["bugs"]) < original:
        save_bugs(bugs_data)
        log.info(f"Bug #{args.bug_id} deleted")
        print(f"🗑️  Bug #{args.bug_id} deleted.")
    else:
        print(f"❌ Bug #{args.bug_id} not found.")


def main():
    parser = argparse.ArgumentParser(
        prog="bug-hunter",
        description="🐛 Bug Hunter Agent — track, prioritize, and investigate bugs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  bug-hunter add "Login fails on Safari" -s high --project web --steps "Open site, click login"
  bug-hunter list --status open --severity high
  bug-hunter list --project api
  bug-hunter show 5
  bug-hunter update 5 --status investigating --assignee alice
  bug-hunter update 5 --status resolved
  bug-hunter stats
  bug-hunter stale 14
  bug-hunter delete 3
        """,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Report a new bug")
    p_add.add_argument("title", help="Bug title/description")
    p_add.add_argument("-s", "--severity", choices=["critical", "high", "medium", "low"], default="medium")
    p_add.add_argument("-d", "--description", default="", help="Detailed description")
    p_add.add_argument("-p", "--project", default="general", help="Project name")
    p_add.add_argument("--steps", default="", help="Steps to reproduce")
    p_add.add_argument("--expected", default="", help="Expected behavior")
    p_add.add_argument("--actual", default="", help="Actual behavior")
    p_add.add_argument("--error-log", dest="error_log", default="", help="Error log excerpt")
    p_add.add_argument("-a", "--assignee", default="", help="Assign to")
    p_add.add_argument("--tags", default="", help="Comma-separated tags")

    p_list = sub.add_parser("list", help="List bugs")
    p_list.add_argument("--status", choices=["open", "investigating", "fixing", "resolved", "wontfix"])
    p_list.add_argument("--severity", choices=["critical", "high", "medium", "low"])
    p_list.add_argument("--project", help="Filter by project name")
    p_list.add_argument("--tag", help="Filter by tag")

    p_show = sub.add_parser("show", help="Show bug details")
    p_show.add_argument("bug_id", type=int, help="Bug ID")

    p_upd = sub.add_parser("update", help="Update a bug")
    p_upd.add_argument("bug_id", type=int, help="Bug ID")
    p_upd.add_argument("--status", choices=["open", "investigating", "fixing", "resolved", "wontfix"])
    p_upd.add_argument("--severity", choices=["critical", "high", "medium", "low"])
    p_upd.add_argument("--title", help="New title")
    p_upd.add_argument("--description", help="New description")
    p_upd.add_argument("-a", "--assignee", default=None, help="Assign to (empty to clear)")

    p_stats = sub.add_parser("stats", help="Show bug statistics")
    p_stats.add_argument("--days", type=int, default=30, help="Days for age calculation")

    p_stale = sub.add_parser("stale", help="Show stale bugs")
    p_stale.add_argument("days", type=int, nargs="?", default=14, help="Days threshold")

    p_del = sub.add_parser("delete", help="Delete a bug")
    p_del.add_argument("bug_id", type=int, help="Bug ID")

    args = parser.parse_args()
    try:
        if args.command == "add":
            cmd_add(args)
        elif args.command == "list":
            cmd_list(args)
        elif args.command == "show":
            cmd_show(args)
        elif args.command == "update":
            cmd_update(args)
        elif args.command == "stats":
            cmd_stats(args)
        elif args.command == "stale":
            cmd_stale(args)
        elif args.command == "delete":
            cmd_delete(args)
    except Exception as e:
        log.error(f"Command '{args.command}' failed: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
