#!/usr/bin/env python3
"""
Learning Events - Phase 3
========================
Event bus for learning system. Publishes and handles events between components.

Usage:
    python3 learning_events.py --publish <type> <data>   # Publish event
    python3 learning_events.py --listen <type>           # Listen for event
    python3 learning_events.py --handlers               # List all handlers
    python3 learning_events.py --status                # Event bus status

Event Types:
    task_completed       → evaluation triggered
    failure_detected     → failure_logger + causal updater
    exploration_triggered → exploration_budget + strategy_mutator
    strategy_mutated     → kg update
    slo_breached         → sre_culture incident
    meta_learned         → kg sync
"""

import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
EVENTS_DIR = WORKSPACE / "memory" / "evaluations" / "events"
EVENT_LOG = EVENTS_DIR / "event_log.json"

# ============================================================================
# EVENT TYPES
# ============================================================================

EVENT_TYPES = {
    "task_completed": "Task execution completed successfully or with failure",
    "failure_detected": "A failure or error was detected",
    "exploration_triggered": "Exploration run was triggered",
    "strategy_mutated": "A strategy mutation was created",
    "slo_breached": "SLO compliance threshold was breached",
    "meta_learned": "A new meta-learning pattern was discovered",
    "kg_synced": "Knowledge graph was synchronized"
}

# ============================================================================
# EVENT BUS
# ============================================================================

class EventBus:
    def __init__(self):
        self.handlers = defaultdict(list)
        self.event_log = []
        self.load_log()
    
    def load_log(self):
        """Load event log from disk."""
        if EVENT_LOG.exists():
            try:
                self.event_log = json.loads(EVENT_LOG.read_text())
            except:
                self.event_log = []
    
    def save_log(self):
        """Save event log to disk."""
        EVENTS_DIR.mkdir(parents=True, exist_ok=True)
        EVENT_LOG.write_text(json.dumps(self.event_log[-100:], indent=2))
    
    def subscribe(self, event_type, handler_name, handler_func):
        """Subscribe a handler to an event type."""
        self.handlers[event_type].append({
            'name': handler_name,
            'func': handler_func
        })
    
    def publish(self, event_type, data):
        """Publish an event to all subscribers."""
        event = {
            'type': event_type,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': data
        }
        
        self.event_log.append(event)
        self.save_log()
        
        # Call handlers
        for handler in self.handlers.get(event_type, []):
            try:
                handler['func'](event)
            except Exception as e:
                print(f"Handler error: {e}")
        
        return event
    
    def get_recent(self, limit=10):
        """Get recent events."""
        return self.event_log[-limit:]
    
    def get_stats(self):
        """Get event statistics."""
        stats = defaultdict(int)
        for event in self.event_log:
            stats[event['type']] += 1
        return dict(stats)

# ============================================================================
# HANDLERS
# ============================================================================

def handle_failure(event):
    """Handle failure_detected events."""
    data = event.get('data', {})
    print(f"   📋 Failure handler: {data.get('description', 'N/A')}")

def handle_exploration(event):
    """Handle exploration_triggered events."""
    data = event.get('data', {})
    print(f"   🚀 Exploration handler: {data.get('strategy', 'unknown')}")

def handle_meta(event):
    """Handle meta_learned events."""
    data = event.get('data', {})
    print(f"   🧠 Meta-learning handler: {data.get('pattern', 'N/A')}")

# ============================================================================
# COMMANDS
# ============================================================================

def publish_event(event_type, data_str):
    """Publish an event."""
    bus = EventBus()
    
    # Parse data string as JSON or use as plain text
    try:
        data = json.loads(data_str) if data_str else {}
    except:
        data = {'message': data_str}
    
    event = bus.publish(event_type, data)
    print(f"✅ Published: {event['type']} at {event['timestamp'][:19]}")
    return event

def show_handlers():
    """Show registered handlers."""
    bus = EventBus()
    
    print("\n📋 Registered Handlers:")
    if not bus.handlers:
        print("   No handlers registered.")
        print("   Run with --subscribe to add handlers.")
    else:
        for event_type, handlers in bus.handlers.items():
            print(f"\n   {event_type}:")
            for h in handlers:
                print(f"     - {h['name']}")
    
    print("\n📢 Available Event Types:")
    for et, desc in EVENT_TYPES.items():
        print(f"   {et}: {desc}")

def show_status():
    """Show event bus status."""
    bus = EventBus()
    stats = bus.get_stats()
    recent = bus.get_recent(5)
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║           LEARNING EVENT BUS - STATUS                    ║
╠══════════════════════════════════════════════════════════╣
║  Total Events: {len(bus.event_log):<43}║
╠══════════════════════════════════════════════════════════╣""")
    
    for et, count in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"║  {et}: {count:<44}║")
    
    print("╠══════════════════════════════════════════════════════════╣")
    print("║  Recent Events:                                         ║")
    for event in recent:
        print(f"║    {event['timestamp'][:19]} {event['type']:<30}║")
    
    print("╚══════════════════════════════════════════════════════════╝")

def show_log(limit=20):
    """Show event log."""
    bus = EventBus()
    events = bus.get_recent(limit)
    
    print(f"\n📜 Event Log (last {len(events)} events):")
    print("=" * 60)
    
    for event in events:
        print(f"\n[{event['timestamp'][:19]}] {event['type']}")
        data = event.get('data', {})
        if data:
            for k, v in data.items():
                print(f"   {k}: {v}")

# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Learning Events - Event Bus")
    parser.add_argument("--publish", nargs=3, metavar=("TYPE", "KEY", "VALUE"), help="Publish event")
    parser.add_argument("--status", action="store_true", help="Show event bus status")
    parser.add_argument("--handlers", action="store_true", help="Show registered handlers")
    parser.add_argument("--log", action="store_true", help="Show event log")
    parser.add_argument("--limit", type=int, default=20, help="Log limit")
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    if args.publish:
        event_type = args.publish[0]
        data_key = args.publish[1]
        data_value = args.publish[2]
        publish_event(event_type, json.dumps({data_key: data_value}))
    
    if args.status:
        show_status()
    
    if args.handlers:
        show_handlers()
    
    if args.log:
        show_log(args.limit)

if __name__ == "__main__":
    main()