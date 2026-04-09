#!/usr/bin/env python3
"""
⚡ EVENT-BASED AUTONOMOUS TASK MANAGER
======================================
Responds to events, not just time.
"""

import redis
import json
import subprocess
from datetime import datetime

# Redis channels for events
EVENT_CHANNELS = {
    "new_lead": {"agent": "outreach", "description": "Neuer Lead erkannt"},
    "new_order": {"agent": "content", "description": "Bestellung erhalten"},
    "new_submission": {"agent": "researcher", "description": "Neue Einreichung"},
    "website_error": {"agent": "dev", "description": "Website Fehler"},
    "low_balance": {"agent": "research", "description": "Niedriges Guthaben"},
    "mention": {"agent": "social", "description": "Erwähnung auf Social Media"},
}

class EventTrigger:
    def __init__(self, redis_url="redis://localhost:6379/0"):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.pubsub = self.redis.pubsub()
    
    def emit(self, event_type: str, data: dict):
        """Emit an event"""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.redis.publish(f"event:{event_type}", json.dumps(event))
        print(f"📢 Event emitted: {event_type}")
    
    def listen(self):
        """Listen for events and trigger agents"""
        print("👂 Listening for events...")
        
        # Subscribe to all event channels
        for channel in EVENT_CHANNELS.keys():
            self.pubsub.subscribe(f"event:{channel}")
        
        for message in self.pubsub.listen():
            if message["type"] == "message":
                try:
                    event = json.loads(message["data"])
                    event_type = event["type"]
                    
                    if event_type in EVENT_CHANNELS:
                        config = EVENT_CHANNELS[event_type]
                        print(f"⚡ Event: {event_type} → Agent: {config['agent']}")
                        
                        # Trigger the agent
                        self.trigger_agent(config["agent"], event)
                        
                except Exception as e:
                    print(f"❌ Error processing event: {e}")
    
    def trigger_agent(self, agent_id: str, event: dict):
        """Trigger an OpenClaw agent"""
        task = f"Event-basiert: {event['type']} - {event.get('data', {})}"
        
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
                print(f"✅ Agent {agent_id} gestartet für {event['type']}")
            else:
                print(f"❌ Agent start fehlgeschlagen: {result.stderr}")
        except Exception as e:
            print(f"❌ Error triggering agent: {e}")


# Quick triggers (for manual/testing)
def trigger(event_type: str, data: dict = None):
    """Quick trigger an event"""
    trigger = EventTrigger()
    trigger.emit(event_type, data or {})


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Manual trigger: python event_trigger.py new_lead {"email": "test@test.com"}
        event_type = sys.argv[1]
        data = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
        trigger(event_type, data)
    else:
        # Start listening
        listener = EventTrigger()
        listener.listen()
