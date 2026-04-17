#!/usr/bin/env python3
"""
Memory Consolidator — Sir HazeClaw Phase 2
=========================================
Consolidates fragmented memory files.

Usage:
    python3 memory_consolidator.py --scan      # Scan and categorize
    python3 memory_consolidator.py --archive   # Archive old files
    python3 memory_consolidator.py --index      # Rebuild INDEX.md
    python3 memory_consolidator.py --full       # Full consolidation

Phase B4: Memory Consolidation Automation
"""

import os
import sys
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "ceo/memory"
NOTES_DIR = MEMORY_DIR / "notes"
ARCHIVE_DIR = MEMORY_DIR / "ARCHIVE"
INDEX_FILE = MEMORY_DIR / "notes/INDEX.md"

# Age thresholds (days)
OLD_THRESHOLD = 30  # Archive files older than this
STALE_THRESHOLD = 7   # Delete temp files older than this

# File categories
KEPT_EXTENSIONS = ['.md', '.json', '.emb.json']
IGNORED_PATTERNS = ['.git', '__pycache__', 'node_modules', '.dreams']

# Priority files to KEEP in place (not archived)
PRIORITY_FILES = {
    'MEMORY.md',
    'USER.md',
    'SOUL.md',
    'IDENTITY.md',
    'AGENTS.md',
    'TOOLS.md',
    'HEARTBEAT.md',
    'notes/INDEX.md',
    'notes/system_improvement_master_plan.md',
    'notes/memory_optimization_plan.md',
    'notes/intention_engine_plan.md',
    'notes/weekly_review_template.md',
    'notes/SYSTEM_IMPROVEMENT_PHASE1_DOC.md',
    'daily_summary_2026-04-17.md',
    '2026-04-17.md',
}

def get_file_age(path: Path) -> int:
    """Get file age in days."""
    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime)
        return (datetime.now() - mtime).days
    except:
        return 0

def should_archive(path: Path) -> tuple[bool, str]:
    """Check if file should be archived."""
    name = path.name
    
    # Never archive priority files
    rel = str(path.relative_to(MEMORY_DIR))
    
    # Never archive priority files
    if rel in PRIORITY_FILES or path.name in PRIORITY_FILES:
        return False, "priority_file"
    
    # Never archive recent files
    age = get_file_age(path)
    if age < OLD_THRESHOLD:
        return False, "recent"
    
    # Archive old notes/ARCHIVE files
    if 'notes' in str(path) or 'ARCHIVE' in str(path):
        return True, "old_note"
    
    # Archive old daily logs
    if '20' in name[:10]:  # Date pattern like 2026-04-17.md
        return True, "old_daily"
    
    return False, "keep"

def scan_memory() -> dict:
    """Scan all memory files and categorize."""
    categories = {
        'priority': [],      # Keep in place
        'to_archive': [],    # Move to ARCHIVE
        'to_delete': [],     # Delete old temp files
        'recent': [],        # Keep, recently modified
    }
    
    for path in MEMORY_DIR.rglob("*.md"):
        # Skip ignored patterns
        if any(p in str(path) for p in IGNORED_PATTERNS):
            continue
        
        rel = str(path.relative_to(MEMORY_DIR))
        age = get_file_age(path)
        
        should_arch, reason = should_archive(path)
        
        info = {
            'path': rel,
            'age_days': age,
            'reason': reason,
            'size_kb': path.stat().st_size // 1024
        }
        
        if should_arch:
            categories['to_archive'].append(info)
        elif age > STALE_THRESHOLD and ('temp' in rel.lower() or 'tmp' in rel.lower()):
            categories['to_delete'].append(info)
        elif reason == "priority_file":
            categories['priority'].append(info)
        else:
            categories['recent'].append(info)
    
    return categories

def build_index_content(files: list) -> str:
    """Build INDEX.md content from file list."""
    lines = [
        "# 📚 Memory System Index",
        f"_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}_",
        "",
        "## 📁 Directory Structure",
        "",
        "```",
        "ceo/memory/",
        "├── short_term/       # Current session data",
        "├── long_term/       # Facts, patterns, preferences",
        "├── episodes/        # Timeline of events",
        "├── procedural/      # Skills, rules, workflows",
        "├── kg/             # Knowledge Graph",
        "├── search/         # Semantic search index",
        "├── notes/          # Plans, guides, learnings",
        "├── autonomy/       # Action/error logs",
        "└── ARCHIVE/        # Old files (auto-archived)",
        "```",
        "",
        f"## 📊 Statistics",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total .md files | {len(files)} |",
        f"| Active notes | {len(list(NOTES_DIR.glob('*.md')))} |",
        f"| Archived files | {len(list(ARCHIVE_DIR.rglob('*.md')))} |",
        "",
    ]
    return "\n".join(lines)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Memory Consolidator')
    parser.add_argument('--scan', action='store_true', help='Scan and categorize')
    parser.add_argument('--archive', action='store_true', help='Archive old files')
    parser.add_argument('--index', action='store_true', help='Rebuild INDEX.md')
    parser.add_argument('--full', action='store_true', help='Full consolidation')
    args = parser.parse_args()
    
    if args.scan or args.full:
        print("🔍 Scanning memory files...")
        cats = scan_memory()
        
        print(f"\n📊 Memory Scan Results:")
        print(f"   Priority (keep): {len(cats['priority'])}")
        print(f"   To archive: {len(cats['to_archive'])}")
        print(f"   To delete: {len(cats['to_delete'])}")
        print(f"   Recent (keep): {len(cats['recent'])}")
        
        if cats['to_archive']:
            print(f"\n📦 Files to archive ({OLD_THRESHOLD}+ days old):")
            for f in cats['to_archive'][:10]:
                print(f"   - {f['path']} ({f['age_days']} days)")
        
        if cats['to_delete']:
            print(f"\n🗑️ Files to delete (old temp files):")
            for f in cats['to_delete'][:5]:
                print(f"   - {f['path']}")
    
    if args.index or args.full:
        print("\n📝 Building INDEX.md...")
        cats = scan_memory()
        all_files = cats['priority'] + cats['recent'] + cats['to_archive']
        content = build_index_content(all_files)
        INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(INDEX_FILE, 'w') as f:
            f.write(content)
        print(f"✅ INDEX.md updated ({len(all_files)} files indexed)")
    
    if args.archive or args.full:
        print("\n📦 Archiving old files...")
        cats = scan_memory()
        archived = 0
        for f in cats['to_archive']:
            src = MEMORY_DIR / f['path']
            # Build target path preserving structure
            parts = f['path'].split('/')
            if 'notes' in parts:
                # Move notes to ARCHIVE/notes/
                target_parts = ['ARCHIVE'] + parts
            else:
                # Move daily logs to ARCHIVE/YYYY-MM/
                date_prefix = f['path'][:10] if f['path'][0].isdigit() else 'unknown'
                target_parts = ['ARCHIVE', date_prefix] + parts[-1:]
            
            target = MEMORY_DIR / '/'.join(target_parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                shutil.move(str(src), str(target))
                archived += 1
            except Exception as e:
                print(f"   ⚠️ Failed to archive {f['path']}: {e}")
        
        print(f"✅ Archived {archived} files")

if __name__ == "__main__":
    main()
