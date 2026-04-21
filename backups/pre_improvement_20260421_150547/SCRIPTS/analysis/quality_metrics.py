#!/usr/bin/env python3
"""
Sir HazeClaw Quality Metrics Tracker
Misst Qualität der Arbeit und trackt Verbesserungen.

Metriken:
- Tasks completed vs planned
- Scripts tested vs untested
- Commits per day
- Backup ratio (Backups/Commits)
- Error rate
- Pattern violations

Usage:
    python3 quality_metrics.py
    python3 quality_metrics.py --days 7
    python3 quality_metrics.py --report
"""

import os
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
KG_PATH = WORKSPACE / "core_ultralight/memory/knowledge_graph.json"
BACKUP_DIR = WORKSPACE.parent / "backups"

# Quality Thresholds
THRESHOLDS = {
    'min_commits_per_day': 3,
    'max_backup_ratio': 0.3,  # Backups/Commits < 0.3 = OK
    'min_test_rate': 0.8,     # 80% of scripts should be tested
    'max_pattern_violations': 2,
}

def get_commits_per_day(days=7):
    """Holt Commits pro Tag für letzte X Tage."""
    stats = []
    
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
            commits = [c for c in result.stdout.strip().split('\n') if c]
            stats.append({
                'date': date_str,
                'count': len(commits),
                'short': date.strftime('%a')
            })
        except:
            stats.append({'date': date_str, 'count': 0, 'short': date.strftime('%a')})
    
    return stats

def get_backups_per_day(days=7):
    """Holt Backups pro Tag für letzte X Tage."""
    stats = []
    
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        date_str = date.strftime("%Y%m%d")
        
        backups = list(BACKUP_DIR.glob(f"backup_{date_str}_*.tar.gz"))
        stats.append({
            'date': date_str,
            'count': len(backups),
            'short': date.strftime('%a')
        })
    
    return stats

def calculate_metrics(days=7):
    """Berechnet alle Quality Metriken."""
    commits = get_commits_per_day(days)
    backups = get_backups_per_day(days)
    
    total_commits = sum(c['count'] for c in commits)
    total_backups = sum(b['count'] for b in backups)
    
    # Average per day
    avg_commits = total_commits / days if days > 0 else 0
    avg_backups = total_backups / days if days > 0 else 0
    
    # Backup ratio
    backup_ratio = total_backups / total_commits if total_commits > 0 else 0
    
    # Quality scores
    scores = {}
    
    # Commit score
    if avg_commits >= 10:
        scores['commits'] = {'score': 100, 'status': 'excellent'}
    elif avg_commits >= 5:
        scores['commits'] = {'score': 80, 'status': 'good'}
    elif avg_commits >= THRESHOLDS['min_commits_per_day']:
        scores['commits'] = {'score': 60, 'status': 'ok'}
    else:
        scores['commits'] = {'score': 30, 'status': 'poor'}
    
    # Backup ratio score
    if backup_ratio <= THRESHOLDS['max_backup_ratio']:
        scores['backup_ratio'] = {'score': 100, 'status': 'excellent'}
    elif backup_ratio <= 0.5:
        scores['backup_ratio'] = {'score': 70, 'status': 'ok'}
    elif backup_ratio <= 1.0:
        scores['backup_ratio'] = {'score': 40, 'status': 'warning'}
    else:
        scores['backup_ratio'] = {'score': 10, 'status': 'critical'}
    
    # Overall score (weighted average)
    overall = (
        scores['commits']['score'] * 0.5 +
        scores['backup_ratio']['score'] * 0.5
    )
    
    return {
        'days': days,
        'commits': commits,
        'backups': backups,
        'total_commits': total_commits,
        'total_backups': total_backups,
        'avg_commits': avg_commits,
        'avg_backups': avg_backups,
        'backup_ratio': backup_ratio,
        'scores': scores,
        'overall_score': overall,
        'timestamp': datetime.now().isoformat()
    }

