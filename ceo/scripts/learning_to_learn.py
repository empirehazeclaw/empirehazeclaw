#!/usr/bin/env python3
"""
Learning-to-Learn - Phase 4, Day 2
===================================
Identifies how different task types learn at different rates and optimizes accordingly.
"""

import json
import argparse
import sys
import math
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
LTQL_DIR = WORKSPACE / "memory" / "evaluations" / "learning_to_learn"
LTQL_FILE = LTQL_DIR / "learning_rates.json"
KG_PATH = WORKSPACE / "memory" / "kg" / "knowledge_graph.json"

FAST_LEARNING_THRESHOLD = 0.3
SLOW_LEARNING_THRESHOLD = 0.7

def init_dirs():
    LTQL_DIR.mkdir(parents=True, exist_ok=True)
    if not LTQL_FILE.exists():
        LTQL_FILE.write_text(json.dumps({
            "task_learning_rates": {},
            "curriculum": [],
            "retention_scores": {},
            "learning_trajectories": {},
            "version": "1.0"
        }))

def load_ltql():
    init_dirs()
    return json.loads(LTQL_FILE.read_text())

def save_ltql(data):
    LTQL_FILE.write_text(json.dumps(data, indent=2))

def load_kg():
    if KG_PATH.exists():
        return json.load(open(KG_PATH))
    return {"entities": {}, "relations": {}}

def analyze_learning_rates():
    ltql = load_ltql()
    kg = load_kg()
    
    task_history = []
    for name, entity in kg.get("entities", {}).items():
        if entity.get("type") == "learning":
            access_count = entity.get("access_count", 1)
            created = entity.get("created", "")
            task_history.append({
                "task_type": entity.get("learning_type", "unknown"),
                "access_count": access_count,
                "created": created,
                "source": "kg"
            })
    
    by_type = defaultdict(list)
    for entry in task_history:
        by_type[entry["task_type"]].append(entry)
    
    learning_rates = {}
    
    for task_type, entries in by_type.items():
        if not entries:
            continue
        
        access_counts = [e.get("access_count", 1) for e in entries if "access_count" in e]
        
        if access_counts:
            avg_access = sum(access_counts) / len(access_counts)
            now = datetime.now(timezone.utc)
            ages = []
            for e in entries:
                if "created" in e and e["created"]:
                    try:
                        age = (now - datetime.fromisoformat(e["created"].replace("Z", "+00:00"))).days
                        ages.append(age)
                    except:
                        pass
            
            avg_age = sum(ages) / len(ages) if ages else 1
            learning_rate = avg_access / max(avg_age, 1)
            normalized_rate = min(learning_rate / 2, 1.0)
            
            category = categorize_learning(learning_rate)
            
            learning_rates[task_type] = {
                "learning_rate": normalized_rate,
                "raw_rate": learning_rate,
                "avg_access_count": avg_access,
                "avg_age_days": avg_age,
                "sample_size": len(entries),
                "category": category
            }
    
    ltql["task_learning_rates"] = learning_rates
    save_ltql(ltql)
    
    print(f"Learning Rate Analysis ({len(learning_rates)} task types)")
    print("=" * 50)
    
    for task_type, data in sorted(learning_rates.items(), key=lambda x: -x[1]["learning_rate"]):
        category = data["category"]
        icon = "fast" if category == "fast" else "slow" if category == "slow" else "medium"
        print(f"  [{icon}] {task_type}: {data['learning_rate']:.2f}")
        print(f"       samples={data['sample_size']}, avg_access={avg_access:.1f}, age={avg_age:.1f}d")
    
    return learning_rates

def categorize_learning(learning_rate):
    if learning_rate >= 1.0:
        return "fast"
    elif learning_rate >= 0.3:
        return "medium"
    elif learning_rate >= 0.1:
        return "slow"
    else:
        return "very_slow"

def get_fast_tasks(limit=10):
    ltql = load_ltql()
    rates = ltql.get("task_learning_rates", {})
    
    fast = [
        (task, data) for task, data in rates.items()
        if data["category"] in ["fast", "medium"]
    ]
    
    print(f"\nFast-Learning Tasks ({len(fast)} total)")
    print("=" * 50)
    for task, data in sorted(fast, key=lambda x: -x[1]["learning_rate"])[:limit]:
        print(f"  {task}")
        print(f"    Rate: {data['learning_rate']:.2f} | Samples: {data['sample_size']}")
    
    return fast

def get_slow_tasks(limit=10):
    ltql = load_ltql()
    rates = ltql.get("task_learning_rates", {})
    
    slow = [
        (task, data) for task, data in rates.items()
        if data["category"] in ["slow", "very_slow"]
    ]
    
    print(f"\nSlow-Learning Tasks ({len(slow)} total)")
    print("=" * 50)
    for task, data in sorted(slow, key=lambda x: x[1]["learning_rate"])[:limit]:
        print(f"  {task}")
        print(f"    Rate: {data['learning_rate']:.2f} | Samples: {data['sample_size']}")
        print(f"    -> Needs more attempts or different strategy")
    
    return slow

