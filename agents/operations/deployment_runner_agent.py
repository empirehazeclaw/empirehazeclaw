#!/usr/bin/env python3
"""
Deployment Runner Agent - Operations
Handles deployment workflows, tracking and rollbacks.
Based on SOUL.md principles: efficiency, action, measurable results.
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "deployment_runner.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DeploymentRunner")

DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
DEPLOYMENTS_FILE = DATA_DIR / "deployments.json"


def load_deployments() -> dict:
    """Load deployment history."""
    try:
        if DEPLOYMENTS_FILE.exists():
            with open(DEPLOYMENTS_FILE, 'r') as f:
                return json.load(f)
        return {"deployments": [], "current_version": None}
    except Exception as e:
        logger.error(f"Failed to load deployments: {e}")
        return {"deployments": [], "current_version": None}


def save_deployments(data: dict) -> bool:
    """Save deployment history."""
    try:
        with open(DEPLOYMENTS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save deployments: {e}")
        return False


def run_command(cmd: List[str], cwd: Optional[str] = None, timeout: int = 300) -> Dict:
    """Run a shell command and return result."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": "Command timed out", "returncode": -1}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}


def create_deployment(name: str, version: str, target: str,
                     build_cmd: Optional[str] = None, deploy_cmd: Optional[str] = None,
                     rollback_cmd: Optional[str] = None) -> dict:
    """Register a new deployment configuration."""
    data = load_deployments()
    
    # Check if version already exists
    for d in data.get("deployments", []):
        if d.get("version") == version:
            raise ValueError(f"Version {version} already exists")
    
    deployment = {
        "id": len(data.get("deployments", [])) + 1,
        "name": name,
        "version": version,
        "target": target,
        "build_cmd": build_cmd,
        "deploy_cmd": deploy_cmd,
        "rollback_cmd": rollback_cmd,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "deployed_at": None,
        "started_at": None,
        "completed_at": None,
        "logs": [],
        "error": None
    }
    
    data["deployments"].append(deployment)
    if save_deployments(data):
        logger.info(f"Created deployment config #{deployment['id']}: {name} v{version}")
        return deployment
    raise Exception("Failed to save deployment")


def execute_deployment(deployment_id: int, skip_build: bool = False) -> Dict:
    """Execute a deployment."""
    data = load_deployments()
    deployment = None
    idx = None
    
    for i, d in enumerate(data.get("deployments", [])):
        if d["id"] == deployment_id:
            deployment = d.copy()
            idx = i
            break
    
    if not deployment:
        return {"success": False, "error": "Deployment not found"}
    
    logs = []
    start_time = datetime.utcnow().isoformat()
    
    # Update status
    deployment["status"] = "running"
    deployment["started_at"] = start_time
    data["deployments"][idx] = deployment
    save_deployments(data)
    
    try:
        # Build step
        if not skip_build and deployment.get("build_cmd"):
            logs.append(f"[{datetime.utcnow().isoformat()}] Running build...")
            result = run_command(["bash", "-c", deployment["build_cmd"]])
            if result["success"]:
                logs.append(f"[{datetime.utcnow().isoformat()}] Build successful")
            else:
                logs.append(f"[{datetime.utcnow().isoformat()}] Build failed: {result['stderr']}")
                deployment["status"] = "failed"
                deployment["logs"] = logs
                deployment["error"] = result["stderr"]
                deployment["completed_at"] = datetime.utcnow().isoformat()
                data["deployments"][idx] = deployment
                save_deployments(data)
                return {"success": False, "logs": logs, "error": result["stderr"]}
        
        # Deploy step
        if deployment.get("deploy_cmd"):
            logs.append(f"[{datetime.utcnow().isoformat()}] Running deploy...")
            result = run_command(["bash", "-c", deployment["deploy_cmd"]])
            if result["success"]:
                logs.append(f"[{datetime.utcnow().isoformat()}] Deploy successful")
            else:
                logs.append(f"[{datetime.utcnow().isoformat()}] Deploy failed: {result['stderr']}")
                deployment["status"] = "failed"
                deployment["logs"] = logs
                deployment["error"] = result["stderr"]
                deployment["completed_at"] = datetime.utcnow().isoformat()
                data["deployments"][idx] = deployment
                save_deployments(data)
                return {"success": False, "logs": logs, "error": result["stderr"]}
        else:
            logs.append(f"[{datetime.utcnow().isoformat()}] No deploy command, marking as complete")
        
        # Success
        deployment["status"] = "deployed"
        deployment["deployed_at"] = datetime.utcnow().isoformat()
        deployment["completed_at"] = datetime.utcnow().isoformat()
        deployment["logs"] = logs
        data["deployments"][idx] = deployment
        data["current_version"] = deployment["version"]
        save_deployments(data)
        
        logger.info(f"Deployment #{deployment_id} completed successfully")
        return {"success": True, "logs": logs}
        
    except Exception as e:
        deployment["status"] = "failed"
        deployment["error"] = str(e)
        deployment["completed_at"] = datetime.utcnow().isoformat()
        data["deployments"][idx] = deployment
        save_deployments(data)
        return {"success": False, "logs": logs, "error": str(e)}


