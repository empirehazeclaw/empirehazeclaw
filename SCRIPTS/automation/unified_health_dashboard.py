#!/usr/bin/env python3
"""
Unified Health Dashboard — Phase 5 of Improvement Plan
======================================================
Single pane of glass for all CEO system health metrics.

Combines:
- Integration Dashboard (KG, Learning, Events)
- Cron Health
- Event Bus Stats
- Memory Usage
- Disk Usage

Usage:
  python3 unified_health_dashboard.py          # Full dashboard
  python3 unified_health_dashboard.py --check  # Quick health check
  python3 unified_health_dashboard.py --alert  # Show only alerts
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")

# Thresholds
THRESHOLDS = {
    "kg_orphan_rate": 0.50,      # Alert if >50% orphans
    "kg_entities": {"min": 100, "max": 2000},  # Expected range
    "disk_usage": 0.85,            # Alert if >85% disk used
    "memory_usage": 0.85,          # Alert if >85% memory used
    "event_backlog": 1000,         # Alert if >1000 unprocessed events
    "cron_errors": 3,             # Alert if >3 cron errors in 24h
    "learning_score": {"min": 0.60},  # Alert if score <0.60
}


def get_kg_health() -> Dict:
    """Get KG health metrics."""
    kg_path = WORKSPACE / "ceo/memory/kg/knowledge_graph.json"
    if not kg_path.exists():
        return {"status": "ERROR", "message": "KG not found"}
    
    kg = json.loads(kg_path.read_text())
    entities = kg.get("entities", {})
    relations = kg.get("relations", {})
    
    # Count orphans
    linked = set()
    if isinstance(relations, dict):
        for r in relations.values():
            if isinstance(r, dict):
                if r.get("from"): linked.add(r["from"])
                if r.get("to"): linked.add(r["to"])
    elif isinstance(relations, list):
        for r in relations:
            if r.get("source"): linked.add(r["source"])
            if r.get("target"): linked.add(r["target"])
    
    for eid, entity in entities.items():
        for rel in entity.get("relations", []):
            if isinstance(rel, dict):
                if rel.get("target"): linked.add(rel["target"])
                if rel.get("source"): linked.add(rel["source"])
            elif isinstance(rel, str):
                linked.add(rel)
    
    orphans = len(entities) - len(linked)
    orphan_rate = orphans / len(entities) if entities else 0
    
    return {
        "status": "OK" if orphan_rate < THRESHOLDS["kg_orphan_rate"] else "WARNING",
        "total_entities": len(entities),
        "linked_entities": len(linked),
        "orphan_entities": orphans,
        "orphan_rate": orphan_rate,
        "total_relations": len(relations) if isinstance(relations, dict) else len(relations),
        "last_updated": kg.get("last_updated", "unknown")
    }


def get_event_bus_stats() -> Dict:
    """Get Event Bus statistics."""
    event_file = WORKSPACE / "data/events/events.jsonl"
    if not event_file.exists():
        return {"status": "ERROR", "message": "Event file not found"}
    
    lines = [l for l in event_file.read_text().strip().split("\n") if l.strip()]
    
    # Count by type
    by_type = {}
    last_24h = 0
    cutoff = datetime.now() - timedelta(hours=24)
    
    for line in lines:
        try:
            evt = json.loads(line)
            t = evt.get("type", "unknown")
            by_type[t] = by_type.get(t, 0) + 1
            if datetime.fromisoformat(evt.get("timestamp", "2020")) > cutoff:
                last_24h += 1
        except:
            pass
    
    total = len(lines)
    
    return {
        "status": "OK" if total < THRESHOLDS["event_backlog"] else "WARNING",
        "total_events": total,
        "last_24h": last_24h,
        "by_type": dict(sorted(by_type.items(), key=lambda x: -x[1])[:10]),
        "top_event_type": max(by_type.items(), key=lambda x: x[1])[0] if by_type else None
    }


def get_consumer_stats() -> Dict:
    """Get event consumer statistics."""
    state_file = WORKSPACE / "data/events/consumer_state.json"
    agent_state = WORKSPACE / "data/events/agent_completed_state.json"
    
    stats = {}
    
    if state_file.exists():
        state = json.loads(state_file.read_text())
        stats["processed_ids"] = len(state.get("processed_ids", []))
    
    if agent_state.exists():
        state = json.loads(agent_state.read_text())
        stats["agent_completed"] = {
            "events_processed": state.get("events_processed", 0),
            "success_count": state.get("success_count", 0),
            "failure_count": state.get("failure_count", 0),
            "tracked_agents": len(state.get("agent_stats", {}))
        }
    
    return {
        "status": "OK",
        "consumer_state": stats
    }


def get_learning_stats() -> Dict:
    """Get Learning Loop statistics."""
    index_file = WORKSPACE / "data/learnings/index.json"
    
    if not index_file.exists():
        return {"status": "ERROR", "message": "Learnings index not found"}
    
    idx = json.loads(index_file.read_text())
    decisions = idx.get("decisions", [])
    recent = idx.get("recent", [])
    strategy_eff = idx.get("strategy_effectiveness", {})
    
    # Calculate success rate
    outcomes = [l.get("outcome") for l in recent[-100:]]
    success_count = outcomes.count("success")
    total_with_outcome = len([o for o in outcomes if o in ("success", "failure")])
    success_rate = success_count / total_with_outcome if total_with_outcome > 0 else 0
    
    return {
        "status": "OK" if success_rate >= THRESHOLDS["learning_score"]["min"] else "WARNING",
        "total_learnings": len(recent),
        "total_decisions": len(decisions),
        "strategy_count": len(strategy_eff),
        "success_rate": success_rate,
        "top_strategies": dict(sorted(strategy_eff.items(), key=lambda x: -x[1])[:5])
    }


def get_system_stats() -> Dict:
    """Get system resource statistics."""
    import subprocess
    
    stats = {}
    
    # Disk usage
    try:
        result = subprocess.run(["df", "-h", "/"], capture_output=True, text=True, timeout=5)
        lines = result.stdout.strip().split("\n")
        if len(lines) > 1:
            parts = lines[1].split()
            stats["disk_total"] = parts[1]
            stats["disk_used"] = parts[2]
            stats["disk_avail"] = parts[3]
            stats["disk_use_pct"] = int(parts[4].rstrip("%"))
    except:
        pass
    
    # Memory usage
    try:
        with open("/proc/meminfo") as f:
            mem = {}
            for line in f:
                if ":" in line:
                    k, v = line.split(":")
                    mem[k.strip()] = v.strip().split()[0]
            total = int(mem.get("MemTotal", 0))
            available = int(mem.get("MemAvailable", 0))
            used = total - available
            stats["memory_total_kb"] = total
            stats["memory_used_kb"] = used
            stats["memory_available_kb"] = available
            stats["memory_use_pct"] = int(used / total * 100) if total > 0 else 0
    except:
        pass
    
    # CPU load
    try:
        with open("/proc/loadavg") as f:
            load = f.read().split()[:3]
            stats["load_avg_1m"] = float(load[0])
            stats["load_avg_5m"] = float(load[1])
            stats["load_avg_15m"] = float(load[2])
    except:
        pass
    
    disk_pct = stats.get("disk_use_pct", 0)
    mem_pct = stats.get("memory_use_pct", 0)
    
    return {
        "status": "OK" if disk_pct < 85 and mem_pct < 85 else "WARNING",
        "disk": {k: v for k, v in stats.items() if k.startswith("disk")},
        "memory": {k: v for k, v in stats.items() if k.startswith("memory")},
        "load": {k: v for k, v in stats.items() if k.startswith("load")}
    }


def get_cron_health() -> Dict:
    """Get cron job health from logs."""
    log_file = WORKSPACE / "logs/cron_idle_detector.log"
    state_file = WORKSPACE / "data/cron_idle_state.json"
    
    # Check recent cron log entries
    errors = 0
    recoveries = 0
    
    if log_file.exists():
        lines = log_file.read_text().split("\n")[-100:]  # Last 100 lines
        for line in lines:
            if "[ERROR]" in line:
                errors += 1
            if "recovered" in line.lower():
                recoveries += 1
    
    # Check state
    last_check = None
    issues = []
    if state_file.exists():
        state = json.loads(state_file.read_text())
        last_check = state.get("last_check")
        issues = state.get("last_issues", [])
    
    return {
        "status": "OK" if errors < THRESHOLDS["cron_errors"] else "WARNING",
        "last_check": last_check,
        "errors_in_log": errors,
        "recoveries": recoveries,
        "current_issues": len(issues),
        "issue_summary": issues[:5] if issues else []
    }


def get_all_alerts() -> List[Dict]:
    """Get all active alerts across all systems."""
    alerts = []
    
    # KG alerts
    kg = get_kg_health()
    if kg.get("status") != "OK":
        alerts.append({
            "source": "KG",
            "severity": "WARNING" if "orphan" in str(kg) else "ERROR",
            "手中的": kg.get("message", f"Orphan rate: {kg.get('orphan_rate', 0):.1%}")
        })
    
    # Event backlog
    eb = get_event_bus_stats()
    if eb.get("total_events", 0) > THRESHOLDS["event_backlog"]:
        alerts.append({
            "source": "Event Bus",
            "severity": "WARNING",
            "message": f"High event backlog: {eb['total_events']}"
        })
    
    # Learning score
    ls = get_learning_stats()
    if ls.get("status") != "OK":
        alerts.append({
            "source": "Learning Loop",
            "severity": "WARNING",
            "message": f"Success rate: {ls.get('success_rate', 0):.1%}"
        })
    
    # System resources
    sys_stats = get_system_stats()
    if sys_stats.get("status") != "OK":
        disk_pct = sys_stats.get("disk", {}).get("disk_use_pct", 0)
        mem_pct = sys_stats.get("memory", {}).get("memory_use_pct", 0)
        if disk_pct > 85:
            alerts.append({
                "source": "Disk",
                "severity": "CRITICAL" if disk_pct > 90 else "WARNING",
                "message": f"Disk usage: {disk_pct}%"
            })
        if mem_pct > 85:
            alerts.append({
                "source": "Memory",
                "severity": "CRITICAL" if mem_pct > 90 else "WARNING",
                "message": f"Memory usage: {mem_pct}%"
            })
    
    # Cron health
    cron = get_cron_health()
    if cron.get("errors_in_log", 0) > THRESHOLDS["cron_errors"]:
        alerts.append({
            "source": "Cron",
            "severity": "WARNING",
            "message": f"{cron['errors_in_log']} errors in recent logs"
        })
    
    return alerts


def print_dashboard():
    """Print full health dashboard."""
    print("=" * 60)
    print("🦞 SIR HAZECLAW — UNIFIED HEALTH DASHBOARD")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)
    
    # System Resources
    print("\n📊 SYSTEM RESOURCES")
    print("-" * 40)
    sys_stats = get_system_stats()
    if "disk" in sys_stats:
        d = sys_stats["disk"]
        print(f"  Disk: {d.get('disk_used','?')}/{d.get('disk_total','?')} ({d.get('disk_use_pct','?')}%)")
    if "memory" in sys_stats:
        m = sys_stats["memory"]
        print(f"  Memory: {m.get('memory_used_kb',0)//1024}MB/{m.get('memory_total_kb',0)//1024}MB ({m.get('memory_use_pct','?')}%)")
    if "load" in sys_stats:
        l = sys_stats["load"]
        print(f"  Load: {l.get('load_avg_1m','?')} (1m) {l.get('load_avg_5m','?')} (5m) {l.get('load_avg_15m','?')} (15m)")
    print(f"  Status: {'✅ ' + sys_stats.get('status', 'OK') if sys_stats.get('status') == 'OK' else '⚠️  WARNING'}")
    
    # KG Health
    print("\n🧠 KNOWLEDGE GRAPH")
    print("-" * 40)
    kg = get_kg_health()
    if "message" in kg and kg.get("status") == "ERROR":
        print(f"  Status: ❌ {kg.get('message')}")
    else:
        print(f"  Entities: {kg.get('total_entities', '?')}")
        print(f"  Relations: {kg.get('total_relations', '?')}")
        print(f"  Orphans: {kg.get('orphan_entities', '?')} ({kg.get('orphan_rate', 0):.1%})")
        print(f"  Status: {'✅ OK' if kg.get('status') == 'OK' else '⚠️  WARNING'}")
    
    # Event Bus
    print("\n📨 EVENT BUS")
    print("-" * 40)
    eb = get_event_bus_stats()
    print(f"  Total Events: {eb.get('total_events', '?')}")
    print(f"  Last 24h: {eb.get('last_24h', '?')}")
    print(f"  Top Type: {eb.get('top_event_type', '?')}")
    print(f"  Status: {'✅ OK' if eb.get('status') == 'OK' else '⚠️  WARNING'}")
    
    # Consumer Stats
    print("\n🔄 EVENT CONSUMERS")
    print("-" * 40)
    cs = get_consumer_stats()
    if "agent_completed" in cs.get("consumer_state", {}):
        ac = cs["consumer_state"]["agent_completed"]
        print(f"  Agent Completed Processed: {ac.get('events_processed', 0)}")
        print(f"  Tracked Agents: {ac.get('tracked_agents', 0)}")
    else:
        print(f"  Consumer State: {len(cs.get('consumer_state', {}))} entries")
    print(f"  Status: ✅ OK")
    
    # Learning Stats
    print("\n📚 LEARNING LOOP")
    print("-" * 40)
    ls = get_learning_stats()
    if "message" in ls and ls.get("status") == "ERROR":
        print(f"  Status: ❌ {ls.get('message')}")
    else:
        print(f"  Total Learnings: {ls.get('total_learnings', '?')}")
        print(f"  Total Decisions: {ls.get('total_decisions', '?')}")
        print(f"  Success Rate: {ls.get('success_rate', 0):.1%}")
        print(f"  Strategies: {ls.get('strategy_count', '?')}")
        print(f"  Status: {'✅ OK' if ls.get('status') == 'OK' else '⚠️  WARNING'}")
    
    # Cron Health
    print("\n⏰ CRON HEALTH")
    print("-" * 40)
    cron = get_cron_health()
    print(f"  Last Check: {cron.get('last_check', 'never')[:19] if cron.get('last_check') else 'never'}")
    print(f"  Errors in Log: {cron.get('errors_in_log', 0)}")
    print(f"  Recoveries: {cron.get('recoveries', 0)}")
    print(f"  Current Issues: {cron.get('current_issues', 0)}")
    print(f"  Status: {'✅ OK' if cron.get('status') == 'OK' else '⚠️  WARNING'}")
    
    # Alerts
    print("\n" + "=" * 60)
    print("🚨 ACTIVE ALERTS")
    print("=" * 60)
    alerts = get_all_alerts()
    if alerts:
        for a in alerts:
            sev = a.get("severity", "INFO")
            icon = "🔴" if sev == "CRITICAL" else "🟡" if sev == "WARNING" else "🔵"
            print(f"  {icon} [{sev}] {a.get('source')}: {a.get('message', a.get('detail', ''))}")
    else:
        print("  ✅ No active alerts")
    
    print("\n" + "=" * 60)


def print_quick_check():
    """Print quick health check summary."""
    alerts = get_all_alerts()
    critical = [a for a in alerts if a.get("severity") == "CRITICAL"]
    warning = [a for a in alerts if a.get("severity") == "WARNING"]
    
    if critical:
        print(f"🔴 {len(critical)} CRITICAL issue(s)")
        for a in critical:
            print(f"   {a.get('source')}: {a.get('message')}")
    elif warning:
        print(f"🟡 {len(warning)} warning(s)")
        for a in warning:
            print(f"   {a.get('source')}: {a.get('message')}")
    else:
        print("✅ All systems healthy")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified Health Dashboard")
    parser.add_argument("--check", action="store_true", help="Quick health check")
    parser.add_argument("--alert", action="store_true", help="Show only alerts")
    
    args = parser.parse_args()
    
    if args.check:
        print_quick_check()
    elif args.alert:
        alerts = get_all_alerts()
        if alerts:
            for a in alerts:
                print(f"[{a.get('severity')}] {a.get('source')}: {a.get('message')}")
        else:
            print("No alerts")
    else:
        print_dashboard()