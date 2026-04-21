#!/usr/bin/env python3
"""
Unified Task Logger
===================
Erfasst ALLE Aufgaben zentral:
- Sub-Agent Tasks (Orchestrator)
- Main Agent Tasks (Nachrichten, Decisions)
- Cron Tasks
- Script Tasks

Usage:
    python3 unified_task_logger.py --log <type> <success> <details>
    python3 unified_task_logger.py --stats
    python3 unified_task_logger.py --report
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

WORKSPACE = '/home/clawbot/.openclaw/workspace/ceo'
LOG_DIR = f"{WORKSPACE}/memory/task_log"
LOG_FILE = f"{LOG_DIR}/unified_tasks.json"
STATS_FILE = f"{LOG_DIR}/task_stats.json"

TASK_TYPES = [
    'message_response',
    'decision',
    'subagent_task', 
    'cron_task',
    'script_execution',
    'learning_integration',
    'health_check',
    'research',
    'file_operation',
    'external_action'
]

OUTCOMES = ['success', 'failure', 'partial', 'skipped']


class UnifiedTaskLogger:
    def __init__(self):
        os.makedirs(LOG_DIR, exist_ok=True)
        self.tasks = self.load_tasks()
        self.stats = self.load_stats()
    
    def load_tasks(self):
        """Load tasks from log file."""
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                return json.load(f)
        return {'tasks': [], 'last_task_id': 0}
    
    def save_tasks(self):
        """Save tasks to log file."""
        with open(LOG_FILE, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def load_stats(self):
        """Load cached statistics."""
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
        return self.init_stats()
    
    def init_stats(self):
        """Initialize stats structure."""
        stats = {
            'by_type': {t: {'success': 0, 'failure': 0, 'partial': 0, 'skipped': 0, 'total': 0} for t in TASK_TYPES},
            'by_day': {},
            'success_rate_by_type': {},
            'last_updated': datetime.now().isoformat(),
            'total_tasks': 0,
            'total_successes': 0,
            'total_failures': 0
        }
        return stats
    
    def save_stats(self):
        """Save stats to file."""
        self.stats['last_updated'] = datetime.now().isoformat()
        with open(STATS_FILE, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def log_task(self, task_type, outcome, details=None, metadata=None):
        """Log a single task."""
        task_id = self.tasks['last_task_id'] + 1
        task = {
            'task_id': task_id,
            'timestamp': datetime.now().isoformat(),
            'type': task_type,
            'outcome': outcome,
            'details': details or '',
            'metadata': metadata or {}
        }
        
        self.tasks['tasks'].append(task)
        self.tasks['last_task_id'] = task_id
        
        # Update stats
        self.update_stats(task)
        
        self.save_tasks()
        self.save_stats()
        
        return task_id
    
    def update_stats(self, task):
        """Update statistics with new task."""
        t_type = task['type']
        outcome = task['outcome']
        
        # By type
        if t_type in self.stats['by_type']:
            if outcome in self.stats['by_type'][t_type]:
                self.stats['by_type'][t_type][outcome] += 1
                self.stats['by_type'][t_type]['total'] += 1
        
        # By day
        day = task['timestamp'][:10]  # YYYY-MM-DD
        if day not in self.stats['by_day']:
            self.stats['by_day'][day] = {'success': 0, 'failure': 0, 'total': 0}
        if outcome in self.stats['by_day'][day]:
            self.stats['by_day'][day][outcome] += 1
            self.stats['by_day'][day]['total'] += 1
        
        # Totals
        self.stats['total_tasks'] += 1
        if outcome == 'success':
            self.stats['total_successes'] += 1
        elif outcome == 'failure':
            self.stats['total_failures'] += 1
        
        # Success rate by type
        for t in TASK_TYPES:
            t_stats = self.stats['by_type'][t]
            if t_stats['total'] > 0:
                rate = (t_stats['success'] + 0.5 * t_stats['partial']) / t_stats['total']
                self.stats['success_rate_by_type'][t] = round(rate, 3)
    
    def get_stats(self):
        """Get current statistics."""
        return self.stats
    
    def get_recent_tasks(self, limit=50):
        """Get recent tasks."""
        return self.tasks['tasks'][-limit:]
    
    def generate_report(self):
        """Generate comprehensive report."""
        stats = self.stats
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_tasks': stats['total_tasks'],
                'total_successes': stats['total_successes'],
                'total_failures': stats['total_failures'],
                'overall_success_rate': round(stats['total_successes'] / max(stats['total_tasks'], 1), 3)
            },
            'by_type': {},
            'recent_trends': self.get_recent_trends(),
            'recommendations': self.get_recommendations()
        }
        
        for t_type in TASK_TYPES:
            t_stats = stats['by_type'][t_type]
            if t_stats['total'] > 0:
                success_rate = round(t_stats['success'] / t_stats['total'], 3) if t_stats['total'] > 0 else 0
                report['by_type'][t_type] = {
                    'total': t_stats['total'],
                    'success': t_stats['success'],
                    'failure': t_stats['failure'],
                    'success_rate': success_rate
                }
        
        return report
    
    def get_recent_trends(self):
        """Analyze recent trends."""
        if len(self.tasks['tasks']) < 5:
            return 'Insufficient data for trends'
        
        recent = self.tasks['tasks'][-20:]
        success_count = sum(1 for t in recent if t['outcome'] == 'success')
        trend = round(success_count / len(recent), 3)
        
        return {
            'last_20_tasks_success_rate': trend,
            'direction': 'improving' if trend > 0.8 else ('declining' if trend < 0.6 else 'stable')
        }
    
    def get_recommendations(self):
        """Generate recommendations based on stats."""
        recs = []
        
        for t_type in TASK_TYPES:
            t_stats = self.stats['by_type'][t_type]
            if t_stats['total'] >= 5:
                rate = t_stats['success'] / t_stats['total']
                if rate < 0.7:
                    recs.append({
                        'priority': 'HIGH',
                        'area': t_type,
                        'issue': f"Success rate only {rate*100:.1f}%",
                        'recommendation': f"Focus on improving {t_type} tasks"
                    })
        
        return recs


# ========== CLI ==========

if __name__ == '__main__':
    logger = UnifiedTaskLogger()
    
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == '--log' and len(sys.argv) >= 4:
        # python3 unified_task_logger.py --log <type> <outcome> [details]
        task_type = sys.argv[2]
        outcome = sys.argv[3]
        details = sys.argv[4] if len(sys.argv) > 4 else ''
        
        if task_type not in TASK_TYPES:
            print(f"Unknown task type: {task_type}")
            print(f"Valid types: {TASK_TYPES}")
            sys.exit(1)
        
        if outcome not in OUTCOMES:
            print(f"Unknown outcome: {outcome}")
            print(f"Valid outcomes: {OUTCOMES}")
            sys.exit(1)
        
        task_id = logger.log_task(task_type, outcome, details)
        print(f"✅ Task logged: #{task_id} ({task_type} = {outcome})")
    
    elif action == '--stats':
        stats = logger.get_stats()
        print("\n📊 UNIFIED TASK STATS")
        print("=" * 50)
        print(f"Total Tasks: {stats['total_tasks']}")
        print(f"Success Rate: {stats['total_successes']/max(stats['total_tasks'],1)*100:.1f}%")
        print("\nBy Type:")
        for t_type in TASK_TYPES:
            t_stats = stats['by_type'][t_type]
            if t_stats['total'] > 0:
                rate = t_stats['success'] / t_stats['total'] * 100
                print(f"  {t_type}: {t_stats['total']} ({rate:.1f}% success)")
    
    elif action == '--report':
        report = logger.generate_report()
        print("\n📋 UNIFIED TASK REPORT")
        print("=" * 50)
        print(f"Generated: {report['generated_at']}")
        print(f"\nTotal Tasks: {report['summary']['total_tasks']}")
        print(f"Overall Success Rate: {report['summary']['overall_success_rate']*100:.1f}%")
        print("\nBy Type:")
        for t_type, data in report['by_type'].items():
            print(f"  {t_type}: {data['total']} tasks, {data['success_rate']*100:.1f}% success")
        if report['recommendations']:
            print("\n⚠️ Recommendations:")
            for rec in report['recommendations']:
                print(f"  [{rec['priority']}] {rec['area']}: {rec['issue']}")
    
    elif action == '--recent':
        recent = logger.get_recent_tasks(limit=20)
        print("\n📝 RECENT TASKS")
        print("=" * 50)
        for task in recent:
            print(f"  #{task['task_id']} | {task['timestamp'][11:19]} | {task['type']} = {task['outcome']}")
    
    else:
        print(__doc__)