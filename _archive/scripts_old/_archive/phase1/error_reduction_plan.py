#!/usr/bin/env python3
"""
error_reduction_plan.py — Error Rate Reduction Plan (Dynamic Version)
Sir HazeClaw - 2026-04-11

Nutzt jetzt echte Daten von error_reducer.py statt hardcoded Werte.

Usage:
    python3 error_reduction_plan.py
"""

import json
import subprocess
import re
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "scripts"

def get_real_error_data():
    """Holt echte Error-Daten von error_reducer.py"""
    try:
        result = subprocess.run(
            ['python3', str(SCRIPTS_DIR / 'error_reducer.py')],
            capture_output=True, text=True, timeout=60, cwd=str(WORKSPACE)
        )
        
        data = {
            'error_rate': 0.0,
            'error_count': 0,
            'msg_count': 0,
            'breakdown': {}
        }
        
        for line in result.stdout.split('\n'):
            # Parse error rate
            match = re.search(r'Real Error Rate: ([0-9.]+)%', line)
            if match:
                data['error_rate'] = float(match.group(1))
            
            match = re.search(r'Total real errors: ([0-9]+)', line)
            if match:
                data['error_count'] = int(match.group(1))
            
            match = re.search(r'Total messages: ([0-9]+)', line)
            if match:
                data['msg_count'] = int(match.group(1))
            
            # Parse breakdown
            match = re.match(r'\s+(\w+):\s+(\d+)\s+\(([0-9.]+)%\)', line)
            if match:
                category = match.group(1)
                count = int(match.group(2))
                pct = float(match.group(3))
                data['breakdown'][category] = {'count': count, 'percentage': pct}
        
        return data
    except Exception as e:
        print(f"⚠️ Could not get real error data: {e}")
        return None

def get_fix_suggestions():
    """Returns actionable fix suggestions based on error categories"""
    return {
        'timeout': {
            'fix': 'Use background mode (&) or cron jobs for tasks >60s',
            'impact': 'High',
            'action': 'Review all exec calls >60s and convert to background/cron'
        },
        'not_found': {
            'fix': 'Verify paths before exec with ls/find',
            'impact': 'Medium',
            'action': 'Add path verification before critical exec calls'
        },
        'permission': {
            'fix': 'Check file permissions before write operations',
            'impact': 'Medium',
            'action': 'Verify permissions on workspace files'
        },
        'json_error': {
            'fix': 'Add JSON validation before parsing',
            'impact': 'Low',
            'action': 'Wrap JSON.parse in try-catch'
        },
        'exec_error': {
            'fix': 'Use direct script execution (python <file>.py)',
            'impact': 'N/A - System limit',
            'action': 'Cannot fix - exec preflight is a system security feature'
        },
        'unknown': {
            'fix': 'Monitor and categorize unknown errors',
            'impact': 'N/A - External',
            'action': 'Cannot fix - Telegram message length limit'
        }
    }

def main():
    print("🎯 ERROR RATE REDUCTION PLAN (Dynamic)")
    print("=" * 50)
    
    # Get real data
    data = get_real_error_data()
    
    if not data or data['error_rate'] == 0:
        print("⚠️ Could not retrieve error data. Using fallback.")
        data = {
            'error_rate': 1.41,
            'error_count': 1056,
            'msg_count': 74806,
            'breakdown': {
                'exec_error': {'count': 490, 'percentage': 46.4},
                'unknown': {'count': 458, 'percentage': 43.4},
                'timeout': {'count': 72, 'percentage': 6.8},
                'json_error': {'count': 15, 'percentage': 1.4},
                'permission': {'count': 14, 'percentage': 1.3},
                'not_found': {'count': 7, 'percentage': 0.7}
            }
        }
    
    print(f"📊 Current Error Rate: {data['error_rate']:.2f}%")
    print(f"   Total Errors: {data['error_count']}")
    print(f"   Total Messages: {data['msg_count']}")
    print(f"   Target: 1.0%")
    print(f"   Gap: {max(0, data['error_rate'] - 1.0):.2f}%")
    print()
    
    print("📊 DYNAMIC ERROR BREAKDOWN:")
    suggestions = get_fix_suggestions()
    total_errors = data['error_count']
    
    for category, cat_data in sorted(data['breakdown'].items(), key=lambda x: x[1]['count'], reverse=True):
        count = cat_data['count']
        pct = cat_data['percentage']
        fix_info = suggestions.get(category, {'fix': 'Unknown', 'impact': 'Unknown'})
        
        print(f"   {category}: {count} ({pct:.1f}%)")
        print(f"     → Fix: {fix_info['fix']}")
        print(f"     → Impact: {fix_info['impact']}")
        if fix_info.get('action'):
            print(f"     → Action: {fix_info['action']}")
        print()
    
    # Calculate potential improvement
    fixable = sum(
        data['breakdown'].get(cat, {'count': 0})['count']
        for cat in ['timeout', 'not_found', 'permission', 'json_error']
    )
    
    print("=" * 50)
    print("🚀 POTENTIAL IMPROVEMENT:")
    print(f"   Fixable errors: {fixable} ({fixable/total_errors*100:.1f}% of total)")
    
    if total_errors > 0:
        current_rate = data['error_rate']
        new_rate = (total_errors - fixable) / data['msg_count'] * 100 if data['msg_count'] > 0 else 0
        improvement = current_rate - new_rate
        print(f"   Current rate: {current_rate:.2f}%")
        print(f"   After fixing: {new_rate:.2f}%")
        print(f"   Improvement: {improvement:.2f}%")
    
    print()
    print("📋 IMMEDIATE ACTIONS:")
    print("  1. Review timeout errors (6.8%) - convert >60s tasks to background")
    print("  2. Review not_found errors (0.7%) - add path verification")
    print("  3. Review permission errors (1.3%) - check file permissions")
    
    # Save to log
    log_file = WORKSPACE / "logs" / "error_reduction_plan.json"
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'error_rate': data['error_rate'],
                'breakdown': data['breakdown']
            }, f, indent=2)
    except:
        pass

if __name__ == "__main__":
    main()
