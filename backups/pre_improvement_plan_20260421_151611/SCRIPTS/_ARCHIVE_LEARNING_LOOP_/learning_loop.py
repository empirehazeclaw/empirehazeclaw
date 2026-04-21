#!/usr/bin/env python3
"""
Sir HazeClaw Learning Loop — Main Loop
The loop that learns from the system, improves the system, and improves itself.

Usage:
    python3 learning_loop.py              # Run full loop
    python3 learning_loop.py --collect     # Collect only
    python3 learning_loop.py --analyze     # Analyze only  
    python3 learning_loop.py --execute     # Execute only
    python3 learning_loop.py --reflexion   # Reflexion only
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
KG_PATH = WORKSPACE / "ceo/memory/kg" / "knowledge_graph.json"
LEARNING_LOG = WORKSPACE / "logs" / "learning_loop.json"
STATE_FILE = WORKSPACE / "data" / "learning_loop_state.json"

def log(msg: str, level: str = "INFO"):
    """Log learning activity."""
    LEARNING_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "level": level,
        "message": msg
    }
    with open(LEARNING_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")

def load_state() -> Dict:
    """Load learning loop state."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "iterations": 0,
        "learnings_applied": 0,
        "patterns_discovered": 0,
        "last_reflexion_score": 0,
        "improvements_made": []
    }

