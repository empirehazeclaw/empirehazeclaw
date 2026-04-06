#!/usr/bin/env python3
"""
Redis State Management
- Service state tracking
- Session management
- Caching
"""

import redis
import json
from datetime import datetime, timedelta

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Service states
def set_service_state(service, status, data=None):
    """Set service state"""
    key = f"service:{service}:state"
    state = {
        "status": status,  # running, stopped, error
        "data": data or {},
        "updated": datetime.now().isoformat()
    }
    r.set(key, json.dumps(state), ex=86400)  # 24h TTL

def get_service_state(service):
    """Get service state"""
    key = f"service:{service}:state"
    data = r.get(key)
    return json.loads(data) if data else None

def get_all_services():
    """Get all service states"""
    keys = r.keys("service:*:state")
    services = {}
    for key in keys:
        service = key.replace("service:", "").replace(":state", "")
        services[service] = get_service_state(service)
    return services

# Session management
def create_session(user_id, data=None):
    """Create new session"""
    import uuid
    session_id = str(uuid.uuid4())
    key = f"session:{session_id}"
    session = {
        "user_id": user_id,
        "data": data or {},
        "created": datetime.now().isoformat(),
        "last_active": datetime.now().isoformat()
    }
    r.set(key, json.dumps(session), ex=86400*7)  # 7 days
    return session_id

def get_session(session_id):
    """Get session"""
    key = f"session:{session_id}"
    data = r.get(key)
    return json.loads(data) if data else None

def update_session(session_id, data):
    """Update session"""
    key = f"session:{session_id}"
    session = get_session(session_id)
    if session:
        session.update(data)
        session["last_active"] = datetime.now().isoformat()
        r.set(key, json.dumps(session), ex=86400*7)
        return True
    return False

def delete_session(session_id):
    """Delete session"""
    r.delete(f"session:{session_id}")

# Caching
def cache_set(key, value, ttl=3600):
    """Cache with TTL"""
    if isinstance(value, (dict, list)):
        value = json.dumps(value)
    r.setex(f"cache:{key}", ttl, value)

def cache_get(key):
    """Get from cache"""
    data = r.get(f"cache:{key}")
    if data:
        try:
            return json.loads(data)
        except:
            return data
    return None

def cache_delete(key):
    """Delete from cache"""
    r.delete(f"cache:{key}")

# Metrics
def inc_metric(name, value=1):
    """Increment metric"""
    r.incrby(f"metric:{name}", value)

def get_metric(name):
    """Get metric value"""
    val = r.get(f"metric:{name}")
    return int(val) if val else 0

def get_metrics():
    """Get all metrics"""
    keys = r.keys("metric:*")
    metrics = {}
    for key in keys:
        name = key.replace("metric:", "")
        metrics[name] = get_metric(name)
    return metrics

# CLI
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "services":
            services = get_all_services()
            print("📊 Services:")
            for name, state in services.items():
                print(f"   {name}: {state['status'] if state else 'unknown'}")
        
        elif cmd == "metrics":
            metrics = get_metrics()
            print("📊 Metrics:")
            for name, value in metrics.items():
                print(f"   {name}: {value}")
        
        elif cmd == "cache":
            key = sys.argv[2] if len(sys.argv) > 2 else "test"
            value = sys.argv[3] if len(sys.argv) > 3 else "test_value"
            cache_set(key, value)
            print(f"✅ Cached: {key} = {value}")
            print(f"   Got: {cache_get(key)}")
        
        elif cmd == "session":
            # Create test session
            session_id = create_session("test_user", {"name": "Test"})
            print(f"✅ Session created: {session_id}")
            session = get_session(session_id)
            print(f"   Session: {session}")
    else:
        print("Redis State Management CLI")
        print("Usage: redis_state.py [services|metrics|cache <key> <value>|session]")
