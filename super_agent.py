#!/usr/bin/env python3
"""
🎛️ SUPER AGENT - ECHTER OpenClaw Agent
=====================================
Koordiniert RESEARCHER, POD, SOCIAL, TRADING Agenten!
"""

import requests
import json

GATEWAY = "http://127.0.0.1:18789"

# Verfügbare echte Agents
REAL_AGENTS = {
    "researcher": "Research Agent - Findet Trends",
    "pod": "POD Agent - Print on Demand",
    "social": "Social Agent - Social Media",
    "trading": "Trading Agent - Markets",
    "debugger": "Debugger Agent - Fixes Bugs",
}

def spawn_agent(agent_id, task):
    """Spawn echten OpenClaw Agent"""
    try:
        response = requests.post(
            f"{GATEWAY}/api/sessions",
            json={
                "runtime": "subagent",
                "agentId": agent_id,
                "task": task,
                "mode": "run"
            },
            timeout=120
        )
        
        if response.status_code in [200, 201]:
            return {"status": "spawned", "agent": agent_id}
        else:
            return {"status": "error", "code": response.status_code}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def run_workflow(workflow_name, tasks):
    """Run einen kompletten Workflow"""
    print(f"\n🎛️ SUPER AGENT - {workflow_name}")
    print("=" * 50)
    
    results = []
    
    for agent_id, task in tasks.items():
        print(f"\n→ Spawning {agent_id}...")
        result = spawn_agent(agent_id, task)
        print(f"   {result['status']}")
        results.append((agent_id, result['status']))
    
    print("\n" + "=" * 50)
    print("📊 WORKFLOW SUMMARY:")
    for agent, status in results:
        emoji = "✅" if status == "spawned" else "❌"
        print(f"{emoji} {agent}")
    
    return results

# Workflows
MORNING_WORKFLOW = {
    "researcher": "Finde 3 neue Business Opportunities. Focus: KI, Software, Automation.",
    "social": "Erstelle einen Tweet über unsere Produkte.",
    "trading": "Analysiere aktuelle Market Trends.",
}

EVENING_WORKFLOW = {
    "pod": "Finde neue POD Design Trends.",
    "social": "Poste einen zweiten Tweet.",
}

if __name__ == "__main__":
    import sys
    
    workflow = sys.argv[1] if len(sys.argv) > 1 else "morning"
    
    if workflow == "morning":
        run_workflow("MORNING", MORNING_WORKFLOW)
    elif workflow == "evening":
        run_workflow("EVENING", EVENING_WORKFLOW)
    else:
        print("Usage: python3 super_agent.py [morning|evening]")
