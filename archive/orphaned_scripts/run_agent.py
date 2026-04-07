#!/usr/bin/env python3
"""🤖 Unified Agent Runner"""
import subprocess
import sys
import json
from datetime import datetime

AGENTS = {
    "revenue": "python3 scripts/agents/revenue_agent.py",
    "content": "python3 scripts/agents/content_agent.py",
    "research": "python3 scripts/agents/research_agent.py",
    "operations": "python3 scripts/agents/operations_agent.py"
}

def run_agent(name):
    if name not in AGENTS:
        return f"❌ Unknown agent: {name}\nAvailable: {list(AGENTS.keys())}"
    
    print(f"🤖 Starting {name}...")
    result = subprocess.run(AGENTS[name].split(), capture_output=True, text=True, timeout=300)
    return result.stdout[:500] if result.returncode == 0 else f"❌ {result.stderr[:200]}"

def list_agents():
    return "\n".join([f"  - {a}" for a in AGENTS.keys()])

if __name__ == "__main__":
    agent = sys.argv[1] if len(sys.argv) > 1 else ""
    if not agent:
        print("=== 🤖 AVAILABLE AGENTS ===")
        print(list_agents())
    else:
        print(run_agent(agent))
