#!/usr/bin/env python3
"""
🔒 File Locking Wrapper for EmpireHazeClaw
Prevents race conditions on concurrent file writes.

Usage:
    from file_lock import locked_write, locked_read
    
    locked_write("/path/to/file.json", {"data": "value"})
    data = locked_read("/path/to/file.json")
"""

import os
import json
import fcntl
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional

LOCK_DIR = Path("/home/clawbot/.openclaw/workspace/.locks")
LOCK_DIR.mkdir(exist_ok=True)

def _get_lock_path(file_path: str) -> Path:
    """Get corresponding lock file for a given file"""
    safe_name = file_path.replace("/", "_").replace(".", "_")
    return LOCK_DIR / f"{safe_name}.lock"

def locked_write(file_path: str, data: Any, mode: str = "w") -> bool:
    """
    Atomically write data to a file with file locking.
    Uses temp file + rename for atomicity.
    
    Args:
        file_path: Path to file to write
        data: Data to write (will be JSON serialized)
        mode: Write mode ('w' for text, 'wb' for binary)
    
    Returns:
        True if successful, False on error
    """
    lock_path = _get_lock_path(file_path)
    target_path = Path(file_path)
    
    try:
        # Acquire exclusive lock
        with open(lock_path, 'w') as lock_file:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            
            try:
                # Serialize data
                if mode == 'w':
                    content = json.dumps(data, indent=2, ensure_ascii=False)
                    bytes_content = content.encode('utf-8')
                else:
                    bytes_content = data if isinstance(data, bytes) else str(data).encode('utf-8')
                
                # Atomic write: temp file + rename
                temp_path = target_path.with_suffix('.tmp')
                with open(temp_path, 'wb') as f:
                    f.write(bytes_content)
                    f.flush()
                    os.fsync(f.fileno())
                os.rename(temp_path, target_path)
                
                return True
                
            finally:
                # Release lock
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                
    except Exception as e:
        print(f"[FILE_LOCK ERROR] {file_path}: {e}")
        return False

def locked_read(file_path: str, default: Any = None) -> Any:
    """
    Read a file with shared locking.
    
    Args:
        file_path: Path to file to read
        default: Default value if file doesn't exist or can't be read
    
    Returns:
        File contents (JSON parsed if possible), or default
    """
    lock_path = _get_lock_path(file_path)
    target_path = Path(file_path)
    
    if not target_path.exists():
        return default
    
    try:
        # Acquire shared lock
        with open(lock_path, 'w') as lock_file:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_SH)
            
            try:
                with open(target_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Try JSON parse
                try:
                    return json.loads(content)
                except (json.JSONDecodeError, TypeError):
                    return content
                    
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                
    except Exception as e:
        print(f"[FILE_LOCK ERROR] Read {file_path}: {e}")
        return default

def locked_append(file_path: str, line: str) -> bool:
    """
    Append a line to a file with locking.
    
    Args:
        file_path: Path to file
        line: Line to append (will have newline added)
    
    Returns:
        True if successful, False on error
    """
    lock_path = _get_lock_path(file_path)
    target_path = Path(file_path)
    
    try:
        with open(lock_path, 'w') as lock_file:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            
            try:
                with open(target_path, 'a', encoding='utf-8') as f:
                    f.write(line + '\n')
                    f.flush()
                    os.fsync(f.fileno())
                return True
                
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                
    except Exception as e:
        print(f"[FILE_LOCK ERROR] Append {file_path}: {e}")
        return False

def is_locked(file_path: str) -> bool:
    """Check if a file is currently locked by another process"""
    lock_path = _get_lock_path(file_path)
    
    if not lock_path.exists():
        return False
    
    try:
        with open(lock_path, 'w') as lock_file:
            # Try non-blocking exclusive lock
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            return False  # Not locked
    except BlockingIOError:
        return True  # Currently locked
    except Exception:
        return False
