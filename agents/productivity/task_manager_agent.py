#!/usr/bin/env python3
"""
Task Manager Agent - OpenClaw Productivity Suite
Manages tasks with priorities, deadlines, and status tracking.
Reads/Writes: /home/clawbot/.openclaw/workspace/data/tasks/tasks.json
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "tasks"
DATA_FILE = DATA_DIR / "tasks.json"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "task_manager.log"

# ─── Logging ──────────────────────────────────────────────────────────────────
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("TaskManager")


# ─── Data Access ───────────────────────────────────────────────────────────────
def load_tasks() -> dict:
    """Load tasks from JSON file, create if not exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        initial = {"tasks": [], "last_updated": datetime.utcnow().isoformat()}
        save_tasks(initial)
        return initial
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        log.error(f"Failed to load tasks: {e}")
        return {"tasks": [], "last_updated": datetime.utcnow().isoformat()}


def save_tasks(data: dict) -> None:
    """Save tasks to JSON file."""
    data["last_updated"] = datetime.utcnow().isoformat()
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        log.error(f"Failed to save tasks: {e}")
        raise


def generate_id(tasks: list) -> int:
    """Generate next task ID."""
    return max((t.get("id", 0) for t in tasks), default=0) + 1


# ─── Commands ─────────────────────────────────────────────────────────────────
def cmd_add(args) -> None:
    """Add a new task."""
    tasks_data = load_tasks()
    task = {
        "id": generate_id(tasks_data["tasks"]),
        "title": args.title,
        "description": args.description or "",
        "priority": args.priority,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "due_date": args.due_date,
        "tags": args.tags.split(",") if args.tags else [],
    }
    tasks_data["tasks"].append(task)
    save_tasks(tasks_data)
    log.info(f"Task added: #{task['id']} - {task['title']}")
    print(f"✅ Task #{task['id']} created: {task['title']} (priority: {task['priority']})")


def cmd_list(args) -> None:
    """List tasks with optional filters."""
    tasks_data = load_tasks()
    tasks = tasks_data["tasks"]

    # Apply filters
    if args.status:
        tasks = [t for t in tasks if t.get("status") == args.status]
    if args.priority:
        tasks = [t for t in tasks if t.get("priority") == args.priority]
    if args.tag:
        tasks = [t for t in tasks if args.tag in t.get("tags", [])]

    # Sort: pending first, then by priority weight, then by id
    priority_order = {"high": 0, "medium": 1, "low": 2}
    tasks.sort(key=lambda t: (t.get("status") != "pending", priority_order.get(t.get("priority", "medium"), 1), t.get("id", 0)))

    if not tasks:
        print("📋 No tasks found matching filters.")
        return

    print(f"\n📋 Tasks ({len(tasks)} found)\n{'─'*60}")
    for t in tasks:
        due = f" | Due: {t['due_date']}" if t.get("due_date") else ""
        tags = f" | Tags: {', '.join(t['tags'])}" if t.get("tags") else ""
        status_icon = {"pending": "⏳", "in_progress": "🔄", "done": "✅"}.get(t.get("status"), "📌")
        print(f"  {status_icon} #{t['id']:3d} [{t['priority'].upper():5s}] {t['title']}{due}{tags}")
        if t.get("description"):
            print(f"         └─ {t['description'][:60]}")
    print()


def cmd_done(args) -> None:
    """Mark task as done."""
    tasks_data = load_tasks()
    for t in tasks_data["tasks"]:
        if t["id"] == args.task_id:
            t["status"] = "done"
            t["completed_at"] = datetime.utcnow().isoformat()
            save_tasks(tasks_data)
            log.info(f"Task #{args.task_id} marked as done")
            print(f"✅ Task #{args.task_id} marked as done!")
            return
    print(f"❌ Task #{args.task_id} not found.")


def cmd_delete(args) -> None:
    """Delete a task."""
    tasks_data = load_tasks()
    original = len(tasks_data["tasks"])
    tasks_data["tasks"] = [t for t in tasks_data["tasks"] if t["id"] != args.task_id]
    if len(tasks_data["tasks"]) < original:
        save_tasks(tasks_data)
        log.info(f"Task #{args.task_id} deleted")
        print(f"🗑️  Task #{args.task_id} deleted.")
    else:
        print(f"❌ Task #{args.task_id} not found.")


