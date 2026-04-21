#!/usr/bin/env python3
"""
Event Bus In-Process Module — CEO Cross-System Communication
==========================================================

Kann jetzt direkt importiert werden statt subprocess zu spawnen:

    from event_bus_inprocess import EventBus, publish_event, subscribe
    EventBus.publish("kg_update", "learning_loop", {"entity": "test"})

Für Backward Compatibility gibt es auch weiterhin CLI:
    python3 event_bus.py publish --type kg_update --data '{"entity":"Test"}'

Phase 3 Refactor: Subprocess → In-Process
"""

import os
import sys
import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Callable, Optional
from collections import defaultdict
from functools import lru_cache

# Config
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
EVENT_DIR = WORKSPACE / "data" / "events"
EVENT_FILE = EVENT_DIR / "events.jsonl"
EVENT_INDEX = EVENT_DIR / "event_index.json"
MAX_EVENTS = 10000

# Lock for thread safety
_file_lock = threading.Lock()

# In-memory callback registry for pub/sub
_callbacks: Dict[str, List[Callable]] = defaultdict(list)


class EventBus:
    """
    In-Process Event Bus mit File-Backend und Pub/Sub.
    
    Usage:
        EventBus.publish("kg_update", "source", {"key": "value"})
        EventBus.subscribe("kg_update", my_handler)
        EventBus.get_events(event_type="kg_update", limit=50)
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        ensure_dir()
    
    @staticmethod
    def ensure_dir():
        """Ensure event directory exists."""
        EVENT_DIR.mkdir(parents=True, exist_ok=True)
        if not EVENT_FILE.exists():
            EVENT_FILE.write_text("")
        if not EVENT_INDEX.exists():
            EventBus._rebuild_index()
    
    @staticmethod
    def _rebuild_index():
        """Rebuild event index from scratch."""
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
    
    @classmethod
    def publish(cls, event_type: str, source: str, data: dict, severity: str = "info") -> dict:
        """
        Publish event to bus (in-process + file).
        
        Args:
            event_type: Type of event (e.g., "kg_update", "pattern_discovered")
            source: Source system (e.g., "learning_loop", "kg_sync")
            data: Event payload
            severity: info|warning|error|critical
        """
        cls.ensure_dir()
        
        event = {
            "id": f"evt_{int(datetime.now().timestamp() * 1000)}",
            "type": event_type,
            "source": source,
            "severity": severity,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }
        
        with _file_lock:
            # Append to file
            with open(EVENT_FILE, 'a') as f:
                f.write(json.dumps(event) + "\n")
            
            # Update index
            try:
                index = json.load(open(EVENT_INDEX))
            except:
                index = {"by_type": {}, "by_source": {}, "chronological": []}
            
            # Ensure nested dicts exist (loaded JSON loses defaultdict)
            if "by_type" not in index:
                index["by_type"] = {}
            if "by_source" not in index:
                index["by_source"] = {}
            if "chronological" not in index:
                index["chronological"] = []
            
            idx = len(open(EVENT_FILE).readlines()) - 1
            if event_type not in index["by_type"]:
                index["by_type"][event_type] = []
            index["by_type"][event_type].append(idx)
            if source not in index["by_source"]:
                index["by_source"][source] = []
            index["by_source"][source].append(idx)
            index["chronological"].append(idx)
            
            with open(EVENT_INDEX, 'w') as f:
                json.dump(index, f)
            
            # Prune old events if needed
            cls._prune_events()
        
        # Notify in-process subscribers
        cls._notify(event)
        
        return event
    
    @classmethod
    def _notify(cls, event: dict):
        """Notify registered in-process subscribers."""
        event_type = event.get("type", "unknown")
        for callback in _callbacks.get(event_type, []):
            try:
                callback(event)
            except Exception as e:
                print(f"EventBus callback error: {e}", file=sys.stderr)
        # Also notify wildcard listeners
        for callback in _callbacks.get("*", []):
            try:
                callback(event)
            except Exception as e:
                print(f"EventBus wildcard callback error: {e}", file=sys.stderr)
    
    @classmethod
    def _prune_events(cls):
        """Keep only last MAX_EVENTS lines."""
        with open(EVENT_FILE) as f:
            lines = f.readlines()
        
        if len(lines) > MAX_EVENTS:
            lines = lines[-MAX_EVENTS:]
            with open(EVENT_FILE, 'w') as f:
                f.writelines(lines)
            cls._rebuild_index()
    
    @classmethod
    def subscribe(cls, event_type: str, callback: Callable):
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: Type to subscribe to, or "*" for all
            callback: Function to call with event dict
        """
        _callbacks[event_type].append(callback)
    
    @classmethod
    def unsubscribe(cls, event_type: str, callback: Callable):
        """Remove a subscription."""
        if event_type in _callbacks and callback in _callbacks[event_type]:
            _callbacks[event_type].remove(callback)
    
    @classmethod
    def get_events(cls, event_type: Optional[str] = None, source: Optional[str] = None,
                   since: Optional[str] = None, limit: int = 50) -> List[dict]:
        """
        Get events with optional filters.
        
        Args:
            event_type: Filter by type
            source: Filter by source
            since: ISO timestamp - only events after this time
            limit: Max events to return
        """
        cls.ensure_dir()
        
        try:
            index = json.load(open(EVENT_INDEX))
        except:
            cls._rebuild_index()
            index = json.load(open(EVENT_INDEX))
        
        # Get candidate indices
        if event_type:
            indices = index.get("by_type", {}).get(event_type, [])
        elif source:
            indices = index.get("by_source", {}).get(source, [])
        else:
            indices = index.get("chronological", [])
        
        # Load events
        events = []
        with open(EVENT_FILE) as f:
            for i, line in enumerate(f):
                if i in indices:
                    try:
                        events.append(json.loads(line.strip()))
                    except:
                        pass
        
        # Filter by time
        if since:
            since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
            events = [e for e in events 
                     if datetime.fromisoformat(e.get("timestamp", "0").replace("Z", "+00:00")) > since_dt]
        
        # Sort by timestamp descending (newest first)
        events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return events[:limit]
    
    @classmethod
    def stats(cls) -> dict:
        """Get event bus statistics."""
        cls.ensure_dir()
        
        try:
            index = json.load(open(EVENT_INDEX))
        except:
            return {"error": "Index not loadable"}
        
        by_type = index.get("by_type", {})
        by_source = index.get("by_source", {})
        
        total = len(index.get("chronological", []))
        
        return {
            "total_events": total,
            "by_type": {t: len(ids) for t, ids in by_type.items()},
            "by_source": {s: len(ids) for s, ids in by_source.items()},
            "subscribers": len(_callbacks),
            "event_types": list(by_type.keys()),
        }


