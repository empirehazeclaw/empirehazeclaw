#!/usr/bin/env python3
"""
📊 Skills Fitness Tracker — Sir HazeClaw
Tracks which skills are actually used and which are dead weight.

Goals:
1. Track skill usage frequency
2. Identify dead/unused skills
3. Suggest skill consolidation
4. Feed insights to Learning Loop

Usage:
    python3 skills_fitness_tracker.py      # Analyze usage
    python3 skills_fitness_tracker.py --fix   # Archive unused skills
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SKILLS_DIR = WORKSPACE / "skills"
LOG_FILE = WORKSPACE / "logs/skills_fitness.log"
STATE_FILE = WORKSPACE / "data/skills_fitness_state.json"

# Dead skill: not used in last 30 days
DEAD_THRESHOLD_DAYS = 30

def log(msg: str, level: str = "INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_state() -> Dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_run": None, "usage": {}, "dead_skills": []}

def save_state(state: Dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_skills() -> List[Dict]:
    """Get all skills with metadata."""
    skills = []
    
    if not SKILLS_DIR.exists():
        return skills
    
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        
        skill = {
            "id": skill_dir.name,
            "path": str(skill_dir),
            "files": []
        }
        
        # Get skill files
        for f in skill_dir.rglob("*"):
            if f.is_file():
                skill["files"].append(f.name)
        
        # Check for metadata
        meta_file = skill_dir / "_meta.json"
        if meta_file.exists():
            with open(meta_file) as f:
                skill["meta"] = json.load(f)
        
        # Check last modified
        mtime = datetime.fromtimestamp(skill_dir.stat().st_mtime)
        skill["last_modified"] = mtime.isoformat()
        skill["days_since_modified"] = (datetime.now() - mtime).days
        
        skills.append(skill)
    
    return skills

def get_usage_from_commands() -> Dict[str, int]:
    """Parse command logs to estimate skill usage."""
    usage = {}
    
    commands_log = WORKSPACE / "logs/commands.log"
    if commands_log.exists():
        with open(commands_log) as f:
            content = f.read()
        
        # Count skill mentions
        for skill_dir in SKILLS_DIR.iterdir():
            if skill_dir.is_dir():
                skill_name = skill_dir.name
                count = content.count(skill_name.lower())
                if count > 0:
                    usage[skill_name] = count
    
    return usage

def analyze_skills(skills: List[Dict], usage: Dict[str, int]) -> Dict:
    """Analyze skills and determine fitness."""
    analysis = []
    
    for skill in skills:
        skill_id = skill["id"]
        files_count = len(skill.get("files", []))
        last_modified = skill.get("days_since_modified", 999)
        usage_count = usage.get(skill_id, 0)
        
        # Fitness scoring
        score = 1.0
        
        # Penalize for being old and unused
        if last_modified > 90:
            score -= 0.3
        elif last_modified > 30:
            score -= 0.1
        
        # Penalize for no usage
        if usage_count == 0 and last_modified > 30:
            score -= 0.4
        
        # Boost for having good structure
        if files_count >= 3:
            score += 0.1
        
        analysis.append({
            "id": skill_id,
            "score": max(0.0, min(1.0, score)),
            "files": files_count,
            "days_since_modified": last_modified,
            "usage_estimate": usage_count,
            "status": "dead" if score < 0.3 else "alive"
        })
    
    return analysis

def main():
    log("=== Skills Fitness Tracker ===")
    
    # Get all skills
    skills = get_skills()
    log(f"Found {len(skills)} skills")
    
    # Get usage estimates
    usage = get_usage_from_commands()
    
    # Analyze
    analysis = analyze_skills(skills, usage)
    
    # Sort by score
    analysis.sort(key=lambda x: x["score"])
    
    # Output
    dead = [a for a in analysis if a["status"] == "dead"]
    alive = [a for a in analysis if a["status"] != "dead"]
    
    log(f"Fitness breakdown: {len(alive)} alive, {len(dead)} dead/unused")
    
    if dead:
        log("Dead skills:")
        for a in dead:
            log(f"  - {a['id']}: score={a['score']:.2f}, {a['days_since_modified']} days old")
    
    # Top performers
    log("Top 5 skills:")
    for a in analysis[-5:]:
        log(f"  - {a['id']}: score={a['score']:.2f}")
    
    # Save state
    state = load_state()
    state["last_run"] = datetime.now().isoformat()
    state["skills_count"] = len(skills)
    state["alive"] = len(alive)
    state["dead"] = len(dead)
    state["analysis"] = analysis
    save_state(state)
    
    # Suggestions
    if dead:
        log(f"Consider archiving {len(dead)} dead skills to reduce noise")
    
    return len(dead)

if __name__ == "__main__":
    main()
