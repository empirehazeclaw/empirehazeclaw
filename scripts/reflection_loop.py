#!/usr/bin/env python3
"""
Sir HazeClaw Reflection Loop
Reflects on recent decisions and self-corrects.

Based on AI Agent Pattern: Reflection Loop
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"

def get_recent_activity():
    """Holt recent Activity aus Git."""
    import subprocess
    result = subprocess.run(
        ["git", "log", "--oneline", "-20", "--since='8 hours ago'"],
        cwd=str(WORKSPACE),
        capture_output=True,
        text=True
    )
    commits = [c.strip() for c in result.stdout.strip().split('\n') if c.strip()]
    return commits

def get_memory_notes():
    """Holt recent Memory Notes."""
    notes_dir = MEMORY_DIR / "notes"
    if not notes_dir.exists():
        return []
    
    recent = []
    cutoff = datetime.now() - timedelta(hours=24)
    
    for f in notes_dir.rglob("*.md"):
        if f.stat().st_mtime > cutoff.timestamp():
            recent.append(f.name)
    
    return recent

def analyze_patterns():
    """Analysiert Patterns in recent Activity."""
    commits = get_recent_activity()
    
    patterns = {
        'commits': len(commits),
        'files_changed': 0,
        'types': {
            'script': 0,
            'doc': 0,
            'memory': 0,
            'heartbeat': 0,
            'skill': 0,
            'research': 0
        }
    }
    
    for commit in commits:
        msg = commit.lower()
        if 'script' in msg or '.py' in msg:
            patterns['types']['script'] += 1
        if '.md' in msg or 'doc' in msg:
            patterns['types']['doc'] += 1
        if 'memory' in msg:
            patterns['types']['memory'] += 1
        if 'heartbeat' in msg:
            patterns['types']['heartbeat'] += 1
        if 'skill' in msg:
            patterns['types']['skill'] += 1
        if 'research' in msg:
            patterns['types']['research'] += 1
    
    return patterns

def generate_reflection():
    """Generiert Reflection Report."""
    patterns = analyze_patterns()
    recent_notes = get_memory_notes()
    recent_commits = get_recent_activity()
    
    lines = []
    lines.append("🔄 **REFLECTION LOOP REPORT**")
    lines.append(f"_Generated: {datetime.now().strftime('%H:%M UTC')}_")
    lines.append("")
    
    # Activity Summary
    lines.append("**📊 Recent Activity (8h):**")
    lines.append(f"  - Commits: {patterns['commits']}")
    for ptype, count in patterns['types'].items():
        if count > 0:
            lines.append(f"  - {ptype}: {count}")
    lines.append("")
    
    # Quality Check
    lines.append("**🎯 Quality Check:**")
    
    issues = []
    
    if patterns['commits'] > 50:
        issues.append("⚠️  Hohe Commit-Frequenz - Qualität vs Quantität?")
    
    script_ratio = patterns['types']['script'] / max(patterns['commits'], 1)
    if script_ratio < 0.3:
        issues.append("⚠️  Wenig Scripts erstellt - fokussiert arbeiten?")
    
    if patterns['types']['doc'] == 0:
        issues.append("ℹ️  Keine Doku-commits - Dokumentation aktuell?")
    
    if recent_notes:
        lines.append(f"  ℹ️  Memory Notes heute: {len(recent_notes)}")
    
    if issues:
        for issue in issues:
            lines.append(f"  {issue}")
    else:
        lines.append("  ✅ Keine Issues erkannt")
    lines.append("")
    
    # Self-Correction
    lines.append("**🔧 Self-Correction:**")
    
    corrections = []
    
    if patterns['commits'] > 100:
        corrections.append("→ Commit-Frequenz sehr hoch. Evtl. mehr testen statt committen.")
    
    if patterns['types']['script'] > 20:
        corrections.append("→ Viele Scripts erstellt. Test Coverage prüfen.")
    
    if corrections:
        for corr in corrections:
            lines.append(f"  {corr}")
    else:
        lines.append("  ✅ Keine Korrekturen nötig")
    lines.append("")
    
    # Recommendations
    lines.append("**💡 Recommendations:**")
    if patterns['commits'] < 10:
        lines.append("  → Mehr fokussiert arbeiten")
    elif patterns['commits'] > 80:
        lines.append("  → Qualität über Quantität - weniger aber besser")
    else:
        lines.append("  → Weiter so!")
    
    return "\n".join(lines)

def main():
    print(generate_reflection())

if __name__ == "__main__":
    main()
