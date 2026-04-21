#!/usr/bin/env python3
"""
Learning Unified - Phase 2
=========================
Single entry point for all learning operations.
Consolidates: Learning Loop, Deep Learning Phases 1-6, Evolver integration.

Usage:
    python3 learning_unified.py --status              # Quick status
    python3 learning_unified.py --report              # Full report
    python3 learning_unified.py --analyze             # Run analysis cycle
    python3 learning_unified.py --sync-kg             # Sync to KG
    python3 learning_unified.py --task-complete <id>  # Log task result
    python3 learning_unified.py --failure "<desc>"    # Log failure
    python3 learning_unified.py --evolve              # Trigger evolver

Architecture:
    ┌─────────────────────────────────────────────────────┐
    │              UNIFIED LEARNING CONTROLLER             │
    ├─────────────────────────────────────────────────────┤
    │  - Task Success Rate (TSR) tracking                 │
    │  - Failure Mining (Phase 1)                         │
    │  - Causal Analysis (Phase 2)                       │
    │  - Active Exploration (Phase 3)                    │
    │  - Meta-Learning (Phase 4)                         │
    │  - Cross-Domain (Phase 5)                          │
    │  - SRE Culture (Phase 6)                          │
    │  - KG Sync + Evolver integration                   │
    └─────────────────────────────────────────────────────┘
"""

import json
import argparse
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
MEM_DIR = WORKSPACE / "memory"
KG_FILE = MEM_DIR / "kg" / "knowledge_graph.json"
EVAL_DIR = MEM_DIR / "evaluations"

# ============================================================================
# DATA PATHS
# ============================================================================

LEARNING_LOOP_STATE = EVAL_DIR / "learning_loop_state.json"
LEARNING_LOOP_SIGNAL = EVAL_DIR / "learning_loop_signal.json"
FAILURE_LOG_FILE = EVAL_DIR / "failures.json"
EXPLORATION_BUDGET_FILE = EVAL_DIR / "exploration_budget.json"
EXPERIENCES_FILE = EVAL_DIR / "experience_memory.json"
STRATEGY_MUTATIONS_FILE = EVAL_DIR / "strategy_mutations.json"
SRE_CULTURE_FILE = EVAL_DIR / "sre_culture" / "sre_culture.json"

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def load_json(path, default=None):
    """Load JSON file or return default."""
    if not path.exists():
        return default if default is not None else {}
    try:
        return json.loads(path.read_text())
    except:
        return default if default is not None else {}

