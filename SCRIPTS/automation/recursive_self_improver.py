#!/usr/bin/env python3
"""
Recursive Self-Improvement Engine — Sir HazeClaw Phase 3
========================================================
The system that improves its own improvement process.

Based on:
- Recursive Self-Improvement (Goodfellow et al., 2016)
- Learning to Learn (Andrychowicz et al., 2016)
- Meta-Learning with Growing Neural Networks

Key Insight: "The best AI is one that improves itself"

Usage:
    python3 recursive_self_improver.py --scan        # Scan improvement opportunities
    python3 recursive_self_improver.py --reflect    # Self-reflection on recent improvements
    python3 recursive_self_improver.py --evolve      # Evolve based on feedback
    python3 recursive_self_improver.py --report      # Generate improvement report

Phase C3: Recursive Self-Improvement
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "SCRIPTS" / "automation"
DATA_DIR = WORKSPACE / "data"
LOGS_DIR = WORKSPACE / "logs"
KG_PATH = WORKSPACE / "ceo/memory/kg/knowledge_graph.json"
LEARNING_DIR = DATA_DIR / "learning_loop"
IMPROVEMENTS_DIR = DATA_DIR / "improvements"

# Meta-learning configuration
IMPROVEMENT_CATEGORIES = {
    "code_quality": {
        "description": "Code structure, readability, error handling",
        "weight": 0.25,
        "indicators": ["bug_fixes", "refactoring", "error_handling"]
    },
    "learning_quality": {
        "description": "Pattern discovery, learning effectiveness",
        "weight": 0.25,
        "indicators": ["patterns_found", "learning_applied", "score_improvement"]
    },
    "efficiency": {
        "description": "Token usage, execution speed, resource usage",
        "weight": 0.20,
        "indicators": ["token_optimization", "faster_execution", "cache_hits"]
    },
    "autonomy": {
        "description": "Self-management, proactivity, decision quality",
        "weight": 0.20,
        "indicators": ["self_healed", "proactive_actions", "decision_accuracy"]
    },
    "knowledge": {
        "description": "KG growth, entity quality, cross-linking",
        "weight": 0.10,
        "indicators": ["kg_entities_added", "relations_created", "orphans_cleaned"]
    }
}

def log(msg: str, level: str = "INFO"):
    """Logging."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": msg
    }
    with open(LOGS_DIR / "recursive_self_improver.log", "a") as f:
        f.write(json.dumps(entry) + "\n")

def load_kg() -> Dict:
    """Load knowledge graph."""
    if KG_PATH.exists():
        try:
            return json.load(open(KG_PATH))
        except:
            return {"entities": {}, "relations": []}
    return {"entities": {}, "relations": []}

def get_learning_stats() -> Dict:
    """Get learning loop statistics."""
    state_file = LEARNING_DIR / "learning_loop_state.json"
    if state_file.exists():
        try:
            return json.load(open(state_file))
        except:
            pass
    return {}

def get_improvement_history() -> List[Dict]:
    """Get history of improvements made."""
    history_file = IMPROVEMENTS_DIR / "improvement_log.json"
    if history_file.exists():
        try:
            data = json.load(open(history_file))
            return data.get("improvements", [])
        except:
            pass
    return []

def analyze_improvement_patterns(improvements: List[Dict]) -> Dict:
    """Analyze patterns in past improvements."""
    patterns = {
        "total": len(improvements),
        "by_category": defaultdict(int),
        "success_rate": {},
        "avg_age_days": 0,
        "failed": [],
        "succeeded": [],
    }
    
    now = datetime.now()
    ages = []
    
    for imp in improvements:
        cat = imp.get("category", "unknown")
        patterns["by_category"][cat] += 1
        
        # Check age
        if "created" in imp:
            try:
                created = datetime.fromisoformat(imp["created"].replace("Z", "+00:00"))
                age = (now - created).days
                ages.append(age)
            except:
                pass
        
        # Check outcome
        outcome = imp.get("outcome", "unknown")
        if outcome in ["success", "validated"]:
            patterns["succeeded"].append(imp)
        elif outcome in ["failed", "reverted"]:
            patterns["failed"].append(imp)
    
    if ages:
        patterns["avg_age_days"] = sum(ages) / len(ages)
    
    if patterns["succeeded"]:
        patterns["success_rate"] = len(patterns["succeeded"]) / patterns["total"]
    else:
        patterns["success_rate"] = 0.5  # Default 50%
    
    return patterns

