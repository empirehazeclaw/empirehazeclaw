#!/usr/bin/env python3
"""
Evolver Integration - Phase 5
============================
Integrates Evolver with unified learning system.
Reads KG state, triggers evolver on stagnation, validates mutations.

Usage:
    python3 evolver_integration.py --status        # Check evolver status
    python3 evolver_integration.py --trigger       # Trigger evolver manually
    python3 evolver_integration.py --validate      # Validate last mutation
    python3 evolver_integration.py --watch         # Watch for stagnation triggers
"""

import json
import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
KG_FILE = WORKSPACE / "memory" / "kg" / "knowledge_graph.json"
SIGNAL_FILE = WORKSPACE / "memory" / "evaluations" / "learning_loop_signal.json"
MUTATIONS_FILE = WORKSPACE / "memory" / "evaluations" / "strategy_mutations.json"
CONFIG_FILE = WORKSPACE / "config" / "learning_config.json"

# Evolver paths
EVOLVER_SCRIPT = Path("/home/clawbot/.openclaw/workspace/scripts/run_smart_evolver.sh")
EVOLVER_BRIDGE = Path("/home/clawbot/.openclaw/workspace/scripts/evolver_signal_bridge.py")
STAGNATION_BREAKER = Path("/home/clawbot/.openclaw/workspace/scripts/evolver_stagnation_breaker.py")

def load_kg():
    return json.loads(KG_FILE.read_text())

def load_config():
    return json.loads(CONFIG_FILE.read_text())

def get_kg_state():
    """Get current KG state for evolver."""
    kg = load_kg()
    entities = kg.get('entities', {})
    relations = kg.get('relations', [])
    if isinstance(relations, dict):
        relations = list(relations.values())
    
    # Find stagnation signals
    stagnation_signals = []
    
    # Check for repeated patterns
    gene_counts = {}
    for entity in entities.values():
        gene = entity.get('gene', entity.get('type', 'unknown'))
        gene_counts[gene] = gene_counts.get(gene, 0) + 1
    
    # Find repeated genes (stagnation indicator)
    for gene, count in gene_counts.items():
        if count > 3:
            stagnation_signals.append({
                'signal': f'gene_{gene}_repeated_{count}x',
                'gene': gene,
                'count': count
            })
    
    # Check indexes for patterns
    if 'indexes' in kg:
        by_type = kg['indexes'].get('by_type', {})
        for entity_type, names in by_type.items():
            if len(names) > 50:
                stagnation_signals.append({
                    'signal': f'type_{entity_type}_saturated',
                    'type': entity_type,
                    'count': len(names)
                })
    
    return {
        'entities': len(entities),
        'relations': len(relations),
        'stagnation_signals': stagnation_signals,
        'gene_distribution': gene_counts
    }

def check_stagnation():
    """Check if system is stagnating."""
    kg_state = get_kg_state()
    
    stagnation_detected = False
    reasons = []
    
    # Check for repeated genes
    for signal in kg_state['stagnation_signals']:
        if 'repeated' in signal.get('signal', ''):
            count = signal.get('count', 0)
            if count > 5:
                stagnation_detected = True
                reasons.append(f"Gene '{signal.get('gene')}' repeated {count}x")
    
    # Check KG growth rate
    # (Would need historical data for this)
    
    return {
        'stagnant': stagnation_detected,
        'reasons': reasons,
        'kg_state': kg_state
    }

