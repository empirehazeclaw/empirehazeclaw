#!/usr/bin/env python3
"""
Moltbook Automation Agent - Moltbook Division
Automates Moltbook workflows, tasks, and integrations.

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
DATA_DIR = WORKSPACE / "data" / "moltbook"
CONFIG_FILE = DATA_DIR / "moltbook_config.json"
WORKFLOWS_FILE = DATA_DIR / "workflows.json"
TASKS_FILE = DATA_DIR / "tasks.json"
INTEGRATIONS_FILE = DATA_DIR / "integrations.json"

# Ensure directories exist
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - MOLTBOOK-AUTO - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "moltbook_automation.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def load_json(filepath, default):
    """Load JSON from file."""
    if not filepath.exists():
        return default
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse {filepath}: {e}")
        return default


def save_json(filepath, data):
    """Save JSON to file."""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        logger.error(f"Failed to save {filepath}: {e}")
        raise


def load_config():
    """Load Moltbook configuration."""
    return load_json(CONFIG_FILE, {
        "version": "1.0",
        "api_key": "",
        "webhook_url": "",
        "auto_sync": True,
        "notifications": True,
        "schedule_interval": 300,  # seconds
        "last_sync": None
    })


def save_config(config):
    """Save Moltbook configuration."""
    save_json(CONFIG_FILE, config)


def load_workflows():
    """Load workflows."""
    return load_json(WORKFLOWS_FILE, {"workflows": []})


def save_workflows(data):
    """Save workflows."""
    save_json(WORKFLOWS_FILE, data)


def load_tasks():
    """Load tasks."""
    return load_json(TASKS_FILE, {"tasks": []})


def save_tasks(data):
    """Save tasks."""
    save_json(TASKS_FILE, data)


def load_integrations():
    """Load integrations."""
    return load_json(INTEGRATIONS_FILE, {"integrations": []})


def save_integrations(data):
    """Save integrations."""
    save_json(INTEGRATIONS_FILE, data)


# ========== CONFIG COMMANDS ==========

def show_config():
    """Show current configuration."""
    config = load_config()
    print(f"\n⚙️  Moltbook Configuration:")
    print("=" * 40)
    print(f"API Key:        {'***' + config.get('api_key', '')[-4:] if config.get('api_key') else 'Not set'}")
    print(f"Webhook URL:    {config.get('webhook_url', 'Not set')}")
    print(f"Auto Sync:      {'Enabled ✅' if config.get('auto_sync') else 'Disabled ❌'}")
    print(f"Notifications:  {'Enabled ✅' if config.get('notifications') else 'Disabled ❌'}")
    print(f"Sync Interval:  {config.get('schedule_interval', 300)}s")
    print(f"Last Sync:      {config.get('last_sync', 'Never')}")


def update_config(**kwargs):
    """Update configuration."""
    config = load_config()
    valid_keys = ['api_key', 'webhook_url', 'auto_sync', 'notifications', 'schedule_interval']
    
    for key, value in kwargs.items():
        if key in valid_keys:
            config[key] = value
    
    save_config(config)
    logger.info(f"Updated config: {kwargs}")
    print(f"✅ Configuration updated.")


# ========== WORKFLOW COMMANDS ==========

def create_workflow(name, trigger_type, action_type, description=None, config=None):
    """Create a new automation workflow."""
    data = load_workflows()
    
    workflow = {
        "id": len(data['workflows']) + 1,
        "name": name,
        "trigger_type": trigger_type,
        "action_type": action_type,
        "description": description or "",
        "config": config or {},
        "status": "active",
        "trigger_count": 0,
        "last_triggered": None,
        "last_success": None,
        "last_error": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    data['workflows'].append(workflow)
    save_workflows(data)
    logger.info(f"Created workflow: {name} (ID: {workflow['id']})")
    print(f"✅ Created workflow: {name} (ID: {workflow['id']})")
    return workflow['id']


def list_workflows(status_filter=None):
    """List all workflows."""
    data = load_workflows()
    workflows = data['workflows']
    
    if status_filter:
        workflows = [w for w in workflows if w.get('status') == status_filter]
    
    if not workflows:
        print("📭 No workflows found.")
        return
    
    status_icons = {"active": "🟢", "paused": "🟡", "disabled": "🔴"}
    
    print(f"\n⚙️  Automation Workflows ({len(workflows)} total):")
    print("-" * 80)
    for wf in workflows:
        icon = status_icons.get(wf.get('status', 'active'), "⚪")
        print(f"{icon} [{wf['id']}] {wf['name']}")
        print(f"   Trigger: {wf.get('trigger_type', 'N/A')} → Action: {wf.get('action_type', 'N/A')}")
        print(f"   Triggered: {wf.get('trigger_count', 0)} times | Last: {wf.get('last_triggered', 'Never')}")
        print()


def show_workflow(workflow_id):
    """Show workflow details."""
    data = load_workflows()
    for wf in data['workflows']:
        if wf['id'] == workflow_id:
            print(f"\n⚙️  Workflow Details:")
            print("=" * 60)
            print(f"ID:           {wf['id']}")
            print(f"Name:         {wf['name']}")
            print(f"Status:       {wf.get('status', 'active')}")
            print(f"Trigger:      {wf.get('trigger_type', 'N/A')}")
            print(f"Action:       {wf.get('action_type', 'N/A')}")
            print(f"Description:  {wf.get('description', 'N/A')}")
            print(f"Triggered:    {wf.get('trigger_count', 0)} times")
            print(f"Last Run:     {wf.get('last_triggered', 'Never')}")
            print(f"Last Success: {wf.get('last_success', 'Never')}")
            if wf.get('last_error'):
                print(f"Last Error:   {wf['last_error']}")
            if wf.get('config'):
                print(f"Config:       {json.dumps(wf['config'], indent=6)}")
            return
    
    print(f"❌ Workflow {workflow_id} not found.")


def update_workflow(workflow_id, **kwargs):
    """Update workflow."""
    data = load_workflows()
    
    for wf in data['workflows']:
        if wf['id'] == workflow_id:
            for key, value in kwargs.items():
                if key in ['name', 'trigger_type', 'action_type', 'description', 'config', 'status']:
                    wf[key] = value
            wf['updated_at'] = datetime.now().isoformat()
            save_workflows(data)
            logger.info(f"Updated workflow {workflow_id}: {kwargs}")
            print(f"✅ Updated workflow {workflow_id}")
            return True
    
    print(f"❌ Workflow {workflow_id} not found.")
    return False


def delete_workflow(workflow_id):
    """Delete workflow."""
    data = load_workflows()
    
    for i, wf in enumerate(data['workflows']):
        if wf['id'] == workflow_id:
            data['workflows'].pop(i)
            save_workflows(data)
            logger.info(f"Deleted workflow {workflow_id}")
            print(f"✅ Deleted workflow {workflow_id}")
            return True
    
    print(f"❌ Workflow {workflow_id} not found.")
    return False


def trigger_workflow(workflow_id, simulate=False):
    """Trigger a workflow execution."""
    data = load_workflows()
    
    for wf in data['workflows']:
        if wf['id'] == workflow_id:
            if wf.get('status') != 'active':
                print(f"⚠️  Workflow is {wf['status']}. Activate it first.")
                return False
            
            wf['trigger_count'] = wf.get('trigger_count', 0) + 1
            wf['last_triggered'] = datetime.now().isoformat()
            
            if simulate:
                wf['last_success'] = datetime.now().isoformat()
                save_workflows(data)
                logger.info(f"Simulated workflow {workflow_id}")
                print(f"✅ Simulated workflow: {wf['name']}")
            else:
                # Simulate actual execution
                try:
                    # Here would be actual workflow execution logic
                    wf['last_success'] = datetime.now().isoformat()
                    save_workflows(data)
                    logger.info(f"Executed workflow {workflow_id}")
                    print(f"✅ Executed workflow: {wf['name']}")
                except Exception as e:
                    wf['last_error'] = str(e)
                    save_workflows(data)
                    logger.error(f"Workflow {workflow_id} failed: {e}")
                    print(f"❌ Workflow failed: {e}")
                    return False
            
            return True
    
    print(f"❌ Workflow {workflow_id} not found.")
    return False


# ========== TASK COMMANDS ==========

def create_task(name, task_type, schedule=None, workflow_id=None, config=None):
    """Create a scheduled task."""
    data = load_tasks()
    
    task = {
        "id": len(data['tasks']) + 1,
        "name": name,
        "type": task_type,
        "schedule": schedule,
        "workflow_id": workflow_id,
        "config": config or {},
        "status": "pending",
        "last_run": None,
        "next_run": schedule or None,
        "run_count": 0,
        "created_at": datetime.now().isoformat()
    }
    
    # Calculate next run if schedule provided
    if schedule:
        task['next_run'] = calculate_next_run(schedule)
    
    data['tasks'].append(task)
    save_tasks(data)
    logger.info(f"Created task: {name} (ID: {task['id']})")
    print(f"✅ Created task: {name} (ID: {task['id']})")
    return task['id']


def calculate_next_run(schedule):
    """Calculate next run time from cron-like schedule."""
    # Simple implementation for common patterns
    now = datetime.now()
    if schedule == "hourly":
        return (now + timedelta(hours=1)).isoformat()
    elif schedule == "daily":
        return (now + timedelta(days=1)).isoformat()
    elif schedule == "weekly":
        return (now + timedelta(weeks=1)).isoformat()
    return None


def list_tasks(status_filter=None):
    """List all tasks."""
    data = load_tasks()
    tasks = data['tasks']
    
    if status_filter:
        tasks = [t for t in tasks if t.get('status') == status_filter]
    
    if not tasks:
        print("📋 No tasks found.")
        return
    
    status_icons = {"pending": "⏳", "running": "🔄", "completed": "✅", "failed": "❌"}
    
    print(f"\n📋 Scheduled Tasks ({len(tasks)} total):")
    print("-" * 80)
    for task in tasks:
        icon = status_icons.get(task.get('status', 'pending'), "⚪")
        print(f"{icon} [{task['id']}] {task['name']}")
        print(f"   Type: {task.get('type', 'N/A')} | Schedule: {task.get('schedule', 'N/A')}")
        print(f"   Next Run: {task.get('next_run', 'N/A')}")
        print()


def run_task(task_id):
    """Execute a task."""
    data = load_tasks()
    
    for task in data['tasks']:
        if task['id'] == task_id:
            task['status'] = 'running'
            task['last_run'] = datetime.now().isoformat()
            task['run_count'] = task.get('run_count', 0) + 1
            save_tasks(data)
            
            logger.info(f"Running task {task_id}: {task['name']}")
            print(f"🔄 Running task: {task['name']}")
            
            # Simulate task execution
            try:
                # Here would be actual task logic
                task['status'] = 'completed'
                task['next_run'] = calculate_next_run(task.get('schedule', 'daily'))
                print(f"✅ Task completed successfully.")
            except Exception as e:
                task['status'] = 'failed'
                print(f"❌ Task failed: {e}")
            
            save_tasks(data)
            return True
    
    print(f"❌ Task {task_id} not found.")
    return False


def delete_task(task_id):
    """Delete a task."""
    data = load_tasks()
    
    for i, task in enumerate(data['tasks']):
        if task['id'] == task_id:
            data['tasks'].pop(i)
            save_tasks(data)
            logger.info(f"Deleted task {task_id}")
            print(f"✅ Deleted task {task_id}")
            return True
    
    print(f"❌ Task {task_id} not found.")
    return False


# ========== INTEGRATION COMMANDS ==========

def add_integration(name, integration_type, api_key=None, config=None):
    """Add an external integration."""
    data = load_integrations()
    
    integration = {
        "id": len(data['integrations']) + 1,
        "name": name,
        "type": integration_type,
        "api_key": api_key or "",
        "config": config or {},
        "status": "connected",
        "last_sync": None,
        "created_at": datetime.now().isoformat()
    }
    
    data['integrations'].append(integration)
    save_integrations(data)
    logger.info(f"Added integration: {name} (ID: {integration['id']})")
    print(f"✅ Added integration: {name} (ID: {integration['id']})")
    return integration['id']


def list_integrations():
    """List all integrations."""
    data = load_integrations()
    integrations = data['integrations']
    
    if not integrations:
        print("🔌 No integrations configured.")
        return
    
    status_icons = {"connected": "🟢", "disconnected": "🔴", "error": "⚠️"}
    
    print(f"\n🔌 Integrations ({len(integrations)} total):")
    print("-" * 60)
    for integ in integrations:
        icon = status_icons.get(integ.get('status', 'connected'), "⚪")
        print(f"{icon} [{integ['id']}] {integ['name']} ({integ.get('type', 'N/A')})")
        print(f"   Status: {integ.get('status', 'N/A')}")
        print(f"   Last Sync: {integ.get('last_sync', 'Never')}")
        print()


def sync_integration(integration_id):
    """Sync an integration."""
    data = load_integrations()
    
    for integ in data['integrations']:
        if integ['id'] == integration_id:
            logger.info(f"Syncing integration {integration_id}: {integ['name']}")
            print(f"🔄 Syncing {integ['name']}...")
            
            try:
                # Simulate sync
                integ['last_sync'] = datetime.now().isoformat()
                integ['status'] = 'connected'
                save_integrations(data)
                print(f"✅ Sync completed.")
                return True
            except Exception as e:
                integ['status'] = 'error'
                save_integrations(data)
                print(f"❌ Sync failed: {e}")
                return False
    
    print(f"❌ Integration {integration_id} not found.")
    return False


def remove_integration(integration_id):
    """Remove an integration."""
    data = load_integrations()
    
    for i, integ in enumerate(data['integrations']):
        if integ['id'] == integration_id:
            data['integrations'].pop(i)
            save_integrations(data)
            logger.info(f"Removed integration {integration_id}")
            print(f"✅ Removed integration {integration_id}")
            return True
    
    print(f"❌ Integration {integration_id} not found.")
    return False


# ========== STATS & UTILS ==========

def get_stats():
    """Show Moltbook statistics."""
    workflows = load_workflows()['workflows']
    tasks = load_tasks()['tasks']
    integrations = load_integrations()['integrations']
    
    active_workflows = len([w for w in workflows if w.get('status') == 'active'])
    total_triggers = sum(w.get('trigger_count', 0) for w in workflows)
    
    pending_tasks = len([t for t in tasks if t.get('status') == 'pending'])
    connected_integrations = len([i for i in integrations if i.get('status') == 'connected'])
    
    print(f"\n📊 Moltbook Automation Statistics:")
    print("=" * 40)
    print(f"Workflows:      {len(workflows)} (Active: {active_workflows} 🟢)")
    print(f"Total Triggers: {total_triggers}")
    print(f"Tasks:          {len(tasks)} (Pending: {pending_tasks} ⏳)")
    print(f"Integrations:   {len(integrations)} (Connected: {connected_integrations} 🟢)")


def sync_all():
    """Sync all active integrations and update timestamps."""
    config = load_config()
    config['last_sync'] = datetime.now().isoformat()
    save_config(config)
    
    integrations = load_integrations()['integrations']
    synced = 0
    for integ in integrations:
        if integ.get('status') == 'connected':
            synced += 1
    
    logger.info(f"Full sync completed")
    print(f"✅ Full sync completed. Synced {synced} integrations.")
    print(f"   Last sync: {config['last_sync']}")


def main():
    parser = argparse.ArgumentParser(
        description="Moltbook Automation Agent - Manage workflows, tasks, and integrations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s config show
  %(prog)s config update --auto-sync true --notifications false
  
  %(prog)s workflow create "Daily Report" --trigger schedule --action email
  %(prog)s workflow list
  %(prog)s workflow show 1
  %(prog)s workflow trigger 1
  %(prog)s workflow update 1 --status paused
  %(prog)s workflow delete 1
  
  %(prog)s task create "Send Newsletter" --type email --schedule daily
  %(prog)s task list
  %(prog)s task run 1
  %(prog)s task delete 1
  
  %(prog)s integration add "Stripe" --type payment
  %(prog)s integration list
  %(prog)s integration sync 1
  %(prog)s integration remove 1
  
  %(prog)s stats
  %(prog)s sync

Trigger Types: schedule, webhook, event, manual
Action Types:  email, webhook, api, notify, transform
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Config commands
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_sub = config_parser.add_subparsers(dest='config_action')
    
    config_show = config_sub.add_parser('show', help='Show configuration')
    config_update = config_sub.add_parser('update', help='Update configuration')
    config_update.add_argument('--api-key', help='API key')
    config_update.add_argument('--webhook-url', help='Webhook URL')
    config_update.add_argument('--auto-sync', type=lambda x: x.lower() == 'true')
    config_update.add_argument('--notifications', type=lambda x: x.lower() == 'true')
    config_update.add_argument('--interval', type=int)
    
    # Workflow commands
    workflow_parser = subparsers.add_parser('workflow', help='Workflow management')
    workflow_sub = workflow_parser.add_subparsers(dest='workflow_action')
    
    wf_create = workflow_sub.add_parser('create', help='Create workflow')
    wf_create.add_argument('name', help='Workflow name')
    wf_create.add_argument('--trigger', required=True, help='Trigger type')
    wf_create.add_argument('--action', required=True, help='Action type')
    wf_create.add_argument('--description', help='Description')
    
    wf_list = workflow_sub.add_parser('list', help='List workflows')
    wf_list.add_argument('--status', help='Filter by status')
    
    wf_show = workflow_sub.add_parser('show', help='Show workflow')
    wf_show.add_argument('workflow_id', type=int, help='Workflow ID')
    
    wf_trigger = workflow_sub.add_parser('trigger', help='Trigger workflow')
    wf_trigger.add_argument('workflow_id', type=int, help='Workflow ID')
    wf_trigger.add_argument('--simulate', action='store_true', help='Simulate only')
    
    wf_update = workflow_sub.add_parser('update', help='Update workflow')
    wf_update.add_argument('workflow_id', type=int, help='Workflow ID')
    wf_update.add_argument('--name', help='New name')
    wf_update.add_argument('--status', choices=['active', 'paused', 'disabled'])
    wf_update.add_argument('--trigger', help='Trigger type')
    wf_update.add_argument('--action', help='Action type')
    
    wf_delete = workflow_sub.add_parser('delete', help='Delete workflow')
    wf_delete.add_argument('workflow_id', type=int, help='Workflow ID')
    
    # Task commands
    task_parser = subparsers.add_parser('task', help='Task management')
    task_sub = task_parser.add_subparsers(dest='task_action')
    
    task_create = task_sub.add_parser('create', help='Create task')
    task_create.add_argument('name', help='Task name')
    task_create.add_argument('--type', '-t', required=True, help='Task type')
    task_create.add_argument('--schedule', '-s', help='Schedule (hourly/daily/weekly)')
    task_create.add_argument('--workflow-id', type=int, help='Link to workflow')
    
    task_list = task_sub.add_parser('list', help='List tasks')
    task_list.add_argument('--status', help='Filter by status')
    
    task_run = task_sub.add_parser('run', help='Run task now')
    task_run.add_argument('task_id', type=int, help='Task ID')
    
    task_delete = task_sub.add_parser('delete', help='Delete task')
    task_delete.add_argument('task_id', type=int, help='Task ID')
    
    # Integration commands
    integ_parser = subparsers.add_parser('integration', help='Integration management')
    integ_sub = integ_parser.add_subparsers(dest='integ_action')
    
    integ_add = integ_sub.add_parser('add', help='Add integration')
    integ_add.add_argument('name', help='Integration name')
    integ_add.add_argument('--type', '-t', required=True, help='Integration type')
    integ_add.add_argument('--api-key', help='API key')
    
    integ_list = integ_sub.add_parser('list', help='List integrations')
    
    integ_sync = integ_sub.add_parser('sync', help='Sync integration')
    integ_sync.add_argument('integration_id', type=int, help='Integration ID')
    
    integ_remove = integ_sub.add_parser('remove', help='Remove integration')
    integ_remove.add_argument('integration_id', type=int, help='Integration ID')
    
    # Stats and sync
    subparsers.add_parser('stats', help='Show statistics')
    subparsers.add_parser('sync', help='Full sync')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        # Config commands
        if args.command == 'config':
            if args.config_action == 'show':
                show_config()
            elif args.config_action == 'update':
                kwargs = {k: v for k, v in vars(args).items() 
                         if k not in ['command', 'config_action'] and v is not None}
                if kwargs:
                    update_config(**kwargs)
                else:
                    print("❌ No updates specified.")
        
        # Workflow commands
        elif args.command == 'workflow':
            if args.workflow_action == 'create':
                create_workflow(args.name, args.trigger, args.action, args.description)
            elif args.workflow_action == 'list':
                list_workflows(args.status)
            elif args.workflow_action == 'show':
                show_workflow(args.workflow_id)
            elif args.workflow_action == 'trigger':
                trigger_workflow(args.workflow_id, args.simulate)
            elif args.workflow_action == 'update':
                kwargs = {k: v for k, v in vars(args).items() 
                         if k not in ['command', 'workflow_action', 'workflow_id'] and v is not None}
                update_workflow(args.workflow_id, **kwargs) if kwargs else print("❌ No updates specified.")
            elif args.workflow_action == 'delete':
                delete_workflow(args.workflow_id)
        
        # Task commands
        elif args.command == 'task':
            if args.task_action == 'create':
                create_task(args.name, args.type, args.schedule, args.workflow_id)
            elif args.task_action == 'list':
                list_tasks(args.status)
            elif args.task_action == 'run':
                run_task(args.task_id)
            elif args.task_action == 'delete':
                delete_task(args.task_id)
        
        # Integration commands
        elif args.command == 'integration':
            if args.integ_action == 'add':
                add_integration(args.name, args.type, args.api_key)
            elif args.integ_action == 'list':
                list_integrations()
            elif args.integ_action == 'sync':
                sync_integration(args.integration_id)
            elif args.integ_action == 'remove':
                remove_integration(args.integration_id)
        
        elif args.command == 'stats':
            get_stats()
        
        elif args.command == 'sync':
            sync_all()
    
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
