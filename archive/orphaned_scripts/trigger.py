#!/usr/bin/env python3
"""Trigger System - Connect Agents"""
import subprocess
import sys

TRIGGERS = {
    "lead_outreach": ["revenue", "research", "mail"],
    "blog_post": ["research", "content"],
    "social_post": ["content"],
    "morning_routine": ["operations", "revenue"],
    "followup": ["mail", "revenue"]
}

def run_trigger(name):
    if name not in TRIGGERS:
        return f"❌ Unknown: {name}\nAvailable: {list(TRIGGERS.keys())}"
    
    agents = TRIGGERS[name]
    print(f"🎯 Trigger: {name}")
    print(f"Running: {agents}")
    
    results = []
    for agent in agents:
        print(f"\n🤖 Running {agent}...")
        result = subprocess.run(
            ["python3", f"scripts/run_agent.py", agent],
            capture_output=True, text=True, timeout=120
        )
        results.append((agent, result.returncode))
    
    success = sum(1 for _, code in results if code == 0)
    return f"✅ {success}/{len(agents)} agents succeeded"

def list_triggers():
    print("=== 🔗 AVAILABLE TRIGGERS ===")
    for name, agents in TRIGGERS.items():
        print(f"  {name}: {' → '.join(agents)}")

if __name__ == "__main__":
    trigger = sys.argv[1] if len(sys.argv) > 1 else ""
    if not trigger:
        list_triggers()
    else:
        print(run_trigger(trigger))
