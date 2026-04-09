"""
🏭 AGENT FACTORY
================
Create agents from YAML configs
"""

import sys
import yaml
sys.path.insert(0, '/home/clawbot/.openclaw/workspace')

from core.agent_factory import AgentFactory

factory = AgentFactory()

def create_agent_from_yaml(yaml_file):
    """Create agent from YAML config"""
    return factory.create_from_config(yaml_file)

def list_agent_configs():
    """List available agent configs"""
    import os
    configs = []
    for f in os.listdir("config/agents"):
        if f.endswith(".yaml"):
            configs.append(f.replace(".yaml", ""))
    return configs

if __name__ == "__main__":
    print("🏭 Agent Factory")
    print("=" * 30)
    print(f"Available: {list_agent_configs()}")
