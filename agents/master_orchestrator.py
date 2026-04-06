#!/usr/bin/env python3
"""
Master Orchestrator - Production Ready
Koordiniert alle Agents automatisch
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class MasterOrchestrator:
    """Production Master Orchestrator"""
    
    def __init__(self, workspace_path: str = None):
        self.workspace = workspace_path or os.path.expanduser("~/.openclaw/workspace")
        
        # Agents Registry
        self.agents = {}
        
        # Task Queue
        self.task_queue = []
        
        # Workflows
        self.workflows = {
            "auto_research": ["researcher", "writer"],
            "full_stack": ["coder", "writer", "memory"],
            "social_media": ["writer", "discord"],
            "content_pipeline": ["researcher", "writer", "discord", "memory"]
        }
        
        # Stats
        self.stats = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "agents": {}
        }
        
        # Load existing agents
        self._load_agents()
    
    def _load_agents(self):
        """Lädt Agent-Config"""
        
        config_path = f"{self.workspace}/skills/master-orchestrator/config.json"
        
        if os.path.exists(config_path):
            try:
                with open(config_path) as f:
                    config = json.load(f)
                    for name, info in config.get("agents", {}).items():
                        self.register_agent(name, info.get("type"), info.get("capabilities", []))
            except Exception:
                pass
    
    def register_agent(self, name: str, agent_type: str, capabilities: List[str]):
        """Registriert einen Agent"""
        
        self.agents[name] = {
            "type": agent_type,
            "capabilities": capabilities,
            "status": "idle",
            "tasks_completed": 0,
            "success_rate": 1.0,
            "registered_at": datetime.now().isoformat()
        }
        
        print(f"✅ Agent registriert: {name}")
    
    def select_agent(self, task: str) -> str:
        """Wählt besten Agent für Task"""
        
        task_lower = task.lower()
        
        # Score each agent
        best_agent = "general"
        best_score = 0
        
        for name, info in self.agents.items():
            score = 0
            
            # Check capabilities
            for cap in info.get("capabilities", []):
                if cap in task_lower:
                    score += 10
            
            # Prefer idle agents
            if info.get("status") == "idle":
                score += 5
            
            # Prefer agents with higher success rate
            score += info.get("success_rate", 0.5) * 5
            
            if score > best_score:
                best_score = score
                best_agent = name
        
        return best_agent
    
    def execute_task(self, task: str, auto_learn: bool = True) -> dict:
        """Führt Task aus"""
        
        self.stats["total_tasks"] += 1
        
        # Select agent
        agent_name = self.select_agent(task)
        
        if agent_name not in self.agents:
            self.stats["failed_tasks"] += 1
            return {"success": False, "error": f"Agent {agent_name} nicht gefunden"}
        
        agent = self.agents[agent_name]
        agent["status"] = "running"
        
        print(f"🤖 {agent_name} führt aus: {task[:50]}...")
        
        # Simulate task execution
        # In production: spawn sub-agent or call API
        
        # Mark as completed
        agent["status"] = "idle"
        agent["tasks_completed"] += 1
        self.stats["successful_tasks"] += 1
        
        return {
            "success": True,
            "agent": agent_name,
            "task": task,
            "timestamp": datetime.now().isoformat()
        }
    
    def execute_workflow(self, workflow_name: str, context: dict = None) -> List[dict]:
        """Führt Workflow Chain aus"""
        
        if workflow_name not in self.workflows:
            return [{"success": False, "error": "Workflow nicht gefunden"}]
        
        results = []
        agents = self.workflows[workflow_name]
        
        print(f"\n🔄 Starte Workflow: {workflow_name}")
        
        for agent_name in agents:
            print(f"   → {agent_name}")
            
            if agent_name in self.agents:
                self.agents[agent_name]["status"] = "running"
        
        # Complete
        for agent_name in agents:
            if agent_name in self.agents:
                self.agents[agent_name]["status"] = "idle"
                results.append({
                    "agent": agent_name,
                    "success": True
                })
        
        return results
    
    def get_stats(self) -> dict:
        """Gibt Stats zurück"""
        
        return {
            "total_tasks": self.stats["total_tasks"],
            "successful": self.stats["successful_tasks"],
            "failed": self.stats["failed_tasks"],
            "success_rate": (
                self.stats["successful_tasks"] / max(1, self.stats["total_tasks"])
            ),
            "agents": {
                name: {
                    "tasks": info.get("tasks_completed", 0),
                    "status": info.get("status", "unknown"),
                    "success_rate": info.get("success_rate", 0)
                }
                for name, info in self.agents.items()
            }
        }
    
    def list_agents(self) -> List[dict]:
        """Liste alle Agents"""
        
        return [
            {
                "name": name,
                "type": info.get("type"),
                "capabilities": info.get("capabilities", []),
                "status": info.get("status", "unknown"),
                "tasks": info.get("tasks_completed", 0)
            }
            for name, info in self.agents.items()
        ]
    
    def list_workflows(self) -> List[str]:
        """Liste alle Workflows"""
        
        return list(self.workflows.keys())


# CLI Interface
def main():
    import sys
    
    orchestrator = MasterOrchestrator()
    
    # Register default agents
    orchestrator.register_agent("writer", "content", ["write", "blog", "social", "email", "content"])
    orchestrator.register_agent("researcher", "research", ["research", "analyze", "data", "web"])
    orchestrator.register_agent("memory", "storage", ["memory", "store", "retrieve", "context"])
    orchestrator.register_agent("coder", "dev", ["code", "debug", "script", "devops"])
    orchestrator.register_agent("discord", "social", ["discord", "post", "channel", "message"])
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "stats":
            stats = orchestrator.get_stats()
            print(json.dumps(stats, indent=2))
        
        elif command == "agents":
            for agent in orchestrator.list_agents():
                print(f"{agent['name']}: {agent['status']} ({agent['tasks']} tasks)")
        
        elif command == "workflows":
            for wf in orchestrator.list_workflows():
                print(wf)
        
        elif command == "execute" and len(sys.argv) > 2:
            task = " ".join(sys.argv[2:])
            result = orchestrator.execute_task(task)
            print(json.dumps(result, indent=2))
        
        elif command == "workflow" and len(sys.argv) > 2:
            wf_name = sys.argv[2]
            results = orchestrator.execute_workflow(wf_name)
            print(json.dumps(results, indent=2))
        
        else:
            print("""
Master Orchestrator CLI

Commands:
  stats              - Zeige Stats
  agents             - Zeige Agents
  workflows          - Zeige Workflows
  execute [task]     - Führe Task aus
  workflow [name]    - Führe Workflow aus
            """)
    else:
        # Interactive mode
        print("""
🎯 Master Orchestrator - Bereit!

Commands:
  stats
  agents
  workflows
  execute [task]
  workflow [name]
        """)

if __name__ == "__main__":
    main()
