#!/usr/bin/env python3
"""
📚 AUTO LEARNINGS
===============
Automatically extracts learnings from errors and successes
"""

import json
from pathlib import Path
from datetime import datetime

FEEDBACK_FILE = Path("data/feedback_loop.json")
LEARNINGS_DIR = Path("memory/learnings")

def extract_learnings():
    """Extract learnings from feedback"""
    if not FEEDBACK_FILE.exists():
        return []
    
    data = json.load(open(FEEDBACK_FILE))
    learnings = []
    
    # Extract from failures
    for f in data.get("failures", []):
        learnings.append({
            "date": f.get("date"),
            "type": "error",
            "insight": f.get("error", ""),
            "lesson": f.get("lesson", "")
        })
    
    # Extract from successes  
    for s in data.get("successes", []):
        learnings.append({
            "date": s.get("date"),
            "type": "success",
            "insight": s.get("action", ""),
            "lesson": "This approach works!"
        })
    
    return learnings

def save_learnings():
    """Save learnings to memory"""
    learnings = extract_learnings()
    
    if not learnings:
        return "No learnings yet"
    
    # Save to learnings directory
    LEARNINGS_DIR.mkdir(parents=True, exist_ok=True)
    
    for i, learning in enumerate(learnings[-10:]):  # Last 10
        filename = f"learning_{i}.md"
        content = f"""# Learning {i+1}

Date: {learning.get('date', 'N/A')}
Type: {learning.get('type', 'N/A')}

## Insight
{learning.get('insight', '')}

## Lesson
{learning.get('lesson', '')}
"""
        (LEARNINGS_DIR / filename).write_text(content)
    
    return f"Saved {len(learnings[-10:])} learnings"

if __name__ == "__main__":
    result = save_learnings()
    print(f"✅ {result}")
