#!/usr/bin/env python3
"""
Integrated Workflow Runner
Combines task analysis with actual agent spawning
"""
import json
import subprocess
from datetime import datetime

def analyze_and_spawn(user_request):
    """Analysiert Request und spawned Agents"""
    
    # Task keywords
    keywords = {
        "dev": ["code", "build", "create", "website", "fix", "script", "html", "css"],
        "researcher": ["research", "analyze", "seo", "search", "analyse"],
        "social": ["twitter", "post", "social", "content"],
        "trading": ["trading", "crypto", "signal"],
        "pod": ["etsy", "printify", "design"]
    }
    
    # Detect needed agents
    request_lower = user_request.lower()
    needed_agents = []
    
    for agent, kws in keywords.items():
        if any(kw in request_lower for kw in kws):
            if agent not in needed_agents:
                needed_agents.append(agent)
    
    if not needed_agents:
        needed_agents = ["dev"]  # Default
    
    print(f"🎯 Request: {user_request}")
    print(f"👥 Needed agents: {needed_agents}")
    
    # Spawn agents (simulated - would need actual API call)
    for agent in needed_agents:
        print(f"   → Spawning {agent}...")
    
    return {
        "request": user_request,
        "agents": needed_agents,
        "status": "ready to spawn"
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = analyze_and_spawn(" ".join(sys.argv[1:]))
        print(json.dumps(result, indent=2))
