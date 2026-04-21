#!/usr/bin/env python3
"""
CEO Integration Dashboard — Phase 5
==================================
Unified monitoring for all integrated systems.
Shows: KG health, Event Bus activity, System connections, Integration health.

Usage:
  python3 integration_dashboard.py          # Full dashboard
  python3 integration_dashboard.py --kg     # KG only
  python3 integration_dashboard.py --events # Event Bus only
  python3 integration_dashboard.py --check  # Quick health check

Phase 5 of System Integration Plan
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
KG_PATH = WORKSPACE / "ceo/memory/kg/knowledge_graph.json"
EVENTS_FILE = WORKSPACE / "data/events/events.jsonl"

# Colors for terminal
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

def load_kg() -> dict:
    with open(KG_PATH) as f:
        return json.load(f)

def get_recent_events(minutes: int = 1440) -> list:
    since = datetime.now() - timedelta(minutes=minutes)
    events = []
    if not EVENTS_FILE.exists():
        return events
    with open(EVENTS_FILE) as f:
        for line in f:
            try:
                evt = json.loads(line.strip())
                if datetime.fromisoformat(evt["timestamp"]) > since:
                    events.append(evt)
            except (ValueError, json.JSONDecodeError):
                pass
    return sorted(events, key=lambda x: x["timestamp"])

def check_kg_health() -> dict:
    """KG Health: entities, relations, orphans, types."""
    kg = load_kg()
    entities = kg.get("entities", {})
    relations = kg.get("relations", {})
    
    # Handle dict-based KG (our format: entities is dict, relations is dict)
    if isinstance(entities, dict):
        entity_ids = set(entities.keys())
    else:
        entity_ids = set()
        for e in entities:
            if isinstance(e, dict):
                entity_ids.add(e.get("id"))
            elif isinstance(e, str):
                entity_ids.add(e)
    
    # Check orphans - find entities not referenced in any relation
    linked_entities = set()
    if isinstance(relations, dict):
        for r in relations.values():
            if isinstance(r, dict):
                linked_entities.add(r.get("from"))
                linked_entities.add(r.get("to"))
    elif isinstance(relations, list):
        for r in relations:
            if isinstance(r, dict):
                linked_entities.add(r.get("from"))
                linked_entities.add(r.get("to"))
    
    orphan_count = len(entity_ids - linked_entities)
    
    # Count by type
    if isinstance(entities, dict):
        type_counts = Counter(e.get("type", "unknown") for e in entities.values() if isinstance(e, dict))
    else:
        type_counts = Counter(e.get("type", "unknown") for e in entities if isinstance(e, dict))
    
    orphan_threshold_pct = 40.0  # 40% orphans is healthy
    orphan_pct = (orphan_count / len(entity_ids) * 100) if entity_ids else 0
    
    return {
        "entities": len(entities),
        "relations": len(relations),
        "orphans": orphan_count,
        "orphan_pct": round(orphan_pct, 1),
        "type_counts": dict(type_counts.most_common(10)),
        "healthy": orphan_pct < orphan_threshold_pct
    }

def check_event_bus_health() -> dict:
    """Event Bus Health: event counts, sources, types."""
    events = get_recent_events(1440)  # Last 24h
    
    if not events:
        return {"total": 0, "by_type": {}, "by_source": {}, "healthy": True}
    
    by_type = Counter(e.get("type") for e in events)
    by_source = Counter(e.get("source") for e in events)
    
    # Check for recent activity (last hour)
    recent = [e for e in events if datetime.fromisoformat(e["timestamp"]) > datetime.now() - timedelta(hours=1)]
    
    return {
        "total": len(events),
        "last_hour": len(recent),
        "by_type": dict(by_type),
        "by_source": dict(by_source.most_common(5)),
        "healthy": len(events) > 0
    }

def check_system_connections() -> dict:
    """Check which systems are connected via Event Bus."""
    events = get_recent_events(1440)
    
    sources = set(e.get("source") for e in events)
    
    # Expected sources
    expected = {
        "learning_to_kg_sync": "Learning Loop → KG Bridge",
        "capability_evolver": "Evolver",
        "system_integration": "Integration Scripts",
        "stagnation_detector": "Health Monitor",
        "stagnation_breaker": "Stagnation Handler",
        "gateway": "OpenClaw Gateway",
    }
    
    connected = {s: expected.get(s, s) for s in sources if s in expected}
    missing = {k: v for k, v in expected.items() if k not in sources}
    
    return {
        "connected": connected,
        "missing": missing,
        "health": len(connected) >= 3  # At least 3 systems should be connected
    }

def check_cross_references() -> dict:
    """Verify systems are actually reading from same sources."""
    checks = []
    
    # Check 1: Scripts point to same KG
    scripts_dir = WORKSPACE / "scripts"
    kg_refs = []
    if scripts_dir.exists():
        for f in scripts_dir.glob("*.py"):
            try:
                content = f.read_text()
                if "knowledge_graph" in content:
                    if "ceo/memory/kg" in content:
                        kg_refs.append(("ceo", f.name))
                    elif "core_ultralight" in content:
                        kg_refs.append(("core_ultralight", f.name))
            except (IOError, UnicodeDecodeError):
                pass
    
    core_ultralight_refs = [r for r in kg_refs if r[0] == "core_ultralight"]
    
    checks.append({
        "name": "Single KG",
        "status": "PASS" if not core_ultralight_refs else "FAIL",
        "detail": f"{len(core_ultralight_refs)} scripts still using core_ultralight" if core_ultralight_refs else "All scripts using CEO KG"
    })
    
    # Check 2: Event Bus has events
    events = get_recent_events(1440)
    checks.append({
        "name": "Event Bus Active",
        "status": "PASS" if events else "FAIL",
        "detail": f"{len(events)} events in last 24h"
    })
    
    # Check 3: Learning Loop sync state exists
    sync_state = WORKSPACE / "data/learning_loop/kg_sync_state.json"
    checks.append({
        "name": "Learning Loop Sync",
        "status": "PASS" if sync_state.exists() else "FAIL",
        "detail": "Sync state file exists" if sync_state.exists() else "No sync state"
    })
    
    return {
        "checks": checks,
        "all_pass": all(c["status"] == "PASS" for c in checks)
    }

def print_dashboard():
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}CEO INTEGRATION DASHBOARD — {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # KG Health
    kg = check_kg_health()
    status = f"{GREEN}✅ HEALTHY{RESET}" if kg["healthy"] else f"{RED}❌ ISSUES{RESET}"
    print(f"{BOLD}[KNOWLEDGE GRAPH]{RESET} {status}")
    print(f"  Entities: {kg['entities']} | Relations: {kg['relations']} | Orphans: {kg['orphans']}")
    print(f"  Top Types: {', '.join(f'{k}({v})' for k,v in list(kg['type_counts'].items())[:5])}")
    print()
    
    # Event Bus Health
    eb = check_event_bus_health()
    status = f"{GREEN}✅ ACTIVE{RESET}" if eb["healthy"] else f"{YELLOW}⚠️ INACTIVE{RESET}"
    print(f"{BOLD}[EVENT BUS]{RESET} {status}")
    print(f"  Events (24h): {eb['total']} | Last Hour: {eb['last_hour']}")
    if eb['by_source']:
        print(f"  Sources: {', '.join(f'{k}({v})' for k,v in eb['by_source'].items())}")
    print()
    
    # System Connections
    sc = check_system_connections()
    status = f"{GREEN}✅ {len(sc['connected'])} SYSTEMS{RESET}" if sc["health"] else f"{YELLOW}⚠️ FEW CONNECTIONS{RESET}"
    print(f"{BOLD}[SYSTEM CONNECTIONS]{RESET} {status}")
    if sc['connected']:
        print(f"  Connected: {', '.join(sc['connected'].keys())}")
    if sc['missing']:
        print(f"  {YELLOW}Not seen: {', '.join(sc['missing'].keys())}{RESET}")
    print()
    
    # Cross-Reference Checks
    cr = check_cross_references()
    status = f"{GREEN}✅ ALL PASS{RESET}" if cr["all_pass"] else f"{RED}❌ ISSUES{RESET}"
    print(f"{BOLD}[CROSS-REFERENCE CHECKS]{RESET} {status}")
    for check in cr['checks']:
        icon = f"{GREEN}✓{RESET}" if check["status"] == "PASS" else f"{RED}✗{RESET}"
        print(f"  {icon} {check['name']}: {check['detail']}")
    print()
    
    # Summary
    all_healthy = kg["healthy"] and eb["healthy"] and cr["all_pass"]
    print(f"{BLUE}{'='*60}{RESET}")
    if all_healthy:
        print(f"{GREEN}{BOLD}🎉 ALL SYSTEMS INTEGRATED AND HEALTHY{RESET}")
    else:
        print(f"{YELLOW}{BOLD}⚠️ SOME ISSUES DETECTED — Review above{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def quick_check() -> dict:
    """Just check if everything is connected."""
    kg = check_kg_health()
    eb = check_event_bus_health()
    cr = check_cross_references()
    
    issues = []
    if not kg["healthy"]:
        issues.append(f"KG has {kg['orphans']} orphans ({kg.get('orphan_pct', 0)}%)")
    if not eb["healthy"]:
        issues.append("Event Bus inactive")
    if not cr["all_pass"]:
        for c in cr["checks"]:
            if c["status"] != "PASS":
                issues.append(c["detail"])
    
    return {
        "healthy": len(issues) == 0,
        "issues": issues
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--kg", action="store_true")
    parser.add_argument("--events", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    
    if args.kg:
        kg = check_kg_health()
        print(json.dumps(kg, indent=2, default=str))
    elif args.events:
        eb = check_event_bus_health()
        print(json.dumps(eb, indent=2, default=str))
    elif args.check:
        result = quick_check()
        if result["healthy"]:
            print(f"{GREEN}✅ All systems healthy{RESET}")
        else:
            print(f"{RED}❌ Issues: {', '.join(result['issues'])}{RESET}")
            sys.exit(1)
    else:
        print_dashboard()
