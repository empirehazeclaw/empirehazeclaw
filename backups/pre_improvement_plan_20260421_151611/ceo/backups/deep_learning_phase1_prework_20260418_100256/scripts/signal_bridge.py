#!/usr/bin/env python3
"""
Signal Bridge — Translates Learning Loop signals to Evolver-compatible signals.
=====================================================================

Problem: Learning Loop uses "performance_gap", "system_health"
         Evolver expects "evolution_stagnation_detected", "stable_success_plateau"

Solution: Map our signals to evolver signals based on semantic similarity.

Enhancements v2:
1. Context-aware mapping (time-of-day based signals)
2. Feedback loop: Store what signals produced good evolver results
3. More Learning Loop signals → Evolver signals mapping
4. Signal priority/ranking system

Usage:
    python3 signal_bridge.py --translate
    python3 signal_bridge.py --inject
    python3 signal_bridge.py --feedback <signal> <quality_score>
    python3 signal_bridge.py --stats
"""

import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
LEARNING_SIGNAL = WORKSPACE / "ceo/memory/evaluations/learning_loop_signal.json"
EVOLVER_GRAPH = WORKSPACE / "skills/capability-evolver/memory/evolution/memory_graph.jsonl"
FEEDBACK_STORE = WORKSPACE / "ceo/memory/evaluations/signal_feedback.json"

# ============================================================
# SIGNAL PRIORITY/RANKING SYSTEM
# ============================================================
# Priority: critical(0) > high(1) > medium(2) > low(3)
# Rank: composite score based on priority + feedback quality

SIGNAL_PRIORITY = {
    # Critical — always action
    "performance_gap": 0,
    "high_error_rate": 0,
    "antipattern": 0,
    
    # High — usually action
    "low_task_success_rate": 1,
    "filler_words": 1,
    "efficiency_drop": 1,
    "stagnation_detected": 1,
    
    # Medium — consider action
    "efficiency": 2,
    "score_increase": 2,
    "improvement": 2,
    
    # Low — informational only
    "system_health": 3,
    "memory_clean": 3,
}

# ============================================================
# BASE SIGNAL MAPPING: Learning Loop signals → Evolver signals
# ============================================================
BASE_SIGNAL_MAP = {
    # Performance issues → stagnation signals
    "performance_gap": ["evolution_stagnation_detected"],
    "low_task_success_rate": ["evolution_stagnation_detected", "stable_success_plateau"],
    "high_error_rate": ["stable_success_plateau", "evolution_stagnation_detected"],
    
    # Efficiency signals
    "efficiency": ["stable_success_plateau"],
    "efficiency_drop": ["evolution_stagnation_detected"],
    
    # Quality signals
    "task_success_rate": ["stable_success_plateau"],
    "accuracy": ["stable_success_plateau"],
    "response_quality": [],
    
    # System signals
    "system_health": [],
    "memory_clean": [],
    "memory_usage": [],
    
    # Anti-patterns → stagnation
    "antipattern": ["evolution_stagnation_detected"],
    "filler_words": ["evolution_stagnation_detected"],
    "verbosity": ["evolution_stagnation_detected"],
    
    # Success signals
    "improvement": ["stable_success_plateau"],
    "score_increase": [],
    "learning_gain": ["stable_success_plateau"],
    
    # Context signals
    "stagnation_detected": ["evolution_stagnation_detected"],
    "drift_detected": ["evolution_stagnation_detected"],
}

# ============================================================
# TIME-OF-DAY CONTEXT: Signals weighted by time
# ============================================================
TIME_CONTEXT_WEIGHTS = {
    # Morning (06-12 UTC): Focus on startup/reliability signals
    "morning": {
        "time_range": (6, 12),
        "boost_signals": ["system_health", "memory_clean", "efficiency"],
        "attenuate_signals": ["performance_gap"],
    },
    # Afternoon (12-18 UTC): Focus on quality/improvement
    "afternoon": {
        "time_range": (12, 18),
        "boost_signals": ["task_success_rate", "accuracy", "response_quality"],
        "attenuate_signals": [],
    },
    # Evening (18-23 UTC): Focus on completion/learning signals
    "evening": {
        "time_range": (18, 23),
        "boost_signals": ["improvement", "learning_gain", "score_increase"],
        "attenuate_signals": ["antipattern", "filler_words"],
    },
    # Night (23-6 UTC): Minimal activity, focus on stability
    "night": {
        "time_range": (23, 6),
        "boost_signals": ["system_health"],
        "attenuate_signals": ["performance_gap", "antipattern", "filler_words"],
    },
}

# ============================================================
# FEEDBACK LOOP: Track signal → evolver result quality
# ============================================================

def load_feedback():
    """Load feedback history."""
    if not FEEDBACK_STORE.exists():
        return {}
    try:
        with open(FEEDBACK_STORE) as f:
            return json.load(f)
    except:
        return {}

def save_feedback(feedback):
    """Save feedback history."""
    FEEDBACK_STORE.parent.mkdir(parents=True, exist_ok=True)
    with open(FEEDBACK_STORE, 'w') as f:
        json.dump(feedback, f, indent=2)

