# 🚀 Self-Reward Pattern — Phase 6 Implementation Plan

**Erstellt:** 2026-04-17 10:35 UTC  
**Status:** 🔴 PRIORITÄT  
**Erwartete Impact:** 🟢 HOCH — Weniger Validation Failures, schnelleres Lernen

---

## 📋 EXECUTIVE SUMMARY

**Problem:**
- System schickt Improvements zur Validation ohne eigene Bewertung
- Bei 2/3 failed Tests wird der Score reduziert
- Viele failures sind vermeidbar wenn das System vorher self-check macht

**Lösung:**
- **Self-Reward**: System bewertet eigenen Output VOR Validation
- Wenn self-score < threshold → Improvement ablehnen oder überarbeiten
- Wenn self-score >= threshold → zur Validation schicken

---

## 🔬 RESEARCH SUMMARY

### Self-Rewarding Language Models (Yuan et al., 2025)
- Model bewertet eigene Outputs und nutzt Scores als Reward Signal
- RLHF ohne separate Reward Model
- Verbessert internale Bewertungsfähigkeit über Zeit

### Self-Consistency (Wang et al., 2022)
- Multiple reasoning chains samplen
- Majority vote für finale Antwort
- Passive Verbesserung der Zuverlässigkeit

### Reflexion (Shinn et al., 2023)
- Verbal feedback loop
- Agent sieht Feedback und korrigiert sich
- Reflection wird vorher angewendet, nicht nachher

---

## 📊 DESIGN FÜR SIR HAZECLAW

### Architektur

```
┌─────────────────────────────────────────────────────────────┐
│                      SELF-REWARD PATTERN                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Improvement selected → Self-Evaluation → Decision          │
│                              │                              │
│                    ┌─────────▼─────────┐                    │
│                    │ Self-Score Check │                    │
│                    │  - Syntax OK?     │                    │
│                    │  - Logic OK?       │                    │
│                    │  - Expected Impact? │                    │
│                    └─────────┬─────────┘                    │
│                              │                              │
│         ┌────────────────────┼────────────────────┐          │
│         │                    │                    │          │
│    Score >= THRESHOLD   Score < THRESHOLD       │          │
│         │                    │                    │          │
│         ▼                    ▼                    │          │
│  Send to Validation   Revise / Retry             │          │
│                              │                    │          │
│                    ┌─────────▼─────────┐          │          │
│                    │  Still low?      │          │          │
│                    └─────────┬─────────┘          │          │
│                              │                    │          │
│                    ┌─────────┴─────────┐        │          │
│                    │                    │        │          │
│               Yes  │                 No │        │          │
│                    ▼                    ▼        │          │
│           Send anyway      Skip (too risky)      │          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Self-Evaluation Criteria

| Criterion | Weight | Check |
|-----------|--------|-------|
| **Syntax Valid** | 20% | Python syntax check, no import errors |
| **Logic Valid** | 25% | No obvious logic errors, dead code |
| **Expected Impact** | 25% | Does this actually address the issue? |
| **History Check** | 20% | Has this worked before in similar contexts? |
| **Risk Assessment** | 10% | Could this make things worse? |

### Thresholds

```python
SELF_REWARD_THRESHOLD = 0.7  # Minimum score to proceed
SELF_REWARD_CONFIDENCE = 0.5  # If below this, skip without trying
```

---

## 📋 IMPLEMENTATION DETAIL

### Phase 1: Self-Evaluator Script

```python
# self_evaluator.py

