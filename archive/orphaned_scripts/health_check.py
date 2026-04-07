#!/usr/bin/env python3
"""Agent Health Check"""
import subprocess
import json
from datetime import datetime

def check_agents():
    print("=== 🤖 AGENT HEALTH ===")
    print(f"Time: {datetime.now()}")
    print("")
    
    # Check if agents exist
    agent_dir = "scripts/agents"
    if not os.path.exists(agent_dir):
        return "❌ No agents directory"
    
    agents = [f.replace(".py", "") for f in os.listdir(agent_dir) if f.endswith(".py")]
    
    for agent in agents:
        print(f"  {'✅' if agent else '❌'} {agent}")
    
    return f"Found {len(agents)} agents"

import os
if __name__ == "__main__":
    print(check_agents())