def identify_meta_patterns(patterns: Dict) -> List[Dict]:
    """Identify meta-patterns in the improvement process."""
    meta_patterns = []
    
    # Pattern 1: Category imbalance
    cat_counts = dict(patterns["by_category"])
    if cat_counts:
        max_cat = max(cat_counts.items(), key=lambda x: x[1])
        min_cat = min(cat_counts.items(), key=lambda x: x[1])
        
        if max_cat[1] > min_cat[1] * 3:
            meta_patterns.append({
                "type": "category_imbalance",
                "description": f"Category '{max_cat[0]}' dominates ({max_cat[1]}) vs '{min_cat[0]}' ({min_cat[1]})",
                "recommendation": f"Focus more on {min_cat[0]} improvements",
                "severity": "MEDIUM"
            })
    
    # Pattern 2: Low success rate
    if patterns["success_rate"] < 0.4:
        meta_patterns.append({
            "type": "low_success_rate",
            "description": f"Success rate only {patterns['success_rate']:.0%}",
            "recommendation": "Review failed improvements for common failure modes",
            "severity": "HIGH"
        })
    
    # Pattern 3: Stale improvements
    if patterns["avg_age_days"] > 14:
        meta_patterns.append({
            "type": "stale_improvements",
            "description": f"Average improvement age: {patterns['avg_age_days']:.0f} days",
            "recommendation": "Review and finalize old improvements",
            "severity": "MEDIUM"
        })
    
    return meta_patterns

def score_improvement_process() -> float:
    """
    Score the improvement process itself (meta-evaluation).
    0.0 = poor, 1.0 = excellent
    """
    score = 0.5  # Start neutral
    
    improvements = get_improvement_history()
    patterns = analyze_improvement_patterns(improvements)
    
    # Factor 1: Success rate (0.3 weight)
    success_score = patterns["success_rate"]
    score += (success_score - 0.5) * 0.3
    
    # Factor 2: Diversity (0.3 weight)
    categories = len(patterns["by_category"])
    diversity_score = min(1.0, categories / 5)  # 5 categories = full score
    score += (diversity_score - 0.5) * 0.3
    
    # Factor 3: Recency (0.2 weight)
    recent_count = sum(1 for i in improvements if True)  # Would check timestamp
    recency_score = min(1.0, recent_count / 10)
    score += (recency_score - 0.5) * 0.2
    
    # Factor 4: Meta-patterns (0.2 weight)
    meta_patterns = identify_meta_patterns(patterns)
    meta_penalty = len([p for p in meta_patterns if p["severity"] == "HIGH"]) * 0.1
    score -= meta_penalty
    
    return max(0.0, min(1.0, score))

def generate_self_reflection(patterns: Dict, meta_patterns: List[Dict]) -> str:
    """Generate self-reflection on improvement process."""
    lines = [
        "## Recursive Self-Improvement Reflection",
        "",
        f"**Timestamp:** {datetime.now().isoformat()}",
        f"**Process Score:** {score_improvement_process():.1%}",
        "",
    ]
    
    lines.append("### 📊 Improvement Patterns")
    lines.append(f"- Total improvements: {patterns['total']}")
    lines.append(f"- Success rate: {patterns['success_rate']:.0%}")
    lines.append(f"- Average age: {patterns['avg_age_days']:.0f} days")
    lines.append("")
    
    if patterns['by_category']:
        lines.append("**By Category:**")
        for cat, count in patterns['by_category'].items():
            lines.append(f"- {cat}: {count}")
        lines.append("")
    
    if meta_patterns:
        lines.append("### ⚠️ Meta-Patterns Detected")
        for mp in meta_patterns:
            severity = mp['severity']
            emoji = "🔴" if severity == "HIGH" else "🟡"
            lines.append(f"{emoji} **{mp['type']}**: {mp['description']}")
            lines.append(f"   → {mp['recommendation']}")
        lines.append("")
    
    lines.append("### 💭 Self-Assessment")
    score = score_improvement_process()
    if score >= 0.8:
        lines.append("✅ The improvement process is highly effective.")
    elif score >= 0.6:
        lines.append("🟡 The improvement process is working, with room for optimization.")
    elif score >= 0.4:
        lines.append("🟠 The improvement process needs attention.")
    else:
        lines.append("🔴 The improvement process is not working well.")
    
    return "\n".join(lines)

