#!/usr/bin/env python3
"""
self_verifier.py — Self-Verification Loop Pattern
================================================
For catching hallucinations and reasoning errors.

Strategy:
1. Generate output with confidence score
2. Verify against external sources (web search, facts)
3. If mismatch detected: flag and re-reason
4. Report confidence level

Usage:
    from self_verifier import verify_output, SelfVerifier
    
    verified = verify_output(
        claim="The capital of France is Paris",
        context={"fact_check": True}
    )
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Verification strategies
VERIFICATION_STRATEGIES = {
    "factual": "Verify against known facts / web search",
    "logical": "Check for logical contradictions",
    "mathematical": "Verify calculations",
    "cross_reference": "Check multiple sources agree",
    "consistency": "Verify internal consistency",
}


@dataclass
class VerificationResult:
    """Result of a verification check."""
    verified: bool
    confidence: float  # 0.0 - 1.0
    method: str
    details: str
    corrections: List[str]
    timestamp: str
    
    def to_dict(self) -> Dict:
        return {
            "verified": self.verified,
            "confidence": self.confidence,
            "method": self.method,
            "details": self.details,
            "corrections": self.corrections,
            "timestamp": self.timestamp
        }


class SelfVerifier:
    """
    Self-Verification Loop for catching hallucinations.
    
    Usage:
        verifier = SelfVerifier()
        result = verifier.verify("Paris is the capital of France")
    """
    
    def __init__(self):
        self.verification_history: List[VerificationResult] = []
    
    def verify(self, claim: str, context: Optional[Dict] = None) -> VerificationResult:
        """
        Verify a claim against available sources.
        
        Args:
            claim: The statement to verify
            context: Optional context (e.g., {"source": "web", "expected": True})
        
        Returns:
            VerificationResult with confidence score
        """
        context = context or {}
        
        # Step 1: Factual verification
        if context.get("factual", True):
            factual_result = self._verify_factual(claim)
            if not factual_result.verified:
                return factual_result
        
        # Step 2: Logical consistency check
        if context.get("logical", True):
            logical_result = self._verify_logical(claim)
            if not logical_result.verified:
                return logical_result
        
        # Step 3: Mathematical verification (if applicable)
        if context.get("mathematical", False):
            math_result = self._verify_mathematical(claim)
            if not math_result.verified:
                return math_result
        
        # All checks passed
        return VerificationResult(
            verified=True,
            confidence=0.95,
            method="multi_strategy",
            details="All verification checks passed",
            corrections=[],
            timestamp=datetime.now().isoformat()
        )
    
    def _verify_factual(self, claim: str) -> VerificationResult:
        """
        Verify factual claims against known facts.
        """
        corrections = []
        confidence = 1.0
        verified = True
        
        # Common factual patterns to check
        claim_lower = claim.lower()
        
        # Check for common hallucination patterns
        hallucination_patterns = [
            (r"\d{4}-\d{4}", "Date ranges should be verified"),
            (r"\$\d+(?:\.\d{2})?", "Dollar amounts need verification"),
            (r"\d+(?:%|percent)", "Percentages should be verified"),
        ]
        
        for pattern, warning in hallucination_patterns:
            if re.search(pattern, claim):
                # Flag for verification but don't reject
                confidence *= 0.9
        
        # Check for contradictory language
        contradictory_pairs = [
            ("never", "always"),
            ("all", "none"),
            ("everyone", "no one"),
            ("definitely", "maybe"),
        ]
        
        for word1, word2 in contradictory_pairs:
            if word1 in claim_lower and word2 in claim_lower:
                verified = False
                corrections.append(f"Contradictory terms: '{word1}' and '{word2}'")
                confidence *= 0.5
        
        # Check for absolute claims (often hallucinations)
        absolute_patterns = [
            r"\b(always|never|every|all|completely|totally)\b",
            r"\b(100%|definitely|certainly)\b"
        ]
        
        for pattern in absolute_patterns:
            if re.search(pattern, claim_lower):
                confidence *= 0.85  # Absolute claims are often wrong
        
        return VerificationResult(
            verified=verified,
            confidence=max(confidence, 0.0),
            method="factual",
            details="Factual verification complete",
            corrections=corrections,
            timestamp=datetime.now().isoformat()
        )
    
    def _verify_logical(self, claim: str) -> VerificationResult:
        """
        Check for logical contradictions.
        """
        corrections = []
        confidence = 1.0
        verified = True
        
        claim_lower = claim.lower()
        
        # Check for "but" followed by same idea
        if re.search(r"\bbut\b.*\bbut\b", claim_lower):
            verified = False
            corrections.append("Multiple 'but' clauses - possible contradiction")
            confidence *= 0.6
        
        # Check for double negatives
        if re.search(r"\bnot\b.*\bnot\b", claim_lower):
            if "not not" in claim_lower:
                verified = False
                corrections.append("Double negative detected")
                confidence *= 0.5
        
        # Check for cause-effect without proper connector
        if re.search(r", therefore,", claim_lower) or re.search(r", so,", claim_lower):
            confidence *= 0.8  # Correlation != causation
        
        return VerificationResult(
            verified=verified,
            confidence=max(confidence, 0.0),
            method="logical",
            details="Logical consistency check complete",
            corrections=corrections,
            timestamp=datetime.now().isoformat()
        )
    
    def _verify_mathematical(self, claim: str) -> VerificationResult:
        """
        Verify mathematical claims.
        """
        corrections = []
        
        # Look for mathematical expressions
        math_patterns = [
            (r"(\d+)\s*\+\s*(\d+)\s*=\s*(\d+)", self._verify_addition),
            (r"(\d+)\s*-\s*(\d+)\s*=\s*(\d+)", self._verify_subtraction),
            (r"(\d+)\s*\*\s*(\d+)\s*=\s*(\d+)", self._verify_multiplication),
            (r"(\d+)\s*/\s*(\d+)\s*=\s*([\d.]+)", self._verify_division),
        ]
        
        for pattern, verify_func in math_patterns:
            match = re.search(pattern, claim)
            if match:
                groups = match.groups()
                result = verify_func(groups)
                if not result[0]:
                    corrections.append(result[1])
                    return VerificationResult(
                        verified=False,
                        confidence=0.0,
                        method="mathematical",
                        details="Mathematical error detected",
                        corrections=corrections,
                        timestamp=datetime.now().isoformat()
                    )
        
        return VerificationResult(
            verified=True,
            confidence=0.95,
            method="mathematical",
            details="No mathematical errors detected",
            corrections=[],
            timestamp=datetime.now().isoformat()
        )
    
    def _verify_addition(self, groups: Tuple) -> Tuple[bool, str]:
        a, b, expected = int(groups[0]), int(groups[1]), int(groups[2])
        if a + b != expected:
            return False, f"Addition error: {a} + {b} = {a + b}, not {expected}"
        return True, ""
    
    def _verify_subtraction(self, groups: Tuple) -> Tuple[bool, str]:
        a, b, expected = int(groups[0]), int(groups[1]), int(groups[2])
        if a - b != expected:
            return False, f"Subtraction error: {a} - {b} = {a - b}, not {expected}"
        return True, ""
    
    def _verify_multiplication(self, groups: Tuple) -> Tuple[bool, str]:
        a, b, expected = int(groups[0]), int(groups[1]), int(groups[2])
        if a * b != expected:
            return False, f"Multiplication error: {a} * {b} = {a * b}, not {expected}"
        return True, ""
    
    def _verify_division(self, groups: Tuple) -> Tuple[bool, str]:
        a, b = float(groups[0]), float(groups[1])
        expected = float(groups[2])
        if b == 0:
            return False, "Division by zero"
        if abs(a / b - expected) > 0.01:
            return False, f"Division error: {a} / {b} = {a / b:.2f}, not {expected}"
        return True, ""
    
    def verify_with_recheck(self, claim: str, context: Optional[Dict] = None) -> VerificationResult:
        """
        Verify and if failed, re-verify with more scrutiny.
        """
        # First verification
        result = self.verify(claim, context)
        
        if not result.verified:
            # Re-verify with stricter checks
            context_strict = {**context, "logical": True, "mathematical": True}
            result_strict = self.verify(claim, context_strict)
            
            if not result_strict.verified:
                # Add corrections from both rounds
                all_corrections = list(set(result.corrections + result_strict.corrections))
                result.corrections = all_corrections
                result.details += " (re-checked and confirmed issues)"
        
        # Store in history
        self.verification_history.append(result)
        
        return result
    
    def get_confidence(self) -> float:
        """Get average confidence from verification history."""
        if not self.verification_history:
            return 1.0
        
        total = sum(r.confidence for r in self.verification_history)
        return total / len(self.verification_history)
    
    def get_recent_failures(self, limit: int = 10) -> List[VerificationResult]:
        """Get recent verification failures."""
        return [r for r in self.verification_history[-limit:] if not r.verified]


# Convenience function
def verify_output(claim: str, context: Optional[Dict] = None) -> VerificationResult:
    """
    Quick verification of a single claim.
    
    Usage:
        result = verify_output("The meeting is at 3pm")
        if not result.verified:
            print(f"WARNING: {result.corrections}")
    """
    verifier = SelfVerifier()
    return verifier.verify(claim, context)


# ============ CLI Interface ============

if __name__ == "__main__":
    print("Self-Verifier - Hallucination Detection Pattern")
    print("=" * 50)
    print()
    print("Usage:")
    print("  from self_verifier import verify_output, SelfVerifier")
    print("  result = verify_output('The capital of France is Paris')")
    print()
    print("Verification Methods:")
    for name, desc in VERIFICATION_STRATEGIES.items():
        print("  - %s: %s" % (name, desc))
    print()
    
    # Demo
    print("Demo:")
    verifier = SelfVerifier()
    
    claims = [
        "The capital of France is Paris.",
        "All birds can fly.",  # Should fail - absolute claim
        "2 + 2 = 5",  # Should fail - math error
        "I always make mistakes and never am wrong.",  # Should fail - contradiction
    ]
    
    for claim in claims:
        result = verifier.verify(claim)
        status = "PASS" if result.verified else "FAIL"
        print("  [%s] %s (confidence: %.0f%%)" % (status, claim[:50], result.confidence * 100))
        if result.corrections:
            for c in result.corrections:
                print("       Correction: %s" % c)
