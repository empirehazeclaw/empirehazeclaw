#!/usr/bin/env python3
"""
Workflow Builder Agent - Productivity Suite
Build, manage, and execute automated workflows.

Inspired by SOUL.md: CEO mindset, Eigenverantwortung, Geschwindigkeit über Perfektion
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# ─── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
WORKSPACE = SCRIPT_DIR.parent.parent.parent
LOG_DIR = WORKSPACE / "logs"
DATA_DIR = WORKSPACE / "data" / "workflow_builder"
WORKFLOWS_FILE = DATA_DIR / "workflows.json"
TEMPLATES_FILE = DATA_DIR / "templates.json"
EXECUTIONS_FILE = DATA_DIR / "executions.json"
CONFIG_FILE = DATA_DIR / "config.json"

# Ensure directories
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [WORKFLOW] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "workflow_builder.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("WorkflowBuilder")


# ─── Data Helpers ─────────────────────────────────────────────────────────────
def load_json(path: Path, default: dict) -> dict:
    """Load JSON, return default if missing or invalid."""
    if not path.exists():
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        log.error(f"Failed to load {path}: {e}")
        return default


def save_json(path: Path, data: dict) -> None:
    """Save data to JSON file."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        log.error(f"Failed to save {path}: {e}")
        raise


def load_workflows() -> dict:
    """Load workflows database."""
    return load_json(WORKFLOWS_FILE, {"workflows": [], "last_updated": None})


def save_workflows(data: dict) -> None:
    """Save workflows database."""
    data["last_updated"] = datetime.utcnow().isoformat()
    save_json(WORKFLOWS_FILE, data)


def load_templates() -> dict:
    """Load workflow templates."""
    defaults = {
        "templates": [
            {
                "id": 1,
                "name": "Content Publishing Pipeline",
                "description": "Generate content, review, and publish across platforms",
                "steps": [
                    {"name": "generate_content", "type": "agent", "config": {"agent": "content_automation", "action": "generate"}},
                    {"name": "review", "type": "approval", "config": {}},
                    {"name": "publish_twitter", "type": "agent", "config": {"agent": "social_automation", "action": "post"}},
                    {"name": "publish_linkedin", "type": "agent", "config": {"agent": "social_automation", "action": "post"}},
                ],
                "estimated_duration_minutes": 30,
            },
            {
                "id": 2,
                "name": "Morning Briefing",
                "description": "Generate morning briefing with metrics and schedule",
                "steps": [
                    {"name": "collect_metrics", "type": "agent", "config": {"agent": "analytics_automation", "action": "collect"}},
                    {"name": "generate_report", "type": "agent", "config": {"agent": "analytics_automation", "action": "report"}},
                    {"name": "send_briefing", "type": "notification", "config": {"channel": "telegram"}},
                ],
                "estimated_duration_minutes": 10,
            },
            {
                "id": 3,
                "name": "Lead Nurturing Sequence",
                "description": "Follow up with leads at various stages",
                "steps": [
                    {"name": "fetch_leads", "type": "agent", "config": {"agent": "lead_intelligence", "action": "fetch"}},
                    {"name": "score_leads", "type": "agent", "config": {"agent": "lead_intelligence", "action": "score"}},
                    {"name": "send_sequence", "type": "agent", "config": {"agent": "email_sequence", "action": "send"}},
                ],
                "estimated_duration_minutes": 45,
            },
        ],
        "last_updated": None,
    }
    return load_json(TEMPLATES_FILE, defaults)


def save_templates(data: dict) -> None:
    """Save templates."""
    data["last_updated"] = datetime.utcnow().isoformat()
    save_json(TEMPLATES_FILE, data)


def load_executions() -> dict:
    """Load execution history."""
    return load_json(EXECUTIONS_FILE, {"executions": [], "last_updated": None})


def save_executions(data: dict) -> None:
    """Save execution history."""
    data["last_updated"] = datetime.utcnow().isoformat()
    save_json(EXECUTIONS_FILE, data)


def load_config() -> dict:
    """Load configuration."""
    defaults = {
        "default_timeout_minutes": 60,
        "max_parallel_steps": 3,
        "retry_on_failure": True,
        "max_retries": 2,
        "notification_enabled": True,
    }
    return load_json(CONFIG_FILE, defaults)


