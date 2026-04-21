#!/usr/bin/env python3
"""
Pattern Learning Engine — extracts and stores patterns from evaluations.
Holt Learnings aus evaluation_feedback und generiert nutzbare Patterns.
"""

import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SIGNAL_FILE = WORKSPACE / "ceo/memory/evaluations/learning_loop_signal.json"
PATTERNS_FILE = WORKSPACE / "ceo/memory/long_term/patterns.md"
LEARNING_STATE = WORKSPACE / "data/learning_loop_state.json"

def load_json(path):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def extract_patterns():
    """Extrahiert Patterns aus dem evaluation Feedback."""
    signal = load_json(SIGNAL_FILE)
    data = signal.get('data', {})
    learnings = signal.get('learnings', [])
    
    patterns = []
    
    # 1. Task Success Rate Pattern
    tsr = data.get('task_success_rate', 0)
    if tsr < 0.80:
        patterns.append({
            'type': 'performance_gap',
            'metric': 'task_success_rate',
            'value': tsr,
            'target': 0.80,
            'gap': 0.80 - tsr,
            'priority': 'HIGH',
            'learnings': [l for l in learnings if l.get('type') == 'performance_gap']
        })
    
    # 2. Efficiency Pattern
    eff = data.get('efficiency', 0)
    if eff > 0:
        patterns.append({
            'type': 'efficiency',
            'metric': 'efficiency',
            'value': eff,
            'status': 'healthy' if eff > 50 else 'needs_attention'
        })
    
    # 3. Antipattern Detection
    antipatterns = data.get('antipattern_issues', [])
    if antipatterns:
        for ap in antipatterns:
            patterns.append({
                'type': 'antipattern',
                'pattern_name': ap.get('pattern_name'),
                'file': ap.get('file'),
                'severity': ap.get('severity'),
                'matches': ap.get('matches'),
                'action': 'fix_required' if ap.get('severity') == 'HIGH' else 'monitor'
            })
    
    # 4. Error Rate Pattern
    error_rate = data.get('error_rate', 0)
    patterns.append({
        'type': 'error_rate',
        'value': error_rate,
        'status': 'healthy' if error_rate < 0.05 else 'needs_attention'
    })
    
    return patterns

def update_learning_state(patterns):
    """Schreibt Patterns in Learning Loop State."""
    state = load_json(LEARNING_STATE)
    
    # Update patterns field
    state['patterns'] = patterns
    state['last_pattern_update'] = datetime.now().isoformat()
    
    # Also update patterns_discovered count
    state['patterns_discovered'] = len(patterns)
    
    save_json(LEARNING_STATE, state)
    print(f"Updated learning state with {len(patterns)} patterns")

def generate_pattern_docs(patterns):
    """Generiert Pattern-Dokumentation für patterns.md."""
    
    sections = []
    sections.append("# PATTERNS — Erkannte Patterns\n")
    sections.append(f"_Letzte Aktualisierung: {datetime.now().strftime('%Y-%m-%d')}_\n")
    sections.append("---\n\n")
    
    # Group by type
    by_type = defaultdict(list)
    for p in patterns:
        by_type[p['type']].append(p)
    
    for ptype, pls in by_type.items():
        sections.append(f"## 🔄 {ptype.upper()}\n\n")
        
        for p in pls:
            if ptype == 'performance_gap':
                sections.append(f"**Task Success Rate:** {p['value']:.1%} (target: {p['target']:.1%})\n")
                sections.append(f"- Gap: {p['gap']:.1%}\n")
                sections.append(f"- Priority: {p['priority']}\n")
                if p.get('learnings'):
                    sections.append(f"- Learning: {p['learnings'][0].get('observation','')}\n")
                sections.append("\n")
            
            elif ptype == 'antipattern':
                sections.append(f"**{p['pattern_name']}** ({p['severity']})\n")
                sections.append(f"- File: `{p['file']}`\n")
                sections.append(f"- Matches: {p['matches']}\n")
                sections.append(f"- Action: {p['action']}\n\n")
            
            elif ptype == 'efficiency':
                sections.append(f"**Efficiency:** {p['value']}\n")
                sections.append(f"- Status: {p['status']}\n\n")
            
            elif ptype == 'error_rate':
                sections.append(f"**Error Rate:** {p['value']:.1%}\n")
                sections.append(f"- Status: {p['status']}\n\n")
    
    with open(PATTERNS_FILE, 'w') as f:
        f.writelines(sections)
    
    print(f"Updated patterns.md with {len(patterns)} patterns")

def main():
    print("=== PATTERN LEARNING ENGINE ===")
    
    # Extract patterns from evaluation
    patterns = extract_patterns()
    print(f"Extracted {len(patterns)} patterns from evaluation")
    
    if not patterns:
        print("No patterns found in current evaluation")
        return
    
    # Update learning state
    update_learning_state(patterns)
    
    # Generate documentation
    generate_pattern_docs(patterns)
    
    print("\n✅ Pattern Learning complete!")
    for p in patterns:
        print(f"  - {p['type']}: {p.get('metric', p.get('pattern_name', 'value'))}")

if __name__ == '__main__':
    main()