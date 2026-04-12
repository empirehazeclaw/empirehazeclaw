#!/usr/bin/env python3
"""
skill_metrics.py — Sir HazeClaw Skill Performance Tracking
Trackt Metriken pro Skill und aktualisiert automatisch.

Usage:
    python3 skill_metrics.py              # Zeigt Dashboard
    python3 skill_metrics.py --update    # Updatet Skills basierend auf Metriken
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SKILL_DIR = WORKSPACE / "skills"
METRICS_FILE = WORKSPACE / "memory" / "skill_metrics.json"

def load_metrics() -> dict:
    """Lädt existierende Metriken."""
    if METRICS_FILE.exists():
        with open(METRICS_FILE) as f:
            return json.load(f)
    return {
        "skills": {},
        "daily": {},
        "last_updated": None
    }

def save_metrics(data: dict):
    """Speichert Metriken."""
    data["last_updated"] = datetime.now().isoformat()
    with open(METRICS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def track_skill_use(skill_name: str, success: bool, duration_ms: int = 0):
    """Trackt Nutzung eines Skills."""
    metrics = load_metrics()
    
    if skill_name not in metrics["skills"]:
        metrics["skills"][skill_name] = {
            "uses": 0,
            "successes": 0,
            "failures": 0,
            "total_duration_ms": 0,
            "last_used": None
        }
    
    skill = metrics["skills"][skill_name]
    skill["uses"] += 1
    if success:
        skill["successes"] += 1
    else:
        skill["failures"] += 1
    skill["total_duration_ms"] += duration_ms
    skill["last_used"] = datetime.now().isoformat()
    
    save_metrics(metrics)

def calculate_score(skill: dict) -> float:
    """Berechnet Score für Skill (0-100)."""
    if skill["uses"] == 0:
        return 50  # Neutral
    
    success_rate = skill["successes"] / skill["uses"]
    avg_duration = skill["total_duration_ms"] / skill["uses"] if skill["uses"] > 0 else 0
    
    # Score: 70% success rate, 30% performance
    performance_factor = min(1.0, 30000 / max(avg_duration, 1000))  # 30s = perfect
    
    score = (success_rate * 70) + (performance_factor * 30)
    return round(score, 1)

def get_dashboard() -> str:
    """Generiert Dashboard."""
    metrics = load_metrics()
    
    lines = []
    lines.append("\n📊 SKILL METRICS DASHBOARD")
    lines.append("=" * 60)
    
    if not metrics["skills"]:
        lines.append("Keine Metriken vorhanden.")
        return "\n".join(lines)
    
    # Sort by score
    sorted_skills = sorted(
        metrics["skills"].items(),
        key=lambda x: calculate_score(x[1]),
        reverse=True
    )
    
    for name, data in sorted_skills:
        score = calculate_score(data)
        success_rate = (data["successes"] / data["uses"] * 100) if data["uses"] > 0 else 0
        
        # Score bar
        bar_len = int(score / 10)
        bar = "█" * bar_len + "░" * (10 - bar_len)
        
        emoji = "🟢" if score >= 80 else "🟡" if score >= 50 else "🔴"
        
        lines.append(f"\n{emoji} {name}")
        lines.append(f"   Score: {score}/100 [{bar}]")
        lines.append(f"   Uses: {data['uses']} | Success: {success_rate:.0f}%")
        
        if data["last_used"]:
            lines.append(f"   Last: {data['last_used'][:10]}")
    
    lines.append("\n" + "=" * 60)
    return "\n".join(lines)

def auto_update_skills():
    """Updatet Skills basierend auf Metriken."""
    metrics = load_metrics()
    
    updates = []
    
    for skill_name, data in metrics["skills"].items():
        score = calculate_score(data)
        
        # Low score = needs improvement
        if score < 50 and data["uses"] >= 3:
            # Find skill file
            skill_path = SKILL_DIR / skill_name
            if not skill_path.exists():
                skill_path = SKILL_DIR / f"{skill_name}.md"
            
            if skill_path.exists():
                updates.append({
                    "skill": skill_name,
                    "score": score,
                    "uses": data["uses"],
                    "path": str(skill_path),
                    "recommendation": "Low score - needs review"
                })
    
    return updates

def main():
    if "--update" in sys.argv:
        # Auto-update mode
        updates = auto_update_skills()
        if updates:
            print("\n🔧 SKILL UPDATES:")
            for u in updates:
                print(f"  ⚠️ {u['skill']} (Score: {u['score']}/100)")
                print(f"     Path: {u['path']}")
                print(f"     Recommendation: {u['recommendation']}")
            print(f"\n{len(updates)} Skills brauchen Review.")
        else:
            print("✅ Alle Skills haben gute Scores!")
    else:
        # Dashboard mode
        print(get_dashboard())
        
        # Show recent activity
        metrics = load_metrics()
        if metrics.get("last_updated"):
            print(f"\nZuletzt aktualisiert: {metrics['last_updated'][:10]}")

if __name__ == "__main__":
    main()
