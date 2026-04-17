#!/usr/bin/env python3
"""
Core Utils — Sir HazeClaw Common Library
==========================================
Shared utilities used across multiple scripts.

Usage:
    from lib.core_utils import load_json, save_json, get_workspace
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional

WORKSPACE = Path('/home/clawbot/.openclaw/workspace')
DATA_DIR = WORKSPACE / 'data'

def load_json(path: Path) -> Dict:
    """Load JSON file."""
    with open(path) as f:
        return json.load(f)

def save_json(path: Path, data: Any) -> None:
    """Save JSON file."""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def get_workspace() -> Path:
    """Get workspace path."""
    return WORKSPACE

def get_data_dir() -> Path:
    """Get data directory path."""
    return DATA_DIR

def timestamp_now() -> str:
    """Get current UTC timestamp."""
    return datetime.utcnow().isoformat() + 'Z'

def safe_get(d: Dict, *keys, default=None) -> Any:
    """Safely get nested dict value."""
    for key in keys:
        try:
            d = d[key]
        except (KeyError, TypeError, IndexError):
            return default
    return d
