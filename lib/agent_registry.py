"""
🤝 AGENT REGISTRY
================
Persistent agent registration for the bus
"""

import json

REGISTRY_FILE = "/home/clawbot/.openclaw/workspace/config/registered_agents.json"

def get_agents():
    """Get all registered agents"""
    try:
        with open(REGISTRY_FILE) as f:
            data = json.load(f)
        return data.get("agents", [])
    except:
        return []

def add_agent(name, capability):
    """Add agent to registry"""
    agents = get_agents()
    
    # Check if exists
    for a in agents:
        if a["name"] == name:
            return a
    
    # Add new
    agents.append({
        "name": name,
        "capability": capability,
        "registered": "2026-03-21"
    })
    
    with open(REGISTRY_FILE, "w") as f:
        json.dump({"agents": agents}, f, indent=2)
    
    return agents

# Add our agents
for name, cap in [
    ("researcher", "research"),
    ("content", "content"),
    ("sales", "sales"),
    ("outreach", "outreach"),
    ("validation", "validation"),
]:
    add_agent(name, cap)

print("🤝 Registered Agents:")
for a in get_agents():
    print(f"  - {a['name']}: {a['capability']}")
