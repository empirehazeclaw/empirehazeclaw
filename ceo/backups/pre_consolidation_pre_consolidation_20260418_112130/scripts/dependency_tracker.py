#!/usr/bin/env python3
"""
Dependency Tracker — Phase 2, Day 2
====================================
Tracks inter-component dependencies:
Cron X → Script Y → KG Update → Metric Change

Finds hidden dependencies that cause failures.

Usage:
    python3 dependency_tracker.py --scan          # Scan all components
    python3 dependency_tracker.py --trace <name> # Trace dependency chain
    python3 dependency_tracker.py --find <name>  # Find dependencies for component
    python3 dependency_tracker.py --graph         # Generate dependency graph
    python3 dependency_tracker.py --stats         # Show dependency stats
    python3 dependency_tracker.py --validate     # Validate known dependencies
"""

import json
import os
import sys
import argparse
import re
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
SCRIPTS_DIR = WORKSPACE / "scripts"
DEP_DIR = WORKSPACE / "memory" / "evaluations" / "dependencies"
DEP_GRAPH_FILE = DEP_DIR / "dependency_graph.json"
DEP_HISTORY_FILE = DEP_DIR / "dependency_history.json"

# Known dependency patterns
EXECUTION_PATTERNS = [
    (r"python3\s+(.+\.py)", "executes"),
    (r"bash\s+(.+\.sh)", "executes"),
    (r"subprocess\.run\s*\(\s*\[.*\"python3\",\s*\"(.+\.py)\"", "executes"),
    (r"from\s+(\w+)\s+import", "imports"),
    (r"import\s+(\w+)", "imports"),
]

# System components to track
SYSTEM_COMPONENTS = {
    "cron": {"type": "scheduler", "color": "yellow"},
    "script": {"type": "executor", "color": "blue"},
    "kg": {"type": "storage", "color": "green"},
    "memory": {"type": "storage", "color": "cyan"},
    "event_bus": {"type": "messaging", "color": "magenta"},
}

def init_dirs():
    DEP_DIR.mkdir(parents=True, exist_ok=True)
    if not DEP_GRAPH_FILE.exists():
        DEP_GRAPH_FILE.write_text(json.dumps({"nodes": {}, "edges": [], "version": "1.0"}))
    if not DEP_HISTORY_FILE.exists():
        DEP_HISTORY_FILE.write_text(json.dumps({"history": [], "version": "1.0"}))

def load_graph():
    init_dirs()
    return json.loads(DEP_GRAPH_FILE.read_text())

def save_graph(graph):
    DEP_GRAPH_FILE.write_text(json.dumps(graph, indent=2))

def load_history():
    init_dirs()
    return json.loads(DEP_HISTORY_FILE.read_text())

def save_history(history):
    DEP_HISTORY_FILE.write_text(json.dumps(history, indent=2))

