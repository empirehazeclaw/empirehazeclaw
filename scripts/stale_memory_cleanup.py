#!/usr/bin/env python3
"""
stale_memory_cleanup.py — Stale Memory Cleanup
==============================================
Automatically identifies and optionally removes stale memories.

Features:
- Find memories older than X days
- Categorize: TRIVIAL (delete), OLD (review), ARCHIVE
- Batch operations
- Dry-run mode

Usage:
    from stale_memory_cleanup import StaleMemoryCleanup, cleanup
    
    cleanup = StaleMemoryCleanup()
    
    # Find stale memories
    stale = cleanup.find_stale_memories(older_than_days=90)
    
    # Preview what would be deleted
    cleanup.print_report(stale)
    
    # Actually delete
    cleanup.delete_stale_memories(stale, confirm=False)
"""

import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# Memory directories to scan
MEMORY_DIRS = [
    Path("/home/clawbot/.openclaw/workspace/memory"),
    Path("/home/clawbot/.openclaw/workspace/core_ultralight/memory"),
    Path("/home/clawbot/.openclaw/workspace/ceo/memory"),
    Path("/home/clawbot/.openclaw/workspace/shared/memory"),
]


class MemoryAge(Enum):
    TRIVIAL = "trivial"      # Very small, very old → delete
    STALE = "stale"          # Old and small → consider deleting
    OLD = "old"              # Old but has content → review
    ANCIENT = "ancient"      # Very old → archive or delete
    RECENT = "recent"        # Recent → keep


@dataclass
class MemoryInfo:
    """Information about a memory file."""
    path: Path
    relative_path: str
    size: int
    created_days_ago: int
    modified_days_ago: int
    age_category: MemoryAge
    content_preview: str
    is_backup: bool
    is_index: bool


