#!/usr/bin/env python3
"""
COO Operations Agent
====================
Handles operational workflows, task management, process automation, and resource tracking.
Keeps the business running smoothly.
"""

import argparse
import json
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import uuid

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - COO - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "coo_operations.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Data paths
DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data/business")
DATA_DIR.mkdir(parents=True, exist_ok=True)
TASKS_FILE = DATA_DIR / "tasks.json"
PROCESSES_FILE = DATA_DIR / "processes.json"
RESOURCES_FILE = DATA_DIR / "resources.json"
WORKFLOWS_FILE = DATA_DIR / "workflows.json"


def load_json(filepath: Path, default: dict = None) -> dict:
    """Load JSON file or return default."""
    if default is None:
        default = {}
    try:
        if filepath.exists():
            return json.loads(filepath.read_text())
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
    return default


def save_json(filepath: Path, data: dict) -> bool:
    """Save data to JSON file."""
    try:
        filepath.write_text(json.dumps(data, indent=2, default=str))
        return True
    except Exception as e:
        logger.error(f"Error saving {filepath}: {e}")
        return False


def init_data_files():
    """Initialize data files if they don't exist."""
    if not TASKS_FILE.exists():
        save_json(TASKS_FILE, {"tasks": [], "next_id": 1})
    
    if not PROCESSES_FILE.exists():
        save_json(PROCESSES_FILE, {"processes": []})
    
    if not RESOURCES_FILE.exists():
        save_json(RESOURCES_FILE, {"resources": []})
    
    if not WORKFLOWS_FILE.exists():
        save_json(WORKFLOWS_FILE, {"workflows": []})


