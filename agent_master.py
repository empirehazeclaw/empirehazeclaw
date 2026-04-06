#!/usr/bin/env python3
"""
🤖 MASTER AGENT CONTROLLER
Coordinates all agents
"""
import subprocess
from datetime import datetime

AGENTS = {
    "revenue": "scripts/agents/revenue_agent.py",
    "operations": "scripts/agents/operations_agent.py",
    "content": "scripts/agents/content_agent.py",
    "research": "scripts/agents/research_agent.py",
    "support": "scripts/agents/support_agent.py"
}

def run_agent(name):
    print(f"\n{'='*50}")
    print(f"🤖 RUNNING: {name.upper()} AGENT")
    print(f"{'='*50}")
    
    result = subprocess.run(
        ["python3", f"/home/clawbot/.openclaw/workspace/{AGENTS[name]}"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    return result.returncode == 0

def daily_routine():
    print(f"\n{'#'*50}")
    print(f"# 🤖 MASTER CONTROLLER - DAILY ROUTINE")
    print(f"# {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'#'*50}")
    
    results = {}
    
    # Run all agents
    for name in AGENTS:
        results[name] = run_agent(name)
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 SUMMARY")
    print(f"{'='*50}")
    for name, ok in results.items():
        print(f"  {'✅' if ok else '❌'} {name}")
    
    return results

if __name__ == "__main__":
    daily_routine()
