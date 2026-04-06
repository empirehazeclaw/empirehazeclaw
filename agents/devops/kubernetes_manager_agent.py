#!/usr/bin/env python3
"""
DevOps Kubernetes Manager Agent
Manages Kubernetes clusters, deployments, pods, and scaling operations.
Reads/Writes: data/k8s_state.json, logs/k8s_operations.log
"""

import argparse
import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "kubernetes_manager.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("KubernetesManager")

STATE_FILE = Path("/home/clawbot/.openclaw/workspace/data/k8s_state.json")


def load_state():
    if not STATE_FILE.exists():
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        default_state = {
            "clusters": [],
            "deployments": [],
            "last_updated": datetime.utcnow().isoformat()
        }
        save_state(default_state)
        return default_state
    with open(STATE_FILE) as f:
        return json.load(f)


def save_state(state):
    state["last_updated"] = datetime.utcnow().isoformat()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def run_kubectl(cmd, cluster=None, namespace=None):
    """Run a kubectl command safely."""
    full_cmd = ["kubectl"]
    if cluster:
        full_cmd.extend(["--cluster", cluster])
    if namespace:
        full_cmd.extend(["-n", namespace])
    full_cmd.extend(cmd)
    try:
        result = subprocess.run(
            full_cmd, capture_output=True, text=True, timeout=30
        )
        return result.stdout, result.stderr, result.returncode
    except FileNotFoundError:
        return "", "kubectl not found. Is it installed?", 1
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1


def discover_clusters():
    """Discover available Kubernetes clusters via kubectl config."""
    stdout, stderr, rc = run_kubectl(["config", "get-contexts", "-o", "name"])
    if rc != 0:
        logger.warning(f"Could not get clusters: {stderr}")
        return []
    clusters = [line.strip() for line in stdout.strip().split("\n") if line.strip()]
    logger.info(f"Discovered {len(clusters)} clusters")
    return clusters


def get_pods(cluster=None, namespace=None, all_namespaces=False):
    """Get pod list."""
    cmd = ["get", "pods", "-o", "json"]
    if all_namespaces:
        cmd.append("-A")
    stdout, stderr, rc = run_kubectl(cmd, cluster, namespace)
    if rc != 0:
        return {"error": stderr}
    try:
        data = json.loads(stdout)
        pods = data.get("items", [])
        result = []
        for pod in pods:
            status = pod.get("status", {})
            containers = pod.get("spec", {}).get("containers", [])
            result.append({
                "name": pod.get("metadata", {}).get("name"),
                "namespace": pod.get("metadata", {}).get("namespace"),
                "phase": status.get("phase", "Unknown"),
                "ready": f"{len([c for c in containers if c.get('ready', False)])}/{len(containers)}",
                "age": status.get("startTime", ""),
                "node": pod.get("spec", {}).get("nodeName", "")
            })
        return {"pods": result}
    except json.JSONDecodeError:
        return {"error": "Failed to parse kubectl output"}


def get_deployments(cluster=None, namespace=None):
    """Get deployment list."""
    cmd = ["get", "deployments", "-o", "json"]
    stdout, stderr, rc = run_kubectl(cmd, cluster, namespace)
    if rc != 0:
        return {"error": stderr}
    try:
        data = json.loads(stdout)
        deps = data.get("items", [])
        result = []
        for d in deps:
            spec = d.get("spec", {})
            status = d.get("status", {})
            result.append({
                "name": d.get("metadata", {}).get("name"),
                "namespace": d.get("metadata", {}).get("namespace"),
                "replicas": spec.get("replicas", 0),
                "ready_replicas": status.get("readyReplicas", 0),
                "available_replicas": status.get("availableReplicas", 0),
                "image": spec.get("template", {}).get("spec", {}).get("containers", [{}])[0].get("image", "")
            })
        return {"deployments": result}
    except (json.JSONDecodeError, IndexError):
        return {"error": "Failed to parse kubectl output"}


def scale_deployment(name, replicas, cluster=None, namespace=None):
    """Scale a deployment."""
    stdout, stderr, rc = run_kubectl(
        ["scale", "--replicas", str(replicas), f"deployment/{name}"],
        cluster, namespace
    )
    if rc != 0:
        logger.error(f"Scale failed: {stderr}")
        return False, stderr
    logger.info(f"Scaled {name} to {replicas} replicas")
    return True, stdout