def scan_script(script_path: Path) -> dict:
    """Scan a script for dependencies."""
    if not script_path.exists():
        return {"dependencies": [], "dependents": [], "errors": []}
    
    try:
        content = script_path.read_text()
    except:
        return {"dependencies": [], "dependents": [], "errors": ["Could not read file"]}
    
    deps = []
    errors = []
    
    # Find execution patterns
    for pattern, dep_type in EXECUTION_PATTERNS:
        matches = re.findall(pattern, content)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0] if match[0] else match[1] if len(match) > 1 else match
            if match and match != script_path.name:
                deps.append({
                    "type": dep_type,
                    "target": match,
                    "line_sample": content[max(0, content.find(match)-20):content.find(match)+len(match)+20][:100]
                })
    
    # Find imports
    import_pattern = r"(?:from\s+([\w\.]+)\s+import|import\s+([\w\.]+))"
    for match in re.finditer(import_pattern, content):
        module = match.group(1) or match.group(2)
        if module and not module.startswith("_"):
            deps.append({
                "type": "imports",
                "target": module,
                "line_sample": match.group(0)[:100]
            })
    
    # Find file references
    file_patterns = [
        (r"/([\w/\-_\.]+\.(?:json|md|py|sh))", "references_file"),
        (r"\"([\w/\-_\.]+\.(?:json|md|py|sh))\"", "references_file"),
        (r"'([\w/\-_\.]+\.(?:json|md|py|sh))'", "references_file"),
    ]
    
    for pattern, ref_type in file_patterns:
        for match in re.finditer(pattern, content):
            path = match.group(1)
            if path and not path.startswith("/"):  # Only relative paths
                deps.append({
                    "type": ref_type,
                    "target": path,
                    "line_sample": match.group(0)[:100]
                })
    
    # Find system component interactions
    kg_refs = re.findall(r"(?:kg|KG|knowledge_graph)", content, re.IGNORECASE)
    memory_refs = re.findall(r"(?:memory|MEMORY)", content, re.IGNORECASE)
    cron_refs = re.findall(r"(?:cron|Cron)", content, re.IGNORECASE)
    event_bus_refs = re.findall(r"(?:event_bus|eventBus|EventBus)", content, re.IGNORECASE)
    
    return {
        "dependencies": deps,
        "dependents": [],
        "errors": errors,
        "metrics": {
            "kg_interactions": len(kg_refs),
            "memory_interactions": len(memory_refs),
            "cron_interactions": len(cron_refs),
            "event_bus_interactions": len(event_bus_refs)
        },
        "size_bytes": len(content)
    }

def scan_all_scripts():
    """Scan all scripts in the scripts directory."""
    print("[*] Scanning scripts directory...")
    
    scripts = list(SCRIPTS_DIR.glob("*.py")) + list(SCRIPTS_DIR.glob("*.sh"))
    results = {}
    
    for script in scripts:
        name = script.name
        print(f"  Scanning: {name}...")
        results[name] = scan_script(script)
    
    return results

def build_dependency_graph(scan_results: dict):
    """Build dependency graph from scan results."""
    graph = load_graph()
    
    # Add nodes
    for script_name, data in scan_results.items():
        if script_name not in graph["nodes"]:
            graph["nodes"][script_name] = {
                "type": "script",
                "file": script_name,
                "dependencies": [],
                "dependents": [],
                "first_seen": datetime.now(timezone.utc).isoformat()
            }
        
        node = graph["nodes"][script_name]
        node["metrics"] = data.get("metrics", {})
        node["size_bytes"] = data.get("size_bytes", 0)
        
        # Update dependencies
        new_deps = []
        for dep in data.get("dependencies", []):
            target = dep["target"]
            
            # Normalize target name
            if target.endswith(".py"):
                target = target.split("/")[-1]
            
            if target not in new_deps:
                new_deps.append(target)
                
                # Add edge
                edge_id = f"{script_name}--{dep['type']}-->{target}"
                if not any(e.get("id") == edge_id for e in graph["edges"]):
                    graph["edges"].append({
                        "id": edge_id,
                        "from": script_name,
                        "to": target,
                        "type": dep["type"],
                        "weight": 0.8,
                        "created_at": datetime.now(timezone.utc).isoformat()
                    })
                
                # Update node dependency lists
                if target not in node["dependencies"]:
                    node["dependencies"].append(target)
        
        # Update dependents (reverse dependency)
        for dep in data.get("dependencies", []):
            target = dep["target"]
            if target.endswith(".py"):
                target = target.split("/")[-1]
            
            if target not in graph["nodes"]:
                graph["nodes"][target] = {
                    "type": "unknown",
                    "file": target,
                    "dependencies": [],
                    "dependents": [],
                    "first_seen": datetime.now(timezone.utc).isoformat()
                }
            
            if script_name not in graph["nodes"][target]["dependents"]:
                graph["nodes"][target]["dependents"].append(script_name)
    
    save_graph(graph)
    return graph

