#!/usr/bin/env python3
"""
Self-Evaluator — Sir HazeClaw Phase 6
=====================================
Pre-validation self-scoring for improvements.

Based on:
- Self-Rewarding Language Models (Yuan et al., 2025)
- Self-Consistency (Wang et al., 2022)
- Reflexion (Shinn et al., 2023)

Usage:
    python3 self_evaluator.py --evaluate improvement.json
    python3 self_evaluator.py --stats

Phase 6 of Self-Improvement Plan
"""

import os
import sys
import json
import math
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# Config
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "SCRIPTS" / "automation"
DATA_DIR = WORKSPACE / "data"
IDEA_BANK_FILE = DATA_DIR / "learning_loop" / "idea_bank.json"

# Self-reward thresholds
SELF_REWARD_THRESHOLD = 0.65  # Minimum score to proceed
SELF_REWARD_CONFIDENCE = 0.45  # If below this, skip without trying


def load_idea_bank() -> Dict:
    """Load idea bank."""
    if IDEA_BANK_FILE.exists():
        try:
            return json.load(open(IDEA_BANK_FILE))
        except:
            pass
    return {"ideas": [], "version": "1.0"}


def similarity(s1: str, s2: str) -> float:
    """Simple string similarity (Jaccard)."""
    if not s1 or not s2:
        return 0.0
    set1 = set(s1.lower().split())
    set2 = set(s2.lower().split())
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)


