#!/usr/bin/env python3
"""
Automation Scripts Agent - Productivity Suite
Manages and executes automation scripts for productivity workflows.

Inspired by SOUL.md: CEO mindset, Eigenverantwortung, Geschwindigkeit über Perfektion
"""

import argparse
import json
import logging
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# ─── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
WORKSPACE = SCRIPT_DIR.parent.parent.parent
LOG_DIR = WORKSPACE / "logs"
DATA_DIR = WORKSPACE / "data" / "automation_scripts"
SCRIPTS_DB_FILE = DATA_DIR / "scripts_db.json"
EXECUTIONS_FILE = DATA_DIR / "executions.json"
CONFIG_FILE = DATA_DIR / "config.json"

# Ensure directories
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [AUTO-SCRIPTS] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "automation_scripts.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("AutomationScripts")


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


def load_scripts_db() -> dict:
    """Load scripts database."""
    defaults = {
        "scripts": [
            {
                "id": 1,
                "name": "backup_workspace",
                "description": "Backup workspace data to archive",
                "path": "scripts/backup.sh",
                "type": "shell",
                "category": "infrastructure",
                "enabled": True,
                "last_run": None,
                "avg_duration_ms": 5000,
            },
            {
                "id": 2,
                "name": "cleanup_logs",
                "description": "Clean up old log files",
                "path": "scripts/cleanup_logs.sh",
                "type": "shell",
                "category": "maintenance",
                "enabled": True,
                "last_run": None,
                "avg_duration_ms": 2000,
            },
            {
                "id": 3,
                "name": "sync_memory",
                "description": "Sync memory to persistent storage",
                "path": "scripts/autosync.js",
                "type": "node",
                "category": "infrastructure",
                "enabled": True,
                "last_run": None,
                "avg_duration_ms": 3000,
            },
        ],
        "last_updated": None,
    }
    return load_json(SCRIPTS_DB_FILE, defaults)


def save_scripts_db(data: dict) -> None:
    """Save scripts database."""
    data["last_updated"] = datetime.utcnow().isoformat()
    save_json(SCRIPTS_DB_FILE, data)


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
        "workspace_path": str(WORKSPACE),
        "max_concurrent": 3,
        "execution_timeout": 300,
        "history_retention_days": 30,
        "log_output": True,
    }
    return load_json(CONFIG_FILE, defaults)


def generate_id(items: list) -> int:
    """Generate next ID."""
    return max((i.get("id", 0) for i in items), default=0) + 1


# ─── Script Execution ───────────────────────────────────────────────────────────
def execute_script(script: dict, args: List[str] = None) -> dict:
    """Execute a script and return result."""
    script_path = WORKSPACE / script.get("path", "")
    
    if not script_path.exists():
        return {
            "success": False,
            "error": f"Script not found: {script_path}",
            "duration_ms": 0,
            "output": "",
        }
    
    script_type = script.get("type", "shell")
    start_time = datetime.utcnow()
    
    try:
        if script_type == "shell":
            cmd = ["bash", str(script_path)]
        elif script_type == "node":
            cmd = ["node", str(script_path)]
        elif script_type == "python":
            cmd = ["python3", str(script_path)]
        else:
            cmd = [str(script_path)]
        
        if args:
            cmd.extend(args)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(WORKSPACE),
        )
        
        end_time = datetime.utcnow()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        return {
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "duration_ms": duration_ms,
            "output": result.stdout if result.stdout else result.stderr,
            "error": result.stderr if result.returncode != 0 else None,
            "executed_at": start_time.isoformat(),
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Script execution timed out",
            "duration_ms": 300000,
            "output": "",
            "executed_at": start_time.isoformat(),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "duration_ms": 0,
            "output": "",
            "executed_at": start_time.isoformat(),
        }


# ─── Commands ─────────────────────────────────────────────────────────────────
def cmd_list(args) -> None:
    """List all automation scripts."""
    data = load_scripts_db()
    scripts = data.get("scripts", [])
    
    if not scripts:
        print("📜 No automation scripts registered.")
        return
    
    category_filter = args.category
    status_filter = args.enabled
    
    filtered = scripts
    if category_filter:
        filtered = [s for s in filtered if s.get("category") == category_filter]
    if status_filter is not None:
        filtered = [s for s in filtered if s.get("enabled") == status_filter]
    
    print(f"📜 Automation Scripts ({len(filtered)} of {len(scripts)}):")
    print("-" * 70)
    
    for s in sorted(filtered, key=lambda x: x.get("name", "")):
        status = "✅" if s.get("enabled") else "❌"
        last_run = s.get("last_run", "Never")[:10] if s.get("last_run") else "Never"
        print(f"  #{s['id']} | {status} | {s['name']:20} | {s['category']:12} | {s['type']:6} | Last: {last_run}")


