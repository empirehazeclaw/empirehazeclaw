#!/usr/bin/env python3
"""
Meta Learning Core — Phase 4, Day 1
====================================
Extends the evaluation framework with self-referential improvement.

Features:
- Pattern generalization scoring
- Meta-learning from learning patterns
- Self-modification of routing logic
- Adaptive learning rate based on task complexity

Usage:
    python3 meta_learning_core.py --analyze          # Analyze recent learnings
    python3 meta_learning_core.py --score          # Calculate generalization scores
    python3 meta_learning_core.py --suggest        # Suggest improvements
    python3 meta_learning_core.py --report         # Meta-learning report
    python3 meta_learning_core.py --adapt <task>  # Get adapted strategy for task
"""

import json
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
META_DIR = WORKSPACE / "memory" / "evaluations" / "meta_learning"
META_FILE = META_DIR / "meta_learning_state.json"
KG_PATH = WORKSPACE / "memory" / "kg" / "knowledge_graph.json"

def init_dirs():
    META_DIR.mkdir(parents=True, exist_ok=True)
    if not META_FILE.exists():
        META_FILE.write_text(json.dumps({
            "patterns": {},
            "generalization_scores": {},
            "learning_history": [],
            "task_complexity_map": {},
            "strategy_effectiveness": {},
            "version": "1.0"
        }))

def load_meta():
    init_dirs()
    return json.loads(META_FILE.read_text())

def save_meta(meta):
    META_FILE.write_text(json.dumps(meta, indent=2))

def load_kg():
    if KG_PATH.exists():
        return json.load(open(KG_PATH))
    return {"entities": {}, "relations": {}}

def analyze_learnings():
    """Analyze learnings to find meta-patterns."""
    meta = load_meta()
    kg = load_kg()
    
    learnings = [
        (name, e) for name, e in kg.get("entities", {}).items()
        if e.get("type") == "learning"
    ]
    
    if not learnings:
        print("[*] No learnings found in KG.")
        return
    
    print(f"\n🔍 Analyzing {len(learnings)} learnings...")
    
    # Group by learning type
    by_type = defaultdict(list)
    for name, entity in learnings:
        lt = entity.get("learning_type", "unknown")
        by_type[lt].append((name, entity))
    
    print(f"\n📊 Learnings by Type:")
    for lt, items in sorted(by_type.items(), key=lambda x: -len(x[1])):
        print(f"  {lt}: {len(items)}")
        meta["patterns"][lt] = {
            "count": len(items),
            "examples": items[:3],
            "last_seen": items[0][1].get("last_accessed", "unknown") if items else "unknown"
        }
    
    # Analyze generalization patterns
    generalization_scores = calculate_generalization_scores(learnings)
    meta["generalization_scores"] = generalization_scores
    
    save_meta(meta)
    print(f"\n✅ Analysis complete. {len(generalization_scores)} patterns scored.")
    
    return meta

def calculate_generalization_scores(learnings: list) -> dict:
    """Calculate how generalizable each learning pattern is."""
    scores = {}
    
    for name, entity in learnings:
        # Factors for generalization:
        # 1. How many different contexts has this been applied in?
        access_count = entity.get("access_count", 1)
        
        # 2. How old is this learning?
        created = entity.get("created", "")
        if created:
            try:
                age_days = (datetime.now(timezone.utc) - datetime.fromisoformat(created.replace("Z", "+00:00"))).days
            except:
                age_days = 0
        else:
            age_days = 0
        
        # 3. How many facts support this?
        fact_count = len(entity.get("facts", []))
        
        # 4. Priority (higher = more important = should generalize more)
        priority_map = {"LOW": 0.5, "MED": 1.0, "HIGH": 1.5, "CRITICAL": 2.0}
        priority = priority_map.get(entity.get("priority", "MED"), 1.0)
        
        # Generalization score formula
        score = (
            min(access_count / 10, 1.0) * 0.3 +  # Accessibility factor
            min(age_days / 30, 1.0) * 0.2 +      # Maturity factor
            min(fact_count / 5, 1.0) * 0.2 +     # Evidence factor
            priority * 0.3                        # Importance factor
        )
        
        scores[name] = {
            "score": min(score, 1.0),
            "access_count": access_count,
            "age_days": age_days,
            "fact_count": fact_count,
            "priority": entity.get("priority", "MED")
        }
    
    return scores

