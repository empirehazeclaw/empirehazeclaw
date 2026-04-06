#!/usr/bin/env python3
"""
Project Tracker Agent - Freelance Division
Tracks freelance projects, milestones, time tracking, and deliverables.

Inspired by SOUL.md: CEO mindset, Eigenverantwortung, Geschwindigkeit über Perfektion
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
WORKSPACE = SCRIPT_DIR.parent.parent.parent
LOG_DIR = WORKSPACE / "logs"
DATA_DIR = WORKSPACE / "data" / "freelance"
PROJECTS_FILE = DATA_DIR / "projects.json"

# Ensure directories exist
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - PROJECT-TRACKER - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "project_tracker.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def load_projects():
    """Load projects from JSON file."""
    if not PROJECTS_FILE.exists():
        return {"projects": [], "version": "1.0"}
    try:
        with open(PROJECTS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse projects file: {e}")
        return {"projects": [], "version": "1.0"}


def save_projects(data):
    """Save projects to JSON file."""
    try:
        with open(PROJECTS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved {len(data['projects'])} projects to {PROJECTS_FILE}")
    except IOError as e:
        logger.error(f"Failed to save projects: {e}")
        raise


def create_project(name, client_id, description=None, budget=None, deadline=None):
    """Create a new project."""
    data = load_projects()
    
    new_project = {
        "id": len(data['projects']) + 1,
        "name": name,
        "client_id": client_id,
        "description": description or "",
        "budget": budget,
        "deadline": deadline,
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "milestones": [],
        "time_entries": [],
        "total_hours": 0.0,
        "total_cost": 0.0,
        "deliverables": []
    }
    
    data['projects'].append(new_project)
    save_projects(data)
    logger.info(f"Created project: {name} (ID: {new_project['id']})")
    print(f"✅ Created project: {name} (ID: {new_project['id']})")
    return True


def list_projects(status_filter=None, client_filter=None):
    """List all projects."""
    data = load_projects()
    projects = data['projects']
    
    if status_filter:
        projects = [p for p in projects if p.get('status') == status_filter]
    
    if client_filter is not None:
        projects = [p for p in projects if p.get('client_id') == client_filter]
    
    if not projects:
        print("📭 No projects found.")
        return
    
    status_icons = {
        "active": "🟢",
        "on_hold": "🟡",
        "completed": "✅",
        "cancelled": "❌"
    }
    
    print(f"\n📋 Projects ({len(projects)} total):")
    print("-" * 80)
    for project in projects:
        icon = status_icons.get(project.get('status', 'active'), "⚪")
        budget_str = f"${project.get('budget', 0):.2f}" if project.get('budget') else "N/A"
        deadline_str = project.get('deadline', 'No deadline')
        print(f"{icon} [{project['id']}] {project['name']}")
        print(f"   Client ID: {project.get('client_id', 'N/A')} | Budget: {budget_str} | Deadline: {deadline_str}")
        print(f"   Hours: {project.get('total_hours', 0):.1f} | Cost: ${project.get('total_cost', 0):.2f}")
        print()


def get_project(project_id):
    """Get a specific project by ID."""
    data = load_projects()
    for project in data['projects']:
        if project['id'] == project_id:
            return project
    return None


def show_project(project_id):
    """Display detailed project information."""
    project = get_project(project_id)
    if not project:
        print(f"❌ Project with ID {project_id} not found.")
        return
    
    status_icons = {
        "active": "🟢 Active",
        "on_hold": "🟡 On Hold",
        "completed": "✅ Completed",
        "cancelled": "❌ Cancelled"
    }
    
    print(f"\n📁 Project Details:")
    print("=" * 60)
    print(f"ID:          {project['id']}")
    print(f"Name:        {project['name']}")
    print(f"Client ID:   {project.get('client_id', 'N/A')}")
    print(f"Status:      {status_icons.get(project.get('status', 'active'), project.get('status'))}")
    print(f"Description: {project.get('description', 'N/A')}")
    print(f"Budget:      ${project.get('budget', 0):.2f}" if project.get('budget') else "Budget:      N/A")
    print(f"Deadline:    {project.get('deadline', 'N/A')}")
    print(f"Created:     {project.get('created_at', 'N/A')}")
    print(f"Total Hours: {project.get('total_hours', 0):.1f}")
    print(f"Total Cost:  ${project.get('total_cost', 0):.2f}")
    
    if project.get('milestones'):
        print(f"\n🎯 Milestones ({len(project['milestones'])}):")
        for i, ms in enumerate(project['milestones'], 1):
            status = "✅" if ms.get('completed') else "⬜"
            print(f"   {status} {i}. {ms.get('name', 'Unnamed')}")
            if ms.get('due_date'):
                print(f"      Due: {ms.get('due_date')}")
    
    if project.get('time_entries'):
        print(f"\n⏱️  Time Entries ({len(project['time_entries'])}):")
        for entry in project['time_entries'][-5:]:
            print(f"   [{entry.get('date', 'N/A')}] {entry.get('hours', 0):.1f}h - {entry.get('description', 'No description')[:40]}")
    
    if project.get('deliverables'):
        print(f"\n📦 Deliverables ({len(project['deliverables'])}):")
        for i, d in enumerate(project['deliverables'], 1):
            status = "✅" if d.get('delivered') else "⬜"
            print(f"   {status} {i}. {d.get('name', 'Unnamed')}")


def update_project(project_id, **kwargs):
    """Update project information."""
    data = load_projects()
    
    for project in data['projects']:
        if project['id'] == project_id:
            for key, value in kwargs.items():
                if key in ['name', 'description', 'budget', 'deadline', 'status']:
                    project[key] = value
            project['updated_at'] = datetime.now().isoformat()
            save_projects(data)
            logger.info(f"Updated project {project_id}: {kwargs}")
            print(f"✅ Updated project {project_id}")
            return True
    
    print(f"❌ Project with ID {project_id} not found.")
    return False


def add_milestone(project_id, name, due_date=None):
    """Add a milestone to a project."""
    data = load_projects()
    
    for project in data['projects']:
        if project['id'] == project_id:
            milestone = {
                "id": len(project.get('milestones', [])) + 1,
                "name": name,
                "due_date": due_date,
                "completed": False,
                "created_at": datetime.now().isoformat()
            }
            project.setdefault('milestones', []).append(milestone)
            project['updated_at'] = datetime.now().isoformat()
            save_projects(data)
            logger.info(f"Added milestone '{name}' to project {project_id}")
            print(f"✅ Added milestone '{name}' to project {project['name']}")
            return True
    
    print(f"❌ Project with ID {project_id} not found.")
    return False


def complete_milestone(project_id, milestone_id):
    """Mark a milestone as completed."""
    data = load_projects()
    
    for project in data['projects']:
        if project['id'] == project_id:
            for ms in project.get('milestones', []):
                if ms['id'] == milestone_id:
                    ms['completed'] = True
                    ms['completed_at'] = datetime.now().isoformat()
                    project['updated_at'] = datetime.now().isoformat()
                    save_projects(data)
                    logger.info(f"Completed milestone {milestone_id} in project {project_id}")
                    print(f"✅ Completed milestone '{ms['name']}'")
                    return True
            print(f"❌ Milestone {milestone_id} not found in project {project_id}")
            return False
    
    print(f"❌ Project with ID {project_id} not found.")
    return False


def log_time(project_id, hours, description=None, date=None):
    """Log time to a project."""
    data = load_projects()
    hourly_rate = 50.0  # Default hourly rate
    
    for project in data['projects']:
        if project['id'] == project_id:
            entry = {
                "id": len(project.get('time_entries', [])) + 1,
                "date": date or datetime.now().strftime("%Y-%m-%d"),
                "hours": float(hours),
                "description": description or "",
                "logged_at": datetime.now().isoformat()
            }
            project.setdefault('time_entries', []).append(entry)
            project['total_hours'] = project.get('total_hours', 0) + float(hours)
            project['total_cost'] = project['total_hours'] * hourly_rate
            project['updated_at'] = datetime.now().isoformat()
            save_projects(data)
            logger.info(f"Logged {hours}h to project {project_id}")
            print(f"✅ Logged {hours}h to project {project['name']} (Total: {project['total_hours']:.1f}h / ${project['total_cost']:.2f})")
            return True
    
    print(f"❌ Project with ID {project_id} not found.")
    return False


def add_deliverable(project_id, name, description=None):
    """Add a deliverable to a project."""
    data = load_projects()
    
    for project in data['projects']:
        if project['id'] == project_id:
            deliverable = {
                "id": len(project.get('deliverables', [])) + 1,
                "name": name,
                "description": description or "",
                "delivered": False,
                "created_at": datetime.now().isoformat()
            }
            project.setdefault('deliverables', []).append(deliverable)
            project['updated_at'] = datetime.now().isoformat()
            save_projects(data)
            logger.info(f"Added deliverable '{name}' to project {project_id}")
            print(f"✅ Added deliverable '{name}' to project {project['name']}")
            return True
    
    print(f"❌ Project with ID {project_id} not found.")
    return False


def deliver_item(project_id, deliverable_id):
    """Mark a deliverable as delivered."""
    data = load_projects()
    
    for project in data['projects']:
        if project['id'] == project_id:
            for d in project.get('deliverables', []):
                if d['id'] == deliverable_id:
                    d['delivered'] = True
                    d['delivered_at'] = datetime.now().isoformat()
                    project['updated_at'] = datetime.now().isoformat()
                    save_projects(data)
                    logger.info(f"Delivered item {deliverable_id} in project {project_id}")
                    print(f"✅ Delivered '{d['name']}'")
                    return True
            print(f"❌ Deliverable {deliverable_id} not found")
            return False
    
    print(f"❌ Project with ID {project_id} not found.")
    return False


def get_stats():
    """Show project statistics."""
    data = load_projects()
    projects = data['projects']
    
    total = len(projects)
    active = len([p for p in projects if p.get('status') == 'active'])
    completed = len([p for p in projects if p.get('status') == 'completed'])
    on_hold = len([p for p in projects if p.get('status') == 'on_hold'])
    
    total_hours = sum(p.get('total_hours', 0) for p in projects)
    total_budget = sum(p.get('budget', 0) for p in projects)
    total_cost = sum(p.get('total_cost', 0) for p in projects)
    
    # Upcoming deadlines
    today = datetime.now().date()
    upcoming = []
    for p in projects:
        if p.get('deadline') and p.get('status') == 'active':
            try:
                deadline = datetime.strptime(p['deadline'], "%Y-%m-%d").date()
                days_until = (deadline - today).days
                if 0 <= days_until <= 7:
                    upcoming.append((p['name'], p['deadline'], days_until))
            except ValueError:
                pass
    
    print(f"\n📊 Project Statistics:")
    print("=" * 40)
    print(f"Total Projects:   {total}")
    print(f"Active:           {active} 🟢")
    print(f"On Hold:          {on_hold} 🟡")
    print(f"Completed:        {completed} ✅")
    print(f"Total Hours:      {total_hours:.1f}")
    print(f"Total Budget:     ${total_budget:.2f}")
    print(f"Total Cost:       ${total_cost:.2f}")
    
    if total_budget > 0:
        profit = total_budget - total_cost
        print(f"Profit/Loss:     ${profit:.2f}")
    
    if upcoming:
        print(f"\n⚠️  Upcoming Deadlines (next 7 days):")
        for name, deadline, days in sorted(upcoming, key=lambda x: x[2]):
            print(f"   {name}: {deadline} ({days} days)")


def main():
    parser = argparse.ArgumentParser(
        description="Project Tracker Agent - Track your freelance projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create "Website Redesign" --client-id 1 --budget 2000 --deadline 2026-04-15
  %(prog)s list
  %(prog)s list --status active
  %(prog)s show 1
  %(prog)s update 1 --status completed
  %(prog)s milestone 1 "Design Phase" --due-date 2026-04-01
  %(prog)s complete-milestone 1 1
  %(prog)s time 1 4.5 --description "Homepage design"
  %(prog)s deliverable 1 "Final mockups"
  %(prog)s deliver 1 1
  %(prog)s stats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create project
    create_parser = subparsers.add_parser('create', help='Create a new project')
    create_parser.add_argument('name', help='Project name')
    create_parser.add_argument('--client-id', type=int, required=True, help='Client ID')
    create_parser.add_argument('--description', '-d', help='Project description')
    create_parser.add_argument('--budget', '-b', type=float, help='Budget in USD')
    create_parser.add_argument('--deadline', '-dl', help='Deadline (YYYY-MM-DD)')
    
    # List projects
    list_parser = subparsers.add_parser('list', help='List all projects')
    list_parser.add_argument('--status', '-s', choices=['active', 'on_hold', 'completed', 'cancelled'],
                            help='Filter by status')
    list_parser.add_argument('--client-id', type=int, help='Filter by client ID')
    
    # Show project
    show_parser = subparsers.add_parser('show', help='Show project details')
    show_parser.add_argument('project_id', type=int, help='Project ID')
    
    # Update project
    update_parser = subparsers.add_parser('update', help='Update project')
    update_parser.add_argument('project_id', type=int, help='Project ID')
    update_parser.add_argument('--name', help='New name')
    update_parser.add_argument('--description', help='New description')
    update_parser.add_argument('--budget', type=float, help='New budget')
    update_parser.add_argument('--deadline', help='New deadline')
    update_parser.add_argument('--status', choices=['active', 'on_hold', 'completed', 'cancelled'],
                               help='New status')
    
    # Add milestone
    milestone_parser = subparsers.add_parser('milestone', help='Add milestone to project')
    milestone_parser.add_argument('project_id', type=int, help='Project ID')
    milestone_parser.add_argument('name', help='Milestone name')
    milestone_parser.add_argument('--due-date', help='Due date (YYYY-MM-DD)')
    
    # Complete milestone
    complete_parser = subparsers.add_parser('complete-milestone', help='Mark milestone complete')
    complete_parser.add_argument('project_id', type=int, help='Project ID')
    complete_parser.add_argument('milestone_id', type=int, help='Milestone ID')
    
    # Log time
    time_parser = subparsers.add_parser('time', help='Log time to project')
    time_parser.add_argument('project_id', type=int, help='Project ID')
    time_parser.add_argument('hours', type=float, help='Hours worked')
    time_parser.add_argument('--description', help='Description of work')
    time_parser.add_argument('--date', help='Date (YYYY-MM-DD, default: today)')
    
    # Add deliverable
    deliverable_parser = subparsers.add_parser('deliverable', help='Add deliverable to project')
    deliverable_parser.add_argument('project_id', type=int, help='Project ID')
    deliverable_parser.add_argument('name', help='Deliverable name')
    deliverable_parser.add_argument('--description', help='Description')
    
    # Mark delivered
    deliver_parser = subparsers.add_parser('deliver', help='Mark deliverable as delivered')
    deliver_parser.add_argument('project_id', type=int, help='Project ID')
    deliver_parser.add_argument('deliverable_id', type=int, help='Deliverable ID')
    
    # Stats
    subparsers.add_parser('stats', help='Show project statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'create':
            create_project(args.name, args.client_id, args.description, args.budget, args.deadline)
        elif args.command == 'list':
            list_projects(args.status, args.client_id if hasattr(args, 'client_id') else None)
        elif args.command == 'show':
            show_project(args.project_id)
        elif args.command == 'update':
            kwargs = {k: v for k, v in vars(args).items() 
                      if k not in ['command', 'project_id'] and v is not None}
            if kwargs:
                update_project(args.project_id, **kwargs)
            else:
                print("❌ No updates specified.")
        elif args.command == 'milestone':
            add_milestone(args.project_id, args.name, args.due_date)
        elif args.command == 'complete-milestone':
            complete_milestone(args.project_id, args.milestone_id)
        elif args.command == 'time':
            log_time(args.project_id, args.hours, args.description, args.date)
        elif args.command == 'deliverable':
            add_deliverable(args.project_id, args.name, args.description)
        elif args.command == 'deliver':
            deliver_item(args.project_id, args.deliverable_id)
        elif args.command == 'stats':
            get_stats()
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