def save_state(state: Dict):
    """Save learning loop state."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

# Import subsystems
try:
    from learning_analyzer import LearningAnalyzer
    from learning_executor import LearningExecutor
    ANALYZER_AVAILABLE = True
except ImportError:
    ANALYZER_AVAILABLE = False
    log("learning_analyzer.py not found", "WARN")

try:
    from learning_collector import LearningCollector
    COLLECTOR_AVAILABLE = True
except ImportError:
    COLLECTOR_AVAILABLE = False
    log("learning_collector.py not found", "WARN")

try:
    from learning_feedback import LearningFeedback
    FEEDBACK_AVAILABLE = True
except ImportError:
    FEEDBACK_AVAILABLE = False
    log("learning_feedback.py not found", "WARN")

class LearningLoop:
    """
    The main learning loop that:
    1. Collects experiences from the system
    2. Analyzes patterns
    3. Executes improvements
    4. Reflexions on what worked
    5. Integrates feedback (Nico and external)
    
    The loop improves ITSELF over time (meta-learning).
    """
    
    def __init__(self):
        self.state = load_state()
        self.collector = LearningCollector() if COLLECTOR_AVAILABLE else None
        self.analyzer = LearningAnalyzer() if ANALYZER_AVAILABLE else None
        self.executor = LearningExecutor() if ANALYZER_AVAILABLE else None
        self.feedback = LearningFeedback() if FEEDBACK_AVAILABLE else None
        
        # Initialize feedback integration if available
        if self.feedback:
            # Process any pending feedback from Nico
            self.feedback.process()
        
    def collect(self) -> List[Dict]:
        """Collect recent experiences and data."""
        if not self.collector:
            log("Collector not available", "ERROR")
            return []
        
        log("Collecting experiences...")
        experiences = self.collector.collect()
        log(f"Collected {len(experiences)} experiences", "INFO")
        return experiences
    
    def analyze(self, experiences: List[Dict]) -> List[Dict]:
        """Analyze experiences for patterns and insights."""
        if not self.analyzer:
            log("Analyzer not available", "ERROR")
            return []
        
        log("Analyzing patterns...")
        patterns = self.analyzer.find_patterns(experiences)
        self.state["patterns_discovered"] += len(patterns)
        log(f"Found {len(patterns)} patterns", "INFO")
        return patterns
    
    def execute(self, patterns: List[Dict]) -> List[str]:
        """Execute improvements based on patterns."""
        if not self.executor:
            log("Executor not available", "ERROR")
            return []
        
        log("Executing improvements...")
        improvements = self.executor.apply_patterns(patterns)
        self.state["learnings_applied"] += len(improvements)
        self.state["improvements_made"].extend(improvements)
        log(f"Applied {len(improvements)} improvements", "INFO")
        return improvements
    
    def reflexion(self, improvements: List[str]) -> float:
        """
        Reflexion: How well did the loop do?
        Returns a score 0-1 representing loop effectiveness.
        
        Meta-learning: The loop learns how to learn better.
        """
        score = 0.0
        
        # Count positive signals
        if improvements:
            score += 0.4  # Base score for improvements
            
        # Check pattern quality
        patterns_count = self.state.get("patterns_discovered", 0)
        if patterns_count > 5:
            score += 0.2
            
        # Check learning rate (improvements per iteration)
        iterations = self.state.get("iterations", 1)
        learnings = self.state.get("learnings_applied", 0)
        if iterations > 0:
            rate = learnings / iterations
            if rate > 0.5:
                score += 0.2
                
        # Check self-improvement (improvements made to the loop itself)
        loop_improvements = sum(1 for imp in self.state.get("improvements_made", []) 
                               if "loop" in imp.lower() or "meta" in imp.lower())
        if loop_improvements > 0:
            score += 0.2  # Bonus for meta-learning
            
        self.state["last_reflexion_score"] = score
        log(f"Reflexion score: {score:.2f}", "INFO")
        
        # Update loop behavior based on score (meta-learning)
        if score < 0.3:
            log("Loop underperforming - adjusting strategy", "WARN")
            # Could trigger more aggressive learning
        elif score > 0.8:
            log("Loop performing well - maintaining strategy", "INFO")
            
        return score
    
    def run_full_loop(self) -> Dict:
        """Run the complete learning loop."""
        self.state["iterations"] += 1
        iteration = self.state["iterations"]
        
        log(f"=== Learning Loop Iteration {iteration} ===", "INFO")
        
        # Step 1: Collect
        experiences = self.collect()
        
        # Step 2: Analyze
        patterns = self.analyze(experiences)
        
        # Step 3: Execute
        improvements = self.execute(patterns)
        
        # Step 4: Reflexion (meta-learning)
        score = self.reflexion(improvements)
        
        # Meta-learning: Update analyzer weights based on reflexion score
        if self.analyzer:
            new_weights = self.analyzer.update_weights(score)
            log(f"Meta-learning: Updated analyzer weights to {new_weights}", "INFO")
        
        # Feedback integration: Adjust based on accumulated feedback
        if self.feedback:
            feedback_adjustments = self.feedback.integrate(score)
            if feedback_adjustments.get("adjustments"):
                log(f"Feedback: {feedback_adjustments}", "INFO")
        
        # Save state
        save_state(self.state)
        
        return {
            "iteration": iteration,
            "experiences": len(experiences),
            "patterns": len(patterns),
            "improvements": len(improvements),
            "reflexion_score": score
        }
    
    def get_status(self) -> Dict:
        """Get current loop status."""
        return {
            "iterations": self.state.get("iterations", 0),
            "learnings_applied": self.state.get("learnings_applied", 0),
            "patterns_discovered": self.state.get("patterns_discovered", 0),
            "last_reflexion_score": self.state.get("last_reflexion_score", 0),
            "recent_improvements": self.state.get("improvements_made", [])[-5:]
        }

def main():
    parser = argparse.ArgumentParser(description="Sir HazeClaw Learning Loop")
    parser.add_argument("--collect", action="store_true", help="Collect only")
    parser.add_argument("--analyze", action="store_true", help="Analyze only")
    parser.add_argument("--execute", action="store_true", help="Execute only")
    parser.add_argument("--reflexion", action="store_true", help="Reflexion only")
    parser.add_argument("--status", action="store_true", help="Show status")
    args = parser.parse_args()
    
    loop = LearningLoop()
    
    if args.status:
        status = loop.get_status()
        print(json.dumps(status, indent=2))
    elif args.collect:
        experiences = loop.collect()
        print(f"Collected {len(experiences)} experiences")
    elif args.analyze:
        experiences = loop.collect()
        patterns = loop.analyze(experiences)
        print(f"Found {len(patterns)} patterns")
    elif args.execute:
        patterns = []
        improvements = loop.execute(patterns)
        print(f"Applied {len(improvements)} improvements")
    elif args.reflexion:
        score = loop.reflexion([])
        print(f"Reflexion score: {score:.2f}")
    else:
        result = loop.run_full_loop()
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()