def cmd_stats(args) -> None:
    """Show task statistics."""
    tasks_data = load_tasks()
    tasks = tasks_data["tasks"]
    total = len(tasks)
    pending = sum(1 for t in tasks if t.get("status") == "pending")
    in_progress = sum(1 for t in tasks if t.get("status") == "in_progress")
    done = sum(1 for t in tasks if t.get("status") == "done")
    high = sum(1 for t in tasks if t.get("priority") == "high" and t.get("status") != "done")
    print(f"\n📊 Task Statistics\n{'─'*40}")
    print(f"  Total:    {total}")
    print(f"  Pending:  {pending} ⏳")
    print(f"  Active:   {in_progress} 🔄")
    print(f"  Done:     {done} ✅")
    print(f"  High Pri: {high} 🔥")
    print()


def cmd_update(args) -> None:
    """Update task fields."""
    tasks_data = load_tasks()
    for t in tasks_data["tasks"]:
        if t["id"] == args.task_id:
            if args.title:
                t["title"] = args.title
            if args.description is not None:
                t["description"] = args.description
            if args.priority:
                t["priority"] = args.priority
            if args.status:
                t["status"] = args.status
            if args.due_date:
                t["due_date"] = args.due_date
            save_tasks(tasks_data)
            log.info(f"Task #{args.task_id} updated")
            print(f"✏️  Task #{args.task_id} updated!")
            return
    print(f"❌ Task #{args.task_id} not found.")


# ─── CLI ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        prog="task-manager",
        description="🗂️  Task Manager Agent — manage tasks with priorities and deadlines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  task-manager add "Write report" -p high --due 2026-03-30 --tags work,urgent
  task-manager list --status pending
  task-manager list --priority high
  task-manager done 5
  task-manager delete 3
  task-manager stats
  task-manager update 5 --status in_progress
        """,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # add
    p_add = sub.add_parser("add", help="Add a new task")
    p_add.add_argument("title", help="Task title")
    p_add.add_argument("-d", "--description", default="", help="Task description")
    p_add.add_argument("-p", "--priority", choices=["high", "medium", "low"], default="medium", help="Priority level")
    p_add.add_argument("--due", dest="due_date", default=None, help="Due date (YYYY-MM-DD)")
    p_add.add_argument("--tags", default="", help="Comma-separated tags")

    # list
    p_list = sub.add_parser("list", help="List tasks")
    p_list.add_argument("--status", choices=["pending", "in_progress", "done"], help="Filter by status")
    p_list.add_argument("--priority", choices=["high", "medium", "low"], help="Filter by priority")
    p_list.add_argument("--tag", help="Filter by tag")

    # done
    p_done = sub.add_parser("done", help="Mark task as done")
    p_done.add_argument("task_id", type=int, help="Task ID to complete")

    # delete
    p_del = sub.add_parser("delete", help="Delete a task")
    p_del.add_argument("task_id", type=int, help="Task ID to delete")

    # stats
    sub.add_parser("stats", help="Show task statistics")

    # update
    p_upd = sub.add_parser("update", help="Update a task")
    p_upd.add_argument("task_id", type=int, help="Task ID to update")
    p_upd.add_argument("--title", help="New title")
    p_upd.add_argument("--description", help="New description")
    p_upd.add_argument("--priority", choices=["high", "medium", "low"], help="New priority")
    p_upd.add_argument("--status", choices=["pending", "in_progress", "done"], help="New status")
    p_upd.add_argument("--due", dest="due_date", help="New due date (YYYY-MM-DD)")

    args = parser.parse_args()

    try:
        if args.command == "add":
            cmd_add(args)
        elif args.command == "list":
            cmd_list(args)
        elif args.command == "done":
            cmd_done(args)
        elif args.command == "delete":
            cmd_delete(args)
        elif args.command == "stats":
            cmd_stats(args)
        elif args.command == "update":
            cmd_update(args)
    except Exception as e:
        log.error(f"Command '{args.command}' failed: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
