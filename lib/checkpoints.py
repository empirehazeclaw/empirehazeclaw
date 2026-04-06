"""
💾 CHECKPOINT MANAGER
====================
Save and resume agent states
"""

import sys
sys.path.insert(0, '.')

from core.checkpoint_manager import CheckpointManager

manager = CheckpointManager()

def save_checkpoint(agent_name, state):
    """Save agent state"""
    return manager.save_state(agent_name, state)

def load_checkpoint(agent_name):
    """Load agent state"""
    return manager.load_state(agent_name)

def list_checkpoints():
    """List all checkpoints"""
    return manager.list_checkpoints()

if __name__ == "__main__":
    # Test
    save_checkpoint("researcher", {"task": "researching AI trends"})
    state = load_checkpoint("researcher")
    print(f"💾 Checkpoint: {state}")
    print(f"📋 List: {list_checkpoints()}")
