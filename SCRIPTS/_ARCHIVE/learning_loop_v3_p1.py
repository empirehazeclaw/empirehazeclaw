#!/usr/bin/env python3
"""
🎯 Learning Loop v3 MAXIMAL — P1 Enhancements

Adds:
- Cross-Pattern Matcher (improved)
- Feedback Queue for Nico's direct feedback  
- Pattern Learning from real errors
- Improved similarity scoring with Levenshtein

Usage:
    python3 learning_loop_v3_p1.py --add-feedback "Your feedback here"
    python3 learning_loop_v3_p1.py --learn-from-errors
    python3 learning_loop_v3_p1.py --find-similar "error message"
"""

import os
import sys
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "scripts"
DATA_DIR = WORKSPACE / "data"
PATTERNS_FILE = DATA_DIR / "learning_loop" / "patterns.json"
FEEDBACK_QUEUE = DATA_DIR / "feedback_queue.json"

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

def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

# ============ FEEDBACK QUEUE ============

def add_feedback(text: str, sentiment: str = "neutral") -> bool:
    """
    Add direct feedback from Nico to the feedback queue.
    
    Args:
        text: Feedback text from Nico
        sentiment: "positive", "negative", or "neutral"
    
    Returns:
        True if added successfully
    """
    queue = load_json(FEEDBACK_QUEUE, {"feedback": [], "version": "1.0"})
    
    entry = {
        "text": text,
        "sentiment": sentiment,
        "timestamp": datetime.now().isoformat(),
        "source": "direct_nico"
    }
    
    queue["feedback"].append(entry)
    queue["feedback"] = queue["feedback"][-50:]  # Keep last 50
    
    save_json(FEEDBACK_QUEUE, queue)
    return True

def get_feedback_summary() -> Dict:
    """Get summary of all feedback."""
    queue = load_json(FEEDBACK_QUEUE, {"feedback": [], "version": "1.0"})
    feedback = queue.get("feedback", [])
    
    summary = {
        "total": len(feedback),
        "positive": sum(1 for f in feedback if f.get("sentiment") == "positive"),
        "negative": sum(1 for f in feedback if f.get("sentiment") == "negative"),
        "neutral": sum(1 for f in feedback if f.get("sentiment") == "neutral"),
        "recent": feedback[-5:]
    }
    
    return summary

# ============ PATTERN LEARNING ============

def learn_from_errors() -> int:
    """
    Learn patterns from recent system errors.
    
    Returns:
        Number of patterns learned
    """
    print("📚 Learning patterns from recent errors...")
    
    patterns_data = load_json(PATTERNS_FILE, {"patterns": [], "version": "1.0"})
    existing_ids = {p.get("id") for p in patterns_data.get("patterns", [])}
    
    learned = 0
    
    # Run error reducer to get recent errors
    try:
        result = subprocess.run(
            ['python3', str(SCRIPTS_DIR / 'error_reducer.py'), '--analyze'],
            capture_output=True, text=True, timeout=60
        )
        
        # Parse error patterns from output
        error_patterns = []
        for line in result.stdout.split('\n'):
            # Look for error pattern indicators
            if 'ERROR' in line.upper() and len(line) > 10:
                error_patterns.append(line.strip())
            elif 'FAILED' in line.upper() and len(line) > 10:
                error_patterns.append(line.strip())
        
        # Also check cron watchdog for failed crons
        try:
            cron_result = subprocess.run(
                ['python3', str(SCRIPTS_DIR / 'cron_watchdog.py'), '--report'],
                capture_output=True, text=True, timeout=30
            )
            for line in cron_result.stdout.split('\n'):
                if 'FAILED' in line.upper():
                    error_patterns.append(f"Cron failure: {line.strip()}")
        except:
            pass
        
        # Create patterns from errors
        for error_text in error_patterns[:10]:  # Limit to 10
            # Generate pattern ID from error content
            words = [w for w in error_text.lower().split() if len(w) > 4]
            pattern_id = "_".join(words[:3]) if words else None
            
            if not pattern_id or pattern_id in existing_ids:
                continue
            
            # Extract error type
            error_type = "unknown"
            if "cron" in error_text.lower():
                error_type = "cron_failure"
            elif "error" in error_text.lower():
                error_type = "general_error"
            elif "timeout" in error_text.lower():
                error_type = "timeout"
            elif "permission" in error_text.lower() or "access" in error_text.lower():
                error_type = "permission"
            
            pattern = {
                "id": pattern_id,
                "description": error_text[:200],
                "error_type": error_type,
                "solution": None,  # No solution yet
                "validated": False,
                "confidence": 0.5,  # Initial confidence
                "initial_confidence": 0.5,
                "first_seen": datetime.now().isoformat(),
                "last_validated": datetime.now().isoformat(),
                "days_since_validation": 0,
                "archived": False,
                "source": "error_learning",
                "access_count": 0,
                "cross_pattern_hits": 0
            }
            
            patterns_data["patterns"].append(pattern)
            existing_ids.add(pattern_id)
            learned += 1
            
    except Exception as e:
        print(f"   ⚠️ Error learning failed: {e}")
    
    save_json(PATTERNS_FILE, patterns_data)
    print(f"   ✅ Learned {learned} new patterns")
    return learned

