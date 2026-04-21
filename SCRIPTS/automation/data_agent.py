#!/usr/bin/env python3
"""
Data Agent — Sir HazeClaw Multi-Agent Architecture
=================================================
Dedicated analytics + system maintenance agent.

Role: Analyst + System Maintenance
- Learning Loop execution, KG quality, Metrics
- Script Health Check (broken symlinks, wrong paths, missing scripts)
- Doc Audit (staleness detection)
- Cron Redundancy Detection
- KG Health (80% orphan threshold for CEO KG)

Usage:
    python3 data_agent.py --collect          # Collect learning signals
    python3 data_agent.py --metrics         # Update metrics
    python3 data_agent.py --kg-maintain     # KG quality maintenance
    python3 data_agent.py --script-health    # Script + Cron health check
    python3 data_agent.py --doc-audit        # Doc staleness audit
    python3 data_agent.py --cron-redundancy  # Cron redundancy check
    python3 data_agent.py --full             # Full cycle (all of the above)

Phase 3 of Multi-Agent Architecture — Enhanced 2026-04-18
"""

import os
import sys
import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict
from urllib.parse import urlparse

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
CEO = WORKSPACE / "ceo"
SCRIPTS_DIR = WORKSPACE / "SCRIPTS" / "automation"
CEO_SCRIPTS = CEO / "scripts"
DATA_DIR = WORKSPACE / "data"
EVENTS_DIR = DATA_DIR / "events"
LOGS_DIR = WORKSPACE / "logs"
KG_PATH = CEO / "memory" / "kg" / "knowledge_graph.json"
DATA_STATE_FILE = DATA_DIR / "data_agent_state.json"
STATE_FILE = CEO / "memory" / "system_health_state.json"

# Config — CEO KG has 98%+ orphan rate by design, threshold is 80%
KG_ORPHAN_THRESHOLD = 0.80
STALE_DOC_DAYS = 30
CRON_SCHEDULE_FILE = "/tmp/openclaw_crons.json"

