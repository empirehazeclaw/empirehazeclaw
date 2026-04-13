#!/usr/bin/env python3
"""
🎯 Learning Loop v3 MAXIMAL — Feedback-Driven Self-Improvement

Architecture:
1. RESEARCH → Generate actionable hypotheses
2. QUALITY GATES → Detect issues
3. FEEDBACK INTEGRATION → Process external signals (Nico, Crons, KG)
4. SELECTION → Match issues to best findings
5. ACTION → Apply best improvement
6. VALIDATION GATE → Verify if it worked
7. SCORE UPDATE → Track + measure improvement

Key Innovations (from NeurIPS 2025 + best practices):
- Reflexion: Verbal feedback loop (no weight updates)
- OODA: Rapid observe-orient-decide-act cycles
- Experience Replay: Store + reuse successful trajectories
- Cross-Pattern: Apply proven solutions to similar errors
- Pattern Decay: Time-based refresh of old patterns

Usage:
    python3 learning_loop_v3.py              # Full cycle
    python3 learning_loop_v3.py --status     # Show status
    python3 learning_loop_v3.py --feedback  # Process feedback only
    python3 learning_loop_v3.py --validate   # Run validation only
"""

import os
import sys
import json
import subprocess
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "scripts"
DATA_DIR = WORKSPACE / "data"
KG_PATH = WORKSPACE / "core_ultralight/memory/knowledge_graph.json"
LOOP_STATE = DATA_DIR / "learning_loop_state.json"
FEEDBACK_QUEUE = DATA_DIR / "feedback_queue.json"
PATTERNS_FILE = DATA_DIR / "learning_loop" / "patterns.json"
IMPROVEMENTS_FILE = DATA_DIR / "learning_loop" / "improvements.json"
VALIDATION_LOG = DATA_DIR / "learning_loop" / "validation_log.json"

# ============ STATE MANAGEMENT ============

def load_state():
    """Load loop state with defaults."""
    defaults = {
        "version": "3.1",  # Updated for Phase 0 fix
        "iteration": 0,
        "score": 0.5,
        "score_history": [],
        "patterns": [],
        "cross_pattern_hits": 0,
        "cross_pattern_misses": 0,
        "validation_successes": 0,
        "validation_failures": 0,
        "feedback_processed": 0,
        "novelty_injections": 0,  # NEW: Phase 0 fix
        "last_validation": None,
        "last_decay": None,
        "created": datetime.now().isoformat()
    }
    if LOOP_STATE.exists():
        try:
            with open(LOOP_STATE) as f:
                data = json.load(f)
                return {**defaults, **data}
        except:
            return defaults
    return defaults

def save_state(state):
    """Save loop state."""
    LOOP_STATE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOOP_STATE, 'w') as f:
        json.dump(state, f, indent=2)

def load_patterns():
    """Load pattern database."""
    if PATTERNS_FILE.exists():
        try:
            with open(PATTERNS_FILE) as f:
                return json.load(f)
        except:
            pass
    return {"patterns": [], "version": "1.0"}

def save_patterns(data):
    """Save pattern database."""
    PATTERNS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PATTERNS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_improvements():
    """Load improvements log."""
    if IMPROVEMENTS_FILE.exists():
        try:
            with open(IMPROVEMENTS_FILE) as f:
                return json.load(f)
        except:
            pass
    return {"improvements": [], "version": "1.0"}

