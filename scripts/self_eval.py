#!/usr/bin/env python3
"""
Sir HazeClaw Self-Evaluation
Evaluates current state vs defined goals.

Usage:
    python3 self_eval.py
    python3 self_eval.py --report
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
KG_PATH = WORKSPACE / "core_ultralight/memory/knowledge_graph.json"
HEARTBEAT_PATH = WORKSPACE / "ceo/HEARTBEAT.md"

# Goals Definition
GOALS = {
    'quality': {
        'name': 'Quality über Quantität',
        'metrics': [
            {'key': 'backup_ratio', 'target': '< 0.3', 'weight': 1.0},
            {'key': 'tested_scripts', 'target': '> 80%', 'weight': 1.5},
        ],
        'min_score': 70,
    },
    'productivity': {
        'name': 'Produktivität',
        'metrics': [
            {'key': 'commits_per_day', 'target': '> 5', 'weight': 1.0},
            {'key': 'tasks_completed', 'target': '> 3/day', 'weight': 1.2},
        ],
        'min_score': 60,
    },
    'knowledge': {
        'name': 'Wissen & Lernen',
        'metrics': [
            {'key': 'kg_entities', 'target': '> 100', 'weight': 1.0},
            {'key': 'patterns_learned', 'target': '> 5', 'weight': 0.8},
        ],
        'min_score': 50,
    },
    'self_management': {
        'name': 'Self-Management',
        'metrics': [
            {'key': 'heartbeat_updated', 'target': 'daily', 'weight': 1.0},
            {'key': 'reflection_done', 'target': 'weekly', 'weight': 0.8},
        ],
        'min_score': 70,
    }
}

def get_git_stats():
    """Holt Git Statistics."""
    today = datetime.now().strftime('%Y-%m-%d')
    
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", f"--since={today}T00:00:00Z"],
            cwd=str(WORKSPACE),
            capture_output=True,
            text=True,
            timeout=10
        )
        commits_today = len([c for c in result.stdout.strip().split('\n') if c])
        
        # Last 7 days
        result = subprocess.run(
            ["git", "log", "--oneline", "--since='7 days ago'"],
            cwd=str(WORKSPACE),
            capture_output=True,
            text=True,
            timeout=10
        )
        commits_week = len([c for c in result.stdout.strip().split('\n') if c])
        
        return {
            'commits_today': commits_today,
            'commits_week': commits_week,
            'avg_per_day': commits_week / 7 if commits_week > 0 else 0
        }
    except:
        return {'commits_today': 0, 'commits_week': 0, 'avg_per_day': 0}

def get_kg_stats():
    """Holt KG Statistics."""
    if not KG_PATH.exists():
        return {'entities': 0, 'relations': 0}
    
    try:
        with open(KG_PATH) as f:
            kg = json.load(f)
        
        return {
            'entities': len(kg.get('entities', {})),
            'relations': len(kg.get('relations', []))
        }
    except:
        return {'entities': 0, 'relations': 0}

def get_backup_ratio():
    """Berechnet Backup/Commit Ratio."""
    backup_dir = WORKSPACE.parent / "backups"
    today = datetime.now().strftime("%Y%m%d")
    
    backups = list(backup_dir.glob(f"backup_{today}_*.tar.gz"))
    git = get_git_stats()
    
    if git['commits_today'] == 0:
        return 999  # Infinite
    
    return len(backups) / git['commits_today']

def get_script_stats():
    """Holt Script Statistics."""
    scripts_dir = WORKSPACE / "scripts"
    scripts = list(scripts_dir.glob("*.py"))
    
    total = len([s for s in scripts if not s.name.startswith('_') and s.name != '__init__.py' and s.name != 'test_framework.py' and s.name != 'self_eval.py'])
    
    # Count unique scripts tested by test_framework
    # Parse test_framework.py to extract tested scripts
    test_framework_path = scripts_dir / 'test_framework.py'
    tested = set()
    
    if test_framework_path.exists():
        content = test_framework_path.read_text()
        import re
        # Find all 'script': 'xxx.py' patterns
        matches = re.findall(r"'script': '(\w+\.py)'", content)
        tested = set(matches)
    
    tested_count = len(tested)
    
    return {
        'total': total,
        'tested': tested_count,
        'untested': total - tested_count,
        'test_rate': tested_count / total if total > 0 else 0
    }

def evaluate_metric(metric_def, current_value):
    """Evaluates a single metric against its target."""
    key = metric_def['key']
    target = metric_def['target'].replace('%', '').strip()
    weight = metric_def.get('weight', 1.0)
    
    # Parse target
    if '>' in target:
        threshold = float(target.replace('>', '').strip())
        if key == 'backup_ratio':
            passed = current_value < threshold
            score = max(0, 100 - (current_value / threshold * 100)) if current_value > 0 else 100
        elif key == 'kg_entities':
            passed = current_value > threshold
            score = min(100, current_value / threshold * 100)
        elif key in ['commits_per_day', 'commits_today', 'commits_week']:
            passed = current_value > threshold
            score = min(100, current_value / threshold * 100)
        elif key == 'test_rate':
            passed = current_value > threshold / 100
            score = current_value * 100 / threshold * 100 if threshold > 0 else 0
        else:
            passed = current_value >= threshold
            score = min(100, current_value / threshold * 100)
    elif '<' in target:
        threshold = float(target.replace('<', '').strip())
        passed = current_value < threshold
        score = max(0, 100 - (current_value / threshold * 100)) if current_value > 0 else 100
    else:
        passed = current_value >= float(target)
        score = min(100, current_value / float(target) * 100)
    
    return {
        'key': key,
        'current': current_value,
        'target': metric_def['target'],
        'passed': passed,
        'score': max(0, min(100, score)),
        'weight': weight
    }

def calculate_scores():
    """Calculates all goal scores."""
    git = get_git_stats()
    kg = get_kg_stats()
    backup_ratio = get_backup_ratio()
    scripts = get_script_stats()
    
    # Map metrics to values
    metric_values = {
        'commits_today': git['commits_today'],
        'commits_per_day': git['avg_per_day'],
        'commits_week': git['commits_week'],
        'kg_entities': kg['entities'],
        'kg_relations': kg['relations'],
        'backup_ratio': backup_ratio,
        'tested_scripts': scripts['tested'],
        'total_scripts': scripts['total'],
        'test_rate': scripts['test_rate'],
    }
    
    # Calculate scores per goal
    results = {}
    
    for goal_key, goal_def in GOALS.items():
        goal_scores = []
        
        for metric_def in goal_def['metrics']:
            key = metric_def['key']
            if key in metric_values:
                value = metric_values[key]
                result = evaluate_metric(metric_def, value)
                goal_scores.append(result)
        
        if goal_scores:
            # Weighted average
            total_weight = sum(m['weight'] for m in goal_scores)
            weighted_sum = sum(m['score'] * m['weight'] for m in goal_scores)
            avg_score = weighted_sum / total_weight if total_weight > 0 else 0
            
            # Passed if all metrics pass
            all_passed = all(m['passed'] for m in goal_scores)
            
            results[goal_key] = {
                'name': goal_def['name'],
                'score': avg_score,
                'passed': all_passed,
                'min_score': goal_def['min_score'],
                'meets_min': avg_score >= goal_def['min_score'],
                'metrics': goal_scores
            }
    
    # Overall score (weighted by min_score importance)
    total_weight = sum(r['min_score'] for r in results.values())
    overall = sum(r['score'] * r['min_score'] for r in results.values()) / total_weight if total_weight > 0 else 0
    
    return {
        'overall': overall,
        'goals': results,
        'metrics': metric_values,
        'timestamp': datetime.now().isoformat()
    }

def generate_report(data):
    """Generiert Self-Evaluation Report."""
    now = datetime.now()
    
    overall = data['overall']
    
    # Overall status
    if overall >= 90:
        status = "🟢 EXCELLENT"
    elif overall >= 70:
        status = "🟡 GOOD"
    elif overall >= 50:
        status = "🟠 OK"
    else:
        status = "🔴 NEEDS WORK"
    
    lines = []
    lines.append(f"📊 **SELF-EVALUATION REPORT**")
    lines.append(f"_Generated: {now.strftime('%Y-%m-%d %H:%M UTC')}_")
    lines.append("")
    lines.append(f"**Overall Score: {overall:.0f}/100 — {status}**")
    lines.append("")
    
    # Goal breakdown
    lines.append("**📋 GOAL ASSESSMENT**")
    lines.append("")
    
    for goal_key, goal in data['goals'].items():
        emoji = "✅" if goal['meets_min'] else "⚠️"
        lines.append(f"{emoji} **{goal['name']}** — {goal['score']:.0f}/100")
        
        for m in goal['metrics']:
            m_emoji = "✅" if m['passed'] else "❌"
            lines.append(f"   {m_emoji} {m['key']}: {m['current']} (target: {m['target']})")
        
        lines.append("")
    
    # Metrics summary
    lines.append("**📈 KEY METRICS**")
    lines.append("")
    
    m = data['metrics']
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Commits Today | {m['commits_today']} |")
    lines.append(f"| Commits/Week Avg | {m['commits_per_day']:.1f} |")
    lines.append(f"| KG Entities | {m['kg_entities']} |")
    lines.append(f"| KG Relations | {m['kg_relations']} |")
    lines.append(f"| Backup Ratio | {m['backup_ratio']:.2f} |")
    lines.append(f"| Scripts Tested | {m['tested_scripts']}/{m['total_scripts']} ({m['test_rate']*100:.0f}%) |")
    
    lines.append("")
    
    # Recommendations
    lines.append("**💡 RECOMMENDATIONS**")
    lines.append("")
    
    needs_work = False
    for goal_key, goal in data['goals'].items():
        if not goal['meets_min']:
            needs_work = True
            failed_metrics = [m for m in goal['metrics'] if not m['passed']]
            for m in failed_metrics:
                if m['key'] == 'backup_ratio':
                    lines.append(f"- ⚠️ Backup Ratio hoch ({m['current']:.2f}) — Weniger Backups, mehr arbeiten")
                elif m['key'] == 'test_rate':
                    lines.append(f"- ⚠️ Test Coverage niedrig ({m['current']*100:.0f}%) — Scripts testen")
                elif m['key'] == 'kg_entities':
                    lines.append(f"- ⚠️ KG dünn ({m['current']}) — Mehr Wissen speichern")
                elif 'commits' in m['key']:
                    lines.append(f"- ⚠️ Wenig Commits ({m['current']}) — Mehr fokussiert arbeiten")
    
    if not needs_work:
        lines.append("- ✅ Alle Goals erreicht! Weiter so!")
    
    lines.append("")
    lines.append(f"_Next Evaluation: Tomorrow_")
    
    return "\n".join(lines)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Self-Evaluation')
    parser.add_argument('--report', action='store_true', help='Generate report')
    args = parser.parse_args()
    
    data = calculate_scores()
    
    if args.report:
        print(generate_report(data))
    else:
        # Quick summary
        print(f"Self-Evaluation: {data['overall']:.0f}/100")
        for goal_key, goal in data['goals'].items():
            emoji = "✅" if goal['meets_min'] else "⚠️"
            print(f"  {emoji} {goal['name']}: {goal['score']:.0f}/100")

if __name__ == "__main__":
    main()
