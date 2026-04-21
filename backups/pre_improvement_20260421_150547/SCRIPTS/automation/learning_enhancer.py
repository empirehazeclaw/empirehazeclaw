#!/usr/bin/env python3
"""
🦞 Sir HazeClaw — Learning Enhancer Skill
Analysiert Learning Loop Performance und schlägt Verbesserungen vor

Usage:
    python3 learning_enhancer.py          # Analyze + suggest
    python3 learning_enhancer.py --fix    # Apply suggested improvements
"""

import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
DATA_DIR = WORKSPACE.parent / "data"
LOG_FILE = WORKSPACE.parent / "logs" / "learning_enhancer.log"
EVENT_BUS = WORKSPACE.parent / "scripts" / "event_bus.py"

def log(msg: str, level: str = "INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] [{level}] {msg}\n")

def publish_event(event_type: str, data: dict):
    """Publish event to Event Bus."""
    import subprocess
    try:
        cmd = [
            "python3", str(EVENT_BUS),
            "publish",
            "--type", event_type,
            "--source", "learning_enhancer",
            "--data", json.dumps(data)
        ]
        subprocess.run(cmd, capture_output=True, timeout=5)
    except Exception:
        pass  # Non-critical if event bus fails

def get_learning_state() -> dict:
    """Hole aktuellen Learning Loop State."""
    # Check reflection store
    reflection_file = DATA_DIR / "reflection_store.json"
    if reflection_file.exists():
        data = json.loads(reflection_file.read_text())
        reflections = data.get("reflections", [])
        
        by_type = {}
        for r in reflections:
            t = r.get("task_type", "unknown")
            by_type[t] = by_type.get(t, 0) + 1
        
        return {
            "total_reflections": len(reflections),
            "by_type": by_type,
            "resolved": sum(1 for r in reflections if r.get("resolved")),
            "last_update": data.get("last_update", "unknown")
        }
    return {"total_reflections": 0, "by_type": {}, "resolved": 0}

def analyze_gaps(state: dict) -> list:
    """Analysiere Lücken im Learning."""
    suggestions = []
    
    # Gap 1: Few learning_loop reflections
    ll_refs = state.get("by_type", {}).get("learning_loop", 0)
    if ll_refs < 5:
        suggestions.append({
            "type": "reflection_gap",
            "priority": "HIGH",
            "issue": f"Nur {ll_refs} learning_loop reflections — mehr Patterns nötig",
            "fix": "Reflection Engine nach Validation Failures besser nutzen"
        })
    
    # Gap 2: No resolved reflections
    resolved = state.get("resolved", 0)
    if resolved == 0 and state.get("total_reflections", 0) > 10:
        suggestions.append({
            "type": "resolution_gap",
            "priority": "MEDIUM",
            "issue": "0/{} reflections resolved — kein Feedback Loop",
            "fix": "Resolved-Flag setzen wenn Issue behoben"
        })
    
    # Gap 3: Imbalance in reflection types
    types = state.get("by_type", {})
    if len(types) < 3:
        suggestions.append({
            "type": "diversity_gap",
            "priority": "MEDIUM",
            "issue": f"Nur {len(types)} reflection types — wenig variety",
            "fix": "Mehr verschiedene Task-Typen reflektieren"
        })
    
    return suggestions

def main():
    log("Learning Enhancer START")
    
    state = get_learning_state()
    
    print("🎯 Learning Enhancer — Analysis")
    print("=" * 50)
    print(f"📊 Total Reflections: {state['total_reflections']}")
    print(f"✅ Resolved: {state['resolved']}")
    print(f"📈 By Type: {state['by_type']}")
    print()
    
    suggestions = analyze_gaps(state)
    
    if suggestions:
        print(f"⚠️ {len(suggestions)} Gap(s) gefunden:")
        for s in suggestions:
            emoji = "🔴" if s["priority"] == "HIGH" else "🟡"
            print(f"   {emoji} {s['type']}: {s['issue']}")
            print(f"      → Fix: {s['fix']}")
            print()
        # Publish gap event
        publish_event("learning_gap_detected", {
            "gaps": suggestions,
            "total_reflections": state['total_reflections'],
            "resolved": state['resolved']
        })
    else:
        print("✅ Keine Gaps gefunden — Learning Loop ist gesund!")
        # Publish healthy event
        publish_event("learning_healthy", {
            "total_reflections": state['total_reflections'],
            "resolved": state['resolved'],
            "by_type": state['by_type']
        })
    
    log(f"Learning Enhancer END: {len(suggestions)} gaps")
    return 0

if __name__ == "__main__":
    sys.exit(main())