def record_feedback(learning_signal, quality_score):
    """
    Record feedback for a signal.
    quality_score: 0-1, how good was the evolver response to this signal.
    """
    feedback = load_feedback()
    
    if learning_signal not in feedback:
        feedback[learning_signal] = {"scores": [], "count": 0, "avg_score": 0.0}
    
    fb = feedback[learning_signal]
    fb["scores"].append(quality_score)
    fb["count"] += 1
    
    # Keep last 20 scores
    if len(fb["scores"]) > 20:
        fb["scores"] = fb["scores"][-20:]
    
    fb["avg_score"] = sum(fb["scores"]) / len(fb["scores"])
    
    save_feedback(feedback)
    print(f"Recorded feedback for '{learning_signal}': score={quality_score}, avg={fb['avg_score']:.2f}")

def get_signal_quality(learning_signal):
    """Get learned quality score for a signal (0-1)."""
    feedback = load_feedback()
    if learning_signal in feedback:
        return feedback[learning_signal]["avg_score"]
    return 0.5  # Default neutral

def get_high_quality_signals():
    """Get signals that historically produced good evolver results."""
    feedback = load_feedback()
    return [s for s, fb in feedback.items() if fb["avg_score"] >= 0.6]

# ============================================================
# CONTEXT-AWARE SIGNAL PROCESSING
# ============================================================

def get_time_context():
    """Get current time context name."""
    hour = datetime.now().hour
    for ctx_name, ctx in TIME_CONTEXT_WEIGHTS.items():
        start, end = ctx["time_range"]
        if start > end:  # Night spans midnight
            if hour >= start or hour < end:
                return ctx_name
        else:
            if start <= hour < end:
                return ctx_name
    return "night"  # Default

def apply_time_context(signals, time_context):
    """Apply time-based weighting to signals."""
    ctx = TIME_CONTEXT_WEIGHTS[time_context]
    
    # Start with base signals
    processed = []
    for s in signals:
        score = 1.0
        quality = get_signal_quality(s)
        
        # Boost signals for this time context
        if s in ctx["boost_signals"]:
            score *= 1.5
        
        # Attenuate signals for this time context
        if s in ctx["attenuate_signals"]:
            score *= 0.5
        
        # Factor in learned quality
        score *= (0.5 + quality)
        
        processed.append((s, score))
    
    return processed

# ============================================================
# CORE SIGNAL TRANSLATION
# ============================================================

def load_learning_signals():
    """Load signals from Learning Loop."""
    if not LEARNING_SIGNAL.exists():
        return []
    with open(LEARNING_SIGNAL) as f:
        data = json.load(f)
    
    # Support both old format (learnings[].type) and new format (recommendations[].category)
    learnings = data.get('learnings', [])
    if learnings:
        return [l.get('type', '') for l in learnings]
    
    recommendations = data.get('recommendations', [])
    if recommendations:
        signals = []
        for r in recommendations:
            cat = r.get('category', '')
            prio = r.get('priority', '')
            if cat == 'tsr' or prio == 'HIGH':
                signals.append('performance_gap')
            elif cat == 'efficiency':
                signals.append('efficiency')
            elif cat == 'error_rate':
                signals.append('error_rate')
            elif cat == 'antipattern':
                signals.append('antipattern')
            else:
                signals.append(cat or 'system_health')
        return signals
    
    return []

def translate_signal(learning_signal):
    """Translate a single Learning Loop signal to evolver signals."""
    return BASE_SIGNAL_MAP.get(learning_signal, [])

def rank_signals(signal_scores):
    """
    Rank signals by priority and learned quality.
    Returns sorted list of (signal, rank_score).
    """
    ranked = []
    for signal, score in signal_scores:
        priority = SIGNAL_PRIORITY.get(signal, 3)  # Default low priority
        rank_score = score * (1.0 / (priority + 1))  # Lower priority = higher divisor
        ranked.append((signal, rank_score, priority))
    
    # Sort by rank_score descending (higher is better)
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked

def translate_all():
    """Translate all Learning Loop signals with context and ranking."""
    learning_signals = load_learning_signals()
    time_context = get_time_context()
    
    # Apply time context weighting
    weighted = apply_time_context(learning_signals, time_context)
    
    # Collect evolver signals with priority
    evolver_signals = set()
    signal_reasons = {}
    signal_ranks = {}
    
    for ls, ws in weighted:
        translated = translate_signal(ls)
        for t in translated:
            evolver_signals.add(t)
            if t not in signal_reasons:
                signal_reasons[t] = []
                signal_ranks[t] = 0
            signal_reasons[t].append(ls)
            signal_ranks[t] = max(signal_ranks[t], ws)
    
    return list(evolver_signals), signal_reasons, signal_ranks, time_context

