#!/usr/bin/env python3
"""
Auto-Workflow Integration for OpenClaw Main Session
Automatically spawns agents based on request analysis
"""
import subprocess
import json
import re

# Agent keyword mappings
AGENT_KEYWORDS = {
    "dev": ["code", "build", "create", "website", "fix", "script", "html", "css", "web", "seite", "entwickle", "program", "blog", "artikel", "content"],
    "researcher": ["research", "analyze", "seo", "search", "analyse", "suche", "recherche"],
    "social": ["twitter", "post", "social", "content", "facebook"],
    "trading": ["trading", "crypto", "signal", "binance"],
    "pod": ["etsy", "printify", "design", "pod"]
}

def detect_agents(request):
    """Detects which agents are needed based on keywords"""
    request_lower = request.lower()
    detected = []
    
    for agent, keywords in AGENT_KEYWORDS.items():
        if any(kw in request_lower for kw in keywords):
            if agent not in detected:
                detected.append(agent)
    
    return detected if detected else ["dev"]

def spawn_agent(agent_id, task):
    """Spawns a sub-agent (simulated - returns the spawn command)"""
    return f"spawning {agent_id} for: {task[:50]}..."

def auto_route(request):
    """
    Main routing function - returns what to do
    Call this for any user request
    """
    agents = detect_agents(request)
    
    result = {
        "request": request,
        "agents_detected": agents,
        "needs_workflow": len(agents) > 1,
        "action": "workflow" if len(agents) > 1 else "spawn",
        "spawn_command": f"node scripts/workflow-spawn.js \"{request}\"" if len(agents) > 1 else f"sessions_spawn agentId={agents[0]}"
    }
    
    return result

# CLI for testing
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        request = " ".join(sys.argv[1:])
        result = auto_route(request)
        print(json.dumps(result, indent=2))