def cmd_run(args) -> None:
    """Execute an automation script."""
    scripts_data = load_scripts_db()
    script = None
    
    for s in scripts_data.get("scripts", []):
        if s["id"] == args.id:
            script = s
            break
    
    if not script:
        print(f"❌ Script #{args.id} not found.")
        return
    
    if not script.get("enabled", True):
        print(f"⚠️ Script '{script['name']}' is disabled.")
        return
    
    log.info(f"Executing script #{script['id']}: {script['name']}")
    print(f"▶️  Running: {script['name']}...")
    
    result = execute_script(script, args.args.split() if args.args else None)
    
    # Save execution record
    executions_data = load_executions()
    exec_record = {
        "id": generate_id(executions_data.get("executions", [])),
        "script_id": script["id"],
        "script_name": script["name"],
        "success": result["success"],
        "duration_ms": result["duration_ms"],
        "output": result.get("output", "")[:500] if result.get("output") else "",
        "error": result.get("error"),
        "executed_at": result.get("executed_at", datetime.utcnow().isoformat()),
    }
    executions_data["executions"].append(exec_record)
    save_executions(executions_data)
    
    # Update script last_run
    for s in scripts_data.get("scripts", []):
        if s["id"] == script["id"]:
            s["last_run"] = datetime.utcnow().isoformat()
            break
    save_scripts_db(scripts_data)
    
    # Output result
    if result["success"]:
        print(f"✅ Script completed successfully ({result['duration_ms']}ms)")
        if result.get("output"):
            print(f"\nOutput:\n{result['output'][:500]}")
    else:
        print(f"❌ Script failed: {result.get('error', 'Unknown error')}")
        print(f"   Duration: {result['duration_ms']}ms")


def cmd_add(args) -> None:
    """Register a new automation script."""
    scripts_data = load_scripts_db()
    
    script = {
        "id": generate_id(scripts_data.get("scripts", [])),
        "name": args.name,
        "description": args.description or "",
        "path": args.path,
        "type": args.type,
        "category": args.category,
        "enabled": True,
        "last_run": None,
        "avg_duration_ms": 0,
        "created_at": datetime.utcnow().isoformat(),
    }
    
    scripts_data["scripts"].append(script)
    save_scripts_db(scripts_data)
    
    print(f"✅ Added script #{script['id']}: {script['name']}")
    print(f"   Path: {script['path']}")
    print(f"   Type: {script['type']}, Category: {script['category']}")


def cmd_update(args) -> None:
    """Update script properties."""
    scripts_data = load_scripts_db()
    
    for s in scripts_data.get("scripts", []):
        if s["id"] == args.id:
            if args.name:
                s["name"] = args.name
            if args.description:
                s["description"] = args.description
            if args.path:
                s["path"] = args.path
            if args.category:
                s["category"] = args.category
            
            save_scripts_db(scripts_data)
            print(f"✅ Updated script #{args.id}")
            return
    
    print(f"❌ Script #{args.id} not found.")


def cmd_enable(args) -> None:
    """Enable a script."""
    scripts_data = load_scripts_db()
    
    for s in scripts_data.get("scripts", []):
        if s["id"] == args.id:
            s["enabled"] = True
            save_scripts_db(scripts_data)
            print(f"✅ Enabled script #{args.id}: {s['name']}")
            return
    
    print(f"❌ Script #{args.id} not found.")


def cmd_disable(args) -> None:
    """Disable a script."""
    scripts_data = load_scripts_db()
    
    for s in scripts_data.get("scripts", []):
        if s["id"] == args.id:
            s["enabled"] = False
            save_scripts_db(scripts_data)
            print(f"❌ Disabled script #{args.id}: {s['name']}")
            return
    
    print(f"❌ Script #{args.id} not found.")


def cmd_delete(args) -> None:
    """Delete a script registration."""
    scripts_data = load_scripts_db()
    original_len = len(scripts_data.get("scripts", []))
    scripts_data["scripts"] = [s for s in scripts_data["scripts"] if s["id"] != args.id]
    
    if len(scripts_data["scripts"]) < original_len:
        save_scripts_db(scripts_data)
        print(f"✅ Deleted script #{args.id}")
    else:
        print(f"❌ Script #{args.id} not found.")


def cmd_history(args) -> None:
    """Show execution history."""
    data = load_executions()
    executions = data.get("executions", [])
    
    if not executions:
        print("📋 No execution history.")
        return
    
    limit = args.limit
    filtered = executions[-limit:] if limit else executions
    
    print(f"📋 Execution History ({len(filtered)} recent):")
    print("-" * 70)
    
    for e in sorted(filtered, key=lambda x: x.get("executed_at", ""), reverse=True):
        status = "✅" if e.get("success") else "❌"
        print(f"  #{e['id']} | {status} | {e.get('script_name', 'unknown'):20} | {e.get('duration_ms', 0)}ms | {e.get('executed_at', '')[:19]}")


