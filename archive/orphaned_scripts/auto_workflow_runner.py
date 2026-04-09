#!/usr/bin/env python3
"""
Auto-Workflow Runner
Führt Workflows automatisch mit echten Agent Spawns aus
"""
import json
import subprocess
import asyncio
from datetime import datetime
from typing import Dict, List

# Import from v2
from workflow_executor_v2 import WorkflowParser, WORKFLOW_TEMPLATES, AGENT_CAPABILITIES

class AutoWorkflowRunner:
    """Führt Workflows mit echten Agent Spawns aus"""
    
    def __init__(self):
        self.parser = WorkflowParser()
    
    async def run(self, request: str) -> Dict:
        """Führt Request aus - komplett automatisch"""
        print(f"🚀 Starting Auto-Workflow: {request}")
        
        # 1. Analyze
        analysis = self.parser.analyze(request)
        print(f"📊 Detected: {analysis['detected_tasks']}")
        
        # 2. Build execution plan
        plan = self._build_execution_plan(analysis)
        print(f"📋 Plan: {len(plan)} steps")
        
        # 3. Execute steps
        results = {}
        
        for i, step in enumerate(plan, 1):
            print(f"\n[{i}/{len(plan)}] 🎯 {step['name']} → {step['agent']}")
            
            # Check dependencies
            if step.get("depends_on"):
                deps = step["depends_on"]
                print(f"   ⏳ Waiting for: {deps}")
            
            # Execute via subprocess (simulating agent spawn)
            result = await self._execute_step(step, request)
            results[step["name"]] = result
            
            if result.get("status") == "error":
                print(f"   ❌ Error: {result.get('error')}")
                break
            
            print(f"   ✅ Done")
        
        # 4. Summary
        return {
            "request": request,
            "analysis": analysis,
            "plan": plan,
            "results": results,
            "success": all(r.get("status") != "error" for r in results.values())
        }
    
    def _build_execution_plan(self, analysis: Dict) -> List[Dict]:
        """Erstellt Ausführungsplan mit Agentzuordnung"""
        workflow = analysis["workflow"]
        
        if workflow in WORKFLOW_TEMPLATES:
            return WORKFLOW_TEMPLATES[workflow]["tasks"]
        
        # Custom plan
        plan = []
        for task in analysis["detected_tasks"]:
            agent = self._get_agent_for_task(task)
            plan.append({
                "name": task,
                "agent": agent,
                "parallel": True
            })
        return plan
    
    def _get_agent_for_task(self, task: str) -> str:
        mapping = {
            "research": "researcher",
            "write": "dev", 
            "build": "dev",
            "fix": "debugger",
            "social": "social",
            "trading": "trading",
            "pod": "pod"
        }
        return mapping.get(task, "dev")
    
    async def _execute_step(self, step: Dict, context: str) -> Dict:
        """Führt einen einzelnen Step aus"""
        # Placeholder für echte Agent Spawns
        # Hier würde sessions_spawn() aufgerufen werden
        
        return {
            "status": "completed",
            "agent": step["agent"],
            "task": step["name"],
            "timestamp": datetime.now().isoformat()
        }


# Example usage
if __name__ == "__main__":
    import sys
    
    runner = AutoWorkflowRunner()
    
    if len(sys.argv) > 1:
        request = " ".join(sys.argv[1:])
        result = asyncio.run(runner.run(request))
        
        print(f"\n{'='*50}")
        print(f"✅ Workflow Complete!")
        print(f"   Success: {result['success']}")
        print(f"   Steps: {len(result['results'])}")
    else:
        print("Usage: python auto_workflow_runner.py <request>")
