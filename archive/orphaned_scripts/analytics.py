#!/usr/bin/env python3
"""
📊 Analytics & Tracking System
=============================
Track agent usage, costs, and performance
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = '/home/clawbot/.openclaw/workspace/data/analytics/'
METRICS_FILE = DATA_DIR + 'metrics.json'

def ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def load_metrics():
    """Load existing metrics"""
    ensure_dir()
    if os.path.exists(METRICS_FILE):
        with open(METRICS_FILE, 'r') as f:
            return json.load(f)
    return {
        'agents': {},
        'daily': {},
        'costs': {},
        'cron_stats': {}
    }

def save_metrics(metrics):
    """Save metrics"""
    with open(METRICS_FILE, 'w') as f:
        json.dump(metrics, f, indent=2)

def track_cron_run(job_name, duration_ms, status):
    """Track cron job execution"""
    metrics = load_metrics()
    today = datetime.now().strftime('%Y-%m-%d')
    
    if 'cron' not in metrics:
        metrics['cron'] = {}
    
    if job_name not in metrics['cron']:
        metrics['cron'][job_name] = {'runs': 0, 'success': 0, 'errors': 0, 'total_time': 0}
    
    stats = metrics['cron'][job_name]
    stats['runs'] += 1
    stats['total_time'] += duration_ms / 1000
    if status == 'ok':
        stats['success'] += 1
    else:
        stats['errors'] += 1
    
    # Daily aggregation
    if today not in metrics.get('daily', {}):
        metrics.setdefault('daily', {})[today] = {'runs': 0, 'errors': 0}
    
    metrics['daily'][today]['runs'] += 1
    if status != 'ok':
        metrics['daily'][today]['errors'] += 1
    
    save_metrics(metrics)
    return stats

def get_agent_usage():
    """Get current agent usage stats"""
    metrics = load_metrics()
    
    # Calculate success rate
    total_runs = sum(s.get('runs', 0) for s in metrics.get('cron', {}).values())
    total_errors = sum(s.get('errors', 0) for s in metrics.get('cron', {}).values())
    success_rate = ((total_runs - total_errors) / total_runs * 100) if total_runs > 0 else 0
    
    return {
        'total_runs': total_runs,
        'total_errors': total_errors,
        'success_rate': round(success_rate, 1),
        'agents': metrics.get('cron', {}),
        'daily': metrics.get('daily', {})
    }

def get_daily_stats():
    """Get stats for today"""
    metrics = load_metrics()
    today = datetime.now().strftime('%Y-%m-%d')
    return metrics.get('daily', {}).get(today, {'runs': 0, 'errors': 0})

def generate_report():
    """Generate analytics report"""
    usage = get_agent_usage()
    daily = get_daily_stats()
    
    report = {
        'generated': datetime.now().isoformat(),
        'today': daily,
        'all_time': {
            'total_runs': usage['total_runs'],
            'total_errors': usage['total_errors'],
            'success_rate': usage['success_rate']
        },
        'top_agents': sorted(
            [(k, v['runs']) for k, v in usage['agents'].items()],
            key=lambda x: x[1], reverse=True
        )[:5]
    }
    
    return report

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == 'report':
            print(json.dumps(generate_report(), indent=2))
        elif cmd == 'track':
            job = sys.argv[2]
            duration = int(sys.argv[3]) if len(sys.argv) > 3 else 0
            status = sys.argv[4] if len(sys.argv) > 4 else 'ok'
            print(json.dumps(track_cron_run(job, duration, status), indent=2))
        elif cmd == 'usage':
            print(json.dumps(get_agent_usage(), indent=2))
    else:
        print(json.dumps(generate_report(), indent=2))
