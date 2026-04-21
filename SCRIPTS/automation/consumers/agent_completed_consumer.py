#!/usr/bin/env python3
"""
Agent Completed Consumer — Phase 2 of Improvement Plan
======================================================
Consumes agent_completed events from Event Bus.
Updates agent stats in KG, detects failure patterns.

Event Types Handled:
  - agent_completed: Agent finished a task (success/failure)
  - task_completed: Task completed (alternative event type)

This addresses the gap: 827+ agent_completed events with no consumer.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
KG_PATH = WORKSPACE / "ceo/memory/kg/knowledge_graph.json"

# Note: These are imported inside functions to avoid circular imports
# from learnings_service import LearningsService
# from event_bus import publish_event


class AgentCompletedConsumer:
    """
    Consumes agent_completed events and:
    1. Updates agent stats in KG
    2. Detects failure patterns
    3. Triggers learning_recording for failures
    """
    
    def __init__(self):
        self.learnings_service = None
        self.publish_event = None
        self.state_file = WORKSPACE / "data/events/agent_completed_state.json"
        self.state = self._load_state()
    
    def _load_state(self) -> dict:
        """Load consumer state for incremental processing."""
        if self.state_file.exists():
            return json.loads(self.state_file.read_text())
        return {
            "last_event_id": None,
            "events_processed": 0,
            "success_count": 0,
            "failure_count": 0,
            "last_failure": None,
            "failure_patterns": {},  # pattern -> count
            "agent_stats": {}  # agent_id -> stats
        }
    
    def _save_state(self):
        """Save consumer state."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(self.state, indent=2))
    
    def handles(self) -> List[str]:
        """Return list of event types this consumer handles."""
        return ["agent_completed", "task_completed"]
    
    def consume(self, event: dict) -> bool:
        """
        Process a single event.
        
        Returns True if processed, False to skip.
        """
        try:
            event_type = event.get("type", "")
            if event_type not in ["agent_completed", "task_completed"]:
                return False
            
            data = event.get("data", {})
            agent_id = data.get("agent_id", "unknown")
            task = data.get("task", "unknown")
            status = data.get("status", "unknown")
            error = data.get("error")
            duration_ms = data.get("duration_ms", 0)
            
            # Update stats
            self.state["events_processed"] += 1
            
            if status == "success" or status == "completed":
                self.state["success_count"] += 1
            else:
                self.state["failure_count"] += 1
                self._handle_failure(agent_id, task, error, event)
            
            # Update agent-specific stats
            if agent_id not in self.state["agent_stats"]:
                self.state["agent_stats"][agent_id] = {
                    "total": 0, "success": 0, "failure": 0, "avg_duration_ms": 0
                }
            
            stats = self.state["agent_stats"][agent_id]
            stats["total"] += 1
            if status == "success" or status == "completed":
                stats["success"] += 1
            else:
                stats["failure"] += 1
            
            # Update average duration
            total_duration = stats["avg_duration_ms"] * (stats["total"] - 1) + duration_ms
            stats["avg_duration_ms"] = total_duration / stats["total"]
            
            # Update KG with agent stats
            self._update_kg_agent_stats(agent_id, stats)
            
            self.state["last_event_id"] = event.get("id")
            self._save_state()
            
            return True
            
        except Exception as e:
            print(f"Error processing event: {e}")
            return False
    
    def _handle_failure(self, agent_id: str, task: str, error: Optional[str], event: dict):
        """Handle a failed task - record pattern and optionally trigger learning."""
        self.state["last_failure"] = {
            "timestamp": event.get("timestamp"),
            "agent_id": agent_id,
            "task": task,
            "error": str(error)[:200] if error else None
        }
        
        # Detect failure pattern (simple keyword extraction)
        if error:
            error_keywords = self._extract_error_keywords(str(error))
            for kw in error_keywords:
                self.state["failure_patterns"][kw] = self.state["failure_patterns"].get(kw, 0) + 1
        
        # Trigger learning if this is a new failure pattern
        if error and self.learnings_service:
            error_str = str(error)
            # Check if this is a recurring failure
            recurring = self._is_recurring_failure(agent_id, task, error_str)
            
            if recurring:
                # Record a learning from this failure
                self.learnings_service.record_learning(
                    source=f"Agent Completed Consumer",
                    category="failure",
                    learning=f"Agent {agent_id} task '{task}' failed with: {error_str[:200]}",
                    context="system_optimization",
                    outcome="failure",
                    metadata={
                        "agent_id": agent_id,
                        "task": task,
                        "recurring": True,
                        "event_id": event.get("id")
                    }
                )
                
                # Publish event for other consumers
                if publish_event:
                    publish_event(
                        event_type="learning_issues_detected",
                        source="agent_completed_consumer",
                        data={
                            "severity": "MEDIUM",
                            "type": "recurring_failure",
                            "agent_id": agent_id,
                            "task": task,
                            "description": f"Recurring failure: {error_str[:100]}"
                        }
                    )
    
    def _extract_error_keywords(self, error: str) -> List[str]:
        """Extract keywords from error message."""
        keywords = []
        error_lower = error.lower()
        
        # Common error patterns
        patterns = [
            "timeout", "connection", "permission", "not found", 
            "syntax", "import", "memory", "disk", "network",
            "invalid", "failed", "error", "crash", "exception"
        ]
        
        for p in patterns:
            if p in error_lower:
                keywords.append(p)
        
        return keywords
    
    def _is_recurring_failure(self, agent_id: str, task: str, error: str) -> bool:
        """Check if this is a recurring failure pattern."""
        error_hash = hash(error[:100]) if error else 0
        
        # Check last 10 failures for same agent+task
        recent_failures = self.state.get("recent_failures", [])
        
        for f in recent_failures[-10:]:
            if f.get("agent_id") == agent_id and f.get("task") == task:
                # Same agent + task in last 10 failures
                return True
        
        # Track this failure
        self.state.setdefault("recent_failures", []).append({
            "agent_id": agent_id,
            "task": task,
            "error_hash": error_hash,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 50
        if len(self.state["recent_failures"]) > 50:
            self.state["recent_failures"] = self.state["recent_failures"][-50:]
        
        return False
    
    def _update_kg_agent_stats(self, agent_id: str, stats: dict):
        """Update agent stats in Knowledge Graph."""
        try:
            if not KG_PATH.exists():
                return
            
            kg = json.loads(KG_PATH.read_text())
            
            # Create or update agent entity
            agent_entity_id = f"agent_{agent_id}"
            if agent_entity_id not in kg.get("entities", {}):
                kg.setdefault("entities", {})[agent_entity_id] = {
                    "type": "Agent",
                    "name": agent_id,
                    "facts": [],
                    "relations": []
                }
            
            entity = kg["entities"][agent_entity_id]
            entity["last_updated"] = datetime.now().isoformat()
            
            # Update stats in entity
            entity["total_tasks"] = stats.get("total", 0)
            entity["success_count"] = stats.get("success", 0)
            entity["failure_count"] = stats.get("failure", 0)
            entity["success_rate"] = (
                stats["success"] / stats["total"] if stats["total"] > 0 else 0
            )
            entity["avg_duration_ms"] = stats.get("avg_duration_ms", 0)
            
            # Add recent activity fact
            activity = f"Task completed at {datetime.now().isoformat()}"
            if "facts" not in entity:
                entity["facts"] = []
            entity["facts"].append(activity)
            
            # Keep only last 10 facts
            entity["facts"] = entity["facts"][-10:]
            
            # Save KG
            KG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(KG_PATH, 'w') as f:
                json.dump(kg, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Failed to update KG: {e}")
    
    def get_failure_trends(self) -> Dict:
        """Get trending failure patterns."""
        patterns = self.state.get("failure_patterns", {})
        sorted_patterns = sorted(patterns.items(), key=lambda x: -x[1])[:10]
        
        return {
            "top_patterns": [{"keyword": k, "count": c} for k, c in sorted_patterns],
            "total_failures": self.state.get("failure_count", 0),
            "last_failure": self.state.get("last_failure")
        }
    
    def get_agent_stats(self) -> Dict:
        """Get stats for all agents."""
        return self.state.get("agent_stats", {})


def run_consumer():
    """Run the consumer on recent events."""
    from event_bus import list_events, CONSUMERS
    
    consumer = AgentCompletedConsumer()
    
    # Check if already registered
    registered_types = []
    for c in CONSUMERS:
        registered_types.extend(c.handles())
    
    if "agent_completed" not in registered_types:
        print("Warning: AgentCompletedConsumer not registered in event_bus.py")
        print("Run: python3 event_bus.py consumers to see registered consumers")
    
    # Process recent events
    events = list_events(event_type="agent_completed", limit=100)
    
    processed = 0
    for event in events:
        if consumer.consume(event):
            processed += 1
    
    print(f"Agent Completed Consumer: Processed {processed} events")
    
    stats = consumer.get_agent_stats()
    print(f"Agents tracked: {len(stats)}")
    
    trends = consumer.get_failure_trends()
    if trends["top_patterns"]:
        print(f"Top failure patterns:")
        for p in trends["top_patterns"][:5]:
            print(f"  {p['keyword']}: {p['count']}")


if __name__ == "__main__":
    import argparse
    
    consumer = AgentCompletedConsumer()
    parser = argparse.ArgumentParser(description="Agent Completed Consumer")
    
    sub = parser.add_subparsers(dest="cmd")
    
    sub.add_parser("run", help="Run consumer on recent events")
    sub.add_parser("stats", help="Show consumer stats")
    sub.add_parser("trends", help="Show failure trends")
    sub.add_parser("agents", help="Show agent stats")
    
    args = parser.parse_args()
    
    if args.cmd == "run":
        run_consumer()
    
    elif args.cmd == "stats":
        print(f"Events processed: {consumer.state.get('events_processed', 0)}")
        print(f"Success: {consumer.state.get('success_count', 0)}")
        print(f"Failures: {consumer.state.get('failure_count', 0)}")
    
    elif args.cmd == "trends":
        trends = consumer.get_failure_trends()
        print("Failure Trends:")
        for p in trends["top_patterns"]:
            print(f"  {p['keyword']}: {p['count']}")
    
    elif args.cmd == "agents":
        stats = consumer.get_agent_stats()
        print("Agent Stats:")
        for agent_id, s in stats.items():
            rate = s["success"] / s["total"] if s["total"] > 0 else 0
            print(f"  {agent_id}: {s['total']} tasks, {rate:.1%} success")
    
    else:
        parser.print_help()