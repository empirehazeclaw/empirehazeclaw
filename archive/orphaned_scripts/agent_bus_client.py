#!/usr/bin/env python3
"""
🤝 AGENT BUS CLIENT
==================
Connect agents via the internal mesh!
"""

import sys
sys.path.insert(0, '/home/clawbot/.openclaw/workspace')

from core.agent_bus import AgentBus

bus = AgentBus()

def list_agents():
    """List all registered agents"""
    return bus.list_agents()

def send_to_agent(agent_name, message):
    """Send message to specific agent"""
    return bus.send(agent_name, message)

def broadcast(message):
    """Broadcast to all agents"""
    agents = list_agents()
    results = []
    for agent in agents:
        result = send_to_agent(agent, message)
        results.append((agent, result))
    return results

# Example usage
if __name__ == "__main__":
    print("🤝 Agent Bus Client")
    print("=" * 30)
    print(f"Agents: {list_agents()}")