def find_dependencies(component_name: str):
    """Find all dependencies for a component."""
    graph = load_graph()
    
    if component_name not in graph["nodes"]:
        print(f"[!] Component '{component_name}' not found in graph.")
        return
    
    node = graph["nodes"][component_name]
    
    print(f"\n📦 Dependencies for: {component_name}")
    print(f"  Type: {node.get('type', 'unknown')}")
    print(f"  Dependencies: {len(node.get('dependencies', []))}")
    for dep in node.get("dependencies", []):
        dep_node = graph["nodes"].get(dep, {})
        print(f"    → {dep} ({dep_node.get('type', '?')})")
    
    print(f"\n  Dependents: {len(node.get('dependents', []))}")
    for dep in node.get("dependents", []):
        dep_node = graph["nodes"].get(dep, {})
        print(f"    ← {dep} ({dep_node.get('type', '?')})")

def trace_chain(component_name: str, max_depth: int = 5):
    """Trace dependency chain from a component."""
    graph = load_graph()
    
    if component_name not in graph["nodes"]:
        print(f"[!] Component '{component_name}' not found.")
        return
    
    def trace(name: str, depth: int = 0, visited: set = None):
        if visited is None:
            visited = set()
        if depth > max_depth or name in visited:
            return
        visited.add(name)
        
        indent = "  " * depth
        node = graph["nodes"].get(name, {})
        print(f"{indent}├─ {name} ({node.get('type', '?')})")
        
        for dep in node.get("dependencies", []):
            trace(dep, depth + 1, visited)
    
    print(f"\n🔍 Dependency Chain for: {component_name}\n")
    trace(component_name)

def find_critical_path():
    """Find the most interconnected components."""
    graph = load_graph()
    
    # Count connections
    connection_count = {}
    for node_name, node in graph["nodes"].items():
        connections = len(node.get("dependencies", [])) + len(node.get("dependents", []))
        connection_count[node_name] = connections
    
    # Sort by connection count
    sorted_components = sorted(connection_count.items(), key=lambda x: -x[1])
    
    print("\n🔴 Critical Components (most connections):\n")
    for name, count in sorted_components[:10]:
        node = graph["nodes"].get(name, {})
        node_type = node.get("type", "?")
        print(f"  {count:3} connections | {name} ({node_type})")

def generate_graph_output():
    """Generate a simple text-based graph."""
    graph = load_graph()
    
    print("\n📊 Dependency Graph")
    print("=" * 60)
    
    # Group by type
    by_type = defaultdict(list)
    for name, node in graph["nodes"].items():
        by_type[node.get("type", "unknown")].append(name)
    
    for node_type, nodes in sorted(by_type.items()):
        print(f"\n[{node_type}] ({len(nodes)} components)")
        for name in sorted(nodes)[:15]:
            node = graph["nodes"][name]
            deps = len(node.get("dependencies", []))
            dependents = len(node.get("dependents", []))
            print(f"  • {name}: {deps} deps, {dependents} dependents")
        if len(nodes) > 15:
            print(f"  ... and {len(nodes) - 15} more")

