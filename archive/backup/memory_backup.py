#!/usr/bin/env python3
"""
💾 Memory Backup Script
Backs up memory folder to timestamped archive
"""
import os
import shutil
import tarfile
from datetime import datetime

MEMORY_DIR = '/home/clawbot/.openclaw/workspace/memory'
BACKUP_DIR = '/home/clawbot/.openclaw/workspace/backups'

def backup_memory():
    """Create timestamped backup of memory folder"""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    backup_file = os.path.join(BACKUP_DIR, f'memory_{timestamp}.tar.gz')
    
    with tarfile.open(backup_file, 'w:gz') as tar:
        tar.add(MEMORY_DIR, arcname='memory')
    
    print(f"✅ Backup created: {backup_file}")
    return backup_file

if __name__ == "__main__":
    backup_memory()
