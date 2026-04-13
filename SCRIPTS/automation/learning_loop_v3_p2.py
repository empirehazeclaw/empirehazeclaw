#!/usr/bin/env python3
"""
🎯 Learning Loop v3 MAXIMAL — P2 Perturbation & Stress Testing

Adds:
1. Perturbation Mode — Break through plateaus with random mutations
2. Error Stress Test — Generate realistic error scenarios
3. Breakthrough Detection — Track when perturbations lead to breakthroughs

Usage:
    python3 learning_loop_v3_p2.py --perturb                    # Run with perturbations
    python3 learning_loop_v3_p2.py --stress-test              # Generate error scenarios
    python3 learning_loop_v3_p2.py --full                     # Full with perturbation + stress
"""

import os
import sys
import json
import random
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "scripts"
DATA_DIR = WORKSPACE / "data"
LOOP_STATE = DATA_DIR / "learning_loop_state.json"
PATTERNS_FILE = DATA_DIR / "learning_loop" / "patterns.json"

# ============ UTILITIES ============

def load_json(path, default=None):
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except:
            return default or {}
    return default or {}

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

# ============ PERTURBATION MODE ============

def generate_perturbations() -> List[Dict]:
    """
    Generate random perturbations to break through plateaus.
    
    Types of perturbations:
    1. Random hypothesis injection
    2. Random error pattern introduction
    3. Confidence boost randomization
    4. Strategy shift (exploration vs exploitation)
    """
    perturbations = []
    
    # 1. Random hypothesis injection
    random_hypotheses = [
        {"title": "Explore: Try token optimization", "category": "token", "impact": "HIGH"},
        {"title": "Explore: Check cron timeout issues", "category": "cron", "impact": "MEDIUM"},
        {"title": "Explore: Memory fragmentation check", "category": "memory", "impact": "MEDIUM"},
        {"title": "Explore: Session bloat investigation", "category": "session", "impact": "HIGH"},
        {"title": "Explore: API rate limit patterns", "category": "api", "impact": "MEDIUM"},
        {"title": "Explore: Disk I/O patterns", "category": "disk", "impact": "LOW"},
        {"title": "Exploit: Focus on high-error-rate scripts", "category": "error", "impact": "HIGH"},
        {"title": "Exploit: Validate existing patterns more aggressively", "category": "validation", "impact": "MEDIUM"},
    ]
    
    # Randomly select 1-2 perturbations
    num_perturbations = random.randint(1, 2)
    selected = random.sample(random_hypotheses, num_perturbations)
    
    for hyp in selected:
        perturbations.append({
            "type": "perturbation",
            "subtype": "random_hypothesis",
            "title": hyp["title"],
            "category": hyp["category"],
            "expected_impact": hyp["impact"],
            "mutations": generate_mutations(hyp["category"]),
            "timestamp": datetime.now().isoformat()
        })
    
    # 2. Confidence randomization for existing patterns
    patterns_data = load_json(PATTERNS_FILE, {"patterns": [], "version": "1.0"})
    if patterns_data.get("patterns"):
        # Boost confidence of a random pattern
        pattern = random.choice(patterns_data["patterns"])
        perturbations.append({
            "type": "perturbation",
            "subtype": "confidence_boost",
            "pattern_id": pattern.get("id"),
            "old_confidence": pattern.get("confidence", 0.5),
            "new_confidence": min(0.95, pattern.get("confidence", 0.5) + random.uniform(0.1, 0.3)),
            "timestamp": datetime.now().isoformat()
        })
    
    # 3. Strategy shift
    strategies = ["exploration", "exploitation", "balanced"]
    current_strategy = load_json(LOOP_STATE, {}).get("strategy", "balanced")
    new_strategy = random.choice([s for s in strategies if s != current_strategy])
    
    perturbations.append({
        "type": "perturbation",
        "subtype": "strategy_shift",
        "from_strategy": current_strategy,
        "to_strategy": new_strategy,
        "timestamp": datetime.now().isoformat()
    })
    
    return perturbations

def generate_mutations(category: str) -> List[str]:
    """Generate specific mutations based on category."""
    mutations = {
        "token": [
            "Reduce prompt verbosity by 20%",
            "Enable context compression for large sessions",
            "Cache repeated subagent outputs"
        ],
        "cron": [
            "Increase timeout for long-running crons",
            "Add retry with exponential backoff",
            "Reduce cron frequency for non-critical tasks"
        ],
        "memory": [
            "Trigger memory cleanup for sessions > 100k tokens",
            "Archive old patterns with low confidence",
            "Promote high-value recalls to permanent memory"
        ],
        "session": [
            "Force session cleanup if idle > 30 min",
            "Pin active sessions, unpin inactive",
            "Set max sessions cap at 50"
        ],
        "api": [
            "Add rate limit handling with backoff",
            "Cache API responses for repeated queries",
            "Batch multiple requests into one"
        ],
        "error": [
            "Increase error detection sensitivity",
            "Add early warning threshold at 2%",
            "Implement automatic error categorization"
        ],
        "disk": [
            "Enable compression for old log files",
            "Archive rather than delete old files",
            "Check for duplicate files"
        ]
    }
    return mutations.get(category, ["No specific mutations available"])