def rollback(deployment_id: Optional[int] = None) -> Dict:
    """Rollback to a previous deployment."""
    data = load_deployments()
    
    if deployment_id:
        # Find specific deployment
        for d in data.get("deployments", []):
            if d["id"] == deployment_id and d["status"] == "deployed":
                target = d
                break
        else:
            return {"success": False, "error": "Deployment not found or not deployed"}
    else:
        # Find most recent deployed
        deployed = [d for d in data.get("deployments", []) if d["status"] == "deployed"]
        if not deployed:
            return {"success": False, "error": "No deployed versions to rollback to"}
        deployed.sort(key=lambda x: x.get("deployed_at", ""), reverse=True)
        target = deployed[1] if len(deployed) > 1 else deployed[0]
        deployment_id = target["id"]
    
    target_idx = None
    for i, d in enumerate(data["deployments"]):
        if d["id"] == deployment_id:
            target_idx = i
            break
    
    if not target_idx is None and target.get("rollback_cmd"):
        logs = []
        logs.append(f"[{datetime.utcnow().isoformat()}] Running rollback...")
        result = run_command(["bash", "-c", target["rollback_cmd"]])
        if result["success"]:
            logs.append(f"[{datetime.utcnow().isoformat()}] Rollback successful")
            data["current_version"] = target["version"]
            save_deployments(data)
            return {"success": True, "logs": logs, "version": target["version"]}
        else:
            return {"success": False, "logs": logs, "error": result["stderr"]}
    
    return {"success": True, "logs": [], "version": target.get("version"), "message": "No rollback command configured"}


def list_deployments(status: Optional[str] = None, limit: int = 20) -> List[Dict]:
    """List deployments."""
    data = load_deployments()
    deployments = data.get("deployments", [])
    
    if status:
        deployments = [d for d in deployments if d.get("status") == status]
    
    deployments.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return deployments[:limit]


def get_deployment(deployment_id: int) -> Optional[Dict]:
    """Get deployment details."""
    data = load_deployments()
    for d in data.get("deployments", []):
        if d["id"] == deployment_id:
            return d
    return None


def delete_deployment(deployment_id: int) -> bool:
    """Delete a deployment record."""
    data = load_deployments()
    original_len = len(data["deployments"])
    data["deployments"] = [d for d in data["deployments"] if d["id"] != deployment_id]
    
    if len(data["deployments"]) < original_len:
        if save_deployments(data):
            logger.info(f"Deleted deployment #{deployment_id}")
            return True
    return False


