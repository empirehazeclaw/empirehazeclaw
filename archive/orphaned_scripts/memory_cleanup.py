#!/usr/bin/env python3
"""
🧹 Memory Cleanup Script
- Removes duplicate files
- Archives old files
- Creates backup
- Run: python3 scripts/memory_cleanup.py
"""
import os
import shutil
import json
from datetime import datetime, timedelta

MEMORY_DIR = '/home/clawbot/.openclaw/workspace/memory'
ARCHIVE_DIR = '/home/clawbot/.openclaw/workspace/memory/archive'
BACKUP_DIR = '/home/clawbot/.openclaw/workspace/memory/backup'

def create_directories():
    """Create necessary directories"""
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)
    print("✅ Directories created")

def backup_knowledge_graph():
    """Backup knowledge graph"""
    # Check multiple possible locations
    kg_file = os.path.join(MEMORY_DIR, 'knowledge_graph.json')
    if not os.path.exists(kg_file):
        kg_file = os.path.join(MEMORY_DIR, 'json/knowledge_graph.json')
    if not os.path.exists(kg_file):
        kg_file = '/home/clawbot/.openclaw/workspace/memory/json/knowledge_graph.json'
    
    if os.path.exists(kg_file):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        backup_file = os.path.join(BACKUP_DIR, f'knowledge_graph_{timestamp}.json')
        shutil.copy2(kg_file, backup_file)
        print(f"✅ Knowledge graph backed up: {backup_file}")
    else:
        print("⚠️ No knowledge graph found")

def find_duplicates():
    """Find duplicate files"""
    files = {}
    duplicates = []
    
    for f in os.listdir(MEMORY_DIR):
        if f.endswith('.md'):
            # Use filename without date as key
            key = f.replace('2026-03-', '').replace('2026-02-', '').replace('2026-01-', '')
            if key in files:
                duplicates.append((files[key], f))
            else:
                files[key] = f
    
    return duplicates

def remove_social_duplicates():
    """Remove duplicate social_posts files"""
    social_files = [f for f in os.listdir(MEMORY_DIR) if 'social_posts' in f]
    
    # Keep only the latest one
    social_files.sort()
    to_remove = social_files[:-1]  # Keep last one
    
    for f in to_remove:
        path = os.path.join(MEMORY_DIR, f)
        # Move to archive instead of delete
        archive_path = os.path.join(ARCHIVE_DIR, f)
        shutil.move(path, archive_path)
        print(f"🗑️ Archived duplicate: {f}")
    
    print(f"✅ Removed {len(to_remove)} duplicate social_posts files")

def archive_old_files(days=30):
    """Archive files older than X days"""
    cutoff = datetime.now() - timedelta(days=days)
    archived = 0
    
    for f in os.listdir(MEMORY_DIR):
        if f.startswith('bi-council') or f.startswith('verification'):
            path = os.path.join(MEMORY_DIR, f)
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            if mtime < cutoff:
                archive_path = os.path.join(ARCHIVE_DIR, f)
                shutil.move(path, archive_path)
                archived += 1
    
    print(f"✅ Archived {archived} old agent files")

def organize_by_date():
    """Organize daily notes by year/month"""
    daily_dir = os.path.join(MEMORY_DIR, 'daily')
    os.makedirs(daily_dir, exist_ok=True)
    
    for f in os.listdir(MEMORY_DIR):
        if f.startswith('20') and f.endswith('.md'):
            # Extract date from filename
            try:
                date_str = f[:10]  # 2026-03-16
                year, month = date_str.split('-')[:2]
                
                # Create year/month folder
                month_dir = os.path.join(daily_dir, year, month)
                os.makedirs(month_dir, exist_ok=True)
                
                # Move file
                src = os.path.join(MEMORY_DIR, f)
                dst = os.path.join(month_dir, f)
                shutil.move(src, dst)
                print(f"📁 Moved: {f} -> {year}/{month}/")
            except:
                pass
    
    print("✅ Organized daily notes by date")

def main():
    print("=" * 50)
    print("🧹 Memory Cleanup Started")
    print("=" * 50)
    
    create_directories()
    backup_knowledge_graph()
    remove_social_duplicates()
    archive_old_files()
    organize_by_date()
    
    print("=" * 50)
    print("✅ Cleanup Complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()
