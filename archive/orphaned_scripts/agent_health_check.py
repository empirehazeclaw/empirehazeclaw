#!/usr/bin/env python3
"""
Agent Health Check - Simple Version
Prüft ob alle Agent-Verzeichnisse existieren und valide sind.
"""
import os
import json

AGENTS_DIR = "/home/clawbot/.openclaw/agents"

AGENTS = [
    "librarian",
    "research", 
    "pod",
    "trading",
    "social",
    "debugger",
    "architect",
    "code-reviewer",
    "verification",
    "main"
]

def check_agent(agent_name: str) -> dict:
    """Prüfe einen Agent."""
    agent_path = os.path.join(AGENTS_DIR, agent_name)
    system_md = os.path.join(agent_path, "agent", "system.md")
    
    exists = os.path.exists(agent_path)
    has_system = os.path.exists(system_md)
    
    if exists and has_system:
        # Check system.md validity
        try:
            with open(system_md) as f:
                content = f.read()
                if len(content) > 100:
                    return {"name": agent_name, "status": "✅", "details": "OK"}
                else:
                    return {"name": agent_name, "status": "⚠️", "details": "system.md too short"}
        except Exception as e:
            return {"name": agent_name, "status": "❌", "details": str(e)}
    elif not exists:
        return {"name": agent_name, "status": "❌", "details": "Not found"}
    else:
        return {"name": agent_name, "status": "⚠️", "details": "No system.md"}

def main():
    print("🧪 Agent Health Check")
    print("=" * 50)
    
    results = []
    for agent in AGENTS:
        result = check_agent(agent)
        results.append(result)
        print(f"{result['name']:20} {result['status']}  ({result['details']})")
    
    print("\n" + "=" * 50)
    print("## Agent Health Report")
    print("| Agent | Status |")
    print("|-------|--------|")
    
    ok_count = sum(1 for r in results if r["status"] == "✅")
    for r in results:
        print(f"| {r['name']} | {r['status']} |")
    
    print(f"\n**Total:** {ok_count}/{len(AGENTS)} ✅")
    
    return 0 if ok_count == len(AGENTS) else 1

if __name__ == "__main__":
    exit(main())
