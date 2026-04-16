#!/usr/bin/env python3
"""
REM Feedback Integrator
Runs OpenClaw REM harness and integrates results into the Learning Loop.

Usage:
    python3 rem_feedback.py              # Run REM harness and add to feedback
    python3 rem_feedback.py --dry-run   # Preview only
"""

import json
import subprocess
import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
KG_PATH = WORKSPACE / "ceo/memory/kg" / "knowledge_graph.json"
FEEDBACK_LOG = WORKSPACE / "logs" / "learning_feedback.json"
REM_LOG = WORKSPACE / "logs" / "rem_harness.json"

def log(msg: str, level: str = "INFO"):
    """Log REM activity."""
    print(f"[REM] {msg}")

def run_rem_harness() -> Tuple[str, bool]:
    """Run openclaw memory rem-harness and capture output."""
    try:
        result = subprocess.run(
            ["openclaw", "memory", "rem-harness", "--agent", "ceo", "--json"],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            return result.stdout, True
        else:
            return result.stderr, False
    except Exception as e:
        return str(e), False

def parse_rem_output(output: str) -> Dict:
    """Parse REM harness output for insights."""
    insights = {
        "themes": [],
        "lasting_truths": [],
        "deep_candidates": [],
        "timestamp": datetime.now().isoformat() + "Z"
    }
    
    # Parse themes (simple pattern matching)
    theme_pattern = r"- Theme: `(.+?)` kept surfacing across (\d+) memories"
    for match in re.finditer(theme_pattern, output):
        theme, count = match.groups()
        insights["themes"].append({
            "theme": theme,
            "recall_count": int(count),
            "source": "rem_harness"
        })
    
    # Parse lasting truths with confidence
    truth_pattern = r"\[confidence=([\d.]+)\s+evidence=(.+?)\]"
    for match in re.finditer(truth_pattern, output):
        confidence = float(match.group(1))
        evidence = match.group(2).strip()
        insights["lasting_truths"].append({
            "confidence": confidence,
            "evidence": evidence,
            "source": "rem_harness"
        })
    
    # Parse deep candidates
    candidate_pattern = r"^(\d+\.\d+)\s+(.+?)$"
    for line in output.split("\n"):
        match = re.match(candidate_pattern, line.strip())
        if match:
            score, description = match.groups()
            insights["deep_candidates"].append({
                "score": float(score),
                "description": description.strip()[:200],  # Truncate
                "source": "rem_harness"
            })
    
    return insights

def add_rem_as_feedback(insights: Dict, dry_run: bool = False) -> int:
    """Add REM insights as feedback to the learning system."""
    feedback_count = 0
    
    if dry_run:
        log("DRY RUN - Would add:")
        for theme in insights["themes"][:3]:
            log(f"  Theme: {theme['theme']} ({theme['recall_count']} recalls)")
        for truth in insights["lasting_truths"][:3]:
            log(f"  Truth: confidence={truth['confidence']}, evidence={truth['evidence'][:80]}")
        return 0
    
    # Add themes as general feedback
    for theme in insights["themes"][:3]:
        feedback = f"REM Theme: '{theme['theme']}' surfaced {theme['recall_count']} times"
        _add_feedback_entry(feedback, theme["recall_count"] / 1000.0)  # Normalize to ~1.0
        feedback_count += 1
    
    # Add lasting truths as high-confidence feedback
    for truth in insights["lasting_truths"][:5]:
        if truth["confidence"] >= 0.5:
            feedback = f"REM Truth (conf={truth['confidence']}): {truth['evidence'][:150]}"
            _add_feedback_entry(feedback, truth["confidence"])
            feedback_count += 1
    
    # Add deep candidates as actionable insights
    for candidate in insights["deep_candidates"][:3]:
        if candidate["score"] >= 0.5:
            feedback = f"REM Candidate (score={candidate['score']}): {candidate['description']}"
            _add_feedback_entry(feedback, candidate["score"])
            feedback_count += 1
    
    return feedback_count

def _add_feedback_entry(feedback: str, quality: float):
    """Add a single feedback entry."""
    quality = max(1.0, min(5.0, quality * 5))  # Scale 0-1 to 1-5
    
    entry = {
        "timestamp": datetime.now().isoformat() + "Z",
        "source": "rem_harness",
        "feedback": feedback,
        "quality": round(quality, 1),
        "processed": False
    }
    
    FEEDBACK_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(FEEDBACK_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")

def update_kg(insights: Dict, dry_run: bool = False):
    """Update Knowledge Graph with REM insights."""
    if not KG_PATH.exists():
        log("KG not found, skipping", "WARN")
        return
    
    try:
        with open(KG_PATH) as f:
            kg = json.load(f)
        
        # Add REM insights as entities
        for theme in insights["themes"][:5]:
            entity_name = f"rem_theme_{theme['theme'].replace(' ', '_')[:30]}"
            kg["entities"][entity_name] = {
                "type": "rem_insight",
                "category": "theme_pattern",
                "facts": [{
                    "content": f"Theme '{theme['theme']}' recalled {theme['recall_count']} times",
                    "confidence": 1.0,
                    "extracted_at": datetime.now().isoformat() + "Z",
                    "source": "rem_harness"
                }],
                "priority": "MEDIUM",
                "created": datetime.now().isoformat() + "Z",
                "last_accessed": datetime.now().isoformat() + "Z",
                "access_count": 1,
                "decay_score": 1.0
            }
        
        if not dry_run:
            with open(KG_PATH, "w") as f:
                json.dump(kg, f, indent=2)
            log(f"Updated KG with {len(insights['themes'])} themes")
        else:
            log(f"DRY RUN - Would update KG with {len(insights['themes'])} themes")
            
    except Exception as e:
        log(f"KG update failed: {e}", "ERROR")

def main():
    parser = argparse.ArgumentParser(description="REM Feedback Integrator")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--no-kg", action="store_true", help="Skip KG update")
    args = parser.parse_args()
    
    log("Starting REM Feedback Integration")
    
    # Run REM harness
    log("Running: openclaw memory rem-harness --agent ceo")
    output, success = run_rem_harness()
    
    if not success:
        log(f"REM harness failed: {output}", "ERROR")
        # Try non-JSON fallback
        log("Retrying without --json...")
        try:
            result = subprocess.run(
                ["openclaw", "memory", "rem-harness", "--agent", "ceo"],
                capture_output=True, text=True, timeout=120
            )
            output = result.stdout + result.stderr
            success = result.returncode == 0
        except Exception as e:
            output = str(e)
    
    if not success:
        log(f"REM harness failed again: {output}", "ERROR")
        return 1
    
    # Parse output
    log("Parsing REM output...")
    insights = parse_rem_output(output)
    log(f"Found: {len(insights['themes'])} themes, {len(insights['lasting_truths'])} truths, {len(insights['deep_candidates'])} candidates")
    
    # Add as feedback
    feedback_count = add_rem_as_feedback(insights, args.dry_run)
    log(f"Added {feedback_count} feedback entries")
    
    # Update KG
    if not args.no_kg:
        update_kg(insights, args.dry_run)
    
    log("REM Feedback Integration complete!")
    return 0

if __name__ == "__main__":
    exit(main())