def generate_id(items: list) -> int:
    """Generate next ID."""
    return max((i.get("id", 0) for i in items), default=0) + 1


# ─── Workflow Execution ─────────────────────────────────────────────────────────
def execute_step(step: dict) -> dict:
    """Execute a single workflow step (simulated)."""
    step_name = step.get("name", "unknown")
    step_type = step.get("type", "unknown")
    
    log.info(f"Executing step: {step_name} ({step_type})")
    
    # Simulate step execution
    import random
    success = random.random() > 0.1  # 90% success rate
    
    return {
        "step": step_name,
        "type": step_type,
        "success": success,
        "output": f"Step '{step_name}' completed" if success else f"Step '{step_name}' failed",
        "duration_ms": random.randint(500, 5000),
        "executed_at": datetime.utcnow().isoformat(),
    }


def execute_workflow(workflow: dict, args: dict = None) -> dict:
    """Execute a complete workflow."""
    workflow_id = workflow.get("id")
    workflow_name = workflow.get("name")
    steps = workflow.get("steps", [])
    
    log.info(f"Starting workflow #{workflow_id}: {workflow_name}")
    
    start_time = datetime.utcnow()
    step_results = []
    overall_success = True
    
    for i, step in enumerate(steps):
        log.info(f"Step {i+1}/{len(steps)}: {step.get('name')}")
        
        result = execute_step(step)
        step_results.append(result)
        
        if not result["success"]:
            overall_success = False
            log.error(f"Step '{step.get('name')}' failed, stopping workflow")
            break
    
    end_time = datetime.utcnow()
    duration_ms = int((end_time - start_time).total_seconds() * 1000)
    
    return {
        "workflow_id": workflow_id,
        "workflow_name": workflow_name,
        "success": overall_success,
        "duration_ms": duration_ms,
        "steps_completed": len(step_results),
        "steps_total": len(steps),
        "step_results": step_results,
        "started_at": start_time.isoformat(),
        "completed_at": end_time.isoformat(),
        "context": args or {},
    }


# ─── Commands ─────────────────────────────────────────────────────────────────
def cmd_list(args) -> None:
    """List all workflows."""
    data = load_workflows()
    workflows = data.get("workflows", [])
    
    if not workflows:
        print("📋 No workflows found. Create one or use a template.")
        return
    
    status_filter = args.status
    filtered = workflows
    if status_filter:
        filtered = [w for w in filtered if w.get("status") == status_filter]
    
    print(f"📋 Workflows ({len(filtered)} of {len(workflows)}):")
    print("-" * 70)
    
    for w in sorted(filtered, key=lambda x: x.get("updated_at", ""), reverse=True):
        status = w.get("status", "draft")
        status_icon = {"active": "🟢", "draft": "📝", "paused": "⏸️"}.get(status, "⚪")
        print(f"  #{w['id']} | {status_icon} {status:8} | {w['name'][:30]}")
        print(f"        Steps: {len(w.get('steps', []))} | Last run: {w.get('last_run', 'Never')[:10] if w.get('last_run') else 'Never'}")


def cmd_create(args) -> None:
    """Create a new workflow."""
    workflows_data = load_workflows()
    
    # Parse steps from JSON string
    try:
        steps = json.loads(args.steps) if args.steps else []
    except json.JSONDecodeError as e:
        print(f"❌ Invalid steps JSON: {e}")
        return
    
    workflow = {
        "id": generate_id(workflows_data.get("workflows", [])),
        "name": args.name,
        "description": args.description or "",
        "steps": steps,
        "status": "draft",
        "variables": {},
        "triggers": [],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "last_run": None,
        "run_count": 0,
    }
    
    workflows_data["workflows"].append(workflow)
    save_workflows(workflows_data)
    
    print(f"✅ Created workflow #{workflow['id']}: {workflow['name']}")
    print(f"   Steps: {len(steps)}")


