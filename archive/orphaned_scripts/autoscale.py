#!/usr/bin/env python3
"""
⚡ Auto-Scaling Controller
==========================
Automatically scale agents based on load
"""

import json
import subprocess
import time
from datetime import datetime

# Load config
CONFIG_FILE = '/home/clawbot/.openclaw/workspace/config/autoscale.json'

DEFAULT_CONFIG = {
    'enabled': True,
    'min_agents': 1,
    'max_agents': 5,
    'scale_up_threshold': 10,  # Queue size
    'scale_down_threshold': 2,
    'check_interval': 60  # seconds
}

def load_config():
    import os
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return DEFAULT_CONFIG

def save_config(config):
    import os
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_queue_size():
    """Get current task queue size"""
    try:
        result = subprocess.run(
            ['curl', '-s', 'http://127.0.0.1:18789/api/queue'],
            capture_output=True, text=True, timeout=5
        )
        data = json.loads(result.stdout)
        return data.get('pending', 0)
    except:
        return 0

def get_active_agents():
    """Get number of active agents"""
    result = subprocess.run(
        ['pgrep', '-af', 'sessions_spawn'],
        capture_output=True, text=True
    )
    return len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0

def scale_up():
    """Scale up agents"""
    print(f"🚀 Scaling UP agents...")
    # Implementation depends on your agent spawning mechanism
    return True

def scale_down():
    """Scale down agents"""
    print(f"📉 Scaling DOWN agents...")
    return True

def check_and_scale():
    """Check load and scale accordingly"""
    config = load_config()
    
    if not config.get('enabled', True):
        return {'status': 'disabled'}
    
    queue_size = get_queue_size()
    active_agents = get_active_agents()
    
    action = None
    
    # Scale up
    if queue_size >= config['scale_up_threshold'] and active_agents < config['max_agents']:
        scale_up()
        action = 'scaled_up'
    
    # Scale down
    elif queue_size <= config['scale_down_threshold'] and active_agents > config['min_agents']:
        scale_down()
        action = 'scaled_down'
    
    return {
        'timestamp': datetime.now().isoformat(),
        'queue_size': queue_size,
        'active_agents': active_agents,
        'action': action,
        'config': config
    }

if __name__ == '__main__':
    result = check_and_scale()
    print(json.dumps(result, indent=2))