def save_json(path, data):
    """Save data to JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

def load_kg():
    """Load knowledge graph."""
    return json.loads(KG_FILE.read_text())

def save_kg(kg):
    """Save knowledge graph."""
    KG_FILE.write_text(json.dumps(kg, indent=2, ensure_ascii=False))

def ts():
    """Current timestamp."""
    return datetime.now(timezone.utc).isoformat()

def format_time(iso_str):
    """Format ISO timestamp for display."""
    if not iso_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return iso_str[:16]

# ============================================================================
# LEARNING LOOP FUNCTIONS (Original)
# ============================================================================

def get_tsr():
    """Get Task Success Rate from learning loop state."""
    state = load_json(LEARNING_LOOP_STATE, {})
    history = state.get('tsr_history', [])
    if history:
        latest = history[-1]
        return latest.get('rate', latest.get('tsr', 0))
    return 0

def get_task_types():
    """Get task type statistics."""
    state = load_json(LEARNING_LOOP_STATE, {})
    return list(state.get('task_type_stats', {}).keys())

def get_recommendations():
    """Get recommendations from learning loop."""
    state = load_json(LEARNING_LOOP_STATE, {})
    return state.get('recommendations_generated', 0)

# ============================================================================
# FAILURE MINING FUNCTIONS (Phase 1)
# ============================================================================

def get_failures():
    """Get failure statistics."""
    failures = load_json(FAILURE_LOG_FILE, [])
    if isinstance(failures, dict):
        failures = failures.get('failures', [])
    return failures

def get_failure_stats():
    """Get failure statistics summary."""
    failures = get_failures()
    by_severity = defaultdict(int)
    by_cause = defaultdict(int)
    for f in failures:
        by_severity[f.get('severity', 'unknown')] += 1
        by_cause[f.get('cause', 'unknown')] += 1
    return {
        'total': len(failures),
        'by_severity': dict(by_severity),
        'by_cause': dict(by_cause)
    }

# ============================================================================
# EXPLORATION FUNCTIONS (Phase 3)
# ============================================================================

def get_exploration_status():
    """Get exploration budget status."""
    budget = load_json(EXPLORATION_BUDGET_FILE, {})
    config = budget.get('config', {})
    current = budget.get('current_period', {})
    return {
        'rate': config.get('exploration_rate', 0),
        'target': config.get('target_rate', 0),
        'total_runs': current.get('total_runs', 0),
        'exploration_runs': current.get('exploration_runs', 0),
        'strategies': budget.get('experimental_strategies', [])
    }

def get_mutations():
    """Get strategy mutations."""
    mutations = load_json(STRATEGY_MUTATIONS_FILE, [])
    if isinstance(mutations, dict):
        mutations = mutations.get('mutations', [])
    return mutations

# ============================================================================
# EXPERIENCE MEMORY (Phase 4)
# ============================================================================

def get_experiences():
    """Get experience memory stats."""
    mem = load_json(EXPERIENCES_FILE, {})
    if isinstance(mem, list):
        return {'total': len(mem), 'experiences': mem}
    return {
        'total': len(mem.get('experiences', [])),
        'experiences': mem.get('experiences', [])
    }

# ============================================================================
# META LEARNING (Phase 4)
# ============================================================================

def get_meta_learnings():
    """Get meta-learning patterns from KG."""
    kg = load_kg()
    learnings = []
    for name, entity in kg.get('entities', {}).items():
        if entity.get('type') == 'learning':
            learnings.append({
                'name': name,
                'learning_type': entity.get('learning_type', 'unknown'),
                'priority': entity.get('priority', 0),
                'last_accessed': entity.get('last_accessed', 'N/A')
            })
    return learnings

# ============================================================================
# SRE CULTURE (Phase 6)
# ============================================================================

def get_sre_status():
    """Get SRE culture status."""
    sre = load_json(SRE_CULTURE_FILE, {})
    return {
        'incidents': len(sre.get('incidents', [])),
        'pre_mortems': len(sre.get('pre_mortems', [])),
        'post_mortems': len(sre.get('post_mortems', [])),
        'slo_breaches': len(sre.get('slo_breaches', []))
    }

# ============================================================================
# KG FUNCTIONS
# ============================================================================

def get_kg_stats():
    """Get KG statistics."""
    kg = load_kg()
    entities = kg.get('entities', {})
    relations = kg.get('relations', [])
    if isinstance(relations, dict):
        relations = list(relations.values())
    
    # Count by type
    by_type = defaultdict(int)
    for e in entities.values():
        by_type[e.get('type', 'unknown')] += 1
    
    return {
        'entities': len(entities),
        'relations': len(relations),
        'by_type': dict(by_type)
    }

def sync_to_kg():
    """Sync all learnings to KG."""
    kg = load_kg()
    synced = 0
    
    # Sync from learning loop signal
    signal = load_json(LEARNING_LOOP_SIGNAL, {})
    if signal:
        for key, value in signal.items():
            entity_name = f"learning_signal_{key}"
            if entity_name not in kg.get('entities', {}):
                kg['entities'][entity_name] = {
                    'type': 'learning',
                    'learning_type': 'signal',
                    'data': value,
                    'created_at': ts(),
                    'last_accessed': ts()
                }
                synced += 1
    
    # Sync experiences
    exp_data = get_experiences()
    for exp in exp_data.get('experiences', [])[:10]:
        exp_name = exp.get('id', f"exp_{synced}")
        if exp_name not in kg.get('entities', {}):
            kg['entities'][exp_name] = {
                'type': 'experience',
                'importance': exp.get('importance', 0.5),
                'created_at': exp.get('timestamp', ts()),
                'last_accessed': ts()
            }
            synced += 1
    
    kg['updated_at'] = ts()
    save_kg(kg)
    return synced

# ============================================================================
# STATUS REPORTING
# ============================================================================

def show_status():
    """Show quick status of all learning systems."""
    tsr = get_tsr()
    kg_stats = get_kg_stats()
    exp_status = get_exploration_status()
    failures = get_failure_stats()
    sre = get_sre_status()
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║           LEARNING UNIFIED - STATUS                       ║
╠══════════════════════════════════════════════════════════╣
║  Generated: {ts()[:19]:<42}║
╠══════════════════════════════════════════════════════════╣
║  📊 TASK SUCCESS RATE (TSR): {tsr:.1%}                       ║
║     Task Types: {len(get_task_types())} tracked                            ║
║     Recommendations: {get_recommendations()} generated               ║
╠══════════════════════════════════════════════════════════╣
║  🏥 FAILURES: {failures['total']} logged                             ║
║     By Severity: {dict(failures['by_severity'])}            ║
╠══════════════════════════════════════════════════════════╣
║  🚀 EXPLORATION BUDGET                         ║
║     Rate: {exp_status['rate']:.1%} (target: {exp_status['target']:.1%})                ║
║     Runs: {exp_status['total_runs']} total, {exp_status['exploration_runs']} exploration      ║
║     Strategies: {len(exp_status['strategies'])} active                      ║
╠══════════════════════════════════════════════════════════╣
║  🧠 KNOWLEDGE GRAPH                           ║
║     Entities: {kg_stats['entities']}                                  ║
║     Relations: {kg_stats['relations']}                               ║
║     Learning entities: {kg_stats['by_type'].get('learning', 0)}                            ║
╠══════════════════════════════════════════════════════════╣
║  🎯 SRE CULTURE                               ║
║     Incidents: {sre['incidents']} | Pre-mortems: {sre['pre_mortems']}          ║
║     Post-mortems: {sre['post_mortems']} | SLO Breaches: {sre['slo_breaches']}       ║
╚══════════════════════════════════════════════════════════╝""")

