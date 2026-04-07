#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          MULTI-SESSION MANAGER                          ║
║          Mehrere Tasks parallel ausführen                 ║
╚══════════════════════════════════════════════════════════════╝

Features:
  - Parallel Task Execution
  - Session Management
  - Resource Management
  - Task Queue
  - Concurrent Workflows
"""

import asyncio
import logging
import sys
import uuid
from collections import defaultdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [MULTI] %(message)s")
log = logging.getLogger("openclaw.multisession")

sys.path.insert(0, str(Path(__file__).parent.parent))


class SessionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskSession:
    """Eine einzelne Task-Session"""
    
    def __init__(self, task_id: str, task: str, session_id: str = None):
        self.task_id = task_id
        self.task = task
        self.session_id = session_id or str(uuid.uuid4())[:8]
        self.status = SessionStatus.PENDING
        self.result = None
        self.error = None
        self.started_at = None
        self.completed_at = None
        self.progress = 0
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "task": self.task,
            "session_id": self.session_id,
            "status": self.status.value,
            "progress": self.progress,
            "started_at": self.started_at,
            "completed_at": self.completed_at
        }


class MultiSessionManager:
    """
    Multi-Session Manager - Mehrere Tasks parallel!
    
    Features:
    - Parallele Ausführung (bis zu 5 gleichzeitig)
    - Session Tracking
    - Resource Management
    - Priority Queue
    """
    
    def __init__(self, max_parallel: int = 5):
        self.max_parallel = max_parallel
        self.sessions: Dict[str, TaskSession] = {}
        self.task_queue: List[TaskSession] = []
        self.running_tasks: Dict[str, asyncio.Task] = {}
        
        self.stats = {
            "total_sessions": 0,
            "completed": 0,
            "failed": 0,
            "parallel_executions": 0
        }
        
        log.info(f"🚀 Multi-Session Manager initialisiert (max {max_parallel} parallel)")
    
    async def submit_task(self, task: str, priority: int = 0) -> str:
        """
        Submitte eine neue Task
        
        Args:
            task: Die Task
            priority: Priorität (0=normal, höher=dringender)
            
        Returns:
            session_id
        """
        
        task_id = f"task_{self.stats['total_sessions'] + 1}"
        session = TaskSession(task_id, task)
        
        self.sessions[session.session_id] = session
        self.stats["total_sessions"] += 1
        
        # Add to queue with priority
        self.task_queue.append(session)
        self.task_queue.sort(key=lambda x: self.sessions[x.session_id].task_id)
        
        log.info(f"📝 Task eingereicht: {task} (session: {session.session_id})")
        
        # Try to start
        await self._process_queue()
        
        return session.session_id
    
    async def submit_batch(self, tasks: List[str]) -> List[str]:
        """
        Submitte mehrere Tasks auf einmal
        
        Args:
            tasks: Liste von Tasks
            
        Returns:
            Liste von session_ids
        """
        
        session_ids = []
        
        for task in tasks:
            sid = await self.submit_task(task)
            session_ids.append(sid)
        
        return session_ids
    
    async def _process_queue(self):
        """Verarbeite die Queue - starte wartende Tasks"""
        
        # Count running
        running = sum(1 for s in self.sessions.values() if s.status == SessionStatus.RUNNING)
        
        # Start available tasks
        while running < self.max_parallel and self.task_queue:
            session = self.task_queue.pop(0)
            
            if session.status == SessionStatus.PENDING:
                session.status = SessionStatus.RUNNING
                session.started_at = datetime.now().isoformat()
                
                # Start execution
                asyncio.create_task(self._execute_task(session))
                
                running += 1
                self.stats["parallel_executions"] += 1
                
                log.info(f"▶ Starte Task: {session.task} (session: {session.session_id})")
    
    async def _execute_task(self, session: TaskSession):
        """Führe eine Task aus"""
        
        try:
            # Simulate task execution
            # In real: call actual agent
            await asyncio.sleep(1)  # Simulate work
            
            session.status = SessionStatus.COMPLETED
            session.result = {"success": True, "output": f"Task '{session.task}' completed"}
            session.progress = 100
            session.completed_at = datetime.now().isoformat()
            
            self.stats["completed"] += 1
            
            log.info(f"✅ Task abgeschlossen: {session.task}")
            
        except Exception as e:
            session.status = SessionStatus.FAILED
            session.error = str(e)
            session.completed_at = datetime.now().isoformat()
            
            self.stats["failed"] += 1
            
            log.error(f"❌ Task fehlgeschlagen: {session.task} - {e}")
        
        # Process next in queue
        await self._process_queue()
    
    async def get_status(self, session_id: str) -> Optional[Dict]:
        """Gib Status einer Session"""
        
        session = self.sessions.get(session_id)
        
        if session:
            return session.to_dict()
        
        return None
    
    async def get_all_status(self) -> List[Dict]:
        """Gib Status aller Sessions"""
        
        return [
            s.to_dict() for s in self.sessions.values()
        ]
    
    async def cancel_task(self, session_id: str) -> bool:
        """Cancelliere eine Task"""
        
        session = self.sessions.get(session_id)
        
        if session and session.status == SessionStatus.RUNNING:
            session.status = SessionStatus.CANCELLED
            session.completed_at = datetime.now().isoformat()
            
            log.info(f"🛑 Task cancelled: {session.task}")
            
            return True
        
        return False
    
    async def wait_for_completion(self, session_ids: List[str], timeout: float = 60) -> Dict:
        """
        Warte auf Abschluss mehrerer Tasks
        
        Args:
            session_ids: Liste von session_ids
            timeout: Timeout in Sekunden
            
        Returns:
            Dict mit Ergebnissen
        """
        
        start = asyncio.get_event_loop().time()
        
        while True:
            # Check if all done
            all_done = True
            results = {}
            
            for sid in session_ids:
                session = self.sessions.get(sid)
                
                if not session:
                    results[sid] = {"error": "Session not found"}
                    continue
                
                if session.status not in [SessionStatus.COMPLETED, SessionStatus.FAILED, SessionStatus.CANCELLED]:
                    all_done = False
                
                results[sid] = {
                    "status": session.status.value,
                    "result": session.result,
                    "error": session.error
                }
            
            if all_done:
                return results
            
            # Check timeout
            if asyncio.get_event_loop().time() - start > timeout:
                return {"error": "Timeout", "results": results}
            
            await asyncio.sleep(0.5)
    
    def get_stats(self) -> Dict:
        """Gib Statistiken"""
        
        return {
            **self.stats,
            "queue_length": len(self.task_queue),
            "running": sum(1 for s in self.sessions.values() if s.status == SessionStatus.RUNNING),
            "completed": sum(1 for s in self.sessions.values() if s.status == SessionStatus.COMPLETED),
            "failed": sum(1 for s in self.sessions.values() if s.status == SessionStatus.FAILED)
        }


# Global instance
_multi_session = None


def get_multi_session_manager() -> MultiSessionManager:
    """Hol den globalen Multi-Session Manager"""
    global _multi_session
    if _multi_session is None:
        _multi_session = MultiSessionManager()
    return _multi_session


if __name__ == "__main__":
    async def test():
        m = MultiSessionManager(max_parallel=3)
        
        # Submit multiple tasks
        print("=== MULTI-SESSION TEST ===\n")
        
        tasks = [
            "Research: KI Trends",
            "Create Blog Post",
            "Send Outreach Emails",
            "Check Analytics",
            "Post on Twitter"
        ]
        
        print(f"Submitting {len(tasks)} tasks...")
        
        session_ids = await m.submit_batch(tasks)
        
        print(f"Session IDs: {session_ids}\n")
        
        # Wait for completion
        results = await m.wait_for_completion(session_ids, timeout=30)
        
        print("=== RESULTS ===")
        for sid, result in results.items():
            print(f"  {sid}: {result['status']}")
        
        print(f"\n=== STATS ===")
        print(m.get_stats())
    
    asyncio.run(test())
