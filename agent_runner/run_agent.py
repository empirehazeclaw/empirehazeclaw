#!/usr/bin/env python3
"""
Agent Runner v2 - Start autonomous agents AND sandbox sub-agents
Usage: python run_agent.py [agent_name] [task]
"""
import sys
import subprocess
import json
import os
from datetime import datetime

# Autonomous Python Agents
AUTONOMOUS_AGENTS = {
    "sales": {
        "script": "autonomous/agents/sales_agent.py",
        "description": "Find leads and send outreach emails"
    },
    "research": {
        "script": "autonomous/agents/research_agent.py", 
        "description": "Research topics, competitors, trends"
    },
    "content": {
        "script": "autonomous/agents/content_agent.py",
        "description": "Create blog posts, social content"
    },
    "outreach": {
        "script": "autonomous/agents/outreach_agent.py",
        "description": "B2B outreach and follow-ups"
    },
    "trading": {
        "script": "autonomous/agents/trading_agent.py",
        "description": "Analyze trading opportunities"
    },
    "validation": {
        "script": "autonomous/agents/validation_agent.py",
        "description": "Validate business ideas"
    },
    "librarian": {
        "script": "autonomous/agents/librarian_agent.py",
        "description": "Organize memory and knowledge"
    }
}

# Sandbox Sub-Agents (spawned via sessions_spawn)
SANDBOX_AGENTS = {
    "architect": {
        "sandbox": "agent-architect-66a9486b",
        "description": "System architecture and design"
    },
    "coder": {
        "sandbox": "agent-code-reviewer-6b000867",
        "description": "Code generation and review"
    },
    "debugger": {
        "sandbox": "agent-debugger-bf675e8f",
        "description": "Find and fix bugs"
    },
    "pod": {
        "sandbox": "agent-pod-f9703aad",
        "description": "Print on Demand management"
    },
    "social": {
        "sandbox": "agent-social-ef348f2d",
        "description": "Social media management"
    },
    "trading": {
        "sandbox": "agent-trading-27131508",
        "description": "Trading analysis"
    },
    "verification": {
        "sandbox": "agent-verification-6c31aff2",
        "description": "Verify and validate"
    }
}

def spawn_subagent(agent_name, task):
    """Spawn a sub-agent session using OpenClaw's sessions_spawn"""
    import requests
    
    # This would be called within the main agent to spawn sub-agents
    # For now, we document how to use it
    print(f"🔄 To spawn {agent_name} as sub-agent, use:")
    print(f"   sessions_spawn(runtime='subagent', task='{task}', label='{agent_name}')")
    return True

def run_autonomous(agent_name, task):
    """Run a Python-based autonomous agent"""
    script_path = f"/home/clawbot/.openclaw/workspace/scripts/{AUTONOMOUS_AGENTS[agent_name]['script']}"
    
    result = subprocess.run(
        ["python3", script_path] + (["--task", task] if task else []),
        capture_output=True,
        text=True,
        cwd="/home/clawbot/.openclaw/workspace"
    )
    
    print(result.stdout)
    if result.stderr:
        print(f"Errors: {result.stderr}")
    return result.returncode == 0

def list_agents():
    print("=== AUTONOME AGENTEN (Python Scripts) ===")
    for name, info in AUTONOMOUS_AGENTS.items():
        print(f"  {name:12} - {info['description']}")
    
    print("\n=== SANDBOX SUB-AGENTEN (OpenClaw Sessions) ===")
    for name, info in SANDBOX_AGENTS.items():
        print(f"  {name:12} - {info['description']}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_agent.py [agent_name] [optional_task]")
        print("\nExamples:")
        print("  python run_agent.py sales 'Finde 5 Leads'")
        print("  python run_agent.py coder 'Review this code'")
        print("  python run_agent.py list")
        list_agents()
        sys.exit(1)
    
    if sys.argv[1] == "list":
        list_agents()
        sys.exit(0)
    
    agent_name = sys.argv[1].lower()
    task = sys.argv[2] if len(sys.argv) > 2 else ""
    
    if agent_name in AUTONOMOUS_AGENTS:
        print(f"🚀 Starting autonomous agent: {agent_name}")
        run_autonomous(agent_name, task)
    elif agent_name in SANDBOX_AGENTS:
        print(f"🧠 Sandbox agent: {agent_name}")
        spawn_subagent(agent_name, task)
        print(f"✅ Use sessions_spawn() in main session to activate!")
    else:
        print(f"Unknown agent: {agent_name}")
        list_agents()
        sys.exit(1)
    
    print(f"✅ Agent {agent_name} done!")
