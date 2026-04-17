#!/usr/bin/env python3
"""
Cross-Pattern Recognition & Validation Script
Real Error Rate Analysis Tool
"""

import random
import math
import time
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import sys


class ErrorStatus(Enum):
    """Error status enumeration."""
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Pattern:
    """Represents a data pattern for analysis."""
    id: int
    features: List[float]
    label: str
    confidence: float = 0.0
    
    def __post_init__(self):
        if not self.features:
            raise ValueError("Features cannot be empty")


@dataclass
class ValidationResult:
    """Result of pattern validation."""
    pattern_id: int
    predicted_label: str
    actual_label: str
    is_correct: bool
    error_distance: float
    confidence: float
    timestamp: float = field(default_factory=time.time)


class CrossPatternAnalyzer:
    """Main analyzer for cross-pattern recognition."""
    
    def __init__(self, threshold: float = 0.75):
        self.threshold = threshold
        self.patterns: List[Pattern] = []
        self.results: List[ValidationResult] = []
        self.total_processed = 0
        self.total_errors = 0
        
    def add_pattern(self, pattern: Pattern) -> bool:
        """Add a pattern to the analyzer."""
        try:
            if not isinstance(pattern, Pattern):
                raise TypeError("Expected Pattern object")
            self.patterns.append(pattern)
            return True
        except Exception as e:
            print(f"Error adding pattern: {e}")
            return False
    
    def generate_synthetic_patterns(self, count: int) -> List[Pattern]:
        """Generate synthetic patterns for testing."""
        patterns = []
        labels = ["A", "B", "C", "D", "E"]
        
        try:
            for i in range(count):
                features = [random.uniform(0, 1) for _ in range(10)]
                label = random.choice(labels)
                pattern = Pattern(
                    id=i,
                    features=features,
                    label=label,
                    confidence=random.uniform(0.5, 1.0)
                )
                patterns.append(pattern)
            return patterns
        except Exception as e:
            print(f"Error generating patterns: {e}")
            return []
    
    def calculate_distance(self, p1: Pattern, p2: Pattern) -> float:
        """Calculate Euclidean distance between two patterns."""
        try:
            if len(p1.features) != len(p2.features):
                raise ValueError("Pattern feature dimensions must match")
            
            distance = math.sqrt(sum(
                (a - b) ** 2 for a, b in zip(p1.features, p2.features)
            ))
            return distance
        except Exception as e:
            print(f"Error calculating distance: {e}")
            return float('inf')
    
    def classify_pattern(self, pattern: Pattern) -> Tuple[str, float]:
        """Classify a pattern based on nearest neighbor."""
        try:
            if not self.patterns:
                return "UNKNOWN", 0.0
            
            min_distance = float('inf')
            nearest_label = "UNKNOWN"
            
            for ref_pattern in self.patterns:
                distance = self.calculate_distance(pattern, ref_pattern)
                if distance < min_distance:
                    min_distance = distance
                    nearest_label = ref_pattern.label
            
            confidence = max(0.0, 1.0 - (min_distance / math.sqrt(10)))
            return nearest_label, confidence
            
        except Exception as e:
            print(f"Error classifying pattern: {e}")
            return "ERROR", 0.0
    
    def validate_pattern(self, pattern: Pattern) -> ValidationResult:
        """Validate a single pattern."""
        try:
            predicted, confidence = self.classify_pattern(pattern)
            is_correct = predicted == pattern.label
            error_distance = self.calculate_distance(
                pattern,
                self.patterns[0] if self.patterns else pattern
            ) if not is_correct else 0.0
            
            result = ValidationResult(
                pattern_id=pattern.id,
                predicted_label=predicted,
                actual_label=pattern.label,
                is_correct=is_correct,
                error_distance=error_distance,
                confidence=confidence
            )
            
            self.results.append(result)
            self.total_processed += 1
            
            if not is_correct:
                self.total_errors += 1
            
            return result
            
        except Exception as e:
            print(f"Error validating pattern: {e}")
            raise
    
    def run_cross_validation(self, k_folds: int = 5) -> Dict:
        """Run k-fold cross validation."""
        try:
            if len(self.patterns) < k_folds:
                raise ValueError(
                    f"Need at least {k_folds} patterns for {k_folds}-fold validation"
                )
            
            fold_size = len(self.patterns) // k_folds
            fold_results = []
            
            for fold in range(k_folds):
                start_idx = fold * fold_size
                end_idx = start_idx + fold_size
                
                test_set = self.patterns[start_idx:end_idx]
                train_set = self.patterns[:start_idx] + self.patterns[end_idx:]
                
                if not train_set:
                    continue
                
                temp_analyzer = CrossPatternAnalyzer(self.threshold)
                for p in train_set:
                    temp_analyzer.add_pattern(p)
                
                fold_correct = 0
                for pattern in test_set:
                    result = temp_analyzer.validate_pattern(pattern)
                    if result.is_correct:
                        fold_correct += 1
                
                fold_accuracy = fold_correct / len(test_set) if test_set else 0
                fold_results.append({
                    'fold': fold + 1,
                    'accuracy': fold_accuracy,
                    'correct': fold_correct,
                    'total': len(test_set)
                })
            
            avg_accuracy = sum(f['accuracy'] for f in fold_results) / k_folds
            error_rate = 1.0 - avg_accuracy
            
            return {
                'folds': fold_results,
                'average_accuracy': avg_accuracy,
                'real_error_rate': error_rate * 100,
                'total_patterns': len(self.patterns)
            }
            
        except Exception as e:
            print(f"Error in cross validation: {e}")
            return {}
    
    def get_statistics(self) -> Dict:
        """Get current statistics."""
        try:
            error_rate = (
                (self.total_errors / self.total_processed * 100)
                if self.total_processed > 0 else 0.0
            )
            
            avg_confidence = (
                sum(r.confidence for r in self.results) / len(self.results)
                if self.results else 0.0
            )
            
            return {
                'total_processed': self.total_processed,
                'total_errors': self.total_errors,
                'error_rate_percent': round(error_rate, 2),
                'average_confidence': round(avg_confidence, 4),
                'total_patterns': len(self.patterns),
                'total_results': len(self.results)
            }
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}


