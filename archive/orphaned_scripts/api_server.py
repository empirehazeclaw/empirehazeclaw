#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          OPENCLAW · FASTAPI REST LAYER                     ║
║          REST API · WebSocket Streaming · Task Queue       ║
╚══════════════════════════════════════════════════════════════╝

Features:
  - POST /api/task - Task einreichen
  - GET /api/task/{id} - Task Status
  - GET /api/task/{id}/stream - WebSocket Streaming
  - GET /api/tasks - Task History
  - DELETE /api/task/{id} - Task abbrechen
  - POST /api/agent/{name} - Agent direkt aufrufen
  - GET /api/memory/stats - Memory Statistiken
  - GET /api/health - Health Check

Auth: API-Key via Header X-API-Key

Usage:
    uvicorn api_server:app --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
import uuid
from uuid import uuid4
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
import sys
sys.path.insert(0, '/home/clawbot/.openclaw/workspace/scripts')

# Import agents
try:
    from agents.memory_agent import MemoryAgent, MemoryType
    from agents.research_agent import ResearchAgent
    from agents.coding_agent import CodingAgent
    from agents.security_agent import SecurityAgent
    from agents.content_agent import ContentAgent, Platform, Tone
    from agents.mail_agent import MailAgent, MailAction
    from agents.data_agent import DataAgent
    AGENTS_AVAILABLE = True
except ImportError as e:
    AGENTS_AVAILABLE = False
    print(f"⚠️ Agenten nicht verfügbar: {e}")

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [API] %(message)s")
log = logging.getLogger("openclaw.api")

# Konfiguration
API_KEY = os.environ.get("OPENCLAW_API_KEY", "openclaw-dev-key-2026")
API_VERSION = "2.0.0"
MAX_CONCURRENT_TASKS = 5


# ═══════════════════════════════════════════════════════════════
#  Datenmodelle
# ═══════════════════════════════════════════════════════════════

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Task:
    """Eine Task im Queue"""
    id: str
    description: str
    agent: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict] = None
    error: Optional[str] = None
    progress: float = 0.0


# ═══════════════════════════════════════════════════════════════
#  Task Queue & Management
# ═══════════════════════════════════════════════════════════════

class TaskQueue:
    """In-Memory Task Queue"""
    
    def __init__(self, max_concurrent: int = MAX_CONCURRENT_TASKS):
        self.tasks: Dict[str, Task] = {}
        self.max_concurrent = max_concurrent
        self.running = 0
        self.queue: asyncio.Queue = asyncio.Queue()
        
    def create_task(self, description: str, agent: str, priority: TaskPriority = TaskPriority.MEDIUM) -> Task:
        task = Task(
            id=str(uuid4()),
            description=description,
            agent=agent,
            priority=priority,
            created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        self.tasks[task.id] = task
        log.info(f"📝 Task erstellt: {task.id} | {agent}")
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)
    
    def get_all_tasks(self, limit: int = 50) -> List[Task]:
        sorted_tasks = sorted(
            self.tasks.values(),
            key=lambda t: t.created_at,
            reverse=True
        )
        return sorted_tasks[:limit]
    
    def update_status(self, task_id: str, status: TaskStatus, result: Any = None, error: str = None, progress: float = None):
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = status
            
            if status == TaskStatus.RUNNING:
                task.started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ")
                self.running += 1
            elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                task.completed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ")
                task.result = result
                task.error = error
                if self.running > 0:
                    self.running -= 1
            
            if progress is not None:
                task.progress = progress
    
    def cancel_task(self, task_id: str) -> bool:
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                task.status = TaskStatus.CANCELLED
                log.info(f"❌ Task cancelled: {task_id}")
                return True
        return False
    
    def get_stats(self) -> Dict:
        total = len(self.tasks)
        by_status = {s.value: 0 for s in TaskStatus}
        for task in self.tasks.values():
            by_status[task.status.value] += 1
        
        return {
            "total": total,
            "by_status": by_status,
            "running": self.running,
            "max_concurrent": self.max_concurrent,
            "queue_size": self.queue.qsize()
        }


