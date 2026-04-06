#!/usr/bin/env python3
"""
Deployment Automation Agent - OpenClaw DevOps Suite
Automates deployment workflows, tracks deployments, rollback support.
Reads/Writes: /home/clawbot/.openclaw/workspace/data/deployments/deployments.json
"""

import argparse
import json
import logging
import os
import shlex
import subprocess
import sys
import tempfile
import hashlib
from datetime import datetime
from pathlib import Path

BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "deployments"
DATA_FILE = DATA_DIR / "deployments.json"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "deployment_automation.log"

LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("DeploymentAgent")


def load_deployments() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        initial = {"deployments": [], "last_updated": datetime.utcnow().isoformat()}
        save_deployments(initial)
        return initial
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        log.error(f"Failed to load deployments: {e}")
        return {"deployments": [], "last_updated": datetime.utcnow().isoformat()}


def save_deployments(data: dict) -> None:
    data["last_updated"] = datetime.utcnow().isoformat()
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        log.error(f"Failed to save deployments: {e}")
        raise


def generate_id(deployments: list) -> int:
    return max((d.get("id", 0) for d in deployments), default=0) + 1


def run_command(cmd: str, cwd: str = None, timeout: int = 120) -> tuple:
    """Run shell command and return (returncode, stdout, stderr)."""
    try:
        # Use list form with shlex.split for security
        cmd_list = shlex.split(cmd)
        result = subprocess.run(
            cmd_list, capture_output=True, text=True,
            cwd=cwd, timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def git_hash(repo_path: str) -> str:
    """Get current git commit hash."""
    code, out, _ = run_command("git rev-parse HEAD", cwd=repo_path)
    return out.strip()[:8] if code == 0 else "unknown"


def git_branch(repo_path: str) -> str:
    """Get current git branch."""
    code, out, _ = run_command("git rev-parse --abbrev-ref HEAD", cwd=repo_path)
    return out.strip() if code == 0 else "unknown"


def cmd_deploy(args) -> None:
    """Deploy a project."""
    data = load_deployments()

    # Resolve project path
    project_path = os.path.abspath(args.project_path) if args.project_path else os.getcwd()
    project_name = args.name or os.path.basename(project_path)

    # Gather info
    branch = git_branch(project_path) if os.path.exists(os.path.join(project_path, ".git")) else "N/A"
    commit = git_hash(project_path) if os.path.exists(os.path.join(project_path, ".git")) else "N/A"

    print(f"🚀 Deploying {project_name}...")
    print(f"   Path: {project_path}")
    print(f"   Branch: {branch} | Commit: {commit}")

    # Build command
    if args.type == "vercel":
        cmd = "vercel --prod --yes"
    elif args.type == "docker":
        tag = f"{args.tag or project_name}:{datetime.utcnow().strftime('%Y%m%d%H%M')}"
        cmd = f"docker build -t {tag} {project_path}"
    elif args.type == "npm":
        cmd = f"npm run {args.script or 'deploy'} --prefix {project_path}"
    elif args.type == "shell":
        cmd = args.custom_cmd or "echo 'No command specified'"
    else:
        cmd = f"echo 'Unknown deploy type: {args.type}'"

    print(f"   Command: {cmd[:80]}")

    if args.dry_run:
        print(f"   🧪 DRY RUN - would execute: {cmd}")
        return

    returncode, stdout, stderr = run_command(cmd, cwd=project_path, timeout=args.timeout or 120)

    deployment = {
        "id": generate_id(data["deployments"]),
        "name": project_name,
        "project_path": project_path,
        "type": args.type,
        "branch": branch,
        "commit": commit,
        "status": "success" if returncode == 0 else "failed",
        "return_code": returncode,
        "output_preview": stdout[:1000] + ("..." if len(stdout) > 1000 else ""),
        "error_preview": stderr[:500] if stderr else "",
        "deployed_at": datetime.utcnow().isoformat(),
        "tag": args.tag or "",
        "env": args.env or "production",
    }

    data["deployments"].append(deployment)
    save_deployments(data)

    if returncode == 0:
        log.info(f"Deployment #{deployment['id']} succeeded: {project_name}")
        print(f"✅ Deployment #{deployment['id']} succeeded!")
        print(f"   Output: {stdout[:300]}")
    else:
        log.error(f"Deployment #{deployment['id']} failed: {project_name}")
        print(f"❌ Deployment #{deployment['id']} FAILED!")
        print(f"   Error: {stderr[:300]}")


def cmd_history(args) -> None:
    """Show deployment history."""
    data = load_deployments()
    deployments = data.get("deployments", [])

    if args.project:
        deployments = [d for d in deployments if args.project.lower() in d.get("name", "").lower()]

    if args.env:
        deployments = [d for d in deployments if d.get("env") == args.env]

    if not deployments:
        print("🚀 No deployments found.")
        return

    deployments.sort(key=lambda d: d.get("deployed_at", ""), reverse=True)
    show = deployments[:args.limit]

    print(f"\n🚀 Deployment History ({len(show)} of {len(deployments)})\n{'─'*70}")
    for d in show:
        icon = "✅" if d.get("status") == "success" else "❌"
        print(f"  {icon} #{d['id']:4d} | {d.get('name','?')[:25]:<25} | {d.get('type'):8s} | {d.get('env')}")
        print(f"       Branch: {d.get('branch','?')} | Commit: {d.get('commit','?')} | {d.get('deployed_at','')[:19]}")
        if d.get("status") == "failed":
            print(f"       Error: {d.get('error_preview','')[:80]}")
    print()


def cmd_rollback(args) -> None:
    """Rollback to a previous deployment."""
    data = load_deployments()
    deployments = [d for d in data["deployments"] if d.get("status") == "success"]
    if not deployments:
        print("❌ No successful deployments found to rollback to.")
        return

    target = None
    for d in deployments:
        if d["id"] == args.deployment_id:
            target = d
            break

    if not target:
        print(f"❌ Deployment #{args.deployment_id} not found or not successful.")
        return

    print(f"🔄 Rolling back {target['name']} to deployment #{target['id']}...")
    print(f"   Commit: {target.get('commit')} | Branch: {target.get('branch')}")

    if args.dry_run:
        print("   🧪 DRY RUN - rollback would proceed")
        return

    # Simple rollback: re-run deploy command with same commit
    if target.get("type") == "vercel":
        cmd = "vercel --prod --yes"
    elif target.get("type") == "docker":
        tag = target.get("tag") or target["name"]
        cmd = f"docker pull {tag}"
    else:
        cmd = f"echo 'Rollback command not implemented for type: {target.get('type')}'"

    returncode, stdout, stderr = run_command(cmd, cwd=target.get("project_path", "/"), timeout=60)

    rollback_record = {
        "id": generate_id(data["deployments"]),
        "name": target["name"] + " (rollback)",
        "project_path": target.get("project_path", ""),
        "type": target.get("type", "shell"),
        "branch": target.get("branch", ""),
        "commit": target.get("commit", ""),
        "status": "success" if returncode == 0 else "failed",
        "return_code": returncode,
        "rollback_of": target["id"],
        "deployed_at": datetime.utcnow().isoformat(),
        "env": target.get("env", "production"),
    }
    data["deployments"].append(rollback_record)
    save_deployments(data)

    if returncode == 0:
        print(f"✅ Rollback succeeded!")
    else:
        print(f"❌ Rollback failed: {stderr[:200]}")


def cmd_status(args) -> None:
    """Show deployment status summary."""
    data = load_deployments()
    deployments = data.get("deployments", [])
    total = len(deployments)
    success = sum(1 for d in deployments if d.get("status") == "success")
    failed = sum(1 for d in deployments if d.get("status") == "failed")
    projects = set(d.get("name") for d in deployments)

    latest = deployments[-1] if deployments else None

    print(f"\n🚀 Deployment Status\n{'─'*40}")
    print(f"  Total Deployments: {total}")
    print(f"  Successful:        {success} ✅")
    print(f"  Failed:            {failed} ❌")
    print(f"  Projects:          {len(projects)}")
    if latest:
        print(f"  Last Deployment:   #{latest['id']} | {latest.get('name')} | {latest.get('status')} | {latest.get('deployed_at','')[:19]}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="deployment-automation",
        description="🚀 Deployment Automation Agent — deploy, track, and rollback",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  deployment-automation deploy --type vercel --project-path /var/www/myapp --name myapp
  deployment-automation deploy --type docker --project-path . --name api --tag myregistry/api:v2
  deployment-automation deploy --type npm --project-path . --script deploy --dry-run
  deployment-automation history --project myapp --limit 10
  deployment-automation rollback 5
  deployment-automation status
        """,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_deploy = sub.add_parser("deploy", help="Deploy a project")
    p_deploy.add_argument("--name", help="Project name")
    p_deploy.add_argument("--type", required=True, choices=["vercel", "docker", "npm", "shell"], help="Deploy type")
    p_deploy.add_argument("--project-path", help="Project directory path")
    p_deploy.add_argument("--script", help="NPM script name")
    p_deploy.add_argument("--tag", help="Docker image tag")
    p_deploy.add_argument("--custom-cmd", help="Custom shell command")
    p_deploy.add_argument("--env", default="production", help="Environment name")
    p_deploy.add_argument("--timeout", type=int, default=120, help="Timeout in seconds")
    p_deploy.add_argument("--dry-run", action="store_true", help="Dry run without executing")

    p_history = sub.add_parser("history", help="Show deployment history")
    p_history.add_argument("--project", help="Filter by project name")
    p_history.add_argument("--env", help="Filter by environment")
    p_history.add_argument("--limit", type=int, default=20, help="Number of entries to show")

    p_rollback = sub.add_parser("rollback", help="Rollback to a previous deployment")
    p_rollback.add_argument("deployment_id", type=int, help="Deployment ID to rollback to")
    p_rollback.add_argument("--dry-run", action="store_true", help="Dry run")

    p_status = sub.add_parser("status", help="Show deployment status")

    args = parser.parse_args()
    try:
        if args.command == "deploy":
            cmd_deploy(args)
        elif args.command == "history":
            cmd_history(args)
        elif args.command == "rollback":
            cmd_rollback(args)
        elif args.command == "status":
            cmd_status(args)
    except Exception as e:
        log.error(f"Command '{args.command}' failed: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
