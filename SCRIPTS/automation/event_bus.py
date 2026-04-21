#!/usr/bin/env python3
"""
Event Bus — CEO Cross-System Communication Layer
================================================
Provides a unified event system for all CEO subsystems.
Events are stored in a simple JSON file and can be published/consumed by any system.

Event Types:
  - kg_update            : KG was modified
  - pattern_discovered    : New pattern found by Learning Loop
  - improvement_applied   : Improvement was validated and applied
  - error_detected        : System error detected
  - cron_completed        : A cron job finished
  - sync_completed        : Cross-system sync finished
  - stagnation_detected   : Evolver or Loop in stagnation
  - learning_score_update : Learning Loop score update (Phase 5)
  - learning_cycle_completed : Learning Loop cycle finished (Phase 5)
  - evolver_completed     : Capability Evolver finished (Phase 4)
  - learning_evolver_feedback : Loop feedback to Evolver (Phase 6)
  - meta_pattern_weights_updated : Meta Controller updated weights (Phase 7)
  - learning_meta_feedback : Learning Loop pattern performance to Meta (Phase 7)
  - meta_insight_generated : Meta Controller generated insight (Phase 7)
  - learning_issues_detected : Learning Loop found issues (Phase 8)
  - stagnation_escaped    : Evolver escaped stagnation (Phase 8)

Phase 8 of System Improvement Plan:
  - File locking for concurrent writes
  - Schema validation
  - Event consumer registry

Usage:
  python3 event_bus.py publish --type kg_update --data '{"entity": "Test"}'
  python3 event_bus.py list --type kg_update --since "2026-04-16"
  python3 event_bus.py stats
  python3 event_bus.py consume  # Process unconsumed events

Phase 3 of System Integration Plan
"""

import os
import sys
import json
import argparse
import fcntl
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable
from collections import defaultdict

# Config
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
EVENT_DIR = WORKSPACE / "data" / "events"
EVENT_FILE = EVENT_DIR / "events.jsonl"
EVENT_INDEX = EVENT_DIR / "event_index.json"
EVENT_LOCK = EVENT_DIR / "events.lock"
MAX_EVENTS = 10000  # Keep last 10k events

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger('event_bus')

# Event Schema (Phase 8)
EVENT_SCHEMA = {
    'type': str,
    'source': str,
    'data': dict,
    'timestamp': str,
    'id': str
}

# Event Consumer Registry (Phase 8)
class EventConsumer:
    """Base class for event consumers."""
    def handles(self) -> List[str]:
        """Return list of event types this consumer handles."""
        return []
    
    def consume(self, event: dict) -> bool:
        """Process event. Return True if processed, False to skip."""
        return False
    
    def should_retry(self, event: dict) -> bool:
        """Return True if this consumer should retry later."""
        return False


class LearningIssuesConsumer(EventConsumer):
    """Process learning_issues_detected events."""
    def handles(self) -> List[str]:
        return ['learning_issues_detected']
    
    def consume(self, event: dict) -> bool:
        data = event.get('data', {})
        severity = data.get('severity', 'info')
        if severity == 'HIGH':
            logger.warning(f"HIGH severity issue detected: {data.get('description', 'unknown')}")
        return True


class StagnationConsumer(EventConsumer):
    """Process stagnation_escaped events."""
    def handles(self) -> List[str]:
        return ['stagnation_escaped']
    
    def consume(self, event: dict) -> bool:
        logger.info(f"Stagnation escaped: {event.get('data', {})}")
        return True


class MetaInsightConsumer(EventConsumer):
    """Process meta_insight_generated events — store to KG."""
    def handles(self) -> List[str]:
        return ['meta_insight_generated']
    
    def consume(self, event: dict) -> bool:
        # This would store to KG in a full implementation
        logger.info(f"Meta insight: {event.get('data', {}).get('insight_type', 'unknown')}")
        return True


class PatternWeightConsumer(EventConsumer):
    """Process meta_pattern_weights_updated events."""
    def handles(self) -> List[str]:
        return ['meta_pattern_weights_updated']
    
    def consume(self, event: dict) -> bool:
        data = event.get('data', {})
        patterns = data.get('patterns_count', 0)
        accuracy = data.get('test_accuracy', 0)
        logger.info(f"Pattern weights updated: {patterns} patterns, accuracy={accuracy:.1%}")
        return True


# Consumer Registry
CONSUMERS: List[EventConsumer] = [
    LearningIssuesConsumer(),
    StagnationConsumer(),
    MetaInsightConsumer(),
    PatternWeightConsumer(),
]


def validate_event(event: dict) -> bool:
    """Validate event against schema. Phase 8."""
    for field, expected_type in EVENT_SCHEMA.items():
        if field not in event:
            logger.warning(f"Event missing required field: {field}")
            return False
        if not isinstance(event[field], expected_type):
            logger.warning(f"Event field {field} has wrong type: {type(event[field])}")
            return False
    return True

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
    """Publish an event to the bus with file locking. Phase 8."""
    ensure_dir()
    
    event = {
        "id": f"evt_{int(datetime.now().timestamp() * 1000)}",
        "type": event_type,
        "source": source,
        "severity": severity,
        "data": data,
        "timestamp": datetime.now().isoformat(),
    }
    
    # Phase 8: Validate event schema
    if not validate_event(event):
        logger.error(f"Event validation failed: {event.get('id')}")
        return None
    
    # Phase 8: File locking for concurrent writes
    lock_file = EVENT_LOCK
    try:
        with open(lock_file, 'w') as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            try:
                # Append to file
                with open(EVENT_FILE, 'a') as f:
                    f.write(json.dumps(event) + "\n")
                
                # Update index
                idx = len(open(EVENT_FILE).readlines()) - 1
                _add_to_index(event, idx)
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
    except Exception as e:
        logger.error(f"Failed to publish event: {e}")
        return None
    
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

def process_unconsumed_events(limit: int = 100) -> int:
    """Process unconsumed events through the consumer registry. Phase 8.
    
    Returns number of events processed.
    Each event is processed only once by its first matching consumer.
    """
    processed = 0
    
    # Get all event types that have consumers
    consumer_map = {}  # event_type -> consumer
    for consumer in CONSUMERS:
        for event_type in consumer.handles():
            if event_type not in consumer_map:
                consumer_map[event_type] = consumer
    
    # Process each event type
    for event_type, consumer in consumer_map.items():
        events = list_events(event_type=event_type, limit=limit)
        for event in events:
            try:
                if consumer.consume(event):
                    processed += 1
            except Exception as e:
                logger.error(f"Consumer {consumer.__class__.__name__} failed: {e}")
    
    return processed


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
    
    sub.add_parser("consume", help="Run event consumers on recent events")
    sub.add_parser("consumers", help="List registered event consumers")
    
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
    
    elif args.cmd == "consume":
        print("Running event consumers...")
        processed = process_unconsumed_events()
        print(f"Consumer run complete. Events processed: {processed}")
    
    elif args.cmd == "consumers":
        print("Registered consumers:")
        for c in CONSUMERS:
            print(f"  - {c.__class__.__name__}: {c.handles()}")
    
    else:
        parser.print_help()
