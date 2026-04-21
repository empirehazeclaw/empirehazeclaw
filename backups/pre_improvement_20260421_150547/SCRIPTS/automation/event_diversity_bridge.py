#!/usr/bin/env python3
"""
Event Diversity Bridge — CEO System Integration
==============================================
Bridges events from various subsystems to the CEO Event Bus.

This script ensures event diversity by publishing events from:
1. Health Monitor (process/memory/disk events)
2. Learning Loop (task_completed, task_failed events)
3. Agent System (agent_delegated, agent_completed events)
4. Cron System (cron_triggered, cron_failed events)

Usage:
    python3 event_diversity_bridge.py --health-events
    python3 event_diversity_bridge.py --learning-events
    python3 event_diversity_bridge.py --agent-events
    python3 event_diversity_bridge.py --cron-events
    python3 event_diversity_bridge.py --all    # All events

Uses the CEO Event Bus (event_bus.py) for publishing.
"""

import os
import sys
import json
import subprocess
import socket
import psutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Config
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
EVENT_BUS = WORKSPACE / "scripts" / "event_bus.py"

# Thresholds
DISK_THRESHOLD = 15  # %
MEMORY_THRESHOLD = 85  # %
LOAD_THRESHOLD = 4.0

CRON_JOBS_PATH = "/home/clawbot/.openclaw/cron/jobs.json"