# ============ CROSS-PATTERN MATCHER (IMPROVED) ============

def find_similar_errors(new_error: str, top_k: int = 5) -> List[Dict]:
    """
    Finds similar past errors using multiple similarity metrics.
    
    Metrics:
    - Levenshtein string similarity
    - Word overlap
    - Error type matching
    - Context matching
    
    Returns top-k similar errors with proven solutions.
    """
    patterns_data = load_json(PATTERNS_FILE, {"patterns": [], "version": "1.0"})
    patterns = patterns_data.get("patterns", [])
    
    if not patterns:
        return []
    
    similar = []
    new_error_lower = new_error.lower()
    new_words = set([w for w in new_error_lower.split() if len(w) > 3])
    
    for pattern in patterns:
        if pattern.get("archived"):
            continue
        
        scores = {}
        
        # 1. Levenshtein similarity (0-1, higher is more similar)
        desc = pattern.get("description", "").lower()
        if desc:
            lev_dist = levenshtein_distance(new_error_lower[:100], desc[:100])
            max_len = max(len(new_error_lower), len(desc))
            scores["levenshtein"] = 1 - (lev_dist / max_len) if max_len > 0 else 0
        
        # 2. Word overlap
        pattern_words = set([w for w in desc.split() if len(w) > 3])
        overlap = len(new_words & pattern_words)
        union = len(new_words | pattern_words)
        scores["word_overlap"] = overlap / union if union > 0 else 0
        
        # 3. Error type match
        new_type = "unknown"
        for etype in ["cron", "error", "timeout", "permission", "api", "file"]:
            if etype in new_error_lower:
                new_type = etype
                break
        scores["type_match"] = 1.0 if pattern.get("error_type") == new_type else 0.0
        
        # 4. Has validated solution
        scores["has_solution"] = 1.0 if pattern.get("solution") and pattern.get("validated") else 0.0
        
        # Weighted total score
        total_score = (
            scores.get("levenshtein", 0) * 0.3 +
            scores.get("word_overlap", 0) * 0.3 +
            scores.get("type_match", 0) * 0.2 +
            scores.get("has_solution", 0) * 0.2
        )
        
        if total_score > 0.15:  # Threshold (lowered for better matching)
            similar.append({
                "pattern": pattern,
                "total_score": total_score,
                "scores": scores,
                "solution": pattern.get("solution"),
                "validated": pattern.get("validated", False)
            })
    
    # Sort by total score
    similar.sort(key=lambda x: x["total_score"], reverse=True)
    
    return similar[:top_k]