def cmd_stats(args) -> None:
    """Show script statistics."""
    scripts_data = load_scripts_db()
    executions_data = load_executions()
    
    scripts = scripts_data.get("scripts", [])
    executions = executions_data.get("executions", [])
    
    total_runs = len(executions)
    successful = sum(1 for e in executions if e.get("success"))
    failed = total_runs - successful
    
    success_rate = (successful / total_runs * 100) if total_runs > 0 else 0
    
    print("\n📊 Automation Scripts Statistics")
    print("=" * 50)
    print(f"Registered Scripts: {len(scripts)}")
    print(f"Enabled Scripts: {sum(1 for s in scripts if s.get('enabled'))}")
    print(f"\nTotal Executions: {total_runs}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    # Most run scripts
    if executions:
        script_counts = {}
        for e in executions:
            name = e.get("script_name", "unknown")
            script_counts[name] = script_counts.get(name, 0) + 1
        
        print("\nMost Executed Scripts:")
        for name, count in sorted(script_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {name}: {count} runs")


def cmd_categories(args) -> None:
    """List script categories."""
    scripts_data = load_scripts_db()
    scripts = scripts_data.get("scripts", [])
    
    categories = {}
    for s in scripts:
        cat = s.get("category", "uncategorized")
        if cat not in categories:
            categories[cat] = {"total": 0, "enabled": 0}
        categories[cat]["total"] += 1
        if s.get("enabled"):
            categories[cat]["enabled"] += 1
    
    print("\n📁 Script Categories")
    print("=" * 50)
    for cat, stats in sorted(categories.items()):
        print(f"  {cat}: {stats['enabled']}/{stats['total']} enabled")


def cmd_config(args) -> None:
    """Show configuration."""
    config = load_config()
    print("\n⚙️ Automation Scripts Config")
    print("=" * 50)
    for key, value in config.items():
        print(f"  {key}: {value}")


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Automation Scripts Agent - Productivity Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list
  %(prog)s list --category infrastructure
  %(prog)s list --enabled true
  %(prog)s run --id 1
  %(prog)s run --id 1 --args "--force"
  %(prog)s add --name "my_script" --path "scripts/my.sh" --type shell --category custom
  %(prog)s update --id 1 --name "new_name"
  %(prog)s enable --id 1
  %(prog)s disable --id 1
  %(prog)s delete --id 1
  %(prog)s history
  %(prog)s history --limit 20
  %(prog)s stats
  %(prog)s categories
  %(prog)s config
        """,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List
    p_list = subparsers.add_parser("list", help="List automation scripts")
    p_list.add_argument("--category", "-c", default=None, help="Filter by category")
    p_list.add_argument("--enabled", "-e", type=lambda x: x.lower() == "true", default=None,
                        help="Filter by enabled status (true/false)")
    
    # Run
    p_run = subparsers.add_parser("run", help="Execute a script")
    p_run.add_argument("--id", "-i", type=int, required=True, help="Script ID")
    p_run.add_argument("--args", "-a", default=None, help="Arguments to pass to script")
    
    # Add
    p_add = subparsers.add_parser("add", help="Register a new script")
    p_add.add_argument("--name", "-n", required=True, help="Script name")
    p_add.add_argument("--path", "-p", required=True, help="Script path (relative to workspace)")
    p_add.add_argument("--type", "-t", required=True, choices=["shell", "node", "python"],
                       help="Script type")
    p_add.add_argument("--category", "-c", default="custom", help="Category")
    p_add.add_argument("--description", "-d", default=None, help="Description")
    
    # Update
    p_update = subparsers.add_parser("update", help="Update script properties")
    p_update.add_argument("--id", "-i", type=int, required=True, help="Script ID")
    p_update.add_argument("--name", "-n", default=None, help="New name")
    p_update.add_argument("--description", "-d", default=None, help="New description")
    p_update.add_argument("--path", "-p", default=None, help="New path")
    p_update.add_argument("--category", "-c", default=None, help="New category")
    
    # Enable
    p_enable = subparsers.add_parser("enable", help="Enable a script")
    p_enable.add_argument("--id", "-i", type=int, required=True, help="Script ID")
    
    # Disable
    p_disable = subparsers.add_parser("disable", help="Disable a script")
    p_disable.add_argument("--id", "-i", type=int, required=True, help="Script ID")
    
    # Delete
    p_delete = subparsers.add_parser("delete", help="Delete script registration")
    p_delete.add_argument("--id", "-i", type=int, required=True, help="Script ID")
    
    # History
    p_history = subparsers.add_parser("history", help="Show execution history")
    p_history.add_argument("--limit", "-l", type=int, default=None, help="Limit results")
    
    # Stats
    subparsers.add_parser("stats", help="Show statistics")
    
    # Categories
    subparsers.add_parser("categories", help="List categories")
    
    # Config
    subparsers.add_parser("config", help="Show configuration")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "list":
            cmd_list(args)
        elif args.command == "run":
            cmd_run(args)
        elif args.command == "add":
            cmd_add(args)
        elif args.command == "update":
            cmd_update(args)
        elif args.command == "enable":
            cmd_enable(args)
        elif args.command == "disable":
            cmd_disable(args)
        elif args.command == "delete":
            cmd_delete(args)
        elif args.command == "history":
            cmd_history(args)
        elif args.command == "stats":
            cmd_stats(args)
        elif args.command == "categories":
            cmd_categories(args)
        elif args.command == "config":
            cmd_config(args)
    except Exception as e:
        log.error(f"Command '{args.command}' failed: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