class StaleMemoryCleanup:
    """
    Stale Memory Cleanup - manages old memory files.
    
    Age categories:
    - TRIVIAL: < 100 bytes AND > 60 days old
    - STALE: < 500 bytes AND > 90 days old
    - OLD: Any size AND > 90 days old
    - ANCIENT: Any size AND > 180 days old
    - RECENT: Modified < 90 days ago
    """
    
    # Thresholds
    TRIVIAL_SIZE = 100
    TRIVIAL_DAYS = 60
    STALE_SIZE = 500
    STALE_DAYS = 90
    ANCIENT_DAYS = 180
    
    # Files to never delete
    PROTECTED_PATTERNS = [
        "INDEX",
        "README",
        "RULES",
        ".vault-key",
    ]
    
    def __init__(self, memory_dirs: Optional[List[Path]] = None):
        self.memory_dirs = memory_dirs or MEMORY_DIRS
        self.scanned: List[MemoryInfo] = []
    
    def scan_memories(self) -> List[MemoryInfo]:
        """
        Scan all memory directories and categorize files.
        
        Returns:
            List of MemoryInfo for all found files
        """
        self.scanned = []
        
        for mem_dir in self.memory_dirs:
            if not mem_dir.exists():
                continue
            
            for md_file in mem_dir.rglob("*.md"):
                # Skip protected files
                if any(p in md_file.name for p in self.PROTECTED_PATTERNS):
                    continue
                
                # Skip backups (already have .backup)
                is_backup = ".backup" in md_file.name or md_file.name.endswith(".bak")
                
                # Basic info
                stat = md_file.stat()
                size = stat.st_size
                
                # Calculate ages
                now = datetime.now()
                modified_time = datetime.fromtimestamp(stat.st_mtime)
                created_time = datetime.fromtimestamp(stat.st_ctime)
                
                modified_days = (now - modified_time).days
                created_days = (now - created_time).days
                
                # Determine age category
                age_category = self._categorize_age(size, modified_days)
                
                # Content preview (first line)
                try:
                    content = md_file.read_text(errors="ignore")
                    preview = content.split('\n')[0][:100] if content else ""
                except:
                    preview = ""
                
                # Create memory info
                rel_path = str(md_file.relative_to(Path("/home/clawbot/.openclaw/workspace")))
                
                info = MemoryInfo(
                    path=md_file,
                    relative_path=rel_path,
                    size=size,
                    created_days_ago=created_days,
                    modified_days_ago=modified_days,
                    age_category=age_category,
                    content_preview=preview,
                    is_backup=is_backup,
                    is_index="INDEX" in md_file.name
                )
                
                self.scanned.append(info)
        
        return self.scanned
    
    def _categorize_age(self, size: int, modified_days: int) -> MemoryAge:
        """Categorize memory based on size and age."""
        if size < self.TRIVIAL_SIZE and modified_days > self.TRIVIAL_DAYS:
            return MemoryAge.TRIVIAL
        elif size < self.STALE_SIZE and modified_days > self.STALE_DAYS:
            return MemoryAge.STALE
        elif modified_days > self.ANCIENT_DAYS:
            return MemoryAge.ANCIENT
        elif modified_days > self.STALE_DAYS:
            return MemoryAge.OLD
        else:
            return MemoryAge.RECENT
    
    def find_stale_memories(
        self,
        older_than_days: Optional[int] = None,
        categories: Optional[List[MemoryAge]] = None,
        include_backups: bool = False
    ) -> List[MemoryInfo]:
        """
        Find stale memories matching criteria.
        
        Args:
            older_than_days: Only include memories older than this
            categories: Only include these age categories
            include_backups: Include backup files
        
        Returns:
            List of MemoryInfo matching criteria
        """
        if not self.scanned:
            self.scan_memories()
        
        results = []
        for mem in self.scanned:
            # Skip backups unless requested
            if mem.is_backup and not include_backups:
                continue
            
            # Skip protected files
            if any(p in mem.path.name for p in self.PROTECTED_PATTERNS):
                continue
            
            # Filter by age
            if older_than_days and mem.modified_days_ago < older_than_days:
                continue
            
            # Filter by category
            if categories and mem.age_category not in categories:
                continue
            
            results.append(mem)
        
        return results
    
    def get_summary(self, memories: Optional[List[MemoryInfo]] = None) -> Dict:
        """Get summary statistics for memory list."""
        memories = memories or self.scanned
        
        if not memories:
            return {
                "total": 0,
                "by_category": {},
                "total_size": 0,
                "oldest_days": 0,
                "largest_size": 0
            }
        
        by_category = {}
        total_size = sum(m.size for m in memories)
        oldest_days = max(m.modified_days_ago for m in memories)
        largest_size = max(m.size for m in memories)
        
        for mem in memories:
            cat = mem.age_category.value
            by_category[cat] = by_category.get(cat, 0) + 1
        
        return {
            "total": len(memories),
            "by_category": by_category,
            "total_size": total_size,
            "oldest_days": oldest_days,
            "largest_size": largest_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2)
        }
    
    def print_report(
        self,
        memories: Optional[List[MemoryInfo]] = None,
        title: str = "Stale Memory Report"
    ):
        """Print a formatted report of memories."""
        memories = memories or self.scanned
        
        if not memories:
            print("No memories found.")
            return
        
        summary = self.get_summary(memories)
        
        print(f"\n{'='*60}")
        print(f"📋 {title}")
        print(f"{'='*60}")
        print(f"Total memories: {summary['total']}")
        print(f"Total size: {summary['total_size_mb']} MB")
        print(f"Oldest: {summary['oldest_days']} days")
        print()
        
        print("By Category:")
        for cat, count in summary['by_category'].items():
            print(f"  {cat}: {count}")
        
        print()
        print("Files:")
        for mem in sorted(memories, key=lambda m: m.modified_days_ago, reverse=True):
            cat_emoji = {
                MemoryAge.TRIVIAL: "🗑️",
                MemoryAge.STALE: "📦",
                MemoryAge.OLD: "📁",
                MemoryAge.ANCIENT: "💀",
                MemoryAge.RECENT: "✅"
            }.get(mem.age_category, "📄")
            
            print(f"  {cat_emoji} [{mem.age_category.value:8}] {mem.modified_days_ago:4}d {mem.size:8}b | {mem.relative_path}")
            if mem.content_preview:
                print(f"       → {mem.content_preview[:60]}...")
    
    def delete_stale_memories(
        self,
        memories: List[MemoryInfo],
        confirm: bool = True,
        dry_run: bool = False
    ) -> Tuple[int, int]:
        """
        Delete stale memories.
        
        Args:
            memories: List of MemoryInfo to delete
            confirm: Ask for confirmation before deleting
            dry_run: Don't actually delete, just report
        
        Returns:
            Tuple of (deleted_count, freed_bytes)
        """
        if confirm and not dry_run:
            print(f"\n⚠️  About to delete {len(memories)} files ({sum(m.size for m in memories)} bytes)")
            response = input("Continue? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("Aborted.")
                return 0, 0
        
        if dry_run:
            print(f"\n🔍 DRY RUN: Would delete {len(memories)} files")
            self.print_report(memories, "Would Delete")
            return len(memories), sum(m.size for m in memories)
        
        deleted = 0
        freed = 0
        
        for mem in memories:
            try:
                # Move to trash instead of permanent delete
                trash_path = mem.path.parent / ".trash" / mem.path.name
                trash_path.parent.mkdir(exist_ok=True)
                mem.path.rename(trash_path)
                deleted += 1
                freed += mem.size
                print(f"  🗑️  Deleted: {mem.relative_path}")
            except Exception as e:
                print(f"  ❌ Failed to delete {mem.relative_path}: {e}")
        
        print(f"\n✅ Deleted {deleted} files, freed {freed} bytes")
        return deleted, freed
    
    def archive_stale_memories(
        self,
        memories: List[MemoryInfo],
        archive_name: str = "stale_archive"
    ) -> Path:
        """
        Archive stale memories into a single file.
        
        Returns:
            Path to created archive
        """
        archive_dir = Path("/home/clawbot/.openclaw/workspace/memory/.archives")
        archive_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_file = archive_dir / f"{archive_name}_{timestamp}.md"
        
        with open(archive_file, "w") as f:
            f.write(f"# Stale Memory Archive - {datetime.now().isoformat()}\n\n")
            f.write(f"Archived {len(memories)} files\n\n")
            
            for mem in sorted(memories, key=lambda m: m.modified_days_ago, reverse=True):
                f.write(f"\n---\n\n")
                f.write(f"## {mem.relative_path}\n")
                f.write(f"Modified: {mem.modified_days_ago} days ago\n")
                f.write(f"Size: {mem.size} bytes\n\n")
                try:
                    content = mem.path.read_text(errors="ignore")
                    f.write(content)
                except:
                    f.write("[Could not read content]")
        
        print(f"✅ Archived {len(memories)} files to {archive_file}")
        return archive_file


# Convenience function
def cleanup(
    older_than_days: int = 90,
    categories: Optional[List[str]] = None,
    delete: bool = False,
    dry_run: bool = True
) -> Tuple[int, int]:
    """
    Quick stale memory cleanup.
    
    Usage:
        # Preview what would be deleted
        cleanup(older_than_days=90)
        
        # Actually delete
        cleanup(older_than_days=90, delete=True)
    """
    cat_map = {
        "trivial": MemoryAge.TRIVIAL,
        "stale": MemoryAge.STALE,
        "old": MemoryAge.OLD,
        "ancient": MemoryAge.ANCIENT,
    }
    
    cat_list = [cat_map[c] for c in (categories or ["stale", "old", "ancient"])]
    
    cleanup = StaleMemoryCleanup()
    stale = cleanup.find_stale_memories(
        older_than_days=older_than_days,
        categories=cat_list
    )
    
    if not stale:
        print("No stale memories found.")
        return 0, 0
    
    cleanup.print_report(stale, f"Stale Memories (> {older_than_days} days)")
    
    if delete:
        return cleanup.delete_stale_memories(stale, confirm=True, dry_run=dry_run)
    
    return len(stale), sum(m.size for m in stale)


# ============ CLI Interface ============

if __name__ == "__main__":
    import sys
    
    print("Stale Memory Cleanup")
    print("=" * 50)
    print()
    
    cleanup = StaleMemoryCleanup()
    
    # Default: find all old memories
    days = 90
    if len(sys.argv) > 1:
        days = int(sys.argv[1])
    
    print(f"Scanning for memories older than {days} days...")
    print()
    
    memories = cleanup.find_stale_memories(older_than_days=days)
    cleanup.print_report(memories, f"Memories older than {days} days")
    
    if memories:
        print()
        print(f"Summary: {len(memories)} files, {sum(m.size for m in memories)} bytes")
        print()
        print("To delete:")
        print(f"  cleanup.delete_stale_memories(memories, confirm=True)")