def cmd_view(args) -> None:
    """View workflow details."""
    data = load_workflows()
    for w in data.get("workflows", []):
        if w["id"] == args.id:
            print(f"\n📋 Workflow #{w['id']}: {w['name']}")
            print("=" * 60)
            print(f"Description: {w.get('description', 'N/A')}")
            print(f"Status:      {w.get('status', 'N/A')}")
            print(f"Steps:       {len(w.get('steps', []))}")
            print(f"Created:    {w.get('created_at', 'N/A')}")
            print(f"Updated:    {w.get('updated_at', 'N/A')}")
            print(f"Last Run:   {w.get('last_run', 'N/A')}")
            print(f"Run Count:  {w.get('run_count', 0)}")
            
            if w.get("steps"):
                print(f"\nSteps:")
                for i, step in enumerate(w["steps"], 1):
                    print(f"  {i}. {step.get('name')} ({step.get('type')})")
            
            if w.get("triggers"):
                print(f"\nTriggers:")
                for t in w["triggers"]:
                    print(f"  - {t}")
            
            if w.get("variables"):
                print(f"\nVariables:")
                for k, v in w["variables"].items():
                    print(f"  {k}: {v}")
            return
    
    print(f"❌ Workflow #{args.id} not found.")


def cmd_run(args) -> None:
    """Execute a workflow."""
    workflows_data = load_workflows()
    workflow = None
    
    for w in workflows_data.get("workflows", []):
        if w["id"] == args.id:
            workflow = w
            break
    
    if not workflow:
        print(f"❌ Workflow #{args.id} not found.")
        return
    
    if workflow.get("status") != "active":
        print(f"⚠️ Workflow is not active (status: {workflow.get('status')})")
        if not args.force:
            return
    
    log.info(f"Running workflow #{workflow['id']}: {workflow['name']}")
    print(f"▶️  Running workflow: {workflow['name']}")
    print(f"   Steps: {len(workflow.get('steps', []))}")
    
    # Parse context args if provided
    context = {}
    if args.context:
        try:
            context = json.loads(args.context)
        except json.JSONDecodeError:
            print("⚠️ Invalid context JSON, continuing without context")
    
    result = execute_workflow(workflow, context)
    
    # Save execution record
    executions_data = load_executions()
    exec_record = {
        "id": generate_id(executions_data.get("executions", [])),
        "workflow_id": workflow["id"],
        "workflow_name": workflow["name"],
        "success": result["success"],
        "duration_ms": result["duration_ms"],
        "steps_completed": result["steps_completed"],
        "started_at": result["started_at"],
        "completed_at": result["completed_at"],
    }
    executions_data["executions"].append(exec_record)
    save_executions(executions_data)
    
    # Update workflow
    for w in workflows_data.get("workflows", []):
        if w["id"] == workflow["id"]:
            w["last_run"] = datetime.utcnow().isoformat()
            w["run_count"] = w.get("run_count", 0) + 1
            break
    save_workflows(workflows_data)
    
    # Print results
    print(f"\n{'✅' if result['success'] else '❌'} Workflow {'completed successfully' if result['success'] else 'failed'}")
    print(f"   Duration: {result['duration_ms']}ms")
    print(f"   Steps: {result['steps_completed']}/{result['steps_total']}")
    
    if not result["success"]:
        for sr in result.get("step_results", []):
            if not sr.get("success"):
                print(f"   Failed step: {sr.get('step')} - {sr.get('output')}")


def cmd_update(args) -> None:
    """Update workflow properties."""
    workflows_data = load_workflows()
    
    for w in workflows_data.get("workflows", []):
        if w["id"] == args.id:
            if args.name:
                w["name"] = args.name
            if args.description:
                w["description"] = args.description
            if args.steps:
                try:
                    w["steps"] = json.loads(args.steps)
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid steps JSON: {e}")
                    return
            
            w["updated_at"] = datetime.utcnow().isoformat()
            save_workflows(workflows_data)
            print(f"✅ Updated workflow #{args.id}")
            return
    
    print(f"❌ Workflow #{args.id} not found.")


def cmd_activate(args) -> None:
    """Activate a workflow."""
    workflows_data = load_workflows()
    
    for w in workflows_data.get("workflows", []):
        if w["id"] == args.id:
            w["status"] = "active"
            w["updated_at"] = datetime.utcnow().isoformat()
            save_workflows(workflows_data)
            print(f"✅ Activated workflow #{args.id}: {w['name']}")
            return
    
    print(f"❌ Workflow #{args.id} not found.")


