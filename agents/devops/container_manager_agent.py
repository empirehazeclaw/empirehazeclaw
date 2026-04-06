#!/usr/bin/env python3
"""
Container Manager Agent - OpenClaw DevOps Suite
Manages Docker containers: start, stop, logs, stats, monitoring.
Reads/Writes: /home/clawbot/.openclaw/workspace/data/containers/containers.json
"""

import argparse
import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "containers"
DATA_FILE = DATA_DIR / "containers.json"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "container_manager.log"

LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ContainerManager")


def load_tracked() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        initial = {"containers": [], "last_updated": datetime.utcnow().isoformat()}
        save_tracked(initial)
        return initial
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        log.error(f"Failed to load container data: {e}")
        return {"containers": [], "last_updated": datetime.utcnow().isoformat()}


def save_tracked(data: dict) -> None:
    data["last_updated"] = datetime.utcnow().isoformat()
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        log.error(f"Failed to save container data: {e}")


def run_docker(args: str, timeout: int = 30) -> tuple:
    """Run docker command and return (returncode, stdout, stderr)."""
    try:
        # Use list form with shlex.split for security
        cmd_list = ["docker"] + shlex.split(args)
        result = subprocess.run(
            cmd_list, capture_output=True, text=True, timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except FileNotFoundError:
        return -1, "", "Docker command not found. Is Docker installed?"
    except Exception as e:
        return -1, "", str(e)


def list_containers(all_fmt: bool = True) -> list:
    """List containers. Returns list of dicts."""
    flag = "-a" if all_fmt else ""
    code, out, _ = run_docker(f"ps {flag} --format '{{{{json .}}}}'")
    if code != 0:
        return []
    containers = []
    for line in out.strip().split("\n"):
        if line:
            try:
                containers.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return containers


def parse_container_info(name: str) -> dict:
    """Get detailed info for a container by name or ID."""
    code, out, _ = run_docker(f"inspect {name}")
    if code != 0 or not out.strip():
        return {}
    try:
        return json.loads(out)[0]
    except (json.JSONDecodeError, IndexError):
        return {}


def container_status(name: str) -> str:
    """Get container status string."""
    info = parse_container_info(name)
    state = info.get("State", {})
    if state.get("Running"):
        return "running"
    if state.get("ExitCode") == 0:
        return "exited"
    return "stopped"


def cmd_ps(args) -> None:
    """List running containers."""
    containers = list_containers(all_fmt=args.all)
    if not containers:
        print("🐳 No containers found." if not args.all else "🐳 No containers (including stopped).")
        return

    print(f"\n🐳 Containers ({len(containers)})\n{'─'*80}")
    for c in containers:
        name = c.get("Names", c.get("Name", "?"))
        image = c.get("Image", "?")
        status = c.get("Status", "?")
        state = c.get("State", "?")
        icon = "🟢" if state == "running" else "🔴" if state == "exited" else "⚪"
        ports = c.get("Ports", "")
        print(f"  {icon} {name:<30} {image:<30} {status}")
        if ports:
            print(f"      Ports: {ports[:60]}")
    print()


def cmd_start(args) -> None:
    """Start a container."""
    code, stdout, stderr = run_docker(f"start {args.container}")
    if code == 0:
        log.info(f"Container started: {args.container}")
        print(f"▶️  Container '{args.container}' started.")
    else:
        log.error(f"Failed to start container {args.container}: {stderr}")
        print(f"❌ Failed to start '{args.container}': {stderr}")


def cmd_stop(args) -> None:
    """Stop a container."""
    code, stdout, stderr = run_docker(f"stop -t {args.timeout} {args.container}")
    if code == 0:
        log.info(f"Container stopped: {args.container}")
        print(f"⏹️  Container '{args.container}' stopped.")
    else:
        log.error(f"Failed to stop container {args.container}: {stderr}")
        print(f"❌ Failed to stop '{args.container}': {stderr}")


def cmd_restart(args) -> None:
    """Restart a container."""
    code, stdout, stderr = run_docker(f"restart -t {args.timeout} {args.container}")
    if code == 0:
        log.info(f"Container restarted: {args.container}")
        print(f"🔄 Container '{args.container}' restarted.")
    else:
        log.error(f"Failed to restart container {args.container}: {stderr}")
        print(f"❌ Failed to restart '{args.container}': {stderr}")


def cmd_logs(args) -> None:
    """Get container logs."""
    tail = f"--tail {args.tail}" if args.tail else "--tail 50"
    code, stdout, stderr = run_docker(f"logs {tail} {'--since ' + args.since if args.since else ''} {args.container}", timeout=15)
    if code == 0 or stdout:
        print(f"📜 Logs for '{args.container}' (tail={args.tail or 50}):\n")
        print(stdout[:args.limit] if args.limit else stdout)
        if stderr:
            print(f"\n[stderr]\n{stderr[:500]}")
    else:
        print(f"❌ Could not fetch logs for '{args.container}': {stderr}")


def cmd_stats(args) -> None:
    """Show container stats."""
    code, out, _ = run_docker("stats --no-stream --format '{{json .}}'")
    if code != 0:
        print("❌ Could not fetch container stats. Is Docker running?")
        return
    stats = []
    for line in out.strip().split("\n"):
        if line:
            try:
                stats.append(json.loads(line))
            except json.JSONDecodeError:
                pass

    if not stats:
        print("📊 No running containers to show stats for.")
        return

    print(f"\n📊 Container Stats\n{'─'*80}")
    for s in stats:
        name = s.get("Name", "?")
        cpu = s.get("CPUPerc", "?")
        mem = s.get("MemUsage", "?")
        net = s.get("NetIO", "?")
        block = s.get("BlockIO", "?")
        print(f"  {name:<30} CPU: {cpu:<10} MEM: {mem:<20} NET: {net}")
    print()


def cmd_inspect(args) -> None:
    """Inspect container details."""
    info = parse_container_info(args.container)
    if not info:
        print(f"❌ Container '{args.container}' not found.")
        return
    config = info.get("Config", {})
    state = info.get("State", {})
    print(f"\n🐳 Container: {args.container}\n{'─'*60}")
    print(f"  ID:       {info.get('Id', '?')[:12]}")
    print(f"  Image:    {info.get('Config', {}).get('Image', '?')}")
    print(f"  Status:   {state.get('Status', '?')}")
    print(f"  Running:  {state.get('Running', False)}")
    print(f"  Created: {info.get('Created', '?')[:19]}")
    print(f"  Ports:   {config.get('ExposedPorts', 'None')}")
    env = config.get("Env", [])
    if env:
        print(f"  Env:     {env[:3]}...")
    cmd = config.get("Cmd", [])
    if cmd:
        print(f"  Cmd:     {' '.join(cmd)}")
    mounts = info.get("Mounts", [])
    if mounts:
        print(f"  Mounts:  {len(mounts)} volume(s) attached")


def cmd_track(args) -> None:
    """Track a container in the database."""
    data = load_tracked()
    # Check if already tracked
    for c in data["containers"]:
        if c.get("name") == args.container:
            print(f"ℹ️  Container '{args.container}' is already tracked.")
            return
    status = container_status(args.container)
    entry = {
        "id": len(data["containers"]) + 1,
        "name": args.container,
        "description": args.description or "",
        "project": args.project or "general",
        "tracked_at": datetime.utcnow().isoformat(),
        "last_status": status,
        "last_checked": datetime.utcnow().isoformat(),
        "auto_restart": args.auto_restart,
    }
    data["containers"].append(entry)
    save_tracked(data)
    log.info(f"Container tracked: {args.container}")
    print(f"✅ Container '{args.container}' tracked (status: {status}).")


def cmd_monitor(args) -> None:
    """Monitor tracked containers."""
    data = load_tracked()
    tracked = data.get("containers", [])
    if not tracked:
        print("📋 No containers being tracked.")
        return

    issues = []
    for c in tracked:
        current = container_status(c["name"])
        c["last_checked"] = datetime.utcnow().isoformat()
        c["last_status"] = current
        if current != "running":
            issues.append((c, current))
        if c.get("auto_restart") and current == "stopped":
            print(f"🔄 Auto-restarting '{c['name']}'...")
            run_docker(f"start {c['name']}")
            c["last_status"] = "running"
        sys.stdout.write(f"  {'🟢' if current == 'running' else '🔴'} {c['name']:<30} {current}\n")
        sys.stdout.flush()

    save_tracked(data)
    if issues:
        print(f"\n⚠️  {len(issues)} issue(s) found:")
        for c, s in issues:
            print(f"  🔴 {c['name']}: {s}")
    else:
        print(f"\n✅ All {len(tracked)} tracked containers healthy.")


def cmd_untrack(args) -> None:
    """Stop tracking a container."""
    data = load_tracked()
    original = len(data["containers"])
    data["containers"] = [c for c in data["containers"] if c.get("name") != args.container]
    if len(data["containers"]) < original:
        save_tracked(data)
        log.info(f"Container untracked: {args.container}")
        print(f"🗑️  Container '{args.container}' untracked.")
    else:
        print(f"❌ Container '{args.container}' not being tracked.")


def main():
    parser = argparse.ArgumentParser(
        prog="container-manager",
        description="🐳 Container Manager Agent — manage and monitor Docker containers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  container-manager ps
  container-manager ps --all
  container-manager start myapp
  container-manager stop myapp
  container-manager restart myapp --timeout 30
  container-manager logs myapp --tail 100
  container-manager logs myapp --since 1h
  container-manager stats
  container-manager inspect myapp
  container-manager track myapp --project api --auto-restart
  container-manager monitor
  container-manager untrack myapp
        """,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("ps", help="List containers").add_argument("--all", action="store_true", help="Include stopped")

    p_start = sub.add_parser("start", help="Start a container")
    p_start.add_argument("container", help="Container name or ID")

    p_stop = sub.add_parser("stop", help="Stop a container")
    p_stop.add_argument("container", help="Container name or ID")
    p_stop.add_argument("--timeout", type=int, default=10, help="Timeout seconds")

    p_restart = sub.add_parser("restart", help="Restart a container")
    p_restart.add_argument("container", help="Container name or ID")
    p_restart.add_argument("--timeout", type=int, default=10, help="Timeout seconds")

    p_logs = sub.add_parser("logs", help="Get container logs")
    p_logs.add_argument("container", help="Container name or ID")
    p_logs.add_argument("--tail", type=int, help="Number of lines to show")
    p_logs.add_argument("--since", help="Show logs since timestamp (e.g., 1h, 30m)")
    p_logs.add_argument("--limit", type=int, help="Limit output characters")

    sub.add_parser("stats", help="Show container stats (CPU, memory)")

    p_inspect = sub.add_parser("inspect", help="Inspect container details")
    p_inspect.add_argument("container", help="Container name or ID")

    p_track = sub.add_parser("track", help="Track a container")
    p_track.add_argument("container", help="Container name or ID")
    p_track.add_argument("-d", "--description", default="", help="Description")
    p_track.add_argument("-p", "--project", default="general", help="Project name")
    p_track.add_argument("--auto-restart", action="store_true", help="Auto-restart if stopped")

    sub.add_parser("monitor", help="Monitor all tracked containers")

    p_untrack = sub.add_parser("untrack", help="Stop tracking a container")
    p_untrack.add_argument("container", help="Container name or ID")

    args = parser.parse_args()
    try:
        if args.command == "ps":
            cmd_ps(args)
        elif args.command == "start":
            cmd_start(args)
        elif args.command == "stop":
            cmd_stop(args)
        elif args.command == "restart":
            cmd_restart(args)
        elif args.command == "logs":
            cmd_logs(args)
        elif args.command == "stats":
            cmd_stats(args)
        elif args.command == "inspect":
            cmd_inspect(args)
        elif args.command == "track":
            cmd_track(args)
        elif args.command == "monitor":
            cmd_monitor(args)
        elif args.command == "untrack":
            cmd_untrack(args)
    except Exception as e:
        log.error(f"Command '{args.command}' failed: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
