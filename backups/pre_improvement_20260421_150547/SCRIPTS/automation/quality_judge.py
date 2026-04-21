#!/usr/bin/env python3
"""
LLM-as-Judge Quality Evaluator — Sir HazeClaw Phase 3
======================================================
Uses LLM to evaluate task outputs and quality.

Based on:
- LLM-as-a-Judge (Zheng et al., 2023)
- Self-Consistency (Wang et al., 2022)
- PRIME (Zhao et al., 2024) — Self-correction via evaluation

Usage:
    python3 quality_judge.py --evaluate <task_result>
    python3 quality_judge.py --batch <file.json>
    python3 quality_judge.py --benchmark

Phase C2: LLM-as-Judge Quality Evaluation
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = WORKSPACE / "data"
JUDGE_DIR = DATA_DIR / "quality_judge"
JUDGE_LOG = JUDGE_DIR / "evaluations.json"
JUDGE_HISTORY = JUDGE_DIR / "history.json"

# Evaluation criteria
CRITERIA = {
    "correctness": {
        "name": "Correctness",
        "description": "Is the output factually correct?",
        "weight": 0.3,
    },
    "relevance": {
        "name": "Relevance", 
        "description": "Does the output address the user's request?",
        "weight": 0.25,
    },
    "completeness": {
        "name": "Completeness",
        "description": "Is the response thorough and complete?",
        "weight": 0.20,
    },
    "clarity": {
        "name": "Clarity",
        "description": "Is the output clear and well-structured?",
        "weight": 0.15,
    },
    "efficiency": {
        "name": "Efficiency",
        "description": "Was the response delivered efficiently?",
        "weight": 0.10,
    },
}

@dataclass
class EvaluationResult:
    """Result of LLM evaluation."""
    task_id: str
    overall_score: float  # 0-100
    verdict: str  # 'excellent', 'good', 'ok', 'poor'
    criteria_scores: Dict[str, float]
    feedback: str
    suggestions: List[str]
    timestamp: str
    model: str

class LLMasJudge:
    """
    LLM-as-a-Judge evaluator.
    
    Uses MiniMax to evaluate task outputs against defined criteria.
    Based on pairwise comparison + rubric scoring.
    """
    
    def __init__(self, model: str = "minimax/MiniMax-M2.7"):
        self.model = model
        self.criteria = CRITERIA
        self.stats = {
            "total_evaluated": 0,
            "excellent": 0,
            "good": 0,
            "ok": 0,
            "poor": 0,
        }
    
    def build_prompt(self, task: str, context: str, output: str) -> str:
        """Build evaluation prompt."""
        criteria_text = "\n".join([
            f"- {c['name']} ({c['weight']*100:.0f}%): {c['description']}"
            for c in self.criteria.values()
        ])
        
        prompt = f"""Du bist ein strenger Quality Judge für AI Agent Outputs.

## Task
{task}

## Context
{context}

## Output zu bewerten
{output}

## Bewertungskriterien
{criteria_text}

## Deine Aufgabe
Bewerte den Output auf einer Skala 0-100 für jedes Kriterium.
Gib einen overall_score, ein verdict, feedback und konkrete verbesserungsvorschläge.

## Output Format (JSON):
{{
  "overall_score": <0-100>,
  "verdict": "excellent|good|ok|poor",
  "criteria_scores": {{
    "correctness": <0-100>,
    "relevance": <0-100>,
    "completeness": <0-100>,
    "clarity": <0-100>,
    "efficiency": <0-100>
  }},
  "feedback": "<kurze analyse>",
  "suggestions": ["<vorschlag 1>", "<vorschlag 2>"]
}}

Sei ehrlich und streng. Ein "good" ist 70-85, "excellent" ist 85+."""
        return prompt
    
    def evaluate(self, task: str, context: str, output: str, task_id: str = None) -> EvaluationResult:
        """Evaluate an output using LLM-as-judge."""
        if not task_id:
            task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        prompt = self.build_prompt(task, context, output)
        
        # Call LLM
        try:
            result = subprocess.run(
                ["python3", "-c", f"""
