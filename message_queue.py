#!/usr/bin/env python3
"""
Message Queue for Agent Task Distribution
- Uses Redis as backend
- Task queue with priorities
- Worker pool support
"""

import redis
import json
import uuid
from datetime import datetime
from enum import Enum

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

class Priority(Enum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3

TASK_QUEUE = "agent:tasks:queue"
TASK_PROCESSING = "agent:tasks:processing"
TASK_COMPLETED = "agent:tasks:completed"

def enqueue_task(agent_type, task_data, priority=Priority.MEDIUM):
    """Add task to queue"""
    task = {
        "id": str(uuid.uuid4()),
        "agent_type": agent_type,
        "task_data": task_data,
        "priority": priority.value,
        "created": datetime.now().isoformat(),
        "status": "pending"
    }
    
    # Add to sorted set with priority as score
    r.zadd(TASK_QUEUE, {json.dumps(task): priority.value})
    
    return task["id"]

def dequeue_task(agent_type=None):
    """Get next task from queue"""
    # Get highest priority task
    if agent_type:
        # Filter by agent type
        tasks = r.zrange(TASK_QUEUE, 0, -1, withscores=True)
        for task_json, score in tasks:
            task = json.loads(task_json)
            if task.get("agent_type") == agent_type:
                r.zrem(TASK_QUEUE, task_json)
                r.zadd(TASK_PROCESSING, {task_json: datetime.now().timestamp()})
                return task
        return None
    else:
        # Get any task
        tasks = r.zrange(TASK_QUEUE, 0, 0, withscores=True)
        if tasks:
            task_json, score = tasks[0]
            task = json.loads(task_json)
            r.zrem(TASK_QUEUE, task_json)
            r.zadd(TASK_PROCESSING, {task_json: datetime.now().timestamp()})
            return task
    return None

def complete_task(task_id):
    """Mark task as completed"""
    tasks = r.zrange(TASK_PROCESSING, 0, -1)
    for task_json in tasks:
        task = json.loads(task_json)
        if task.get("id") == task_id:
            task["status"] = "completed"
            task["completed"] = datetime.now().isoformat()
            r.zrem(TASK_PROCESSING, task_json)
            r.zadd(TASK_COMPLETED, {json.dumps(task): datetime.now().timestamp()})
            return True
    return False

def get_queue_stats():
    """Get queue statistics"""
    pending = r.zcard(TASK_QUEUE)
    processing = r.zcard(TASK_PROCESSING)
    completed = r.zcard(TASK_COMPLETED)
    
    return {
        "pending": pending,
        "processing": processing,
        "completed": completed
    }

def get_pending_tasks(limit=10):
    """Get pending tasks"""
    tasks = r.zrange(TASK_QUEUE, 0, limit-1, withscores=True)
    return [json.loads(t[0]) for t in tasks]

# CLI
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "enqueue":
            agent = sys.argv[2] if len(sys.argv) > 2 else "general"
            task = sys.argv[3] if len(sys.argv) > 3 else "Test task"
            priority = Priority[sys.argv[4].upper()] if len(sys.argv) > 4 else Priority.MEDIUM
            
            task_id = enqueue_task(agent, task, priority)
            print(f"✅ Task enqueued: {task_id}")
        
        elif cmd == "dequeue":
            agent = sys.argv[2] if len(sys.argv) > 2 else None
            task = dequeue_task(agent)
            if task:
                print(f"📥 Dequeued: {task}")
            else:
                print("Queue empty")
        
        elif cmd == "stats":
            stats = get_queue_stats()
            print(f"📊 Queue Stats:")
            print(f"   Pending: {stats['pending']}")
            print(f"   Processing: {stats['processing']}")
            print(f"   Completed: {stats['completed']}")
        
        elif cmd == "list":
            tasks = get_pending_tasks()
            print(f"📋 Pending Tasks ({len(tasks)}):")
            for t in tasks:
                print(f"   - [{t['agent_type']}] {t['task_data'][:50]}")
    else:
        print("Message Queue CLI")
        print("Usage: message_queue.py [enqueue|dequeue|stats|list]")
