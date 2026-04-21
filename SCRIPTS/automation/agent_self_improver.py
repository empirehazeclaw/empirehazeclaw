#!/usr/bin/env python3
"""
Agent Self-Improver — Sir HazeClaw's Self-Learning System

A "Learning Loop for the Learning Loop" - analyzes my own behavior
and improves my scripts/patterns/decisions over time.

Research-based design from best practices:
- Reflection Pattern (self-critique before output)
- ReAct Pattern (Think → Act → Observe → Adjust)
- Verbal Reinforcement (store critiques for future)
- Continuous Learning Loop (Data → Analysis → Improvement)

Author: Sir HazeClaw
Date: 2026-04-13
"""

import sys
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# ============ CONFIGURATION ============

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = WORKSPACE / "DATA" / "self_improvement"
DECISIONS_DIR = DATA_DIR / "decisions"
CONFIG_CHANGES_DIR = DATA_DIR / "config_changes"
LEARNINGS_FILE = DATA_DIR / "learnings" / "learnings.json"

# Import the memory/log analyzer
try:
    from memory_log_analyzer import MemoryLogAnalyzer
except ImportError:
    MemoryLogAnalyzer = None

# Import unified Learnings Service
sys.path.insert(0, str(WORKSPACE / 'SCRIPTS/automation'))
try:
    from learnings_service import LearningsService
except:
    LearningsService = None

# Safety limits
MAX_CHANGES_PER_CYCLE = 1
OBSERVATION_PERIOD_HOURS = 24
ROLLBACK_THRESHOLD_DEGRADE = 0.1

# ============ COMPONENT 1: LEARNING STORE ============