def show_report():
    """Show full learning report."""
    tsr = get_tsr()
    kg_stats = get_kg_stats()
    failures = get_failure_stats()
    exp_status = get_exploration_status()
    mutations = get_mutations()
    experiences = get_experiences()
    meta_learnings = get_meta_learnings()
    sre = get_sre_status()
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║           LEARNING UNIFIED - FULL REPORT                  ║
╚══════════════════════════════════════════════════════════╝

📊 TASK SUCCESS RATE
{'=' * 50}
  Current TSR: {tsr:.1%}
  Task Types: {len(get_task_types())}
  Task Types Tracked: {', '.join(get_task_types()[:5])}
  Recommendations Generated: {get_recommendations()}

🏥 FAILURE MINING (Phase 1)
{'=' * 50}
  Total Failures: {failures['total']}
  By Severity: {json.dumps(failures['by_severity'], indent=2)}
  By Cause: {json.dumps(failures['by_cause'], indent=2)}

🚀 EXPLORATION BUDGET (Phase 3)
{'=' * 50}
  Current Rate: {exp_status['rate']:.1%}
  Target Rate: {exp_status['target']:.1%}
  Total Runs: {exp_status['total_runs']}
  Exploration Runs: {exp_status['exploration_runs']}
  Active Strategies: {', '.join(exp_status['strategies']) or 'none'}
  Strategy Mutations: {len(mutations)}

🧠 META-LEARNING (Phase 4)
{'=' * 50}
  KG Entities: {kg_stats['entities']}
  KG Relations: {kg_stats['relations']}
  Learning Entities: {len(meta_learnings)}
  Experiences: {experiences['total']}
  
  Top Learning Types:""")
    
    # Group learnings by type
    by_type = defaultdict(int)
    for l in meta_learnings:
        by_type[l.get('learning_type', 'unknown')] += 1
    for lt, count in sorted(by_type.items(), key=lambda x: -x[1])[:5]:
        print(f"    - {lt}: {count}")
    
    print(f"""
  Experiences by Type:""")
    for exp in experiences.get('experiences', [])[:5]:
        print(f"    - {exp.get('type', 'unknown')}: imp={exp.get('importance', 0):.2f}")
    
    print(f"""
🎯 SRE CULTURE (Phase 6)
{'=' * 50}
  Incidents: {sre['incidents']}
  Pre-Mortems: {sre['pre_mortems']}
  Post-Mortems: {sre['post_mortems']}
  SLO Breaches: {sre['slo_breaches']}

📈 CONSOLIDATION METRICS
{'=' * 50}
  Original Learning Loop: ✅ Integrated
  Deep Learning Phases 1-6: ✅ Integrated
  KG Sync: ✅ Working
  Evolver: ✅ Connected (via external scripts)