def log(msg: str, level: str = "INFO"):
    """Simple logging."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / "data_agent.log"
    entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": msg
    }
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")

# ============ STATE ============

def load_state() -> Dict:
    if STATE_FILE.exists():
        try:
            return json.load(open(STATE_FILE))
        except:
            pass
    return {
        "last_full_cycle": None,
        "cycles_run": 0,
        "script_issues": [],
        "doc_issues": [],
        "cron_issues": [],
        "kg_health": {},
        "last_script_check": None,
        "last_doc_audit": None,
        "last_cron_check": None,
    }

def save_state(state: Dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

# ============ KG ============

def load_kg() -> Dict:
    if KG_PATH.exists():
        try:
            return json.load(open(KG_PATH))
        except:
            return {"entities": {}, "relations": []}
    return {"entities": {}, "relations": []}

def get_kg_connected_entities(kg: Dict) -> Set[str]:
    """Get all entity IDs that have relations (embedded or top-level)."""
    connected = set()
    
    # Top-level relations
    top_rel = kg.get("relations", {})
    if isinstance(top_rel, dict):
        for r in top_rel.values():
            if isinstance(r, dict):
                if r.get("from"): connected.add(r["from"])
                if r.get("to"): connected.add(r["to"])
    elif isinstance(top_rel, list):
        for r in top_rel:
            if isinstance(r, dict):
                if r.get("source"): connected.add(r["source"])
                if r.get("target"): connected.add(r["target"])
    
    # Embedded relations (CEO KG format: entity.relations = [{target, type}])
    for eid, ent in kg.get("entities", {}).items():
        for rel in ent.get("relations", []):
            if isinstance(rel, dict):
                if rel.get("target"): connected.add(rel["target"])
                if rel.get("source"): connected.add(rel["source"])
            elif isinstance(rel, str):
                connected.add(rel)
    
    return connected

def maintain_kg_quality() -> Dict:
    """KG quality check with CEO KG–correct 80% orphan threshold."""
    kg = load_kg()
    entities = kg.get("entities", {})
    connected = get_kg_connected_entities(kg)
    
    entity_ids = set(entities.keys())
    orphans = entity_ids - connected
    orphan_pct = len(orphans) / len(entity_ids) if entity_ids else 0
    
    result = {
        "entity_count": len(entity_ids),
        "connected_count": len(connected),
        "orphan_count": len(orphans),
        "orphan_pct": orphan_pct,
        "healthy": orphan_pct <= KG_ORPHAN_THRESHOLD,
        "threshold": KG_ORPHAN_THRESHOLD,
        "recommendation": None,
    }
    
    if orphan_pct > KG_ORPHAN_THRESHOLD:
        result["recommendation"] = f"Orphan rate {orphan_pct:.1%} exceeds {KG_ORPHAN_THRESHOLD:.1%}"
    else:
        result["recommendation"] = f"Orphan rate {orphan_pct:.1%} within acceptable range"
    
    return result

# ============ SCRIPT HEALTH ============

def get_cron_scripts() -> Dict[str, Tuple[str, str]]:
    """Get all scripts referenced by cron jobs. Returns {script_path: (cron_name, job_id)}."""
    # Try reading from OpenClaw's internal cron store first
    cron_store = Path("/home/clawbot/.openclaw/cron/jobs.json")
    scripts = {}
    
    if cron_store.exists():
        try:
            data = json.loads(cron_store.read_text())
            jobs = data if isinstance(data, list) else data.get('jobs', [])
            for job in jobs:
                msg = job.get('payload', {}).get('message', '')
                job_name = job.get('name', 'unnamed')
                job_id = job.get('id', '')[:8]
                # Extract absolute paths
                for p in re.findall(r'(/[^"\s]+\.(?:py|sh))', str(msg)):
                    if p.startswith("/"):
                        scripts[p] = (job_name, job_id)
            return scripts
        except Exception as e:
            log(f"Failed to read cron store: {e}", "WARN")
    
    # Fallback: try openclaw CLI
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list", "--json"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return {}
        data = json.loads(result.stdout)
        for job in data.get("jobs", []):
            msg = job.get("payload", {}).get("message", "")
            job_name = job.get("name", "unnamed")
            job_id = job.get("id", "")[:8]
            for p in re.findall(r'(/[^"\s]+\.(?:py|sh))', str(msg)):
                if p.startswith("/"):
                    scripts[p] = (job_name, job_id)
    except Exception as e:
        log(f"openclaw cron list failed: {e}", "WARN")
    
    return scripts

def check_script_health() -> Dict:
    """Check all cron scripts for existence, symlinks, path correctness."""
    scripts = get_cron_scripts()
    issues = []
    checked = set()
    
    for script_path, (cron_name, job_id) in scripts.items():
        if script_path in checked:
            continue
        checked.add(script_path)
        
        p = Path(script_path)
        
        # Check existence
        if not p.exists():
            # Broken symlink?
            if p.is_symlink():
                target = p.resolve()
                if not target.exists():
                    issues.append({
                        "type": "broken_symlink",
                        "script": script_path,
                        "cron": cron_name,
                        "job_id": job_id,
                        "detail": f"symlink points to non-existent: {target}",
                        "severity": "CRITICAL",
                    })
            else:
                issues.append({
                    "type": "missing_script",
                    "script": script_path,
                    "cron": cron_name,
                    "job_id": job_id,
                    "detail": "Script does not exist",
                    "severity": "CRITICAL",
                })
            continue
        
        # Check if executable for shell scripts
        if script_path.endswith(".sh"):
            if not os.access(p, os.X_OK):
                issues.append({
                    "type": "not_executable",
                    "script": script_path,
                    "cron": cron_name,
                    "job_id": job_id,
                    "detail": "Shell script not executable",
                    "severity": "LOW",
                })
        
        # Check for wrong path patterns (scripts/ vs SCRIPTS/ etc)
        path_lower = script_path.lower()
        if "/workspace/scripts/" in script_path:
            # Check if script exists there or in SCRIPTS/
            alt_path = script_path.replace("/workspace/scripts/", "/workspace/SCRIPTS/")
            if not Path(alt_path).exists() and not p.exists():
                pass  # Already handled as missing
        
        # Check if it's a symlink that points to another symlink (double symlink = likely broken)
        if p.is_symlink():
            target = p.resolve()
            if target.is_symlink():
                issues.append({
                    "type": "double_symlink",
                    "script": script_path,
                    "cron": cron_name,
                    "job_id": job_id,
                    "detail": f"Double symlink chain: {p} -> {target}",
                    "severity": "HIGH",
                })
    
    return {
        "scripts_checked": len(checked),
        "issues": issues,
        "critical_count": sum(1 for i in issues if i["severity"] == "CRITICAL"),
        "high_count": sum(1 for i in issues if i["severity"] == "HIGH"),
        "low_count": sum(1 for i in issues if i["severity"] == "LOW"),
        "healthy": len(issues) == 0,
    }

# ============ DOC AUDIT ============

def check_doc_audit() -> Dict:
    """Check for stale docs (>30 days old or in wrong location)."""
    docs_dir = CEO / "docs"
    issues = []
    total = 0
    
    stale_threshold = datetime.now() - timedelta(days=STALE_DOC_DAYS)
    
    # Check docs/ directory
    if docs_dir.exists():
        for f in docs_dir.glob("*.md"):
            total += 1
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if mtime < stale_threshold:
                issues.append({
                    "type": "stale_doc",
                    "file": f.name,
                    "path": str(f.relative_to(CEO)),
                    "mtime": mtime.isoformat(),
                    "age_days": (datetime.now() - mtime).days,
                    "severity": "MEDIUM",
                })
    
    # Check architecture/
    arch_dir = docs_dir / "architecture"
    if arch_dir.exists():
        for f in arch_dir.glob("*.md"):
            total += 1
    
    # Check _archive_plans/
    arch_dir = docs_dir / "_archive_plans"
    if arch_dir.exists():
        for f in arch_dir.glob("*.md"):
            total += 1
    
    # Check docs without index (orphan docs)
    for f in (docs_dir).glob("*.md"):
        if f.name not in ["INDEX.md"] and not f.name.startswith("_"):
            # Doc without proper index entry
            pass
    
    return {
        "docs_total": total,
        "issues": issues,
        "stale_count": len(issues),
        "healthy": len(issues) == 0,
    }

# ============ CRON REDUNDANCY ============

def check_cron_redundancy() -> Dict:
    """Detect crons with similar payloads that might be redundant."""
    result = subprocess.run(
        ["openclaw", "cron", "list", "--json"],
        capture_output=True, text=True, timeout=15
    )
    if result.returncode != 0:
        return {"error": "Could not fetch cron list"}
    
    data = json.loads(result.stdout)
    jobs = data.get("jobs", [])
    
    # Normalize payload for comparison
    def normalize(msg: str) -> str:
        # Remove timestamps, numbers, specific paths
        n = re.sub(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}', 'T', msg)
        n = re.sub(r'\d+', 'N', n)
        n = re.sub(r'(python3?\s+)(/[^\s]+)', r'\1SCRIPT', n)
        n = re.sub(r'/home/clawbot/[^\s]+', '', n)
        n = re.sub(r'\s+', ' ', n).strip().lower()
        return n[:80]
    
    # Group by normalized payload
    groups = defaultdict(list)
    for job in jobs:
        norm = normalize(job.get("payload", {}).get("message", ""))
        groups[norm].append({
            "name": job.get("name", "unnamed")[:50],
            "id": job.get("id", "")[:8],
            "enabled": job.get("enabled", False),
            "schedule": job.get("schedule", {}).get("expr", "unknown"),
        })
    
    # Find groups with >1 cron
    redundancies = []
    for norm, cron_list in groups.items():
        if len(cron_list) > 1 and len(norm) > 20:
            enabled = [c["name"] for c in cron_list if c["enabled"]]
            if len(enabled) > 1:
                redundancies.append({
                    "pattern": norm[:60],
                    "crons": cron_list,
                    "enabled_count": len(enabled),
                    "severity": "MEDIUM" if len(enabled) <= 2 else "HIGH",
                })
    
    return {
        "total_crons": len(jobs),
        "redundancy_groups": len(redundancies),
        "redundancies": redundancies,
        "healthy": len(redundancies) == 0,
    }

# ============ FULL CYCLE ============

def run_full_cycle() -> Dict:
    """Run complete data agent cycle."""
    state = load_state()
    results = {
        "timestamp": datetime.now().isoformat(),
        "kg_health": None,
        "script_health": None,
        "doc_audit": None,
        "cron_redundancy": None,
        "alerts": [],
    }
    
    # KG Health
    kg = maintain_kg_quality()
    results["kg_health"] = kg
    if not kg["healthy"]:
        results["alerts"].append({
            "type": "kg_orphan_rate",
            "severity": "HIGH",
            "message": kg["recommendation"],
        })
    state["kg_health"] = kg
    
    # Script Health
    scripts = check_script_health()
    results["script_health"] = scripts
    if scripts["issues"]:
        for issue in scripts["issues"]:
            if issue["severity"] in ("CRITICAL", "HIGH"):
                results["alerts"].append({
                    "type": f"script_{issue['type']}",
                    "severity": issue["severity"],
                    "message": f"[{issue['cron']}] {issue['script']}: {issue['detail']}",
                })
    state["script_issues"] = scripts["issues"]
    state["last_script_check"] = datetime.now().isoformat()
    
    # Doc Audit
    docs = check_doc_audit()
    results["doc_audit"] = docs
    if docs["issues"]:
        results["alerts"].append({
            "type": "stale_docs",
            "severity": "LOW",
            "message": f"{docs['stale_count']} stale docs (>30 days)",
        })
    state["doc_issues"] = docs["issues"]
    state["last_doc_audit"] = datetime.now().isoformat()
    
    # Cron Redundancy
    cron_red = check_cron_redundancy()
    results["cron_redundancy"] = cron_red
    if cron_red.get("redundancies"):
        for r in cron_red["redundancies"]:
            results["alerts"].append({
                "type": "cron_redundancy",
                "severity": r["severity"],
                "message": f"{r['enabled_count']} crons with similar payloads",
            })
    state["cron_issues"] = cron_red
    state["last_cron_check"] = datetime.now().isoformat()
    
    # Update state
    state["last_full_cycle"] = datetime.now().isoformat()
    state["cycles_run"] = state.get("cycles_run", 0) + 1
    save_state(state)
    
    return results

# ============ OUTPUT ============

def print_results(results: Dict):
    """Print data agent results."""
    print(f"\n📊 Data Agent — {results['timestamp']}")
    print("=" * 60)
    
    # KG
    kg = results.get("kg_health", {})
    kg_status = "✅" if kg.get("healthy") else "⚠️"
    print(f"\n{kg_status} KG Health:")
    print(f"   Entities: {kg.get('entity_count', 0)} | Connected: {kg.get('connected_count', 0)}")
    print(f"   Orphans: {kg.get('orphan_count', 0)} ({kg.get('orphan_pct', 0):.1%})")
    print(f"   {kg.get('recommendation', '')}")
    
    # Script Health
    sh = results.get("script_health", {})
    sh_status = "✅" if sh.get("healthy") else "⚠️"
    print(f"\n{sh_status} Script Health ({sh.get('scripts_checked', 0)} checked):")
    if sh.get("issues"):
        for issue in sh["issues"][:5]:
            print(f"   [{issue['severity']}] {issue['cron']}: {issue['detail'][:50]}")
    else:
        print("   All scripts OK")
    
    # Doc Audit
    da = results.get("doc_audit", {})
    da_status = "✅" if da.get("healthy") else "⚠️"
    print(f"\n{da_status} Doc Audit ({da.get('docs_total', 0)} docs):")
    if da.get("issues"):
        for issue in da["issues"][:3]:
            print(f"   [STALE] {issue['file']} ({issue['age_days']} days old)")
    else:
        print("   All docs OK")
    
    # Cron Redundancy
    cr = results.get("cron_redundancy", {})
    cr_status = "✅" if cr.get("healthy") else "⚠️"
    print(f"\n{cr_status} Cron Redundancy ({cr.get('total_crons', 0)} total):")
    if cr.get("redundancies"):
        for r in cr["redundancies"][:3]:
            print(f"   [{r['severity']}] {r['enabled_count']} similar crons")
    else:
        print("   No redundancies detected")
    
    # Alerts
    alerts = results.get("alerts", [])
    if alerts:
        print(f"\n🚨 ALERTS ({len(alerts)}):")
        for a in alerts:
            print(f"   [{a['severity']}] {a['message']}")
    else:
        print(f"\n✅ All systems healthy — no alerts")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Data Agent — Analytics + System Maintenance")
    parser.add_argument("--collect", action="store_true", help="Collect learning signals")
    parser.add_argument("--metrics", action="store_true", help="Update metrics")
    parser.add_argument("--kg-maintain", action="store_true", help="KG quality maintenance")
    parser.add_argument("--script-health", action="store_true", help="Script + Cron health check")
    parser.add_argument("--doc-audit", action="store_true", help="Doc staleness audit")
    parser.add_argument("--cron-redundancy", action="store_true", help="Cron redundancy check")
    parser.add_argument("--full", action="store_true", help="Full cycle")
    args = parser.parse_args()
    
    if args.collect:
        # Legacy support
        print("📥 Collect not yet implemented in enhanced version")
    
    elif args.metrics:
        kg = maintain_kg_quality()
        print(f"🔧 KG: {kg['entity_count']} entities, {kg['orphan_count']} orphans ({kg['orphan_pct']:.1%})")
        print(f"   {kg['recommendation']}")
    
    elif args.kg_maintain:
        kg = maintain_kg_quality()
        status = "✅" if kg["healthy"] else "⚠️"
        print(f"{status} KG Health: {kg['orphan_count']} orphans ({kg['orphan_pct']:.1%})")
        if not kg["healthy"]:
            print(f"   {kg['recommendation']}")
    
    elif args.script_health:
        sh = check_script_health()
        status = "✅" if sh["healthy"] else "⚠️"
        print(f"{status} Script Health: {sh['scripts_checked']} checked, {len(sh['issues'])} issues")
        for issue in sh["issues"]:
            print(f"   [{issue['severity']}] {issue['detail']}")
    
    elif args.doc_audit:
        da = check_doc_audit()
        status = "✅" if da["healthy"] else "⚠️"
        print(f"{status} Doc Audit: {da['docs_total']} docs, {da['stale_count']} stale")
        for issue in da["issues"]:
            print(f"   [STALE] {issue['file']} ({issue['age_days']} days)")
    
    elif args.cron_redundancy:
        cr = check_cron_redundancy()
        status = "✅" if cr["healthy"] else "⚠️"
        print(f"{status} Cron Redundancy: {cr['total_crons']} crons, {cr['redundancy_groups']} overlaps")
        for r in cr.get("redundancies", []):
            print(f"   [{r['severity']}] {r['enabled_count']} crons: {[c['name'] for c in r['crons'][:2]]}")
    
    elif args.full:
        results = run_full_cycle()
        print_results(results)
    
    else:
        results = run_full_cycle()
        print_results(results)

if __name__ == "__main__":
    main()