def get_stats() -> Dict:
    """Get deployment statistics."""
    data = load_deployments()
    deployments = data.get("deployments", [])
    
    stats = {
        "total": len(deployments),
        "by_status": {},
        "current_version": data.get("current_version"),
        "success_rate": 0
    }
    
    deployed = [d for d in deployments if d.get("status") == "deployed"]
    failed = [d for d in deployments if d.get("status") == "failed"]
    
    if deployments:
        stats["success_rate"] = round(len(deployed) / len(deployments) * 100, 1)
    
    for d in deployments:
        status = d.get("status", "unknown")
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Deployment Runner Agent - Manage deployment workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create --name "api-service" --version "1.2.0" --target "production" --deploy-cmd "./deploy.sh"
  %(prog)s deploy --id 1
  %(prog)s deploy --id 1 --skip-build
  %(prog)s rollback --id 2
  %(prog)s rollback
  %(prog)s list --status deployed
  %(prog)s get --id 1
  %(prog)s delete --id 1
  %(prog)s stats
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create
    create_parser = subparsers.add_parser("create", help="Create deployment config")
    create_parser.add_argument("--name", "-n", required=True, help="Deployment name")
    create_parser.add_argument("--version", "-v", required=True, help="Version tag")
    create_parser.add_argument("--target", "-t", required=True, help="Target environment")
    create_parser.add_argument("--build-cmd", help="Build command")
    create_parser.add_argument("--deploy-cmd", help="Deploy command")
    create_parser.add_argument("--rollback-cmd", help="Rollback command")

    # Deploy
    deploy_parser = subparsers.add_parser("deploy", help="Execute deployment")
    deploy_parser.add_argument("--id", "-i", type=int, required=True, help="Deployment ID")
    deploy_parser.add_argument("--skip-build", action="store_true", help="Skip build step")

    # Rollback
    rollback_parser = subparsers.add_parser("rollback", help="Rollback deployment")
    rollback_parser.add_argument("--id", "-i", type=int, help="Specific deployment ID to rollback to")

    # List
    list_parser = subparsers.add_parser("list", help="List deployments")
    list_parser.add_argument("--status", "-s", help="Filter by status")
    list_parser.add_argument("--limit", "-l", type=int, default=20, help="Limit results")

    # Get
    get_parser = subparsers.add_parser("get", help="Get deployment details")
    get_parser.add_argument("--id", "-i", type=int, required=True, help="Deployment ID")

    # Delete
    delete_parser = subparsers.add_parser("delete", help="Delete deployment record")
    delete_parser.add_argument("--id", "-i", type=int, required=True, help="Deployment ID")

    # Stats
    subparsers.add_parser("stats", help="Show deployment statistics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    try:
        if args.command == "create":
            deployment = create_deployment(
                name=args.name,
                version=args.version,
                target=args.target,
                build_cmd=args.build_cmd,
                deploy_cmd=args.deploy_cmd,
                rollback_cmd=args.rollback_cmd
            )
            print(f"✅ Created deployment #{deployment['id']}: {deployment['name']} v{deployment['version']}")

        elif args.command == "deploy":
            print(f"🚀 Executing deployment #{args.id}...")
            result = execute_deployment(args.id, skip_build=args.skip_build)
            if result["success"]:
                print("✅ Deployment successful!")
                for log in result.get("logs", []):
                    print(f"   {log}")
            else:
                print(f"❌ Deployment failed: {result.get('error', 'Unknown error')}")
                for log in result.get("logs", []):
                    print(f"   {log}")
                return 1

        elif args.command == "rollback":
            print("🔄 Rolling back...")
            result = rollback(deployment_id=args.id if hasattr(args, 'id') else None)
            if result["success"]:
                print(f"✅ Rollback complete (version: {result.get('version', '?')})")
                for log in result.get("logs", []):
                    print(f"   {log}")
            else:
                print(f"❌ Rollback failed: {result.get('error', 'Unknown error')}")
                return 1

        elif args.command == "list":
            deployments = list_deployments(
                status=args.status if hasattr(args, 'status') else None,
                limit=args.limit if hasattr(args, 'limit') else 20
            )
            if not deployments:
                print("No deployments found.")
            else:
                print(f"Found {len(deployments)} deployment(s):\n")
                for d in deployments:
                    status_icon = {"deployed": "✅", "failed": "❌", "running": "⏳", "pending": "⏸️"}.get(d.get("status", ""), "❓")
                    current = " (current)" if d.get("version") == load_deployments().get("current_version") else ""
                    print(f"  {status_icon} #{d['id']} | {d.get('version', '?'):10} | {d.get('status', '?'):10} | {d['name']}{current}")

        elif args.command == "get":
            deployment = get_deployment(args.id)
            if deployment:
                print(f"\nDeployment #{deployment['id']}")
                print(f"  Name: {deployment['name']}")
                print(f"  Version: {deployment['version']}")
                print(f"  Target: {deployment['target']}")
                print(f"  Status: {deployment.get('status', '?')}")
                print(f"  Created: {deployment.get('created_at', '?')}")
                print(f"  Deployed: {deployment.get('deployed_at', 'Not deployed')}")
                if deployment.get("logs"):
                    print(f"  Logs:")
                    for log in deployment["logs"][-10:]:
                        print(f"    {log}")
                if deployment.get("error"):
                    print(f"  Error: {deployment['error']}")
            else:
                print(f"Deployment #{args.id} not found.")
                return 1

        elif args.command == "delete":
            if delete_deployment(args.id):
                print(f"✅ Deleted deployment #{args.id}")
            else:
                print(f"Deployment #{args.id} not found.")
                return 1

        elif args.command == "stats":
            stats = get_stats()
            print("\n🚀 Deployment Statistics")
            print(f"  Total Deployments: {stats['total']}")
            print(f"  Success Rate: {stats['success_rate']}%")
            print(f"  Current Version: {stats['current_version'] or 'None'}")
            print("  By Status:")
            for status, count in stats["by_status"].items():
                print(f"    {status}: {count}")

        return 0

    except ValueError as e:
        print(f"❌ Validation Error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Command failed: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
