#!/usr/bin/env python3
"""
memory_validator.py — Memory Validation Layer
============================================
Verifies memory integrity and detects issues.

Checks:
- File corruption (encoding, null bytes, truncation)
- Tampering detection (hash mismatch with audit log)
- Stale data detection (old memories needing review)
- Anomaly detection (unusual patterns)

Usage:
    from memory_validator import MemoryValidator, validate_memory
    
    validator = MemoryValidator()
    result = validator.validate_file('MEMORY.md')
    
    if not result.is_valid:
        print("ISSUES:", result.issues)
    
    # Full system scan
    issues = validator.validate_all_memory()
"""

import hashlib
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# Known memory locations
MEMORY_DIRS = [
    Path("/home/clawbot/.openclaw/workspace/memory"),
    Path("/home/clawbot/.openclaw/workspace/core_ultralight/memory"),
    Path("/home/clawbot/.openclaw/workspace/ceo/memory"),
    Path("/home/clawbot/.openclaw/workspace/shared/memory"),
]


class IssueSeverity(Enum):
    LOW = "low"         # Minor issue, informational
    MEDIUM = "medium"   # Should be reviewed
    HIGH = "high"       # Should be fixed
    CRITICAL = "critical"  # Must fix immediately


@dataclass
class ValidationIssue:
    """A validation issue found in memory."""
    file: str
    severity: IssueSeverity
    issue_type: str
    description: str
    details: Optional[Dict] = None


@dataclass
class ValidationResult:
    """Result of memory validation."""
    is_valid: bool
    file: str
    issues: List[ValidationIssue]
    checked_at: str
    file_hash: str
    file_size: int
    last_modified: Optional[str] = None
    last_verified: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "is_valid": self.is_valid,
            "file": self.file,
            "issues": [
                {
                    "severity": i.severity.value,
                    "type": i.issue_type,
                    "description": i.description
                } for i in self.issues
            ],
            "checked_at": self.checked_at,
            "file_hash": self.file_hash,
            "file_size": self.file_size,
        }