def translate_with_ranking():
    """
    Get translated signals with full ranking info.
    Returns: (evolver_signals, ranked_learning_signals, time_context)
    """
    learning_signals = load_learning_signals()
    time_context = get_time_context()
    
    # Apply time context and get scores
    weighted = apply_time_context(learning_signals, time_context)
    
    # Rank them
    ranked = rank_signals(weighted)
    
    # Translate top-ranked to evolver signals
    evolver_signals = set()
    signal_reasons = {}
    
    for ls, rank_score, priority in ranked:
        translated = translate_signal(ls)
        for t in translated:
            evolver_signals.add(t)
            if t not in signal_reasons:
                signal_reasons[t] = []
            signal_reasons[t].append(ls)
    
    return list(evolver_signals), ranked, signal_reasons, time_context

# ============================================================
# EVOLVER EVENT BUILDING & INJECTION
# ============================================================

def build_evolver_event(signals, reasons, time_context="unknown"):
    """Build a MemoryGraphEvent for signal injection."""
    return {
        "type": "MemoryGraphEvent",
        "kind": "signal",
        "id": f"mge_{int(datetime.now().timestamp()*1000)}_signal_bridge",
        "ts": datetime.now().isoformat(),
        "signal": {
            "key": "|".join(signals),
            "signals": signals,
            "error_signature": None,
            "source": "learning_loop_signal_bridge",
            "reasons": reasons,
            "time_context": time_context,
        },
        "observed": {
            "agent": "ceo",
            "session_scope": "signal_bridge",
            "drift_enabled": False,
            "review_mode": False,
            "dry_run": False,
            "system_health": "signal_bridge_integration",
            "mood": "informative",
            "scan_ms": 0,
            "memory_size_bytes": 0,
            "recent_error_count": 0,
            "node": "v22.22.2",
            "platform": "linux",
            "cwd": str(WORKSPACE),
            "evidence": {
                "recent_session_tail": "signal_bridge",
                "today_log_tail": "signal_bridge"
            }
        }
    }

def inject_signals(signals, reasons, time_context="unknown"):
    """Inject translated signals into evolver's memory_graph."""
    if not signals:
        print("No signals to inject (all were non-actionable)")
        return False
    
    event = build_evolver_event(signals, reasons, time_context)
    
    with open(EVOLVER_GRAPH, 'a') as f:
        f.write(json.dumps(event) + '\n')
    
    print(f"Injected {len(signals)} evolver signals: {signals}")
    for s, r in reasons.items():
        print(f"  {s} (from: {r})")
    
    return True

# ============================================================
# MAIN CLI
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Signal Bridge — Learning Loop → Evolver")
    parser.add_argument('--translate', action='store_true', help='Show translated signals')
    parser.add_argument('--inject', action='store_true', help='Inject signals into evolver')
    parser.add_argument('--feedback', nargs=2, metavar=('SIGNAL', 'SCORE'),
                        help='Record feedback for a signal (0-1 score)')
    parser.add_argument('--stats', action='store_true', help='Show feedback stats')
    parser.add_argument('--ranking', action='store_true', help='Show ranked signal list')
    args = parser.parse_args()
    
    print("=== SIGNAL BRIDGE v2 ===")
    
    # Handle feedback mode
    if args.feedback:
        signal_name, score_str = args.feedback
        try:
            score = float(score_str)
            score = max(0.0, min(1.0, score))  # Clamp to 0-1
            record_feedback(signal_name, score)
            return
        except ValueError:
            print(f"Invalid score: {score_str} (use 0-1)")
            return
    
    # Handle stats mode
    if args.stats:
        feedback = load_feedback()
        if not feedback:
            print("No feedback recorded yet.")
        else:
            print("\nSignal Feedback History:")
            for signal, fb in sorted(feedback.items(), key=lambda x: x[1]['avg_score'], reverse=True):
                bar = "█" * int(fb['avg_score'] * 10) + "░" * (10 - int(fb['avg_score'] * 10))
                print(f"  {signal:30s} {bar} {fb['avg_score']:.2f} (n={fb['count']})")
            print(f"\nHigh-quality signals (avg >= 0.6): {get_high_quality_signals()}")
        return
    
    # Load and translate
    learning_signals = load_learning_signals()
    time_context = get_time_context()
    print(f"Time context: {time_context}")
    print(f"Learning Loop signals: {learning_signals}")
    
    evolver_signals, reasons, ranks, ctx = translate_all()
    print(f"\nEvolver signals: {evolver_signals}")
    
    if args.translate or args.ranking:
        evolver_signals, ranked_signals, reasons, ctx = translate_with_ranking()
        print(f"\nContext: {ctx}")
        print("\nRanked Learning Loop signals:")
        for i, (s, score, priority) in enumerate(ranked_signals):
            p_label = ["CRIT", "HIGH", "MED", "LOW"][priority]
            q = get_signal_quality(s)
            print(f"  {i+1}. [{p_label}] {s:25s} score={score:.3f} quality={q:.2f}")
    
    if args.translate:
        print("\nTranslation map:")
        for s, r in reasons.items():
            print(f"  {s} ← {r}")
    
    if args.inject:
        success = inject_signals(evolver_signals, reasons, ctx)
        if success:
            print("\n✅ Signals injected into evolver memory_graph")
        else:
            print("\n⚠️ No signals to inject")

if __name__ == '__main__':
    main()
