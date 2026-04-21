#!/usr/bin/env python3
"""
memory_versioning.py — Memory Versioning & Rollback
=================================================
Keeps history of memory changes for rollback capability.

Features:
- Automatic versioning of memory files
- Rollback to previous versions
- Version comparison
- Automatic cleanup of old versions

Usage:
    from memory_versioning import MemoryVersioning, versioning
    
    versioner = MemoryVersioning()
    versioner.save_version('MEMORY.md', 'New content here')
    
    # List versions
    versions = versioner.list_versions('MEMORY.md')
    
    # Rollback
    versioner.rollback('MEMORY.md', version_id='v3')
"""

import json
import shutil
import hashlib
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass

# Version storage
VERSION_DIR = Path("/home/clawbot/.openclaw/workspace/.memory_versions")


@dataclass
class VersionInfo:
    """Information about a memory version."""
    version_id: str
    file_name: str
    timestamp: str
    content_hash: str
    content_length: int
    change_type: str  # "create", "update", "rollback"
    user: str
    comment: Optional[str] = None


class MemoryVersioning:
    """
    Memory Versioning - provides rollback capability for memory files.
    
    Keeps:
    - Last N versions of each memory file
    - Version metadata for quick lookup
    - Hash verification for integrity
    
    Cleanup:
    - Automatic removal of old versions (configurable)
    - Manual cleanup available
    """
    
    # Default settings
    MAX_VERSIONS_PER_FILE = 10
    MAX_AGE_DAYS = 30
    
    def __init__(
        self,
        version_dir: Optional[str] = None,
        max_versions: int = MAX_VERSIONS_PER_FILE,
        max_age_days: int = MAX_AGE_DAYS
    ):
        self.version_dir = Path(version_dir) if version_dir else VERSION_DIR
        self.version_dir.mkdir(parents=True, exist_ok=True)
        self.max_versions = max_versions
        self.max_age_days = max_age_days
        
        # Index file for quick lookup
        self.index_file = self.version_dir / "version_index.json"
    
    def _compute_hash(self, content: str) -> str:
        """Compute short hash of content."""
        return hashlib.sha256(content.encode()).hexdigest()[:12]
    
    def _get_file_versions_dir(self, file_name: str) -> Path:
        """Get directory for versions of a specific file."""
        # Sanitize filename
        safe_name = file_name.replace("/", "_").replace("\\", "_")
        file_dir = self.version_dir / safe_name
        file_dir.mkdir(parents=True, exist_ok=True)
        return file_dir
    
    def _load_index(self) -> Dict:
        """Load version index."""
        if self.index_file.exists():
            with open(self.index_file) as f:
                return json.load(f)
        return {}
    
    def _save_index(self, index: Dict) -> None:
        """Save version index."""
        with open(self.index_file, "w") as f:
            json.dump(index, f, indent=2)
    
    def save_version(
        self,
        file_name: str,
        content: str,
        user: str = "system",
        change_type: str = "update",
        comment: Optional[str] = None
    ) -> VersionInfo:
        """
        Save a new version of a memory file.
        
        Args:
            file_name: Name of the memory file
            content: Content to save
            user: User/system identifier
            change_type: Type of change (create, update, rollback)
            comment: Optional comment
        
        Returns:
            VersionInfo about the saved version
        """
        # Create version info
        content_hash = self._compute_hash(content)
        timestamp = datetime.now().isoformat()
        
        # Generate version ID
        version_id = f"v{len(self.list_versions(file_name)) + 1}_{content_hash[:6]}"
        
        version_info = VersionInfo(
            version_id=version_id,
            file_name=file_name,
            timestamp=timestamp,
            content_hash=content_hash,
            content_length=len(content),
            change_type=change_type,
            user=user,
            comment=comment
        )
        
        # Save version content
        file_dir = self._get_file_versions_dir(file_name)
        version_file = file_dir / f"{version_id}.txt"
        version_file.write_text(content)
        
        # Save version metadata
        meta_file = file_dir / f"{version_id}.meta.json"
        with open(meta_file, "w") as f:
            json.dump(version_info.__dict__, f, indent=2)
        
        # Update index
        index = self._load_index()
        if file_name not in index:
            index[file_name] = []
        index[file_name].append(version_info.__dict__)
        self._save_index(index)
        
        # Cleanup old versions
        self._cleanup_old_versions(file_name)
        
        return version_info
    
    def list_versions(
        self,
        file_name: str,
        limit: Optional[int] = None
    ) -> List[VersionInfo]:
        """
        List all versions of a memory file.
        
        Returns:
            List of VersionInfo objects, most recent first
        """
        index = self._load_index()
        versions = index.get(file_name, [])
        
        # Convert to VersionInfo objects
        version_infos = [VersionInfo(**v) for v in versions]
        
        # Sort by timestamp (newest first)
        version_infos.sort(key=lambda v: v.timestamp, reverse=True)
        
        if limit:
            version_infos = version_infos[:limit]
        
        return version_infos
    
    def get_version(
        self,
        file_name: str,
        version_id: str
    ) -> Optional[Tuple[str, VersionInfo]]:
        """
        Get content of a specific version.
        
        Returns:
            Tuple of (content, VersionInfo) or None if not found
        """
        file_dir = self._get_file_versions_dir(file_name)
        version_file = file_dir / f"{version_id}.txt"
        
        if not version_file.exists():
            return None
        
        content = version_file.read_text()
        
        # Load metadata
        meta_file = file_dir / f"{version_id}.meta.json"
        if meta_file.exists():
            with open(meta_file) as f:
                meta = json.load(f)
            version_info = VersionInfo(**meta)
        else:
            version_info = VersionInfo(
                version_id=version_id,
                file_name=file_name,
                timestamp="unknown",
                content_hash=self._compute_hash(content),
                content_length=len(content),
                change_type="unknown",
                user="unknown"
            )
        
        return content, version_info
    
    def rollback(
        self,
        file_name: str,
        version_id: str,
        user: str = "system",
        create_backup: bool = True
    ) -> Optional[str]:
        """
        Rollback a memory file to a previous version.
        
        Args:
            file_name: Name of the file to rollback
            version_id: Version to rollback to
            user: User performing rollback
            create_backup: Whether to backup current version first
        
        Returns:
            Content of the rolled-back version, or None if failed
        """
        result = self.get_version(file_name, version_id)
        
        if not result:
            return None
        
        content, version_info = result
        
        # Get original file path
        original_path = Path("/home/clawbot/.openclaw/workspace") / file_name
        
        # Backup current version if exists and requested
        if create_backup and original_path.exists():
            current_content = original_path.read_text()
            self.save_version(
                file_name,
                current_content,
                user=user,
                change_type="pre_rollback_backup",
                comment=f"Auto-backup before rollback to {version_id}"
            )
        
        # Save rollback as new version
        self.save_version(
            file_name,
            content,
            user=user,
            change_type="rollback",
            comment=f"Rolled back to {version_id}"
        )
        
        return content
    
    def compare_versions(
        self,
        file_name: str,
        version_id_1: str,
        version_id_2: str
    ) -> Optional[Dict]:
        """
        Compare two versions of a memory file.
        
        Returns:
            Dict with comparison results, or None if not found
        """
        result1 = self.get_version(file_name, version_id_1)
        result2 = self.get_version(file_name, version_id_2)
        
        if not result1 or not result2:
            return None
        
        content1, info1 = result1
        content2, info2 = result2
        
        # Simple diff (line-based)
        lines1 = content1.split('\n')
        lines2 = content2.split('\n')
        
        return {
            "file": file_name,
            "version1": version_id_1,
            "version2": version_id_2,
            "timestamp1": info1.timestamp,
            "timestamp2": info2.timestamp,
            "size1": len(content1),
            "size2": len(content2),
            "size_diff": len(content2) - len(content1),
            "lines_added": len([l for l in lines2 if l not in lines1]),
            "lines_removed": len([l for l in lines1 if l not in lines2]),
        }
    
    def _cleanup_old_versions(self, file_name: str) -> int:
        """
        Remove old versions beyond max_versions.
        
        Returns:
            Number of versions removed
        """
        versions = self.list_versions(file_name)
        
        if len(versions) <= self.max_versions:
            return 0
        
        # Remove oldest versions
        removed = 0
        versions_to_remove = versions[self.max_versions:]
        
        file_dir = self._get_file_versions_dir(file_name)
        index = self._load_index()
        
        for version_info in versions_to_remove:
            version_id = version_info.version_id
            
            # Remove files
            (file_dir / f"{version_id}.txt").unlink(missing_ok=True)
            (file_dir / f"{version_id}.meta.json").unlink(missing_ok=True)
            
            # Remove from index
            index[file_name] = [
                v for v in index.get(file_name, [])
                if v["version_id"] != version_id
            ]
            removed += 1
        
        self._save_index(index)
        
        return removed
    
    def cleanup_old_versions(self, older_than_days: Optional[int] = None) -> int:
        """
        Cleanup all old versions across all files.
        
        Args:
            older_than_days: Remove versions older than this. Uses MAX_AGE_DAYS if None.
        
        Returns:
            Total number of versions removed
        """
        older_than_days = older_than_days or self.max_age_days
        cutoff = datetime.now().timestamp() - (older_than_days * 86400)
        
        index = self._load_index()
        total_removed = 0
        
        for file_name, versions in index.items():
            file_dir = self._get_file_versions_dir(file_name)
            
            # Find versions to remove
            versions_to_keep = []
            for v in versions:
                version_time = datetime.fromisoformat(v["timestamp"]).timestamp()
                if version_time < cutoff:
                    # Remove this version
                    version_id = v["version_id"]
                    (file_dir / f"{version_id}.txt").unlink(missing_ok=True)
                    (file_dir / f"{version_id}.meta.json").unlink(missing_ok=True)
                    total_removed += 1
                else:
                    versions_to_keep.append(v)
            
            index[file_name] = versions_to_keep
        
        self._save_index(index)
        
        return total_removed
    
    def get_stats(self) -> Dict:
        """Get versioning statistics."""
        index = self._load_index()
        
        total_versions = sum(len(versions) for versions in index.values())
        
        file_stats = {}
        for file_name, versions in index.items():
            file_stats[file_name] = len(versions)
        
        return {
            "total_files": len(index),
            "total_versions": total_versions,
            "max_versions_per_file": self.max_versions,
            "version_dir": str(self.version_dir),
            "version_dir_size_mb": round(
                sum(f.stat().st_size for f in self.version_dir.rglob("*") if f.is_file()) / 1024 / 1024, 2
            ),
            "files": file_stats
        }


# Global instance
versioning = MemoryVersioning()


# ============ CLI Interface ============

if __name__ == "__main__":
    print("Memory Versioning - Rollback Capability")
    print("=" * 50)
    print()
    
    versioner = MemoryVersioning()
    stats = versioner.get_stats()
    
    print("Statistics:")
    print("  Total files: %d" % stats["total_files"])
    print("  Total versions: %d" % stats["total_versions"])
    print("  Storage: %s MB" % stats["version_dir_size_mb"])
    print()
    
    print("Usage:")
    print("  from memory_versioning import versioning")
    print("  versioning.save_version('MEMORY.md', 'content')")
    print("  versions = versioning.list_versions('MEMORY.md')")
    print("  content = versioning.rollback('MEMORY.md', 'v1_abc123')")
