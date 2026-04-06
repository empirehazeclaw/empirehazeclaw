#!/usr/bin/env python3
"""
📋 AUTONOMOUS TASK MANAGER v3 (Simple File-Based)
==================================================
Event-based task processing without Redis dependency.
"""

import json
import os
import subprocess
from datetime import datetime

EVENTS_DIR = "/home/clawbot/.openclaw/workspace/data/events"
os.makedirs(EVENTS_DIR, exist_ok=True)

# Event types and their handlers
EVENT_HANDLERS = {
    "website_down": {
        "agent": "dev",
        "task": "Check website health immediately!",
    },
    "new_lead": {
        "agent": "outreach", 
        "task": "Process new lead - follow up within 1 hour.",
    },
    "new_order": {
        "agent": "content",
        "task": "New order received - create thank you message.",
    },
    "social_mention": {
        "agent": "social",
        "task": "Respond to social media mention within 30 minutes.",
    },
    "bug_report": {
        "agent": "debugger",
        "task": "Investigate and fix bug report.",
    },
    "daily_check": {
        "agent": "researcher",
        "task": "Quick research task.",
    }
}

def emit_event(event_type: str, data: dict = None):
    """Emit an event (creates a file)"""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    event_id = f"{event_type}_{timestamp}"
    
    event = {
        "id": event_id,
        "type": event_type,
        "data": data or {},
        "timestamp": datetime.utcnow().isoformat(),
        "processed": False
    }
    
    filepath = f"{EVENTS_DIR}/{event_id}.json"
    with open(filepath, "w") as f:
        json.dump(event, f, indent=2)
    
    print(f"📢 Event emitted: {event_type}")
    return event_id

def process_events():
    """Process pending events"""
    processed = 0
    
    # Get all event files
    event_files = sorted([f for f in os.listdir(EVENTS_DIR) if f.endswith(".json")])
    
    for filename in event_files[:5]:  # Max 5 at a time
        filepath = f"{EVENTS_DIR}/{filename}"
        
        try:
            with open(filepath, "r") as f:
                event = json.load(f)
            
            if event.get("processed"):
                continue
            
            event_type = event["type"]
            
            if event_type not in EVENT_HANDLERS:
                print(f"⚠️ No handler for: {event_type}")
                continue
            
            handler = EVENT_HANDLERS[event_type]
            
            # Trigger agent
            print(f"⚡ Processing: {event_type} → {handler['agent']}")
            
            full_task = handler["task"]
            if event.get("data"):
                full_task += f"\n\nData: {json.dumps(event['data'])}"
            
            # Trigger via sessions_spawn
            cmd = [
                "curl", "-s", "-X", "POST",
                "http://127.0.0.1:18789/api/sessions",
                "-H", "Content-Type: application/json",
                "-d", json.dumps({
                    "runtime": "subagent",
                    "agentId": handler["agent"],
                    "task": full_task,
                    "mode": "run"
                })
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            
            if result.returncode == 0:
                event["processed"] = True
                event["processed_at"] = datetime.utcnow().isoformat()
                with open(filepath, "w") as f:
                    json.dump(event, f, indent=2)
                processed += 1
                print(f"✅ Event processed: {event_type}")
            else:
                print(f"❌ Agent failed: {result.stderr.decode()[:100]}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return processed

# CLI
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "emit":
            event_type = sys.argv[2] if len(sys.argv) > 2 else "daily_check"
            data = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
            emit_event(event_type, data)
        elif sys.argv[1] == "process":
            count = process_events()
            print(f"Processed {count} events")
        else:
            print("Usage: python task_manager_v3.py [emit|process]")
    else:
        count = process_events()
        print(f"Processed {count} events")