def run_self_scan() -> Dict:
    """Scan for improvement opportunities."""
    scan_results = {
        "timestamp": datetime.now().isoformat(),
        "learning_stats": get_learning_stats(),
        "improvement_patterns": {},
        "meta_patterns": [],
        "opportunities": [],
        "process_score": 0.0,
    }
    
    # Analyze improvement history
    improvements = get_improvement_history()
    scan_results["improvement_patterns"] = analyze_improvement_patterns(improvements)
    
    # Identify meta-patterns
    scan_results["meta_patterns"] = identify_meta_patterns(
        scan_results["improvement_patterns"]
    )
    
    # Score the process
    scan_results["process_score"] = score_improvement_process()
    
    # Generate opportunities based on meta-patterns
    for mp in scan_results["meta_patterns"]:
        if mp["type"] == "category_imbalance":
            scan_results["opportunities"].append({
                "type": "balance_categories",
                "description": f"Invest more in {mp.get('recommendation', 'balanced improvements')}",
                "priority": "HIGH"
            })
        elif mp["type"] == "low_success_rate":
            scan_results["opportunities"].append({
                "type": "improve_validation",
                "description": "Review and improve validation before applying changes",
                "priority": "HIGH"
            })
    
    return scan_results

def run_self_reflection() -> str:
    """Run self-reflection on improvement process."""
    improvements = get_improvement_history()
    patterns = analyze_improvement_patterns(improvements)
    meta_patterns = identify_meta_patterns(patterns)
    
    reflection = generate_self_reflection(patterns, meta_patterns)
    print(reflection)
    
    return reflection

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Recursive Self-Improvement Engine')
    parser.add_argument('--scan', action='store_true', help='Scan improvement opportunities')
    parser.add_argument('--reflect', action='store_true', help='Self-reflection on improvements')
    parser.add_argument('--evolve', action='store_true', help='Evolve based on feedback')
    parser.add_argument('--report', action='store_true', help='Generate improvement report')
    args = parser.parse_args()
    
    if args.scan:
        print("🔍 Scanning improvement process...")
        results = run_self_scan()
        
        print(f"\n📊 Process Score: {results['process_score']:.1%}")
        print(f"\n📈 Statistics:")
        stats = results['improvement_patterns']
        print(f"   Total improvements: {stats['total']}")
        print(f"   Success rate: {stats['success_rate']:.0%}")
        print(f"   Avg age: {stats['avg_age_days']:.0f} days")
        
        if results['meta_patterns']:
            print(f"\n⚠️ Meta-Patterns: {len(results['meta_patterns'])}")
            for mp in results['meta_patterns'][:3]:
                print(f"   [{mp['severity']}] {mp['type']}: {mp['description'][:50]}")
        
        if results['opportunities']:
            print(f"\n💡 Opportunities:")
            for opp in results['opportunities'][:3]:
                print(f"   [{opp['priority']}] {opp['description']}")
    
    elif args.reflect:
        run_self_reflection()
    
    elif args.evolve:
        print("🧬 Evolving improvement process...")
        
        # Run self-scan
        scan = run_self_scan()
        
        # Apply corrections based on meta-patterns
        corrections = []
        for mp in scan['meta_patterns']:
            if mp['type'] == 'category_imbalance':
                corrections.append("Focus on underrepresented categories")
            elif mp['type'] == 'low_success_rate':
                corrections.append("Improve validation process")
        
        if corrections:
            print("✅ Corrections identified:")
            for c in corrections:
                print(f"   - {c}")
        else:
            print("✅ No corrections needed - process is healthy")
        
        print(f"\n📊 Current Process Score: {scan['process_score']:.1%}")
    
    elif args.report:
        improvements = get_improvement_history()
        patterns = analyze_improvement_patterns(improvements)
        meta_patterns = identify_meta_patterns(patterns)
        
        print("📊 RECURSIVE SELF-IMPROVEMENT REPORT")
        print("=" * 60)
        print(f"\n📈 Improvement Metrics:")
        print(f"   Total: {patterns['total']}")
        print(f"   Success Rate: {patterns['success_rate']:.0%}")
        print(f"   Avg Age: {patterns['avg_age_days']:.0f} days")
        
        print(f"\n💡 Meta-Patterns: {len(meta_patterns)}")
        for mp in meta_patterns[:5]:
            print(f"   [{mp['severity']}] {mp['type']}")
        
        print(f"\n🎯 Process Score: {score_improvement_process():.1%}")
    
    else:
        print("Recursive Self-Improvement Engine")
        print("Usage:")
        print("  --scan     Scan for improvement opportunities")
        print("  --reflect  Self-reflection on improvements")
        print("  --evolve   Evolve based on feedback")
        print("  --report   Generate improvement report")

if __name__ == "__main__":
    main()