def generate_curriculum():
    ltql = load_ltql()
    rates = ltql.get("task_learning_rates", {})
    
    curriculum = []
    
    fast = sorted(
        [(t, d) for t, d in rates.items() if d["category"] == "fast"],
        key=lambda x: -x[1]["learning_rate"]
    )
    medium = sorted(
        [(t, d) for t, d in rates.items() if d["category"] == "medium"],
        key=lambda x: -x[1]["learning_rate"]
    )
    slow = sorted(
        [(t, d) for t, d in rates.items() if d["category"] in ["slow", "very_slow"]],
        key=lambda x: x[1]["learning_rate"]
    )
    
    curriculum.append({
        "phase": 1,
        "name": "Quick Wins",
        "description": "Build confidence with fast-learning tasks",
        "tasks": [t for t, _ in fast[:5]]
    })
    
    curriculum.append({
        "phase": 2,
        "name": "Core Skills",
        "description": "Develop fundamental capabilities",
        "tasks": [t for t, _ in medium[:5]]
    })
    
    curriculum.append({
        "phase": 3,
        "name": "Mastery Training",
        "description": "Deep practice for challenging tasks",
        "tasks": [t for t, _ in slow[:5]]
    })
    
    ltql["curriculum"] = curriculum
    save_ltql(ltql)
    
    print(f"\nLearning Curriculum")
    print("=" * 40)
    for phase in curriculum:
        print(f"Phase {phase['phase']}: {phase['name']}")
        print(f"  {phase['description']}")
        for task in phase["tasks"]:
            print(f"    -> {task}")
        print()
    
    return curriculum

def optimize_learning_for_type(task_type):
    ltql = load_ltql()
    rates = ltql.get("task_learning_rates", {})
    
    if task_type not in rates:
        return {
            "task_type": task_type,
            "learning_rate": None,
            "strategy": "default",
            "recommendations": [
                "Start with simple examples",
                "Gradually increase complexity",
                "Track success rate per attempt"
            ]
        }
    
    data = rates[task_type]
    category = data["category"]
    
    if category == "fast":
        recommendations = [
            "High learning rate detected - can increase task complexity",
            "Reduce redundant practice once mastered",
            "Move quickly to next concept"
        ]
        strategy = {
            "attempts_before_mastery": 2,
            "complexity_increase_rate": "fast",
            "retention_check_frequency": "low"
        }
    elif category == "medium":
        recommendations = [
            "Standard learning curve",
            "Balanced practice recommended",
            "Monitor for stagnation after 5 attempts"
        ]
        strategy = {
            "attempts_before_mastery": 5,
            "complexity_increase_rate": "moderate",
            "retention_check_frequency": "medium"
        }
    else:
        recommendations = [
            "Slower learning detected - increase practice",
            "Consider breaking task into smaller steps",
            "Use spaced repetition for retention",
            "Consider delegation or assistance"
        ]
        strategy = {
            "attempts_before_mastery": 10,
            "complexity_increase_rate": "slow",
            "retention_check_frequency": "high",
            "enable_assistance": True
        }
    
    return {
        "task_type": task_type,
        "learning_rate": data["learning_rate"],
        "category": category,
        "strategy": strategy,
        "recommendations": recommendations
    }

def generate_report():
    ltql = load_ltql()
    rates = ltql.get("task_learning_rates", {})
    
    if not rates:
        analyze_learning_rates()
        rates = ltql.get("task_learning_rates", {})
    
    fast_count = sum(1 for d in rates.values() if d["category"] == "fast")
    medium_count = sum(1 for d in rates.values() if d["category"] == "medium")
    slow_count = sum(1 for d in rates.values() if d["category"] in ["slow", "very_slow"])
    
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "task_types_analyzed": len(rates),
        "fast_learners": fast_count,
        "medium_learners": medium_count,
        "slow_learners": slow_count,
        "curriculum_phases": len(ltql.get("curriculum", [])),
        "recommendations": []
    }
    
    if slow_count > fast_count:
        report["recommendations"].append({
            "type": "curriculum_imbalance",
            "issue": "More slow learners than fast",
            "recommendation": "Consider simplifying task definitions"
        })
    
    print(f"Learning-to-Learn Report")
    print("=" * 50)
    print(f"Generated: {report['generated_at'][:19]}")
    print(f"Task Types Analyzed: {report['task_types_analyzed']}")
    print(f"  Fast: {fast_count}")
    print(f"  Medium: {medium_count}")
    print(f"  Slow: {slow_count}")
    print(f"Curriculum: {report['curriculum_phases']} phases")
    print(f"Recommendations: {len(report['recommendations'])}")
    
    report_file = WORKSPACE / "docs" / "learning_to_learn_report.json"
    report_file.write_text(json.dumps(report, indent=2))
    print(f"Report saved: {report_file}")
    
    return report

def main():
    parser = argparse.ArgumentParser(description="Learning-to-Learn")
    parser.add_argument("--analyze", action="store_true", help="Analyze learning rates")
    parser.add_argument("--fast-tasks", action="store_true", help="List fast-learning tasks")
    parser.add_argument("--slow-tasks", action="store_true", help="List slow-learning tasks")
    parser.add_argument("--curriculum", action="store_true", help="Generate learning curriculum")
    parser.add_argument("--optimize", metavar="TYPE", help="Optimize strategy for task type")
    parser.add_argument("--report", action="store_true", help="Generate learning report")
    
    args = parser.parse_args()
    
    init_dirs()
    
    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(0)
    
    if args.analyze:
        analyze_learning_rates()
    
    if args.fast_tasks:
        get_fast_tasks()
    
    if args.slow_tasks:
        get_slow_tasks()
    
    if args.curriculum:
        generate_curriculum()
    
    if args.optimize:
        result = optimize_learning_for_type(args.optimize)
        print(f"\nOptimization for {result['task_type']}:")
        print(f"  Category: {result.get('category', 'unknown')}")
        lr = result.get('learning_rate')
        lr_str = f"{lr:.2f}" if lr is not None else "N/A"
        print(f"  Learning Rate: {lr_str}")
        print(f"  Strategy: {result.get('strategy', {})}")
        print(f"  Recommendations:")
        for r in result.get("recommendations", []):
            print(f"    -> {r}")
    
    if args.report:
        generate_report()

if __name__ == "__main__":
    main()
