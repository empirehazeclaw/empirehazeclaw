#!/usr/bin/env python3
"""
Sir HazeClaw Skill Loader
Loads skills on-demand to reduce token usage.

Based on Hermes Agent Pattern: Skill-on-Demand Loading
Goal: 46% token reduction through selective skill loading

Usage:
    from skill_loader import load_skill
    skill = load_skill('coding')
    result = skill.main(task)
"""

import importlib.util
import sys
from pathlib import Path
from typing import Optional, Callable, Any

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SKILLS_DIR = WORKSPACE / "skills"

# Skill cache to avoid reloading
_skill_cache = {}

def load_skill(skill_name: str, force_reload: bool = False) -> Optional[Any]:
    """
    Load a skill on-demand.
    
    Args:
        skill_name: Name of skill directory (e.g., 'coding', 'research')
        force_reload: If True, reload even if cached
    
    Returns:
        Module if skill exists and loads, None otherwise
    """
    global _skill_cache
    
    # Check cache first
    if not force_reload and skill_name in _skill_cache:
        return _skill_cache[skill_name]
    
    # Build paths
    skill_path = SKILLS_DIR / skill_name
    
    if not skill_path.exists():
        print(f"⚠️ Skill '{skill_name}' not found at {skill_path}")
        return None
    
    # Try to load index.py
    index_path = skill_path / "index.py"
    if not index_path.exists():
        # Try SKILL.md only (documentation skill)
        skill_md = skill_path / "SKILL.md"
        if skill_md.exists():
            print(f"📚 Skill '{skill_name}' is documentation-only")
            return None
        print(f"⚠️ Skill '{skill_name}' has no index.py")
        return None
    
    # Load module
    try:
        spec = importlib.util.spec_from_file_location(f"skill_{skill_name}", index_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"skill_{skill_name}"] = module
        spec.loader.exec_module(module)
        
        # Cache it
        _skill_cache[skill_name] = module
        
        print(f"✅ Skill '{skill_name}' loaded")
        return module
        
    except Exception as e:
        print(f"❌ Failed to load skill '{skill_name}': {e}")
        return None

def get_skill_function(skill_name: str, function_name: str = "main") -> Optional[Callable]:
    """
    Load a skill and get a specific function.
    
    Args:
        skill_name: Name of skill
        function_name: Name of function to get (default: 'main')
    
    Returns:
        Function if exists, None otherwise
    """
    module = load_skill(skill_name)
    if module is None:
        return None
    
    if hasattr(module, function_name):
        return getattr(module, function_name)
    
    print(f"⚠️ Function '{function_name}' not found in skill '{skill_name}'")
    return None

def list_skills() -> list:
    """List all available skills."""
    if not SKILLS_DIR.exists():
        return []
    
    skills = []
    for item in SKILLS_DIR.iterdir():
        if item.is_dir() and not item.name.startswith('_'):
            skills.append(item.name)
    
    return sorted(skills)

def show_skill_status():
    """Show status of all skills."""
    print("📦 **Skill Status**")
    print()
    
    skills = list_skills()
    print(f"Total Skills: {len(skills)}")
    print()
    
    loaded = list(_skill_cache.keys())
    print(f"Loaded: {len(loaded)}")
    for s in loaded:
        print(f"  ✅ {s}")
    
    unloaded = [s for s in skills if s not in loaded]
    if unloaded:
        print(f"Unloaded: {len(unloaded)}")
        for s in unloaded:
            print(f"  ⚪ {s}")

def main():
    """Show skill status."""
    show_skill_status()
    return 0

if __name__ == "__main__":
    sys.exit(main())
