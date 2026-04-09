#!/usr/bin/env python3
"""
Event Bus for Agent Communication
- Publish/Subscribe pattern
- Event routing
- Event history
"""

import redis
import json
from datetime import datetime

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

CHANNEL_PREFIX = "event:"

def publish(event_type, data):
    """Publish event to bus"""
    event = {
        "type": event_type,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    
    # Publish to type-specific channel
    r.publish(f"{CHANNEL_PREFIX}{event_type}", json.dumps(event))
    
    # Also publish to all-events
    r.publish(f"{CHANNEL_PREFIX}all", json.dumps(event))
    
    # Store in history (keep last 1000)
    key = "event:history"
    r.lpush(key, json.dumps(event))
    r.ltrim(key, 0, 999)
    
    return event

def subscribe(event_type):
    """Subscribe to events"""
    pubsub = r.pubsub()
    channel = f"{CHANNEL_PREFIX}{event_type}"
    pubsub.subscribe(channel)
    return pubsub

def get_history(limit=100, event_type=None):
    """Get event history"""
    key = "event:history"
    if event_type:
        # Filter by type
        events = []
        for i in range(r.llen(key)):
            event_json = r.lindex(key, i)
            if event_json:
                event = json.loads(event_json)
                if event.get("type") == event_type:
                    events.append(event)
        return events[:limit]
    else:
        return [json.loads(e) for e in r.lrange(key, 0, limit-1)]

def get_stats():
    """Get event bus statistics"""
    return {
        "channels": len(r.keys(f"{CHANNEL_PREFIX}*")),
        "history_size": r.llen("event:history"),
    }

# Event types
class EventTypes:
    TASK_STARTED = "task:started"
    TASK_COMPLETED = "task:completed"
    TASK_FAILED = "task:failed"
    PAYMENT_RECEIVED = "payment:received"
    LEAD_GENERATED = "lead:generated"
    LEAD_CONTACTED = "lead:contacted"
    USER_SIGNED_UP = "user:signed_up"
    SUPPORT_TICKET = "support:ticket"

# CLI
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "publish":
            event_type = sys.argv[2] if len(sys.argv) > 2 else "test"
            data = sys.argv[3] if len(sys.argv) > 3 else "Test data"
            event = publish(event_type, {"message": data})
            print(f"✅ Published: {event_type}")
        
        elif cmd == "history":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            event_type = sys.argv[3] if len(sys.argv) > 3 else None
            
            events = get_history(limit, event_type)
            print(f"📋 Event History ({len(events)} events):")
            for e in events:
                print(f"   [{e['type']}] {e['timestamp']}")
        
        elif cmd == "stats":
            stats = get_stats()
            print(f"📊 Event Bus Stats:")
            print(f"   Channels: {stats['channels']}")
            print(f"   History: {stats['history_size']}")
    else:
        print("Event Bus CLI")
        print("Usage: event_bus.py [publish|history|stats]")