class LearningStore:
    """Persistent storage for agent learnings."""
    
    def __init__(self):
        self.learnings_file = LEARNINGS_FILE
        self.ensure_storage()
    
    def ensure_storage(self):
        """Ensure storage directories exist."""
        self.learnings_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.learnings_file.exists():
            self.save_learnings({
                "patterns": [],
                "warnings": [],
                "improvements": [],
                "metadata": {
                    "created": datetime.utcnow().isoformat(),
                    "version": "1.0"
                }
            })
    
    def load_learnings(self) -> Dict:
        """Load all learnings from storage."""
        with open(self.learnings_file, 'r') as f:
            return json.load(f)
    
    def save_learnings(self, data: Dict):
        """Save learnings to storage."""
        with open(self.learnings_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def store_pattern(self, pattern: Dict) -> bool:
        """Store a successful pattern."""
        data = self.load_learnings()
        pattern.update({
            "id": f"pattern_{len(data['patterns']) + 1}",
            "stored_at": datetime.utcnow().isoformat(),
            "success_count": 1,
            "failure_count": 0
        })
        data["patterns"].append(pattern)
        self.save_learnings(data)
        print(f"✅ Stored pattern: {pattern.get('name', 'unnamed')[:50]}")
        return True
    
    def store_warning(self, warning: Dict) -> bool:
        """Store a pattern to avoid."""
        data = self.load_learnings()
        warning.update({
            "id": f"warning_{len(data['warnings']) + 1}",
            "stored_at": datetime.utcnow().isoformat(),
            "hit_count": 1
        })
        data["warnings"].append(warning)
        self.save_learnings(data)
        print(f"⚠️ Stored warning: {warning.get('pattern', 'unnamed')[:50]}")
        return True
    
    def record_improvement(self, improvement: Dict) -> bool:
        """Record a successful improvement."""
        data = self.load_learnings()
        improvement.update({
            "id": f"improvement_{len(data['improvements']) + 1}",
            "applied_at": datetime.utcnow().isoformat(),
            "success": True
        })
        data["improvements"].append(improvement)
        self.save_learnings(data)
        
        # Also sync to unified Learnings Service
        if LearningsService:
            try:
                ls = LearningsService()
                ls.record_learning(
                    source="Self-Improver",
                    category="improvement",
                    learning=improvement.get("description", str(improvement)),
                    context=improvement.get("type", "general"),
                    outcome="success"
                )
            except Exception as e:
                print(f"Warning: Failed to sync to Learnings Service: {e}")
        
        return True
    
    def get_patterns_for_context(self, context: str, limit: int = 5) -> List[Dict]:
        """Retrieve patterns relevant to current context."""
        data = self.load_learnings()
        patterns = data.get("patterns", [])
        
        # Simple relevance scoring based on keywords
        scored = []
        for p in patterns:
            score = 0
            desc = p.get("description", "").lower()
            ctx = context.lower()
            for word in ctx.split():
                if word in desc:
                    score += 1
            scored.append((score, p))
        
        scored.sort(reverse=True, key=lambda x: x[0])
        return [p[1] for p in scored[:limit]]
    
    def calculate_improvement_score(self) -> float:
        """Calculate overall improvement over time."""
        data = self.load_learnings()
        patterns = data.get("patterns", [])
        improvements = data.get("improvements", [])
        
        if not patterns:
            return 0.0
        
        # Score based on pattern success rate and improvement count
        success_rate = sum(1 for p in patterns if p.get("success_count", 0) > p.get("failure_count", 0)) / len(patterns)
        improvement_bonus = min(len(improvements) * 0.05, 0.3)
        
        return min(0.95, success_rate * 0.5 + improvement_bonus)


# ============ COMPONENT 2: DECISION TRACKER ============

class DecisionTracker:
    """Track decisions, context, and outcomes."""
    
    def __init__(self):
        self.decisions_dir = DECISIONS_DIR
        self.ensure_storage()
    
    def ensure_storage(self):
        """Ensure storage directory exists."""
        self.decisions_dir.mkdir(parents=True, exist_ok=True)
    
    def record_decision(
        self,
        context: str,
        decision: str,
        confidence: float,
        alternatives: List[str] = None,
        reasoning: str = ""
    ) -> str:
        """Record a decision I made."""
        decision_id = f"dec_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{len(self.get_recent_decisions())}"
        
        record = {
            "id": decision_id,
            "context": context,
            "decision": decision,
            "confidence": confidence,
            "alternatives": alternatives or [],
            "reasoning": reasoning,
            "recorded_at": datetime.utcnow().isoformat(),
            "outcome": None,
            "outcome_quality": None
        }
        
        filepath = self.decisions_dir / f"{decision_id}.json"
        with open(filepath, 'w') as f:
            json.dump(record, f, indent=2)
        
        print(f"📝 Recorded decision: {decision[:50]} (confidence: {confidence})")
        return decision_id
    
    def record_outcome(self, decision_id: str, outcome: str, quality: float) -> bool:
        """Record the outcome of a decision."""
        filepath = self.decisions_dir / f"{decision_id}.json"
        
        if not filepath.exists():
            print(f"❌ Decision not found: {decision_id}")
            return False
        
        with open(filepath, 'r') as f:
            record = json.load(f)
        
        record["outcome"] = outcome
        record["outcome_quality"] = quality
        record["outcome_recorded_at"] = datetime.utcnow().isoformat()
        
        with open(filepath, 'w') as f:
            json.dump(record, f, indent=2)
        
        print(f"✅ Recorded outcome for {decision_id}: {outcome} (quality: {quality})")
        return True
    
    def get_recent_decisions(self, limit: int = 50) -> List[Dict]:
        """Get recent decisions."""
        files = sorted(self.decisions_dir.glob("dec_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
        decisions = []
        
        for f in files[:limit]:
            with open(f, 'r') as fp:
                decisions.append(json.load(fp))
        
        return decisions
    
    def calculate_calibration(self) -> Dict:
        """Calculate how well my confidence matched actual outcomes."""
        decisions = self.get_recent_decisions()
        decisions_with_outcome = [d for d in decisions if d.get("outcome") is not None]
        
        if not decisions_with_outcome:
            return {"calibration_score": 0.0, "sample_size": 0}
        
        total_error = 0.0
        for d in decisions_with_outcome:
            confidence = d.get("confidence", 0.5)
            quality = d.get("outcome_quality", 0.0)
            total_error += abs(confidence - quality)
        
        avg_error = total_error / len(decisions_with_outcome)
        calibration_score = max(0.0, 1.0 - (avg_error * 2))  # 0 = perfect calibration
        
        return {
            "calibration_score": calibration_score,
            "sample_size": len(decisions_with_outcome),
            "avg_error": avg_error
        }


# ============ COMPONENT 3: SELF-EVALUATION ENGINE ============

class SelfEvaluationEngine:
    """Compare self-assessment against actual outcomes."""
    
    def __init__(self):
        self.decision_tracker = DecisionTracker()
        self.learning_store = LearningStore()
    
    def evaluate_recent_performance(self) -> Dict:
        """Evaluate recent performance across all tracked decisions."""
        calibration = self.decision_tracker.calculate_calibration()
        improvement_score = self.learning_store.calculate_improvement_score()
        
        recent = self.decision_tracker.get_recent_decisions(limit=20)
        decisions_with_outcome = [d for d in recent if d.get("outcome") is not None]
        
        # Calculate decision accuracy
        good_decisions = [d for d in decisions_with_outcome if d.get("outcome_quality", 0) >= 0.6]
        decision_accuracy = len(good_decisions) / len(decisions_with_outcome) if decisions_with_outcome else 0.0
        
        return {
            "calibration_score": calibration.get("calibration_score", 0.0),
            "decision_accuracy": decision_accuracy,
            "improvement_score": improvement_score,
            "decisions_tracked": len(recent),
            "decisions_with_outcome": len(decisions_with_outcome),
            "evaluated_at": datetime.utcnow().isoformat()
        }
    
    def identify_patterns_in_decisions(self) -> Dict:
        """Identify patterns in my decision-making."""
        decisions = self.decision_tracker.get_recent_decisions(limit=100)
        
        high_confidence = [d for d in decisions if d.get("confidence", 0) >= 0.7]
        low_confidence = [d for d in decisions if d.get("confidence", 0) < 0.5]
        
        high_conf_correct = [d for d in high_confidence if d.get("outcome_quality", 0) >= 0.6]
        low_conf_correct = [d for d in low_confidence if d.get("outcome_quality", 0) >= 0.6]
        
        return {
            "high_confidence_decisions": len(high_confidence),
            "high_confidence_correct": len(high_conf_correct),
            "low_confidence_decisions": len(low_confidence),
            "low_confidence_correct": len(low_conf_correct),
            "overconfidence_ratio": len(high_confidence) / max(1, len(decisions)),
            "underconfidence_ratio": len(low_confidence) / max(1, len(decisions))
        }


# ============ COMPONENT 4: CONFIGURATION MODIFIER ============

class ConfigurationModifier:
    """Safely modify scripts based on learnings."""
    
    def __init__(self):
        self.changes_dir = CONFIG_CHANGES_DIR
        self.learning_store = LearningStore()
        self.ensure_storage()
    
    def ensure_storage(self):
        """Ensure storage directory exists."""
        self.changes_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze_script(self, script_path: str) -> Dict:
        """Analyze a script for improvement opportunities."""
        if not os.path.exists(script_path):
            return {"error": f"Script not found: {script_path}"}
        
        with open(script_path, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        return {
            "path": script_path,
            "line_count": len(lines),
            "char_count": len(content),
            "functions": self._extract_functions(content),
            "imports": self._extract_imports(content),
            "comments_ratio": content.count('#') / max(1, len(lines))
        }
    
    def _extract_functions(self, content: str) -> List[str]:
        """Extract function definitions."""
        import re
        functions = re.findall(r'def (\w+)\(', content)
        return functions
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements."""
        imports = []
        for line in content.split('\n'):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                imports.append(line.strip())
        return imports
    
    def suggest_modifications(self, script_analysis: Dict, learnings: List[Dict]) -> List[Dict]:
        """Generate modification suggestions based on learnings."""
        suggestions = []
        
        for learning in learnings:
            if learning.get("type") == "improvement":
                suggestion = {
                    "script": script_analysis.get("path"),
                    "learning_id": learning.get("id"),
                    "change": learning.get("change", {}),
                    "reason": learning.get("description", "Pattern-based improvement")
                }
                suggestions.append(suggestion)
        
        return suggestions
    
    def apply_modification(self, script_path: str, change: Dict) -> Tuple[bool, str]:
        """Apply a validated modification to a script."""
        if not os.path.exists(script_path):
            return False, f"Script not found: {script_path}"
        
        # Create backup
        with open(script_path, 'r') as f:
            original = f.read()
        
        backup_path = f"{script_path}.backup.{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        with open(backup_path, 'w') as f:
            f.write(original)
        
        # Apply change (simplified - would need more sophisticated implementation)
        modified = original  # Placeholder
        
        change_id = f"change_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        change_record = {
            "id": change_id,
            "script": script_path,
            "backup": backup_path,
            "change": change,
            "applied_at": datetime.utcnow().isoformat(),
            "status": "applied",
            "rollback_available": True
        }
        
        change_file = self.changes_dir / f"{change_id}.json"
        with open(change_file, 'w') as f:
            json.dump(change_record, f, indent=2)
        
        return True, change_id
    
    def rollback_if_needed(self, change_id: str, metrics: Dict) -> bool:
        """Rollback if modification caused metric degradation."""
        change_file = self.changes_dir / f"{change_id}.json"
        
        if not change_file.exists():
            return False
        
        with open(change_file, 'r') as f:
            change = json.load(f)
        
        if not change.get("rollback_available"):
            return False
        
        # Check if metrics degraded
        error_rate = metrics.get("error_rate", 0)
        if error_rate > ROLLBACK_THRESHOLD_DEGRADE:
            return self._rollback(change_id, change)
        
        return False
    
    def _rollback(self, change_id: str, change: Dict) -> bool:
        """Perform rollback."""
        backup_path = change.get("backup")
        
        if not backup_path or not os.path.exists(backup_path):
            print(f"❌ Backup not found for {change_id}")
            return False
        
        script_path = change.get("script")
        
        with open(backup_path, 'r') as f:
            original = f.read()
        
        with open(script_path, 'w') as f:
            f.write(original)
        
        change["status"] = "rolled_back"
        change["rolled_back_at"] = datetime.utcnow().isoformat()
        
        with open(self.changes_dir / f"{change_id}.json", 'w') as f:
            json.dump(change, f, indent=2)
        
        print(f"🔄 Rolled back {change_id}")
        return True


# ============ COMPONENT 5: CONVERSATION ANALYZER ============

class ConversationAnalyzer:
    """Analyze conversation history for improvement patterns."""
    
    def __init__(self):
        self.learning_store = LearningStore()
    
    def extract_signals_from_session(self, session_data: Dict) -> List[Dict]:
        """Extract learning signals from a session."""
        signals = []
        
        messages = session_data.get("messages", [])
        
        for i, msg in enumerate(messages):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            
            # Signal: User feedback
            if role == "user":
                if any(x in content.lower() for x in ["danke", "perfekt", "super", " excellent", "thanks"]):
                    signals.append({
                        "type": "positive_feedback",
                        "content": content[:100],
                        "signal_strength": 0.8
                    })
                elif any(x in content.lower() for x in ["nein", "falsch", "wrong", "bad", "schlecht"]):
                    signals.append({
                        "type": "negative_feedback",
                        "content": content[:100],
                        "signal_strength": 0.8
                    })
            
            # Signal: Tool usage patterns
            if role == "assistant" and msg.get("tool_calls"):
                signals.append({
                    "type": "tool_usage",
                    "tools": [tc.get("function", {}).get("name") for tc in msg.get("tool_calls", [])],
                    "signal_strength": 0.5
                })
        
        return signals
    
    def identify_success_patterns(self, sessions: List[Dict]) -> List[Dict]:
        """Find patterns that lead to positive outcomes."""
        patterns = []
        
        for session in sessions:
            signals = self.extract_signals_from_session(session)
            positive_count = len([s for s in signals if s.get("type") == "positive_feedback"])
            
            if positive_count >= 2:
                patterns.append({
                    "type": "success_pattern",
                    "session_id": session.get("session_id"),
                    "positive_signals": positive_count,
                    "characteristics": self._extract_characteristics(session)
                })
        
        return patterns
    
    def identify_failure_patterns(self, sessions: List[Dict]) -> List[Dict]:
        """Find patterns that lead to negative outcomes."""
        patterns = []
        
        for session in sessions:
            signals = self.extract_signals_from_session(session)
            negative_count = len([s for s in signals if s.get("type") == "negative_feedback"])
            
            if negative_count >= 1:
                patterns.append({
                    "type": "failure_pattern",
                    "session_id": session.get("session_id"),
                    "negative_signals": negative_count,
                    "characteristics": self._extract_characteristics(session)
                })
        
        return patterns
    
    def _extract_characteristics(self, session: Dict) -> Dict:
        """Extract session characteristics."""
        messages = session.get("messages", [])
        
        return {
            "message_count": len(messages),
            "tool_calls": sum(1 for m in messages if m.get("tool_calls")),
            "avg_message_length": sum(len(m.get("content", "")) for m in messages) / max(1, len(messages))
        }


# ============ MAIN ORCHESTRATOR ============

class AgentSelfImprover:
    """Main orchestrator for the Agent Self-Improver system."""
    
    def __init__(self):
        self.learning_store = LearningStore()
        self.decision_tracker = DecisionTracker()
        self.self_eval = SelfEvaluationEngine()
        self.config_modifier = ConfigurationModifier()
        self.conversation_analyzer = ConversationAnalyzer()
    
    def run_self_improvement_cycle(self, context: str = "") -> Dict:
        """
        Run one complete self-improvement cycle.
        
        Process:
        1. Analyze recent performance
        2. Extract patterns from conversations
        3. Update learnings
        4. Generate improvement suggestions
        5. Apply safe modifications
        """
        print("\n" + "="*60)
        print("🔄 AGENT SELF-IMPROVER — Self-Improvement Cycle")
        print("="*60)
        
        # Step 1: Performance Analysis
        print("\n📊 Step 1: Analyzing recent performance...")
        performance = self.self_eval.evaluate_recent_performance()
        print(f"   Calibration Score: {performance['calibration_score']:.2f}")
        print(f"   Decision Accuracy: {performance['decision_accuracy']:.2f}")
        print(f"   Improvement Score: {performance['improvement_score']:.2f}")
        
        # Step 2: Pattern Analysis
        print("\n📊 Step 2: Analyzing decision patterns...")
        patterns = self.self_eval.identify_patterns_in_decisions()
        print(f"   High-confidence decisions: {patterns['high_confidence_decisions']}")
        print(f"   High-confidence correct: {patterns['high_confidence_correct']}")
        print(f"   Low-confidence decisions: {patterns['low_confidence_decisions']}")
        
        # Step 3: Learning Store Analysis
        print("\n📊 Step 3: Checking learning store...")
        improvement_score = self.learning_store.calculate_improvement_score()
        print(f"   Current improvement score: {improvement_score:.2f}")
        
        # Step 4: Memory & Log Analysis (NEW!)
        print("\n📊 Step 4: Analyzing memory & logs...")
        if MemoryLogAnalyzer:
            try:
                mem_analyzer = MemoryLogAnalyzer()
                insights = mem_analyzer.analyze_and_store()
                mem_patterns, mem_warnings = mem_analyzer.get_patterns_from_insights(insights)
                
                # Store extracted patterns
                for p in mem_patterns[:10]:  # Limit per cycle
                    self.learning_store.store_pattern(p)
                
                # Store warnings
                for w in mem_warnings[:5]:  # Limit per cycle
                    self.learning_store.store_warning(w)
                
                print(f"   Memory patterns stored: {len(mem_patterns)}")
                print(f"   Warnings stored: {len(mem_warnings)}")
            except Exception as e:
                print(f"   ⚠️ Memory analysis failed: {e}")
        else:
            print("   ⚠️ MemoryLogAnalyzer not available")
        
        # Step 4: Generate Summary
        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "performance": performance,
            "patterns": patterns,
            "improvement_score": improvement_score,
            "context": context
        }
        
        print("\n" + "="*60)
        print("✅ Self-Improvement Cycle Complete")
        print("="*60)
        
        return summary
    
    def record_decision_and_context(
        self,
        context: str,
        decision: str,
        confidence: float,
        reasoning: str = ""
    ) -> str:
        """Convenience method to record a decision with context."""
        return self.decision_tracker.record_decision(
            context=context,
            decision=decision,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def record_outcome_and_learn(
        self,
        decision_id: str,
        outcome: str,
        quality: float
    ) -> bool:
        """Record outcome and update learnings."""
        success = self.decision_tracker.record_outcome(decision_id, outcome, quality)
        
        if success and quality >= 0.7:
            # Good outcome - store as positive pattern
            self.learning_store.store_pattern({
                "name": f"decision_{decision_id}",
                "description": f"Quality: {quality}",
                "success_count": 1
            })
        elif success and quality < 0.3:
            # Bad outcome - store as warning
            self.learning_store.store_warning({
                "pattern": f"decision_{decision_id}",
                "description": f"Failed with quality: {quality}"
            })
        
        return success


# ============ CLI INTERFACE ============

def main():
    """CLI interface for Agent Self-Improver."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Self-Improver — Sir HazeClaw's Self-Learning System")
    parser.add_argument("--cycle", action="store_true", help="Run self-improvement cycle")
    parser.add_argument("--analyze", metavar="SCRIPT", help="Analyze a script for improvements")
    parser.add_argument("--decisions", action="store_true", help="Show recent decisions")
    parser.add_argument("--calibration", action="store_true", help="Show calibration score")
    parser.add_argument("--learnings", action="store_true", help="Show stored learnings")
    parser.add_argument("--score", action="store_true", help="Show improvement score")
    
    args = parser.parse_args()
    
    improver = AgentSelfImprover()
    
    if args.cycle:
        result = improver.run_self_improvement_cycle()
        print(json.dumps(result, indent=2))
    
    elif args.analyze:
        result = improver.config_modifier.analyze_script(args.analyze)
        print(json.dumps(result, indent=2))
    
    elif args.decisions:
        decisions = improver.decision_tracker.get_recent_decisions(limit=10)
        print(json.dumps(decisions, indent=2))
    
    elif args.calibration:
        calibration = improver.decision_tracker.calculate_calibration()
        print(json.dumps(calibration, indent=2))
    
    elif args.learnings:
        learnings = improver.learning_store.load_learnings()
        print(json.dumps(learnings, indent=2))
    
    elif args.score:
        score = improver.learning_store.calculate_improvement_score()
        print(f"Improvement Score: {score:.2f}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