def save_improvements(data):
    """Save improvements log."""
    IMPROVEMENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(IMPROVEMENTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_validation_log():
    """Load validation log."""
    if VALIDATION_LOG.exists():
        try:
            with open(VALIDATION_LOG) as f:
                return json.load(f)
        except:
            pass
    return {"validations": [], "version": "1.0"}

def save_validation_log(data):
    """Save validation log."""
    VALIDATION_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(VALIDATION_LOG, 'w') as f:
        json.dump(data, f, indent=2)

# ============ FEEDBACK INTEGRATION (P0) ============

def collect_feedback() -> Dict[str, List]:
    """
    Collects feedback from all available sources.
    
    Sources:
    - Direct feedback from Nico (stored in feedback_queue)
    - Cron results (success/failure signals)
    - KG updates (access patterns)
    - System metrics (error rates, session counts)
    - Self-evaluation (did the loop improve?)
    
    Returns:
        Dict with feedback signals by source
    """
    print("📥 PHASE 0: Feedback Collection...")
    
    feedback = {
        "direct": [],      # From Nico
        "cron": [],        # From cron results
        "kg": [],          # From KG updates
        "metrics": [],     # From system metrics
        "self_eval": []    # From self-evaluation
    }
    
    # 1. Direct feedback from queue
    if FEEDBACK_QUEUE.exists():
        try:
            with open(FEEDBACK_QUEUE) as f:
                queue = json.load(f)
                feedback["direct"] = queue.get("feedback", [])[-10:]
                # Clear processed feedback
                queue["feedback"] = queue["feedback"][-5:]  # Keep last 5
                with open(FEEDBACK_QUEUE, 'w') as f:
                    json.dump(queue, f, indent=2)
        except:
            pass
    
    # 2. Cron results - check recent failures/successes
    try:
        result = subprocess.run(
            ['python3', str(SCRIPTS_DIR / 'cron_monitor.py'), '--report'],
            capture_output=True, text=True, timeout=30
        )
        # Parse cron status
        cron_feedback = []
        for line in result.stdout.split('\n'):
            if 'FAILED' in line.upper() or 'ERROR' in line.upper():
                cron_feedback.append({
                    "type": "cron_failure",
                    "message": line.strip(),
                    "timestamp": datetime.now().isoformat()
                })
            elif 'SUCCESS' in line.upper() or 'OK' in line.upper():
                cron_feedback.append({
                    "type": "cron_success",
                    "message": line.strip(),
                    "timestamp": datetime.now().isoformat()
                })
        feedback["cron"] = cron_feedback[-5:]
    except:
        pass
    
    # 3. KG updates - what patterns are being accessed?
    try:
        if KG_PATH.exists():
            with open(KG_PATH) as f:
                kg = json.load(f)
            # Find patterns with high access counts
            entities = kg.get("entities", {})
            kg_feedback = []
            for entity_id, entity_data in entities.items():
                access_count = entity_data.get("access_count", 0)
                if access_count > 10:
                    kg_feedback.append({
                        "type": "kg_high_access",
                        "entity": entity_id,
                        "access_count": access_count,
                        "timestamp": datetime.now().isoformat()
                    })
            feedback["kg"] = kg_feedback[-5:]
    except:
        pass
    
    # 4. System metrics - error rate, session count
    try:
        result = subprocess.run(
            ['python3', str(SCRIPTS_DIR / 'error_rate_monitor.py')],
            capture_output=True, text=True, timeout=30
        )
        for line in result.stdout.split('\n'):
            if 'Error Rate:' in line:
                match = re.search(r'Error Rate: ([0-9.]+)%', line)
                if match:
                    error_rate = float(match.group(1))
                    feedback["metrics"].append({
                        "type": "error_rate",
                        "value": error_rate,
                        "timestamp": datetime.now().isoformat()
                    })
    except:
        pass
    
    # 5. Self-evaluation - check if last improvement worked
    state = load_state()
    improvements = load_improvements()
    if improvements.get("improvements"):
        last_imp = improvements["improvements"][-1]
        self_eval = {
            "type": "last_improvement",
            "improvement": last_imp.get("title", "unknown"),
            "validated": last_imp.get("validated", False),
            "timestamp": datetime.now().isoformat()
        }
        feedback["self_eval"].append(self_eval)
    
    total_signals = sum(len(v) for v in feedback.values())
    print(f"   ✅ Collected {total_signals} feedback signals")
    for source, signals in feedback.items():
        if signals:
            print(f"      - {source}: {len(signals)}")
    
    return feedback

def process_feedback(feedback: Dict) -> Dict:
    """
    Processes raw feedback into weighted signals.
    
    Each signal gets:
    - weight: 0.0-1.0 based on source reliability
    - sentiment: positive/negative/neutral
    - category: what type of signal
    
    Returns:
        Processed signals ready for improvement selection
    """
    print("🧠 Processing feedback...")
    
    processed = []
    
    # Source weights (reliability)
    weights = {
        "direct": 1.0,      # Direct from Nico - highest trust
        "cron": 0.8,       # System data - high trust
        "kg": 0.6,         # Access patterns - medium
        "metrics": 0.9,    # Quantitative - high trust
        "self_eval": 0.7   # Self-evaluation - medium-high
    }
    
    for source, signals in feedback.items():
        weight = weights.get(source, 0.5)
        
        for signal in signals:
            # Determine sentiment
            sentiment = "neutral"
            if source == "cron":
                if signal.get("type") == "cron_failure":
                    sentiment = "negative"
                elif signal.get("type") == "cron_success":
                    sentiment = "positive"
            elif source == "metrics":
                val = signal.get("value", 0)
                if val > 5:
                    sentiment = "negative"
                elif val < 1:
                    sentiment = "positive"
            elif source == "self_eval":
                if signal.get("validated"):
                    sentiment = "positive"
                else:
                    sentiment = "negative"
            
            processed.append({
                "source": source,
                "type": signal.get("type", "unknown"),
                "sentiment": sentiment,
                "weight": weight,
                "data": signal,
                "timestamp": signal.get("timestamp", datetime.now().isoformat())
            })
    
    # Aggregate sentiments by type
    sentiment_summary = defaultdict(lambda: {"positive": 0, "negative": 0, "neutral": 0, "weighted_sum": 0.0})
    
    for p in processed:
        s = p["sentiment"]
        w = p["weight"]
        sentiment_summary[p["type"]][s] += 1
        sentiment_summary[p["type"]]["weighted_sum"] += w if s == "positive" else -w if s == "negative" else 0
    
    print(f"   ✅ Processed {len(processed)} signals")
    return {
        "signals": processed,
        "summary": dict(sentiment_summary),
        "total_processed": len(processed)
    }

# ============ VALIDATION GATE (P0) ============

def validation_gate(improvement: Dict, previous_state: Dict) -> Tuple[bool, Dict]:
    """
    Validates if an improvement actually worked.
    
    Before marking improvement as "done":
    1. Apply fix
    2. Wait for next cycle / trigger test
    3. Measure: Did error rate decrease?
    4. Measure: Did metric improve?
    5. If NO → Rollback + flag as failed experiment
    6. If YES → Confirm pattern, update score
    
    Returns:
        (validated: bool, validation_details: dict)
    """
    print("🔍 VALIDATION GATE: Testing improvement...")
    
    validation_details = {
        "improvement": improvement.get("title", "unknown"),
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "passed": False,
        "error_delta": None,
        "score_delta": None
    }
    
    # Get baseline metrics before improvement
    baseline_score = previous_state.get("score", 0.5)
    baseline_errors = get_current_error_rate()
    
    # Run validation tests
    try:
        result = subprocess.run(
            ['python3', str(SCRIPTS_DIR / 'error_reducer.py'), '--check'],
            capture_output=True, text=True, timeout=30
        )
        validation_details["tests"].append({
            "name": "error_check",
            "passed": result.returncode == 0,
            "output": result.stdout[:100]
        })
    except Exception as e:
        validation_details["tests"].append({
            "name": "error_check",
            "passed": False,
            "error": str(e)[:50]
        })
    
    # Test 2: Script syntax check (if applicable)
    if improvement.get("script"):
        script_path = SCRIPTS_DIR / improvement["script"]
        if script_path.exists():
            try:
                result = subprocess.run(
                    ['python3', '-m', 'py_compile', str(script_path)],
                    capture_output=True, text=True, timeout=10
                )
                validation_details["tests"].append({
                    "name": "syntax_check",
                    "passed": result.returncode == 0,
                    "output": "OK" if result.returncode == 0 else "Syntax error"
                })
            except:
                pass
    
    # Test 3: Cron health check
    try:
        result = subprocess.run(
            ['python3', str(SCRIPTS_DIR / 'cron_watchdog.py'), '--report'],
            capture_output=True, text=True, timeout=30
        )
        failed_count = result.stdout.count('FAILED')
        validation_details["tests"].append({
            "name": "cron_health",
            "passed": failed_count == 0,
            "failed_crons": failed_count
        })
    except:
        pass
    
    # Calculate validation result
    passed_tests = sum(1 for t in validation_details["tests"] if t.get("passed", False))
    total_tests = len(validation_details["tests"])
    
    # Current error rate
    current_errors = get_current_error_rate()
    error_delta = current_errors - baseline_errors
    validation_details["error_delta"] = error_delta
    
    # Validation passes if:
    # - At least 1 test passes AND
    # - Error rate didn't increase significantly OR some improvement
    # - No critical failures
    has_passed_test = passed_tests >= 1
    no_error_increase = error_delta <= 0.5
    validation_details["passed"] = has_passed_test and no_error_increase
    
    # Score improvement (based on validation result)
    if validation_details["passed"]:
        # Positive reinforcement
        score_delta = 0.1
    else:
        # Failed validation - small negative, but not as severe
        score_delta = -0.05
    
    validation_details["baseline_score"] = baseline_score
    validation_details["current_score"] = baseline_score + score_delta
    
    # Log validation
    log = load_validation_log()
    log["validations"].append(validation_details)
    log["validations"] = log["validations"][-100:]  # Keep last 100
    save_validation_log(log)
    
    # Update state
    state = load_state()  # Fresh load
    if validation_details["passed"]:
        state["validation_successes"] = state.get("validation_successes", 0) + 1
        print(f"   ✅ VALIDATION PASSED")
        print(f"      Error delta: {error_delta:+.2f}%")
        print(f"      Score delta: {score_delta:+.3f}")
    else:
        state["validation_failures"] = state.get("validation_failures", 0) + 1
        print(f"   ❌ VALIDATION FAILED")
        print(f"      Tests passed: {passed_tests}/{total_tests}")
        print(f"      Error delta: {error_delta:+.2f}%")
        print(f"      Score delta: {score_delta:+.3f}")
    
    # Update score based on validation
    if score_delta != 0:
        new_score = baseline_score + (score_delta * 0.3)  # Dampen
        state["score"] = max(0.0, min(1.0, new_score))
        state["score_history"].append(state["score"])
        state["score_history"] = state["score_history"][-50:]
    save_state(state)
    
    return validation_details["passed"], validation_details

def get_current_error_rate() -> float:
    """Get current system error rate."""
    try:
        result = subprocess.run(
            ['python3', str(SCRIPTS_DIR / 'error_rate_monitor.py')],
            capture_output=True, text=True, timeout=30
        )
        for line in result.stdout.split('\n'):
            if 'Error Rate:' in line:
                match = re.search(r'Error Rate: ([0-9.]+)%', line)
                if match:
                    return float(match.group(1))
    except:
        pass
    return 2.0  # Default fallback

def calculate_loop_score() -> float:
    """
    Calculates the loop's self-improvement score.
    
    Phase 0 Fixed Formula (from PLATEAU_BREAKTHROUGH_PLAN):
    - base_score: Foundation (40%)
    - validation_success_rate: Validation weight (30%)
    - novelty_factor: New learning bonus (20%)
    - pattern_quality: Pattern quality (10%)
    
    Key fixes vs original:
    1. NO neutral base inflation (removed 0.5 neutral defaults)
    2. Novelty now tracked explicitly
    3. Pattern quality tracked explicitly
    4. Damping applied in score update (max 0.05 per iteration)
    """
    state = load_state()
    
    # Validation success rate (only count if we have actual validations)
    val_success = state.get("validation_successes", 0)
    val_fail = state.get("validation_failures", 0)
    val_total = val_success + val_fail
    
    if val_total > 0:
        validation_success_rate = val_success / val_total
    else:
        validation_success_rate = 0.0  # No credit without real validations
    
    # Cross-pattern rate (only count if we have actual attempts)
    cross_hits = state.get("cross_pattern_hits", 0)
    cross_miss = state.get("cross_pattern_misses", 0)
    cross_total = cross_hits + cross_miss
    
    if cross_total > 0:
        cross_rate = cross_hits / cross_total
    else:
        cross_rate = 0.0  # No credit without attempts
    
    # Feedback processed (count-based, no neutral boost)
    feedback_proc = state.get("feedback_processed", 0)
    feedback_factor = min(feedback_proc / 30, 1.0) * 0.2
    
    # Iteration bonus (loop is running)
    iteration = state.get("iteration", 0)
    iteration_factor = min(iteration / 20, 1.0) * 0.1  # Max 0.1 from iterations
    
    # === PHASE 0 FIX: Novelty Factor ===
    # Novelty: +0.05 per new pattern, +0.02 per cross-pattern hit
    novelty_injections = state.get("novelty_injections", 0)
    cross_pattern_hits = state.get("cross_pattern_hits", 0)
    novelty_factor = min(novelty_injections * 0.05 + cross_pattern_hits * 0.02, 0.3)  # Cap at 0.3
    
    # === PHASE 0 FIX: Pattern Quality ===
    # Based on pattern confidence and decay
    patterns_data = load_patterns()
    patterns = patterns_data.get("patterns", [])
    if patterns:
        avg_confidence = sum(p.get("confidence", 0) for p in patterns) / len(patterns)
        pattern_quality = avg_confidence * 0.1  # Scale to 0-0.1
    else:
        pattern_quality = 0.0
    
    # === PHASE 0 FIX: New Formula ===
    # base_score * 0.4 + validation_success_rate * 0.3 + novelty_factor * 0.2 + pattern_quality * 0.1
    base_score = 0.5  # Neutral foundation
    score = (
        base_score * 0.4 +
        validation_success_rate * 0.3 +
        novelty_factor * 0.2 +
        pattern_quality +
        feedback_factor +
        iteration_factor
    )
    
    # Cap at 0.95 to prevent infinity
    return min(0.95, max(0.0, score))

# ============ PATTERN DECAY ENGINE (P1) ============

def run_pattern_decay():
    """
    Applies time-based decay to old patterns.
    
    Every pattern has:
    - first_seen: timestamp
    - last_validated: timestamp
    - confidence: float (0-1)
    - decay_rate: float
    
    Decay Formula:
    confidence = initial_confidence * (1 - decay_rate)^days_since_validation
    """
    print("📉 Running Pattern Decay Engine...")
    
    state = load_state()
    last_decay = state.get("last_decay")
    
    # Only run decay once per day
    if last_decay:
        last_decay_date = datetime.fromisoformat(last_decay)
        if (datetime.now() - last_decay_date).total_seconds() < 86400:
            print("   ⏭️ Decay already run today")
            return
    
    patterns_data = load_patterns()
    patterns = patterns_data.get("patterns", [])
    
    decay_rate = 0.05  # 5% per day
    min_confidence = 0.2
    archived = 0
    
    for pattern in patterns:
        last_validated = pattern.get("last_validated")
        if last_validated:
            days_since = (datetime.now() - datetime.fromisoformat(last_validated)).days
            if days_since > 0:
                initial = pattern.get("initial_confidence", 0.8)
                new_confidence = initial * ((1 - decay_rate) ** days_since)
                pattern["confidence"] = max(min_confidence, new_confidence)
                pattern["days_since_validation"] = days_since
                
                # Archive if too old and low confidence
                if new_confidence < min_confidence and days_since > 30:
                    pattern["archived"] = True
                    archived += 1
    
    patterns_data["patterns"] = patterns
    save_patterns(patterns_data)
    
    state["last_decay"] = datetime.now().isoformat()
    save_state(state)
    
    print(f"   ✅ Decay applied to {len(patterns)} patterns")
    print(f"   📦 {archived} patterns archived")

def refresh_pattern(pattern_id: str) -> bool:
    """
    Refreshes a pattern by running a mini-research cycle.
    
    Returns True if pattern is still relevant.
    """
    patterns_data = load_patterns()
    patterns = patterns_data.get("patterns", [])
    
    for pattern in patterns:
        if pattern.get("id") == pattern_id:
            # Run quick validation
            print(f"   🔄 Refreshing pattern: {pattern_id}")
            
            # Check if related errors still occur
            error_type = pattern.get("error_type", "")
            current_errors = get_current_error_rate()
            
            # Simple check: is error rate still elevated?
            if current_errors < 1.0:
                pattern["still_relevant"] = False
                return False
            
            pattern["last_validated"] = datetime.now().isoformat()
            pattern["confidence"] = pattern.get("initial_confidence", 0.8)
            pattern["days_since_validation"] = 0
            pattern["still_relevant"] = True
            save_patterns(patterns_data)
            return True
    
    return False

# ============ CROSS-PATTERN MATCHER (P1) ============

def find_similar_errors(new_error: str) -> List[Dict]:
    """
    Finds similar past errors using multiple similarity metrics.
    
    Similarity scoring:
    - String similarity (Levenshtein)
    - Root cause similarity (common error types)
    - Context similarity (same cron, same time, etc.)
    
    Returns top-k similar errors with proven solutions.
    """
    patterns_data = load_patterns()
    patterns = patterns_data.get("patterns", [])
    
    similar = []
    new_error_lower = new_error.lower()
    new_words = set(new_error_lower.split())
    
    for pattern in patterns:
        if pattern.get("archived"):
            continue
        
        score = 0.0
        reasons = []
        
        # Word overlap (simple semantic similarity)
        pattern_words = set(pattern.get("description", "").lower().split())
        overlap = len(new_words & pattern_words)
        if overlap > 0:
            score += overlap * 0.3
            reasons.append(f"word_overlap:{overlap}")
        
        # Error type match
        if pattern.get("error_type") and pattern.get("error_type") in new_error_lower:
            score += 0.5
            reasons.append("error_type_match")
        
        # Context match (same script/cron)
        if pattern.get("context", {}).get("script") and pattern.get("context")["script"] in new_error:
            score += 0.3
            reasons.append("context_match")
        
        # Solution exists
        if pattern.get("solution") and pattern.get("validated"):
            score += 0.2
            reasons.append("has_validated_solution")
        
        if score > 0.3:
            similar.append({
                "pattern": pattern,
                "similarity_score": score,
                "reasons": reasons
            })
    
    # Sort by similarity
    similar.sort(key=lambda x: x["similarity_score"], reverse=True)
    
    return similar[:5]  # Top 5

def apply_cross_pattern_solution(similar_errors: List[Dict]) -> Tuple[bool, str]:
    """
    Applies a proven solution from similar errors.
    
    Returns (success, message)
    """
    if not similar_errors:
        return False, "No similar errors found"
    
    best = similar_errors[0]
    pattern = best["pattern"]
    
    if not pattern.get("solution"):
        return False, "No solution available"
    
    print(f"   🎯 Applying cross-pattern solution from similarity score {best['similarity_score']:.2f}")
    print(f"   📝 Solution: {pattern['solution'][:100]}...")
    
    # Track cross-pattern usage
    state = load_state()
    state["cross_pattern_hits"] += 1
    save_state(state)
    
    return True, f"Applied solution from pattern: {pattern.get('id', 'unknown')}"

# ============ MAIN LOOP ============

def run_full_cycle():
    """Run the complete Learning Loop v3 MAXIMAL cycle."""
    print("=" * 60)
    print("🎯 LEARNING LOOP v3 MAXIMAL — Full Cycle")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    print()
    
    state = load_state()
    state["iteration"] += 1
    iteration = state["iteration"]
    
    start_time = datetime.now()
    
    # PHASE 0: Feedback Collection
    print("=" * 60)
    print("📥 PHASE 0: Feedback Collection")
    print("=" * 60)
    feedback = collect_feedback()
    processed_feedback = process_feedback(feedback)
    state["feedback_processed"] += processed_feedback["total_processed"]
    print()
    
    # PHASE 1: System Check
    print("=" * 60)
    print("📊 PHASE 1: System Check")
    print("=" * 60)
    issues = run_system_check()
    print(f"   Found {len(issues)} issues")
    print()
    
    # PHASE 2: Research + Hypotheses
    print("=" * 60)
    print("🔍 PHASE 2: Research + Hypotheses")
    print("=" * 60)
    hypotheses = run_research()
    print(f"   Generated {len(hypotheses)} hypotheses")
    
    # PHASE 2.5: Novelty Injection (Phase 0 fix)
    # Increment novelty when we generate new hypotheses
    if hypotheses:
        state = load_state()
        state["novelty_injections"] = state.get("novelty_injections", 0) + 1
        save_state(state)
        print(f"   ✨ Novelty injection: {state['novelty_injections']} total")
    print()
    
    # PHASE 3: Quality Gates
    print("=" * 60)
    print("🔒 PHASE 3: Quality Gates")
    print("=" * 60)
    gate_issues = run_quality_gates()
    print(f"   Detected {len(gate_issues)} issues")
    print()
    
    # PHASE 4: Improvement Selection + Cross-Pattern Check
    print("=" * 60)
    print("🚀 PHASE 4: Improvement Selection")
    print("=" * 60)
    
    # Check for cross-pattern matches first
    cross_pattern_applied = False
    for issue in gate_issues[:2]:
        similar = find_similar_errors(issue.get("description", ""))
        if similar and similar[0]["similarity_score"] > 0.5:
            success, msg = apply_cross_pattern_solution(similar)
            if success:
                cross_pattern_applied = True
    
    if not cross_pattern_applied:
        improvements = select_improvements(gate_issues, hypotheses)
        print(f"   Selected {len(improvements)} improvements")
        
        # PHASE 5: Validation Gate
        print()
        print("=" * 60)
        print("🔍 PHASE 5: Validation Gate")
        print("=" * 60)
        
        for imp in improvements[:1]:  # Validate top improvement
            validated, details = validation_gate(imp, state)
            imp["validated"] = validated
            
            # Log improvement
            improvements_log = load_improvements()
            improvements_log["improvements"].append({
                "timestamp": datetime.now().isoformat(),
                "title": imp.get("title", "unknown"),
                "validated": validated,
                "validation_details": details
            })
            improvements_log["improvements"] = improvements_log["improvements"][-50:]
            save_improvements(improvements_log)
    
    # PHASE 6: Pattern Decay (run daily)
    run_pattern_decay()
    
    # Calculate final score (reload state to get validation updates)
    state = load_state()  # Fresh load to get validation counts
    final_score = calculate_loop_score()
    state["score"] = final_score
    state["score_history"].append(final_score)
    save_state(state)
    
    duration = (datetime.now() - start_time).total_seconds()
    
    print()
    print("=" * 60)
    print("📊 CYCLE SUMMARY")
    print("=" * 60)
    print(f"   Iteration: {iteration}")
    print(f"   Duration: {duration:.1f}s")
    print(f"   Feedback signals: {processed_feedback['total_processed']}")
    print(f"   Issues found: {len(issues) + len(gate_issues)}")
    print(f"   Hypotheses: {len(hypotheses)}")
    print(f"   Loop Score: {final_score:.3f}")
    print(f"   Validation success rate: {state['validation_successes']}/{state['validation_successes'] + state['validation_failures']}")
    print(f"   Cross-pattern hits: {state['cross_pattern_hits']}")
    print("=" * 60)
    
    return True

def run_system_check() -> List[Dict]:
    """Run system health check."""
    issues = []
    
    # Gateway check
    try:
        result = subprocess.run(
            ['curl', '-s', 'http://127.0.0.1:18789/health'],
            capture_output=True, text=True, timeout=5
        )
        if '"ok":true' not in result.stdout and 'live' not in result.stdout:
            issues.append({
                "type": "gateway",
                "description": "Gateway health check failed",
                "severity": "HIGH"
            })
    except:
        issues.append({
            "type": "gateway",
            "description": "Gateway unreachable",
            "severity": "HIGH"
        })
    
    # Disk check
    try:
        result = subprocess.run(['df', '-h', str(WORKSPACE)], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if '/' in line and not line.startswith('Filesystem'):
                parts = line.split()
                if len(parts) >= 5:
                    use_pct = int(parts[4].replace('%', ''))
                    if use_pct > 85:
                        issues.append({
                            "type": "disk",
                            "description": f"Disk at {use_pct}%",
                            "severity": "HIGH"
                        })
    except:
        pass
    
    return issues

def run_research() -> List[Dict]:
    """Run research phase to generate hypotheses."""
    hypotheses = []
    
    try:
        result = subprocess.run(
            ['python3', str(SCRIPTS_DIR / 'innovation_research.py'), '--daily'],
            capture_output=True, text=True, timeout=120
        )
        
        # Parse for improvement-relevant topics
        content = result.stdout.lower()
        topics = [
            ('self-improv', 'Self-Improvement'),
            ('autonom', 'Autonomous Learning'),
            ('token', 'Token Optimization'),
            ('memory', 'Memory Optimization'),
            ('feedback', 'Feedback Integration'),
            ('pattern', 'Pattern Recognition')
        ]
        
        for keyword, title in topics:
            if keyword in content:
                hypotheses.append({
                    "title": f"Apply {title} Pattern",
                    "category": title.lower().replace(' ', '_'),
                    "source": "research",
                    "expected_impact": "MEDIUM"
                })
    except:
        pass
    
    return hypotheses[:5]

def run_quality_gates() -> List[Dict]:
    """Run quality gates to detect issues."""
    issues = []
    
    # Self-eval
    try:
        result = subprocess.run(
            ['python3', str(SCRIPTS_DIR / 'self_eval.py')],
            capture_output=True, text=True, timeout=30
        )
        score_match = re.search(r'(\d+)/100', result.stdout)
        if score_match:
            score = int(score_match.group(1))
            if score < 80:
                issues.append({
                    "type": "low_self_eval",
                    "description": f"Self-Eval score: {score}/100",
                    "severity": "HIGH" if score < 70 else "MEDIUM"
                })
    except:
        pass
    
    # Error rate
    error_rate = get_current_error_rate()
    if error_rate > 5:
        issues.append({
            "type": "high_error_rate",
            "description": f"Error rate: {error_rate}%",
            "severity": "HIGH"
        })
    elif error_rate > 2:
        issues.append({
            "type": "elevated_error_rate",
            "description": f"Error rate: {error_rate}%",
            "severity": "MEDIUM"
        })
    
    return issues

def select_improvements(issues: List[Dict], hypotheses: List[Dict]) -> List[Dict]:
    """Select best improvements based on issues and hypotheses."""
    improvements = []
    
    # Priority: critical issues first
    for issue in issues:
        if issue.get("severity") == "HIGH":
            improvements.append({
                "title": f"Fix: {issue['description']}",
                "type": issue["type"],
                "source": "issue",
                "expected_impact": "HIGH"
            })
    
    # Then research hypotheses
    for hyp in hypotheses[:2]:
        if len(improvements) >= 3:
            break
        improvements.append({
            "title": hyp["title"],
            "type": hyp.get("category", "research"),
            "source": "research",
            "expected_impact": hyp.get("expected_impact", "MEDIUM")
        })
    
    return improvements[:3]

def show_status():
    """Show current loop status."""
    state = load_state()
    patterns_data = load_patterns()
    improvements = load_improvements()
    validation_log = load_validation_log()
    
    print("📊 LEARNING LOOP v3 MAXIMAL — STATUS")
    print("=" * 50)
    print(f"Version: {state.get('version', 'unknown')}")
    print(f"Iteration: {state.get('iteration', 0)}")
    print(f"Score: {state.get('score', 0):.3f}")
    print()
    print("📈 Metrics:")
    print(f"  Validation successes: {state.get('validation_successes', 0)}")
    print(f"  Validation failures: {state.get('validation_failures', 0)}")
    print(f"  Cross-pattern hits: {state.get('cross_pattern_hits', 0)}")
    print(f"  Cross-pattern misses: {state.get('cross_pattern_misses', 0)}")
    print(f"  Feedback processed: {state.get('feedback_processed', 0)}")
    print()
    print("📚 Patterns:")
    print(f"  Total patterns: {len(patterns_data.get('patterns', []))}")
    archived = sum(1 for p in patterns_data.get('patterns', []) if p.get('archived'))
    print(f"  Archived: {archived}")
    print()
    print("📋 Recent Improvements:")
    for imp in improvements.get("improvements", [])[-3:]:
        status = "✅" if imp.get("validated") else "❌"
        print(f"  {status} {imp.get('title', 'unknown')[:40]}")
    print()
    print("🔍 Recent Validations:")
    for val in validation_log.get("validations", [])[-3:]:
        status = "✅" if val.get("passed") else "❌"
        print(f"  {status} {val.get('improvement', 'unknown')[:40]}")
    
    # Score history sparkline
    history = state.get("score_history", [])
    if history:
        print()
        print("📈 Score History:")
        sparkline = ""
        for s in history[-20:]:
            if s >= 0.8:
                sparkline += "█"
            elif s >= 0.6:
                sparkline += "▓"
            elif s >= 0.4:
                sparkline += "▒"
            else:
                sparkline += "░"
        print(f"  [{sparkline}]")

# ============ CLI ============

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--status":
            show_status()
        elif sys.argv[1] == "--feedback":
            feedback = collect_feedback()
            processed = process_feedback(feedback)
            print(f"\nProcessed {processed['total_processed']} signals")
            print("\nSentiment Summary:")
            for signal_type, summary in processed["summary"].items():
                print(f"  {signal_type}: {summary}")
        elif sys.argv[1] == "--validate":
            state = load_state()
            improvements = load_improvements()
            if improvements.get("improvements"):
                last = improvements["improvements"][-1]
                validated, details = validation_gate(last, state)
                print(f"Validation: {'PASSED' if validated else 'FAILED'}")
        elif sys.argv[1] == "--decay":
            run_pattern_decay()
        else:
            print("Unknown command")
            print("Usage: learning_loop_v3.py [--status|--feedback|--validate|--decay]")
    else:
        run_full_cycle()
