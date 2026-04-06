#!/usr/bin/env python3
"""
Scheduler Agent - OpenClaw Productivity Suite
Schedules recurring tasks, reminders, and calendar events.
Reads/Writes: /home/clawbot/.openclaw/workspace/data/schedules/schedules.json
"""

import argparse
import json
import logging
import os
import shlex
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "schedules"
DATA_FILE = DATA_DIR / "schedules.json"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "scheduler.log"

LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("Scheduler")


def load_schedules() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        initial = {"schedules": [], "last_updated": datetime.utcnow().isoformat()}
        save_schedules(initial)
        return initial
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        log.error(f"Failed to load schedules: {e}")
        return {"schedules": [], "last_updated": datetime.utcnow().isoformat()}


def save_schedules(data: dict) -> None:
    data["last_updated"] = datetime.utcnow().isoformat()
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        log.error(f"Failed to save schedules: {e}")
        raise


def generate_id(schedules: list) -> int:
    return max((s.get("id", 0) for s in schedules), default=0) + 1


def parse_cron_field(field: str, max_val: int) -> list:
    """Parse a single cron field. Supports *, numbers, ranges, lists."""
    if field == "*":
        return list(range(0 if max_val > 59 else 1, max_val + 1))
    result = []
    for part in field.split(","):
        if "-" in part:
            start, end = part.split("-")
            result.extend(range(int(start), int(end) + 1))
        else:
            result.append(int(part))
    return sorted(set(result))


def get_next_run(cron_schedule: dict) -> datetime:
    """Calculate next run time from cron-like schedule."""
    now = datetime.utcnow()
    minute = parse_cron_field(cron_schedule.get("minute", "*"), 59)
    hour = parse_cron_field(cron_schedule.get("hour", "*"), 23)
    day_of_month = parse_cron_field(cron_schedule.get("day_of_month", "*"), 31)
    month = parse_cron_field(cron_schedule.get("month", "*"), 12)
    day_of_week = parse_cron_field(cron_schedule.get("day_of_week", "*"), 6)

    # Simple: find next matching slot (check next 366 days)
    for day_offset in range(367):
        candidate = now + timedelta(days=day_offset)
        if (candidate.month in month and
            candidate.day in day_of_month and
            candidate.weekday() in day_of_week and
            candidate.hour in hour and
            candidate.minute in minute):
            return candidate.replace(second=0, microsecond=0)
    return now + timedelta(days=1)


def cron_to_human(sched: dict) -> str:
    """Convert cron-like schedule to human readable."""
    minute = sched.get("minute", "*")
    hour = sched.get("hour", "*")
    dom = sched.get("day_of_month", "*")
    month = sched.get("month", "*")
    dow = sched.get("day_of_week", "*")

    if minute == "0" and hour == "0" and dom == "*" and dow == "*":
        return "Daily at midnight"
    if minute != "*" and hour != "*" and dom == "*" and dow == "*":
        return f"Daily at {hour.zfill(2)}:{minute.zfill(2)}"
    if dow != "*" and dom == "*":
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        sel = [days[int(d)] for d in parse_cron_field(dow, 6)]
        return f"Weekly on {', '.join(sel)} at {hour}:{minute}"
    if dom != "*":
        return f"Monthly on day {dom} at {hour}:{minute}"
    return f"Custom: min={minute}, hr={hour}, dom={dom}, mon={month}, dow={dow}"


def cmd_add(args) -> None:
    """Add a new scheduled task."""
    schedules_data = load_schedules()
    schedule = {
        "id": generate_id(schedules_data["schedules"]),
        "name": args.name,
        "description": args.description or "",
        "cron": {
            "minute": args.minute,
            "hour": args.hour,
            "day_of_month": args.day_of_month,
            "month": args.month,
            "day_of_week": args.day_of_week,
        },
        "command": args.command,
        "enabled": True,
        "created_at": datetime.utcnow().isoformat(),
        "last_run": None,
        "next_run": get_next_run({
            "minute": args.minute,
            "hour": args.hour,
            "day_of_month": args.day_of_month,
            "month": args.month,
            "day_of_week": args.day_of_week,
        }).isoformat(),
        "run_count": 0,
    }
    schedules_data["schedules"].append(schedule)
    save_schedules(schedules_data)
    log.info(f"Schedule added: #{schedule['id']} - {schedule['name']}")
    print(f"📅 Schedule #{schedule['id']} created: {schedule['name']}")
    print(f"   Next run: {schedule['next_run']}")