def cmd_pause(args) -> None:
    """Pause a workflow."""
    workflows_data = load_workflows()
    
    for w in workflows_data.get("workflows", []):
        if w["id"] == args.id:
            w["status"] = "paused"
            w["updated_at"] = datetime.utcnow().isoformat()
            save_workflows(workflows_data)
            print(f"⏸️  Paused workflow #{args.id}: {w['name']}")
            return
    
    print(f"❌ Workflow #{args.id} not found.")


def cmd_delete(args) -> None:
    """Delete a workflow."""
    workflows_data = load_workflows()
    original_len = len(workflows_data.get("workflows", []))
    workflows_data["workflows"] = [w for w in workflows_data["workflows"] if w["id"] != args.id]
    
    if len(workflows_data["workflows"]) < original_len:
        save_workflows(workflows_data)
        print(f"✅ Deleted workflow #{args.id}")
    else:
        print(f"❌ Workflow #{args.id} not found.")


def cmd_templates(args) -> None:
    """List workflow templates."""
    data = load_templates()
    templates = data.get("templates", [])
    
    if not templates:
        print("📋 No templates available.")
        return
    
    print(f"📋 Workflow Templates ({len(templates)}):")
    print("-" * 70)
    
    for t in templates:
        print(f"  #{t['id']} | {t['name'][:35]}")
        print(f"        {t.get('description', 'N/A')[:60]}")
        print(f"        Steps: {len(t.get('steps', []))} | Est. Time: {t.get('estimated_duration_minutes', '?')}min")


def cmd_template_use(args) -> None:
    """Create workflow from template."""
    templates_data = load_templates()
    template = None
    
    for t in templates_data.get("templates", []):
        if t["id"] == args.template_id:
            template = t
            break
    
    if not template:
        print(f"❌ Template #{args.template_id} not found.")
        return
    
    workflows_data = load_workflows()
    
    workflow = {
        "id": generate_id(workflows_data.get("workflows", [])),
        "name": args.name or template["name"],
        "description": template.get("description", ""),
        "steps": template.get("steps", []),
        "status": "draft",
        "variables": {},
        "triggers": [],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "last_run": None,
        "run_count": 0,
    }
    
    workflows_data["workflows"].append(workflow)
    save_workflows(workflows_data)
    
    print(f"✅ Created workflow #{workflow['id']} from template '{template['name']}'")
    print(f"   Steps: {len(workflow['steps'])}")


def cmd_history(args) -> None:
    """Show workflow execution history."""
    data = load_executions()
    executions = data.get("executions", [])
    
    if not executions:
        print("📋 No execution history.")
        return
    
    workflow_filter = args.workflow_id
    if workflow_filter:
        executions = [e for e in executions if e.get("workflow_id") == workflow_filter]
    
    limit = args.limit
    filtered = executions[-limit:] if limit else executions
    
    print(f"📋 Execution History ({len(filtered)} recent):")
    print("-" * 70)
    
    for e in sorted(filtered, key=lambda x: x.get("started_at", ""), reverse=True):
        status = "✅" if e.get("success") else "❌"
        print(f"  #{e['id']} | {status} | WF#{e.get('workflow_id')}: {e.get('workflow_name', 'unknown')[:25]}")
        print(f"        Duration: {e.get('duration_ms', 0)}ms | Steps: {e.get('steps_completed', '?')} | {e.get('started_at', '')[:19]}")


def cmd_stats(args) -> None:
    """Show workflow statistics."""
    workflows_data = load_workflows()
    executions_data = load_executions()
    
    workflows = workflows_data.get("workflows", [])
    executions = executions_data.get("executions", [])
    
    active = sum(1 for w in workflows if w.get("status") == "active")
    total_runs = len(executions)
    successful = sum(1 for e in executions if e.get("success"))
    
    print("\n📊 Workflow Statistics")
    print("=" * 50)
    print(f"Total Workflows: {len(workflows)}")
    print(f"Active Workflows: {active}")
    print(f"Total Runs: {total_runs}")
    print(f"Successful Runs: {successful}")
    print(f"Success Rate: {(successful/total_runs*100) if total_runs > 0 else 0:.1f}%")