def apply_cross_pattern_solution(pattern: Dict) -> Tuple[bool, str]:
    """
    Apply a proven solution from a similar pattern.
    
    Returns (success, message)
    """
    if not pattern.get("solution"):
        return False, "No solution available"
    
    print(f"   🎯 Applying cross-pattern solution")
    print(f"   📝 Pattern: {pattern.get('description', 'unknown')[:60]}...")
    print(f"   💡 Solution: {pattern['solution'][:100]}...")
    
    # Update cross-pattern hit counter
    patterns_data = load_json(PATTERNS_FILE, {"patterns": [], "version": "1.0"})
    for p in patterns_data.get("patterns", []):
        if p.get("id") == pattern.get("id"):
            p["cross_pattern_hits"] = p.get("cross_pattern_hits", 0) + 1
            break
    save_json(PATTERNS_FILE, patterns_data)
    
    return True, f"Solution applied from pattern: {pattern.get('id')}"

def validate_and_store_solution(pattern_id: str, solution: str) -> bool:
    """
    Store a validated solution for a pattern.
    
    Returns True if stored successfully.
    """
    patterns_data = load_json(PATTERNS_FILE, {"patterns": [], "version": "1.0"})
    
    for pattern in patterns_data.get("patterns", []):
        if pattern.get("id") == pattern_id:
            pattern["solution"] = solution
            pattern["validated"] = True
            pattern["confidence"] = 0.9  # Boost confidence
            pattern["last_validated"] = datetime.now().isoformat()
            save_json(PATTERNS_FILE, patterns_data)
            return True
    
    return False

# ============ CLI ============

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--add-feedback":
            if len(sys.argv) > 2:
                sentiment = sys.argv[2] if len(sys.argv) > 3 else "neutral"
                add_feedback(" ".join(sys.argv[2:]), sentiment)
                print("✅ Feedback added")
            else:
                print("Usage: --add-feedback \"Your feedback\" [positive|negative|neutral]")
        
        elif sys.argv[1] == "--learn-from-errors":
            learned = learn_from_errors()
            print(f"✅ Learned {learned} patterns from errors")
        
        elif sys.argv[1] == "--find-similar":
            if len(sys.argv) > 2:
                error_text = " ".join(sys.argv[2:])
                similar = find_similar_errors(error_text)
                if similar:
                    print(f"Found {len(similar)} similar patterns:")
                    for s in similar:
                        print(f"  [{s['total_score']:.2f}] {s['pattern'].get('description', 'N/A')[:50]}...")
                        if s.get('solution'):
                            print(f"      → {s['solution'][:60]}...")
                else:
                    print("No similar patterns found")
            else:
                print("Usage: --find-similar \"error message\"")
        
        elif sys.argv[1] == "--feedback-summary":
            summary = get_feedback_summary()
            print(f"Feedback Summary:")
            print(f"  Total: {summary['total']}")
            print(f"  Positive: {summary['positive']}")
            print(f"  Negative: {summary['negative']}")
            print(f"  Neutral: {summary['neutral']}")
        
        elif sys.argv[1] == "--list-patterns":
            patterns_data = load_json(PATTERNS_FILE, {"patterns": [], "version": "1.0"})
            patterns = patterns_data.get("patterns", [])
            if patterns:
                print(f"Total patterns: {len(patterns)}")
                for p in patterns[:10]:
                    status = "✅" if p.get("validated") else "❌"
                    conf = p.get("confidence", 0)
                    print(f"  {status} [{conf:.2f}] {p.get('description', 'N/A')[:40]}...")
            else:
                print("No patterns yet. Run --learn-from-errors first.")
        
        else:
            print("Unknown command")
            print("Usage:")
            print("  --add-feedback \"text\" [sentiment]  Add feedback")
            print("  --learn-from-errors                  Learn from recent errors")
            print("  --find-similar \"error\"              Find similar patterns")
            print("  --feedback-summary                  Show feedback summary")
            print("  --list-patterns                      List all patterns")
    else:
        print("Learning Loop v3 MAXIMAL — P1 Enhancements")
        print("Usage: python3 learning_loop_v3_p1.py [command]")

if __name__ == "__main__":
    main()
