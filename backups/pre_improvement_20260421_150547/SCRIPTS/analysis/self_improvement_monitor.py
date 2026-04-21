#!/usr/bin/env python3
"""
self_improvement_monitor.py — Monitors Self-Improvement Progress
Sir HazeClaw - 2026-04-11

Usage:
    python3 self_improvement_monitor.py
"""

import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SKILLS_DIR = WORKSPACE / "skills" / "_library"
METRICS_FILE = WORKSPACE / "memory" / "session_metrics_history.json"

def get_skill_count():
    """Count available skills."""
    if SKILLS_DIR.exists():
        return len(list(SKILLS_DIR.glob("*.md")))
    return 0

def get_session_trend():
    """Analyze session metrics trend."""
    if METRICS_FILE.exists():
        with open(METRICS_FILE) as f:
            data = json.load(f)
        
        history = data.get("history", [])
        if len(history) >= 2:
            recent = history[-1]
            prev = history[-2]
            return {
                "error_rate": recent.get("error_rate", 0),
                "prev_error_rate": prev.get("error_rate", 0),
                "sessions": recent.get("sessions", 0),
                "friction": recent.get("friction", 0)
            }
    return None

def get_kg_count():
    """Count KG entities."""
    kg_path = WORKSPACE / "core_ultralight" / "memory" / "knowledge_graph.json"
    if kg_path.exists():
        with open(kg_path) as f:
            kg = json.load(f)
        return len(kg.get("entities", {}))
    return 0

def main():
    print("📊 SELF-IMPROVEMENT MONITOR")
    print("=" * 50)
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print()
    
    # Skills
    skills = get_skill_count()
    target_skills = 20
    skill_pct = min(100, (skills / target_skills) * 100)
    print(f"📚 Skills: {skills}/{target_skills} ({skill_pct:.0f}%)")
    print(f"   █{'█' * int(skill_pct / 10)}{'░' * (10 - int(skill_pct / 10))}")
    
    # Error Rate
    trend = get_session_trend()
    if trend:
        er = trend["error_rate"]
        target_er = 15
        if er <= target_er:
            print(f"📈 Error Rate: {er}% ✅ TARGET!")
        else:
            gap = er - target_er
            print(f"📈 Error Rate: {er}% (Target: {target_er}%, Gap: {gap}%)")
    else:
        print("📈 Error Rate: N/A")
    
    # Sessions
    if trend:
        print(f"📊 Sessions (today): {trend['sessions']}")
        print(f"🔄 Friction Events: {trend['friction']}")
    
    # KG
    kg = get_kg_count()
    target_kg = 250
    kg_pct = min(100, (kg / target_kg) * 100)
    print(f"🧠 KG Entities: {kg}/{target_kg} ({kg_pct:.0f}%)")
    print(f"   █{'█' * int(kg_pct / 10)}{'░' * (10 - int(kg_pct / 10))}")
    
    print()
    print("=" * 50)
    print("🎯 PHASE STATUS:")
    
    # Phase 1
    phase1_done = skills >= 15 and trend and trend["error_rate"] <= 20
    print(f"   Phase 1 (Error < 20%): {'✅' if phase1_done else '⚠️'}")
    
    # Phase 2
    phase2_done = trend and trend["error_rate"] <= 15
    print(f"   Phase 2 (Error < 15%): {'✅' if phase2_done else '⚠️'}")
    
    # Phase 3
    phase3_done = trend and trend["error_rate"] <= 10
    print(f"   Phase 3 (Error < 10%): {'✅' if phase3_done else '⚠️'}")
    
    print()
    print("📋 NEXT ACTIONS:")
    if not phase1_done:
        print("   1. Apply timeout handling on long tasks")
        print("   2. Use loop detection before retry")
        print("   3. Verify paths before exec")
    elif not phase2_done:
        print("   1. Continue error reduction efforts")
        print("   2. Track FAS rate")
    else:
        print("   1. Maintain current performance")
        print("   2. Push for < 10% error rate")

if __name__ == "__main__":
    main()
