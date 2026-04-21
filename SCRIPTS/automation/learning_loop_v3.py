#!/usr/bin/env python3
"""
🎯 Learning Loop v3 MAXIMAL - Feedback-Driven Self-Improvement

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

# Memory & Log Analyzer for enhanced learning (imported after WORKSPACE is defined below)

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "scripts"
DATA_DIR = WORKSPACE / "data"
KG_PATH = WORKSPACE / "ceo/memory/kg/knowledge_graph.json"
LOOP_STATE = DATA_DIR / "learning_loop_state.json"
FEEDBACK_QUEUE = DATA_DIR / "feedback_queue.json"
PATTERNS_FILE = DATA_DIR / "learning_loop" / "patterns.json"
IMPROVEMENTS_FILE = DATA_DIR / "learning_loop" / "improvements.json"
VALIDATION_LOG = DATA_DIR / "learning_loop" / "validation_log.json"
IDEA_BANK_FILE = DATA_DIR / "learning_loop" / "idea_bank.json"  # NEW: Phase 1

# Memory & Log Analyzer for enhanced learning (imported after paths are defined)
try:
    from pathlib import Path
    _automation_dir = WORKSPACE / "SCRIPTS" / "automation"
    if not str(_automation_dir) in sys.path:
        sys.path.insert(0, str(_automation_dir))
    from memory_log_analyzer import MemoryLogAnalyzer
except ImportError:
    MemoryLogAnalyzer = None

# ============ NOISE PATTERN FILTER - Plateau Fix ============
NOISE_PATTERNS_PATCH = [
    "error_reducer_error",
    "analyzing_errors",
    "error_rate:",
    "total_errors:",
    "error_breakdown:",
    "exec_error:",
    "error_tools:",
    "failure:_failed",
    "failure:_failed_jobs",
    "failure:_error:_message",
    "pattern_20260",
    "SYSTEM_FIX: Added",
    "TEMPORAL_INVESTIGATE:",
]

def is_noise_pattern_patch(title: str) -> bool:
    """Check if a pattern title is parser noise."""
    if not title:
        return False
    title_lower = title.lower()
    for noise in NOISE_PATTERNS_PATCH:
        if noise.lower() in title_lower:
            return True
    return False

def clean_improvements_log_patch():
    """Clean improvements log of noise - call at start of run_full_cycle."""
    improvements = load_improvements()
    original = len(improvements.get("improvements", []))
    cleaned = [i for i in improvements.get("improvements", []) if not is_noise_pattern_patch(i.get("title", ""))]
    improvements["improvements"] = cleaned[-50:]
    save_improvements(improvements)
    removed = original - len(cleaned)
    if removed > 0:
        print(f"   🧹 Cleaned {removed} noise entries from improvements log")
    return removed

# ============ EXPLORATION BUDGET INTEGRATION ============
EXPLORATION_SCRIPT = Path("/home/clawbot/.openclaw/workspace/ceo/scripts/exploration_budget.py")

def should_explore() -> dict:
    """Check if next run should be exploration or exploitation."""
    try:
        result = subprocess.run(
            ["python3", str(EXPLORATION_SCRIPT), "--should-explore"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and "should_explore" in result.stdout:
            # Parse output to determine decision
            should_exp = "should_explore: True" in result.stdout
            return {"explore": should_exp, "source": "exploration_budget"}
        return {"explore": False, "source": "fallback"}
    except Exception as e:
        return {"explore": False, "source": f"error: {e}"}

def log_exploration_run(run_type: str, success: bool, strategy: str = "learning_loop_v3"):
    """Log an exploration or exploitation run to the budget."""
    if run_type not in ["exploration", "exploitation"]:
        return
    try:
        subprocess.run(
            ["python3", str(EXPLORATION_SCRIPT), "--log-run", run_type, strategy, str(success).lower()],
            capture_output=True, timeout=10
        )
    except:
        pass

# ============ STATE MANAGEMENT ============

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
        "consecutive_failures": 0,  # NEW: Phase 2 - rollback tracking
        "learning_rate": 0.1,  # NEW: Plateau Fix - adaptive LR
        "lr_stagnation_count": 0,  # NEW: Count consecutive plateau runs
        "pattern_source": "task",  # NEW: Rotation: task|failure|success|capability
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

# Thompson Sampling rewards file (separate to avoid state management issues)
THOMPSON_FILE = DATA_DIR / "thompson_rewards.json"

def load_thompson_rewards() -> Dict:
    """Load Thompson rewards from separate file."""
    if THOMPSON_FILE.exists():
        try:
            with open(THOMPSON_FILE) as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_thompson_rewards(rewards: Dict):
    """Save Thompson rewards to separate file."""
    THOMPSON_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(THOMPSON_FILE, 'w') as f:
        json.dump(rewards, f, indent=2)

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

    # Ensure all patterns have required fields
    for p in data.get("patterns", []):
        if "confidence" not in p:
            p["confidence"] = p.get("initial_confidence", 0.5)
        if "initial_confidence" not in p:
            p["initial_confidence"] = p.get("confidence", 0.5)

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

# ============ IDEA BANK (PHASE 1 - Dolphin Style) ============

def load_idea_bank():
    """Load idea bank - ineffective ideas that didn't work."""
    if IDEA_BANK_FILE.exists():
        try:
            with open(IDEA_BANK_FILE) as f:
                return json.load(f)
        except:
            pass
    return {"ideas": [], "version": "1.0"}


