#!/usr/bin/env python3
"""
Quick Agent Spawner - Für Faule 😄
Syntax: python3 spawn_agent.py <agent> [aufgabe]
"""

import sys
import os

# Agent Mapping
AGENTS = {
    # Schicht 2: Spezialisten
    "review": {
        "agent": "code-reviewer",
        "desc": "Code Review & Security"
    },
    "debug": {
        "agent": "debugger", 
        "desc": "Bug finden & fixen"
    },
    "arch": {
        "agent": "architect",
        "desc": "System-Design"
    },
    # Schicht 3: Domänen
    "research": {
        "agent": "research",
        "desc": "Web-Recherche"
    },
    "pod": {
        "agent": "pod",
        "desc": "POD Business"
    },
    "trading": {
        "agent": "trading",
        "desc": "Trading-Analyse"
    },
    "social": {
        "agent": "social",
        "desc": "Social Media"
    },
    # Bestehende
    "lib": {
        "agent": "librarian",
        "desc": "Wissens-Manager"
    },
    "verify": {
        "agent": "verification",
        "desc": "Risk Check"
    }
}

def spawn(agent_key: str, task: str = None):
    """Spawnt einen Agenten"""
    
    if agent_key not in AGENTS:
        print("❌ Unbekannter Agent!")
        print("\nVerfügbare Agenten:")
        for k, v in AGENTS.items():
            print(f"  {k:10} → {v['desc']}")
        return
    
    agent = AGENTS[agent_key]["agent"]
    desc = AGENTS[agent_key]["desc"]
    
    print(f"🚀 Spawne {desc}...")
    
    # OpenClaw Session Spawn
    os.system(f'openclaw sessions spawn --agent-id {agent} --task "{task or desc}" --mode session')
    
    print(f"✅ {desc} gestartet!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 spawn_agent.py <agent> [aufgabe]")
        print("\nVerfügbare Agenten:")
        for k, v in AGENTS.items():
            print(f"  {k:10} → {v['desc']}")
        sys.exit(1)
    
    agent = sys.argv[1]
    task = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
    
    spawn(agent, task)