def rollout_status(deployment, cluster=None, namespace=None):
    """Check rollout status."""
    stdout, stderr, rc = run_kubectl(
        ["rollout", "status", f"deployment/{deployment}"],
        cluster, namespace
    )
    return stdout, stderr, rc


def describe_pod(name, cluster=None, namespace=None):
    """Describe a pod."""
    stdout, stderr, rc = run_kubectl(
        ["describe", "pod", name],
        cluster, namespace
    )
    return stdout, stderr, rc


def get_nodes(cluster=None):
    """Get cluster nodes."""
    stdout, stderr, rc = run_kubectl(["get", "nodes", "-o", "json"], cluster)
    if rc != 0:
        return {"error": stderr}
    try:
        data = json.loads(stdout)
        nodes = data.get("items", [])
        result = []
        for node in nodes:
            status = node.get("status", {})
            alloc = node.get("status", {}).get("allocatable", {})
            result.append({
                "name": node.get("metadata", {}).get("name"),
                "status": next((c.get("type") for c in status.get("conditions", []) if c.get("type") == "Ready"), "Unknown"),
                "cpu": alloc.get("cpu", "unknown"),
                "memory": alloc.get("memory", "unknown"),
                "pods": alloc.get("pods", "unknown"),
                "roles": list(node.get("metadata", {}).get("labels", {}).get("node-role.kubernetes.io/master") and ["master"] or [])
            })
        return {"nodes": result}
    except json.JSONDecodeError:
        return {"error": "Failed to parse kubectl output"}


def cmd_clusters(args):
    clusters = discover_clusters()
    if not clusters:
        print("No clusters found or kubectl not available.")
        return
    print(f"\nDiscovered {len(clusters)} cluster(s):")
    for c in clusters:
        print(f"  - {c}")


def cmd_pods(args):
    result = get_pods(cluster=args.cluster, namespace=args.namespace,
                       all_namespaces=args.all_namespaces)
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    pods = result.get("pods", [])
    if not pods:
        print("No pods found.")
        return
    ns = "all namespaces" if args.all_namespaces else (args.namespace or "default")
    print(f"\nPods in {ns}:")
    print(f"{'Namespace':<20} {'Name':<35} {'Ready':<8} {'Status':<12} {'Node':<20}")
    print("-" * 100)
    for p in pods:
        print(f"{p.get('namespace',''):<20} {p.get('name',''):<35} "
              f"{p.get('ready',''):<8} {p.get('phase',''):<12} {p.get('node',''):<20}")


def cmd_deployments(args):
    result = get_deployments(cluster=args.cluster, namespace=args.namespace)
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    deps = result.get("deployments", [])
    if not deps:
        print("No deployments found.")
        return
    ns = args.namespace or "default"
    print(f"\nDeployments in {ns}:")
    print(f"{'Namespace':<20} {'Name':<30} {'Replicas':>8} {'Ready':>8} {'Image':<25}")
    print("-" * 100)
    for d in deps:
        print(f"{d.get('namespace',''):<20} {d.get('name',''):<30} "
              f"{d.get('replicas',0):>8} {d.get('ready_replicas',0):>8} "
              f"{d.get('image',''):<25}")


def cmd_scale(args):
    success, msg = scale_deployment(args.deployment, args.replicas,
                                     cluster=args.cluster, namespace=args.namespace)
    if success:
        print(f"Scaled {args.deployment} to {args.replicas} replicas.")
    else:
        print(f"Scale failed: {msg}")


def cmd_rollout(args):
    stdout, stderr, rc = rollout_status(args.deployment, args.cluster, args.namespace)
    if rc == 0:
        print(f"Rollout complete: {args.deployment}")
        if stdout:
            print(stdout)
    else:
        print(f"Rollout status error: {stderr}")


def cmd_nodes(args):
    result = get_nodes(cluster=args.cluster)
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    nodes = result.get("nodes", [])
    if not nodes:
        print("No nodes found.")
        return
    print(f"\n{'Name':<35} {'Status':<10} {'CPU':<10} {'Memory':<12} {'Pods':>8}")
    print("-" * 80)
    for n in nodes:
        print(f"{n.get('name',''):<35} {n.get('status',''):<10} "
              f"{n.get('cpu',''):<10} {n.get('memory',''):<12} {n.get('pods',''):>8}")


def cmd_describe(args):
    stdout, stderr, rc = describe_pod(args.pod, cluster=args.cluster,
                                       namespace=args.namespace)
    if rc == 0:
        print(stdout)
    else:
        print(f"Error: {stderr}")


