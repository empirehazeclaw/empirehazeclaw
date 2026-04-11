#!/usr/bin/env python3
"""
memory_isolation.py — Memory Isolation Layer
===========================================
Ensures proper isolation between different memory domains.

Purpose:
- USER.md memory = private to specific user context
- SHARED memory = accessible across sessions
- SYSTEM memory = critical configs, never leak
- CEO/Human memory = strictly separated

Usage:
    from memory_isolation import MemoryIsolation, get_memory_scope
    
    iso = MemoryIsolation()
    
    # Check if content should be accessible
    if iso.can_access('MEMORY.md', 'shared_session'):
        read_memory()
    else:
        print("ACCESS DENIED - wrong scope")
"""

import re
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum


class MemoryScope(Enum):
    """Memory scope levels."""
    PRIVATE = "private"      # Only for specific user
    SHARED = "shared"         # Shared across sessions
    SYSTEM = "system"         # Critical configs, never leak
    PUBLIC = "public"         # Safe to share externally


@dataclass
class IsolationRule:
    """Rule for memory isolation."""
    scope: MemoryScope
    file_patterns: List[str]
    directories: List[str]
    description: str


@dataclass
class AccessContext:
    """Context for memory access."""
    session_type: str         # "user", "shared", "system", "api"
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    channels: Set[str] = field(default_factory=set)  # telegram, discord, etc.
    is_elevated: bool = False  # Has admin/sudo privileges