def dependency_stats():
    """Show dependency statistics."""
    graph = load_graph()
    
    total_nodes = len(graph["nodes"])
    total_edges = len(graph["edges"])
    
    # Type distribution
    type_dist = defaultdict(int)
    for node in graph["nodes"].values():
        type_dist[node.get("type", "unknown")] += 1
    
    # Edge type distribution
    edge_type_dist = defaultdict(int)
    for edge in graph["edges"]:
        edge_type_dist[edge.get("type", "unknown")] += 1
    
    # Most depended upon
    dependent_count = {name: len(node.get("dependents", [])) for name, node in graph["nodes"].items()}
    most_depended = sorted(dependent_count.items(), key=lambda x: -x[1])[:5]
    
    # Most dependencies
    dep_count = {name: len(node.get("dependencies", [])) for name, node in graph["nodes"].items()}
    most_deps = sorted(dep_count.items(), key=lambda x: -x[1])[:5]
    
    print("\n📊 Dependency Statistics")
    print("=" * 50)
    print(f"  Total Components: {total_nodes}")
    print(f"  Total Edges:      {total_edges}")
    
    print(f"\n  By Type:")
    for t, c in sorted(type_dist.items(), key=lambda x: -x[1]):
        print(f"    {t:15} {c}")
    
    print(f"\n  Edge Types:")
    for t, c in sorted(edge_type_dist.items(), key=lambda x: -x[1]):
        print(f"    {t:15} {c}")
    
    print(f"\n  Most Depended Upon:")
    for name, count in most_depended:
        print(f"    {count:3}x {name}")
    
    print(f"\n  Most Dependencies:")
    for name, count in most_deps:
        print(f"    {count:3}x {name}")

def validate_dependencies():
    """Check for broken or circular dependencies."""
    graph = load_graph()
    
    broken = []
    circular = []
    
    for node_name, node in graph["nodes"].items():
        for dep in node.get("dependencies", []):
            if dep not in graph["nodes"]:
                broken.append((node_name, dep))
    
    # Simple circular dependency check
    def has_cycle(node, visited, rec_stack):
        visited.add(node)
        rec_stack.add(node)
        
        for dep in graph["nodes"].get(node, {}).get("dependencies", []):
            if dep not in visited:
                if has_cycle(dep, visited, rec_stack):
                    return True
            elif dep in rec_stack:
                circular.append((node, dep))
                return True
        
        rec_stack.remove(node)
        return False
    
    visited = set()
    for node in graph["nodes"]:
        if node not in visited:
            has_cycle(node, visited, set())
    
    print("\n🔍 Dependency Validation")
    print("=" * 50)
    
    if broken:
        print(f"\n  ❌ Broken Dependencies: {len(broken)}")
        for from_node, to_node in broken[:10]:
            print(f"    {from_node} → {to_node} (target not found)")
    else:
        print(f"\n  ✅ No broken dependencies")
    
    if circular:
        print(f"\n  ⚠️  Circular Dependencies: {len(circular)}")
        for from_node, to_node in circular[:10]:
            print(f"    {from_node} → {to_node}")
    else:
        print(f"  ✅ No circular dependencies")

def scan():
    """Full scan and graph build."""
    print("[*] Starting dependency scan...\n")
    
    results = scan_all_scripts()
    print(f"\n[*] Scanned {len(results)} scripts.")
    
    graph = build_dependency_graph(results)
    print(f"[*] Built graph with {len(graph['nodes'])} nodes and {len(graph['edges'])} edges.")
    
    # Save history
    history = load_history()
    history["history"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scripts_scanned": len(results),
        "nodes": len(graph["nodes"]),
        "edges": len(graph["edges"])
    })
    save_history(history)
    
    print("[+] Done.")
    return graph

def main():
    parser = argparse.ArgumentParser(description="Dependency Tracker")
    parser.add_argument("--scan", action="store_true", help="Scan all scripts and build graph")
    parser.add_argument("--trace", metavar="NAME", help="Trace dependency chain")
    parser.add_argument("--find", metavar="NAME", help="Find dependencies for component")
    parser.add_argument("--graph", action="store_true", help="Generate graph output")
    parser.add_argument("--stats", action="store_true", help="Show dependency statistics")
    parser.add_argument("--validate", action="store_true", help="Validate dependencies")
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(0)
    
    if args.scan:
        scan()
    
    if args.trace:
        trace_chain(args.trace)
    
    if args.find:
        find_dependencies(args.find)
    
    if args.graph:
        generate_graph_output()
    
    if args.stats:
        dependency_stats()
    
    if args.validate:
        validate_dependencies()

if __name__ == "__main__":
    main()
