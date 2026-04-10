#!/usr/bin/env python3
"""
Sir HazeClaw Deep Self-Reflection
Tiefgehende Selbst-Analyse für kontinuierliche Verbesserung.

Usage:
    python3 deep_reflection.py
    python3 deep_reflection.py --days 7
    python3 deep_reflection.py --output kg
"""

import os
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
KG_PATH = WORKSPACE / "core_ultralight/memory/knowledge_graph.json"
MEMORY_FILE = WORKSPACE / "memory/2026-04-10.md"
HEARTBEAT_PATH = WORKSPACE / "ceo/HEARTBEAT.md"
PATTERNS_FILE = WORKSPACE / "ceo/PATTERN_RECOGNITION.md"

# Reflection Questions (deep)
REFLECTION_QUESTIONS = [
    {
        "category": "QUALITY",
        "question": "Which tasks were completed with high quality today?",
        "aspect": "Was habe ich heute GUT gemacht?"
    },
    {
        "category": "QUALITY", 
        "question": "Which tasks were rushed or incomplete?",
        "aspect": "Was habe ich heute SCHLECHT gemacht?"
    },
    {
        "category": "PATTERNS",
        "question": "Did I notice any recurring patterns?",
        "aspect": "Welche Patterns habe ich heute erkannt?"
    },
    {
        "category": "PATTERNS",
        "question": "Did I fall into any bad habits?",
        "aspect": "Welche Bad Patterns sind aufgetreten?"
    },
    {
        "category": "LEARNING",
        "question": "What new thing did I learn today?",
        "aspect": "Was habe ich heute NEUES gelernt?"
    },
    {
        "category": "LEARNING",
        "question": "What would I do differently if I could redo today?",
        "aspect": "Was würde ich ANDERS machen?"
    },
    {
        "category": "VALUE",
        "question": "Which action created the most value?",
        "aspect": "Wo habe ich den größten VALUE geschaffen?"
    },
    {
        "category": "VALUE",
        "question": "Which action wasted time without benefit?",
        "aspect": "Wo habe ich ZEIT VERSCHWENDET?"
    },
    {
        "category": "GROWTH",
        "question": "How did I improve my capabilities?",
        "aspect": "Wie habe ich mich HEUTE verbessert?"
    },
    {
        "category": "GROWTH",
        "question": "What skill or knowledge gap remains?",
        "aspect": "Welche SKILL-GAP bleibt?"
    }
]

def get_git_activity(days=1):
    """Holt Git Activity für letzte X Tage."""
    commits = []
    
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", f"--since={date_str}T00:00:00Z", f"--until={date_str}T23:59:59Z"],
                cwd=str(WORKSPACE),
                capture_output=True,
                text=True,
                timeout=10
            )
            day_commits = [c for c in result.stdout.strip().split('\n') if c]
            commits.append({
                'date': date_str,
                'count': len(day_commits),
                'commits': day_commits[:5]  # Last 5
            })
        except:
            commits.append({'date': date_str, 'count': 0, 'commits': []})
    
    return commits

def get_todays_memory():
    """Holt今天的 Memory Notes."""
    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = WORKSPACE / "memory" / f"{today}.md"
    
    if memory_file.exists():
        content = memory_file.read_text()
        return content[:2000]  # First 2000 chars
    return ""

def get_patterns():
    """Liest bekannte Patterns."""
    patterns = {
        'bad': [],
        'good': []
    }
    
    if PATTERNS_FILE.exists():
        content = PATTERNS_FILE.read_text()
        # Simple parsing - just check what's in there
        patterns['has_file'] = True
    else:
        patterns['has_file'] = False
    
    return patterns

def analyze_quality(commits, memory_content):
    """Analysiert Quality der Arbeit."""
    insights = []
    
    if not commits:
        insights.append("⚠️ Keine Commits heute - keine Arbeit dokumentiert")
        return insights
    
    total = sum(c['count'] for c in commits)
    if total > 50:
        insights.append("🔴 Sehr viele Commits ({} - könnte übereilt sein)".format(total))
    elif total > 20:
        insights.append("🟡 Viele Commits ({} - productive)".format(total))
    elif total > 5:
        insights.append("✅ Moderate Commits ({} - gesunde Pace)".format(total))
    else:
        insights.append("⚠️ Wenige Commits ({} - wenig Output)".format(total))
    
    return insights