class MemoryIsolation:
    """
    Memory Isolation Layer - prevents memory cross-contamination.
    
    Isolation domains:
    - PRIVATE: User-specific memory (USER.md, personal notes)
    - SHARED: Cross-session memory (shared/, kg_summary.md)
    - SYSTEM: Critical configs (.vault-key, gateway config)
    - PUBLIC: Safe to share (docs/, public notes)
    
    Rules:
    1. PRIVATE memory cannot be accessed by SHARED sessions
    2. SYSTEM memory requires elevated privileges
    3. SHARED memory cannot contain PRIVATE user data
    4. Cross-user memory must go through sanitization
    """
    
    # Default isolation rules
    RULES = [
        IsolationRule(
            scope=MemoryScope.SYSTEM,
            file_patterns=[
                r"\.vault-key$",
                r"\.env$",
                r"password",
                r"credential",
                r"api.?key",
                r"token",
            ],
            directories=[
                "/gateway/config",
                "/.workspace/.env",
            ],
            description="Critical secrets - no access without elevation"
        ),
        IsolationRule(
            scope=MemoryScope.PRIVATE,
            file_patterns=[
                r"USER\.md$",
                r"todo-tomorrow\.md$",
                r"/personal/",
                r"/private/",
            ],
            directories=[
                "memory/personal",
                "memory/private",
                "memory/.dreams",
            ],
            description="User-private memory - only owner session"
        ),
        IsolationRule(
            scope=MemoryScope.SHARED,
            file_patterns=[
                r"shared/",
                r"SHARED_MEMORY",
                r"kg_summary\.md",
                r"research\.md",
                r"builder\.md",
            ],
            directories=[
                "shared/",
                "memory/shared/",
            ],
            description="Shared memory - accessible to all sessions"
        ),
        IsolationRule(
            scope=MemoryScope.PUBLIC,
            file_patterns=[
                r"docs/",
                r"docs/patterns/",
                r"skills/",
                r"STRUCTURE",
                r"README",
            ],
            directories=[
                "docs/",
                "skills/",
                "scripts/",
            ],
            description="Public resources - safe to share"
        ),
    ]
    
    # Forbidden patterns in shared memory (private data leaks)
    FORBIDDEN_IN_SHARED = [
        r"password\s*[=:]\s*\S+",
        r"api[_-]?key\s*[=:]\s*\S+",
        r"token\s*[=:]\s*\S+",
        r"secret\s*[=:]\s*\S+",
        r"ssn\s*[=:]\s*\S+",
        r"credit.?card\s*[=:]\s*\S+",
        r"phone\s*[=:]\s*\S+",
        r"email\s*[=:]\s*\S+@",
        r"\b5392634979\b",  # Nico's user ID - example
    ]
    
    def __init__(self, rules: Optional[List[IsolationRule]] = None):
        self.rules = rules or self.RULES
    
    def classify_file(self, file_path: str) -> MemoryScope:
        """
        Classify a file's memory scope.
        
        Returns:
            MemoryScope enum value
        """
        path = Path(file_path)
        path_str = str(path)
        name = path.name
        
        # Check rules in order (most restrictive first)
        for rule in self.RULES:
            # Check file patterns
            for pattern in rule.file_patterns:
                if re.search(pattern, name, re.IGNORECASE):
                    return rule.scope
            
            # Check directories
            for dir_pattern in rule.directories:
                if dir_pattern in path_str:
                    return rule.scope
        
        # Default to SHARED for memory files
        if "memory" in path_str:
            return MemoryScope.SHARED
        
        # Default to PUBLIC for docs
        if "docs" in path_str or "scripts" in path_str:
            return MemoryScope.PUBLIC
        
        return MemoryScope.SHARED  # Safe default
    
    def can_access(
        self,
        file_path: str,
        context: AccessContext
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if a context can access a file.
        
        Returns:
            (can_access, reason_if_denied)
        """
        scope = self.classify_file(file_path)
        
        # SYSTEM scope requires elevation
        if scope == MemoryScope.SYSTEM:
            if not context.is_elevated:
                return False, f"SYSTEM scope requires elevated privileges"
            return True, None
        
        # PRIVATE scope requires matching user/session
        if scope == MemoryScope.PRIVATE:
            if context.session_type == "shared":
                return False, "PRIVATE memory cannot be accessed from SHARED session"
            if context.session_type == "user" and context.session_id:
                # User can access their own private memory
                # (in real impl, would verify session owns this file)
                return True, None
            return True, None  # System sessions can access
        
        # SHARED and PUBLIC are always accessible
        return True, None
    
    def validate_shared_content(
        self,
        content: str,
        context: AccessContext
    ) -> Tuple[bool, List[str]]:
        """
        Validate that shared content doesn't contain private data.
        
        Returns:
            (is_valid, list_of_violations)
        """
        violations = []
        
        for pattern in self.FORBIDDEN_IN_SHARED:
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(f"Private data pattern found: {pattern}")
        
        return len(violations) == 0, violations
    
    def suggest_scope(
        self,
        file_path: str,
        content: str
    ) -> MemoryScope:
        """
        Suggest appropriate scope based on content analysis.
        
        Returns:
            Recommended MemoryScope
        """
        path = Path(file_path)
        
        # Check for sensitive patterns
        for pattern in self.FORBIDDEN_IN_SHARED:
            if re.search(pattern, content, re.IGNORECASE):
                # Contains sensitive data - should be private or system
                if any(s in str(path).lower() for s in ["key", "credential", "password", "secret"]):
                    return MemoryScope.SYSTEM
                return MemoryScope.PRIVATE
        
        # Check location hints
        if "/personal/" in str(path) or "/private/" in str(path):
            return MemoryScope.PRIVATE
        
        if "/shared/" in str(path) or "shared_memory" in path.name.lower():
            return MemoryScope.SHARED
        
        # Default based on path
        return self.classify_file(file_path)
    
    def get_accessible_scopes(self, context: AccessContext) -> Set[MemoryScope]:
        """
        Get scopes accessible to a given context.
        
        Returns:
            Set of accessible MemoryScope values
        """
        scopes = {MemoryScope.PUBLIC}  # Everyone can access public
        
        if context.session_type != "api":  # API has limited access
            scopes.add(MemoryScope.SHARED)
        
        if context.session_type in ["user", "system"]:
            scopes.add(MemoryScope.PRIVATE)
        
        if context.is_elevated:
            scopes.add(MemoryScope.SYSTEM)
        
        return scopes
    
    def check_isolation(self, context: AccessContext) -> Dict:
        """
        Check isolation status for a context.
        
        Returns:
            Dict with isolation analysis
        """
        accessible = self.get_accessible_scopes(context)
        
        return {
            "context": {
                "session_type": context.session_type,
                "session_id": context.session_id,
                "is_elevated": context.is_elevated,
            },
            "accessible_scopes": [s.value for s in accessible],
            "can_access_system": MemoryScope.SYSTEM in accessible,
            "can_access_private": MemoryScope.PRIVATE in accessible,
            "isolation_score": len(accessible) / 4,  # 0.0 (max isolation) to 1.0 (full access)
        }


# Convenience functions
def get_memory_scope(file_path: str) -> str:
    """Quick scope classification."""
    iso = MemoryIsolation()
    return iso.classify_file(file_path).value


def can_access_memory(file_path: str, session_type: str = "shared") -> bool:
    """Quick access check."""
    iso = MemoryIsolation()
    context = AccessContext(session_type=session_type)
    allowed, _ = iso.can_access(file_path, context)
    return allowed


# ============ CLI Interface ============

if __name__ == "__main__":
    print("Memory Isolation Layer")
    print("=" * 50)
    print()
    
    iso = MemoryIsolation()
    
    # Test classification
    test_files = [
        "/workspace/MEMORY.md",
        "/workspace/memory/2026-04-11.md",
        "/workspace/shared/memory/kg_summary.md",
        "/workspace/.env",
        "/workspace/.vault-key",
        "/workspace/USER.md",
        "/workspace/docs/README.md",
        "/workspace/skills/INDEX.md",
    ]
    
    print("File Classification:")
    for f in test_files:
        scope = iso.classify_file(f)
        print(f"  {scope.value:8} | {f}")
    
    print()
    print("Context Analysis:")
    
    # Test different contexts
    for session_type in ["user", "shared", "api", "system"]:
        context = AccessContext(
            session_type=session_type,
            is_elevated=(session_type == "system")
        )
        check = iso.check_isolation(context)
        print(f"  {session_type:8}: scopes={check['accessible_scopes']}, isolation={check['isolation_score']:.2f}")
    
    print()
    print("Usage:")
    print("  from memory_isolation import MemoryIsolation")
    print("  iso = MemoryIsolation()")
    print("  scope = iso.classify_file('memory/2026-04-11.md')")
    print("  allowed, reason = iso.can_access(file, context)")