def trigger_evolver():
    """Trigger evolver to generate new strategies."""
    print("\n🚀 Triggering Evolver...")
    
    # Get KG state for signal bridge
    kg_state = get_kg_state()
    print(f"   KG State: {kg_state['entities']} entities, {len(kg_state['stagnation_signals'])} stagnation signals")
    
    # Check if stagnation
    stagnation = check_stagnation()
    if stagnation['stagnant']:
        print(f"   ⚠️  Stagnation detected: {', '.join(stagnation['reasons'])}")
        print(f"   🔧 Forcing repair strategy...")
    else:
        print(f"   ✅ No stagnation detected")
    
    # Run evolver via signal bridge
    if EVOLVER_BRIDGE.exists():
        print(f"\n   Running evolver_signal_bridge...")
        try:
            result = subprocess.run(
                ["python3", str(EVOLVER_BRIDGE)],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0:
                print(f"   ✅ Evolver signal bridge completed")
                print(f"   Output: {result.stdout[:200]}...")
            else:
                print(f"   ⚠️  Evolver signal bridge returned: {result.returncode}")
        except Exception as e:
            print(f"   ❌ Error running evolver: {e}")
    
    # Run smart evolver
    if EVOLVER_SCRIPT.exists():
        print(f"\n   Running smart evolver...")
        try:
            result = subprocess.run(
                ["bash", str(EVOLVER_SCRIPT)],
                capture_output=True, text=True, timeout=180
            )
            if result.returncode == 0:
                print(f"   ✅ Evolver completed successfully")
                # Extract key info
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'finished' in line.lower() or 'complete' in line.lower():
                        print(f"      {line.strip()}")
            else:
                print(f"   ⚠️  Evolver returned: {result.returncode}")
        except Exception as e:
            print(f"   ❌ Error running evolver: {e}")
    
    return True

def validate_last_mutation():
    """Validate the most recent strategy mutation."""
    print("\n🔍 Validating last mutation...")
    
    mutations = []
    if MUTATIONS_FILE.exists():
        try:
            mutations = json.loads(MUTATIONS_FILE.read_text())
            if isinstance(mutations, dict):
                mutations = mutations.get('mutations', [])
        except:
            mutations = []
    
    if not mutations:
        print("   ⚠️  No mutations found")
        return None
    
    latest = mutations[-1]
    print(f"   Latest mutation: {latest.get('id', 'unknown')}")
    print(f"   Strategy: {latest.get('strategy', latest.get('mutation_type', 'unknown'))}")
    print(f"   Timestamp: {latest.get('timestamp', 'unknown')}")
    
    # Validate against KG
    kg = load_kg()
    entity_name = latest.get('id', latest.get('strategy', 'unknown'))
    
    if entity_name in kg.get('entities', {}):
        print(f"   ✅ Mutation validated in KG")
        entity = kg['entities'][entity_name]
        print(f"      Type: {entity.get('type', 'unknown')}")
        print(f"      Provenance: {entity.get('provenance', 'unknown')}")
    else:
        print(f"   ⚠️  Mutation not yet in KG (pending sync)")
    
    return latest

def show_status():
    """Show evolver integration status."""
    stagnation = check_stagnation()
    kg_state = get_kg_state()
    config = load_config()
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║           EVOLVER INTEGRATION - STATUS                   ║
╠══════════════════════════════════════════════════════════╣
║  Stagnation Status: {'STAGNANT ⚠️' if stagnation['stagnant'] else 'HEALTHY ✅'}                           ║""")
    
    if stagnation['reasons']:
        print(f"║  Reasons:                                            ║")
        for reason in stagnation['reasons']:
            print(f"║    - {reason:<47}║")
    
    print(f"""╠══════════════════════════════════════════════════════════╣
║  KG State:                                                ║
║    Entities: {kg_state['entities']:<47}║
║    Relations: {len(kg_state.get('relations', [])) if isinstance(kg_state.get('relations'), list) else 'N/A':<45}║
║    Stagnation Signals: {len(kg_state['stagnation_signals']):<38}║
╠══════════════════════════════════════════════════════════╣
║  Config:                                                   ║
║    Stagnation Threshold: {config.get('exploration_config', {}).get('stagnation_threshold', 5):<33}║
║    Exploration Rate: {config.get('exploration_config', {}).get('rate', 0):.0%}                                     ║
╠══════════════════════════════════════════════════════════╣
║  Scripts:                                                  ║
║    Smart Evolver: {'✅' if EVOLVER_SCRIPT.exists() else '❌'} available                              ║
║    Signal Bridge: {'✅' if EVOLVER_BRIDGE.exists() else '❌'} available                              ║
║    Stagnation Breaker: {'✅' if STAGNATION_BREAKER.exists() else '❌'} available              ║
╚══════════════════════════════════════════════════════════╝""")

def main():
    parser = argparse.ArgumentParser(description="Evolver Integration")
    parser.add_argument("--status", action="store_true", help="Check status")
    parser.add_argument("--trigger", action="store_true", help="Trigger evolver")
    parser.add_argument("--validate", action="store_true", help="Validate last mutation")
    parser.add_argument("--watch", action="store_true", help="Watch for stagnation")
    parser.add_argument("--check", action="store_true", help="Check stagnation")
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    if args.status:
        show_status()
    
    if args.check:
        stagnation = check_stagnation()
        print(f"\nStagnation: {stagnation['stagnant']}")
        if stagnation['reasons']:
            print("Reasons:")
            for r in stagnation['reasons']:
                print(f"  - {r}")
    
    if args.trigger:
        trigger_evolver()
    
    if args.validate:
        validate_last_mutation()

if __name__ == "__main__":
    main()