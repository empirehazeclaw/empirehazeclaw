#!/usr/bin/env python3
"""
Goals Tracker Agent
Track personal and professional goals, milestones, and progress.
Stores data in JSON format.
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "goals_tracker.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GoalsTrackerAgent")

DATA_FILE = Path("/home/clawbot/.openclaw/workspace/data/goals_tracker.json")
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"goals": [], "milestones": [], "last_goal_id": 0, "last_milestone_id": 0}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def create_goal(args):
    """Create a new goal."""
    data = load_data()
    data["last_goal_id"] += 1
    
    goal = {
        "id": data["last_goal_id"],
        "title": args.title,
        "description": args.description or "",
        "category": args.category,
        "target_value": float(args.target) if args.target else None,
        "current_value": float(args.start) if args.start else 0,
        "unit": args.unit or "",
        "deadline": args.deadline,
        "priority": args.priority,
        "status": "active",
        "milestones": [],
        "created_at": datetime.now().isoformat(),
        "completed_at": None
    }
    
    data["goals"].append(goal)
    save_data(data)
    logger.info(f"Created goal {goal['id']}: {goal['title']}")
    print(f"✅ Created goal #{goal['id']}: {goal['title']}")
    print(f"   Category: {args.category} | Priority: {args.priority}")
    if args.deadline:
        print(f"   Deadline: {args.deadline}")
    return goal

def add_milestone(args):
    """Add a milestone to a goal."""
    data = load_data()
    for g in data["goals"]:
        if g["id"] == int(args.goal):
            data["last_milestone_id"] += 1
            milestone = {
                "id": data["last_milestone_id"],
                "title": args.title,
                "target_value": float(args.target) if args.target else None,
                "completed": False,
                "completed_at": None,
                "created_at": datetime.now().isoformat()
            }
            g["milestones"].append(milestone)
            save_data(data)
            print(f"✅ Added milestone to goal #{g['id']}: {args.title}")
            return
    print(f"Goal #{args.goal} not found.")

def update_progress(args):
    """Update progress on a goal."""
    data = load_data()
    for g in data["goals"]:
        if g["id"] == int(args.id):
            old_value = g["current_value"]
            g["current_value"] = float(args.value)
            
            if g["target_value"] and g["current_value"] >= g["target_value"]:
                g["status"] = "completed"
                g["completed_at"] = datetime.now().isoformat()
                print(f"🎉 Goal completed!")
            
            save_data(data)
            
            pct = 0
            if g["target_value"]:
                pct = (g["current_value"] / g["target_value"]) * 100
            
            print(f"✅ Updated goal #{g['id']}: {g['title']}")
            print(f"   Progress: {old_value} → {g['current_value']} {g['unit']}")
            if g["target_value"]:
                print(f"   {pct:.1f}% complete")
            return
    print(f"Goal #{args.id} not found.")

def complete_milestone(args):
    """Mark a milestone as complete."""
    data = load_data()
    for g in data["goals"]:
        if g["id"] == int(args.goal):
            for m in g["milestones"]:
                if m["id"] == int(args.milestone):
                    m["completed"] = True
                    m["completed_at"] = datetime.now().isoformat()
                    save_data(data)
                    print(f"✅ Completed milestone: {m['title']}")
                    return
            print(f"Milestone #{args.milestone} not found in goal #{args.goal}")
            return
    print(f"Goal #{args.goal} not found.")

def list_goals(args):
    """List all goals."""
    data = load_data()
    goals = data["goals"]
    
    if args.category:
        goals = [g for g in goals if g["category"] == args.category]
    if args.status:
        goals = [g for g in goals if g["status"] == args.status]
    if args.priority:
        goals = [g for g in goals if g["priority"] == args.priority]
    
    if not goals:
        print("No goals found.")
        return
    
    print(f"\n🎯 Goals ({len(goals)}):\n")
    for g in goals:
        status_icon = {"active": "🔄", "completed": "✅", "paused": "⏸️", "cancelled": "❌"}.get(g["status"], "❓")
        pct = 0
        if g["target_value"]:
            pct = (g["current_value"] / g["target_value"]) * 100
        
        print(f"  [{g['id']}] {status_icon} {g['title']}")
        print(f"      Category: {g['category']} | Priority: {g['priority']}")
        if g["target_value"]:
            print(f"      Progress: {g['current_value']}/{g['target_value']} {g['unit']} ({pct:.1f}%)")
        if g["deadline"]:
            print(f"      Deadline: {g['deadline']}")
        print()

def get_goal(args):
    """Get detailed goal information."""
    data = load_data()
    for g in data["goals"]:
        if g["id"] == int(args.id):
            pct = 0
            if g["target_value"]:
                pct = (g["current_value"] / g["target_value"]) * 100
            
            print(f"\n🎯 Goal #{g['id']}: {g['title']}")
            print(f"  Description: {g['description']}")
            print(f"  Category: {g['category']} | Priority: {g['priority']}")
            print(f"  Status: {g['status']}")
            if g["target_value"]:
                print(f"  Progress: {g['current_value']}/{g['target_value']} {g['unit']} ({pct:.1f}%)")
            else:
                print(f"  Progress: {g['current_value']} {g['unit']}")
            if g["deadline"]:
                print(f"  Deadline: {g['deadline']}")
            print(f"  Created: {g['created_at'][:10]}")
            if g["completed_at"]:
                print(f"  Completed: {g['completed_at'][:10]}")
            
            if g["milestones"]:
                print(f"\n  📍 Milestones:")
                completed = 0
                for m in g["milestones"]:
                    status = "✅" if m["completed"] else "⏳"
                    if m["completed"]:
                        completed += 1
                    print(f"    {status} [{m['id']}] {m['title']}")
                    if m["target_value"]:
                        print(f"        Target: {m['target_value']}")
                    if m["completed_at"]:
                        print(f"        Completed: {m['completed_at'][:10]}")
                print(f"\n  Milestones: {completed}/{len(g['milestones'])} completed")
            return
    print(f"Goal #{args.id} not found.")

def update_goal(args):
    """Update goal details."""
    data = load_data()
    for g in data["goals"]:
        if g["id"] == int(args.id):
            if args.title:
                g["title"] = args.title
            if args.description:
                g["description"] = args.description
            if args.priority:
                g["priority"] = args.priority
            if args.deadline:
                g["deadline"] = args.deadline
            if args.status:
                g["status"] = args.status
                if args.status == "completed":
                    g["completed_at"] = datetime.now().isoformat()
            save_data(data)
            print(f"✅ Updated goal #{g['id']}")
            return
    print(f"Goal #{args.id} not found.")

def delete_goal(args):
    """Delete a goal."""
    data = load_data()
    original = len(data["goals"])
    data["goals"] = [g for g in data["goals"] if g["id"] != int(args.id)]
    if len(data["goals"]) < original:
        save_data(data)
        print(f"✅ Deleted goal #{args.id}")
    else:
        print(f"Goal #{args.id} not found.")

def dashboard(args):
    """Show goals dashboard."""
    data = load_data()
    goals = data["goals"]
    
    total = len(goals)
    active = len([g for g in goals if g["status"] == "active"])
    completed = len([g for g in goals if g["status"] == "completed"])
    
    goals_with_targets = [g for g in goals if g["target_value"]]
    overall_pct = 0
    if goals_with_targets:
        overall_pct = sum((g["current_value"] / g["target_value"]) * 100 for g in goals_with_targets) / len(goals_with_targets)
    
    today = datetime.now()
    upcoming = []
    for g in goals:
        if g["deadline"] and g["status"] == "active":
            try:
                deadline = datetime.strptime(g["deadline"], "%Y-%m-%d")
                days_left = (deadline - today).days
                if 0 <= days_left <= 30:
                    upcoming.append((g, days_left))
            except:
                pass
    
    print(f"\n📊 Goals Dashboard\n")
    print(f"  Total Goals: {total}")
    print(f"  Active: {active} | Completed: {completed}")
    print(f"  Overall Progress: {overall_pct:.1f}%")
    
    if upcoming:
        print(f"\n  ⏰ Upcoming Deadlines:")
        for g, days in sorted(upcoming, key=lambda x: x[1])[:5]:
            print(f"    {g['title']}: {days} days left")
    
    print(f"\n  By Priority:")
    for p in ["high", "medium", "low"]:
        count = len([g for g in goals if g["priority"] == p and g["status"] == "active"])
        print(f"    {p.capitalize()}: {count}")

def main():
    parser = argparse.ArgumentParser(
        description="Goals Tracker Agent - Track personal and professional goals",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create --title "Save $10,000" --category finance --target 10000 --unit "$" --deadline 2026-12-31 --priority high
  %(prog)s add-milestone --goal 1 --title "Save $5,000" --target 5000
  %(prog)s update --id 1 --value 2500
  %(prog)s complete --goal 1 --milestone 1
  %(prog)s list --status active --priority high
  %(prog)s get --id 1
  %(prog)s dashboard
  %(prog)s delete --id 2
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    p_create = subparsers.add_parser("create", help="Create a goal")
    p_create.add_argument("--title", required=True, help="Goal title")
    p_create.add_argument("--description", help="Description")
    p_create.add_argument("--category", required=True, choices=["health", "finance", "career", "education", "personal", "other"])
    p_create.add_argument("--target", help="Target value")
    p_create.add_argument("--start", help="Starting value")
    p_create.add_argument("--unit", help="Unit")
    p_create.add_argument("--deadline", help="Deadline (YYYY-MM-DD)")
    p_create.add_argument("--priority", required=True, choices=["high", "medium", "low"])
    
    p_milestone = subparsers.add_parser("add-milestone", help="Add milestone")
    p_milestone.add_argument("--goal", required=True, type=int, help="Goal ID")
    p_milestone.add_argument("--title", required=True, help="Milestone title")
    p_milestone.add_argument("--target", help="Target value")
    
    p_update = subparsers.add_parser("update", help="Update progress")
    p_update.add_argument("--id", required=True, type=int, help="Goal ID")
    p_update.add_argument("--value", required=True, help="New current value")
    
    p_complete = subparsers.add_parser("complete", help="Complete milestone")
    p_complete.add_argument("--goal", required=True, type=int, help="Goal ID")
    p_complete.add_argument("--milestone", required=True, type=int, help="Milestone ID")
    
    p_list = subparsers.add_parser("list", help="List goals")
    p_list.add_argument("--category", choices=["health", "finance", "career", "education", "personal", "other"])
    p_list.add_argument("--status", choices=["active", "completed", "paused", "cancelled"])
    p_list.add_argument("--priority", choices=["high", "medium", "low"])
    
    p_get = subparsers.add_parser("get", help="Get goal details")
    p_get.add_argument("--id", required=True, type=int, help="Goal ID")
    
    p_update_goal = subparsers.add_parser("update-goal", help="Update goal")
    p_update_goal.add_argument("--id", required=True, type=int, help="Goal ID")
    p_update_goal.add_argument("--title", help="New title")
    p_update_goal.add_argument("--description", help="New description")
    p_update_goal.add_argument("--priority", choices=["high", "medium", "low"])
    p_update_goal.add_argument("--deadline", help="New deadline")
    p_update_goal.add_argument("--status", choices=["active", "completed", "paused", "cancelled"])
    
    p_delete = subparsers.add_parser("delete", help="Delete goal")
    p_delete.add_argument("--id", required=True, type=int, help="Goal ID")
    
    subparsers.add_parser("dashboard", help="Show dashboard")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    try:
        if args.command == "create":
            create_goal(args)
        elif args.command == "add-milestone":
            add_milestone(args)
        elif args.command == "update":
            update_progress(args)
        elif args.command == "complete":
            complete_milestone(args)
        elif args.command == "list":
            list_goals(args)
        elif args.command == "get":
            get_goal(args)
        elif args.command == "update-goal":
            update_goal(args)
        elif args.command == "delete":
            delete_goal(args)
        elif args.command == "dashboard":
            dashboard(args)
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