def estimate_task_complexity(task: dict) -> str:
    """Estimate complexity of a task based on its properties."""
    score = 0
    
    # Type complexity
    task_type = task.get("type", "unknown")
    if task_type in ["delegation", "multi_step"]:
        score += 2
    elif task_type in ["research", "analysis"]:
        score += 1
    
    # Context size
    context = task.get("context", {})
    if context:
        if len(str(context)) > 1000:
            score += 2
        elif len(str(context)) > 500:
            score += 1
    
    # Previous failures
    if task.get("failure_count", 0) > 0:
        score += task.get("failure_count", 0)
    
    # Retry count
    if task.get("attempt", 1) > 1:
        score += 1
    
    # Map to complexity level
    if score >= 4:
        return "high"
    elif score >= 2:
        return "medium"
    else:
        return "low"

def get_adapted_strategy(task: dict, meta: dict = None):
    """Get an adapted strategy for a task based on meta-learning."""
    if meta is None:
        meta = load_meta()
    
    complexity = estimate_task_complexity(task)
    task_type = task.get("type", "unknown")
    
    # Strategy selection based on task properties
    strategies = {
        "low": {
            "timeout": 30,
            "retries": 2,
            "delegation": "auto",
            "context_mode": "minimal"
        },
        "medium": {
            "timeout": 60,
            "retries": 3,
            "delegation": "auto",
            "context_mode": "full"
        },
        "high": {
            "timeout": 120,
            "retries": 5,
            "delegation": "full",
            "context_mode": "expanded"
        }
    }
    
    # Adjust based on past effectiveness
    task_key = f"{task_type}_{complexity}"
    effectiveness = meta.get("strategy_effectiveness", {}).get(task_key, {})
    
    if effectiveness:
        # If certain strategies worked better, adjust
        best_strategy = effectiveness.get("best_strategy", "medium")
        if best_strategy in strategies:
            base = strategies[best_strategy].copy()
        else:
            base = strategies[complexity].copy()
    else:
        base = strategies[complexity].copy()
    
    # Add meta-learning insights
    insights = []
    
    # Check if similar tasks had failures
    similar_failures = meta.get("task_complexity_map", {}).get(task_key, {}).get("failures", 0)
    if similar_failures > 0:
        base["retries"] += 1
        insights.append(f"Similar tasks had {similar_failures} failures - increased retries")
    
    # Check generalization score
    high_score_patterns = [
        name for name, data in meta.get("generalization_scores", {}).items()
        if data.get("score", 0) > 0.7
    ]
    if high_score_patterns:
        insights.append(f"High generalization patterns available: {len(high_score_patterns)}")
    
    return {
        "complexity": complexity,
        "strategy": base,
        "task_key": task_key,
        "insights": insights,
        "generalization_applied": len(high_score_patterns) > 0
    }

