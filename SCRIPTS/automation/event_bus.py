#!/usr/bin/env python3
"""
Event Bus — CEO Cross-System Communication Layer
================================================
Provides a unified event system for all CEO subsystems.
Events are stored in a simple JSON file and can be published/consumed by any system.

Event Types:
  - kg_update       : KG was modified
  - pattern_discovered : New pattern found by Learning Loop
  - improvement_applied : Improvement was validated and applied
  - error_detected  : System error detected
  - cron_completed   : A cron job finished
  - sync_completed   : Cross-system sync finished
  - stagnation_detected : Evolver or Loop in stagnation

Usage:
  python3 event_bus.py publish --type kg_update --data '{"entity": "Test"}'
  python3 event_bus.py list --type kg_update --since "2026-04-16"
  python3 event_bus.py stats

Phase 3 of System Integration Plan
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

# Config
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
EVENT_DIR = WORKSPACE / "data" / "events"
EVENT_FILE = EVENT_DIR / "events.jsonl"
EVENT_INDEX = EVENT_DIR / "event_index.json"
MAX_EVENTS = 10000  # Keep last 10k events

def ensure_dir():
    EVENT_DIR.mkdir(parents=True, exist_ok=True)
    if not EVENT_FILE.exists():
        EVENT_FILE.write_text("")
    if not EVENT_INDEX.exists():
        _rebuild_index()

def _rebuild_index():
    """Rebuild the event index from scratch."""
    index = {
        "by_type": defaultdict(list),
        "by_source": defaultdict(list),
        "chronological": []
    }
    if not EVENT_FILE.exists():
        with open(EVENT_INDEX, 'w') as f:
            json.dump(dict(index), f)
        return index
    
    events = []
    with open(EVENT_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except:
                    pass
    
    for i, evt in enumerate(events):
        t = evt.get("type", "unknown")
        s = evt.get("source", "unknown")
        index["by_type"][t].append(i)
        index["by_source"][s].append(i)
        index["chronological"].append(i)
    
    with open(EVENT_INDEX, 'w') as f:
        json.dump(index, f)
    return index

def _load_index() -> dict:
    if EVENT_INDEX.exists():
        with open(EVENT_INDEX) as f:
            data = json.load(f)
        # Preserve defaultdict behavior
        return {
            "by_type": defaultdict(list, data.get("by_type", {})),
            "by_source": defaultdict(list, data.get("by_source", {})),
            "chronological": data.get("chronological", [])
        }
    return _rebuild_index()

def _add_to_index(evt: dict, idx: int):
    """Add event to index."""
    index = _load_index()
    t = evt.get("type", "unknown")
    s = evt.get("source", "unknown")
    index["by_type"][t].append(idx)
    index["by_source"][s].append(idx)
    index["chronological"].append(idx)
    with open(EVENT_INDEX, 'w') as f:
        json.dump(index, f)

def publish_event(event_type: str, source: str, data: dict, severity: str = "info") -> dict:
    """Publish an event to the bus."""
    ensure_dir()
    
    event = {
        "id": f"evt_{int(datetime.now().timestamp() * 1000)}",
        "type": event_type,
        "source": source,
        "severity": severity,
        "data": data,
        "timestamp": datetime.now().isoformat(),
    }
    
    # Append to file
    with open(EVENT_FILE, 'a') as f:
        f.write(json.dumps(event) + "\n")
    
    # Update index
    idx = len(open(EVENT_FILE).readlines()) - 1
    _add_to_index(event, idx)
    
    # Prune old events if needed
    _prune_events()
    
    return event

def _prune_events():
    """Keep only last MAX_EVENTS lines."""
    with open(EVENT_FILE) as f:
        lines = f.readlines()
    
    if len(lines) > MAX_EVENTS:
        lines = lines[-MAX_EVENTS:]
        with open(EVENT_FILE, 'w') as f:
            f.writelines(lines)
        _rebuild_index()

def list_events(event_type: Optional[str] = None, source: Optional[str] = None,
                since: Optional[str] = None, limit: int = 50) -> List[dict]:
    """List events with optional filters."""
    ensure_dir()
    
    index = _load_index()
    events = []
    
    # Get candidate indices
    if event_type:
        indices = set(index.get("by_type", {}).get(event_type, []))
    elif source:
        indices = set(index.get("by_source", {}).get(source, []))
    else:
        indices = set(index.get("chronological", []))
    
    # Load and filter
    cutoff = None
    if since:
        cutoff = datetime.fromisoformat(since)
    
    with open(EVENT_FILE) as f:
        for i, line in enumerate(f):
            if i not in indices:
                continue
            line = line.strip()
            if not line:
                continue
            try:
                evt = json.loads(line)
                if cutoff and datetime.fromisoformat(evt["timestamp"]) < cutoff:
                    continue
                events.append(evt)
            except:
                pass
    
    # Sort by timestamp desc, limit
    events.sort(key=lambda x: x["timestamp"], reverse=True)
    return events[:limit]

def stats() -> dict:
    """Get event statistics."""
    ensure_dir()
    index = _load_index()
    
    total = len(index.get("chronological", []))
    by_type = {k: len(v) for k, v in index.get("by_type", {}).items()}
    by_source = {k: len(v) for k, v in index.get("by_source", {}).items()}
    
    # Last 24h count
    since_24h = datetime.now() - timedelta(hours=24)
    last_24h = 0
    with open(EVENT_FILE) as f:
        for line in f:
            try:
                evt = json.loads(line.strip())
                if datetime.fromisoformat(evt["timestamp"]) > since_24h:
                    last_24h += 1
            except:
                pass
    
    return {
        "total_events": total,
        "last_24h": last_24h,
        "by_type": by_type,
        "by_source": by_source,
    }

def get_recent_events(minutes: int = 60) -> List[dict]:
    """Get events from the last N minutes."""
    since = datetime.now() - timedelta(minutes=minutes)
    return list_events(since=since.isoformat(), limit=100)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CEO Event Bus")
    sub = parser.add_subparsers(dest="cmd")
    
    p = sub.add_parser("publish", help="Publish an event")
    p.add_argument("--type", required=True, help="Event type")
    p.add_argument("--source", required=True, help="Event source")
    p.add_argument("--severity", default="info", help="Severity: info, warning, error")
    p.add_argument("--data", required=True, help="JSON data")
    
    p = sub.add_parser("list", help="List events")
    p.add_argument("--type", help="Filter by type")
    p.add_argument("--source", help="Filter by source")
    p.add_argument("--since", help="ISO timestamp")
    p.add_argument("--limit", type=int, default=50)
    
    sub.add_parser("stats", help="Show event statistics")
    
    p = sub.add_parser("recent", help="Show recent events")
    p.add_argument("--minutes", type=int, default=60)
    
    args = parser.parse_args()
    
    if args.cmd == "publish":
        data = json.loads(args.data)
        evt = publish_event(args.type, args.source, data, args.severity)
        print(f"Published: {evt['id']}")
    
    elif args.cmd == "list":
        events = list_events(args.type, args.source, args.since, args.limit)
        for e in events:
            print(f"{e['timestamp']} [{e['type']}] {e['source']}: {json.dumps(e['data'])[:80]}")
    
    elif args.cmd == "stats":
        s = stats()
        print(f"Total events: {s['total_events']}")
        print(f"Last 24h: {s['last_24h']}")
        print("\nBy type:")
        for t, c in sorted(s["by_type"].items(), key=lambda x: -x[1]):
            print(f"  {t}: {c}")
        print("\nBy source:")
        for src, c in sorted(s["by_source"].items(), key=lambda x: -x[1]):
            print(f"  {src}: {c}")
    
    elif args.cmd == "recent":
        events = get_recent_events(args.minutes)
        print(f"Events in last {args.minutes} minutes: {len(events)}")
        for e in events[:20]:
            print(f"  {e['timestamp']} [{e['type']}] {e['source']}")
    
    else:
        parser.print_help()
