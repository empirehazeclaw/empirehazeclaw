#!/usr/bin/env python3
"""
Learning Loop Feedback Integrator
Integrates Nico's direct feedback into the learning system.

Usage:
    python3 learning_feedback.py --feedback "that was good" --quality 5
    python3 learning_feedback.py --feedback "that was wrong" --quality 1
"""

import json
import argparse
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
KG_PATH = WORKSPACE / "core_ultralight" / "memory" / "knowledge_graph.json"
FEEDBACK_LOG = WORKSPACE / "logs" / "learning_feedback.json"

def add_feedback(feedback: str, quality: int):
    """Add feedback to the learning system."""
    FEEDBACK_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "timestamp": datetime.now().isoformat() + "Z",
        "feedback": feedback,
        "quality": quality,  # 1-5 scale
        "processed": False
    }
    
    with open(FEEDBACK_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    # Also add to KG if high quality
    if quality >= 4 and KG_PATH.exists():
        try:
            with open(KG_PATH) as f:
                kg = json.load(f)
            
            entity_name = f"feedback_positive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            kg["entities"][entity_name] = {
                "type": "learning_feedback",
                "category": "nico_feedback",
                "facts": [{
                    "content": feedback,
                    "confidence": quality / 5,
                    "extracted_at": datetime.now().isoformat() + "Z",
                    "category": "quality_feedback"
                }],
                "priority": "HIGH" if quality >= 5 else "MEDIUM",
                "created": datetime.now().isoformat() + "Z",
                "last_accessed": datetime.now().isoformat() + "Z",
                "access_count": 1,
                "decay_score": 1.0
            }
            
            with open(KG_PATH, "w") as f:
                json.dump(kg, f, indent=2)
            
            print(f"Added to KG: {entity_name}")
        except Exception as e:
            print(f"KG update failed: {e}")
    
    print(f"Feedback logged: quality={quality}")
    return entry

def process_feedback():
    """Process accumulated feedback for learning."""
    if not FEEDBACK_LOG.exists():
        return {"processed": 0, "entries": []}
    
    entries = []
    with open(FEEDBACK_LOG) as f:
        for line in f:
            try:
                entries.append(json.loads(line))
            except:
                continue
    
    unprocessed = [e for e in entries if not e.get("processed")]
    
    # Update analyzer weights based on feedback
    if unprocessed:
        state_file = WORKSPACE / "data" / "learning_loop_state.json"
        state = {}
        if state_file.exists():
            try:
                state = json.load(open(state_file))
            except:
                state = {}
        
        avg_quality = sum(e.get("quality", 3) for e in unprocessed) / len(unprocessed)
        
        if "feedback_stats" not in state:
            state["feedback_stats"] = {"count": 0, "avg_quality": 0}
        
        state["feedback_stats"]["count"] += len(unprocessed)
        state["feedback_stats"]["avg_quality"] = avg_quality
        state["feedback_stats"]["last_update"] = datetime.now().isoformat() + "Z"
        
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)
        
        # Mark as processed
        for e in unprocessed:
            e["processed"] = True
        
        with open(FEEDBACK_LOG, "w") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")
        
        print(f"Processed {len(unprocessed)} feedback entries, avg quality: {avg_quality:.1f}")
    
    return {"processed": len(unprocessed), "entries": unprocessed}

class LearningFeedback:
    """Integrates external feedback into the learning loop."""
    
    def __init__(self):
        self.feedback_log = FEEDBACK_LOG
        self.kg_path = KG_PATH
    
    def add(self, feedback: str, quality: int) -> str:
        """Add feedback to the system."""
        return add_feedback(feedback, quality)
    
    def process(self) -> dict:
        """Process accumulated feedback."""
        return process_feedback()
    
    def integrate(self, reflexion_score: float) -> dict:
        """Integrate feedback with reflexion score for meta-learning."""
        result = {"adjustments": []}
        
        if not self.feedback_log.exists():
            return result
        
        # Read recent feedback
        recent = []
        if self.feedback_log.exists():
            with open(self.feedback_log) as f:
                for line in f:
                    try:
                        recent.append(json.loads(line))
                    except:
                        continue
        
        # Filter recent (last hour)
        cutoff = datetime.now().timestamp() - 3600
        recent = [e for e in recent if datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00")).timestamp() > cutoff]
        
        if not recent:
            return result
        
        avg_quality = sum(e.get("quality", 3) for e in recent) / len(recent)
        
        # Adjust meta-learning based on feedback quality
        if avg_quality < 3:
            # Low quality feedback - be more conservative
            result["adjustments"].append({"type": "conservative", "reason": "low_feedback_quality"})
        elif avg_quality >= 5:
            # High quality feedback - be more aggressive
            result["adjustments"].append({"type": "aggressive", "reason": "high_feedback_quality"})
        
        result["feedback_count"] = len(recent)
        result["avg_quality"] = avg_quality
        
        return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--feedback", type=str, help="Feedback text")
    parser.add_argument("--quality", type=int, default=3, help="Quality 1-5")
    parser.add_argument("--process", action="store_true", help="Process accumulated feedback")
    args = parser.parse_args()
    
    if args.process:
        result = process_feedback()
        print(f"Processed: {result['processed']}")
    elif args.feedback:
        add_feedback(args.feedback, args.quality)
    else:
        parser.print_help()