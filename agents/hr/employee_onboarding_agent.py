#!/usr/bin/env python3
"""
Employee Onboarding Agent
Manages employee onboarding workflows and tracks progress.
Reads: employees.json, onboarding_checklists.json
Writes: employees.json, onboarding_progress.json, output/<employee>-checklist.txt
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
AGENTS_DIR = SCRIPT_DIR.parent
WORKSPACE = SCRIPT_DIR.parent.parent.parent
DATA_DIR = WORKSPACE / "data" / "hr"
LOGS_DIR = WORKSPACE / "logs"
OUTPUT_DIR = WORKSPACE / "data" / "hr" / "output"

LOGS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "employee_onboarding.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("EmployeeOnboarding")


def load_json(path: Path) -> dict | list:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {} if "." not in path.name else []
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {path}: {e}")
        return {} if "." not in path.name else []


def save_json(path: Path, data: Any) -> bool:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Failed to save {path}: {e}")
        return False


def get_default_checklists() -> dict:
    return {
        "default": {
            "name": "Standard Onboarding",
            "duration_days": 30,
            "stages": [
                {
                    "id": "day1",
                    "name": "Day 1 - Welcome",
                    "tasks": [
                        {"id": "setup_accounts", "title": "Set up email and Slack accounts", "owner": "IT"},
                        {"id": "welcome_email", "title": "Send welcome email with first-day info", "owner": "HR"},
                        {"id": "prepare_desk", "title": "Prepare workspace/equipment", "owner": "IT"},
                        {"id": "intro_meeting", "title": "Schedule intro meeting with team", "owner": "Manager"},
                    ],
                },
                {
                    "id": "week1",
                    "name": "Week 1 - Orientation",
                    "tasks": [
                        {"id": "company_overview", "title": "Company overview and history presentation", "owner": "HR"},
                        {"id": "org_structure", "title": "Review org chart and key contacts", "owner": "HR"},
                        {"id": "tools_training", "title": "Tools and systems training", "owner": "IT"},
                        {"id": "team_lunch", "title": "Team lunch introduction", "owner": "Manager"},
                        {"id": "first_project", "title": "Assign first small project", "owner": "Manager"},
                    ],
                },
                {
                    "id": "week2_4",
                    "name": "Weeks 2-4 - Integration",
                    "tasks": [
                        {"id": "setup_goals", "title": "Set up 30/60/90 day goals", "owner": "Manager"},
                        {"id": "role_training", "title": "Role-specific training", "owner": "Manager"},
                        {"id": "feedback_session", "title": "First feedback session", "owner": "Manager"},
                        {"id": "peer_buddy", "title": "Assign peer buddy", "owner": "HR"},
                    ],
                },
                {
                    "id": "completion",
                    "name": "Day 30 - Completion",
                    "tasks": [
                        {"id": "review_goals", "title": "30-day goals review", "owner": "Manager"},
                        {"id": "onboarding_survey", "title": "Onboarding satisfaction survey", "owner": "HR"},
                        {"id": "complete_doc", "title": "Complete all HR documentation", "owner": "HR"},
                    ],
                },
            ],
        }
    }


def get_default_employees() -> list:
    return []


def generate_checklist_for_employee(employee: dict, checklist: dict) -> str:
    """Generate a personalized onboarding checklist for an employee."""
    name = employee.get("name", "Employee")
    start_date = employee.get("start_date", datetime.now().strftime("%Y-%m-%d"))
    
    lines = []
    lines.append(f"# Onboarding Checklist for {name}")
    lines.append(f"**Start Date:** {start_date}")
    lines.append(f"**Department:** {employee.get('department', 'TBD')}")
    lines.append(f"**Role:** {employee.get('title', 'TBD')}")
    lines.append(f"**Manager:** {employee.get('manager', 'TBD')}")
    lines.append("")
    lines.append(f"Duration: {checklist.get('duration_days', 30)} days")
    lines.append("")
    
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        start = datetime.now()
    
    for stage in checklist.get("stages", []):
        lines.append(f"## {stage['name']}")
        lines.append("")
        for task in stage.get("tasks", []):
            task_id = task.get("id", "unknown")
            lines.append(f"- [ ] **{task['title']}**")
            lines.append(f"  - Owner: {task.get('owner', 'TBD')}")
            lines.append(f"  - Task ID: `{task_id}`")
        lines.append("")
    
    lines.append("---")
    lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    return "\n".join(lines)


def cmd_add(args) -> int:
    """Add a new employee to the system."""
    employees_file = DATA_DIR / "employees.json"
    employees = load_json(employees_file) or []
    
    # Check if employee already exists
    for emp in employees:
        if emp.get("email", "").lower() == args.email.lower():
            logger.error(f"Employee with email {args.email} already exists")
            return 1
    
    employee = {
        "id": f"emp_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "name": args.name,
        "email": args.email,
        "title": args.title,
        "department": args.department,
        "manager": args.manager or "",
        "start_date": args.start_date or datetime.now().strftime("%Y-%m-%d"),
        "status": "onboarding",
        "created_at": datetime.now().isoformat(),
    }
    
    employees.append(employee)
    save_json(employees_file, employees)
    
    # Create onboarding progress entry
    progress_file = DATA_DIR / "onboarding_progress.json"
    progress = load_json(progress_file) or []
    
    progress_entry = {
        "employee_id": employee["id"],
        "employee_name": employee["name"],
        "started_at": datetime.now().isoformat(),
        "tasks": {},
        "status": "in_progress",
    }
    progress.append(progress_entry)
    save_json(progress_file, progress)
    
    print(f"✅ Added employee: {employee['name']} ({employee['id']})")
    logger.info(f"Added employee: {employee['id']} - {employee['name']}")
    return 0


def cmd_list(args) -> int:
    """List all employees."""
    employees_file = DATA_DIR / "employees.json"
    employees = load_json(employees_file) or []
    
    if not employees:
        print("No employees found. Add one with: --add")
        return 0
    
    status_icons = {"onboarding": "🔄", "active": "✅", "offboarding": "🚪", "inactive": "⏸️"}
    
    print(f"\n👥 Employees ({len(employees)} total):")
    print("-" * 70)
    for emp in employees:
        icon = status_icons.get(emp.get("status", "unknown"), "❓")
        print(f"  {icon} [{emp['id']}] {emp['name']}")
        print(f"       📧 {emp.get('email', 'N/A')} | {emp.get('title', 'N/A')} | {emp.get('department', 'N/A')}")
        print(f"       Started: {emp.get('start_date', 'N/A')} | Status: {emp.get('status', 'unknown')}")
    print()
    return 0


def cmd_checklist(args) -> int:
    """Generate or show onboarding checklist for an employee."""
    employees_file = DATA_DIR / "employees.json"
    checklists_file = DATA_DIR / "onboarding_checklists.json"
    
    employees = load_json(employees_file) or []
    checklists = load_json(checklists_file) or get_default_checklists()
    
    # Find employee
    employee = None
    for emp in employees:
        if emp.get("id") == args.employee_id or emp.get("email", "").lower() == args.employee_id.lower():
            employee = emp
            break
    
    if not employee:
        logger.error(f"Employee not found: {args.employee_id}")
        return 1
    
    checklist = checklists.get("default", checklists.get("default"))
    
    checklist_text = generate_checklist_for_employee(employee, checklist)
    
    # Save to file
    safe_name = employee["name"].lower().replace(" ", "-")
    date_str = datetime.now().strftime("%Y%m%d")
    output_file = OUTPUT_DIR / f"checklist-{safe_name}-{date_str}.txt"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(checklist_text)
    
    print(checklist_text)
    print(f"\n✅ Saved to: {output_file}")
    logger.info(f"Generated checklist for {employee['id']}")
    return 0


def cmd_complete_task(args) -> int:
    """Mark an onboarding task as complete."""
    progress_file = DATA_DIR / "onboarding_progress.json"
    progress = load_json(progress_file) or []
    
    employee_id = args.employee_id
    task_id = args.task_id
    
    for p in progress:
        if p.get("employee_id") == employee_id:
            p["tasks"][task_id] = {
                "completed_at": datetime.now().isoformat(),
                "completed_by": args.completed_by or "system",
            }
            
            # Check if all tasks complete
            total_tasks = 11  # from default checklist
            completed = len(p.get("tasks", {}))
            if completed >= total_tasks:
                p["status"] = "completed"
                p["completed_at"] = datetime.now().isoformat()
            
            save_json(progress_file, progress)
            print(f"✅ Marked task '{task_id}' complete for employee {employee_id}")
            print(f"   Progress: {completed}/{total_tasks} tasks")
            logger.info(f"Completed task {task_id} for {employee_id}")
            return 0
    
    logger.error(f"Employee not found in progress: {employee_id}")
    return 1


def cmd_status(args) -> int:
    """Show onboarding status for an employee."""
    progress_file = DATA_DIR / "onboarding_progress.json"
    progress = load_json(progress_file) or []
    
    employee_id = args.employee_id
    
    for p in progress:
        if p.get("employee_id") == employee_id:
            print(f"\n📋 Onboarding Status for {p.get('employee_name', 'Unknown')}")
            print("-" * 50)
            print(f"   Started: {p.get('started_at', 'N/A')[:10]}")
            print(f"   Status: {p.get('status', 'unknown')}")
            tasks = p.get("tasks", {})
            print(f"   Completed Tasks: {len(tasks)}")
            if tasks:
                print("   Task Details:")
                for task_id, details in tasks.items():
                    completed_at = details.get("completed_at", "N/A")[:10]
                    print(f"     ✅ {task_id}: {completed_at}")
            return 0
    
    logger.error(f"Employee not found: {employee_id}")
    return 1


def cmd_init(args) -> int:
    """Initialize HR data files."""
    employees_file = DATA_DIR / "employees.json"
    checklists_file = DATA_DIR / "onboarding_checklists.json"
    
    if not employees_file.exists():
        save_json(employees_file, get_default_employees())
        print(f"✅ Created: {employees_file}")
    else:
        print(f"⚠️  {employees_file} already exists")
    
    if not checklists_file.exists():
        save_json(checklists_file, get_default_checklists())
        print(f"✅ Created: {checklists_file}")
    else:
        print(f"⚠️  {checklists_file} already exists")
    
    logger.info("Initialized onboarding data files")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Employee Onboarding Agent - Manage onboarding workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --init                           Initialize data files
  %(prog)s --list                            List all employees
  %(prog)s --add --name "John Doe" --email john@example.com --title "Engineer" --department Engineering
  %(prog)s --checklist emp_20260327112030    Generate checklist for employee
  %(prog)s --status emp_20260327112030       Show onboarding status
  %(prog)s --complete-task emp_20260327112030 --task-id setup_accounts
        """,
    )
    
    parser.add_argument("--init", action="store_true", help="Initialize data files")
    parser.add_argument("--list", action="store_true", help="List all employees")
    parser.add_argument("--add", action="store_true", help="Add a new employee")
    parser.add_argument("--name", help="Employee name (for --add)")
    parser.add_argument("--email", help="Employee email (for --add)")
    parser.add_argument("--title", default="Team Member", help="Job title")
    parser.add_argument("--department", default="General", help="Department")
    parser.add_argument("--manager", help="Manager name")
    parser.add_argument("--start-date", dest="start_date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--checklist", help="Generate checklist for employee ID")
    parser.add_argument("--status", dest="employee_id", help="Show onboarding status for employee")
    parser.add_argument("--complete-task", action="store_true", help="Mark task complete")
    parser.add_argument("--task-id", dest="task_id", help="Task ID to mark complete")
    parser.add_argument("--completed-by", dest="completed_by", help="Who completed the task")
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        parser.print_help()
        print("\n💡 Quick start: %(prog)s --init && %(prog)s --add --name 'John Doe' --email john@company.com")
        return 0
    
    try:
        if args.init:
            return cmd_init(args)
        if args.list:
            return cmd_list(args)
        if args.add:
            if not args.name or not args.email:
                logger.error("--name and --email required for --add")
                return 1
            return cmd_add(args)
        if args.checklist:
            args.employee_id = args.checklist
            return cmd_checklist(args)
        if "--status" in sys.argv:
            emp_id = getattr(args, 'employee_id', None)
            if emp_id:
                args.employee_id = emp_id
                return cmd_status(args)
        if args.complete_task:
            if not args.employee_id or not args.task_id:
                logger.error("--employee-id and --task-id required for --complete-task")
                return 1
            return cmd_complete_task(args)
        
        parser.print_help()
        return 0
    except KeyboardInterrupt:
        print("\n⚠️  Cancelled")
        return 130
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
