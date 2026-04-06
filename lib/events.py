"""
📡 ENHANCED EVENT SYSTEM
========================
Better Redis event handling with emit and handlers
"""

import redis
import json
from datetime import datetime

class EventSystem:
    def __init__(self, redis_url="redis://localhost:6379/0"):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.prefix = "openclaw:event:"
        print("📡 Event System connected")
    
    def emit(self, event_type, data, priority="normal"):
        """Emit event to queue"""
        
        event = {
            "id": f"{event_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": event_type,
            "data": data,
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
            "retries": 0
        }
        
        # Add to queue
        self.redis.lpush(f"{self.prefix}queue", json.dumps(event))
        
        print(f"📡 Event emitted: {event_type}")
        return event
    
    def emit_critical(self, event_type, data):
        """Emit critical event (high priority)"""
        return self.emit(event_type, data, priority="high")
    
    def process(self, handlers):
        """Process events with handlers"""
        processed = 0
        
        for _ in range(10):  # Max 10 at a time
            event_json = self.redis.rpop(f"{self.prefix}queue")
            if not event_json:
                break
            
            event = json.loads(event_json)
            event_type = event["type"]
            
            handler = handlers.get(event_type)
            
            if handler:
                try:
                    handler(event)
                    processed += 1
                except Exception as e:
                    print(f"❌ Handler error: {e}")
                    # Requeue for retry
                    if event["retries"] < 3:
                        event["retries"] += 1
                        self.redis.lpush(f"{self.prefix}queue", json.dumps(event))
            else:
                print(f"⚠️ No handler for: {event_type}")
        
        return processed

# Event Types
EVENTS = {
    "NEW_LEAD": "Neuer Lead gefunden",
    "NEW_ORDER": "Neue Bestellung",
    "SERVICE_DOWN": "Service ausgefallen",
    "REVENUE_ZERO": "Revenue bei 0",
    "HIGH_ERRORS": "Zu viele Fehler",
    "CONTENT_PUBLISHED": "Content veröffentlicht",
    "OUTREACH_SENT": "Outreach gesendet"
}

if __name__ == "__main__":
    events = EventSystem()
    
    # Emit test event
    events.emit("NEW_LEAD", {"email": "test@example.com"})
    
    # Test processing
    def handle_test(event):
        print(f"Handling: {event['type']}")
    
    processed = events.process({"NEW_LEAD": handle_test})
    print(f"Processed: {processed}")
