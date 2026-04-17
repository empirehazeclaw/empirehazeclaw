#!/usr/bin/env python3
"""
Learning Analyzer — Sir HazeClaw
Analyzes collected experiences to find patterns and improvement opportunities.

Usage:
    from learning_analyzer import LearningAnalyzer
    analyzer = LearningAnalyzer()
    patterns = analyzer.find_patterns(experiences)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
KG_PATH = WORKSPACE / "core_ultralight" / "memory" / "knowledge_graph.json"

class LearningAnalyzer:
    """
    Analyzes experiences to find patterns.
    
    The analyzer itself improves over time as it learns
    what patterns are most valuable (meta-learning).
    """
    
    def __init__(self):
        # Pattern weights (can be updated by reflexion)
        self.weights = {
            "cron_failure": 0.8,
            "system_error": 0.7,
            "user_error_feedback": 0.6,
            "positive_feedback": 0.5,
            "kg_entity_access": 0.3
        }
        self.min_confidence = 0.5
        
    def find_patterns(self, experiences: List[Dict]) -> List[Dict]:
        """Find patterns in experiences."""
        patterns = []
        
        # Group by type
        by_type = {}
        for exp in experiences:
            exp_type = exp.get("type", "unknown")
            if exp_type not in by_type:
                by_type[exp_type] = []
            by_type[exp_type].append(exp)
        
        # Analyze each type
        for exp_type, items in by_type.items():
            if len(items) >= 2:  # Need at least 2 to form a pattern
                pattern = self.analyze_type_pattern(exp_type, items)
                if pattern:
                    patterns.append(pattern)
        
        # Look for temporal patterns (things happening together)
        temporal = self.find_temporal_patterns(experiences)
        patterns.extend(temporal)
        
        # Rank patterns by confidence
        patterns.sort(key=lambda p: -p.get("confidence", 0))
        
        return patterns
    
    def analyze_type_pattern(self, exp_type: str, items: List[Dict]) -> Dict:
        """Analyze a specific type of experience."""
        weight = self.weights.get(exp_type, 0.5)
        
        # Count occurrences
        count = len(items)
        
        # Calculate confidence based on count and weight
        confidence = min(weight * (count / 10), 1.0)
        
        if confidence < self.min_confidence:
            return None
        
        # Extract common elements
        common = self.find_common_elements(items)
        
        return {
            "type": "type_pattern",
            "experience_type": exp_type,
            "count": count,
            "confidence": confidence,
            "common_elements": common,
            "suggestion": self.generate_suggestion(exp_type, items)
        }
    
    def find_common_elements(self, items: List[Dict]) -> List[str]:
        """Find common elements across items."""
        common = []
        
        # Look for common words in content
        content_words = []
        for item in items:
            content = item.get("content", item.get("entity", ""))
            if content:
                words = content.lower().split()[:10]
                content_words.extend(words)
        
        # Find most common
        word_count = {}
        for word in content_words:
            if len(word) > 4:  # Ignore short words
                word_count[word] = word_count.get(word, 0) + 1
        
        common = sorted(word_count.items(), key=lambda x: -x[1])[:5]
        return [word for word, count in common if count >= 2]
    
    def find_temporal_patterns(self, experiences: List[Dict]) -> List[Dict]:
        """Find patterns based on timing (e.g., errors happening together)."""
        patterns = []
        
        # Group by timestamp (within same hour)
        by_hour = {}
        for exp in experiences:
            ts = exp.get("timestamp", "")
            if ts:
                hour = ts[:13]  # YYYY-MM-DDTHH
                if hour not in by_hour:
                    by_hour[hour] = []
                by_hour[hour].append(exp)
        
        # Look for hours with multiple errors
        for hour, items in by_hour.items():
            errors = [i for i in items if "error" in i.get("type", "").lower()]
            if len(errors) >= 3:
                patterns.append({
                    "type": "temporal_pattern",
                    "pattern": "multiple_errors_same_hour",
                    "hour": hour,
                    "count": len(errors),
                    "confidence": min(len(errors) / 10, 1.0),
                    "suggestion": "Investigate cause of multiple errors in same hour"
                })
        
        return patterns
    
    def generate_suggestion(self, exp_type: str, items: List[Dict]) -> str:
        """Generate improvement suggestion based on pattern."""
        suggestions = {
            "cron_failure": "Review and fix failing cron job",
            "system_error": "Analyze error pattern and implement fix",
            "user_error_feedback": "Improve user guidance or interface",
            "positive_feedback": "Document what worked for reuse",
            "kg_entity_access": "KG entity valuable - ensure it's used properly",
            "cron_degraded": "Monitor and optimize degraded cron job"
        }
        
        base = suggestions.get(exp_type, "Review and improve")
        
        # Add specifics if available
        if exp_type == "cron_failure":
            job_name = items[0].get("job_name", "unknown")
            return f"Fix cron job: {job_name}"
        
        return base

    def update_weights(self, reflexion_score: float):
        """
        Meta-learning: Update pattern weights based on reflexion results.
        If a pattern type consistently leads to improvements, increase its weight.
        This is the CLOSED-LOOP part of the learning system.
        """
        # Load current weights from state
        state_file = WORKSPACE / "data" / "learning_loop_state.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        
        state = {}
        if state_file.exists():
            try:
                state = json.load(open(state_file))
            except (IOError, json.JSONDecodeError):
                # File read or JSON parse failed - use empty state
                state = {}
        
        if "analyzer_weights" not in state:
            state["analyzer_weights"] = self.weights.copy()
        
        # Adjust based on reflexion score
        if reflexion_score > 0.7:
            # Loop is doing well - increase all weights slightly (be more aggressive)
            for key in state["analyzer_weights"]:
                state["analyzer_weights"][key] = min(state["analyzer_weights"][key] + 0.02, 1.0)
            self.weights = state["analyzer_weights"]
        elif reflexion_score < 0.3:
            # Loop is struggling - be more conservative (higher threshold)
            for key in state["analyzer_weights"]:
                state["analyzer_weights"][key] = max(state["analyzer_weights"][key] - 0.05, 0.1)
            self.weights = state["analyzer_weights"]
        
        # Log weight changes
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)
        
        return self.weights

def main():
    """Test analyzer."""
    from learning_collector import LearningCollector
    
    collector = LearningCollector()
    experiences = collector.collect()
    
    analyzer = LearningAnalyzer()
    patterns = analyzer.find_patterns(experiences)
    
    print(f"Found {len(patterns)} patterns:")
    for pattern in patterns[:10]:
        print(f"  [{pattern.get('confidence', 0):.2f}] {pattern.get('suggestion', 'No suggestion')[:100]}")

if __name__ == "__main__":
    main()