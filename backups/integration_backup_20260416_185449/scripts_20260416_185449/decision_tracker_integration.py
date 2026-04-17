#!/usr/bin/env python3
"""
Decision Tracker Integration for Learning Loop v3

Lightweight decision tracking that integrates with learning_loop_v3.py
to capture key decisions and outcomes for self-improvement analysis.

Usage:
    from decision_tracker_integration import track_decision, track_outcome
    
    # Track a decision
    track_decision(
        context="improvement_selection",
        decision="Cross-pattern match selected over new hypothesis",
        confidence=0.75,
        metadata={"similarity_score": 0.82}
    )
    
    # Track an outcome
    track_outcome(
        context="improvement_selection",
        outcome="validated",
        quality=0.85,
        metadata={"iteration": 42}
    )
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = WORKSPACE / "DATA" / "self_improvement"
DECISIONS_DIR = DATA_DIR / "decisions"
LEARNINGS_FILE = DATA_DIR / "learnings" / "learnings.json"

# Ensure directories exist
DECISIONS_DIR.mkdir(parents=True, exist_ok=True)
LEARNINGS_FILE.parent.mkdir(parents=True, exist_ok=True)


def _load_decisions() -> List[Dict]:
    """Load all recent decisions."""
    if not DECISIONS_DIR.exists():
        return []
    files = sorted(DECISIONS_DIR.glob("dec_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    decisions = []
    for f in files[:100]:
        with open(f, 'r') as fp:
            decisions.append(json.load(fp))
    return decisions


def _save_decision(record: Dict) -> str:
    """Save a decision to disk."""
    decision_id = record.get("id", f"dec_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    filepath = DECISIONS_DIR / f"{decision_id}.json"
    with open(filepath, 'w') as f:
        json.dump(record, f, indent=2)
    return decision_id


def _update_learnings(pattern: Optional[Dict] = None, warning: Optional[Dict] = None):
    """Update learnings store with pattern or warning."""
    if not LEARNINGS_FILE.exists():
        with open(LEARNINGS_FILE, 'w') as f:
            json.dump({"patterns": [], "warnings": [], "improvements": [], "metadata": {"created": datetime.now().isoformat()}}, f)
    
    with open(LEARNINGS_FILE, 'r') as f:
        data = json.load(f)
    
    if pattern:
        pattern.update({
            "id": f"pattern_{len(data['patterns']) + 1}",
            "stored_at": datetime.now().isoformat()
        })
        data["patterns"].append(pattern)
        print(f"   📝 Stored pattern: {pattern.get('name', 'unnamed')[:50]}")
    
    if warning:
        warning.update({
            "id": f"warning_{len(data['warnings']) + 1}",
            "stored_at": datetime.now().isoformat()
        })
        data["warnings"].append(warning)
        print(f"   ⚠️ Stored warning: {warning.get('pattern', 'unnamed')[:50]}")
    
    with open(LEARNINGS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def track_decision(
    context: str,
    decision: str,
    confidence: float,
    reasoning: str = "",
    alternatives: List[str] = None,
    metadata: Dict = None
) -> str:
    """
    Track a decision with context and confidence.
    
    Args:
        context: Where in the system this decision happened
        decision: What was decided
        confidence: How confident (0.0-1.0)
        reasoning: Why this decision was made
        alternatives: What other options were considered
        metadata: Additional context data
    
    Returns:
        Decision ID for tracking outcomes
    """
    decisions = _load_decisions()
    decision_id = f"dec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(decisions)}"
    
    record = {
        "id": decision_id,
        "context": context,
        "decision": decision,
        "confidence": confidence,
        "reasoning": reasoning,
        "alternatives": alternatives or [],
        "metadata": metadata or {},
        "recorded_at": datetime.now().isoformat(),
        "outcome": None,
        "outcome_quality": None
    }
    
    _save_decision(record)
    print(f"   📊 Decision tracked: [{context}] {decision[:60]}... (conf: {confidence})")
    
    return decision_id


def track_outcome(
    decision_id: str,
    outcome: str,
    quality: float,
    metadata: Dict = None
) -> bool:
    """
    Record the outcome of a tracked decision.
    
    Args:
        decision_id: ID returned from track_decision
        outcome: What happened (validated, failed, improved, etc.)
        quality: Quality score (0.0-1.0)
        metadata: Additional result data
    
    Returns:
        True if recorded successfully
    """
    filepath = DECISIONS_DIR / f"{decision_id}.json"
    
    if not filepath.exists():
        print(f"   ❌ Decision not found: {decision_id}")
        return False
    
    with open(filepath, 'r') as f:
        record = json.load(f)
    
    record["outcome"] = outcome
    record["outcome_quality"] = quality
    record["outcome_recorded_at"] = datetime.now().isoformat()
    record["metadata"].update(metadata or {})
    
    with open(filepath, 'w') as f:
        json.dump(record, f, indent=2)
    
    print(f"   ✅ Outcome recorded: {decision_id} → {outcome} (quality: {quality})")
    
    # Auto-update learnings
    if quality >= 0.7:
        _update_learnings(pattern={
            "name": f"decision_{decision_id}",
            "context": record.get("context"),
            "decision": record.get("decision"),
            "description": f"Quality {quality}: {outcome}",
            "success_count": 1
        })
    elif quality < 0.3:
        _update_learnings(warning={
            "pattern": f"decision_{decision_id}",
            "context": record.get("context"),
            "description": f"Failed with quality {quality}: {outcome}"
        })
    
    return True


def track_improvement_selection(
    selection_type: str,  # "cross_pattern" or "hypothesis" or "forced_novelty"
    improvement_title: str,
    confidence: float,
    alternatives_count: int = 0,
    similarity_score: float = None,
    metadata: Dict = None
) -> str:
    """Track improvement selection decision."""
    return track_decision(
        context="improvement_selection",
        decision=f"{selection_type}: {improvement_title[:60]}",
        confidence=confidence,
        reasoning=f"Selected from {alternatives_count} alternatives",
        metadata={
            "selection_type": selection_type,
            "similarity_score": similarity_score,
            **(metadata or {})
        }
    )


def track_validation_result(
    improvement_title: str,
    validated: bool,
    quality: float,
    tests_passed: int,
    tests_total: int,
    metadata: Dict = None
) -> str:
    """Track validation result decision."""
    decision_id = track_decision(
        context="validation",
        decision=f"{'VALIDATED' if validated else 'REJECTED'}: {improvement_title[:60]}",
        confidence=quality,
        reasoning=f"{tests_passed}/{tests_total} tests passed",
        metadata={
            "validated": validated,
            "tests_passed": tests_passed,
            "tests_total": tests_total,
            **(metadata or {})
        }
    )
    
    # Record outcome immediately since we know the result
    track_outcome(
        decision_id=decision_id,
        outcome="validated" if validated else "rejected",
        quality=quality,
        metadata={"tests": f"{tests_passed}/{tests_total}"}
    )
    
    return decision_id


def track_score_change(
    old_score: float,
    new_score: float,
    reason: str,
    metadata: Dict = None
) -> str:
    """Track score changes."""
    confidence = min(0.95, abs(new_score - old_score) * 5 + 0.5)  # Larger changes = higher confidence
    
    return track_decision(
        context="score_update",
        decision=f"Score {old_score:.3f} → {new_score:.3f}",
        confidence=confidence,
        reasoning=reason,
        metadata={
            "old_score": old_score,
            "new_score": new_score,
            "delta": new_score - old_score,
            **(metadata or {})
        }
    )


def get_decision_stats() -> Dict:
    """Get statistics about tracked decisions."""
    decisions = _load_decisions()
    decisions_with_outcome = [d for d in decisions if d.get("outcome") is not None]
    
    if not decisions_with_outcome:
        return {"total_decisions": 0, "calibration_score": 0.0, "sample_size": 0}
    
    total_error = sum(abs(d.get("confidence", 0.5) - d.get("outcome_quality", 0)) for d in decisions_with_outcome)
    avg_error = total_error / len(decisions_with_outcome)
    calibration_score = max(0.0, 1.0 - (avg_error * 2))
    
    good_outcomes = [d for d in decisions_with_outcome if d.get("outcome_quality", 0) >= 0.6]
    
    return {
        "total_decisions": len(decisions),
        "decisions_with_outcome": len(decisions_with_outcome),
        "calibration_score": calibration_score,
        "accuracy": len(good_outcomes) / len(decisions_with_outcome) if decisions_with_outcome else 0.0,
        "avg_confidence": sum(d.get("confidence", 0) for d in decisions_with_outcome) / len(decisions_with_outcome),
        "avg_quality": sum(d.get("outcome_quality", 0) for d in decisions_with_outcome) / len(decisions_with_outcome)
    }


if __name__ == "__main__":
    # Test if called directly
    import sys
    
    print("=== Decision Tracker Integration Test ===")
    
    # Test track_decision
    dec_id = track_decision(
        context="test",
        decision="Testing the decision tracker",
        confidence=0.8,
        reasoning="Verifying integration works"
    )
    print(f"Decision ID: {dec_id}")
    
    # Test track_outcome
    track_outcome(dec_id, "success", 0.9)
    
    # Test stats
    stats = get_decision_stats()
    print(f"\nStats: {stats}")
    
    print("\n✅ Decision tracker integration working!")