def cmd_config(args) -> None:
    """Show configuration."""
    config = load_config()
    print("\n⚙️ Workflow Builder Config")
    print("=" * 50)
    for key, value in config.items():
        print(f"  {key}: {value}")


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Workflow Builder Agent - Productivity Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list
  %(prog)s list --status active
  %(prog)s create --name "My Workflow" --steps '[{"name":"step1","type":"agent"}]'
  %(prog)s view --id 1
  %(prog)s run --id 1
  %(prog)s run --id 1 --context '{"key":"value"}'
  %(prog)s update --id 1 --name "New Name"
  %(prog)s activate --id 1
  %(prog)s pause --id 1
  %(prog)s delete --id 1
  %(prog)s templates
  %(prog)s template-use --template-id 1 --name "My Morning Flow"
  %(prog)s history
  %(prog)s history --workflow-id 1 --limit 10
  %(prog)s stats
  %(prog)s config
        """,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List
    p_list = subparsers.add_parser("list", help="List workflows")
    p_list.add_argument("--status", "-s", default=None, help="Filter by status")
    
    # Create
    p_create = subparsers.add_parser("create", help="Create a new workflow")
    p_create.add_argument("--name", "-n", required=True, help="Workflow name")
    p_create.add_argument("--description", "-d", default=None, help="Description")
    p_create.add_argument("--steps", "-s", default=None, help="Steps JSON array")
    
    # View
    p_view = subparsers.add_parser("view", help="View workflow details")
    p_view.add_argument("--id", "-i", type=int, required=True, help="Workflow ID")
    
    # Run
    p_run = subparsers.add_parser("run", help="Execute a workflow")
    p_run.add_argument("--id", "-i", type=int, required=True, help="Workflow ID")
    p_run.add_argument("--context", "-c", default=None, help="Context JSON")
    p_run.add_argument("--force", "-f", action="store_true", help="Run even if not active")
    
    # Update
    p_update = subparsers.add_parser("update", help="Update workflow")
    p_update.add_argument("--id", "-i", type=int, required=True, help="Workflow ID")
    p_update.add_argument("--name", "-n", default=None, help="New name")
    p_update.add_argument("--description", "-d", default=None, help="New description")
    p_update.add_argument("--steps", "-s", default=None, help="New steps JSON")
    
    # Activate
    p_activate = subparsers.add_parser("activate", help="Activate a workflow")
    p_activate.add_argument("--id", "-i", type=int, required=True, help="Workflow ID")
    
    # Pause
    p_pause = subparsers.add_parser("pause", help="Pause a workflow")
    p_pause.add_argument("--id", "-i", type=int, required=True, help="Workflow ID")
    
    # Delete
    p_delete = subparsers.add_parser("delete", help="Delete a workflow")
    p_delete.add_argument("--id", "-i", type=int, required=True, help="Workflow ID")
    
    # Templates
    subparsers.add_parser("templates", help="List workflow templates")
    
    # Template Use
    p_use = subparsers.add_parser("template-use", help="Create workflow from template")
    p_use.add_argument("--template-id", "-t", type=int, required=True, help="Template ID")
    p_use.add_argument("--name", "-n", default=None, help="Workflow name (default: template name)")
    
    # History
    p_history = subparsers.add_parser("history", help="Show execution history")
    p_history.add_argument("--workflow-id", "-w", type=int, default=None, help="Filter by workflow")
    p_history.add_argument("--limit", "-l", type=int, default=None, help="Limit results")
    
    # Stats
    subparsers.add_parser("stats", help="Show statistics")
    
    # Config
    subparsers.add_parser("config", help="Show configuration")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "list":
            cmd_list(args)
        elif args.command == "create":
            cmd_create(args)
        elif args.command == "view":
            cmd_view(args)
        elif args.command == "run":
            cmd_run(args)
        elif args.command == "update":
            cmd_update(args)
        elif args.command == "activate":
            cmd_activate(args)
        elif args.command == "pause":
            cmd_pause(args)
        elif args.command == "delete":
            cmd_delete(args)
        elif args.command == "templates":
            cmd_templates(args)
        elif args.command == "template-use":
            cmd_template_use(args)
        elif args.command == "history":
            cmd_history(args)
        elif args.command == "stats":
            cmd_stats(args)
        elif args.command == "config":
            cmd_config(args)
    except Exception as e:
        log.error(f"Command '{args.command}' failed: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
