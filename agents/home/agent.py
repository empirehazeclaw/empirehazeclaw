#!/usr/bin/env python3
"""
Home Agent
Home automation, appliance maintenance, household tasks.
"""
import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("openclaw.home")

DATA_DIR = Path.home() / ".openclaw" / "workspace" / "data" / "home"
DATA_DIR.mkdir(parents=True, exist_ok=True)

APPLIANCES_FILE = DATA_DIR / "appliances.json"
AUTOMATIONS_FILE = DATA_DIR / "automations.json"
TASKS_FILE = DATA_DIR / "tasks.json"


def load_json(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception as e:
            log.warning("Failed to load %s: %s", path, e)
    return default


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, default=str))


@dataclass
class Appliance:
    name: str
    category: str  # kitchen, hvac, plumbing, electrical, cleaning, entertainment, other
    brand: str = ""
    model: str = ""
    purchase_date: str = ""
    warranty_months: int = 0
    last_maintenance: str = ""
    maintenance_interval_days: int = 90
    location: str = ""
    notes: str = ""


@dataclass
class Automation:
    name: str
    trigger: str  # time, sensor, manual
    action: str
    schedule: str = ""  # cron-like: "08:00", "Mon 08:00"
    enabled: bool = True
    notes: str = ""


class HomeAgent:
    def __init__(self):
        self.appliances = load_json(APPLIANCES_FILE, {})
        self.automations = load_json(AUTOMATIONS_FILE, [])
        self.tasks = load_json(TASKS_FILE, [])

    # ── Appliance Management ──────────────────────────────────

    def add_appliance(self, name: str, category: str, **kwargs):
        app = Appliance(name=name, category=category.lower(), **kwargs)
        self.appliances[name] = vars(app)
        save_json(APPLIANCES_FILE, self.appliances)
        log.info("Added appliance: %s (%s)", name, category)
        return f"🏠 Appliance '{name}' added."

    def list_appliances(self, category: str = ""):
        filtered = self.appliances
        if category:
            filtered = {k: v for k, v in self.appliances.items() if v['category'] == category.lower()}
        if not filtered:
            return "No appliances found."
        cats = {"kitchen": "🍳", "hvac": "🌡️", "plumbing": "🚿", "electrical": "⚡",
                "cleaning": "🧹", "entertainment": "📺", "other": "🏠"}
        lines = ["🏠 Appliances:", ""]
        for name, data in filtered.items():
            icon = cats.get(data['category'], "🏠")
            lines.append(f"  {icon} {name} — {data['brand']} {data['model']} | {data['location']}")
            if data.get('last_maintenance'):
                lines.append(f"     Last maintenance: {data['last_maintenance']}")
        return "\n".join(lines)

    def maintenance_due(self):
        today = datetime.now()
        lines = ["🔧 Maintenance Due:", ""]
        due_count = 0
        for name, data in self.appliances.items():
            if data.get('last_maintenance'):
                try:
                    last = datetime.strptime(data['last_maintenance'], "%Y-%m-%d")
                    interval = data.get('maintenance_interval_days', 90)
                    if (today - last).days >= interval:
                        lines.append(f"  ⚠️  {name} — last: {data['last_maintenance']} ({int((today-last).days)} days ago)")
                        due_count += 1
                except ValueError:
                    pass
        if due_count == 0:
            lines.append("  ✅ All appliances up to date.")
        return "\n".join(lines)

    # ── Automations ────────────────────────────────────────────

    def add_automation(self, name: str, trigger: str, action: str, **kwargs):
        auto = Automation(name=name, trigger=trigger.lower(), action=action, **kwargs)
        self.automations.append(vars(auto))
        save_json(AUTOMATIONS_FILE, self.automations)
        log.info("Added automation: %s", name)
        return f"⚡ Automation '{name}' added."

    def list_automations(self):
        if not self.automations:
            return "No automations configured."
        lines = ["⚡ Automations:", ""]
        for a in self.automations:
            status = "🟢" if a['enabled'] else "🔴"
            lines.append(f"  {status} {a['name']} | trigger: {a['trigger']} | action: {a['action']}")
            if a.get('schedule'):
                lines.append(f"      Schedule: {a['schedule']}")
        return "\n".join(lines)

    def toggle_automation(self, name: str):
        for a in self.automations:
            if a['name'] == name:
                a['enabled'] = not a['enabled']
                save_json(AUTOMATIONS_FILE, self.automations)
                status = "enabled" if a['enabled'] else "disabled"
                log.info("Automation %s %s", name, status)
                return f"⚡ Automation '{name}' {status}."
        return f"❌ Automation '{name}' not found."

    # ── Household Tasks ────────────────────────────────────────

    def add_task(self, title: str, due_date: str = "", priority: str = "medium", notes: str = ""):
        task = {
            "title": title, "due_date": due_date, "priority": priority,
            "notes": notes, "status": "pending",
            "created": datetime.now().strftime("%Y-%m-%d")
        }
        self.tasks.append(task)
        save_json(TASKS_FILE, self.tasks)
        log.info("Added task: %s", title)
        return f"📋 Task '{title}' added."

    def list_tasks(self, status: str = ""):
        tasks = self.tasks
        if status:
            tasks = [t for t in self.tasks if t.get('status') == status]
        if not tasks:
            return "No tasks found."
        prio_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        lines = ["📋 Household Tasks:", ""]
        for t in tasks:
            icon = prio_icon.get(t.get('priority', 'medium'), "🟡")
            done = "✅" if t.get('status') == 'done' else "⬜"
            lines.append(f"  {done} {icon} {t['title']} | due: {t.get('due_date', 'none')}")
        return "\n".join(lines)

    # ── Report ─────────────────────────────────────────────────

    def report(self) -> str:
        lines = ["🏠 Home Agent Report — " + datetime.now().strftime("%Y-%m-%d %H:%M"), ""]
        lines.append(f"📊 {len(self.appliances)} appliances, {len(self.automations)} automations, {len(self.tasks)} tasks\n")
        lines.append(self.maintenance_due() + "\n")
        lines.append(self.list_automations())
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        prog="home-agent",
        description="🏠 Home Agent — appliance maintenance, automations, household tasks"
    )
    sub = parser.add_subparsers(dest="cmd")

    p = sub.add_parser("add-appliance", help="Register an appliance")
    p.add_argument("--name", required=True, help="Appliance name")
    p.add_argument("--category", required=True, help="kitchen, hvac, plumbing, electrical, cleaning, entertainment")
    p.add_argument("--brand", default="", help="Brand")
    p.add_argument("--model", default="", help="Model")
    p.add_argument("--location", default="", help="Location in home")
    p.add_argument("--purchase-date", default="", help="Purchase date (YYYY-MM-DD)")
    p.add_argument("--warranty-months", type=int, default=0, help="Warranty in months")
    p.add_argument("--maintenance-interval-days", type=int, default=90, help="Days between maintenance")
    p.add_argument("--last-maintenance", default="", help="Last maintenance date (YYYY-MM-DD)")

    p = sub.add_parser("list-appliances", help="List all appliances")
    p.add_argument("--category", default="", help="Filter by category")

    sub.add_parser("maintenance-due", help="Check maintenance schedule")

    p = sub.add_parser("add-automation", help="Add an automation")
    p.add_argument("--name", required=True, help="Automation name")
    p.add_argument("--trigger", required=True, help="time, sensor, manual")
    p.add_argument("--action", required=True, help="Action description")
    p.add_argument("--schedule", default="", help="Schedule (e.g. 08:00, Mon 08:00)")
    p.add_argument("--notes", default="", help="Notes")

    sub.add_parser("list-automations", help="List automations")
    p = sub.add_parser("toggle-automation", help="Enable/disable automation")
    p.add_argument("--name", required=True, help="Automation name")

    p = sub.add_parser("add-task", help="Add a household task")
    p.add_argument("--title", required=True, help="Task title")
    p.add_argument("--due-date", default="", help="Due date (YYYY-MM-DD)")
    p.add_argument("--priority", default="medium", help="high, medium, low")
    p.add_argument("--notes", default="", help="Notes")

    p = sub.add_parser("list-tasks", help="List tasks")
    p.add_argument("--status", default="", help="Filter by status: pending, done")

    sub.add_parser("report", help="Full home report")

    args = parser.parse_args()
    agent = HomeAgent()

    if args.cmd == "add-appliance":
        print(agent.add_appliance(args.name, args.category,
                                  brand=args.brand, model=args.model, location=args.location,
                                  purchase_date=args.purchase_date, warranty_months=args.warranty_months,
                                  maintenance_interval_days=args.maintenance_interval_days,
                                  last_maintenance=args.last_maintenance))
    elif args.cmd == "list-appliances":
        print(agent.list_appliances(getattr(args, 'category', '')))
    elif args.cmd == "maintenance-due":
        print(agent.maintenance_due())
    elif args.cmd == "add-automation":
        print(agent.add_automation(args.name, args.trigger, args.action,
                                   schedule=args.schedule, notes=args.notes))
    elif args.cmd == "list-automations":
        print(agent.list_automations())
    elif args.cmd == "toggle-automation":
        print(agent.toggle_automation(args.name))
    elif args.cmd == "add-task":
        print(agent.add_task(args.title, args.due_date, args.priority, args.notes))
    elif args.cmd == "list-tasks":
        print(agent.list_tasks(args.status))
    elif args.cmd == "report":
        print(agent.report())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