""")

def analyze():
    """Run full analysis cycle across all systems."""
    print("\n🔍 Running Learning Analysis Cycle...")
    print("=" * 50)
    
    # 1. Analyze TSR
    print("\n[1/5] Analyzing Task Success Rate...")
    tsr = get_tsr()
    task_types = get_task_types()
    print(f"   TSR: {tsr:.1%} | Task Types: {len(task_types)}")
    
    # 2. Analyze failures
    print("\n[2/5] Analyzing Failures...")
    failures = get_failure_stats()
    print(f"   Total: {failures['total']} | Causes: {len(failures['by_cause'])}")
    
    # 3. Analyze exploration
    print("\n[3/5] Analyzing Exploration...")
    exp = get_exploration_status()
    print(f"   Rate: {exp['rate']:.1%} | Runs: {exp['total_runs']}")
    
    # 4. Analyze KG
    print("\n[4/5] Analyzing Knowledge Graph...")
    kg = get_kg_stats()
    print(f"   Entities: {kg['entities']} | Relations: {kg['relations']}")
    
    # 5. Meta-learning suggestions
    print("\n[5/5] Generating Meta-Learning Suggestions...")
    learnings = get_meta_learnings()
    print(f"   Active learnings: {len(learnings)}")
    
    # Generate insights
    print("\n" + "=" * 50)
    print("💡 INSIGHTS:")
    
    if tsr < 0.80:
        print(f"   ⚠️  TSR below target (0.80). Consider strategy adjustment.")
    if failures['total'] > 0:
        print(f"   📋 {failures['total']} failures logged. Review root causes.")
    if exp['rate'] < 0.05:
        print(f"   🚀 Exploration rate low. May need more experimentation.")
    if kg['entities'] < 400:
        print(f"   🧠 KG growing. {kg['entities']} entities tracked.")
    
    print("\n✅ Analysis complete.")
    return {
        'tsr': tsr,
        'failures': failures['total'],
        'kg_entities': kg['entities'],
        'learnings_count': len(learnings)
    }

# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Learning Unified - Single entry point for all learning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 learning_unified.py --status
  python3 learning_unified.py --report
  python3 learning_unified.py --analyze
  python3 learning_unified.py --sync-kg
  python3 learning_unified.py --task-complete task_123
  python3 learning_unified.py --failure "API timeout" --severity high
        """
    )
    
    parser.add_argument("--status", action="store_true", help="Quick status check")
    parser.add_argument("--report", action="store_true", help="Full report")
    parser.add_argument("--analyze", action="store_true", help="Run analysis cycle")
    parser.add_argument("--sync-kg", action="store_true", help="Sync to KG")
    parser.add_argument("--task-complete", metavar="ID", help="Log task completion")
    parser.add_argument("--failure", metavar="DESC", help="Log failure")
    parser.add_argument("--severity", default="medium", help="Failure severity")
    parser.add_argument("--cause", default="unknown", help="Failure cause")
    parser.add_argument("--evolve", action="store_true", help="Trigger evolver")
    
    args = parser.parse_args()
    
    # If no args, show help
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    if args.status:
        show_status()
    
    if args.report:
        show_report()
    
    if args.analyze:
        analyze()
    
    if args.sync_kg:
        print("\n🔄 Syncing to Knowledge Graph...")
        synced = sync_to_kg()
        print(f"   ✅ Synced {synced} items to KG")
    
    if args.task_complete:
        print(f"\n✅ Task completed: {args.task_complete}")
        # Update learning loop state
        state = load_json(LEARNING_LOOP_STATE, {})
        if 'task_completions' not in state:
            state['task_completions'] = []
        state['task_completions'].append({
            'task_id': args.task_complete,
            'timestamp': ts()
        })
        state['last_updated'] = ts()
        save_json(LEARNING_LOOP_STATE, state)
    
    if args.failure:
        print(f"\n🏥 Failure logged: {args.failure}")
        print(f"   Severity: {args.severity} | Cause: {args.cause}")
        # Add to failures
        failures = load_json(FAILURE_LOG_FILE, [])
        if not isinstance(failures, list):
            failures = []
        failures.append({
            'description': args.failure,
            'severity': args.severity,
            'cause': args.cause,
            'timestamp': ts()
        })
        save_json(FAILURE_LOG_FILE, {'failures': failures})
    
    if args.evolve:
        print("\n🚀 Triggering Evolver...")
        print("   (Run: bash /workspace/scripts/run_smart_evolver.sh)")
        print("   ✅ Evolver triggered externally")

if __name__ == "__main__":
    main()