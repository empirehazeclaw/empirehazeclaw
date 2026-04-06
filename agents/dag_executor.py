#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          DAG EXECUTION ENGINE                                ║
║          Parallele Tasks + Abhängigkeiten                    ║
╚══════════════════════════════════════════════════════════════╝

Unterstützt:
  - Parallele Ausführung von unabhängigen Tasks
  - Abhängigkeiten zwischen Tasks (DAG)
  - Error Handling mit Retry-Logik
  - Ergebnis-Aggregation

Hinweis: LLM-Routing wird NICHT verwendet
"""

from __future__ import annotations

import asyncio
import json
import time
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import uuid4
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [DAG] %(message)s")
log = logging.getLogger("openclaw.dag")


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class DAGTask:
    """Ein einzelner Task im DAG"""
    id: str
    agent: str
    action: str
    params: Dict = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    parallel_with: List[str] = field(default_factory=list)  # Tasks die parallel laufen können
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 2
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid4())


@dataclass
class DAGResult:
    """Ergebnis einer DAG-Ausführung"""
    dag_id: str
    status: str  # "success", "failed", "partial"
    tasks: List[DAGTask]
    total_duration: float
    completed_count: int
    failed_count: int
    results: Dict[str, Any] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)


class DAGExecutor:
    """
    Directed Acyclic Graph Executor
    
    Führt Tasks mit Abhängigkeiten aus:
    
    Beispiel:
        Task A (keine deps)
        Task B (depends on A)
        Task C (depends on A, parallel_with D)
        Task D (parallel with C)
        
        Execution:
        1. A läuft
        2. B, C, D laufen parallel (nach A)
    """
    
    def __init__(self, max_parallel: int = 3):
        self.max_parallel = max_parallel
        self.tasks: Dict[str, DAGTask] = {}
        self.agent_handlers: Dict[str, Callable] = {}
        
    def register_agent(self, agent_name: str, handler: Callable):
        """Registriere einen Agent-Handler"""
        self.agent_handlers[agent_name] = handler
        log.info(f"✅ Agent registriert: {agent_name}")
    
    def add_task(self, task: DAGTask):
        """Füge Task zum DAG hinzu"""
        self.tasks[task.id] = task
        log.info(f"➕ Task hinzugefügt: {task.agent} ({task.id[:8]})")
    
    def build_from_steps(self, steps: List[Dict]) -> List[DAGTask]:
        """
        Baue DAG aus Liste von Steps
        
        Example:
            steps = [
                {"agent": "research", "action": "recherche"},
                {"agent": "content", "action": "create", "depends_on": ["research"]},
                {"agent": "revenue", "action": "distribute", "depends_on": ["content"]}
            ]
        """
        task_map = {}
        
        for i, step in enumerate(steps):
            # Generate ID if not provided
            task_id = step.get("id") or f"task_{i}"
            
            task = DAGTask(
                id=task_id,
                agent=step["agent"],
                action=step["action"],
                params=step.get("params", {}),
                depends_on=step.get("depends_on", []),
                parallel_with=step.get("parallel_with", []),
                max_retries=step.get("max_retries", 2)
            )
            
            self.add_task(task)
            task_map[step["agent"]] = task_id
        
        # Auto-resolve dependencies if only agent names provided
        for task in self.tasks.values():
            if task.depends_on:
                resolved = []
                for dep in task.depends_on:
                    if dep in task_map:
                        resolved.append(task_map[dep])
                task.depends_on = resolved
        
        return list(self.tasks.values())
    
    def get_ready_tasks(self, completed: Set[str]) -> List[DAGTask]:
        """Finde alle Tasks die bereit sind zur Ausführung"""
        ready = []
        
        for task in self.tasks.values():
            if task.status != TaskStatus.PENDING:
                continue
                
            # Check if all dependencies are met
            deps_met = all(dep_id in completed for dep_id in task.depends_on)
            
            if deps_met:
                ready.append(task)
        
        return ready
    
    def can_run_parallel(self, task1: DAGTask, task2: DAGTask, running: Set[str]) -> bool:
        """Prüfe ob zwei Tasks parallel laufen können"""
        # Check explicit parallel_with
        if task2.id in task1.parallel_with or task1.id in task2.parallel_with:
            return True
        
        # Check if they have no dependencies on each other
        if task1.id not in task2.depends_on and task2.id not in task1.depends_on:
            return True
        
        return False
    
    async def execute_task(self, task: DAGTask) -> Any:
        """Führe einzelnen Task aus"""
        log.info(f"▶️  Starte: {task.agent} → {task.action}")
        
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        
        handler = self.agent_handlers.get(task.agent)
        
        if not handler:
            task.status = TaskStatus.FAILED
            task.error = f"No handler for agent: {task.agent}"
            log.error(f"❌ Kein Handler für {task.agent}")
            return None
        
        try:
            # Execute handler
            result = await handler(task.action, task.params)
            
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.now()
            
            duration = (task.completed_at - task.started_at).total_seconds()
            log.info(f"✅ Fertig: {task.agent} ({duration:.2f}s)")
            
            return result
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            
            log.error(f"❌ Fehler: {task.agent} → {e}")
            
            # Retry if possible
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                log.info(f"🔄 Retry {task.retry_count}/{task.max_retries} für {task.agent}")
                return await self.execute_task(task)
            
            return None
    
    async def execute(self) -> DAGResult:
        """
        Führe den gesamten DAG aus
        
        Returns:
            DAGResult mit allen Ergebnissen
        """
        dag_id = str(uuid4())
        start_time = time.time()
        
        completed: Set[str] = set()
        running: Set[str] = set()
        failed: Set[str] = set()
        
        log.info(f"🚀 Starte DAG: {dag_id}")
        
        while True:
            # Check if we're done
            if len(completed) + len(failed) == len(self.tasks):
                break
            
            # Get ready tasks
            ready = self.get_ready_tasks(completed)
            
            # Filter out already running
            ready = [t for t in ready if t.id not in running]
            
            if not ready:
                # No tasks ready - might be waiting on running or all failed
                if running:
                    await asyncio.sleep(0.5)
                    continue
                else:
                    log.warning("⚠️ Keine Tasks mehr bereit")
                    break
            
            # Limit parallel execution
            available_slots = self.max_parallel - len(running)
            ready = ready[:available_slots]
            
            # Execute in parallel
            if len(ready) > 1:
                log.info(f"⚡ Parallele Ausführung: {[t.agent for t in ready]}")
                tasks_coroutines = [self.execute_task(t) for t in ready]
                await asyncio.gather(*tasks_coroutines, return_exceptions=True)
            else:
                await self.execute_task(ready[0])
            
            # Update status sets
            for task in self.tasks.values():
                if task.status == TaskStatus.COMPLETED and task.id not in completed:
                    completed.add(task.id)
                elif task.status == TaskStatus.FAILED and task.id not in failed:
                    failed.add(task.id)
                elif task.status == TaskStatus.RUNNING:
                    running.add(task.id)
        
        # Build result
        total_duration = time.time() - start_time
        
        results = {
            task.id: task.result 
            for task in self.tasks.values() 
            if task.status == TaskStatus.COMPLETED
        }
        
        errors = {
            task.id: task.error 
            for task in self.tasks.values() 
            if task.status == TaskStatus.FAILED
        }
        
        status = "success" if not failed else "failed" if failed == len(self.tasks) else "partial"
        
        result = DAGResult(
            dag_id=dag_id,
            status=status,
            tasks=list(self.tasks.values()),
            total_duration=total_duration,
            completed_count=len(completed),
            failed_count=len(failed),
            results=results,
            errors=errors
        )
        
        log.info(f"🏁 DAG fertig: {status} | {len(completed)}/{len(self.tasks)} | {total_duration:.2f}s")
        
        return result
    
    def visualize(self) -> str:
        """Erstelle visuelle Darstellung des DAG"""
        lines = ["\n📊 DAG VISUALIZATION:\n"]
        
        for task in self.tasks.values():
            deps = ", ".join([d[:8] for d in task.depends_on]) or "None"
            lines.append(f"  [{task.status.value:8}] {task.id[:8]} | {task.agent:12} | {task.action:12} | deps: {deps}")
        
        return "\n".join(lines)


async def example_handler(action: str, params: Dict) -> str:
    """Beispiel-Handler für Tests"""
    await asyncio.sleep(0.5)  # Simulate work
    return f"Result of {action}"


def main():
    """CLI Test"""
    import sys
    
    executor = DAGExecutor(max_parallel=2)
    executor.register_agent("research", example_handler)
    executor.register_agent("content", example_handler)
    executor.register_agent("revenue", example_handler)
    executor.register_agent("memory", example_handler)
    
    # Build DAG from steps (like in your design)
    steps = [
        {"agent": "research", "action": "recherche"},
        {"agent": "content", "action": "create", "depends_on": ["research"]},
        {"agent": "revenue", "action": "distribute", "depends_on": ["content"]},
        {"agent": "memory", "action": "store", "depends_on": ["content"]}
    ]
    
    executor.build_from_steps(steps)
    
    print(executor.visualize())
    
    # Execute
    result = asyncio.run(executor.execute())
    
    print(f"\n✅ Ergebnis: {result.status}")
    print(f"   Duration: {result.total_duration:.2f}s")
    print(f"   Completed: {result.completed_count}/{len(result.tasks)}")


if __name__ == "__main__":
    main()