def record_task_outcome(task: dict, success: bool, meta: dict = None):
    """Record the outcome of a task to improve future strategy selection."""
    if meta is None:
        meta = load_meta()
    
    complexity = estimate_task_complexity(task)
    task_type = task.get("type", "unknown")
    task_key = f"{task_type}_{complexity}"
    
    # Update task complexity map
    if task_key not in meta["task_complexity_map"]:
        meta["task_complexity_map"][task_key] = {
            "total": 0,
            "successes": 0,
            "failures": 0,
            "strategies_used": []
        }
    
    tcm = meta["task_complexity_map"][task_key]
    tcm["total"] += 1
    if success:
        tcm["successes"] += 1
    else:
        tcm["failures"] += 1
    
    strategy = task.get("strategy", "unknown")
    if strategy not in tcm["strategies_used"]:
        tcm["strategies_used"].append(strategy)
    
    # Update strategy effectiveness
    if strategy not in meta["strategy_effectiveness"]:
        meta["strategy_effectiveness"][strategy] = {
            "attempts": 0,
            "successes": 0,
            "failures": 0
        }
    
    se = meta["strategy_effectiveness"][strategy]
    se["attempts"] += 1
    if success:
        se["successes"] += 1
    else:
        se["failures"] += 1
    
    # Calculate best strategy for this task type
    if tcm["total"] >= 3:  # Need minimum data
        best = None
        best_rate = 0
        for strat in tcm["strategies_used"]:
            se = meta["strategy_effectiveness"].get(strat, {})
            attempts = se.get("attempts", 0)
            if attempts > 0:
                rate = se.get("successes", 0) / attempts
                if rate > best_rate:
                    best_rate = rate
                    best = strat
        
        if best:
            meta["strategy_effectiveness"][task_key] = {
                "best_strategy": best,
                "success_rate": best_rate
            }
    
    # Add to learning history
    meta["learning_history"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task_type": task_type,
        "complexity": complexity,
        "strategy": strategy,
        "success": success
    })
    
    # Keep history limited
    if len(meta["learning_history"]) > 1000:
        meta["learning_history"] = meta["learning_history"][-500:]
    
    save_meta(meta)
    print(f"[*] Recorded outcome: {task_key} -> {'✅' if success else '❌'}")

def suggest_improvements():
    """Suggest system improvements based on meta-learning analysis."""
    meta = load_meta()
    suggestions = []
    
    # Analyze task complexity map
    for task_key, data in meta.get("task_complexity_map", {}).items():
        if data["total"] >= 3:
            success_rate = data["successes"] / data["total"]
            
            if success_rate < 0.5:
                suggestions.append({
                    "type": "task_optimization",
                    "task": task_key,
                    "issue": f"Low success rate: {success_rate:.1%}",
                    "recommendation": "Review strategy for this task type",
                    "priority": "HIGH"
                })
            
            if data["failures"] > 2 and data["failures"] > data["successes"]:
                suggestions.append({
                    "type": "failure_pattern",
                    "task": task_key,
                    "issue": f"More failures than successes: {data['failures']} vs {data['successes']}",
                    "recommendation": "Consider different approach or delegation",
                    "priority": "MED"
                })
    
    # Analyze generalization scores
    low_generalization = [
        (name, data) for name, data in meta.get("generalization_scores", {}).items()
        if data.get("score", 1.0) < 0.3
    ]
    
    if low_generalization:
        suggestions.append({
            "type": "learning_quality",
            "issue": f"{len(low_generalization)} learnings with low generalization",
            "recommendation": "Review and potentially consolidate similar learnings",
            "priority": "LOW"
        })
    
    # Analyze strategy effectiveness
    for strategy, data in meta.get("strategy_effectiveness", {}).items():
        if data["attempts"] >= 5:
            success_rate = data["successes"] / data["attempts"]
            if success_rate < 0.4:
                suggestions.append({
                    "type": "strategy_optimization",
                    "strategy": strategy,
                    "issue": f"Strategy '{strategy}' has {success_rate:.1%} success rate",
                    "recommendation": "Consider alternative strategy",
                    "priority": "MED"
                })
    
    print(f"\n📋 Meta-Learning Suggestions ({len(suggestions)} total)\n")
    for s in suggestions[:10]:
        priority_icon = "🔴" if s["priority"] == "HIGH" else "🟡" if s["priority"] == "MED" else "🟢"
        print(f"  {priority_icon} [{s['type']}]")
        print(f"      Issue: {s.get('issue', 'N/A')}")
        print(f"      → {s.get('recommendation', 'N/A')}")
        print()
    
    return suggestions