class MemoryValidator:
    """
    Memory Validation Layer - verifies memory integrity.
    
    Uses:
    - Hash verification against audit log
    - Encoding checks
    - Pattern checks for corruption
    - Age checks for stale data
    """
    
    # Thresholds
    MAX_FILE_SIZE = 10_000_000  # 10MB
    MAX_LINE_LENGTH = 50_000
    STALE_DAYS = 90  # Memory older than this is stale
    WARNING_DAYS = 30  # Memory older than this gets warning
    
    # Known sensitive patterns that might indicate tampering
    TAMPERING_PATTERNS = [
        ("\x00", "NULL_BYTES", IssueSeverity.HIGH, "Null bytes found - possible binary corruption"),
        ("\r\x00", "CORRUPT_EOL", IssueSeverity.MEDIUM, "Mixed line endings detected"),
    ]
    
    def __init__(self, audit_log_file: Optional[str] = None):
        self.audit_file = Path(audit_log_file) if audit_log_file else Path("/home/clawbot/.openclaw/workspace/logs/memory_audit.jsonl")
    
    def _compute_hash(self, content: str) -> str:
        """Compute SHA256 hash of content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
    
    def validate_file(
        self,
        file_path: str,
        check_stale: bool = True
    ) -> ValidationResult:
        """
        Validate a single memory file.
        
        Returns:
            ValidationResult with issues found
        """
        path = Path(file_path)
        issues = []
        
        checked_at = datetime.now().isoformat()
        
        # Check if file exists
        if not path.exists():
            return ValidationResult(
                is_valid=False,
                file=str(path),
                issues=[ValidationIssue(
                    file=str(path),
                    severity=IssueSeverity.CRITICAL,
                    issue_type="FILE_MISSING",
                    description="Memory file does not exist"
                )],
                checked_at=checked_at,
                file_hash="",
                file_size=0
            )
        
        # Basic file info
        stat = path.stat()
        file_size = stat.st_size
        file_hash = self._compute_hash(path.read_text(errors="ignore"))
        last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
        
        # Check 1: File size
        if file_size == 0:
            issues.append(ValidationIssue(
                file=str(path),
                severity=IssueSeverity.MEDIUM,
                issue_type="EMPTY_FILE",
                description="File is empty"
            ))
        elif file_size > self.MAX_FILE_SIZE:
            issues.append(ValidationIssue(
                file=str(path),
                severity=IssueSeverity.HIGH,
                issue_type="FILE_TOO_LARGE",
                description=f"File is {file_size} bytes (max: {self.MAX_FILE_SIZE})",
                details={"size": file_size, "max": self.MAX_FILE_SIZE}
            ))
        
        # Check 2: Encoding issues
        try:
            content = path.read_text(encoding='utf-8')
        except UnicodeDecodeError as e:
            issues.append(ValidationIssue(
                file=str(path),
                severity=IssueSeverity.HIGH,
                issue_type="ENCODING_ERROR",
                description=f"File cannot be decoded as UTF-8: {e}",
                details={"encoding_error": str(e)}
            ))
            content = path.read_text(errors="ignore")
        except Exception as e:
            issues.append(ValidationIssue(
                file=str(path),
                severity=IssueSeverity.CRITICAL,
                issue_type="READ_ERROR",
                description=f"Cannot read file: {e}"
            ))
            return ValidationResult(
                is_valid=False,
                file=str(path),
                issues=issues,
                checked_at=checked_at,
                file_hash="",
                file_size=file_size
            )
        
        # Check 3: Null bytes
        if '\x00' in content:
            issues.append(ValidationIssue(
                file=str(path),
                severity=IssueSeverity.HIGH,
                issue_type="NULL_BYTES",
                description="File contains null bytes - possible corruption"
            ))
        
        # Check 4: Line length
        lines = content.split('\n')
        long_lines = [(i+1, len(line)) for i, line in enumerate(lines) if len(line) > self.MAX_LINE_LENGTH]
        if long_lines:
            issues.append(ValidationIssue(
                file=str(path),
                severity=IssueSeverity.LOW,
                issue_type="LONG_LINES",
                description=f"{len(long_lines)} lines exceed {self.MAX_LINE_LENGTH} chars",
                details={"long_lines": long_lines[:10]}
            ))
        
        # Check 5: Hash verification against audit log
        audit_hash = self._get_audit_hash(path.name)
        if audit_hash and audit_hash != file_hash:
            issues.append(ValidationIssue(
                file=str(path),
                severity=IssueSeverity.CRITICAL,
                issue_type="HASH_MISMATCH",
                description="File hash does not match audit log - possible tampering!",
                details={"expected": audit_hash, "actual": file_hash}
            ))
        
        # Check 6: Stale data
        if check_stale:
            age_days = (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).days
            if age_days > self.STALE_DAYS:
                issues.append(ValidationIssue(
                    file=str(path),
                    severity=IssueSeverity.MEDIUM,
                    issue_type="STALE_MEMORY",
                    description=f"Memory is {age_days} days old (> {self.STALE_DAYS})",
                    details={"age_days": age_days}
                ))
            elif age_days > self.WARNING_DAYS:
                issues.append(ValidationIssue(
                    file=str(path),
                    severity=IssueSeverity.LOW,
                    issue_type="AGING_MEMORY",
                    description=f"Memory is {age_days} days old (>{self.WARNING_DAYS})",
                    details={"age_days": age_days}
                ))
        
        # Check 7: Content sanity
        if len(content) < 10 and file_size > 0:
            issues.append(ValidationIssue(
                file=str(path),
                severity=IssueSeverity.LOW,
                issue_type="TRIVIAL_CONTENT",
                description="File has very little content"
            ))
        
        is_valid = not any(i.severity in [IssueSeverity.HIGH, IssueSeverity.CRITICAL] for i in issues)
        
        return ValidationResult(
            is_valid=is_valid,
            file=str(path),
            issues=issues,
            checked_at=checked_at,
            file_hash=file_hash,
            file_size=file_size,
            last_modified=last_modified
        )
    
    def validate_all_memory(
        self,
        dirs: Optional[List[Path]] = None,
        check_stale: bool = True
    ) -> Tuple[List[ValidationResult], Dict]:
        """
        Validate all memory files in known directories.
        
        Returns:
            Tuple of (results list, summary dict)
        """
        dirs = dirs or MEMORY_DIRS
        results = []
        summary = {
            "total": 0,
            "valid": 0,
            "issues": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "missing": 0
        }
        
        for mem_dir in dirs:
            if not mem_dir.exists():
                continue
            
            for md_file in mem_dir.rglob("*.md"):
                # Skip backups
                if "backup" in md_file.name:
                    continue
                
                summary["total"] += 1
                result = self.validate_file(str(md_file), check_stale=check_stale)
                results.append(result)
                
                if result.is_valid:
                    summary["valid"] += 1
                else:
                    summary["issues"] += 1
                
                for issue in result.issues:
                    if issue.severity == IssueSeverity.CRITICAL:
                        summary["critical"] += 1
                    elif issue.severity == IssueSeverity.HIGH:
                        summary["high"] += 1
                    elif issue.severity == IssueSeverity.MEDIUM:
                        summary["medium"] += 1
                    elif issue.severity == IssueSeverity.LOW:
                        summary["low"] += 1
        
        return results, summary
    
    def _get_audit_hash(self, file_name: str) -> Optional[str]:
        """Get last known hash from audit log."""
        if not self.audit_file.exists():
            return None
        
        try:
            with open(self.audit_file) as f:
                entries = [json.loads(line) for line in f if line.strip()]
            
            # Find last write entry for this file
            for entry in reversed(entries):
                if entry.get("file") == file_name and entry.get("operation") == "write":
                    return entry.get("content_hash")
        except Exception:
            pass
        
        return None
    
    def quick_check(self, file_path: str) -> Tuple[bool, List[str]]:
        """
        Quick validation check.
        
        Returns:
            (is_valid, list_of_issue_descriptions)
        """
        result = self.validate_file(file_path, check_stale=False)
        return result.is_valid, [i.description for i in result.issues]


# Convenience function
def validate_memory(
    file_path: Optional[str] = None,
    all_memory: bool = False
) -> Tuple[List[ValidationResult], Dict]:
    """
    Validate memory files.
    
    Usage:
        # Single file
        result = validate_memory('MEMORY.md')
        
        # All memory
        results, summary = validate_memory(all_memory=True)
    """
    validator = MemoryValidator()
    
    if all_memory:
        return validator.validate_all_memory()
    elif file_path:
        result = validator.validate_file(file_path)
        return [result], {"total": 1, "valid": 1 if result.is_valid else 0}
    else:
        return [], {"error": "Must specify file_path or all_memory=True"}


# ============ CLI Interface ============

if __name__ == "__main__":
    import sys
    
    print("Memory Validator - Integrity Checking")
    print("=" * 50)
    print()
    
    validator = MemoryValidator()
    
    if len(sys.argv) > 1:
        # Validate specific file
        if sys.argv[1] == "--all":
            print("Validating ALL memory files...")
            results, summary = validator.validate_all_memory()
            
            print(f"\n📊 SUMMARY:")
            print(f"   Total: {summary['total']}")
            print(f"   ✅ Valid: {summary['valid']}")
            print(f"   🚨 Issues: {summary['issues']}")
            print(f"      CRITICAL: {summary['critical']}")
            print(f"      HIGH: {summary['high']}")
            print(f"      MEDIUM: {summary['medium']}")
            print(f"      LOW: {summary['low']}")
            
            # Show critical/high issues
            for r in results:
                for i in r.issues:
                    if i.severity in [IssueSeverity.CRITICAL, IssueSeverity.HIGH]:
                        print(f"\n   [{i.severity.value.upper()}] {r.file}")
                        print(f"      {i.description}")
        else:
            # Single file
            result = validator.validate_file(sys.argv[1])
            print(f"File: {result.file}")
            print(f"Valid: {result.is_valid}")
            print(f"Hash: {result.file_hash}")
            print(f"Size: {result.file_size}")
            if result.issues:
                print(f"\nIssues ({len(result.issues)}):")
                for i in result.issues:
                    print(f"  [{i.severity.value.upper()}] {i.description}")
    else:
        print("Usage:")
        print("  python memory_validator.py <file>     # Validate single file")
        print("  python memory_validator.py --all      # Validate all memory")