class SelfEvaluator:
    """
    Pre-validation self-scoring for improvements.
    
    Based on:
    - Self-Rewarding LM (Yuan 2025)
    - Self-Consistency (Wang 2022)
    """
    
    def __init__(self):
        self.threshold = 0.7
        self.confidence_threshold = 0.5
    
    def evaluate(self, improvement: dict, context: dict) -> dict:
        """
        Evaluate an improvement before sending to validation.
        
        Returns:
            {
                'score': 0.0-1.0,
                'decision': 'proceed' | 'revise' | 'skip',
                'reasons': [...],
                'checks': {...}
            }
        """
        checks = {
            'syntax': self._check_syntax(improvement),
            'logic': self._check_logic(improvement),
            'impact': self._check_expected_impact(improvement, context),
            'history': self._check_history(improvement),
            'risk': self._check_risk(improvement)
        }
        
        # Weighted score
        weights = {'syntax': 0.20, 'logic': 0.25, 'impact': 0.25, 'history': 0.20, 'risk': 0.10}
        score = sum(checks[k]['score'] * weights[k] for k in weights)
        
        # Decision
        if score >= self.threshold:
            decision = 'proceed'
        elif score >= self.confidence_threshold:
            decision = 'revise'
        else:
            decision = 'skip'
        
        return {
            'score': score,
            'decision': decision,
            'checks': checks,
            'reasons': self._generate_reasons(checks)
        }
    
    def _check_syntax(self, improvement) -> dict:
        """Check if code has valid syntax."""
        if not improvement.get('script'):
            return {'score': 1.0, 'reason': 'No code to check'}
        
        script_path = SCRIPTS_DIR / improvement['script']
        if not script_path.exists():
            return {'score': 0.0, 'reason': 'Script file not found'}
        
        try:
            compile(script_path.read_text(), str(script_path), 'exec')
            return {'score': 1.0, 'reason': 'Syntax OK'}
        except SyntaxError as e:
            return {'score': 0.0, 'reason': f'Syntax error: {e}'}
    
    def _check_logic(self, improvement) -> dict:
        """Check for obvious logic errors."""
        # Rule-based checks
        issues = []
        
        # Check for empty except blocks
        if 'except:' in improvement.get('code', ''):
            if 'pass' in improvement.get('code', ''):
                issues.append('Empty except block detected')
        
        # Check for obvious infinite loops
        code = improvement.get('code', '')
        if 'while True' in code and 'break' not in code:
            issues.append('Potential infinite loop')
        
        if issues:
            return {'score': 0.3, 'reason': '; '.join(issues)}
        return {'score': 0.9, 'reason': 'No obvious logic errors'}
    
    def _check_expected_impact(self, improvement, context) -> dict:
        """Check if improvement actually addresses the issue."""
        issue_desc = context.get('issue_description', '').lower()
        improvement_desc = improvement.get('title', '').lower()
        
        # Simple keyword matching
        issue_keywords = set(issue_desc.split())
        improvement_keywords = set(improvement_desc.split())
        
        overlap = len(issue_keywords & improvement_keywords)
        total = len(issue_keywords)
        
        if total == 0:
            return {'score': 0.5, 'reason': 'Cannot assess impact'}
        
        overlap_ratio = overlap / total
        return {
            'score': max(0.1, overlap_ratio),
            'reason': f'{overlap}/{total} keywords match'
        }
    
    def _check_history(self, improvement) -> dict:
        """Check if similar improvement worked before."""
        # Check idea bank for past attempts
        idea_bank = load_idea_bank()
        similar = [i for i in idea_bank.get('ideas', [])
                   if self._similarity(i.get('title', ''), improvement.get('title', '')) > 0.5]
        
        if not similar:
            return {'score': 0.6, 'reason': 'No history available'}
        
        # Check if similar failed before
        failures = [i for i in similar if 'validation failed' in i.get('why_ineffective', '').lower()]
        if failures:
            return {'score': 0.2, 'reason': f'{len(failures)} similar attempts failed'}
        
        return {'score': 0.8, 'reason': 'History looks positive'}
    
    def _check_risk(self, improvement) -> dict:
        """Assess risk of making things worse."""
        risky_keywords = ['delete', 'drop', 'truncate', 'remove all', 'kill']
        code = improvement.get('code', '').lower()
        
        risks = [kw for kw in risky_keywords if kw in code]
        if risks:
            return {'score': 0.3, 'reason': f'Risky keywords: {risks}'}
        return {'score': 0.9, 'reason': 'Low risk'}
```

### Phase 2: Integration in Learning Loop

In `validation_gate()` VOR dem actual validation:

```python
# PHASE 6: Self-Reward Check
self_evaluator = SelfEvaluator()
eval_result = self_evaluator.evaluate(improvement, context)

print(f"   🎯 Self-Score: {eval_result['score']:.2f} [{eval_result['decision']}]")

if eval_result['decision'] == 'skip':
    print(f"      ⏭️ Skipping: too risky (score {eval_result['score']:.2f} < {SELF_REWARD_CONFIDENCE})")
    # Mark as failed without validation
    return False, {'self_eval_skipped': True, 'reason': eval_result['reasons']}

if eval_result['decision'] == 'revise':
    print(f"      🔄 Attempting revision based on self-eval...")
    # Try to fix issues identified by self-evaluator
    improvement = self._revise_based_on_feedback(improvement, eval_result)
```

---

## 🎯 EXPECTED OUTCOMES

| Metric | Current | Expected |
|--------|---------|----------|
| Validation Success Rate | ~97% (200/205) | 98%+ |
| Failed Validations | ~5 per 205 | <3 per 205 |
| Score | 0.762 | 0.78+ |
| Idea Bank Growth | +30 entries/day | +10 entries/day |

---

## ⚠️ RISKS & MITIGATIONS

| Risk | Severity | Mitigation |
|------|----------|------------|
| Self-evaluator too strict | MEDIUM | Threshold adjustable, can be bypassed |
| False negatives (good ideas rejected) | MEDIUM | Always can proceed anyway |
| Computation overhead | LOW | Lightweight checks only |

---

## 📊 METRICS TO TRACK

- `self_eval_score_avg`: Average self-evaluation score
- `self_eval_decisions`: Distribution of proceed/revise/skip
- `self_eval_accuracy`: Did proceed decisions correlate with validation success?
- `self_eval_improvement`: Score change after implementing self-reward

---

## 🔗 REFERENCES

- Self-Rewarding Language Models (Yuan et al., 2025)
- Self-Consistency (Wang et al., 2022)
- Reflexion (Shinn et al., 2023)
- Better Ways to Build Self-Improving AI Agents (Nakajima, 2025)

---

_Letzte Aktualisierung: 2026-04-17 10:35 UTC_
_Sir HazeClaw — Phase 6 Self-Reward Plan_