def publish_event(event_type: str, source: str, data: dict, severity: str = "info") -> dict:
    """Publish an event to the CEO Event Bus."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("event_bus", str(EVENT_BUS))
        event_bus = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(event_bus)
        
        return event_bus.publish_event(event_type, source, data, severity)
    except Exception as e:
        print(f"   ⚠️ Event bus publish failed: {e}")
        return {"error": str(e)}


# ============================================================================
# HEALTH MONITOR EVENTS
# ============================================================================

def check_gateway_health() -> Tuple[bool, dict]:
    """Check gateway health and return status with details."""
    GATEWAY_HOST = "127.0.0.1"
    GATEWAY_PORT = 18789
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((GATEWAY_HOST, GATEWAY_PORT))
        sock.close()
        
        if result == 0:
            return True, {"host": GATEWAY_HOST, "port": GATEWAY_PORT, "status": "responding"}
        else:
            return False, {"host": GATEWAY_HOST, "port": GATEWAY_PORT, "status": "unreachable", "error": "port_connect_failed"}
    except Exception as e:
        return False, {"host": GATEWAY_HOST, "port": GATEWAY_PORT, "status": "error", "error": str(e)}


def check_disk_health() -> Tuple[bool, dict]:
    """Check disk health and return status with details."""
    try:
        usage = psutil.disk_usage('/')
        percent = usage.percent
        free_gb = usage.free / (1024**3)
        total_gb = usage.total / (1024**3)
        
        is_healthy = percent < (100 - DISK_THRESHOLD)
        
        return is_healthy, {
            "percent_used": round(percent, 1),
            "free_gb": round(free_gb, 2),
            "total_gb": round(total_gb, 2),
            "threshold": DISK_THRESHOLD,
            "status": "healthy" if is_healthy else "critical"
        }
    except Exception as e:
        return False, {"status": "error", "error": str(e)}


def check_memory_health() -> Tuple[bool, dict]:
    """Check memory health and return status with details."""
    try:
        mem = psutil.virtual_memory()
        percent = mem.percent
        available_gb = mem.available / (1024**3)
        total_gb = mem.total / (1024**3)
        used_gb = mem.used / (1024**3)
        
        is_healthy = percent < MEMORY_THRESHOLD
        
        return is_healthy, {
            "percent_used": round(percent, 1),
            "available_gb": round(available_gb, 2),
            "used_gb": round(used_gb, 2),
            "total_gb": round(total_gb, 2),
            "threshold": MEMORY_THRESHOLD,
            "status": "healthy" if is_healthy else "high"
        }
    except Exception as e:
        return False, {"status": "error", "error": str(e)}


def check_load_health() -> Tuple[bool, dict]:
    """Check system load and return status with details."""
    try:
        load = psutil.getloadavg()
        
        is_healthy = load[0] < LOAD_THRESHOLD
        
        return is_healthy, {
            "load_1m": round(load[0], 2),
            "load_5m": round(load[1], 2),
            "load_15m": round(load[2], 2),
            "threshold": LOAD_THRESHOLD,
            "status": "healthy" if is_healthy else "high"
        }
    except Exception as e:
        return False, {"status": "error", "error": str(e)}


def publish_health_events():
    """Publish health monitoring events - only on state changes."""
    print("🏥 Publishing Health Monitor Events...")
    
    events_published = 0
    
    # State file to track previous state
    STATE_FILE = WORKSPACE / "data" / "health_event_state.json"
    
    # Load previous state
    previous_state = {}
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                previous_state = json.load(f)
        except:
            pass
    
    # Gateway check
    ok, data = check_gateway_health()
    check_name = "gateway"
    prev_status = previous_state.get(check_name, {}).get("status")
    curr_status = data.get("status")
    
    # Only publish on state change
    if prev_status != curr_status:
        if ok:
            publish_event("health_check_passed", "health_monitor", {
                "check": check_name,
                **data
            })
        else:
            publish_event("health_check_failed", "health_monitor", {
                "check": check_name,
                **data
            }, "warning")
        events_published += 1
    
    # Disk check
    ok, data = check_disk_health()
    check_name = "disk"
    prev_status = previous_state.get(check_name, {}).get("status")
    curr_status = data.get("status")
    
    # Publish on state change or threshold breach
    if prev_status != curr_status or (curr_status == "critical" and prev_status != "critical"):
        if ok:
            publish_event("health_check_passed", "health_monitor", {
                "check": check_name,
                **data
            })
        else:
            publish_event("disk_low", "health_monitor", {
                **data
            }, "warning")
        events_published += 1
    
    # Memory check
    ok, data = check_memory_health()
    check_name = "memory"
    prev_status = previous_state.get(check_name, {}).get("status")
    curr_status = data.get("status")
    
    # Publish on state change or threshold breach
    if prev_status != curr_status or (curr_status == "high" and prev_status != "high"):
        if ok:
            publish_event("health_check_passed", "health_monitor", {
                "check": check_name,
                **data
            })
        else:
            publish_event("memory_high", "health_monitor", {
                **data
            }, "warning")
        events_published += 1
    
    # Load check
    ok, data = check_load_health()
    check_name = "load"
    prev_status = previous_state.get(check_name, {}).get("status")
    curr_status = data.get("status")
    
    # Publish on state change or threshold breach
    if prev_status != curr_status or (curr_status == "high" and prev_status != "high"):
        if ok:
            publish_event("health_check_passed", "health_monitor", {
                "check": check_name,
                **data
            })
        else:
            publish_event("load_high", "health_monitor", {
                **data
            }, "warning")
        events_published += 1
    
    # Save current state
    new_state = {
        "gateway": {"status": check_gateway_health()[1].get("status")},
        "disk": check_disk_health()[1],
        "memory": check_memory_health()[1],
        "load": check_load_health()[1],
        "timestamp": datetime.now().isoformat()
    }
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(new_state, f)
    except:
        pass
    
    # Always publish a summary health event (but only if something changed or periodic)
    publish_event("system_health_summary", "health_monitor", {
        "gateway": check_gateway_health()[1].get("status"),
        "disk": check_disk_health()[1].get("percent_used"),
        "memory": check_memory_health()[1].get("percent_used"),
        "load_1m": check_load_health()[1].get("load_1m")
    })
    events_published += 1
    
    print(f"   ✅ Published {events_published} health events")
    return events_published


# ============================================================================
# LEARNING LOOP EVENTS
# ============================================================================

def publish_learning_events():
    """Publish learning loop task events."""
    print("🎯 Publishing Learning Loop Events...")
    
    events_published = 0
    
    # Load learning loop state to determine recent activity
    STATE_FILE = WORKSPACE / "data" / "learning_loop_state.json"
    
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                state = json.load(f)
            
            iteration = state.get("iteration", 0)
            score = state.get("score", 0)
            val_success = state.get("validation_successes", 0)
            val_fail = state.get("validation_failures", 0)
            
            # Publish learning loop health
            if iteration > 0:
                publish_event("learning_healthy", "learning_loop", {
                    "iteration": iteration,
                    "score": round(score, 3),
                    "validation_successes": val_success,
                    "validation_failures": val_fail
                })
                events_published += 1
            
            # Check for recent validation
            improvements_file = WORKSPACE / "data" / "learning_loop" / "improvements.json"
            if improvements_file.exists():
                with open(improvements_file) as f:
                    improvements = json.load(f)
                
                recent = improvements.get("improvements", [])[-5:]
                for imp in recent:
                    validated = imp.get("validated", False)
                    event_type = "task_completed" if validated else "task_failed"
                    
                    publish_event(event_type, "learning_loop", {
                        "title": imp.get("title", "unknown")[:100],
                        "validated": validated,
                        "timestamp": imp.get("timestamp")
                    }, "info" if validated else "warning")
                    events_published += 1
                    
        except Exception as e:
            print(f"   ⚠️ Failed to read learning loop state: {e}")
    
    print(f"   ✅ Published {events_published} learning events")
    return events_published


# ============================================================================
# AGENT SYSTEM EVENTS
# ============================================================================

def publish_agent_events():
    """Publish agent delegation and completion events - only on state changes."""
    print("🤖 Publishing Agent System Events...")
    
    events_published = 0
    
    # State file to track previous state
    STATE_FILE = WORKSPACE / "data" / "agent_event_state.json"
    
    # Load previous state
    previous_state = {
        "completed_task_ids": set(),
        "failed_task_ids": set(),
        "pending_task_ids": set()
    }
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                data = json.load(f)
            previous_state["completed_task_ids"] = set(data.get("completed_task_ids", []))
            previous_state["failed_task_ids"] = set(data.get("failed_task_ids", []))
            previous_state["pending_task_ids"] = set(data.get("pending_task_ids", []))
        except:
            pass
    
    # Check orchestrator state
    ORCHESTRATOR_STATE = WORKSPACE / "ceo" / "memory" / "evaluations" / "orchestrator_state.json"
    
    current_completed = set()
    current_failed = set()
    current_pending = set()
    
    if ORCHESTRATOR_STATE.exists():
        try:
            with open(ORCHESTRATOR_STATE) as f:
                state = json.load(f)
            
            delegated = state.get("delegated_tasks", [])
            completed_tasks = state.get("completed_tasks", [])
            failed_tasks = state.get("failed_tasks", [])
            
            # Get current task IDs (as strings to avoid hashing issues)
            for task in delegated:
                task_id = str(task.get("task_id", ""))
                if task.get("status") == "pending":
                    current_pending.add(task_id)
                    # Only publish NEW pending tasks
                    if task_id not in previous_state["pending_task_ids"]:
                        publish_event("agent_delegated", "agent_system", {
                            "task_id": task_id,
                            "task_type": task.get("type"),
                            "delegated_to": task.get("delegated_to"),
                            "priority": task.get("priority"),
                            "created_at": task.get("created_at")
                        })
                        events_published += 1
            
            # Track completed task IDs (as strings) - completed_tasks can be list of task_ids or full objects
            for item in completed_tasks:
                if isinstance(item, dict):
                    task_id_str = str(item.get("task_id", ""))
                else:
                    task_id_str = str(item)
                
                current_completed.add(task_id_str)
                # Only publish NEW completions
                if task_id_str not in previous_state["completed_task_ids"]:
                    publish_event("agent_completed", "agent_system", {
                        "task_id": task_id_str,
                        "status": "completed"
                    })
                    events_published += 1
            
            # Track failed task IDs (as strings) - failed_tasks can be list of task_ids or full objects
            for item in failed_tasks:
                if isinstance(item, dict):
                    task_id_str = str(item.get("task_id", ""))
                else:
                    task_id_str = str(item)
                
                current_failed.add(task_id_str)
                # Only publish NEW failures
                if task_id_str not in previous_state["failed_task_ids"]:
                    publish_event("agent_failed", "agent_system", {
                        "task_id": task_id_str,
                        "status": "failed"
                    }, "warning")
                    events_published += 1
                
        except Exception as e:
            print(f"   ⚠️ Failed to read agent state: {e}")
    
    # Save current state
    new_state = {
        "completed_task_ids": list(current_completed),
        "failed_task_ids": list(current_failed),
        "pending_task_ids": list(current_pending),
        "timestamp": datetime.now().isoformat()
    }
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(new_state, f)
    except:
        pass
    
    print(f"   ✅ Published {events_published} agent events")
    return events_published


# ============================================================================
# CRON SYSTEM EVENTS
# ============================================================================

def check_cron_jobs() -> Tuple[List[dict], List[dict], List[dict]]:
    """Check cron jobs and return enabled, failed, and disabled lists."""
    enabled = []
    failed = []
    disabled = []
    
    if not Path(CRON_JOBS_PATH).exists():
        return enabled, failed, disabled
    
    try:
        with open(CRON_JOBS_PATH) as f:
            data = json.load(f)
        
        jobs = data.get("jobs", [])
        
        for job in jobs:
            if job.get("enabled", True):
                enabled.append(job)
                if job.get("state", {}).get("lastRunStatus") == "error":
                    failed.append(job)
            else:
                disabled.append(job)
                
    except Exception as e:
        print(f"   ⚠️ Failed to read cron jobs: {e}")
    
    return enabled, failed, disabled


def publish_cron_events():
    """Publish cron system events - only on state changes."""
    print("⏰ Publishing Cron System Events...")
    
    events_published = 0
    
    # State file to track previous state
    STATE_FILE = WORKSPACE / "data" / "cron_event_state.json"
    
    # Load previous state
    previous_failed = set()
    previous_state = {}
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                previous_state = json.load(f)
            previous_failed = set(previous_state.get("failed_jobs", []))
        except:
            pass
    
    enabled, failed, disabled = check_cron_jobs()
    
    # Get current failed job IDs
    current_failed_ids = set()
    for job in failed:
        job_id = job.get("id", "unknown")
        job_name = job.get("name", "unknown")
        current_failed_ids.add(job_id)
        
        # Only publish if this is a NEW failure or the error changed
        if job_id not in previous_failed:
            publish_event("cron_failed", "cron_system", {
                "job_name": job_name,
                "job_id": job_id,
                "error": job.get("state", {}).get("lastError", "unknown"),
                "consecutive_errors": job.get("state", {}).get("consecutiveErrors", 0)
            }, "warning")
            events_published += 1
        else:
            # Check if error message changed
            prev_error = previous_state.get("job_errors", {}).get(job_id, "")
            curr_error = job.get("state", {}).get("lastError", "")
            if prev_error != curr_error:
                publish_event("cron_failed", "cron_system", {
                    "job_name": job_name,
                    "job_id": job_id,
                    "error": curr_error,
                    "consecutive_errors": job.get("state", {}).get("consecutiveErrors", 0),
                    "error_changed": True
                }, "warning")
                events_published += 1
    
    # Publish recovery events for jobs that were failing but now ok
    recovered = previous_failed - current_failed_ids
    for job_id in recovered:
        publish_event("cron_recovered", "cron_system", {
            "job_id": job_id,
            "previous_error": previous_state.get("job_errors", {}).get(job_id, "unknown")
        }, "info")
        events_published += 1
    
    # Publish ONE cron_summary event (not per-job)
    publish_event("cron_summary", "cron_system", {
        "total_enabled": len(enabled),
        "total_failed": len(failed),
        "total_disabled": len(disabled),
        "health_status": "healthy" if len(failed) == 0 else "degraded",
        "new_failures": len(failed) - len(recovered & current_failed_ids) if current_failed_ids else 0
    })
    events_published += 1
    
    # Save current state
    new_state = {
        "failed_jobs": list(current_failed_ids),
        "job_errors": {job.get("id", "unknown"): job.get("state", {}).get("lastError", "") for job in failed},
        "timestamp": datetime.now().isoformat()
    }
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(new_state, f)
    except:
        pass
    
    print(f"   ✅ Published {events_published} cron events")
    return events_published


# ============================================================================
# MAIN
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Event Diversity Bridge")
    parser.add_argument("--health-events", action="store_true", help="Publish health monitor events")
    parser.add_argument("--learning-events", action="store_true", help="Publish learning loop events")
    parser.add_argument("--agent-events", action="store_true", help="Publish agent system events")
    parser.add_argument("--cron-events", action="store_true", help="Publish cron system events")
    parser.add_argument("--all", action="store_true", help="Publish all events")
    
    args = parser.parse_args()
    
    # Default to all if no specific flag
    if not any([args.health_events, args.learning_events, args.agent_events, args.cron_events, args.all]):
        args.all = True
    
    print("=" * 60)
    print("🔗 Event Diversity Bridge")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)
    print()
    
    total_events = 0
    
    if args.all or args.health_events:
        total_events += publish_health_events()
        print()
    
    if args.all or args.learning_events:
        total_events += publish_learning_events()
        print()
    
    if args.all or args.agent_events:
        total_events += publish_agent_events()
        print()
    
    if args.all or args.cron_events:
        total_events += publish_cron_events()
        print()
    
    print("=" * 60)
    print(f"✅ Total events published: {total_events}")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