def generate_report():
    """Generate comprehensive meta-learning report."""
    meta = load_meta()
    
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_learnings_analyzed": len(meta.get("generalization_scores", {})),
        "task_types_tracked": len(meta.get("task_complexity_map", {})),
        "strategies_tracked": len(meta.get("strategy_effectiveness", {})),
        "learning_history_size": len(meta.get("learning_history", [])),
        "patterns": meta.get("patterns", {}),
        "generalization_scores": meta.get("generalization_scores", {}),
        "suggestions": suggest_improvements()
    }
    
    print(f"""
📊 Meta-Learning Core Report
{'=' * 50}
Generated: {report['generated_at'][:19]}

Learnings:
  Total Analyzed: {report['total_learnings_analyzed']}
  High Generalization (>0.7): {sum(1 for s in meta.get('generalization_scores', {}).values() if s.get('score', 0) > 0.7)}
  Low Generalization (<0.3): {sum(1 for s in meta.get('generalization_scores', {}).values() if s.get('score', 0) < 0.3)}

Task Tracking:
  Task Types Tracked: {report['task_types_tracked']}
  Strategies Tracked: {report['strategies_tracked']}
  Learning History: {report['learning_history_size']} entries

Top Patterns:
""")
    
    patterns = meta.get("patterns", {})
    for ptype, data in sorted(patterns.items(), key=lambda x: -x[1].get("count", 0))[:5]:
        print(f"  {ptype}: {data.get('count', 0)} learnings")
    
    print(f"\nSuggestions: {len(report['suggestions'])}")
    
    # Save report
    report_file = WORKSPACE / "docs" / "meta_learning_report.json"
    report_file.write_text(json.dumps(report, indent=2))
    print(f"\n📄 Report saved: {report_file}")
    
    return report

def score_learnings():
    """Calculate and display generalization scores."""
    meta = load_meta()
    kg = load_kg()
    
    learnings = [
        (name, e) for name, e in kg.get("entities", {}).items()
        if e.get("type") == "learning"
    ]
    
    if not learnings:
        print("[*] No learnings found. Run --analyze first.")
        return
    
    scores = calculate_generalization_scores(learnings)
    meta["generalization_scores"] = scores
    save_meta(meta)
    
    print(f"\n📊 Generalization Scores ({len(scores)} learnings)\n")
    
    for name, data in sorted(scores.items(), key=lambda x: -x[1].get("score", 0))[:20]:
        score = data.get("score", 0)
        bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
        print(f"  [{bar}] {score:.2f} {name[:40]}")
        print(f"         access={data.get('access_count', 0)}, age={data.get('age_days', 0)}d, priority={data.get('priority', 'MED')}")
    
    avg = sum(s.get("score", 0) for s in scores.values()) / max(len(scores), 1)
    print(f"\n  Average Score: {avg:.2f}")

def main():
    parser = argparse.ArgumentParser(description="Meta Learning Core")
    parser.add_argument("--analyze", action="store_true", help="Analyze learnings")
    parser.add_argument("--score", action="store_true", help="Calculate generalization scores")
    parser.add_argument("--suggest", action="store_true", help="Suggest improvements")
    parser.add_argument("--report", action="store_true", help="Generate meta-learning report")
    parser.add_argument("--adapt", metavar="TASK_JSON", help="Get adapted strategy for task")
    parser.add_argument("--record", nargs=3, metavar=("TYPE", "STRATEGY", "SUCCESS"), help="Record task outcome")
    
    args = parser.parse_args()
    
    init_dirs()
    
    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(0)
    
    if args.analyze:
        analyze_learnings()
    
    if args.score:
        score_learnings()
    
    if args.suggest:
        suggest_improvements()
    
    if args.report:
        generate_report()
    
    if args.adapt:
        try:
            task = json.loads(args.adapt)
        except:
            task = {"type": args.adapt}
        result = get_adapted_strategy(task)
        print(f"\n🔧 Adapted Strategy for {result['task_key']}:")
        print(f"   Complexity: {result['complexity']}")
        print(f"   Strategy: {result['strategy']}")
        if result['insights']:
            print(f"   Insights:")
            for i in result['insights']:
                print(f"     • {i}")
    
    if args.record:
        task_type, strategy, success = args.record
        task = {"type": task_type, "strategy": strategy}
        record_task_outcome(task, success.lower() == "true")
        print(f"[*] Recorded: {task_type} with {strategy} -> {success}")

if __name__ == "__main__":
    main()
