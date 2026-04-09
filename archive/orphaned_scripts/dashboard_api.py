#!/usr/bin/env python3
"""
Enhanced Dashboard API - Real-time Agent Status
"""

import json
import subprocess
import os
from datetime import datetime

def get_system_stats():
    """Get system stats"""
    stats = {
        "timestamp": datetime.now().isoformat(),
        "agents": {},
        "services": {},
        "cron": {}
    }
    
    # Get cron jobs
    try:
        result = subprocess.run(
            ['cat', '/home/clawbot/.openclaw/cron/jobs.json'],
            capture_output=True, text=True, timeout=5
        )
        cron_data = json.loads(result.stdout)
        
        enabled = 0
        total = 0
        errors = 0
        
        for job in cron_data.get('jobs', []):
            total += 1
            if job.get('enabled', False):
                enabled += 1
            if job.get('state', {}).get('lastRunStatus') == 'error':
                errors += 1
        
        stats['cron'] = {
            'total': total,
            'enabled': enabled,
            'errors': errors
        }
    except:
        pass
    
    # Get agent registry
    try:
        result = subprocess.run(
            ['cat', '/home/clawbot/.openclaw/workspace/config/registered_agents.json'],
            capture_output=True, text=True, timeout=5
        )
        agents_data = json.loads(result.stdout)
        stats['agents']['registered'] = len(agents_data.get('agents', []))
    except:
        pass
    
    # Get services status
    services = {
        'gateway': check_process('openclaw-gateway'),
        'event_listener': check_process('event_listener'),
        'ws_gateway': check_process('ws_agent_gateway'),
        'dashboard': check_process('dashboard_server')
    }
    stats['services'] = services
    
    return stats

def check_process(name):
    """Check if process is running"""
    result = subprocess.run(
        ['pgrep', '-af', name],
        capture_output=True, text=True
    )
    count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
    return {'running': count > 0, 'count': count}

if __name__ == '__main__':
    print(json.dumps(get_system_stats(), indent=2))