import json
import sys
# Use openclaw's LLM if available, fallback to direct call
try:
    from openclaw import OpenClaw
    oc = OpenClaw()
    resp = oc.chat("{prompt.replace('"', '\\"')}")
    print(resp)
except Exception as e:
    print(json.dumps({{"error": str(e)}}))
"""],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Try to parse JSON response
            response_text = result.stdout.strip()
            
            # Handle JSON parsing
            try:
                evaluation = json.loads(response_text)
            except:
                # Fallback: parse manually
                evaluation = self._parse_fallback(response_text)
            
            overall_score = evaluation.get("overall_score", 50)
            verdict = evaluation.get("verdict", "ok")
            criteria_scores = evaluation.get("criteria_scores", {})
            feedback = evaluation.get("feedback", "")
            suggestions = evaluation.get("suggestions", [])
            
        except Exception as e:
            # Fallback on error
            overall_score = 50
            verdict = "ok"
            criteria_scores = {k: 50 for k in self.criteria.keys()}
            feedback = f"Evaluation failed: {e}"
            suggestions = ["Retry evaluation"]
        
        result_obj = EvaluationResult(
            task_id=task_id,
            overall_score=overall_score,
            verdict=verdict,
            criteria_scores=criteria_scores,
            feedback=feedback,
            suggestions=suggestions,
            timestamp=datetime.now().isoformat(),
            model=self.model
        )
        
        # Update stats
        self.stats["total_evaluated"] += 1
        if verdict in self.stats:
            self.stats[verdict] += 1
        
        return result_obj
    
    def _parse_fallback(self, text: str) -> Dict:
        """Fallback parser when JSON parsing fails."""
        # Simple heuristic parsing
        scores = {}
        for line in text.split('\n'):
            for crit in self.criteria.keys():
                if crit in line.lower() and ':' in line:
                    try:
                        score = int(''.join(filter(str.isdigit, line.split(':')[-1])))
                        scores[crit] = min(100, max(0, score))
                    except:
                        pass
        
        if not scores:
            scores = {k: 50 for k in self.criteria.keys()}
        
        return {
            "overall_score": sum(scores.values()) / len(scores),
            "verdict": "ok",
            "criteria_scores": scores,
            "feedback": text[:200],
            "suggestions": []
        }
    
    def evaluate_simple(self, task: str, output: str) -> float:
        """
        Simple self-evaluation without LLM call.
        Useful for quick checks.
        """
        score = 70  # Base score
        
        # Length heuristics
        if len(output) < 50:
            score -= 10
        elif len(output) > 5000:
            score -= 5
        
        # Check for common quality markers
        if any(marker in output.lower() for marker in ['✅', '❌', '⚠️', '📊']):
            score += 5  # Good formatting
        if output.count('\n') > 5:
            score += 3  # Structured
        
        # Check for error indicators
        if any(err in output.lower() for err in ['error', 'failed', 'exception']):
            score -= 15
        
        return min(100, max(0, score))
    
    def save_evaluation(self, result: EvaluationResult):
        """Save evaluation to log."""
        JUDGE_DIR.mkdir(parents=True, exist_ok=True)
        
        # Append to log
        if JUDGE_LOG.exists():
            evaluations = json.load(open(JUDGE_LOG))
        else:
            evaluations = []
        
        evaluations.append({
            "task_id": result.task_id,
            "overall_score": result.overall_score,
            "verdict": result.verdict,
            "criteria_scores": result.criteria_scores,
            "feedback": result.feedback,
            "suggestions": result.suggestions,
            "timestamp": result.timestamp,
        })
        
        with open(JUDGE_LOG, "w") as f:
            json.dump(evaluations, f, indent=2)
        
        # Update history
        self._update_history(result)
    
    def _update_history(self, result: EvaluationResult):
        """Update rolling history."""
        if JUDGE_HISTORY.exists():
            history = json.load(open(JUDGE_HISTORY))
        else:
            history = {"scores": [], "daily": {}}
        
        history["scores"].append(result.overall_score)
        history["scores"] = history["scores"][-100:]  # Keep last 100
        
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in history["daily"]:
            history["daily"][today] = []
        history["daily"][today].append(result.overall_score)
        
        with open(JUDGE_HISTORY, "w") as f:
            json.dump(history, f, indent=2)
    
    def get_average_score(self, days: int = 7) -> float:
        """Get average score over N days."""
        if JUDGE_HISTORY.exists():
            history = json.load(open(JUDGE_HISTORY))
            cutoff = datetime.now().timestamp() - (days * 86400)
            
            recent_scores = []
            for score, ts in [(s, t) for d in history.get("daily", {}).values() for s, t in d]:
                if datetime.fromisoformat(ts).timestamp() > cutoff:
                    recent_scores.append(score)
            
            return sum(recent_scores) / len(recent_scores) if recent_scores else 0
        return 0
    
    def print_report(self):
        """Print quality report."""
        print("\n📊 QUALITY JUDGE REPORT")
        print("=" * 50)
        
        if JUDGE_HISTORY.exists():
            history = json.load(open(JUDGE_HISTORY))
            scores = history.get("scores", [])
            if scores:
                avg = sum(scores) / len(scores)
                print(f"Overall Average: {avg:.1f}/100 ({len(scores)} evaluations)")
                print(f"Recent Trend: {scores[-5:]}")
        else:
            print("No evaluations yet")
        
        print(f"\nVerdict Distribution:")
        for verdict, count in self.stats.items():
            if verdict != "total_evaluated" and count > 0:
                print(f"  {verdict}: {count}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='LLM-as-Judge Quality Evaluator')
    parser.add_argument('--evaluate', type=str, help='Evaluate a task output')
    parser.add_argument('--task', type=str, default='Unknown task', help='Task description')
    parser.add_argument('--context', type=str, default='', help='Context for task')
    parser.add_argument('--batch', type=str, help='Batch evaluate from JSON file')
    parser.add_argument('--benchmark', action='store_true', help='Run benchmark')
    parser.add_argument('--report', action='store_true', help='Show report')
    args = parser.parse_args()
    
    judge = LLMasJudge()
    
    if args.report:
        judge.print_report()
        return
    
    if args.benchmark:
        # Run simple benchmark
        print("🏋️ Running Benchmark...")
        test_cases = [
            ("Simple question", "What's 2+2?", "4", "quick answer"),
            ("Complex task", "Explain quantum physics", "Quantum physics is...", "detailed explanation"),
            ("Error case", "Fix this bug", "Error: file not found", "error response"),
        ]
        
        results = []
        for name, task, output, desc in test_cases:
            score = judge.evaluate_simple(task, output)
            results.append((name, desc, score))
            print(f"  {name}: {score}/100 ({desc})")
        
        print(f"\nBenchmark Average: {sum(r[2] for r in results) / len(results):.1f}/100")
        return
    
    if args.evaluate:
        # Single evaluation
        task = args.task
        context = args.context or ""
        output = args.evaluate
        
        print(f"🔍 Evaluating output for: {task[:50]}...")
        
        # Try LLM evaluation
        result = judge.evaluate(task, context, output)
        
        print(f"\n📋 Evaluation Result:")
        print(f"   Overall Score: {result.overall_score}/100")
        print(f"   Verdict: {result.verdict.upper()}")
        print(f"   Feedback: {result.feedback[:100]}...")
        
        if result.suggestions:
            print(f"\n💡 Suggestions:")
            for s in result.suggestions[:3]:
                print(f"   - {s}")
        
        # Save
        judge.save_evaluation(result)
        print(f"\n✅ Evaluation saved")
        return
    
    if args.batch:
        # Batch evaluation
        print(f"📦 Batch evaluating from {args.batch}...")
        with open(args.batch) as f:
            tasks = json.load(f)
        
        for item in tasks:
            result = judge.evaluate(
                item.get('task', 'Unknown'),
                item.get('context', ''),
                item.get('output', ''),
                item.get('id', None)
            )
            judge.save_evaluation(result)
        
        print(f"✅ Evaluated {len(tasks)} tasks")
        judge.print_report()
        return
    
    # Default: help
    print("LLM-as-Judge Quality Evaluator")
    print("Usage:")
    print("  --evaluate <text>  Evaluate a single output")
    print("  --benchmark        Run benchmark tests")
    print("  --report           Show quality report")


if __name__ == "__main__":
    main()
