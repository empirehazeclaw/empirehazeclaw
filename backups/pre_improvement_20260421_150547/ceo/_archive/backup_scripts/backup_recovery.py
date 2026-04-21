#!/usr/bin/env python3
"""
💾 Backup & Recovery System
=============================
Automatic config backups and disaster recovery
"""

import os
import json
import shutil
import subprocess
from datetime import datetime

BACKUP_DIR = '/home/clawbot/.openclaw/backup/'
CRITICAL_FILES = [
    '/home/clawbot/.openclaw/openclaw.json',
    '/home/clawbot/.openclaw/cron/jobs.json',
    '/home/clawbot/.openclaw/workspace/config/registered_agents.json',
]

def create_backup():
    """Create a backup of critical files"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(BACKUP_DIR, f'backup_{timestamp}')
    
    os.makedirs(backup_path, exist_ok=True)
    
    copied = []
    for file in CRITICAL_FILES:
        if os.path.exists(file):
            dest = os.path.join(backup_path, os.path.basename(file))
            shutil.copy2(file, dest)
            copied.append(file)
    
    # Also backup skills
    skills_dest = os.path.join(backup_path, 'skills')
    if os.path.exists('/home/clawbot/.openclaw/skills/'):
        shutil.copytree('/home/clawbot/.openclaw/skills/', skills_dest, dirs_exist_ok=True)
    
    # Save backup manifest
    manifest = {
        'timestamp': datetime.now().isoformat(),
        'files': copied,
        'version': '1.0'
    }
    with open(os.path.join(backup_path, 'manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Keep only last 10 backups
    cleanup_old_backups(10)
    
    return {'status': 'success', 'backup_path': backup_path, 'files': len(copied)}

def cleanup_old_backups(keep=10):
    """Remove old backups"""
    if not os.path.exists(BACKUP_DIR):
        return
    
    backups = sorted([d for d in os.listdir(BACKUP_DIR) if d.startswith('backup_')])
    
    while len(backups) > keep:
        oldest = backups.pop(0)
        shutil.rmtree(os.path.join(BACKUP_DIR, oldest))

def list_backups():
    """List available backups"""
    if not os.path.exists(BACKUP_DIR):
        return []
    
    backups = []
    for d in sorted(os.listdir(BACKUP_DIR)):
        path = os.path.join(BACKUP_DIR, d)
        if os.path.isdir(path):
            manifest_path = os.path.join(path, 'manifest.json')
            if os.path.exists(manifest_path):
                with open(manifest_path, 'r') as f:
                    m = json.load(f)
                    backups.append({
                        'name': d,
                        'timestamp': m.get('timestamp'),
                        'files': len(m.get('files', []))
                    })
    return backups

def restore_backup(backup_name):
    """Restore from a backup"""
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    
    if not os.path.exists(backup_path):
        return {'status': 'error', 'message': 'Backup not found'}
    
    restored = []
    for file in CRITICAL_FILES:
        backup_file = os.path.join(backup_path, os.path.basename(file))
        if os.path.exists(backup_file):
            shutil.copy2(backup_file, file)
            restored.append(file)
    
    return {'status': 'success', 'restored': len(restored)}

def get_latest_backup():
    """Get the most recent backup"""
    backups = list_backups()
    return backups[-1] if backups else None

if __name__ == '__main__':
    import sys
    
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'list'
    
    if cmd == 'backup':
        print(json.dumps(create_backup(), indent=2))
    elif cmd == 'list':
        print(json.dumps(list_backups(), indent=2))
    elif cmd == 'restore':
        name = sys.argv[2] if len(sys.argv) > 2 else None
        if name:
            print(json.dumps(restore_backup(name), indent=2))
        else:
            latest = get_latest_backup()
            print(json.dumps(restore_backup(latest['name']), indent=2))
    elif cmd == 'latest':
        print(json.dumps(get_latest_backup(), indent=2))
