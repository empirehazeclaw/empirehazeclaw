#!/usr/bin/env python3
"""
API Authentication Layer
- JWT token generation
- Token verification
- API key management
"""

import jwt
import json
import uuid
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SECRET_KEY = "***REDACTED***"  # Rotate: empire_haze_claw_2026_secret_key_change_in_production
KEYS_FILE = WORKSPACE / "data" / "api_keys.json"

def generate_api_key(name, permissions=None):
    """Generate new API key"""
    key_id = str(uuid.uuid4())[:8]
    key_secret = hashlib.sha256(f"{name}{datetime.now()}".encode()).hexdigest()[:32]
    full_key = f"eh_{key_id}_{key_secret}"
    
    keys = load_keys()
    keys[full_key] = {
        "name": name,
        "permissions": permissions or ["read"],
        "created": datetime.now().isoformat(),
        "active": True
    }
    save_keys(keys)
    
    return {"key": full_key, "name": name}

def load_keys():
    if KEYS_FILE.exists():
        return json.loads(KEYS_FILE.read_text())
    return {}

def save_keys(keys):
    KEYS_FILE.parent.mkdir(parents=True, exist_ok=True)
    KEYS_FILE.write_text(json.dumps(keys, indent=2))

def verify_key(api_key):
    """Verify API key"""
    keys = load_keys()
    return keys.get(api_key, {})

def generate_token(user_id, permissions=None):
    """Generate JWT token"""
    payload = {
        "user_id": user_id,
        "permissions": permissions or ["read"],
        "exp": datetime.now() + timedelta(days=7),
        "iat": datetime.now()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return {"valid": True, "payload": payload}
    except jwt.ExpiredSignatureError:
        return {"valid": False, "error": "Token expired"}
    except jwt.InvalidTokenError:
        return {"valid": False, "error": "Invalid token"}

def require_auth(permissions=None):
    """Decorator for API endpoints"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get token from header
            auth_header = kwargs.get('headers', {}).get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return {"error": "No token provided"}, 401
            
            token = auth_header[7:]
            result = verify_token(token)
            
            if not result.get("valid"):
                return {"error": result.get("error")}, 401
            
            # Check permissions
            if permissions:
                token_perms = result["payload"].get("permissions", [])
                if not any(p in token_perms for p in permissions):
                    return {"error": "Insufficient permissions"}, 403
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# CLI
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "create":
            name = sys.argv[2] if len(sys.argv) > 2 else "API User"
            perms = sys.argv[3].split(",") if len(sys.argv) > 3 else ["read"]
            
            result = generate_api_key(name, perms)
            print(f"✅ API Key created:")
            print(f"   Key: {result['key']}")
            print(f"   Name: {result['name']}")
        
        elif cmd == "list":
            keys = load_keys()
            print(f"📋 API Keys ({len(keys)}):")
            for key, data in keys.items():
                status = "✅" if data.get("active") else "❌"
                print(f"   {status} {key[:20]}... - {data.get('name', 'N/A')}")
        
        elif cmd == "verify":
            key = sys.argv[2] if len(sys.argv) > 2 else None
            if key:
                result = verify_key(key)
                print(f"🔑 Key valid: {bool(result)}")
                print(f"   {result}")
        
        elif cmd == "token":
            user = sys.argv[2] if len(sys.argv) > 2 else "user"
            token = generate_token(user, ["read", "write"])
            print(f"🎫 JWT Token:")
            print(f"   {token}")
    else:
        print("API Auth CLI")
        print("Usage: api_auth.py [create|list|verify|token]")