def generate_deep_reflection():
    """Generiert tiefgehende Selbst-Reflection."""
    now = datetime.now()
    today_str = now.strftime('%Y-%m-%d')
    
    # Gather data
    commits = get_git_activity(1)
    memory = get_todays_memory()
    patterns = get_patterns()
    
    lines = []
    lines.append("")
    lines.append("=" * 60)
    lines.append("🔮 DEEP SELF-REFLECTION")
    lines.append(f"Generated: {now.strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("=" * 60)
    lines.append("")
    
    # 1. Quantitative Analysis
    lines.append("## 📊 QUANTITATIVE ANALYSIS")
    lines.append("")
    for commit_data in commits:
        lines.append(f"**{commit_data['date']}:** {commit_data['count']} Commits")
        if commit_data['commits']:
            for c in commit_data['commits'][:3]:
                lines.append(f"  - {c[:70]}")
    lines.append("")
    
    # 2. Quality Analysis
    lines.append("## ✅ QUALITY ANALYSIS")
    lines.append("")
    quality_insights = analyze_quality(commits, memory)
    for insight in quality_insights:
        lines.append(f"- {insight}")
    lines.append("")
    
    # 3. Deep Questions
    lines.append("## 🪞 DEEP QUESTIONS")
    lines.append("")
    for i, q in enumerate(REFLECTION_QUESTIONS[:5], 1):  # First 5 questions
        lines.append(f"**{q['aspect']}**")
        lines.append(f"_{q['question']}_")
        lines.append("- " + "_" * 40)  # Placeholder for answer
        lines.append("")
    
    # 4. Actionable Learnings
    lines.append("## 💡 ACTIONABLE LEARNINGS")
    lines.append("")
    lines.append("1. **Was nehme ich mit?**")
    lines.append("   - ")
    lines.append("")
    lines.append("2. **Was werde ich morgen anders machen?**")
    lines.append("   - ")
    lines.append("")
    lines.append("3. **Welche Pattern muss ich aktiv vermeiden?**")
    lines.append("   - ")
    lines.append("")
    
    # 5. Tomorrow's Focus
    lines.append("## 🎯 TOMORROW'S FOCUS")
    lines.append("")
    lines.append("- [ ] ")
    lines.append("- [ ] ")
    lines.append("- [ ] ")
    lines.append("")
    
    lines.append("=" * 60)
    lines.append(f"_Reflection completed: {now.strftime('%H:%M:%S')}_")
    lines.append("")
    
    return "\n".join(lines)

def save_to_dreams(reflection_text):
    """Speichert Reflection in .dreams."""
    dreams_file = WORKSPACE / "memory/.dreams/reflection_history.md"
    dreams_file.parent.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Append to existing or create new
    with open(dreams_file, 'a') as f:
        f.write(f"\n\n{reflection_text}")
    
    return dreams_file

def add_to_kg(reflection_text):
    """Fügt Key Insights zum Knowledge Graph hinzu."""
    if not KG_PATH.exists():
        print("⚠️ KG nicht gefunden")
        return False
    
    try:
        with open(KG_PATH) as f:
            kg = json.load(f)
        
        # Create reflection entity
        today = datetime.now().strftime('%Y%m%d')
        entity_id = f"reflection_deep_{today}"
        
        entity = {
            "type": "reflection",
            "category": "self_improvement",
            "facts": [{
                "content": reflection_text[:500],  # First 500 chars
                "confidence": 0.9,
                "extracted_at": datetime.now().isoformat(),
                "category": "self_reflection"
            }],
            "priority": "MEDIUM",
            "created": datetime.now().isoformat(),
            "tags": ["self_improvement", "reflection", "daily"]
        }
        
        kg['entities'][entity_id] = entity
        kg['last_updated'] = datetime.now().isoformat()
        
        with open(KG_PATH, 'w') as f:
            json.dump(kg, f, indent=2)
        
        return True
    except Exception as e:
        print(f"⚠️ KG Update Fehler: {e}")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Deep Self-Reflection')
    parser.add_argument('--days', type=int, default=1, help='Days to analyze')
    parser.add_argument('--output', choices=['print', 'kg', 'dreams', 'all'], default='print')
    args = parser.parse_args()
    
    reflection = generate_deep_reflection()
    
    if args.output == 'print':
        print(reflection)
    elif args.output == 'kg':
        if add_to_kg(reflection):
            print("✅ Reflection to KG added")
    elif args.output == 'dreams':
        path = save_to_dreams(reflection)
        print(f"✅ Reflection saved to {path}")
    elif args.output == 'all':
        path = save_to_dreams(reflection)
        print(f"✅ Saved to {path}")
        if add_to_kg(reflection):
            print("✅ Also added to KG")

if __name__ == "__main__":
    main()