def cmd_logs(args):
    """Get logs from a pod."""
    cmd = ["logs"]
    if args.tail:
        cmd.extend(["--tail", str(args.tail)])
    if args.previous:
        cmd.append("--previous")
    cmd.append(args.pod)
    stdout, stderr, rc = run_kubectl(cmd, cluster=args.cluster, namespace=args.namespace)
    if rc == 0:
        print(stdout)
    else:
        print(f"Error: {stderr}")


def cmd_health(args):
    """Quick cluster health check."""
    print(f"\n{'='*55}")
    print(f"  KUBERNETES CLUSTER HEALTH CHECK")
    print(f"{'='*55}")

    # Get clusters
    clusters = discover_clusters()
    print(f"  Clusters      : {len(clusters)}")
    for c in clusters:
        print(f"    - {c}")

    # Get nodes
    for cluster in (clusters or [None]):
        result = get_nodes(cluster=cluster)
        if "error" not in result:
            nodes = result.get("nodes", [])
            ready = [n for n in nodes if n.get("status") == "Ready"]
            print(f"\n  Cluster: {cluster or 'default'}")
            print(f"    Nodes       : {len(nodes)} ({len(ready)} ready)")

    # Get pods in all namespaces
    for cluster in (clusters or [None]):
        result = get_pods(cluster=cluster, all_namespaces=True)
        if "error" not in result:
            pods = result.get("pods", [])
            running = [p for p in pods if p.get("phase") == "Running"]
            pending = [p for p in pods if p.get("phase") == "Pending"]
            failed = [p for p in pods if p.get("phase") in ("Failed", "Error")]
            print(f"\n  Cluster: {cluster or 'default'}")
            print(f"    Total Pods   : {len(pods)}")
            print(f"    Running      : {len(running)}")
            print(f"    Pending      : {len(pending)}")
            print(f"    Failed/Error : {len(failed)}")
            if failed:
                print(f"    ⚠ Failed pods: {[p['name'] for p in failed[:5]]}")

    print(f"{'='*55}")


def main():
    parser = argparse.ArgumentParser(description="Kubernetes Manager Agent")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    subparsers.add_parser("clusters", help="Discover clusters").set_defaults(func=cmd_clusters)

    p_pods = subparsers.add_parser("pods", help="List pods")
    p_pods.add_argument("--cluster")
    p_pods.add_argument("--namespace", "-n")
    p_pods.add_argument("-A", dest="all_namespaces", action="store_true")
    p_pods.set_defaults(func=cmd_pods)

    p_deps = subparsers.add_parser("deployments", help="List deployments")
    p_deps.add_argument("--cluster")
    p_deps.add_argument("--namespace", "-n")
    p_deps.set_defaults(func=cmd_deployments)

    p_scale = subparsers.add_parser("scale", help="Scale a deployment")
    p_scale.add_argument("deployment", help="Deployment name")
    p_scale.add_argument("replicas", type=int)
    p_scale.add_argument("--cluster")
    p_scale.add_argument("--namespace", "-n")
    p_scale.set_defaults(func=cmd_scale)

    p_rollout = subparsers.add_parser("rollout", help="Check rollout status")
    p_rollout.add_argument("deployment")
    p_rollout.add_argument("--cluster")
    p_rollout.add_argument("--namespace", "-n")
    p_rollout.set_defaults(func=cmd_rollout)

    p_nodes = subparsers.add_parser("nodes", help="List nodes")
    p_nodes.add_argument("--cluster")
    p_nodes.set_defaults(func=cmd_nodes)

    p_desc = subparsers.add_parser("describe", help="Describe a pod")
    p_desc.add_argument("pod")
    p_desc.add_argument("--cluster")
    p_desc.add_argument("--namespace", "-n")
    p_desc.set_defaults(func=cmd_describe)

    p_logs = subparsers.add_parser("logs", help="Get pod logs")
    p_logs.add_argument("pod")
    p_logs.add_argument("--cluster")
    p_logs.add_argument("--namespace", "-n")
    p_logs.add_argument("--tail", type=int, help="Lines to show")
    p_logs.add_argument("--previous", action="store_true", help="Previous terminated container")
    p_logs.set_defaults(func=cmd_logs)

    subparsers.add_parser("health", help="Cluster health check").set_defaults(func=cmd_health)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