class SelfEvaluator:
    """
    Pre-validation self-scoring for improvements.
    
    Key insight (from Self-Rewarding LM):
    - Model should be able to evaluate its own outputs
    - Internal self-evaluation improves over time
    - Pre-validation screening reduces unnecessary failures
    """
    
    def __init__(self, threshold: float = None, confidence_threshold: float = None):
        self.threshold = threshold or SELF_REWARD_THRESHOLD
        self.confidence_threshold = confidence_threshold or SELF_REWARD_CONFIDENCE
        self.stats = {
            'total_evaluated': 0,
            'proceed': 0,
            'revise': 0,
            'skip': 0,
            'validation_outcomes': {'success': 0, 'failure': 0}
        }
    
    def evaluate(self, improvement: Dict, context: Dict, use_llm: bool = True) -> Dict:
        """
        Evaluate an improvement before sending to validation.
        
        Args:
            improvement: The improvement to evaluate
            context: Context (issue description, etc.)
            use_llm: If True, try LLM evaluation first (Phase 8 upgrade)
        
        Returns:
            {
                'score': 0.0-1.0,
                'decision': 'proceed' | 'revise' | 'skip',
                'checks': {...},
                'reasons': [...]
            }
        """
        self.stats['total_evaluated'] += 1
        
        # Try LLM evaluation first (Phase 8)
        if use_llm:
            llm_result = self.evaluate_with_llm(improvement, context)
            if llm_result.get('llm_used'):
                # LLM gave a valid response - use it
                decision = llm_result.get('decision', 'proceed')
                score = llm_result.get('score', 0.5)
                
                # Update stats
                if decision == 'proceed':
                    self.stats['proceed'] += 1
                elif decision == 'revise':
                    self.stats['revise'] += 1
                else:
                    self.stats['skip'] += 1
                
                return {
                    'score': score,
                    'decision': decision,
                    'checks': {'llm_evaluation': llm_result},
                    'reasons': [llm_result.get('reasoning', 'LLM evaluation')],
                    'llm_used': True,
                    'threshold': self.threshold,
                    'confidence_threshold': self.confidence_threshold
                }
        
        # Fall back to rule-based evaluation
        checks = {
            'syntax': self._check_syntax(improvement),
            'logic': self._check_logic(improvement),
            'impact': self._check_expected_impact(improvement, context),
            'history': self._check_history(improvement),
            'risk': self._check_risk(improvement)
        }
        
        # Weighted score
        weights = {
            'syntax': 0.15,
            'logic': 0.20,
            'impact': 0.30,
            'history': 0.20,
            'risk': 0.15
        }
        score = sum(checks[k]['score'] * weights[k] for k in weights)
        
        # Decision
        if score >= self.threshold:
            decision = 'proceed'
            self.stats['proceed'] += 1
        elif score >= self.confidence_threshold:
            decision = 'revise'
            self.stats['revise'] += 1
        else:
            decision = 'skip'
            self.stats['skip'] += 1
        
        reasons = self._generate_reasons(checks, score, decision)
        
        return {
            'score': score,
            'decision': decision,
            'checks': checks,
            'reasons': reasons,
            'llm_used': False,
            'threshold': self.threshold,
            'confidence_threshold': self.confidence_threshold
        }
    
    def _check_syntax(self, improvement: Dict) -> Dict:
        """Check if code has valid syntax."""
        if not improvement.get('script'):
            return {'score': 1.0, 'reason': 'No code to check', 'status': 'pass'}
        
        script_name = improvement.get('script')
        if isinstance(script_name, str):
            script_path = SCRIPTS_DIR / script_name
        else:
            return {'score': 0.5, 'reason': 'Invalid script reference', 'status': 'warn'}
        
        if not script_path.exists():
            return {'score': 0.0, 'reason': f'Script not found: {script_name}', 'status': 'fail'}
        
        try:
            code = script_path.read_text()
            compile(code, str(script_path), 'exec')
            return {'score': 1.0, 'reason': 'Syntax OK', 'status': 'pass'}
        except SyntaxError as e:
            return {'score': 0.0, 'reason': f'Syntax error at line {e.lineno}', 'status': 'fail'}
        except Exception as e:
            return {'score': 0.3, 'reason': f'Compile error: {str(e)[:30]}', 'status': 'fail'}
    
    def _check_logic(self, improvement: Dict) -> Dict:
        """Check for obvious logic errors."""
        script_name = improvement.get('script')
        if not script_name:
            return {'score': 0.7, 'reason': 'No code to analyze', 'status': 'pass'}
        
        try:
            script_path = SCRIPTS_DIR / script_name
            if not script_path.exists():
                return {'score': 0.5, 'reason': 'Script not found', 'status': 'warn'}
            
            code = script_path.read_text()
            issues = []
            
            # Check for empty except blocks
            except_blocks = re.findall(r'except.*?:\s*\n\s*(?:\n|pass|...|# NOOP)', code, re.DOTALL)
            if except_blocks:
                issues.append(f'Empty except block ({len(except_blocks)})')
            
            # Check for potential infinite loops
            if 'while True' in code and 'break' not in code:
                issues.append('Potential infinite loop')
            
            # Check for bare except
            if 'except:' in code and 'Exception' not in code:
                # Check if there's proper exception handling nearby
                if not re.search(r'except\s*\(\s*Exception', code):
                    issues.append('Bare except without specific exceptions')
            
            # Check for unreachable code
            if 'return' in code:
                # Simple check for code after return
                lines = code.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().startswith('return '):
                        # Check if there's significant code after
                        after = '\n'.join(lines[i+1:]).strip()
                        if after and not after.startswith('#'):
                            # Non-comment code after return
                            if len(after) > 20:  # More than just whitespace
                                issues.append(f'Unreachable code after return (line {i+1})')
            
            # Check for obvious recursion without base case
            func_names = re.findall(r'def\s+(\w+)\s*\(', code)
            for name in func_names:
                # Count recursive calls in function
                func_pattern = rf'def\s+{name}\s*\([^)]*\):(.*?)(?=\ndef\s|\Z)'
                match = re.search(func_pattern, code, re.DOTALL)
                if match:
                    func_body = match.group(1)
                    recursive_calls = len(re.findall(rf'\b{name}\s*\(', func_body))
                    if recursive_calls > 0 and 'if' not in func_body[:50]:
                        issues.append(f'Potential recursion without base case: {name}')
            
            if issues:
                return {'score': 0.3, 'reason': '; '.join(issues[:2]), 'status': 'fail'}
            return {'score': 0.9, 'reason': 'No obvious logic errors', 'status': 'pass'}
        
        except Exception as e:
            return {'score': 0.5, 'reason': f'Logic check error: {str(e)[:30]}', 'status': 'warn'}
    
    def _check_expected_impact(self, improvement: Dict, context: Dict) -> Dict:
        """Check if improvement actually addresses the issue."""
        issue_desc = (context.get('issue_description', '') or '').lower()
        improvement_desc = (improvement.get('title', '') or '').lower()
        improvement_type = (improvement.get('type', '') or '').lower()
        
        if not issue_desc:
            return {'score': 0.5, 'reason': 'No issue context available', 'status': 'warn'}
        
        # Keyword matching
        issue_keywords = set(issue_desc.split())
        improvement_keywords = set(improvement_desc.split())
        
        # Remove stopwords
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'fix', 'issue', 'problem'}
        issue_keywords -= stopwords
        improvement_keywords -= stopwords
        
        overlap = len(issue_keywords & improvement_keywords)
        total = len(issue_keywords)
        
        if total == 0:
            overlap_score = 0.5
        else:
            overlap_score = overlap / total
        
        # Type matching bonus
        type_bonus = 0.0
        if improvement_type and improvement_type in issue_desc:
            type_bonus = 0.1
        
        score = min(1.0, overlap_score + type_bonus)
        reason = f'{overlap}/{total} keywords match'
        if type_bonus > 0:
            reason += f', type bonus +{type_bonus:.1f}'
        
        if score < 0.3:
            status = 'fail'
        elif score < 0.6:
            status = 'warn'
        else:
            status = 'pass'
        
        return {'score': score, 'reason': reason, 'status': status}
    
    def _check_history(self, improvement: Dict) -> Dict:
        """Check if similar improvement worked before."""
        idea_bank = load_idea_bank()
        ideas = idea_bank.get('ideas', [])
        
        if not ideas:
            return {'score': 0.6, 'reason': 'No history available', 'status': 'pass'}
        
        # Find similar past attempts
        improvement_title = improvement.get('title', '')
        similar = [i for i in ideas if similarity(i.get('title', ''), improvement_title) > 0.4]
        
        if not similar:
            return {'score': 0.6, 'reason': 'No similar past attempts', 'status': 'pass'}
        
        # Check outcomes of similar attempts
        failures = [i for i in similar if 'validation failed' in i.get('why_ineffective', '').lower()]
        successes = [i for i in similar if 'validation' in i.get('why_ineffective', '').lower()]
        
        if len(similar) >= 3 and len(failures) / len(similar) > 0.7:
            # High failure rate for similar attempts
            return {
                'score': 0.15,
                'reason': f'{len(failures)}/{len(similar)} similar attempts failed',
                'status': 'fail'
            }
        elif len(failures) > 0 and len(successes) == 0:
            return {
                'score': 0.3,
                'reason': f'{len(failures)} similar failures, no successes',
                'status': 'fail'
            }
        
        return {
            'score': 0.7,
            'reason': f'History mixed ({len(successes)} success, {len(failures)} fail)',
            'status': 'pass'
        }
    
    def _check_risk(self, improvement: Dict) -> Dict:
        """Assess risk of making things worse."""
        script_name = improvement.get('script')
        if not script_name:
            return {'score': 0.8, 'reason': 'No code to assess', 'status': 'pass'}
        
        try:
            script_path = SCRIPTS_DIR / script_name
            if not script_path.exists():
                return {'score': 0.5, 'reason': 'Script not found', 'status': 'warn'}
            
            code = script_path.read_text().lower()
            risks = []
            
            # High-risk operations
            risky_keywords = [
                ('delete', 'deletion'),
                ('drop', 'dropping'),
                ('truncate', 'truncation'),
                ('remove(', 'removing'),
                ('rm ', 'shell rm'),
                ('kill', 'process termination'),
                ('shutdown', 'system shutdown'),
                ('exit(', 'system exit'),
                ('sys.exit', 'system exit')
            ]
            
            for keyword, description in risky_keywords:
                if keyword in code:
                    # Check it's not in a comment
                    for line in code.split('\n'):
                        if keyword in line and not line.strip().startswith('#'):
                            risks.append(description)
                            break
            
            # Check for external system modifications
            external_patterns = [
                (r'urllib\.request', 'external network'),
                (r'requests\.', 'external network'),
                (r'subprocess\.call', 'subprocess call'),
                (r'subprocess\.run.*shell\s*=\s*True', 'shell command'),
            ]
            
            for pattern, description in external_patterns:
                if re.search(pattern, code):
                    risks.append(description)
            
            if len(risks) > 2:
                return {'score': 0.2, 'reason': f'Multiple risks: {risks[:3]}', 'status': 'fail'}
            elif risks:
                return {'score': 0.5, 'reason': f'Risks: {risks}', 'status': 'warn'}
            
            return {'score': 0.9, 'reason': 'Low risk operations only', 'status': 'pass'}
        
        except Exception as e:
            return {'score': 0.5, 'reason': f'Risk check error: {str(e)[:30]}', 'status': 'warn'}
    
    def _generate_reasons(self, checks: Dict, score: float, decision: str) -> List[str]:
        """Generate human-readable reasons for the evaluation."""
        reasons = []
        
        # Add failing check reasons first
        for check_name, check_result in checks.items():
            if check_result.get('status') == 'fail':
                reasons.append(f"[{check_name.upper()}] {check_result['reason']}")
        
        # Add top reasons
        if not reasons:
            reasons.append(f"All checks passed (score: {score:.2f})")
        
        # Add decision hint
        if decision == 'proceed':
            reasons.append("Ready for validation")
        elif decision == 'revise':
            reasons.append("Should revise before validation")
        else:
            reasons.append("Too risky - recommend skip")
        
        return reasons
    
    def record_outcome(self, decision: str, validation_passed: bool):
        """Record validation outcome for future self-evaluation improvement."""
        if decision == 'proceed' or decision == 'revise':
            if validation_passed:
                self.stats['validation_outcomes']['success'] += 1
            else:
                self.stats['validation_outcomes']['failure'] += 1
    
    def get_accuracy(self) -> float:
        """Calculate self-eval accuracy (% of proceed decisions that passed validation)."""
        total = self.stats['validation_outcomes']['success'] + self.stats['validation_outcomes']['failure']
        if total == 0:
            return 0.0
        return self.stats['validation_outcomes']['success'] / total
    
    def get_stats(self) -> Dict:
        """Get self-evaluator statistics."""
        total = self.stats['total_evaluated']
        if total == 0:
            return self.stats.copy()
        
        return {
            **self.stats,
            'accuracy': self.get_accuracy(),
            'decision_rates': {
                'proceed': self.stats['proceed'] / total,
                'revise': self.stats['revise'] / total,
                'skip': self.stats['skip'] / total,
            }
        }

    def evaluate_with_llm(self, improvement: Dict, context: Dict) -> Dict:
        """
        LLM-based self-evaluation (Phase 8 upgrade).
        
        Uses the LLM to evaluate the improvement before validation.
        This is more nuanced than rule-based checks because:
        - Understands semantic meaning
        - Can spot subtle logic issues
        - Evaluates "does this actually solve the problem?"
        
        Based on Self-Rewarding LM (Yuan et al., 2025):
        - Model evaluates its own outputs
        - Uses internal understanding, not just pattern matching
        
        Args:
            improvement: The improvement to evaluate
            context: Context including issue description
        
        Returns:
            Dict with score (0-1), decision, and reasoning
        """
        # Check if LLM is available
        try:
            import urllib.request
            import urllib.error
        except ImportError:
            return {
                'score': 0.5,
                'decision': 'proceed',
                'reasoning': 'LLM not available, using rule-based',
                'llm_used': False
            }
        
        # Get LLM API key
        secrets = {}
        try:
            secrets_path = Path("/home/clawbot/.openclaw/secrets.env")
            if secrets_path.exists():
                for line in secrets_path.read_text().split('\n'):
                    if '=' in line and not line.startswith('#'):
                        k, v = line.split('=', 1)
                        secrets[k] = v
        except:
            pass
        
        api_key = secrets.get('MINIMAX_API_KEY', os.environ.get('MINIMAX_API_KEY', ''))
        if not api_key:
            return {
                'score': 0.5,
                'decision': 'proceed',
                'reasoning': 'No API key available',
                'llm_used': False
            }
        
        # Build prompt
        issue = context.get('issue_description', 'Unknown issue')
        title = improvement.get('title', 'Untitled')
        description = improvement.get('description', '')
        script = improvement.get('script', 'No script')
        
        # Try to read the script content
        script_content = ''
        if script and script != 'No script':
            try:
                script_path = SCRIPTS_DIR / script
                if script_path.exists():
                    script_content = script_path.read_text()[:2000]  # First 2000 chars
            except:
                pass
        
        prompt = f"""BEWERTUNG (nur die drei Zeilen antworten, nichts anderes):

SCORE: 0.0-1.0
ENTSCHEIDUNG: PROCEED oder REVISE oder SKIP
BEGRUENDUNG: ein kurzer Satz

---

Bewerte ob dieser Verbesserungsvorschlag sinnvoll und ausführbar ist:

TITEL: {title}
ISSUE/PROBLEM: {issue}
BESCHREIBUNG: {description}

Kriterien:
- Loest dieses Script das beschriebene Problem?
- Ist die Loesungsrichtung sinnvoll?
- Risiko: Kann es das System verbessern oder verschlechtern?

Sei NICHT zu streng bei Details — der Learning Loop generiert erstmal grobe Ideen.
Bewerte die GRUNDLEGENDE SINNVOLLKEIT.
"""
        
        # Call LLM using OpenClaw's MiniMax configuration
        try:
            # Higher max_tokens to avoid truncation
            data = {
                "model": "MiniMax-M2.7",
                "max_tokens": 1000,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            req = urllib.request.Request(
                "https://api.minimax.io/anthropic/v1/messages",
                data=json.dumps(data).encode('utf-8'),
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01"
                },
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                # MiniMax returns content as array with type 'text' or 'thinking'
                content_text = ''
                for c in result.get('content', []):
                    if c.get('type') == 'text':
                        content_text = c.get('text', '')
                        break
                content = content_text
            
            # Parse response - split by lines for robustness
            lines = content.strip().split('\n')
            score = 0.5
            decision = 'proceed'
            reasoning = content[:100]
            
            for line in lines:
                line = line.strip()
                if line.startswith('SCORE:'):
                    try:
                        score = float(line.split(':')[1].strip())
                    except:
                        pass
                elif line.startswith('ENTSCHEIDUNG:'):
                    decision_raw = line.split(':')[1].strip().lower()
                    if decision_raw in ['proceed', 'revise', 'skip']:
                        decision = decision_raw
                elif line.startswith('BEGRUENDUNG') or line.startswith('BEGRÜNDUNG'):
                    # Everything after the colon is the reasoning
                    if ':' in line:
                        reasoning = line.split(':', 1)[1].strip()
            
            return {
                'score': min(1.0, max(0.0, score)),
                'decision': decision,
                'reasoning': reasoning[:200],
                'llm_used': True
            }
                
        except Exception as e:
            return {
                'score': 0.5,
                'decision': 'proceed',
                'reasoning': f'LLM call failed: {str(e)[:50]}',
                'llm_used': False
            }

    def evaluate_code(self, code: str, context: Dict) -> Dict:
        """
        LLM-based evaluation of actual CODE (Phase 8 Option B).
        
        This is called AFTER script generation to evaluate the real code.
        Much more effective than evaluating ideas because:
        - Sees actual implementation
        - Can spot bugs, logic errors
        - Understands what the code actually does
        
        Args:
            code: The actual Python code to evaluate
            context: Context including issue description
        
        Returns:
            Dict with score (0-1), decision, and reasoning
        """
        # Check if LLM is available
        try:
            import urllib.request
            import urllib.error
        except ImportError:
            return {
                'score': 0.5,
                'decision': 'proceed',
                'reasoning': 'LLM not available',
                'llm_used': False
            }
        
        # Get API key
        secrets = {}
        try:
            secrets_path = Path("/home/clawbot/.openclaw/secrets.env")
            if secrets_path.exists():
                for line in secrets_path.read_text().split('\n'):
                    if '=' in line and not line.startswith('#'):
                        k, v = line.split('=', 1)
                        secrets[k] = v
        except:
            pass
        
        api_key = secrets.get('MINIMAX_API_KEY', os.environ.get('MINIMAX_API_KEY', ''))
        if not api_key:
            return {
                'score': 0.5,
                'decision': 'proceed',
                'reasoning': 'No API key available',
                'llm_used': False
            }
        
        issue = context.get('issue_description', 'Unknown issue')
        
        # Truncate code if too long
        code_snippet = code[:3000] if len(code) > 3000 else code
        
        prompt = f"""BEWERTUNG (nur die drei Zeilen antworten, nichts anderes):

SCORE: 0.0-1.0
ENTSCHEIDUNG: PROCEED oder REVISE oder SKIP
BEGRUENDUNG: ein kurzer Satz

---

Bewerte diesen Python Code:

```python
{code_snippet}
```

ISSUE/PROBLEM DAS GELOEST WERDEN SOLL:
{issue}

Kriterien:
- Korrigiert dieser Code das beschriebene Problem?
- Sind Logik und Syntax korrekt?
- Kann dieser Code das System verbessern?

Sei fair aber kritisch. Approve wenn der Code das Problem addressiert.
"""
        
        # Call LLM
        try:
            data = {
                "model": "MiniMax-M2.7",
                "max_tokens": 1000,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            req = urllib.request.Request(
                "https://api.minimax.io/anthropic/v1/messages",
                data=json.dumps(data).encode('utf-8'),
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01"
                },
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode('utf-8'))
                content_text = ''
                for c in result.get('content', []):
                    if c.get('type') == 'text':
                        content_text = c.get('text', '')
                        break
                content = content_text
            
            # Parse response - split by lines for robustness
            lines = content.strip().split('\n')
            score = 0.5
            decision = 'proceed'
            reasoning = content[:100]
            
            for line in lines:
                line = line.strip()
                if line.startswith('SCORE:'):
                    try:
                        score = float(line.split(':')[1].strip())
                    except:
                        pass
                elif line.startswith('ENTSCHEIDUNG:'):
                    decision_raw = line.split(':')[1].strip().lower()
                    if decision_raw in ['proceed', 'revise', 'skip']:
                        decision = decision_raw
                elif line.startswith('BEGRUENDUNG') or line.startswith('BEGRÜNDUNG'):
                    if ':' in line:
                        reasoning = line.split(':', 1)[1].strip()
            
            return {
                'score': min(1.0, max(0.0, score)),
                'decision': decision,
                'reasoning': reasoning[:200],
                'llm_used': True
            }
                
        except Exception as e:
            return {
                'score': 0.5,
                'decision': 'proceed',
                'reasoning': f'LLM call failed: {str(e)[:50]}',
                'llm_used': False
            }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Self-Evaluator for Learning Loop")
    subparsers = parser.add_subparsers(dest="command")
    
    # Evaluate command
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate an improvement")
    eval_parser.add_argument("--improvement", required=True, help="JSON improvement file")
    eval_parser.add_argument("--context", default="{}", help="JSON context object")
    
    # Stats command
    subparsers.add_parser("stats", help="Show evaluator statistics")
    
    args = parser.parse_args()
    
    if args.command == "evaluate":
        improvement = json.loads(args.improvement) if isinstance(args.improvement, str) else args.improvement
        context = json.loads(args.context) if isinstance(args.context, str) else args.context
        
        evaluator = SelfEvaluator()
        result = evaluator.evaluate(improvement, context)
        
        print(f"Self-Evaluation Result:")
        print(f"  Score: {result['score']:.2f}")
        print(f"  Decision: {result['decision'].upper()}")
        print(f"  Threshold: {result['threshold']}")
        print(f"  Confidence Threshold: {result['confidence_threshold']}")
        print()
        print("Checks:")
        for check_name, check_result in result['checks'].items():
            status_icon = {'pass': '✅', 'warn': '⚠️', 'fail': '❌'}.get(check_result.get('status'), '?')
            print(f"  {status_icon} {check_name}: {check_result['score']:.2f} - {check_result['reason']}")
        print()
        print("Reasons:")
        for reason in result['reasons']:
            print(f"  - {reason}")
    
    elif args.command == "stats":
        evaluator = SelfEvaluator()
        stats = evaluator.get_stats()
        print("Self-Evaluator Statistics:")
        print(f"  Total Evaluated: {stats['total_evaluated']}")
        print(f"  Decisions: proceed={stats['proceed']}, revise={stats['revise']}, skip={stats['skip']}")
        if stats['total_evaluated'] > 0:
            print(f"  Decision Rates:")
            for k, v in stats['decision_rates'].items():
                print(f"    {k}: {v:.1%}")
        print(f"  Accuracy: {stats['accuracy']:.1%}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
