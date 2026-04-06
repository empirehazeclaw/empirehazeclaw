#!/usr/bin/env python3
"""
🎛️ SPAWN AGENTS - Trigger Super Agent Workflow
==============================================
This triggers the current agent (main) to spawn other agents
"""

import subprocess
import json

# The current session key
SESSION_KEY = "agent:main:telegram:direct:5392630979"

# Tasks for each agent
TASKS = {
    "researcher": "Recherche: Finde 3 neue Business Opportunities für EmpireHazeClaw. Focus auf: KI Tools, Software, Automation.",
    "social": "Social Media: Erstelle einen Tweet über unsere Produkte auf empirehazeclaw.store",
    "pod": "POD Research: Finde neue Design Trends für Print on Demand.",
}

def spawn_via_gateway(agent_id, task):
    """Use gateway API to spawn agent"""
    cmd = [
        "curl", "-s", "-X", "POST",
        "http://127.0.0.1:18789/api/sessions",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({
            "runtime": "subagent",
            "agentId": agent_id,
            "task": task,
            "mode": "run"
        })
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

def run_workflow(workflow_name):
    print(f"🎛️ SPAWN WORKFLOW: {workflow_name}")
    print("=" * 50)
    
    if workflow_name == "morning":
        for agent_id, task in TASKS.items():
            print(f"\n→ Spawning {agent_id}...")
            success = spawn_via_gateway(agent_id, task)
            print(f"   {'✅' if success else '❌'}")
    
    print("\n✅ Workflow triggered!")

if __name__ == "__main__":
    import sys
    workflow = sys.argv[1] if len(sys.argv) > 1 else "morning"
    run_workflow(workflow)
