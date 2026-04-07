#!/usr/bin/env python3
"""
📋 AUTONOMOUS TASK MANAGER v4 (Redis-Based)
============================================
Event-based task processing with Redis.
"""

import redis
import json
import subprocess
from datetime import datetime

class TaskManagerRedis:
    def __init__(self, redis_url="redis://localhost:6379/0"):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.prefix = "openclaw:event:"
        print("🔌 Task Manager (Redis) connected")
    
    def emit_event(self, event_type: str, data: dict = None):
        """Emit an event to Redis queue"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        event_id = f"{event_type}_{timestamp}"
        
        event = {
            "id": event_id,
            "type": event_type,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat(),
            "processed": False
        }
        
        # Add to processing queue
        self.redis.lpush(f"{self.prefix}queue", json.dumps(event))
        
        print(f"📢 Event emitted: {event_type}")
        return event_id
    
    def process_events(self):
        """Process pending events from Redis queue"""
        processed = 0
        
        for _ in range(5):  # Max 5 at a time
            # Pop event from queue
            event_json = self.redis.rpop(f"{self.prefix}queue")
            if not event_json:
                break
            
            try:
                event = json.loads(event_json)
                
                if event.get("processed"):
                    continue
                
                event_type = event["type"]
                handler = EVENT_HANDLERS.get(event_type)
                
                if not handler:
                    print(f"⚠️ No handler for: {event_type}")
                    continue
                
                print(f"⚡ Processing: {event_type} → {handler['agent']}")
                
                # Build task with event data
                full_task = handler["task"]
                if event.get("data"):
                    full_task += f"\n\nData: {json.dumps(event['data'])}"
                
                # Trigger agent via sessions_spawn
                self.trigger_agent(handler["agent"], full_task)
                
                # Mark as processed
                event["processed"] = True
                event["processed_at"] = datetime.utcnow().isoformat()
                self.redis.set(f"{self.prefix}{event['id']}", json.dumps(event))
                
                processed += 1
                
            except Exception as e:
                print(f"❌ Error: {e}")
        
        return processed
    
    def trigger_agent(self, agent_id: str, task: str):
        """Trigger OpenClaw agent via sessions_spawn"""
        
        cmd = [
            "curl", "-s", "-X", "POST",
            "http://127.0.0.1:18789/api/sessions",
            "-H", "Content-Type: application/json",
            "-d", json.dumps({
                "runtime": "subagent",
                "agentId": agent_id,
                "task": task,
                "mode": "run"
            })
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            if result.returncode == 0:
                print(f"✅ Agent {agent_id} started")
                return True
            else:
                print(f"❌ Agent failed")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


# Event handlers
EVENT_HANDLERS = {
    "website_down": {
        "agent": "dev",
        "task": "⚠️ CRITICAL: Website is down! Check immediately and fix.",
    },
    "new_lead": {
        "agent": "outreach", 
        "task": "📧 New lead detected! Follow up within 1 hour with personalized message.",
    },
    "new_order": {
        "agent": "content",
        "task": "🛒 New order received! Create thank you message and check for upsell.",
    },
    "social_mention": {
        "agent": "social",
        "task": "📱 Social media mention! Respond within 30 minutes.",
    },
    "bug_report": {
        "agent": "debugger",
        "task": "🐛 Bug report received! Investigate and fix.",
    },
    "daily_check": {
        "agent": "researcher",
        "task": "📊 Run daily research check - find 3 new opportunities.",
    },
    # Roadmap tasks
    "research_needed": {
        "agent": "researcher",
        "task": "🔍 Research this roadmap item: ",
    },
    "new_content_needed": {
        "agent": "content",
        "task": "📝 Implement this roadmap feature: ",
    },
    "new_pod_design": {
        "agent": "pod",
        "task": "🎨 Create POD design for: ",
    },
    "dev_task": {
        "agent": "dev",
        "task": "💻 Development task from roadmap: ",
    }
}

# CLI
if __name__ == "__main__":
    import sys
    manager = TaskManagerRedis()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "emit":
            event_type = sys.argv[2] if len(sys.argv) > 2 else "daily_check"
            data = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
            manager.emit_event(event_type, data)
        elif sys.argv[1] == "process":
            count = manager.process_events()
            print(f"Processed {count} events")
        else:
            print("Usage: python task_manager_v4.py [emit|process]")
    else:
        count = manager.process_events()
        print(f"Processed {count} events")