# Module-level convenience functions
def publish_event(event_type: str, source: str, data: dict, severity: str = "info") -> dict:
    """Publish event — module-level convenience function."""
    return EventBus.publish(event_type, source, data, severity)

def subscribe(event_type: str, callback: Callable):
    """Subscribe — module-level convenience function."""
    EventBus.subscribe(event_type, callback)

def get_events(event_type: Optional[str] = None, source: Optional[str] = None,
               since: Optional[str] = None, limit: int = 50) -> List[dict]:
    """Get events — module-level convenience function."""
    return EventBus.get_events(event_type, source, since, limit)

def stats() -> dict:
    """Stats — module-level convenience function."""
    return EventBus.stats()


# CLI Interface (backward compatibility)
if __name__ == "__main__" or len(sys.argv) > 1 and sys.argv[1] in ("publish", "list", "stats"):
    import argparse
    
    parser = argparse.ArgumentParser(description="Event Bus CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    pub = subparsers.add_parser("publish", help="Publish an event")
    pub.add_argument("--type", required=True, help="Event type")
    pub.add_argument("--source", required=True, help="Event source")
    pub.add_argument("--data", required=True, help="JSON event data")
    pub.add_argument("--severity", default="info", help="Severity")
    
    list_cmd = subparsers.add_parser("list", help="List events")
    list_cmd.add_argument("--type", help="Filter by type")
    list_cmd.add_argument("--source", help="Filter by source")
    list_cmd.add_argument("--since", help="ISO timestamp")
    list_cmd.add_argument("--limit", type=int, default=50)
    
    stats_cmd = subparsers.add_parser("stats", help="Show statistics")
    
    args = parser.parse_args()
    
    if args.command == "publish":
        import ast
        try:
            data = json.loads(args.data)
        except:
            try:
                data = ast.literal_eval(args.data)
            except:
                data = {"raw": args.data}
        result = publish_event(args.type, args.source, data, args.severity)
        print(f"Published: {result['id']}")
    
    elif args.command == "list":
        events = get_events(args.type, args.source, args.since, args.limit)
        for evt in events:
            print(f"[{evt.get('timestamp','?')[:19]}] {evt.get('type','?')} ({evt.get('source','?')}): {json.dumps(evt.get('data',{}))[:60]}")
    
    elif args.command == "stats":
        s = stats()
        print(f"Total events: {s.get('total_events', '?')}")
        print(f"Subscribers: {s.get('subscribers', '?')}")
        print(f"Event types: {s.get('event_types', [])}")
    
    else:
        parser.print_help()