class DataProcessor:
    """Handles data processing operations."""
    
    @staticmethod
    def normalize_features(features: List[float]) -> List[float]:
        """Normalize feature values to 0-1 range."""
        try:
            if not features:
                return []
            
            min_val = min(features)
            max_val = max(features)
            
            if max_val - min_val == 0:
                return [0.5] * len(features)
            
            return [(f - min_val) / (max_val - min_val) for f in features]
            
        except Exception as e:
            print(f"Error normalizing features: {e}")
            return features
    
    @staticmethod
    def calculate_statistics(data: List[float]) -> Dict:
        """Calculate statistical measures."""
        try:
            if not data:
                return {}
            
            sorted_data = sorted(data)
            n = len(data)
            
            mean = sum(data) / n
            variance = sum((x - mean) ** 2 for x in data) / n
            std_dev = math.sqrt(variance)
            
            median = sorted_data[n // 2] if n % 2 else (
                sorted_data[n // 2 - 1] + sorted_data[n // 2]
            ) / 2
            
            return {
                'mean': round(mean, 4),
                'median': round(median, 4),
                'std_dev': round(std_dev, 4),
                'variance': round(variance, 4),
                'min': round(min(data), 4),
                'max': round(max(data), 4),
                'count': n
            }
        except Exception as e:
            print(f"Error calculating statistics: {e}")
            return {}


def print_banner():
    """Print program banner."""
    print("\n" + "=" * 60)
    print("  CROSS-PATTERN RECOGNITION & VALIDATION TOOL")
    print("  Real Error Rate Analysis System")
    print("=" * 60)


def print_results(results: List[ValidationResult], limit: int = 10):
    """Print validation results."""
    print("\n--- Validation Results ---")
    print(f"{'ID':<6} {'Predicted':<10} {'Actual':<10} {'Correct':<8} {'Confidence':<10}")
    print("-" * 50)
    
    for result in results[:limit]:
        status = "✓" if result.is_correct else "✗"
        print(
            f"{result.pattern_id:<6} "
            f"{result.predicted_label:<10} "
            f"{result.actual_label:<10} "
            f"{status:<8} "
            f"{result.confidence:.4f}"
        )
    
    if len(results) > limit:
        print(f"... and {len(results) - limit} more results")


def main():
    """Main function for the program."""
    print_banner()
    
    try:
        # Initialize analyzer
        analyzer = CrossPatternAnalyzer(threshold=0.75)
        
        # Generate synthetic patterns
        print("\n[1] Generating synthetic patterns...")
        patterns = analyzer.generate_synthetic_patterns(50)
        
        for pattern in patterns:
            try:
                analyzer.add_pattern(pattern)
            except Exception as e:
                print(f"Skipping invalid pattern: {e}")
        
        print(f"    Generated and added {len(patterns)} patterns")
        
        # Run cross validation
        print("\n[2] Running 5-fold cross validation...")
        cv_results = analyzer.run_cross_validation(k_folds=5)
        
        if cv_results:
            print(f"\n    Average Accuracy: {cv_results['average_accuracy']:.2%}")
            print(f"    📈 Real Error Rate: {cv_results['real_error_rate']:.2f}%")
            print(f"    Total Patterns: {cv_results['total_patterns']}")
            
            print("\n    Fold Results:")
            for fold in cv_results['folds']:
                print(
                    f"      Fold {fold['fold']}: "
                    f"Accuracy {fold['accuracy']:.2%} "
                    f"({fold['correct']}/{fold['total']})"
                )
        
        # Validate all patterns
        print("\n[3] Validating all patterns...")
        for pattern in analyzer.patterns[:20]:
            try:
                analyzer.validate_pattern(pattern)
            except Exception as e:
                print(f"Validation error for pattern {pattern.id}: {e}")
        
        # Print sample results
        print_results(analyzer.results, limit=10)
        
        # Print statistics
        print("\n[4] Statistics Summary:")
        stats = analyzer.get_statistics()
        for key, value in stats.items():
            print(f"    {key}: {value}")
        
        # Additional analysis
        print("\n[5] Feature Statistics:")
        all_features = [f for p in analyzer.patterns for f in p.features]
        feature_stats = DataProcessor.calculate_statistics(all_features)
        for key, value in feature_stats.items():
            print(f"    {key}: {value}")
        
        # Pattern similarity analysis
        print("\n[6] Pattern Similarity Analysis:")
        if len(analyzer.patterns) >= 2:
            distances = []
            for i in range(min(10, len(analyzer.patterns))):
                for j in range(i + 1, min(10, len(analyzer.patterns))):
                    dist = analyzer.calculate_distance(
                        analyzer.patterns[i],
                        analyzer.patterns[j]
                    )
                    distances.append(dist)
            
            if distances:
                avg_dist = sum(distances) / len(distances)
                print(f"    Average inter-pattern distance: {avg_dist:.4f}")
                print(f"    Min distance: {min(distances):.4f}")
                print(f"    Max distance: {max(distances):.4f}")
        
        print("\n" + "=" * 60)
        print("  Analysis Complete")
        print("=" * 60 + "\n")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return 1
        
    except Exception as e:
        print(f"\n\nCritical error in main: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)