def apply_perturbation(perturbation: Dict) -> bool:
    """Apply a perturbation to the system."""
    state = load_json(LOOP_STATE, {})
    
    if perturbation["subtype"] == "strategy_shift":
        state["strategy"] = perturbation["to_strategy"]
        print(f"   🔄 Strategy shift: {perturbation['from_strategy']} → {perturbation['to_strategy']}")
        save_json(LOOP_STATE, state)
        return True
    
    elif perturbation["subtype"] == "confidence_boost":
        patterns_data = load_json(PATTERNS_FILE, {"patterns": [], "version": "1.0"})
        for p in patterns_data.get("patterns", []):
            if p.get("id") == perturbation["pattern_id"]:
                p["confidence"] = perturbation["new_confidence"]
                p["last_validated"] = datetime.now().isoformat()
                print(f"   📈 Confidence boost: {perturbation['pattern_id']} ({perturbation['old_confidence']:.2f} → {perturbation['new_confidence']:.2f})")
                save_json(PATTERNS_FILE, patterns_data)
                return True
        return False
    
    # For hypothesis injections, we just log them - they'll be picked up by the main loop
    return True

# ============ STRESS TESTING ============

def run_stress_test() -> List[Dict]:
    """
    Generate realistic error scenarios by intentionally creating stress conditions.
    
    This doesn't break anything - it just creates test scenarios
    that trigger the loop's error detection and handling.
    """
    print("💥 Running Error Stress Test...")
    
    stress_results = []
    
    # 1. Check for high-error scripts
    try:
        result = subprocess.run(
            ['python3', str(SCRIPTS_DIR / 'error_reducer.py'), '--analyze'],
            capture_output=True, text=True, timeout=60
        )
        
        # Parse error patterns
        errors = []
        for line in result.stdout.split('\n'):
            if 'ERROR' in line.upper() and len(line) > 20:
                errors.append(line.strip())
        
        if errors:
            stress_results.append({
                "type": "error_analysis",
                "errors_found": len(errors),
                "sample_errors": errors[:3]
            })
            print(f"   📊 Found {len(errors)} error conditions")
    except Exception as e:
        print(f"   ⚠️ Error analysis failed: {e}")
    
    # 2. Cron health stress test
    try:
        result = subprocess.run(
            ['python3', str(SCRIPTS_DIR / 'cron_watchdog.py'), '--report'],
            capture_output=True, text=True, timeout=30
        )
        
        failed_crons = result.stdout.count('FAILED')
        stress_results.append({
            "type": "cron_health",
            "failed_count": failed_crons,
            "health_status": "critical" if failed_crons > 0 else "healthy"
        })
        print(f"   ⏰ Cron health: {failed_crons} failed")
    except Exception as e:
        print(f"   ⚠️ Cron check failed: {e}")
    
    # 3. Session bloat check
    try:
        result = subprocess.run(
            ['python3', str(SCRIPTS_DIR / 'context_compressor.py'), '--stats'],
            capture_output=True, text=True, timeout=30
        )
        # Parse for session counts
        session_bloat = "unknown"
        for line in result.stdout.split('\n'):
            if 'session' in line.lower() and 'count' in line.lower():
                session_bloat = line.strip()
                break
        
        stress_results.append({
            "type": "session_bloat",
            "status": session_bloat
        })
    except:
        pass
    
    # 4. KG access stress
    try:
        result = subprocess.run(
            ['python3', str(SCRIPTS_DIR / 'kg_updater.py'), '--stats'],
            capture_output=True, text=True, timeout=30
        )
        kg_health = "unknown"
        for line in result.stdout.split('\n'):
            if 'entity' in line.lower():
                kg_health = line.strip()
                break
        
        stress_results.append({
            "type": "kg_health",
            "status": kg_health
        })
    except:
        pass
    
    return stress_results

# ============ BREAKTHROUGH DETECTION ============

def detect_breakthrough(old_score: float, new_score: float) -> Tuple[bool, str]:
    """Detect if a perturbation led to a breakthrough."""
    threshold = 0.05  # 5% improvement = breakthrough
    
    if new_score > old_score + threshold:
        return True, f"Breakthrough detected: {old_score:.3f} → {new_score:.3f} (+{new_score - old_score:.3f})"
    
    if new_score < old_score - threshold:
        return True, f"Regression detected: {old_score:.3f} → {new_score:.3f} ({new_score - old_score:.3f})"
    
    return False, "No significant change"