def cmd_list(args) -> None:
    """List all schedules."""
    schedules_data = load_schedules()
    schedules = schedules_data["schedules"]

    if args.enabled is not None:
        schedules = [s for s in schedules if s.get("enabled") == args.enabled]

    if not schedules:
        print("📅 No schedules found.")
        return

    print(f"\n📅 Schedules ({len(schedules)} found)\n{'─'*70}")
    for s in schedules:
        status = "🟢 active" if s.get("enabled") else "🔴 paused"
        next_run = s.get("next_run", "N/A")
        last_run = s.get("last_run", "Never")
        runs = s.get("run_count", 0)
        human = cron_to_human(s.get("cron", {}))
        print(f"  #{s['id']:3d} {status} | {s['name']}")
        print(f"      Schedule: {human}")
        print(f"      Command:  {s.get('command', 'N/A')[:60]}")
        print(f"      Next:     {next_run} | Last: {last_run} | Runs: {runs}")
    print()


def cmd_run(args) -> None:
    """Trigger a schedule to run now."""
    schedules_data = load_schedules()
    for s in schedules_data["schedules"]:
        if s["id"] == args.schedule_id:
            if not s.get("enabled"):
                print(f"⚠️  Schedule #{s['id']} is paused. Enable it first.")
                return
            cmd = s.get("command")
            if not cmd:
                print(f"❌ No command configured for schedule #{s['id']}")
                return
            print(f"▶️  Running: {s['name']}...")
            try:
                cmd_list = shlex.split(cmd)
                result = subprocess.run(cmd_list, capture_output=True, text=True, timeout=60)
                s["last_run"] = datetime.utcnow().isoformat()
                s["run_count"] = s.get("run_count", 0) + 1
                s["next_run"] = get_next_run(s["cron"]).isoformat()
                save_schedules(schedules_data)
                if result.returncode == 0:
                    log.info(f"Schedule #{s['id']} ran successfully")
                    print(f"✅ Schedule #{s['id']} completed successfully.")
                    if result.stdout:
                        print(f"   Output: {result.stdout[:200]}")
                else:
                    log.error(f"Schedule #{s['id']} failed: {result.stderr}")
                    print(f"❌ Schedule #{s['id']} failed: {result.stderr[:200]}")
            except subprocess.TimeoutExpired:
                log.error(f"Schedule #{s['id']} timed out")
                print(f"⏱️  Schedule #{s['id']} timed out.")
            except Exception as e:
                log.error(f"Schedule #{s['id']} error: {e}")
                print(f"❌ Error running schedule: {e}")
            return
    print(f"❌ Schedule #{args.schedule_id} not found.")


def cmd_enable(args) -> None:
    """Enable a schedule."""
    schedules_data = load_schedules()
    for s in schedules_data["schedules"]:
        if s["id"] == args.schedule_id:
            s["enabled"] = True
            s["next_run"] = get_next_run(s["cron"]).isoformat()
            save_schedules(schedules_data)
            log.info(f"Schedule #{args.schedule_id} enabled")
            print(f"🟢 Schedule #{args.schedule_id} enabled. Next run: {s['next_run']}")
            return
    print(f"❌ Schedule #{args.schedule_id} not found.")


def cmd_disable(args) -> None:
    """Disable a schedule."""
    schedules_data = load_schedules()
    for s in schedules_data["schedules"]:
        if s["id"] == args.schedule_id:
            s["enabled"] = False
            save_schedules(schedules_data)
            log.info(f"Schedule #{args.schedule_id} disabled")
            print(f"🔴 Schedule #{args.schedule_id} disabled.")
            return
    print(f"❌ Schedule #{args.schedule_id} not found.")