# ═══════════════════════════════════════════════════════════════
#  API Key Security
# ═══════════════════════════════════════════════════════════════

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Depends(api_key_header)) -> str:
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return api_key


# ═══════════════════════════════════════════════════════════════
#  FastAPI App
# ═══════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/Shutdown"""
    log.info("🚀 OpenClaw API starting...")
    
    # Initialize agents
    if AGENTS_AVAILABLE:
        app.state.agents = {
            "memory": MemoryAgent(),
            "research": ResearchAgent(),
            "coding": CodingAgent(),
            "security": SecurityAgent(),
            "content": ContentAgent(),
            "mail": MailAgent(),
            "data": DataAgent()
        }
        log.info(f"✅ Agenten geladen: {list(app.state.agents.keys())}")
    
    # Initialize task queue
    app.state.task_queue = TaskQueue()
    
    yield
    
    log.info("👋 OpenClaw API shutting down...")


app = FastAPI(
    title="OpenClaw API",
    description="Multi-Agent System API",
    version=API_VERSION,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════
#  Request Models
# ═══════════════════════════════════════════════════════════════

class TaskRequest(BaseModel):
    description: str
    agent: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    params: Dict[str, Any] = Field(default_factory=dict)


class AgentRequest(BaseModel):
    action: str
    params: Dict[str, Any] = Field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════
#  Health & Status
# ═══════════════════════════════════════════════════════════════

@app.get("/api/health")
async def health_check():
    """Health Check"""
    queue: TaskQueue = app.state.task_queue
    
    return {
        "status": "healthy",
        "version": API_VERSION,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "queue": queue.get_stats(),
        "agents_loaded": AGENTS_AVAILABLE
    }


# ═══════════════════════════════════════════════════════════════
#  Task Endpoints
# ═══════════════════════════════════════════════════════════════

@app.post("/api/task", response_model=Dict)
async def create_task(
    request: TaskRequest,
    api_key: str = Depends(verify_api_key)
):
    """Erstelle eine neue Task"""
    queue: TaskQueue = app.state.task_queue
    
    task = queue.create_task(
        description=request.description,
        agent=request.agent or "orchestrator",
        priority=request.priority
    )
    
    # Start processing in background
    asyncio.create_task(process_task(task.id, request.params, app.state))
    
    return {
        "task_id": task.id,
        "status": task.status.value,
        "created_at": task.created_at
    }


@app.get("/api/task/{task_id}")
async def get_task(task_id: str, api_key: str = Depends(verify_api_key)):
    """Hole Task Status"""
    queue: TaskQueue = app.state.task_queue
    task = queue.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "id": task.id,
        "description": task.description,
        "agent": task.agent,
        "status": task.status.value,
        "priority": task.priority.value,
        "created_at": task.created_at,
        "started_at": task.started_at,
        "completed_at": task.completed_at,
        "result": task.result,
        "error": task.error,
        "progress": task.progress
    }


@app.get("/api/tasks")
async def list_tasks(
    limit: int = 50,
    api_key: str = Depends(verify_api_key)
):
    """Liste alle Tasks"""
    queue: TaskQueue = app.state.task_queue
    tasks = queue.get_all_tasks(limit)
    
    return {
        "total": len(tasks),
        "tasks": [
            {
                "id": t.id,
                "description": t.description[:50],
                "agent": t.agent,
                "status": t.status.value,
                "created_at": t.created_at
            }
            for t in tasks
        ]
    }


@app.delete("/api/task/{task_id}")
async def cancel_task(task_id: str, api_key: str = Depends(verify_api_key)):
    """Cancel a task"""
    queue: TaskQueue = app.state.task_queue
    
    if not queue.cancel_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found or cannot be cancelled")
    
    return {"task_id": task_id, "status": "cancelled"}


