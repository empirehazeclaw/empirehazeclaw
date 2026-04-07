#!/usr/bin/env python3
"""Agent Automation Router"""
import re
import sys

# Routing rules
ROUTING = {
    "dev": ["code", "build", "fix", "script", "implement", "create"],
    "trading": ["trading", "stock", "crypto", "analyze", "trade", "market"],
    "researcher": ["research", "find", "search", "recherche", "suchen"],
    "social": ["post", "social", "twitter", "instagram", "content"],
    "debugger": ["debug", "error", "bug", "fehler", "problem"],
    "pod": ["podcast", "audio", "sprecher", "voice"],
}

def route_task(task_text):
    """Route task to appropriate agent"""
    task_lower = task_text.lower()
    
    for agent, keywords in ROUTING.items():
        for keyword in keywords:
            if keyword in task_lower:
                return agent
    
    return "dev"  # Default to dev

def main():
    if len(sys.argv) < 2:
        print("Usage: python router.py '<task description>'")
        sys.exit(1)
    
    task = " ".join(sys.argv[1:])
    agent = route_task(task)
    print(f"route:{agent}")

if __name__ == "__main__":
    main()
