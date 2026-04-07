#!/usr/bin/env python3
"""Create new permanent agents"""
import json
import os
import sys
from datetime import datetime

AGENTS_DIR = "data/agents"
TEMPLATES = {
    "sales": {
        "name": "sales_agent",
        "description": "Sales and lead generation",
        "tasks": ["lead_generation", "outreach", "followup", "close_deals"],
        "schedule": "daily",
        "priority": 1
    },
    "marketing": {
        "name": "marketing_agent", 
        "description": "Content and social media",
        "tasks": ["blog_posts", "social_media", "seo", "ads"],
        "schedule": "daily",
        "priority": 2
    },
    "support": {
        "name": "support_agent",
        "description": "Customer support",
        "tasks": ["respond_queries", "tickets", "faq"],
        "schedule": "on_demand",
        "priority": 3
    },
    "development": {
        "name": "development_agent",
        "description": "Code and product development",
        "tasks": ["write_code", "test", "deploy", "fix_bugs"],
        "schedule": "on_demand",
        "priority": 2
    }
}

def load_registry():
    with open(f"{AGENTS_DIR}/agent_registry.json") as f:
        return json.load(f)

def save_registry(data):
    with open(f"{AGENTS_DIR}/agent_registry.json", "w") as f:
        json.dump(data, f, indent=2)

def create_agent(name, description, tasks):
    """Create a new permanent agent"""
    registry = load_registry()
    
    agent = {
        "id": f"agent_{datetime.now().timestamp()}",
        "name": name,
        "description": description,
        "tasks": tasks,
        "created_at": datetime.now().isoformat(),
        "status": "active",
        "runs": 0
    }
    
    registry["agents"].append(agent)
    save_registry(registry)
    
    # Also create the actual script
    script_path = f"scripts/agents/{name}.py"
    with open(script_path, "w") as f:
        f.write(f'''#!/usr/bin/env python3
"""
{name}: {description}
Tasks: {", ".join(tasks)}
Created: {datetime.now().isoformat()}
"""
import sys
import subprocess

def run():
    print(f"🤖 Running {name}")
    print(f"Tasks: {tasks}")
    # Add your agent logic here
    return "Done"

if __name__ == "__main__":
    run()
''')
    
    return f"✅ Created {name} at {script_path}"

def list_agents():
    registry = load_registry()
    print("=== 🤖 PERMANENT AGENTS ===")
    for a in registry["agents"]:
        print(f"  - {a['name']}: {a['description']} (runs: {a['runs']})")

def get_agent(name):
    registry = load_registry()
    for a in registry["agents"]:
        if a["name"] == name:
            return a
    return None

# CLI
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    
    if cmd == "list":
        list_agents()
    elif cmd == "create":
        name = sys.argv[2] if len(sys.argv) > 2 else "new_agent"
        desc = sys.argv[3] if len(sys.argv) > 3 else "Custom agent"
        tasks = sys.argv[4].split(",") if len(sys.argv) > 4 else ["task1"]
        print(create_agent(name, desc, tasks))
    elif cmd == "templates":
        print("=== 📋 TEMPLATES ===")
        for t, d in TEMPLATES.items():
            print(f"  {t}: {d['description']}")
    else:
        print(f"Usage: python3 create_agent.py [list|create|templates]")
