#!/usr/bin/env python3
"""
📋 AUTONOMOUS TASK MANAGER v2
==============================
Checks Redis for pending tasks and triggers agents event-based.
"""

import sys
import os
sys.path.insert(0, "/home/clawbot/.openclaw/workspace")

import json
import redis
import subprocess
from datetime import datetime

# Event types and their handlers
EVENT_HANDLERS = {
    "website_down": {
        "agent": "dev",
        "task": "Check website health and fix any issues immediately.",
        "priority": "high"
    },
    "new_lead": {
        "agent": "outreach",
        "task": "Process new lead: Follow up within 1 hour with personalized email.",
        "priority": "high"
    },
    "new_order": {
        "agent": "content",
        "task": "New order received. Create thank you message and upsell opportunity.",
        "priority": "medium"
    },
    "social_mention": {
        "agent": "social",
        "task": "Respond to social media mention within 30 minutes.",
        "priority": "high"
    },
    "low_api_credits": {
        "agent": "researcher",
        "task": "Research alternative APIs or ways to get more credits.",
        "priority": "medium"
    },
    "bug_report": {
        "agent": "debugger",
        "task": "Investigate and fix bug report.",
        "priority": "high"
    }
}

class TaskManager:
    def __init__(self):
        self.redis = redis.from_url("redis://localhost:6379/0", decode_responses=True)
        self.prefix = "openclaw:events:"
    
    def emit_event(self, event_type: str, data: dict):
        """Emit an event to Redis"""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "processed": False
        }
        
        # Store event
        event_id = f"{event_type}_{datetime.utcnow().timestamp()}"
        self.redis.set(f"{self.prefix}{event_id}", json.dumps(event))
        
        # Add to processing queue
        self.redis.lpush(f"{self.prefix}queue", event_id)
        
        print(f"📢 Event emitted: {event_type}")
        return event_id
    
    def process_events(self):
        """Process pending events"""
        processed = 0
        
        # Get events from queue (max 5 at a time)
        for _ in range(5):
            event_id = self.redis.rpop(f"{self.prefix}queue")
            if not event_id:
                break
            
            # Get event data
            event_data = self.redis.get(f"{self.prefix}{event_id}")
            if not event_data:
                continue
            
            event = json.loads(event_data)
            
            if event.get("processed"):
                continue
            
            # Get handler
            event_type = event["type"]
            if event_type not in EVENT_HANDLERS:
                print(f"⚠️ No handler for: {event_type}")
                continue
            
            handler = EVENT_HANDLERS[event_type]
            
            # Trigger agent
            print(f"⚡ Processing: {event_type} → {handler['agent']}")
            
            success = self.trigger_agent(
                handler["agent"],
                handler["task"],
                event.get("data", {})
            )
            
            if success:
                # Mark as processed
                event["processed"] = True
                event["processed_at"] = datetime.utcnow().isoformat()
                self.redis.set(f"{self.prefix}{event_id}", json.dumps(event))
                processed += 1
        
        return processed
    
    def trigger_agent(self, agent_id: str, task: str, data: dict):
        """Trigger OpenClaw agent via sessions_spawn"""
        
        # Build full task with event data
        full_task = task
        if data:
            full_task += f"\n\nData: {json.dumps(data)}"
        
        # Try sessions_spawn tool equivalent via API
        cmd = [
            "curl", "-s", "-X", "POST",
            "http://127.0.0.1:18789/api/sessions",
            "-H", "Content-Type: application/json",
            "-d", json.dumps({
                "runtime": "subagent",
                "agentId": agent_id,
                "task": full_task,
                "mode": "run"
            })
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            if result.returncode == 0:
                print(f"✅ Agent {agent_id} started for task")
                return True
            else:
                print(f"❌ Agent start failed: {result.stderr.decode()}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


# Quick event emission
if __name__ == "__main__":
    manager = TaskManager()
    
    import sys
    
    if len(sys.argv) > 1:
        # Emit event: python task_manager_v2.py emit new_lead {"email": "test"}
        if sys.argv[1] == "emit":
            event_type = sys.argv[2]
            data = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
            manager.emit_event(event_type, data)
        
        # Process events: python task_manager_v2.py process
        elif sys.argv[1] == "process":
            count = manager.process_events()
            print(f"Processed {count} events")
    
    else:
        # Default: process
        count = manager.process_events()
        print(f"Processed {count} events")