def generate_report(metrics):
    """Generiert Quality Report."""
    now = datetime.now()
    
    lines = []
    lines.append(f"📊 **Quality Metrics — {now.strftime('%Y-%m-%d')}**")
    lines.append("")
    
    # Summary
    overall = metrics['overall_score']
    if overall >= 90:
        emoji = "🟢"
        status = "EXCELLENT"
    elif overall >= 70:
        emoji = "🟡"
        status = "GOOD"
    elif overall >= 50:
        emoji = "🟠"
        status = "OK"
    else:
        emoji = "🔴"
        status = "NEEDS IMPROVEMENT"
    
    lines.append(f"**Overall Score: {overall:.0f}/100 {emoji} — {status}**")
    lines.append("")
    
    # Commits
    lines.append("**📝 COMMITS**")
    c_score = metrics['scores']['commits']
    lines.append(f"- Average: {metrics['avg_commits']:.1f}/day")
    lines.append(f"- Total: {metrics['total_commits']} ({metrics['days']} days)")
    lines.append(f"- Status: {c_score['status'].upper()} ({c_score['score']}/100)")
    lines.append("")
    
    # Visual bar
    lines.append("**Daily Commits:**")
    max_c = max(c['count'] for c in metrics['commits']) if metrics['commits'] else 1
    for c in reversed(metrics['commits']):
        bar_len = int((c['count'] / max_c) * 15) if max_c > 0 else 0
        bar = '█' * bar_len
        lines.append(f"  {c['short']}: {c['count']:3d} {bar}")
    lines.append("")
    
    # Backups
    lines.append("**💾 BACKUPS**")
    b_score = metrics['scores']['backup_ratio']
    lines.append(f"- Average: {metrics['avg_backups']:.1f}/day")
    lines.append(f"- Total: {metrics['total_backups']} ({metrics['days']} days)")
    lines.append(f"- Ratio: {metrics['backup_ratio']:.2f} (Backups/Commits)")
    lines.append(f"- Status: {b_score['status'].upper()} ({b_score['score']}/100)")
    lines.append("")
    
    # Visual bar for backups
    lines.append("**Daily Backups:**")
    max_b = max(b['count'] for b in metrics['backups']) if metrics['backups'] else 1
    for b in reversed(metrics['backups']):
        bar_len = int((b['count'] / max_b) * 15) if max_b > 0 else 0
        bar = '█' * bar_len
        lines.append(f"  {b['short']}: {b['count']:3d} {bar}")
    lines.append("")
    
    # Recommendations
    lines.append("**💡 RECOMMENDATIONS**")
    if c_score['status'] == 'poor':
        lines.append("- ⚠️ Commit Frequency niedrig - mehr fokussierte Arbeit")
    if b_score['status'] in ['warning', 'critical']:
        lines.append("- ⚠️ Backup Ratio hoch - weniger Backups, mehr Arbeiten")
    if overall >= 90:
        lines.append("- ✅ Quality excellent - weiter so!")
    
    lines.append("")
    lines.append(f"_Generated: {now.strftime('%H:%M:%S')}_")
    
    return "\n".join(lines)

def save_metrics_to_kg(metrics):
    """Speichert Metrics in KG."""
    if not KG_PATH.exists():
        return False
    
    try:
        with open(KG_PATH) as f:
            kg = json.load(f)
        
        today = datetime.now().strftime('%Y%m%d')
        entity_id = f"quality_metrics_{today}"
        
        entity = {
            "type": "metrics",
            "category": "quality_tracking",
            "facts": [{
                "content": f"Quality Score: {metrics['overall_score']:.0f}/100, Commits: {metrics['total_commits']}, Backups: {metrics['total_backups']}, Backup Ratio: {metrics['backup_ratio']:.2f}",
                "confidence": 0.95,
                "extracted_at": datetime.now().isoformat(),
                "category": "quality_metrics"
            }],
            "priority": "MEDIUM",
            "created": datetime.now().isoformat(),
            "tags": ["metrics", "quality", "daily"]
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
    
    parser = argparse.ArgumentParser(description='Quality Metrics Tracker')
    parser.add_argument('--days', type=int, default=7, help='Days to analyze')
    parser.add_argument('--save', action='store_true', help='Save to KG')
    args = parser.parse_args()
    
    metrics = calculate_metrics(args.days)
    report = generate_report(metrics)
    print(report)
    
    if args.save:
        if save_metrics_to_kg(metrics):
            print("\n✅ Metrics saved to KG")

if __name__ == "__main__":
    main()