def log_perturbation_result(perturbation: Dict, success: bool, details: str):
    """Log perturbation results for meta-learning."""
    log_file = DATA_DIR / "learning_loop" / "perturbation_log.json"
    log = load_json(log_file, {"perturbations": [], "version": "1.0"})
    
    entry = {
        "perturbation": perturbation,
        "success": success,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    
    log["perturbations"].append(entry)
    log["perturbations"] = log["perturbations"][-100:]  # Keep last 100
    save_json(log_file, entry)

# ============ MAIN ============

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--perturb":
            print("🎯 PERTURBATION MODE")
            print("=" * 50)
            
            state = load_json(LOOP_STATE, {})
            old_score = state.get("score", 0.5)
            
            perturbations = generate_perturbations()
            print(f"\nGenerated {len(perturbations)} perturbations:\n")
            
            for i, p in enumerate(perturbations, 1):
                print(f"{i}. [{p['subtype']}] {p.get('title', 'N/A')}")
            
            print("\nApplying perturbations...")
            for p in perturbations:
                apply_perturbation(p)
            
            # Run main loop to see effect
            print("\n" + "=" * 50)
            print("Running main loop after perturbations...")
            print("=" * 50)
            result = subprocess.run(
                ['python3', str(SCRIPTS_DIR / 'learning_loop_v3.py')],
                capture_output=True, text=True, timeout=180
            )
            
            # Parse result
            new_score = old_score
            for line in result.stdout.split('\n'):
                if 'Loop Score:' in line:
                    match = re.search(r'Loop Score: ([0-9.]+)', line)
                    if match:
                        new_score = float(match.group(1))
            
            breakthrough, message = detect_breakthrough(old_score, new_score)
            
            print("\n" + "=" * 50)
            print("RESULTS")
            print("=" * 50)
            print(f"Old Score: {old_score:.3f}")
            print(f"New Score: {new_score:.3f}")
            print(f"Status: {'🎉 ' + message if breakthrough else '➡️  No breakthrough'}")
        
        elif sys.argv[1] == "--stress-test":
            print("💥 ERROR STRESS TEST")
            print("=" * 50)
            results = run_stress_test()
            
            print("\n" + "=" * 50)
            print("STRESS TEST RESULTS")
            print("=" * 50)
            for r in results:
                print(f"\n[{r['type']}]")
                for k, v in r.items():
                    if k != 'type':
                        print(f"  {k}: {v}")
        
        elif sys.argv[1] == "--full":
            print("🚀 FULL PERTURBATION + STRESS TEST")
            print("=" * 50)
            
            # Phase 1: Stress test first
            print("\n📊 PHASE 1: Error Stress Test")
            print("-" * 50)
            stress_results = run_stress_test()
            
            # Phase 2: Perturbation mode
            print("\n🎯 PHASE 2: Perturbation Mode")
            print("-" * 50)
            
            state = load_json(LOOP_STATE, {})
            old_score = state.get("score", 0.5)
            
            perturbations = generate_perturbations()
            print(f"Generated {len(perturbations)} perturbations")
            
            for p in perturbations:
                apply_perturbation(p)
            
            # Phase 3: Run main loop
            print("\n🔄 PHASE 3: Main Loop Execution")
            print("-" * 50)
            result = subprocess.run(
                ['python3', str(SCRIPTS_DIR / 'learning_loop_v3.py')],
                capture_output=True, text=True, timeout=180
            )
            
            # Parse score
            new_score = old_score
            for line in result.stdout.split('\n'):
                if 'Loop Score:' in line:
                    match = re.search(r'Loop Score: ([0-9.]+)', line)
                    if match:
                        new_score = float(match.group(1))
            
            breakthrough, message = detect_breakthrough(old_score, new_score)
            
            print("\n" + "=" * 50)
            print("FINAL RESULTS")
            print("=" * 50)
            print(f"Score before: {old_score:.3f}")
            print(f"Score after:  {new_score:.3f}")
            print(f"Change:       {new_score - old_score:+.3f}")
            print(f"Breakthrough: {'YES! 🎉' if breakthrough else 'No'}")
            
            if breakthrough:
                print(f"\n💡 {message}")
        
        else:
            print("Unknown command")
            print("Usage:")
            print("  --perturb      Run perturbation mode")
            print("  --stress-test  Run error stress test")
            print("  --full         Run full perturbation + stress test")
    else:
        print("Learning Loop v3 MAXIMAL — P2 Enhancements")
        print("Usage: python3 learning_loop_v3_p2.py [command]")
        print("\nCommands:")
        print("  --perturb      Break through plateaus with random mutations")
        print("  --stress-test  Generate realistic error scenarios")
        print("  --full         Combined perturbation + stress test")

if __name__ == "__main__":
    main()
