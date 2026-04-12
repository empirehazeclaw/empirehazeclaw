#!/usr/bin/env python3
"""
memory_audit.py — Memory Audit Log
==================================
Logs ALL memory modifications for security and compliance.

Tracks:
- Who/what made changes
- When changes were made
- What was changed
- Verification of changes

Usage:
    from memory_audit import MemoryAudit, audit_log
    
    audit = MemoryAudit()
    audit.log_write(file='MEMORY.md', content='...', user='user_123')
    audit.log_read(file='MEMORY.md', user='user_123')
    
    # Get audit trail
    trail = audit.get_trail(file='MEMORY.md', limit=50)
"""

import json
import hashlib
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

AUDIT_LOG_FILE = Path("/home/clawbot/.openclaw/workspace/logs/memory_audit.jsonl")


class MemoryAudit:
    """
    Memory Audit Logger - tracks all memory modifications.
    
    Provides:
    - Complete audit trail of memory operations
    - Change verification (hash comparison)
    - Searchable log
    - Export capabilities
    """
    
    def __init__(self, audit_file: Optional[str] = None):
        self.audit_file = Path(audit_file) if audit_file else AUDIT_LOG_FILE
        self.audit_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _compute_hash(self, content: str) -> str:
        """Compute SHA256 hash of content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
    
    def log_write(
        self,
        file: str,
        content: str,
        user: str = "system",
        operation: str = "write",
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Log a memory write operation.
        
        Returns:
            Audit entry with hash
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "file": file,
            "user": user,
            "content_hash": self._compute_hash(content),
            "content_length": len(content),
            "action": "memory_write",
            "verified": True,
        }
        
        if metadata:
            entry["metadata"] = metadata
        
        # Append to audit log
        self._append_entry(entry)
        
        return entry
    
    def log_read(
        self,
        file: str,
        user: str = "system",
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Log a memory read operation."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": "read",
            "file": file,
            "user": user,
            "action": "memory_read",
        }
        
        if metadata:
            entry["metadata"] = metadata
        
        self._append_entry(entry)
        
        return entry
    
    def log_delete(
        self,
        file: str,
        user: str = "system",
        reason: str = "",
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Log a memory delete operation."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": "delete",
            "file": file,
            "user": user,
            "reason": reason,
            "action": "memory_delete",
        }
        
        if metadata:
            entry["metadata"] = metadata
        
        self._append_entry(entry)
        
        return entry
    
    def log_access(
        self,
        file: str,
        access_type: str,  # "read", "write", "delete", "search"
        user: str = "system",
        details: Optional[Dict] = None
    ) -> Dict:
        """Generic access logging."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": access_type,
            "file": file,
            "user": user,
            "action": f"memory_{access_type}",
        }
        
        if details:
            entry["details"] = details
        
        self._append_entry(entry)
        
        return entry
    
    def verify_integrity(
        self,
        file: str,
        current_content: str
    ) -> Dict:
        """
        Verify memory integrity against last known state.
        
        Returns:
            Dict with verification result and last known hash
        """
        # Get last write entry for this file
        last_write = self._get_last_write(file)
        
        if not last_write:
            return {
                "file": file,
                "verified": False,
                "reason": "No previous write found",
                "last_write": None
            }
        
        current_hash = self._compute_hash(current_content)
        expected_hash = last_write.get("content_hash")
        
        return {
            "file": file,
            "verified": current_hash == expected_hash,
            "current_hash": current_hash,
            "expected_hash": expected_hash,
            "last_write": last_write.get("timestamp"),
            "modified_since": last_write.get("timestamp")
        }
    
    def get_trail(
        self,
        file: Optional[str] = None,
        user: Optional[str] = None,
        operation: Optional[str] = None,
        limit: int = 100,
        since: Optional[str] = None
    ) -> List[Dict]:
        """
        Get audit trail with optional filters.
        
        Args:
            file: Filter by file name
            user: Filter by user
            operation: Filter by operation type
            limit: Maximum entries to return
            since: ISO timestamp to filter from
        """
        entries = []
        
        if not self.audit_file.exists():
            return entries
        
        with open(self.audit_file) as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    
                    # Apply filters
                    if file and entry.get("file") != file:
                        continue
                    if user and entry.get("user") != user:
                        continue
                    if operation and entry.get("operation") != operation:
                        continue
                    if since and entry.get("timestamp", "") < since:
                        continue
                    
                    entries.append(entry)
                    
                    if len(entries) >= limit:
                        break
                        
                except json.JSONDecodeError:
                    continue
        
        # Return most recent first
        return list(reversed(entries))
    
    def get_stats(self) -> Dict:
        """Get audit log statistics."""
        if not self.audit_file.exists():
            return {
                "total_entries": 0,
                "file_size_kb": 0,
                "oldest_entry": None,
                "newest_entry": None,
                "by_operation": {},
            }
        
        entries = self.get_trail(limit=100000)
        
        by_operation = {}
        for entry in entries:
            op = entry.get("operation", "unknown")
            by_operation[op] = by_operation.get(op, 0) + 1
        
        return {
            "total_entries": len(entries),
            "file_size_kb": round(self.audit_file.stat().st_size / 1024, 2),
            "oldest_entry": entries[0].get("timestamp") if entries else None,
            "newest_entry": entries[-1].get("timestamp") if entries else None,
            "by_operation": by_operation,
        }
    
    def _append_entry(self, entry: Dict) -> None:
        """Append entry to audit log file."""
        with open(self.audit_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def _get_last_write(self, file: str) -> Optional[Dict]:
        """Get the last write entry for a file."""
        entries = self.get_trail(file=file, operation="write", limit=1)
        return entries[0] if entries else None
    
    def export_trail(self, output_file: str, **filters) -> int:
        """
        Export audit trail to a file.
        
        Returns:
            Number of entries exported
        """
        entries = self.get_trail(**filters, limit=100000)
        
        with open(output_file, "w") as f:
            json.dump(entries, f, indent=2)
        
        return len(entries)
    
    def clear_old_entries(self, older_than_days: int = 30) -> int:
        """
        Clear audit entries older than specified days.
        
        Returns:
            Number of entries removed
        """
        if not self.audit_file.exists():
            return 0
        
        cutoff = datetime.now().timestamp() - (older_than_days * 86400)
        cutoff_iso = datetime.fromtimestamp(cutoff).isoformat()
        
        # Read all entries
        with open(self.audit_file) as f:
            all_entries = [json.loads(line) for line in f if line.strip()]
        
        # Filter to keep only recent
        recent_entries = [
            entry for entry in all_entries
            if entry.get("timestamp", "") >= cutoff_iso
        ]
        
        removed = len(all_entries) - len(recent_entries)
        
        # Write back
        with open(self.audit_file, "w") as f:
            for entry in recent_entries:
                f.write(json.dumps(entry) + "\n")
        
        return removed


# Global instance
audit_log = MemoryAudit()


# ============ CLI Interface ============

if __name__ == "__main__":
    import sys
    
    print("Memory Audit Log - Security Tracking")
    print("=" * 50)
    print()
    
    audit = MemoryAudit()
    stats = audit.get_stats()
    
    print("Statistics:")
    print("  Total entries: %d" % stats["total_entries"])
    print("  File size: %s KB" % stats["file_size_kb"])
    print("  Oldest: %s" % (stats["oldest_entry"] or "N/A"))
    print("  Newest: %s" % (stats["newest_entry"] or "N/A"))
    print()
    
    if stats["by_operation"]:
        print("By Operation:")
        for op, count in stats["by_operation"].items():
            print("  %s: %d" % (op, count))
    
    print()
    print("Usage:")
    print("  from memory_audit import audit_log")
    print("  audit_log.log_write(file='MEMORY.md', content='...')")
    print("  audit_log.log_read(file='MEMORY.md')")
    print("  trail = audit_log.get_trail(file='MEMORY.md')")