def cmd_status(args) -> int:
    """Show operational status overview."""
    logger.info("Showing operational status...")
    
    tasks = load_json(TASKS_FILE)
    processes = load_json(PROCESSES_FILE)
    resources = load_json(RESOURCES_FILE)
    workflows = load_json(WORKFLOWS_FILE)
    
    active_tasks = [t for t in tasks.get('tasks', []) if t.get('status') == 'in_progress']
    pending_tasks = [t for t in tasks.get('tasks', []) if t.get('status') == 'pending']
    completed_today = [t for t in tasks.get('tasks', []) 
                       if t.get('status') == 'completed' 
                       and t.get('completed_at', '').startswith(datetime.now().strftime('%Y-%m-%d'))]
    
    print("\n" + "="*60)
    print("⚙️  COO OPERATIONS DASHBOARD")
    print("="*60)
    print(f"📅 Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("-"*60)
    
    print("\n📋 TASKS")
    print(f"   Active:    {len(active_tasks)}")
    print(f"   Pending:   {len(pending_tasks)}")
    print(f"   Completed Today: {len(completed_today)}")
    
    if active_tasks:
        print("\n   Active Tasks:")
        for task in active_tasks[:5]:
            print(f"      🔄 {task.get('title', 'Untitled')} (Priority: {task.get('priority', 'medium')})")
    
    print("\n🔄 PROCESSES")
    print(f"   Total: {len(processes.get('processes', []))}")
    active_procs = [p for p in processes.get('processes', []) if p.get('status') == 'running']
    print(f"   Running: {len(active_procs)}")
    
    print("\n👥 RESOURCES")
    print(f"   Total: {len(resources.get('resources', []))}")
    
    print("\n🚀 WORKFLOWS")
    print(f"   Total: {len(workflows.get('workflows', []))}")
    active_wf = [w for w in workflows.get('workflows', []) if w.get('status') == 'active']
    print(f"   Active: {len(active_wf)}")
    
    print("\n" + "="*60)
    return 0


def cmd_add_task(args) -> int:
    """Add a new task."""
    logger.info(f"Adding task: {args.title}")
    
    tasks = load_json(TASKS_FILE)
    
    task = {
        "id": tasks.get('next_id', 1),
        "title": args.title,
        "description": args.description or "",
        "status": "pending",
        "priority": args.priority,
        "category": args.category or "general",
        "created_at": datetime.now().isoformat(),
        "due_date": args.due_date,
        "assignee": args.assignee
    }
    
    tasks['tasks'].append(task)
    tasks['next_id'] = tasks.get('next_id', 1) + 1
    
    save_json(TASKS_FILE, tasks)
    
    print(f"✅ Task added: #{task['id']} - {args.title}")
    return 0


def cmd_list_tasks(args) -> int:
    """List tasks with optional filters."""
    logger.info("Listing tasks...")
    
    tasks = load_json(TASKS_FILE)
    all_tasks = tasks.get('tasks', [])
    
    if args.status:
        all_tasks = [t for t in all_tasks if t.get('status') == args.status]
    if args.category:
        all_tasks = [t for t in all_tasks if t.get('category') == args.category]
    if args.priority:
        all_tasks = [t for t in all_tasks if t.get('priority') == args.priority]
    
    if not all_tasks:
        print("No tasks found matching criteria.")
        return 0
    
    print(f"\n📋 Tasks ({len(all_tasks)} found):")
    print("-"*70)
    for task in all_tasks:
        status_icon = {"pending": "⏳", "in_progress": "🔄", "completed": "✅", "blocked": "🚫"}.get(
            task.get('status', 'pending'), "❓")
        print(f"   {status_icon} #{task.get('id')} | {task.get('priority', 'medium'):<10} | {task.get('title', 'Untitled')}")
        if task.get('due_date'):
            print(f"          Due: {task.get('due_date')} | Category: {task.get('category', 'none')}")
    
    return 0


def cmd_complete_task(args) -> int:
    """Mark a task as completed."""
    logger.info(f"Completing task: #{args.task_id}")
    
    tasks = load_json(TASKS_FILE)
    
    for task in tasks.get('tasks', []):
        if task.get('id') == int(args.task_id):
            task['status'] = 'completed'
            task['completed_at'] = datetime.now().isoformat()
            save_json(TASKS_FILE, tasks)
            print(f"✅ Task #{args.task_id} marked as completed!")
            return 0
    
    print(f"❌ Task #{args.task_id} not found.")
    return 1


def cmd_add_process(args) -> int:
    """Add a new process."""
    logger.info(f"Adding process: {args.name}")
    
    processes = load_json(PROCESSES_FILE)
    
    process = {
        "id": str(uuid.uuid4())[:8],
        "name": args.name,
        "description": args.description or "",
        "status": args.status or "idle",
        "steps": [],
        "created_at": datetime.now().isoformat(),
        "last_run": None
    }
    
    processes['processes'].append(process)
    save_json(PROCESSES_FILE, processes)
    
    print(f"✅ Process added: {args.name} (ID: {process['id']})")
    return 0


def cmd_run_process(args) -> int:
    """Run a process."""
    logger.info(f"Running process: {args.process_id}")
    
    processes = load_json(PROCESSES_FILE)
    
    for process in processes.get('processes', []):
        if process.get('id') == args.process_id:
            process['status'] = 'running'
            process['last_run'] = datetime.now().isoformat()
            save_json(PROCESSES_FILE, processes)
            print(f"🚀 Process {args.process_id} started...")
            return 0
    
    print(f"❌ Process {args.process_id} not found.")
    return 1


def cmd_add_resource(args) -> int:
    """Add a resource tracking entry."""
    logger.info(f"Adding resource: {args.name}")
    
    resources = load_json(RESOURCES_FILE)
    
    resource = {
        "id": str(uuid.uuid4())[:8],
        "name": args.name,
        "type": args.type or "general",
        "status": args.resource_status or "available",
        "quantity": int(args.quantity) if args.quantity else 1,
        "notes": args.notes or "",
        "created_at": datetime.now().isoformat()
    }
    
    resources['resources'].append(resource)
    save_json(RESOURCES_FILE, resources)
    
    print(f"✅ Resource added: {args.name}")
    return 0


def cmd_list_resources(args) -> int:
    """List all resources."""
    logger.info("Listing resources...")
    
    resources = load_json(RESOURCES_FILE)
    all_resources = resources.get('resources', [])
    
    if args.type:
        all_resources = [r for r in all_resources if r.get('type') == args.type]
    
    print(f"\n👥 Resources ({len(all_resources)} found):")
    print("-"*60)
    for r in all_resources:
        status_icon = {"available": "🟢", "in_use": "🟡", "unavailable": "🔴"}.get(
            r.get('status', 'available'), "⚪")
        print(f"   {status_icon} {r.get('name')} | Type: {r.get('type')} | Qty: {r.get('quantity')}")
    
    return 0


def cmd_add_workflow(args) -> int:
    """Add a workflow."""
    logger.info(f"Adding workflow: {args.name}")
    
    workflows = load_json(WORKFLOWS_FILE)
    
    workflow = {
        "id": str(uuid.uuid4())[:8],
        "name": args.name,
        "description": args.description or "",
        "trigger": args.trigger or "manual",
        "steps": args.steps.split(',') if args.steps else [],
        "status": "inactive",
        "created_at": datetime.now().isoformat(),
        "last_triggered": None
    }
    
    workflows['workflows'].append(workflow)
    save_json(WORKFLOWS_FILE, workflows)
    
    print(f"✅ Workflow added: {args.name}")
    return 0


def cmd_trigger_workflow(args) -> int:
    """Trigger a workflow."""
    logger.info(f"Triggering workflow: {args.workflow_id}")
    
    workflows = load_json(WORKFLOWS_FILE)
    
    for wf in workflows.get('workflows', []):
        if wf.get('id') == args.workflow_id:
            wf['status'] = 'active'
            wf['last_triggered'] = datetime.now().isoformat()
            save_json(WORKFLOWS_FILE, workflows)
            print(f"🚀 Workflow {args.workflow_id} triggered!")
            return 0
    
    print(f"❌ Workflow {args.workflow_id} not found.")
    return 1


def cmd_metrics(args) -> int:
    """Show operational metrics."""
    logger.info("Calculating operational metrics...")
    
    tasks = load_json(TASKS_FILE)
    processes = load_json(PROCESSES_FILE)
    resources = load_json(RESOURCES_FILE)
    workflows = load_json(WORKFLOWS_FILE)
    
    all_tasks = tasks.get('tasks', [])
    
    # Calculate metrics
    total_tasks = len(all_tasks)
    completed = len([t for t in all_tasks if t.get('status') == 'completed'])
    in_progress = len([t for t in all_tasks if t.get('status') == 'in_progress'])
    pending = len([t for t in all_tasks if t.get('status') == 'pending'])
    
    completion_rate = (completed / total_tasks * 100) if total_tasks > 0 else 0
    
    # Calculate today's throughput
    today = datetime.now().strftime('%Y-%m-%d')
    completed_today = len([t for t in all_tasks 
                          if t.get('status') == 'completed' 
                          and t.get('completed_at', '').startswith(today)])
    
    print("\n" + "="*60)
    print("📊 OPERATIONAL METRICS")
    print("="*60)
    print(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("-"*60)
    
    print("\n📋 TASK METRICS")
    print(f"   Total Tasks:      {total_tasks}")
    print(f"   Completed:        {completed} ({completion_rate:.1f}%)")
    print(f"   In Progress:      {in_progress}")
    print(f"   Pending:          {pending}")
    print(f"   Throughput Today: {completed_today} tasks")
    
    print("\n🔄 PROCESS METRICS")
    running = len([p for p in processes.get('processes', []) if p.get('status') == 'running'])
    print(f"   Total Processes:  {len(processes.get('processes', []))}")
    print(f"   Running:          {running}")
    
    print("\n👥 RESOURCE METRICS")
    available = len([r for r in resources.get('resources', []) if r.get('status') == 'available'])
    in_use = len([r for r in resources.get('resources', []) if r.get('status') == 'in_use'])
    print(f"   Total Resources:  {len(resources.get('resources', []))}")
    print(f"   Available:        {available}")
    print(f"   In Use:           {in_use}")
    
    print("\n🚀 WORKFLOW METRICS")
    active_wf = len([w for w in workflows.get('workflows', []) if w.get('status') == 'active'])
    print(f"   Total Workflows:  {len(workflows.get('workflows', []))}")
    print(f"   Active:           {active_wf}")
    
    print("\n" + "="*60)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="⚙️ COO Operations Agent - Workflow & Task Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status                    Show operational status
  %(prog)s add-task --title "Deploy v2" --priority high --category dev
  %(prog)s list-tasks --status pending
  %(prog)s complete-task --task-id 1
  %(prog)s add-process --name "Backup" --description "Daily backup"
  %(prog)s add-resource --name "Server 1" --type server
  %(prog)s add-workflow --name "Daily Report" --trigger schedule
  %(prog)s metrics                   Show operational metrics
        """
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    subparsers.add_parser('status', help='Show operational status overview')
    
    # Task commands
    task_parser = subparsers.add_parser('add-task', help='Add a new task')
    task_parser.add_argument('--title', required=True, help='Task title')
    task_parser.add_argument('--description', help='Task description')
    task_parser.add_argument('--priority', default='medium', choices=['low', 'medium', 'high', 'urgent'])
    task_parser.add_argument('--category', help='Task category')
    task_parser.add_argument('--due-date', help='Due date (YYYY-MM-DD)')
    task_parser.add_argument('--assignee', help='Assignee name')
    
    list_parser = subparsers.add_parser('list-tasks', help='List tasks')
    list_parser.add_argument('--status', choices=['pending', 'in_progress', 'completed', 'blocked'])
    list_parser.add_argument('--category', help='Filter by category')
    list_parser.add_argument('--priority', choices=['low', 'medium', 'high', 'urgent'])
    
    complete_parser = subparsers.add_parser('complete-task', help='Mark task as completed')
    complete_parser.add_argument('--task-id', required=True, help='Task ID to complete')
    
    # Process commands
    proc_parser = subparsers.add_parser('add-process', help='Add a new process')
    proc_parser.add_argument('--name', required=True, help='Process name')
    proc_parser.add_argument('--description', help='Process description')
    proc_parser.add_argument('--status', default='idle', choices=['idle', 'running', 'paused', 'stopped'])
    
    run_parser = subparsers.add_parser('run-process', help='Run a process')
    run_parser.add_argument('--process-id', required=True, help='Process ID to run')
    
    # Resource commands
    res_parser = subparsers.add_parser('add-resource', help='Add a resource')
    res_parser.add_argument('--name', required=True, help='Resource name')
    res_parser.add_argument('--type', help='Resource type (server, tool, service)')
    res_parser.add_argument('--status', default='available', choices=['available', 'in_use', 'unavailable'])
    res_parser.add_argument('--quantity', help='Quantity')
    res_parser.add_argument('--notes', help='Notes')
    
    list_res_parser = subparsers.add_parser('list-resources', help='List resources')
    list_res_parser.add_argument('--type', help='Filter by type')
    
    # Workflow commands
    wf_parser = subparsers.add_parser('add-workflow', help='Add a workflow')
    wf_parser.add_argument('--name', required=True, help='Workflow name')
    wf_parser.add_argument('--description', help='Workflow description')
    wf_parser.add_argument('--trigger', default='manual', help='Trigger type')
    wf_parser.add_argument('--steps', help='Comma-separated steps')
    
    trigger_parser = subparsers.add_parser('trigger-workflow', help='Trigger a workflow')
    trigger_parser.add_argument('--workflow-id', required=True, help='Workflow ID')
    
    # Metrics command
    subparsers.add_parser('metrics', help='Show operational metrics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize data files
    init_data_files()
    
    # Route to command handler
    commands = {
        'status': cmd_status,
        'add-task': cmd_add_task,
        'list-tasks': cmd_list_tasks,
        'complete-task': cmd_complete_task,
        'add-process': cmd_add_process,
        'run-process': cmd_run_process,
        'add-resource': cmd_add_resource,
        'list-resources': cmd_list_resources,
        'add-workflow': cmd_add_workflow,
        'trigger-workflow': cmd_trigger_workflow,
        'metrics': cmd_metrics
    }
    
    try:
        return commands[args.command](args)
    except Exception as e:
        logger.error(f"Command failed: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