def cmd_delete(args) -> None:
    """Delete a schedule."""
    schedules_data = load_schedules()
    original = len(schedules_data["schedules"])
    schedules_data["schedules"] = [s for s in schedules_data["schedules"] if s["id"] != args.schedule_id]
    if len(schedules_data["schedules"]) < original:
        save_schedules(schedules_data)
        log.info(f"Schedule #{args.schedule_id} deleted")
        print(f"🗑️  Schedule #{args.schedule_id} deleted.")
    else:
        print(f"❌ Schedule #{args.schedule_id} not found.")


def cmd_due(args) -> None:
    """Show schedules due in next N hours."""
    schedules_data = load_schedules()
    now = datetime.utcnow()
    due_hours = args.hours
    cutoff = now + timedelta(hours=due_hours)
    due = []
    for s in schedules_data["schedules"]:
        if not s.get("enabled"):
            continue
        next_run = s.get("next_run")
        if next_run:
            try:
                next_dt = datetime.fromisoformat(next_run)
                if now <= next_dt <= cutoff:
                    due.append((s, next_dt))
            except ValueError:
                pass

    if not due:
        print(f"📅 No schedules due in the next {due_hours} hours.")
        return
    due.sort(key=lambda x: x[1])
    print(f"\n📅 Due in next {due_hours}h ({len(due)} found)\n{'─'*60}")
    for s, next_dt in due:
        print(f"  #{s['id']:3d} | {s['name']} | {next_dt} | {s.get('command','')[:50]}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="scheduler",
        description="📅 Scheduler Agent — manage recurring tasks and events",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  scheduler add "Daily Backup" --minute 0 --hour 3 --command "python3 /scripts/backup.py"
  scheduler add "Weekly Report" --minute 0 --hour 9 --day-of-week 1 --command "python3 report.py"
  scheduler list
  scheduler run 3
  scheduler enable 3
  scheduler disable 3
  scheduler due 24
  scheduler delete 2
        """,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Add a new schedule")
    p_add.add_argument("name", help="Schedule name")
    p_add.add_argument("-d", "--description", default="", help="Description")
    p_add.add_argument("--minute", default="*", help="Minute field (default: *)")
    p_add.add_argument("--hour", default="*", help="Hour field (default: *)")
    p_add.add_argument("--day-of-month", dest="day_of_month", default="*", help="Day of month field")
    p_add.add_argument("--month", default="*", help="Month field")
    p_add.add_argument("--day-of-week", dest="day_of_week", default="*", help="Day of week (0=Mon..6=Sun)")
    p_add.add_argument("-c", "--command", required=True, help="Command to execute")

    p_list = sub.add_parser("list", help="List all schedules")
    p_list.add_argument("--enabled", type=lambda x: x.lower() == "true", choices=[True, False], help="Filter by enabled status")

    p_run = sub.add_parser("run", help="Run a schedule now")
    p_run.add_argument("schedule_id", type=int, help="Schedule ID to run")

    p_enable = sub.add_parser("enable", help="Enable a schedule")
    p_enable.add_argument("schedule_id", type=int, help="Schedule ID to enable")

    p_disable = sub.add_parser("disable", help="Disable a schedule")
    p_disable.add_argument("schedule_id", type=int, help="Schedule ID to disable")

    p_del = sub.add_parser("delete", help="Delete a schedule")
    p_del.add_argument("schedule_id", type=int, help="Schedule ID to delete")

    p_due = sub.add_parser("due", help="Show schedules due soon")
    p_due.add_argument("hours", type=int, nargs="?", default=24, help="Hours to look ahead (default: 24)")

    args = parser.parse_args()
    try:
        if args.command == "add":
            cmd_add(args)
        elif args.command == "list":
            cmd_list(args)
        elif args.command == "run":
            cmd_run(args)
        elif args.command == "enable":
            cmd_enable(args)
        elif args.command == "disable":
            cmd_disable(args)
        elif args.command == "delete":
            cmd_delete(args)
        elif args.command == "due":
            cmd_due(args)
    except Exception as e:
        log.error(f"Command '{args.command}' failed: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