@app.get("/api/task/{task_id}/stream")
async def stream_task(task_id: str, api_key: str = Depends(verify_api_key)):
    """WebSocket Stream für Task Updates"""
    queue: TaskQueue = app.state.task_queue
    task = queue.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    async def event_generator():
        """Sende Events via SSE"""
        last_update = task.updated_at if hasattr(task, 'updated_at') else 0
        
        while task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            await asyncio.sleep(1)
            
            # Check for updates
            current_task = queue.get_task(task_id)
            if current_task and current_task.updated_at != last_update:
                yield f"data: {json.dumps({'status': current_task.status.value, 'progress': current_task.progress})}\n\n"
                last_update = current_task.updated_at
        
        # Final status
        final_task = queue.get_task(task_id)
        yield f"data: {json.dumps({'status': final_task.status.value, 'progress': 1.0, 'done': True})}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ═══════════════════════════════════════════════════════════════
#  Agent Endpoints
# ═══════════════════════════════════════════════════════════════

@app.post("/api/agent/{agent_name}")
async def call_agent(
    agent_name: str,
    request: AgentRequest,
    api_key: str = Depends(verify_api_key)
):
    """Rufe einen Agenten direkt auf"""
    if not AGENTS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Agents not loaded")
    
    agents: Dict = app.state.agents
    
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    
    agent = agents[agent_name]
    
    # Route to appropriate handler
    if agent_name == "research":
        result = await agent.research(request.params.get("query", ""), request.params.get("depth", "standard"))
        return {"agent": agent_name, "result": result.__dict__}
    
    elif agent_name == "content":
        result = agent.generate_content(request.params.get("spec"))
        return {"agent": agent_name, "result": result.__dict__}
    
    elif agent_name == "mail":
        result = agent.send_email(request.params.get("spec"))
        return {"agent": agent_name, "result": result.__dict__}
    
    elif agent_name == "data":
        result = agent.analyze_data(request.params.get("data", []))
        return {"agent": agent_name, "result": result.__dict__}
    
    elif agent_name == "security":
        result = await agent.scan(request.params.get("target", "workspace"))
        return {"agent": agent_name, "result": result}
    
    elif agent_name == "coding":
        result = await agent.run_with_debug(request.params.get("code", ""))
        return {"agent": agent_name, "result": result.__dict__}
    
    return {"agent": agent_name, "message": "Agent executed"}


# ═══════════════════════════════════════════════════════════════
#  Memory Endpoints
# ═══════════════════════════════════════════════════════════════

@app.get("/api/memory/stats")
async def memory_stats(api_key: str = Depends(verify_api_key)):
    """Memory Statistiken"""
    if not AGENTS_AVAILABLE:
        return {"status": "unavailable"}
    
    memory: MemoryAgent = app.state.agents.get("memory")
    if not memory:
        return {"status": "not_initialized"}
    
    stats = memory.get_stats()
    return {"stats": stats}


# ═══════════════════════════════════════════════════════════════
#  Helper Functions
# ═══════════════════════════════════════════════════════════════

async def process_task(task_id: str, params: Dict, state):
    """Hintergrund-Verarbeitung einer Task"""
    queue: TaskQueue = state.task_queue
    
    task = queue.get_task(task_id)
    if not task:
        return
    
    queue.update_status(task_id, TaskStatus.RUNNING, progress=0.1)
    
    try:
        # Simple agent execution
        agent_name = task.agent
        
        if AGENTS_AVAILABLE and hasattr(state, 'agents'):
            agents = state.agents
            
            if agent_name in agents:
                # Execute agent
                result = {"status": "completed", "message": f"{agent_name} executed"}
                
                queue.update_status(
                    task_id,
                    TaskStatus.COMPLETED,
                    result=result,
                    progress=1.0
                )
            else:
                queue.update_status(
                    task_id,
                    TaskStatus.COMPLETED,
                    result={"status": "completed", "message": "Task processed"},
                    progress=1.0
                )
        else:
            # Mock result
            queue.update_status(
                task_id,
                TaskStatus.COMPLETED,
                result={"status": "completed", "message": "Task processed"},
                progress=1.0
            )
    
    except Exception as e:
        log.error(f"Task {task_id} failed: {e}")
        queue.update_status(task_id, TaskStatus.FAILED, error=str(e))


# ═══════════════════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