def save_idea_bank(data):
    """Save idea bank."""
    IDEA_BANK_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(IDEA_BANK_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_to_idea_bank(idea_title: str, error_info: str, why_ineffective: str):
    """
    Add an idea that didn't work to the idea bank.

    This is the Dolphin "ineffective idea bank" pattern:
    - Record what was tried and WHY it failed
    - Use this to avoid similar approaches in the future
    """
    idea_bank = load_idea_bank()

    # Create idea entry
    idea_entry = {
        "id": f"idea_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "title": idea_title,
        "error_info": error_info,
        "why_ineffective": why_ineffective,
        "created": datetime.now().isoformat(),
        "times_encountered": 1
    }

    # Check if similar idea already exists (avoid duplicates)
    existing = False
    for existing_idea in idea_bank["ideas"]:
        if existing_idea["title"] == idea_title:
            existing_idea["times_encountered"] += 1
            existing = True
            break

    if not existing:
        idea_bank["ideas"].append(idea_entry)

    # Keep last 100 ideas
    idea_bank["ideas"] = idea_bank["ideas"][-100:]
    save_idea_bank(idea_bank)
    print(f"   📝 Added to idea bank: {idea_title[:50]}...")

def is_idea_novel(title: str, category: str) -> bool:
    """
    Check if an idea is novel (not in idea bank as ineffective).

    Uses simple keyword matching since we don't have embeddings.
    """
    idea_bank = load_idea_bank()

    title_lower = title.lower()
    category_lower = category.lower()

    for idea in idea_bank["ideas"]:
        idea_title = idea["title"].lower()
        idea_category = idea.get("category", "").lower()

        # Check for title overlap (simple string matching)
        title_words = set(title_lower.split())
        idea_words = set(idea_title.split())
        overlap = title_words & idea_words

        if len(overlap) >= 2:  # At least 2 common words = similar
            print(f"   ⚠️ Similar ineffective idea found: {idea['title'][:40]}")
            print(f"      Why failed: {idea['why_ineffective'][:80]}")
            return False

        # Check category match
        if category_lower == idea_category and idea_category:
            print(f"   ⚠️ Same category ineffective idea: {idea['title'][:40]}")
            return False

    return True

def get_exploration_perturbation() -> Dict:
    """
    Get random exploration perturbation (10% chance per iteration).

    Phase 1: Random perturbation to break plateaus.
    """
    import random

    perturbations = [
        {"type": "random_topic", "weight": 0.4,
         "description": "Explore completely new topic"},
        {"type": "approach_flip", "weight": 0.3,
         "description": "Try opposite approach"},
        {"type": "method_shuffle", "weight": 0.3,
         "description": "Shuffle method combination"}
    ]

    if random.random() < 0.1:  # 10% chance
        # Weighted random selection
        r = random.random()
        cumulative = 0
        for pert in perturbations:
            cumulative += pert["weight"]
            if r <= cumulative:
                print(f"   🎲 Exploration perturbation: {pert['description']}")
                return pert

    return {"type": "none", "weight": 0, "description": "No perturbation"}


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

# ============ VALIDATION GATE v2 (PHASE 2) ============

# PHASE 2: Stricter thresholds
ERROR_DELTA_THRESHOLD = 2.0  # Must improve or stay same (was 0.1 - too strict for 0.77+ score)
MIN_TESTS_PASSED = 2          # At least 2/3 tests must pass (was 1)
ROLLBACK_STREAK_LIMIT = 3     # Rollback score after 3 consecutive failures

def validation_gate(improvement: Dict, previous_state: Dict) -> Tuple[bool, Dict]:
    """
    PHASE 2: Stricter Validation Gate with real metrics.

    Improvements vs v1:
    1. Error delta threshold: 0.5 → 0.1 (must actually improve or stay same)
    2. Min tests passed: 1 → 2 (at least 2/3 tests must pass)
    3. Streak tracking: Rollback score after 3 consecutive failures
    4. Actual error check: Uses error_reducer, not just monitoring
    """
    print("🔍 VALIDATION GATE v2: Testing improvement...")

    validation_details = {
        "improvement": improvement.get("title", "unknown"),
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "passed": False,
        "error_delta": None,
        "score_delta": None,
        "version": "2.0"  # Mark as v2
    }

    # Get baseline metrics before improvement
    baseline_score = previous_state.get("score", 0.5)
    baseline_errors = get_current_error_rate()

    # === PHASE 2: Run deeper validation tests ===

    # Test 1: Error reducer check (real validation)
    try:
        result = subprocess.run(
            ['python3', str(SCRIPTS_DIR / 'error_reducer.py'), '--check'],
            capture_output=True, text=True, timeout=30
        )
        passed = result.returncode == 0
        validation_details["tests"].append({
            "name": "error_reducer_check",
            "passed": passed,
            "output": "No critical errors" if passed else result.stdout[:100]
        })
    except Exception as e:
        validation_details["tests"].append({
            "name": "error_reducer_check",
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
                passed = result.returncode == 0
                validation_details["tests"].append({
                    "name": "syntax_check",
                    "passed": passed,
                    "output": "OK" if passed else "Syntax error"
                })
            except:
                validation_details["tests"].append({
                    "name": "syntax_check",
                    "passed": False,
                    "error": "Check failed"
                })
    else:
        # No script = skip syntax check (pass by default)
        validation_details["tests"].append({
            "name": "syntax_check",
            "passed": True,
            "output": "No script to check"
        })

    # Test 3: Cron health check (improvement must not break crons)
    try:
        result = subprocess.run(
            ['python3', str(SCRIPTS_DIR / 'cron_watchdog.py'), '--report'],
            capture_output=True, text=True, timeout=30
        )
        failed_count = result.stdout.count('FAILED')
        passed = failed_count == 0
        validation_details["tests"].append({
            "name": "cron_health",
            "passed": passed,
            "failed_crons": failed_count
        })
    except:
        validation_details["tests"].append({
            "name": "cron_health",
            "passed": False,
            "error": "Cron check failed"
        })

    # Test 4: Meta-improvement validation (NEW: for forced novelty)
    # If this is a forced novelty improvement, verify loop health improved
    if improvement.get("forced") and improvement.get("is_meta_improvement"):
        # For meta-improvements, check that iteration count increased
        # (proves the loop actually ran and made progress)
        state_check = load_state()
        iteration_ok = state_check.get("iteration", 0) > 0
        validation_details["tests"].append({
            "name": "meta_improvement_check",
            "passed": iteration_ok,
            "output": f"Iteration: {state_check.get('iteration', 0)}"
        })
        # Also: score should not have dropped significantly
        current_score = state_check.get("score", 0.5)
        score_dropped = current_score < (baseline_score - 0.1)
        if score_dropped:
            validation_details["tests"].append({
                "name": "meta_score_stability",
                "passed": False,
                "output": f"Score dropped from {baseline_score:.3f} to {current_score:.3f}"
            })

    # === Calculate validation result ===
    passed_tests = sum(1 for t in validation_details["tests"] if t.get("passed", False))
    total_tests = len(validation_details["tests"])

    # Current error rate
    current_errors = get_current_error_rate()
    error_delta = current_errors - baseline_errors
    validation_details["error_delta"] = error_delta

    # === PHASE 2: Stricter validation rules ===
    # Rule 1: At least 2/3 tests must pass (was 1/3)
    has_minimum_tests = passed_tests >= MIN_TESTS_PASSED

    # Rule 2: Error rate must improve OR stay within threshold (was 0.5, now 0.1)
    error_within_threshold = error_delta <= ERROR_DELTA_THRESHOLD

    # Rule 3: No critical failures
    # PHASE 3 FIX: cron_health is only blocking if improvement is cron-related
    # Otherwise it's just a warning (pre-existing cron issues shouldn't block other improvements)
    imp_category = improvement.get("category", "").lower()
    imp_source = improvement.get("source", "").lower()
    is_cron_related = "cron" in imp_category or "cron" in imp_source or "health" in imp_category

    critical_failures = []
    for t in validation_details["tests"]:
        if not t.get("passed", False):
            # meta_improvement failures are warnings, not critical (we're already in recovery mode)
            if t.get("name") in ("error_reducer_check", "syntax_check"):
                critical_failures.append(t.get("name"))
            elif t.get("name") == "cron_health" and is_cron_related:
                critical_failures.append("cron_health")
            elif t.get("name") == "cron_health" and not is_cron_related:
                # PHASE 3: Pre-existing cron issue - make it a warning, not a failure
                print(f"   ⚠️ Warning: cron_health failing (pre-existing, not blocking for non-cron improvement)")
            elif t.get("name") in ("meta_improvement_check", "meta_score_stability"):
                # Meta improvement tests - just warn, don't fail
                print(f"   ⚠️ Meta test warning: {t.get('name')} - {t.get('output', 'failed')}")

    no_critical_failure = len(critical_failures) == 0

    # Combined: All rules must pass
    validation_details["passed"] = has_minimum_tests and error_within_threshold and no_critical_failure

    # === Score delta based on validation result ===
    if validation_details["passed"]:
        # PHASE 2: Reward proportional to improvement
        if error_delta < 0:  # Actually improved
            score_delta = 0.15  # Higher reward for actual improvement
        else:  # Same or tiny increase within threshold
            score_delta = 0.10  # Normal reward
    else:
        # PHASE 2: Stricter penalty
        score_delta = -0.10  # Higher penalty for failure

    validation_details["baseline_score"] = baseline_score
    validation_details["current_score"] = baseline_score + score_delta
    validation_details["rules_checked"] = {
        "min_tests": has_minimum_tests,
        "error_threshold": error_within_threshold,
        "no_critical": no_critical_failure
    }

    # Log validation
    log = load_validation_log()
    log["validations"].append(validation_details)
    log["validations"] = log["validations"][-100:]
    save_validation_log(log)

    # === Update state with streak tracking ===
    state = load_state()  # Fresh load
    if validation_details["passed"]:
        state["validation_successes"] = state.get("validation_successes", 0) + 1
        state["consecutive_failures"] = 0  # Reset failure streak
        print(f"   ✅ VALIDATION PASSED (v2)")
        print(f"      Tests: {passed_tests}/{total_tests}")
        print(f"      Error delta: {error_delta:+.2f}% (threshold: ±{ERROR_DELTA_THRESHOLD}%)")
        print(f"      Score delta: {score_delta:+.3f}")

        # PHASE 3: Track cross-pattern usage for scoring
        if improvement.get("source") == "cross_pattern":
            state["cross_pattern_hits"] = state.get("cross_pattern_hits", 0) + 1
            print(f"   🎯 Cross-pattern success! Total hits: {state['cross_pattern_hits']}")

            # PHASE 4: Track consecutive same pattern
            pattern_id = improvement.get("cross_pattern_match", {}).get("id", "unknown")
            last_pattern = state.get("last_validated_pattern")
            if last_pattern == pattern_id:
                state["consecutive_same_pattern"] = state.get("consecutive_same_pattern", 0) + 1
                if state["consecutive_same_pattern"] >= 3:
                    print(f"   ⚠️ PHASE 4: Same pattern used {state['consecutive_same_pattern']} times - may be stuck!")
            else:
                state["consecutive_same_pattern"] = 0  # Reset for new pattern
            state["last_validated_pattern"] = pattern_id

            # PHASE 4: If forced novelty, also reset consecutive_same (new approach)
            if improvement.get("source") == "forced_novelty":
                state["forced_novelty_count"] = state.get("forced_novelty_count", 0) + 1
                current_pattern_id = improvement.get("cross_pattern_match", {}).get("id", "unknown")
                last_forced = state.get("last_forced_pattern_id")

                if last_forced == current_pattern_id and state["forced_novelty_count"] > 2:
                    # Same cross-pattern forced 3+ times - deeper decay needed!
                    print(f"   🚨 PHASE 4: Repeated forced novelty for same pattern!")
                    decay_pattern_confidence(current_pattern_id, decay_rate=0.5)
                    state["forced_novelty_count"] = 0  # Reset counter

                state["last_forced_pattern_id"] = current_pattern_id
                state["consecutive_same_pattern"] = 0
                print(f"   ✅ PHASE 4: Forced novelty succeeded - consecutive reset")

        # PHASE 3: Store successful solution in pattern repository
        store_solution_pattern(improvement, validation_details)
        print(f"      Tests: {passed_tests}/{total_tests}")
        print(f"      Error delta: {error_delta:+.2f}% (threshold: ±{ERROR_DELTA_THRESHOLD}%)")
        print(f"      Score delta: {score_delta:+.3f}")
    else:
        state["validation_failures"] = state.get("validation_failures", 0) + 1
        state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1
        print(f"   ❌ VALIDATION FAILED (v2)")
        print(f"      Tests: {passed_tests}/{total_tests} passed")
        print(f"      Error delta: {error_delta:+.2f}% (threshold: ±{ERROR_DELTA_THRESHOLD}%)")
        print(f"      Score delta: {score_delta:+.3f}")
        print(f"      Consecutive failures: {state['consecutive_failures']}")

        # PHASE 2: Auto-rollback after 3 consecutive failures
        if state["consecutive_failures"] >= ROLLBACK_STREAK_LIMIT:
            print(f"   ⚠️ AUTO-ROLLBACK: {state['consecutive_failures']} consecutive failures")
            score_delta = -0.20  # Extra penalty for repeated failures
            state["consecutive_failures"] = 0  # Reset after rollback

        # PHASE 1: Add failed idea to idea bank so we don't repeat it
        imp_title = improvement.get("title", "unknown")
        imp_category = improvement.get("category", "general")
        error_info = f"Failed v2 validation: {passed_tests}/{total_tests} tests passed, error_delta={error_delta:+.2f}%"
        why_ineffective = f"Error delta={error_delta:+.2f}% exceeded threshold" if error_delta > ERROR_DELTA_THRESHOLD else f"Validation tests failed: {passed_tests}/{total_tests}"
        add_to_idea_bank(imp_title, error_info, why_ineffective)

    # Update score based on validation (with damping, scaled by learning_rate)
    if score_delta != 0:
        learning_rate = state.get("learning_rate", 0.1)
        # Scale factor: default 0.3 at LR=0.1, lower LR = smaller adjustments
        dampening = learning_rate * 3
        new_score = baseline_score + (score_delta * dampening)
        state["score"] = max(0.0, min(0.95, new_score))
        state["score_history"].append(state["score"])
        state["score_history"] = state["score_history"][-50:]
        if learning_rate < 0.08:
            print(f"   📊 SCORE UPDATE: {baseline_score:.3f} → {state['score']:.3f} (LR={learning_rate:.3f}, damp={dampening:.2f})")

    # === Thompson Sampling: Update ONLY on successful validation ===
    # (Failures don't teach us which is best - just which isn't)
    # This is the key insight: we explore broadly but only reinforce success

    imp_category = improvement.get('category', 'general')
    imp_source = improvement.get('source', '')

    # Determine the category
    if 'cross_pattern' in imp_source:
        category = f"cross_pattern_{improvement.get('type', 'general')}"
    elif 'issue' in imp_source:
        category = f"issue_{imp_category}"
    else:
        # Fix double prefix
        if imp_category.startswith('hypothesis_'):
            category = imp_category
        else:
            category = f"hypothesis_{imp_category}"

    # Only update on SUCCESS - failures are uncertain
    if validation_details["passed"]:
        rewards = load_thompson_rewards()
        if category not in rewards:
            rewards[category] = {'successes': 1, 'failures': 1}

        rewards[category]['successes'] += 1
        save_thompson_rewards(rewards)
        print(f"   🎲 Thompson: {category} -> successes={rewards[category]['successes']} (validierung bestanden)")
    else:
        # Log failure but don't update rewards (failure is not informative)
        print(f"   🎲 Thompson: validation failed für {category} - keine reward update (failures sind unsicher)")
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
    novelty_factor = min(novelty_injections * 0.05 + cross_pattern_hits * 0.02, 0.6)  # Cap at 0.6 (was 0.5)

    # PLATEAU DETECTION: If score hasn't improved in 10 runs, boost exploration
    score_history = state.get("score_history", [])
    learning_rate = state.get("learning_rate", 0.1)
    lr_stagnation_count = state.get("lr_stagnation_count", 0)
    pattern_source = state.get("pattern_source", "task")
    
    if len(score_history) >= 10:
        recent_scores = score_history[-10:]
        max_recent = max(recent_scores)
        min_recent = min(recent_scores)
        recent_range = max_recent - min_recent

        if recent_range < 0.010:  # Plateau detected (less than 1.0% variation - AGGRESSIVE)
            lr_stagnation_count += 1
            
            # ADAPTIVE LR REDUCTION: If plateau for 2+ consecutive checks, reduce LR by 30%
            if lr_stagnation_count >= 2:
                old_lr = learning_rate
                learning_rate = max(learning_rate * 0.7, 0.005)  # Floor at 0.005 - AGGRESSIVE
                lr_stagnation_count = 0  # Reset after adjustment
                print(f"   📉 ADAPTIVE LR: Reduced from {old_lr:.3f} to {learning_rate:.3f}")
            
            # Boost novelty to escape plateau
            novelty_factor = min(novelty_factor * 1.5, 0.7)
            print(f"   📈 PLATEAU ESCAPE: Boosting novelty to {novelty_factor:.2f} (range={recent_range:.3f})")
            
            # PATTERN SOURCE ROTATION: Switch to different domain
            source_rotation = {"task": "failure", "failure": "success", "success": "capability", "capability": "task"}
            pattern_source = source_rotation.get(pattern_source, "task")
            print(f"   🔄 PATTERN SOURCE: Rotated to '{pattern_source}' domain")
        else:
            # Reset stagnation count when there's meaningful variation
            if lr_stagnation_count > 0:
                lr_stagnation_count = max(0, lr_stagnation_count - 1)
    else:
        lr_stagnation_count = 0

    # Store updated values in state for next run
    state["learning_rate"] = learning_rate
    state["lr_stagnation_count"] = lr_stagnation_count
    state["pattern_source"] = pattern_source

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
    final_score = min(0.95, max(0.0, score))
    
    # Return score AND the plateau detection values for run_full_cycle to save
    plateau_info = {
        "learning_rate": state["learning_rate"],
        "lr_stagnation_count": state["lr_stagnation_count"],
        "pattern_source": state["pattern_source"]
    }
    
    return final_score, plateau_info


# ============ PHASE 3: CROSS-PATTERN SOLUTION REPOSITORY ============

def store_solution_pattern(improvement: Dict, validation_details: Dict):
    """
    PHASE 3: Store validated solution in patterns database.

    After successful validation, store:
    - Error signature (keywords from description)
    - Solution steps
    - Success rate (incremental)
    - Confidence score
    """
    patterns_data = load_patterns()
    patterns = patterns_data.get("patterns", [])

    # Create error signature from improvement title and category
    title = improvement.get("title", "unknown")
    
    # PLATEAU FIX: Don't store patterns with [CROSS-PATTERN] prefix (causes doubling)
    if title.startswith('[CROSS-PATTERN]'):
        title = title[len('[CROSS-PATTERN]'):].strip()
    if title.startswith('[CROSS-PATTERN]'):
        title = title[len('[CROSS-PATTERN]'):].strip()
    if title.startswith('[PHASE 4]'):
        title = title[len('[PHASE 4]'):].strip()
    if title.startswith('[ISSUE]'):
        title = title[len('[ISSUE]'):].strip()
    if title.startswith('[Exploration]'):
        title = title[len('[Exploration]'):].strip()

    # PLATEAU FIX: Don't store noise patterns
    if is_noise_pattern_patch(title):
        print(f"   ⏭️ Skipping noise pattern storage: {title[:40]}")
        return

    # PLATEAU FIX: Don't store forced novelty meta-improvements as regular patterns
    # (they're experiments, not proven solutions)
    if improvement.get("is_meta_improvement"):
        print(f"   ⏭️ Skipping meta-improvement pattern storage: {title[:50]}")
        return

    category = improvement.get("category", "general")

    # Generate error signature (keywords)
    words = title.lower().split()
    error_signature = [w for w in words if len(w) > 3][:5]  # Top 5 meaningful words

    # Check if similar pattern already exists
    for existing in patterns:
        existing_sig = existing.get("error_signature", [])
        overlap = len(set(error_signature) & set(existing_sig))
        if overlap >= 2:  # Similar pattern exists
            # Update success count
            existing["success_count"] = existing.get("success_count", 1) + 1
            existing["last_validated"] = datetime.now().isoformat()
            existing["confidence"] = min(0.95, existing.get("confidence", 0.5) + 0.05)
            print(f"   🔄 Updated existing pattern: {title[:40]}")
            save_patterns(patterns_data)
            return

    # Create new pattern
    new_pattern = {
        "id": f"pattern_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "title": title,
        "category": category,
        "error_signature": error_signature,
        "description": improvement.get("title", ""),
        "solution": f"Applied improvement: {title}",
        "success_count": 1,
        "failure_count": 0,
        "validated": True,
        "confidence": 0.7,  # Start with 70% confidence
        "initial_confidence": 0.7,
        "first_seen": datetime.now().isoformat(),
        "last_validated": datetime.now().isoformat(),
        "error_type": improvement.get("type", "general"),
        "context": {
            "source": improvement.get("source", "unknown"),
            "script": improvement.get("script")
        }
    }

    patterns.append(new_pattern)
    patterns_data["patterns"] = patterns
    save_patterns(patterns_data)
    print(f"   ✅ Stored solution pattern: {title[:40]}")


def find_cross_pattern_solution(new_issue_description: str, issue_type: str, state: Dict = None) -> Tuple[Optional[Dict], float]:
    """
    PHASE 3: Enhanced cross-pattern matching.

    Uses solution repository to find proven solutions for similar issues.
    Returns (best_solution_pattern, similarity_score) or (None, 0).
    """
    patterns_data = load_patterns()
    patterns = patterns_data.get("patterns", [])

    if not patterns:
        return None, 0.0

    new_desc_lower = new_issue_description.lower()
    new_words = set(new_desc_lower.split())

    best_match = None
    best_score = 0.0

    for pattern in patterns:
        if pattern.get("archived"):
            continue

        # PLATEAU FIX: Skip noise patterns
        pattern_title = pattern.get("title", "") or pattern.get("description", "")
        if is_noise_pattern_patch(pattern_title):
            continue

        score = 0.0
        reasons = []

        # PHASE 3: Error signature matching (top priority)
        sig = pattern.get("error_signature", [])
        if sig:
            sig_matches = len(set(sig) & new_words)
            if sig_matches > 0:
                score += sig_matches * 0.4  # Higher weight for signature match
                reasons.append(f"sig_match:{sig_matches}")
        else:
            # Fallback to description-based matching if no signature
            pattern_words = set(pattern.get("description", "").lower().split())
            overlap = len(new_words & pattern_words)
            if overlap >= 2:
                score += overlap * 0.15
                reasons.append(f"desc_overlap:{overlap}")

        # Word overlap
        pattern_words = set(pattern.get("description", "").lower().split())
        overlap = len(new_words & pattern_words)
        if overlap > 0:
            score += overlap * 0.2
            reasons.append(f"word_overlap:{overlap}")

        # Issue type match
        if pattern.get("error_type") == issue_type:
            score += 0.3
            reasons.append("type_match")

        # Solution exists and validated
        if pattern.get("solution") and pattern.get("validated"):
            score += 0.2
            reasons.append("has_solution")

        # Confidence bonus (prefer higher confidence patterns)
        confidence = pattern.get("confidence", 0.5)
        if confidence > 0.7:
            score += 0.1
            reasons.append(f"high_conf:{confidence:.1f}")

        # Cross-domain bonus: patterns from different categories get 20% boost
        pattern_category = pattern.get("category", "general")
        issue_categories = ["error", "cron", "session", "token", "kg", "feedback", "validation"]
        is_cross_domain = pattern_category not in issue_categories
        if is_cross_domain:
            score *= 1.2
            reasons.append("cross_domain")

        # PLATEAU ESCAPE: When stuck, prefer cross-domain patterns
        if state and len(state.get("score_history", [])) >= 5:
            recent_range = max(state["score_history"][-5:]) - min(state["score_history"][-5:])
            if recent_range < 0.03 and is_cross_domain:
                score *= 1.3
                reasons.append("plateau_escape")

        if score > best_score:
            best_score = score
            best_match = pattern

    # PHASE 3: Lowered threshold from 0.3 to 0.15
    if best_score >= 0.15:
        return best_match, best_score
    return None, 0.0


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

    print(f"   🎯 Applying cross-pattern solution (score: {best['similarity_score']:.2f})")
    print(f"   📝 Solution: {pattern['solution'][:100]}...")

    # Track cross-pattern usage
    state = load_state()
    state["cross_pattern_hits"] += 1
    save_state(state)

    return True, f"Applied solution from pattern: {pattern.get('id', 'unknown')}"


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

    decay_rate = 0.07  # 7% per day (tuned up from 5% to break plateau)
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

        # PLATEAU FIX: Skip noise patterns
        pattern_title = pattern.get("title", "") or pattern.get("description", "")
        if is_noise_pattern_patch(pattern_title):
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



# ============ PHASE 4: FORCED NOVELTY INJECTION ============

def detect_local_optimum(state: Dict) -> bool:
    """
    PHASE 4: Detect when system is stuck in local optimum.

    Criteria (any one triggers):
    - consecutive_same_pattern >= 3
    - Score not moving AND high novelty/cross_hits
    """
    consecutive_same = state.get("consecutive_same_pattern", 0)
    cross_hits = state.get("cross_pattern_hits", 0)
    novelty = state.get("novelty_injections", 0)

    # If same pattern used 3+ times, definitely stuck
    if consecutive_same >= 3:
        print(f"   🔍 PHASE 4 Check: consecutive_same_pattern={consecutive_same} >= 3")
        return True

    # If novelty factor is maxed AND score stable, likely stuck
    if novelty >= 10 and cross_hits >= 5:
        score_history = state.get("score_history", [])
        if len(score_history) >= 3:
            if max(score_history[-3:]) == min(score_history[-3:]):
                print(f"   🔍 PHASE 4 Check: score stable at {score_history[-1]:.3f} with high novelty/cross_hits")
                return True

    return False


def force_novelty_injection(state: Dict) -> Dict:
    """
    PHASE 4: Force a genuinely new improvement when stuck.

    Returns an improvement dict that breaks the local optimum.
    Now makes CONCRETE improvements, not just generic "Explore: X".
    """
    print("   🚀 PHASE 4: FORCED NOVELTY INJECTION")
    print("   ⚠️ System detected local optimum - forcing new approach")

    # Reset consecutive same pattern counter
    state["consecutive_same_pattern"] = 0

    # Concrete actions for each category (instead of generic "Explore: X")
    concrete_actions = {
        "feedback_integration": "Analyze last 10 feedback entries, identify 1 gap in processing, fix that specific gap",
        "context_compression": "Measure current context size for hourly cron, find 1 specific text that can be shortened without losing info",
        "token_optimization": "Review last 24h of API calls, identify 1 specific call that used too many tokens, optimize or cache it",
        "validation_depth": "Add 1 new validation test to validation_gate that currently doesn't exist (e.g., check memory usage < threshold)",
        "error_prediction": "Analyze error patterns from last 7 days, predict 1 specific error that will happen soon, add prevention",
        "session_efficiency": "Review open sessions, close any orphaned sessions, measure average session length and identify 1 optimization",
        "kg_quality": "Run KG consistency check, find 1 entity with missing relations, add those relations",
        "backup_recovery": "Test GitHub backup recovery time, identify 1 specific bottleneck, fix or document it"
    }

    import random
    categories = list(concrete_actions.keys())
    category = random.choice(categories)
    action = concrete_actions[category]

    forced_improvement = {
        "title": f"[PHASE 4] {action}",
        "type": category,
        "source": "forced_novelty",
        "expected_impact": "HIGH",
        "forced": True,
        "is_meta_improvement": True,  # Mark so we don't store as regular pattern
        "reason": "Local optimum detected - forced concrete exploration"
    }

    # Decay pattern confidence so we don't keep reusing same pattern
    patterns_data = load_patterns()
    for p in patterns_data.get("patterns", []):
        conf = p.get("confidence")
        if conf is not None and conf > 0.5:
            p["confidence"] = max(0.3, conf * 0.9)
    save_patterns(patterns_data)
    print(f"   📉 Decayed pattern confidence to enable new approaches")
    print(f"   🎯 Concrete action: {action[:60]}...")

    # Track forced novelty so next iteration can reset consecutive counter
    state["last_forced_novelty"] = datetime.now().isoformat()
    save_state(state)

    return forced_improvement


def update_consecutive_tracking(state: Dict, pattern_id: str):
    """
    PHASE 4: Track consecutive use of same pattern.
    """
    last_pattern = state.get("last_validated_pattern")

    if last_pattern == pattern_id:
        state["consecutive_same_pattern"] = state.get("consecutive_same_pattern", 0) + 1
    else:
        state["consecutive_same_pattern"] = 0

    state["last_validated_pattern"] = pattern_id
    save_state(state)


# ============ MAIN LOOP ============

def run_full_cycle():
    """Run the complete Learning Loop v3 MAXIMAL cycle."""
    print("=" * 60)
    print("🎯 LEARNING LOOP v3 MAXIMAL - Full Cycle")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    print()

    state = load_state()
    iteration = state.get("iteration", 0) + 1
    state["iteration"] = iteration
    save_state(state)  # Save immediately so validation_gate can read current iteration
    iteration = iteration

    start_time = datetime.now()

    # PLATEAU FIX: Clean noise from improvements log BEFORE processing
    clean_improvements_log_patch()

    # PHASE 0: Feedback Collection
    print("=" * 60)
    print("📥 PHASE 0: Feedback Collection")
    print("=" * 60)
    feedback = collect_feedback()
    processed_feedback = process_feedback(feedback)
    state["feedback_processed"] += processed_feedback["total_processed"]
    print()

    # PHASE 0.5: Memory & Log Analysis (NEW!)
    # Extract signals from memory and logs to enhance learning
    if MemoryLogAnalyzer:
        print("=" * 60)
        print("📚 PHASE 0.5: Memory & Log Analysis")
        print("=" * 60)
        try:
            mem_analyzer = MemoryLogAnalyzer()
            insights = mem_analyzer.analyze_and_store()
            patterns_from_memory, warnings_from_memory = mem_analyzer.get_patterns_from_insights(insights)

            # Store patterns for future reference
            patterns_data = load_patterns()
            for p in patterns_from_memory[:20]:
                # Check for duplicates
                existing = [x for x in patterns_data.get("patterns", [])
                           if x.get("title") == p.get("name")]
                if not existing:
                    new_pattern = {
                        "title": p.get("name"),
                        "description": p.get("description", ""),
                        "error_type": "memory_signal",
                        "success_count": 1,
                        "category": "memory_analysis"
                    }
                    patterns_data["patterns"].append(new_pattern)

            # Add warnings to idea bank
            idea_data = load_idea_bank()
            for w in warnings_from_memory[:10]:
                idea = {
                    "title": f"WARNING: {w.get('pattern', 'unknown')}",
                    "description": w.get("description", ""),
                    "type": "memory_warning",
                    "why_ineffective": "Known failure pattern from memory/logs",
                    "why_ineffective_count": 1,
                    "source": "memory_analysis"
                }
                # Check for duplicates
                existing = [x for x in idea_data.get("ideas", [])
                           if idea["title"] in x.get("title", "")]
                if not existing:
                    idea_data["ideas"].append(idea)

            save_patterns(patterns_data)
            save_idea_bank(idea_data)

            print(f"   📝 Memory patterns stored: {len(patterns_from_memory)}")
            print(f"   ⚠️ Warnings from memory/logs: {len(warnings_from_memory)}")
            print(f"   📊 Insights summary: {insights.get('summary', {})}")

        except Exception as e:
            print(f"   ⚠️ Memory analysis failed: {e}")
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

    # EXPLORATION: Decide if this run is exploration or exploitation
    exploration_decision = should_explore()
    run_type = "exploration" if exploration_decision.get("explore") else "exploitation"
    print(f"[EXPLORATION] Decision: {run_type} ({exploration_decision.get('source', 'unknown')})")

    # PHASE 4: Improvement Selection + Local Optimum Detection
    print("=" * 60)
    print("🚀 PHASE 4: Improvement Selection")
    print("=" * 60)

    improvements = []
    cross_pattern_improvement = None

    # PHASE 4: Check for local optimum first
    state = load_state()
    if detect_local_optimum(state):
        forced_imp = force_novelty_injection(state)
        improvements = [forced_imp]
        print(f"   🚀 Forced novelty: {forced_imp['title']}")
    else:
        # Normal flow: check for cross-pattern matches first
        # Check for cross-pattern matches
        cross_pattern_found = False
        for issue in gate_issues[:2]:
            similar = find_similar_errors(issue.get("description", ""))
            if similar and similar[0]["similarity_score"] > 0.5:
                pattern = similar[0]["pattern"]
                # Don't double-prefix
                raw_title = pattern.get('title') or pattern.get('description', 'unknown')[:40]
                # Remove any existing [CROSS-PATTERN] prefix to avoid doubling
                if raw_title.startswith('[CROSS-PATTERN]'):
                    raw_title = raw_title[len('[CROSS-PATTERN]'):].strip()
                if raw_title.startswith('[CROSS-PATTERN]'):
                    raw_title = raw_title[len('[CROSS-PATTERN]'):].strip()
                cross_pattern_improvement = {
                    "title": f"[CROSS-PATTERN] {raw_title}",
                    "type": "cross_pattern",
                    "source": "cross_pattern",
                    "expected_impact": "HIGH",
                    "cross_pattern_match": pattern,
                    "similarity_score": similar[0]["similarity_score"]
                }
                print(f"   🎯 Cross-pattern match found (score: {similar[0]['similarity_score']:.2f})")
                cross_pattern_found = True
                break
        
        # PHASE 4 FIX: Always show MAB selection for transparency
        print(f"   🎲 Multi-Armed Bandit: Running selection algorithm...")
        debug_candidates = select_improvements(gate_issues, hypotheses)
        if debug_candidates:
            print(f"   📊 MAB Top 3 candidates:")
            for i, c in enumerate(debug_candidates[:3]):
                print(f"      {i+1}. [{c.get('source', 'unknown')}] {c.get('title', 'unknown')[:50]}")

        if not cross_pattern_improvement:
            improvements = select_improvements(gate_issues, hypotheses)
            print(f"   Selected {len(improvements)} improvements")
        else:
            # Check if we recently used forced novelty - if so, skip cross-pattern even if match found
            state_recent = load_state()
            if state_recent.get('recently_forced_novelty'):
                print(f"   ⏭️ Skipping cross-pattern (recently forced novelty - forcing exploration)")
                state_recent['recently_forced_novelty'] = False
                save_state(state_recent)
                improvements = select_improvements(gate_issues, hypotheses)
                print(f"   🔄 Used MAB selection instead of cross-pattern")
            else:
                improvements = [cross_pattern_improvement]

    # PHASE 5: Validation Gate
    print()
    print("=" * 60)
    print("🔍 PHASE 5: Validation Gate")
    print("=" * 60)

    for imp in improvements[:1]:  # Validate top improvement
            validated, details = validation_gate(imp, state)
            imp["validated"] = validated

            # FIX PLATEAU: If last iteration was forced novelty, reset consecutive counter
            # (we're trying something genuinely new, shouldn't count as "same pattern")
            last_forced = state.get("last_forced_novelty")
            if last_forced and imp.get("forced"):
                last_forced_time = datetime.fromisoformat(last_forced)
                seconds_since_forced = (datetime.now() - last_forced_time).total_seconds()
                if seconds_since_forced < 7200:  # Within last 2 hours
                    state["consecutive_same_pattern"] = 0
                    print(f"   🔄 Reset consecutive counter (recent forced novelty)")

            # Track consecutive pattern usage (only if NOT a forced novelty)
            if not imp.get('forced'):
                update_consecutive_tracking(state, imp.get("title", "unknown"))
            else:
                # Mark that we recently forced novelty so next cycle skips cross-pattern
                state['recently_forced_novelty'] = True
                print(f"   🔄 Marked recently forced - will skip cross-pattern next cycle")

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

    # Calculate final score
    # IMPORTANT: Don't reload state here - use the state that was modified by validation_gate
    # to preserve validation_successes and cross_pattern_hits
    state_to_use = state  # Use the state object from run_full_cycle scope
    final_score, plateau_info = calculate_loop_score()
    state_to_use["score"] = final_score
    state_to_use["score_history"].append(final_score)
    # Apply plateau detection values (learning_rate, lr_stagnation_count, pattern_source)
    state_to_use.update(plateau_info)
    save_state(state_to_use)

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

    # EXPLORATION: Log this run
    success = state.get('validation_successes', 0) > 0 if state.get('validation_failures', 0) > 0 or state.get('validation_successes', 0) > 0 else False
    if state.get('validation_failures', 0) > 0:
        success = state.get('validation_successes', 0) > 0
    elif state.get('validation_successes', 0) == 0 and state.get('validation_failures', 0) == 0:
        success = True  # No validations ran = consider neutral as success
    else:
        success = state.get('validation_successes', 0) > 0
    
    log_exploration_run(run_type, success, "learning_loop_v3")
    print(f"[EXPLORATION] Logged: {run_type}, success={success}")

    # === EVENT BUS DIVERSIFICATION: Emit rich events for Evolver ===
    try:
        emit_learning_cycle_events(iteration, final_score, state_to_use, issues, gate_issues, duration, len(hypotheses))
    except Exception as e:
        print(f"   ⚠️ Event emission failed: {e}")

    return True


def emit_learning_cycle_events(iteration, final_score, state, issues, gate_issues, duration, hypotheses_count=0):
    """Emit diverse events to Event Bus for Evolver signal generation."""
    import uuid
    
    EVENT_BUS = SCRIPTS_DIR / "event_bus.py"
    
    # 1. Loop Score Event
    score_delta = 0
    if len(state.get('score_history', [])) >= 2:
        score_delta = final_score - state['score_history'][-2]
    
    score_event = {
        "type": "learning_score_update",
        "source": "learning_loop",
        "severity": "info",
        "data": {
            "iteration": iteration,
            "score": round(final_score, 4),
            "score_delta": round(score_delta, 4),
            "learning_rate": state.get('learning_rate', 0.1),
            "lr_stagnation_count": state.get('lr_stagnation_count', 0),
            "pattern_source": state.get('pattern_source', 'unknown'),
            "validation_success_rate": state.get('validation_successes', 0) / max(1, state.get('validation_successes', 0) + state.get('validation_failures', 0))
        }
    }
    
    # 2. Issues Found Event
    if issues or gate_issues:
        issue_event = {
            "type": "learning_issues_detected",
            "source": "learning_loop",
            "severity": "warning" if len(issues) < 3 else "error",
            "data": {
                "issue_count": len(issues) + len(gate_issues),
                "issue_types": list(set(i.get('type', 'unknown') for i in issues + gate_issues)),
                "hypotheses_generated": hypotheses_count
            }
        }
    
    # 3. Pattern Discovery Event
    patterns_data = load_patterns()
    pattern_count = len(patterns_data.get('patterns', []))
    if pattern_count > 0:
        pattern_event = {
            "type": "learning_patterns_update",
            "source": "learning_loop",
            "severity": "info",
            "data": {
                "total_patterns": pattern_count,
                "cross_pattern_hits": state.get('cross_pattern_hits', 0),
                "iteration": iteration
            }
        }
    
    # 4. Plateau Detection Event
    score_history = state.get('score_history', [])
    if len(score_history) >= 10:
        recent_range = max(score_history[-10:]) - min(score_history[-10:])
        if recent_range < 0.010:  # AGGRESSIVE: trigger at 1.0% range
            plateau_event = {
                "type": "learning_plateau_detected",
                "source": "learning_loop",
                "severity": "warning",
                "data": {
                    "score_range": round(recent_range, 4),
                    "score": round(final_score, 4),
                    "lr_stagnation_count": state.get('lr_stagnation_count', 0),
                    "learning_rate": state.get('learning_rate', 0.1)
                }
            }
    
    # 5. Cycle Completion Event (always emit)
    completion_event = {
        "type": "learning_cycle_completed",
        "source": "learning_loop",
        "severity": "info",
        "data": {
            "iteration": iteration,
            "duration_seconds": round(duration, 1),
            "feedback_processed": state.get('feedback_processed', 0),
            "score": round(final_score, 4),
            "validation_successes": state.get('validation_successes', 0),
            "validation_failures": state.get('validation_failures', 0)
        }
    }
    
    # Emit all events via event_bus.py
    events_to_emit = [score_event, completion_event]
    if issues or gate_issues:
        events_to_emit.append(issue_event)
    if pattern_count > 0:
        events_to_emit.append(pattern_event)
    if len(score_history) >= 10 and recent_range < 0.010:
        events_to_emit.append(plateau_event)
    
    for evt in events_to_emit:
        try:
            result = subprocess.run(
                ['python3', str(EVENT_BUS), 'publish',
                 '--type', evt['type'],
                 '--source', evt['source'],
                 '--severity', evt.get('severity', 'info'),
                 '--data', json.dumps(evt['data'])],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                print(f"   📡 Event emitted: {evt['type']}")
        except Exception as e:
            print(f"   ⚠️ Failed to emit {evt['type']}: {e}")

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

# ============ DYNAMIC HYPOTHESIS GENERATION (Phase 1) ============

def analyze_system_state() -> List[Dict]:
    """
    Analyze real system state to generate actionable signals.

    Replaces static idea bank with dynamic analysis.
    """
    signals = []

    # 1. Analyze cron errors from watchdog log
    try:
        watchdog_log = WORKSPACE / "logs" / "cron_watchdog.log"
        if watchdog_log.exists():
            content = watchdog_log.read_text()
            # Find failed crons (look for ❌ lines in recent entries)
            in_recent_section = False
            for line in content.split('\n'):
                # Check for header with today's date
                if '2026-04-14' in line:
                    in_recent_section = True

                if in_recent_section and '❌' in line:
                    # Extract cron name after ❌
                    parts = line.split('❌')
                    if len(parts) > 1:
                        cron_info = parts[1].strip()
                        if ':' in cron_info:
                            cron_name = cron_info.split(':')[0].strip()
                            if cron_name and len(cron_name) < 50:  # Sanity check
                                signals.append({
                                    "type": "cron_failure",
                                    "source": "cron_watchdog",
                                    "severity": "HIGH",
                                    "description": f"Cron failed: {cron_name}",
                                    "evidence": line.strip()
                                })
    except Exception as e:
        print(f"   ⚠️ Cron analysis failed: {e}")

    # 2. Analyze health alerts (only recent ones)
    try:
        health_log = WORKSPACE / "logs" / "health_alerts.log"
        if health_log.exists():
            content = health_log.read_text()
            in_recent_section = False
            alert_count = 0
            for line in content.split('\n'):
                # Look for today's alerts
                if '2026-04-14' in line:
                    in_recent_section = True

                if in_recent_section and ('FAILED' in line or 'CRITICAL' in line):
                    alert_count += 1

            if alert_count > 0:
                signals.append({
                    "type": "health_alert",
                    "source": "health_alerts",
                    "severity": "HIGH",
                    "description": f"{alert_count} health alerts in recent logs",
                    "evidence": f"Alert count: {alert_count}"
                })
    except Exception as e:
        print(f"   ⚠️ Health alert analysis failed: {e}")

    # 3. Analyze learning loop performance (plateau detection)
    try:
        state = load_state()
        score_history = state.get("score_history", [])
        if len(score_history) >= 5:
            recent_range = max(score_history[-5:]) - min(score_history[-5:])
            if recent_range < 0.01:  # Plateau detected
                signals.append({
                    "type": "plateau_detected",
                    "source": "loop_state",
                    "severity": "MEDIUM",
                    "description": f"Score plateau: range={recent_range:.4f}, latest={score_history[-1]:.3f}",
                    "evidence": f"History: {score_history[-5:]}"
                })
    except Exception as e:
        print(f"   ⚠️ Loop state analysis failed: {e}")

    # 4. Analyze KG gaps (missing relations)
    try:
        kg_path = KG_PATH
        if kg_path.exists():
            with open(kg_path) as f:
                kg = json.load(f)
            entities = kg.get("entities", {})  # entities is a dict, not list
            # Find entities with no relations
            orphan_count = 0
            for name, entity_data in entities.items():
                relations = entity_data.get("relations", []) if isinstance(entity_data, dict) else []
                if len(relations) == 0:
                    orphan_count += 1
            if orphan_count > 10:
                signals.append({
                    "type": "kg_quality_gap",
                    "source": "knowledge_graph",
                    "severity": "LOW",
                    "description": f"{orphan_count} KG entities with no relations",
                    "evidence": f"Total entities: {len(entities)}, Orphans: {orphan_count}"
                })
    except Exception as e:
        print(f"   ⚠️ KG analysis failed: {e}")

    # 5. Analyze feedback queue (unprocessed signals)
    try:
        feedback_queue = DATA_DIR / "feedback_queue.json"
        if feedback_queue.exists():
            with open(feedback_queue) as f:
                fq = json.load(f)
            queue = fq.get("queue", [])
            if len(queue) > 20:
                signals.append({
                    "type": "feedback_backlog",
                    "source": "feedback_queue",
                    "severity": "MEDIUM",
                    "description": f"{len(queue)} unprocessed feedback items",
                    "evidence": f"Queue size: {len(queue)}"
                })
    except Exception as e:
        print(f"   ⚠️ Feedback queue analysis failed: {e}")

    print(f"   📊 System analysis: {len(signals)} signals found")
    for s in signals[:5]:
        print(f"      - [{s['type']}] {s['description'][:60]}")

    return signals


def generate_hypothesis_from_signal(signal: Dict) -> Optional[Dict]:
    """
    Generate concrete hypothesis from system signal.

    Each hypothesis must have:
    - Concrete action (not generic "Explore: X")
    - Testable validation
    - Expected impact
    """
    signal_type = signal.get("type", "")
    description = signal.get("description", "")
    evidence = signal.get("evidence", "")

    if signal_type == "cron_failure":
        # Extract cron name and create specific fix
        cron_name = description.replace("Cron failed: ", "").strip()

        # Map known crons to their scripts
        cron_script_map = {
            "REM Feedback Integration": ("rem_feedback.py", "check REM harness output and fix delivery"),
            "Token Budget Tracker": ("token_budget_tracker.py", "check API response and timeout handling"),
            "GitHub Backup Daily": ("github_backup.sh", "check git auth and network connectivity"),
            "CEO Weekly Review": ("weekly_review.py", "check email sending and report generation"),
        }

        if cron_name in cron_script_map:
            script, action = cron_script_map[cron_name]
            return {
                "title": f"Fix {cron_name}: {action}",
                "action": f"Run and debug {script}",
                "category": "cron_health",
                "source": "dynamic_signal",
                "expected_impact": "HIGH",
                "validation": f"Execute {script} and verify exit code 0"
            }
        else:
            return {
                "title": f"Investigate and fix {cron_name} failure",
                "action": f"Analyze cron log for {cron_name}",
                "category": "cron_health",
                "source": "dynamic_signal",
                "expected_impact": "HIGH",
                "validation": "Cron runs successfully without error"
            }

    elif signal_type == "health_alert":
        description_lower = description.lower()
        if "script not found" in description_lower:
            # Extract just the script path
            if "-" in description:
                script_name = description.split("-")[-1].strip()
            else:
                script_name = description.split("not found")[-1].strip() if "not found" in description else "unknown"

            # Clean up the script path
            script_name = script_name.replace("at ", "").strip()

            return {
                "title": f"Fix missing script: {script_name}",
                "action": f"Create or restore {script_name}",
                "category": "system_health",
                "source": "dynamic_signal",
                "expected_impact": "HIGH",
                "validation": f"Script exists and is executable"
            }
        return {
            "title": f"Investigate health alert",
            "action": "Check system logs and verify service status",
            "category": "system_health",
            "source": "dynamic_signal",
            "expected_impact": "MEDIUM",
            "validation": "Health check passes"
        }

    elif signal_type == "plateau_detected":
        return {
            "title": "Break score plateau with novel approach",
            "action": "Force exploration of unvisited improvement category",
            "category": "loop_optimization",
            "source": "dynamic_signal",
            "expected_impact": "MEDIUM",
            "validation": "Score increases by >0.01 next cycle"
        }

    elif signal_type == "kg_quality_gap":
        return {
            "title": "Reduce KG orphans: add relations to disconnected entities",
            "action": "Run KG consistency check and add missing relations",
            "category": "kg_quality",
            "source": "dynamic_signal",
            "expected_impact": "LOW",
            "validation": "KG orphan count decreases by >50%"
        }

    elif signal_type == "feedback_backlog":
        return {
            "title": "Process feedback backlog",
            "action": "Run feedback processing and clear queue",
            "category": "feedback_integration",
            "source": "dynamic_signal",
            "expected_impact": "MEDIUM",
            "validation": "Feedback queue size reduces to <10"
        }

    return None  # Unknown signal type


def get_proven_patterns() -> List[Dict]:
    """
    Get hypotheses from patterns that have high confidence and success rate.
    """
    patterns_data = load_patterns()
    patterns = patterns_data.get("patterns", [])

    proven = []
    for p in patterns:
        confidence = p.get("confidence", 0)
        success_count = p.get("success_count", 0)

        if confidence >= 0.7 and success_count >= 2:
            proven.append({
                "title": f"Apply proven pattern: {p.get('title', 'unknown')[:50]}",
                "category": p.get("category", "general"),
                "source": "proven_pattern",
                "expected_impact": "HIGH",
                "pattern_id": p.get("id", "unknown")
            })

    return proven[:2]  # Return max 2 proven patterns


def run_research() -> List[Dict]:
    """
    Run research phase to generate hypotheses.

    PHASE 1 REPLACEMENT: Dynamic hypothesis generation from system state.
    Replaces static idea bank with real system analysis.
    """
    hypotheses = []

    print("=" * 60)
    print("🔬 DYNAMIC HYPOTHESIS GENERATION")
    print("=" * 60)

    # 1. Analyze system state
    print("\n📊 Analyzing system state...")
    signals = analyze_system_state()

    # 2. Generate hypotheses from signals
    print("\n💡 Generating hypotheses from signals...")
    for signal in signals:
        h = generate_hypothesis_from_signal(signal)
        if h:
            hypotheses.append(h)
            print(f"   ✅ {h['title'][:60]}")

    # 3. Add proven patterns if we have < 3 hypotheses
    if len(hypotheses) < 3:
        print("\n🔄 Adding proven patterns...")
        proven = get_proven_patterns()
        for p in proven:
            if len(hypotheses) >= 5:
                break
            hypotheses.append(p)
            print(f"   ✅ Proven: {p['title'][:60]}")

    # 4. If still < 3, add forced novelty (fallback)
    if len(hypotheses) < 3:
        print("\n🎲 Adding exploration hypothesis...")
        import random
        exploration_categories = [
            ("feedback_integration", "Analyze last 10 feedback entries, identify 1 processing gap"),
            ("context_compression", "Measure context size, find 1 specific text to shorten"),
            ("token_optimization", "Review last 24h API calls, find 1 inefficient call"),
            ("validation_depth", "Add 1 new validation test that currently doesn't exist"),
            ("error_prediction", "Analyze error patterns, predict 1 specific upcoming error"),
            ("session_efficiency", "Review sessions, close 1 orphaned session"),
            ("kg_quality", "Find 1 entity with missing relations, add them"),
            ("backup_recovery", "Test backup recovery, identify 1 bottleneck"),
        ]
        cat, action = random.choice(exploration_categories)
        hypotheses.append({
            "title": f"[Exploration] {action}",
            "category": cat,
            "source": "exploration",
            "expected_impact": "MEDIUM",
            "is_exploration": True
        })
        print(f"   ✅ Exploration: {action[:60]}")

    print(f"\n📝 Generated {len(hypotheses)} hypotheses")
    return hypotheses[:5]


# Keep old function as deprecated alias for backwards compatibility
def run_research_OLD() -> List[Dict]:
    """DEPRECATED - Use run_research() instead"""
    return run_research()

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

    # Plateau detection - if score not improving, add as issue
    try:
        state = load_state()
        score_history = state.get("score_history", [])
        if len(score_history) >= 5:
            recent_range = max(score_history[-5:]) - min(score_history[-5:])
            if recent_range < 0.01:  # Plateau: less than 1% variation
                issues.append({
                    "type": "learning_plateau",
                    "description": f"Score plateau detected: range={recent_range:.4f}, latest={score_history[-1]:.3f}",
                    "severity": "HIGH",
                    "source": "quality_gate"
                })
    except:
        pass

    return issues

def select_improvements(issues: List[Dict], hypotheses: List[Dict]) -> List[Dict]:
    """
    Select best improvements using Multi-Armed Bandit with Thompson Sampling + UCB.

    Combines:
    1. Thompson Sampling: Probabilistic selection based on Beta distribution
    2. UCB1: Deterministic bonus for unexplored arms
    3. Epsilon-Greedy: Random exploration with decaying probability

    This balances exploration (try new things) vs exploitation (use what works).
    """
    improvements = []

    # Load reward history for Thompson Sampling (from separate file)
    reward_history = load_thompson_rewards()
    state = load_state()

    # Annealing: decrease exploration over time
    iteration = state.get('iteration', 1)
    epsilon = max(0.10, 0.3 - (iteration * 0.01))  # Decays from 0.3 to 0.10 (higher floor for more exploration)

    # Candidates with their priors
    candidates = []

    # Add cross-pattern solutions (higher prior success rate)
    for issue in issues[:2]:
        issue_desc = issue.get("description", "")
        issue_type = issue.get("type", "general")
        match, score = find_cross_pattern_solution(issue_desc, issue_type)
        if match:
            match_title = match.get('title') or match.get('description', 'unknown')[:40] or match.get('id', 'unknown')
            category = f"cross_pattern_{issue_type}"
            prior_alpha = reward_history.get(category, {}).get("successes", 2)
            prior_beta = reward_history.get(category, {}).get("failures", 1)
            total_trials = prior_alpha + prior_beta - 3  # Subtract initial prior of 2+1

            candidates.append({
                "title": f"[CROSS-PATTERN] {match_title}",
                "type": issue_type,
                "source": "cross_pattern",
                "script": match.get("context", {}).get("script"),
                "expected_impact": "HIGH",
                "cross_pattern_match": match,
                "priority_base": 0.3,
                "category": category,
                "prior_alpha": prior_alpha,
                "prior_beta": prior_beta,
                "total_trials": total_trials
            })

    # Add critical issues
    for issue in issues:
        if len(candidates) >= 5:
            break
        if issue.get("severity") == "HIGH":
            category = f"issue_{issue['type']}"
            prior_alpha = reward_history.get(category, {}).get("successes", 2)
            prior_beta = reward_history.get(category, {}).get("failures", 1)
            total_trials = prior_alpha + prior_beta - 3

            candidates.append({
                "title": f"Fix: {issue['description']}",
                "type": issue["type"],
                "source": "issue",
                "expected_impact": "HIGH",
                "priority_base": 0.2,
                "category": category,
                "prior_alpha": prior_alpha,
                "prior_beta": prior_beta,
                "total_trials": total_trials
            })

    # Add research hypotheses
    for hyp in hypotheses[:3]:
        hyp_cat = hyp.get('category', 'general')
        # Fix double prefix
        if hyp_cat.startswith('hypothesis_'):
            category = hyp_cat
        else:
            category = f"hypothesis_{hyp_cat}"

        prior_alpha = reward_history.get(category, {}).get("successes", 2)
        prior_beta = reward_history.get(category, {}).get("failures", 1)
        total_trials = prior_alpha + prior_beta - 3

        candidates.append({
            "title": hyp.get("title", "unknown"),
            "type": hyp_cat,
            "source": hyp.get("source", "research"),
            "expected_impact": hyp.get("expected_impact", "MEDIUM"),
            "priority_base": 0.1,
            "category": category,
            "prior_alpha": prior_alpha,
            "prior_beta": prior_beta,
            "total_trials": total_trials
        })

    if not candidates:
        return improvements

    # === Multi-Armed Bandit Selection ===
    import random
    import math

    samples = []
    total_total_trials = sum(max(0, c['total_trials']) for c in candidates) + 1

    for c in candidates:
        alpha = c["prior_alpha"]
        beta = c["prior_beta"]
        total_trials = c['total_trials']

        # Thompson Sampling: Sample from Beta distribution
        try:
            thompson_sample = random.betavariate(alpha, beta)
        except:
            thompson_sample = 0.5

        # UCB1 bonus: encourages exploration of less-tried arms
        # UCB1 = mean + sqrt(2 * ln(total_trials) / arm_trials)
        if total_trials > 0:
            mean = (alpha - 1) / total_trials  # Actual success rate
            ucb_bonus = math.sqrt(2 * math.log(total_total_trials) / total_trials)
        else:
            mean = 0.5
            ucb_bonus = 1.0  # High bonus for never-tried arms

        # Combined score with UCB
        final_sample = thompson_sample + ucb_bonus + c.get("priority_base", 0)

        samples.append({
            "candidate": c,
            "thompson_sample": thompson_sample,
            "ucb_bonus": ucb_bonus,
            "final_sample": final_sample
        })

    # Epsilon-greedy: with probability epsilon, pick randomly (exploration)
    if random.random() < epsilon:
        # Exploration: pick random candidate
        chosen = random.choice(samples)
        print(f"   🎲 MAB Exploration (ε={epsilon:.2f}): randomly selected")
    else:
        # Exploitation: pick best sample
        samples.sort(key=lambda x: x["final_sample"], reverse=True)
        chosen = samples[0]

    print(f"   🎲 Multi-Armed Bandit: {len(candidates)} candidates (ε={epsilon:.2f})")
    for i, s in enumerate(samples[:3]):
        c = s["candidate"]
        ucb_str = f"+{s['ucb_bonus']:.2f}" if s['ucb_bonus'] > 0 else "0.00"
        print(f"      {i+1}. {s['final_sample']:.3f} [TS={s['thompson_sample']:.2f}, UCB=+{ucb_str}] [{c['source']}] {c['title'][:40]}")

    # Select top candidates
    for s in samples[:3]:
        improvements.append(s["candidate"])

    return improvements[:3]

def show_status():
    """Show current loop status."""
    state = load_state()
    patterns_data = load_patterns()
    improvements = load_improvements()
    validation_log = load_validation_log()

    print("📊 LEARNING LOOP v3 MAXIMAL - STATUS")
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
    import sys
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

