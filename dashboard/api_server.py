#!/usr/bin/env python3
"""
API Server - FastAPI
REST Endpoints for OpenClaw
"""

import os
import json
import time
from datetime import datetime
from typing import Optional

# Try to import FastAPI, install if missing
try:
    from fastapi import FastAPI, HTTPException, Depends, Header, Request
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# ============== CONFIG ==============

API_VERSION = "1.0.0"
API_TITLE = "OpenClaw API"
API_HOST = "0.0.0.0"
API_PORT = 8000

# API Keys
API_KEYS = {
    "test-key-123": {
        "name": "test-user",
        "rate_limit": 100
    }
}

# Rate limiting storage
rate_limits = {}

# ============== MODELS ==============

class AgentRequest(BaseModel):
    agent: str
    task: str
    model: Optional[str] = None

class MemoryRequest(BaseModel):
    key: str
    value: Optional[str] = None

class KnowledgeQuery(BaseModel):
    query: str
    top_k: Optional[int] = 5

class ScriptRequest(BaseModel):
    script: str
    args: Optional[list] = None

# ============== AUTH ==============

async def verify_api_key(x_api_key: str = Header(None)):
    """Verify API key"""
    
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    # Rate limit check
    current = int(time.time() / 60)
    key = f"{x_api_key}:{current}"
    
    if key not in rate_limits:
        rate_limits[key] = 0
    
    rate_limits[key] += 1
    
    if rate_limits[key] > API_KEYS[x_api_key]["rate_limit"]:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    return API_KEYS[x_api_key]

# ============== CREATE APP ==============

def create_app() -> FastAPI:
    """Create and configure FastAPI app"""
    
    app = FastAPI(
        title=API_TITLE,
        version=API_VERSION,
        description="REST API for OpenClaw Agent System"
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # ============== ENDPOINTS ==============
    
    @app.get("/")
    async def root():
        return {
            "name": "OpenClaw API",
            "version": API_VERSION,
            "status": "online"
        }
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    
    # Agents
    @app.get("/agents")
    async def list_agents(api_key: dict = Depends(verify_api_key)):
        return {
            "agents": [
                {"name": "writer", "status": "idle"},
                {"name": "researcher", "status": "idle"},
                {"name": "memory", "status": "idle"},
                {"name": "coder", "status": "idle"},
                {"name": "discord", "status": "idle"}
            ]
        }
    
    @app.get("/agents/{agent_name}")
    async def get_agent(agent_name: str, api_key: dict = Depends(verify_api_key)):
        return {
            "name": agent_name,
            "status": "idle",
            "tasks_completed": 0
        }
    
    @app.post("/agents/execute")
    async def execute_agent(request: AgentRequest, api_key: dict = Depends(verify_api_key)):
        return {
            "status": "success",
            "agent": request.agent,
            "task": request.task,
            "timestamp": datetime.now().isoformat()
        }
    
    # Memory
    @app.get("/memory/{key}")
    async def get_memory(key: str, api_key: dict = Depends(verify_api_key)):
        return {"key": key, "value": None}
    
    @app.post("/memory")
    async def set_memory(request: MemoryRequest, api_key: dict = Depends(verify_api_key)):
        return {"status": "success", "key": request.key}
    
    @app.delete("/memory/{key}")
    async def delete_memory(key: str, api_key: dict = Depends(verify_api_key)):
        return {"status": "success", "key": key}
    
    # Knowledge
    @app.get("/knowledge")
    async def list_knowledge(api_key: dict = Depends(verify_api_key)):
        return {"documents": 62}
    
    @app.post("/knowledge/search")
    async def search_knowledge(request: KnowledgeQuery, api_key: dict = Depends(verify_api_key)):
        return {"query": request.query, "results": [], "count": 0}
    
    # Scripts
    @app.post("/scripts/execute")
    async def execute_script(request: ScriptRequest, api_key: dict = Depends(verify_api_key)):
        return {"status": "success", "script": request.script}
    
    # System
    @app.get("/system/info")
    async def system_info(api_key: dict = Depends(verify_api_key)):
        return {
            "version": API_VERSION,
            "disk_used_percent": 35.3
        }
    
    @app.get("/system/stats")
    async def system_stats(api_key: dict = Depends(verify_api_key)):
        return {
            "requests_total": sum(rate_limits.values()),
            "rate_limits": len(rate_limits)
        }
    
    return app

# ============== MAIN ==============

def main():
    """Main entry point"""
    
    if not FASTAPI_AVAILABLE:
        print("❌ FastAPI nicht installiert!")
        print("   Installiere mit: pip install fastapi uvicorn")
        print("")
        print("📋 Alternativ: JSON Server Mode")
        print("   python3 scripts/api_server.py --mode json")
        return
    
    print(f"🌐 Starte OpenClaw API Server...")
    print(f"   Version: {API_VERSION}")
    print(f"   Port: {API_PORT}")
    print(f"   Docs: http://localhost:{API_PORT}/docs")
    print("")
    print("📝 Endpoints:")
    print("   GET  /             - Root")
    print("   GET  /health       - Health Check")
    print("   GET  /agents       - List Agents")
    print("   POST /agents/execute - Execute Agent")
    print("   GET  /memory/{key} - Get Memory")
    print("   POST /knowledge/search - Search Knowledge")
    print("")
    print("🔑 API Key: test-key-123")
    print("")
    
    try:
        import uvicorn
        app = create_app()
        uvicorn.run(app, host=API_HOST, port=API_PORT)
    except ImportError:
        print("❌ Uvicorn nicht installiert!")
        print("   Installiere mit: pip install uvicorn")

if __name__ == "__main__":
    main()
