#!/usr/bin/env python3
"""
Phase 6.4: Memory Consolidator
===============================
Automatically consolidates and cleans up memory files.

Features:
- Deduplication of similar entries
- Staleness detection for old facts
- Semantic cleanup of redundant content
- Automated archiving of old files

Usage:
    python3 memory_consolidator.py --action analyze
    python3 memory_consolidator.py --action deduplicate [--dry-run]
    python3 memory_consolidator.py --action archive
    python3 memory_consolidator.py --action full
"""

import json
import os
import sys
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

WORKSPACE = '/home/clawbot/.openclaw/workspace/ceo'
MEMORY_DIR = f"{WORKSPACE}/memory"
ARCHIVE_DIR = f"{WORKSPACE}/memory/ARCHIVE"
ANALYSIS_FILE = f"{WORKSPACE}/memory/evaluations/memory_analysis.json"


class MemoryConsolidator:
    def __init__(self):
        self.analysis = {
            'timestamp': datetime.now().isoformat(),
            'files_scanned': 0,
            'total_size_kb': 0,
            'duplicates': [],
            'stale_facts': [],
            'recommendations': []
        }
    
    def scan_memory(self):
        """Scan all memory files and build analysis."""
        print("🔍 Scanning Memory...")
        print("=" * 50)
        
        memory_files = []
        
        for root, dirs, files in os.walk(MEMORY_DIR):
            # Skip ARCHIVE, .dreams, __pycache__
            if 'ARCHIVE' in root or '.dreams' in root or '__pycache__' in root:
                continue
            
            for f in files:
                if not f.endswith('.md') and not f.endswith('.json'):
                    continue
                
                path = os.path.join(root, f)
                size = os.path.getsize(path)
                mtime = datetime.fromtimestamp(os.path.getmtime(path))
                age_days = (datetime.now() - mtime).days
                
                rel_path = os.path.relpath(path, MEMORY_DIR)
                
                memory_files.append({
                    'path': path,
                    'rel_path': rel_path,
                    'size': size,
                    'size_kb': size / 1024,
                    'mtime': mtime.isoformat(),
                    'age_days': age_days,
                    'type': 'md' if f.endswith('.md') else 'json'
                })
                
                self.analysis['files_scanned'] += 1
                self.analysis['total_size_kb'] += size / 1024
        
        self.analysis['files'] = memory_files
        
        # Analyze by type
        by_type = Counter(f['type'] for f in memory_files)
        by_age = Counter(f['age_days'] > 30 for f in memory_files)
        
        print(f"\n📊 Memory Scan Results:")
        print(f"   Total Files: {len(memory_files)}")
        print(f"   Total Size: {self.analysis['total_size_kb']:.1f} KB")
        print(f"   Markdown: {by_type.get('md', 0)}")
        print(f"   JSON: {by_type.get('json', 0)}")
        print(f"   Old (>30 days): {by_age.get(True, 0)}")
        print(f"   Recent: {by_age.get(False, 0)}")
        
        return memory_files
    
    def find_duplicates(self):
        """Find duplicate or near-duplicate files."""
        print("\n🔎 Finding Duplicates...")
        
        # Group by size first (quick filter)
        by_size = {}
        for f in self.analysis.get('files', []):
            size = f['size']
            if size > 1000:  # Only files > 1KB
                if size not in by_size:
                    by_size[size] = []
                by_size[size].append(f)
        
        duplicates = []
        
        for size, files in by_size.items():
            if len(files) < 2:
                continue
            
            # Group by content hash
            by_hash = {}
            for f in files:
                try:
                    with open(f['path'], 'r') as fh:
                        content = fh.read()
                        h = hashlib.md5(content.encode()).hexdigest()
                        if h not in by_hash:
                            by_hash[h] = []
                        by_hash[h].append(f)
                
                except:
                    continue
            
            for h, group in by_hash.items():
                if len(group) > 1:
                    duplicates.append({
                        'hash': h,
                        'files': group,
                        'count': len(group)
                    })
        
        self.analysis['duplicates'] = duplicates
        
        if duplicates:
            print(f"   ⚠️ Found {len(duplicates)} duplicate groups:")
            for d in duplicates[:5]:  # Show first 5
                print(f"      {d['count']}x: {d['files'][0]['rel_path']}")
        else:
            print(f"   ✅ No duplicates found")
        
        return duplicates
    
    def find_stale_facts(self):
        """Find facts that are old and probably stale."""
        print("\n⏰ Checking for Stale Facts...")
        
        stale = []
        
        # Check daily notes for old events
        for f in self.analysis.get('files', []):
            if not f['rel_path'].startswith('2'):
                continue
            
            if f['age_days'] > 14:
                # Check if it contains timestamps suggesting it's old news
                try:
                    with open(f['path'], 'r') as fh:
                        content = fh.read()
                    
                    # Look for old date patterns
                    old_date_patterns = ['2026-03', '2026-02', '2026-01']
                    for pattern in old_date_patterns:
                        if pattern in f['rel_path']:
                            stale.append({
                                'file': f,
                                'reason': f'Old date in filename ({pattern})',
                                'action': 'archive'
                            })
                            break
                
                except:
                    pass
        
        self.analysis['stale_facts'] = stale
        
        if stale:
            print(f"   ⚠️ Found {len(stale)} potentially stale entries:")
            for s in stale[:5]:
                print(f"      {s['file']['rel_path']}: {s['reason']}")
        else:
            print(f"   ✅ No stale facts detected")
        
        return stale
    
    def generate_recommendations(self):
        """Generate cleanup recommendations."""
        print("\n💡 Generating Recommendations...")
        
        recs = []
        
        # Duplicates
        dup_count = len(self.analysis.get('duplicates', []))
        if dup_count > 0:
            recs.append({
                'type': 'duplicates',
                'priority': 'MED',
                'action': 'review and delete duplicates',
                'count': dup_count
            })
        
        # Stale facts
        stale_count = len(self.analysis.get('stale_facts', []))
        if stale_count > 0:
            recs.append({
                'type': 'stale',
                'priority': 'LOW',
                'action': 'archive old entries',
                'count': stale_count
            })
        
        # Size issues
        if self.analysis['total_size_kb'] > 5000:
            recs.append({
                'type': 'size',
                'priority': 'HIGH',
                'action': 'consider archiving more aggressively',
                'size_kb': self.analysis['total_size_kb']
            })
        
        # Old daily notes
        old_dailies = [f for f in self.analysis.get('files', []) 
                      if f['age_days'] > 30 and f['rel_path'].startswith('2')]
        if old_dailies:
            recs.append({
                'type': 'old_dailies',
                'priority': 'LOW',
                'action': 'archive daily notes older than 30 days',
                'count': len(old_dailies)
            })
        
        self.analysis['recommendations'] = recs
        
        if recs:
            print(f"   Found {len(recs)} recommendations:")
            for r in recs:
                print(f"      [{r['priority']}] {r['type']}: {r['action']}")
        else:
            print(f"   ✅ Memory is clean, no recommendations")
        
        return recs
    
    def archive_old_files(self, days=30, dry_run=True):
        """Archive files older than specified days."""
        print(f"\n📦 Archiving files older than {days} days...")
        
        if dry_run:
            print("   ⚠️ DRY RUN - no files will be moved")
        
        archived = []
        
        for f in self.analysis.get('files', []):
            if f['age_days'] <= days:
                continue
            
            # Skip important files
            if f['rel_path'] in ['INDEX.md', 'goals.json', 'heartbeat-state.json']:
                continue
            
            if dry_run:
                archived.append(f)
            else:
                # Actually move to archive
                try:
                    os.makedirs(ARCHIVE_DIR, exist_ok=True)
                    new_path = os.path.join(ARCHIVE_DIR, f'{f["rel_path"]}.{datetime.now().strftime("%Y%m%d")}')
                    
                    # Handle conflicts
                    if os.path.exists(new_path):
                        base, ext = os.path.splitext(new_path)
                        new_path = f"{base}_2{ext}"
                    
                    os.rename(f['path'], new_path)
                    archived.append(f)
                except Exception as e:
                    print(f"   ❌ Failed to archive {f['rel_path']}: {e}")
        
        if archived:
            print(f"   {'Would archive' if dry_run else 'Archived'} {len(archived)} files")
            for a in archived[:10]:
                print(f"      - {a['rel_path']}")
        
        return archived
    
    def run(self, action='analyze', dry_run=True):
        """Run requested action."""
        if action == 'analyze':
            self.scan_memory()
            self.find_duplicates()
            self.find_stale_facts()
            self.generate_recommendations()
            self.save_analysis()
            return self.analysis
        
        elif action == 'deduplicate':
            self.scan_memory()
            self.find_duplicates()
            if not dry_run:
                print("⚠️ Deduplication not yet implemented")
            return self.analysis
        
        elif action == 'archive':
            self.scan_memory()
            return self.archive_old_files(days=30, dry_run=dry_run)
        
        elif action == 'full':
            self.scan_memory()
            self.find_duplicates()
            self.find_stale_facts()
            self.generate_recommendations()
            self.save_analysis()
            return self.analysis
        
        else:
            print(f"Unknown action: {action}")
            return None
    
    def save_analysis(self):
        """Save analysis to file."""
        with open(ANALYSIS_FILE, 'w') as f:
            json.dump(self.analysis, f, indent=2)
        print(f"\n💾 Analysis saved to: {ANALYSIS_FILE}")


def main():
    consolidator = MemoryConsolidator()
    
    action = 'analyze'
    dry_run = True
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--action' and i+1 < len(args):
            action = args[i+1]
            i += 2
        elif args[i] == '--dry-run':
            dry_run = False
            i += 1
        else:
            i += 1
    
    consolidator.run(action, dry_run)


if __name__ == '__main__':
    main()
