#!/usr/bin/env python3
"""
Rate Limiting
- Per-IP rate limiting
- Per-API-key rate limiting
- Configurable limits
"""

import redis
import time
from datetime import datetime, timedelta

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Default limits
LIMITS = {
    "default": {"requests": 100, "window": 60},  # 100 req/min
    "create": {"requests": 10, "window": 60},   # 10 creates/min
    "post": {"requests": 5, "window": 60},     # 5 posts/min
}

def check_rate_limit(identifier, limit_type="default"):
    """Check if identifier has exceeded rate limit"""
    limit = LIMITS.get(limit_type, LIMITS["default"])
    key = f"rate:{limit_type}:{identifier}"
    
    # Get current count
    count = r.get(key)
    if count is None:
        r.setex(key, limit["window"], 1)
        return {"allowed": True, "remaining": limit["requests"] - 1, "reset": limit["window"]}
    
    count = int(count)
    if count >= limit["requests"]:
        ttl = r.ttl(key)
        return {
            "allowed": False,
            "remaining": 0,
            "reset": ttl,
            "message": f"Rate limit exceeded. Try again in {ttl} seconds."
        }
    
    # Increment
    r.incr(key)
    return {
        "allowed": True,
        "remaining": limit["requests"] - count - 1,
        "reset": r.ttl(key)
    }

def reset_limit(identifier, limit_type="default"):
    """Reset rate limit for identifier"""
    key = f"rate:{limit_type}:{identifier}"
    r.delete(key)

# Middleware for Flask
def rate_limit_middleware(limit_type="default"):
    """Flask middleware for rate limiting"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get identifier (IP or API key)
            identifier = kwargs.get('headers', {}).get('X-Forwarded-For', 'unknown')
            
            result = check_rate_limit(identifier, limit_type)
            
            if not result["allowed"]:
                return {"error": result["message"]}, 429
            
            # Add rate limit headers
            if hasattr(wrapper, '__wrapped__'):
                wrapper.headers = {
                    'X-RateLimit-Limit': str(LIMITS[limit_type]["requests"]),
                    'X-RateLimit-Remaining': str(result["remaining"]),
                    'X-RateLimit-Reset': str(result["reset"])
                }
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# CLI
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "check":
            ip = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
            limit_type = sys.argv[3] if len(sys.argv) > 3 else "default"
            
            result = check_rate_limit(ip, limit_type)
            print(f"📊 Rate limit check for {ip}:")
            print(f"   Allowed: {result['allowed']}")
            print(f"   Remaining: {result['remaining']}")
            print(f"   Reset: {result['reset']}s")
        
        elif cmd == "reset":
            ip = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
            limit_type = sys.argv[3] if len(sys.argv) > 3 else "default"
            
            reset_limit(ip, limit_type)
            print(f"✅ Rate limit reset for {ip}")
        
        elif cmd == "stats":
            keys = r.keys("rate:*")
            print(f"📊 Active rate limits: {len(keys)}")
            for key in keys[:10]:
                count = r.get(key)
                ttl = r.ttl(key)
                print(f"   {key}: {count} requests, {ttl}s remaining")
    else:
        print("Rate Limiter CLI")
        print("Usage: rate_limiter.py [check|reset|stats]")
