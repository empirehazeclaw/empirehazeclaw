#!/usr/bin/env python3
"""
CROSS-PATTERN Analysis Script
Calculates and tracks error rates with pattern detection
"""

import sys
import random
import time
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field


@dataclass
class PatternResult:
    """Represents a pattern detection result."""
    pattern_id: str
    detected: bool
    error_rate: float
    confidence: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


class CrossPatternDetector:
    """Detects cross-patterns in data streams."""
    
    def __init__(self, threshold: float = 0.05):
        self.threshold = threshold
        self.patterns: List[Dict[str, Any]] = []
        self.error_history: List[float] = []
        self._pattern_count = 0
    
    def generate_pattern_id(self) -> str:
        """Generate unique pattern ID."""
        self._pattern_count += 1
        return f"PATTERN_{self._pattern_count:04d}"
    
    def analyze_sequence(self, data: List[float]) -> PatternResult:
        """Analyze a sequence for cross-patterns."""
        try:
            if not data:
                raise ValueError("Empty data sequence")
            
            mean_val = sum(data) / len(data)
            variance = sum((x - mean_val) ** 2 for x in data) / len(data)
            std_dev = variance ** 0.5
            
            # Calculate error rate
            error_count = sum(1 for x in data if abs(x - mean_val) > 2 * std_dev)
            error_rate = error_count / len(data)
            
            self.error_history.append(error_rate)
            
            # Detect cross-pattern
            detected = error_rate > self.threshold
            confidence = min(error_rate * 10, 1.0)
            
            pattern = {
                'id': self.generate_pattern_id(),
                'mean': mean_val,
                'std_dev': std_dev,
                'variance': variance,
                'error_count': error_count,
                'data_points': len(data)
            }
            self.patterns.append(pattern)
            
            return PatternResult(
                pattern_id=pattern['id'],
                detected=detected,
                error_rate=error_rate,
                confidence=confidence,
                metadata=pattern
            )
            
        except Exception as e:
            raise RuntimeError(f"Pattern analysis failed: {e}")
    
    def calculate_real_error_rate(self) -> float:
        """Calculate real error rate from history."""
        try:
            if not self.error_history:
                return 0.0
            
            # Weighted moving average
            weights = [0.1 * (i + 1) for i in range(len(self.error_history))]
            total_weight = sum(weights)
            weighted_sum = sum(r * w for r, w in zip(self.error_history, weights))
            
            return weighted_sum / total_weight
            
        except Exception as e:
            print(f"Error rate calculation failed: {e}")
            return 0.0
    
    def get_statistics(self) -> Dict[str, float]:
        """Get statistical summary."""
        if not self.error_history:
            return {}
        
        sorted_errors = sorted(self.error_history)
        n = len(sorted_errors)
        
        return {
            'mean': sum(self.error_history) / n,
            'median': sorted_errors[n // 2],
            'min': min(self.error_history),
            'max': max(self.error_history),
            'std_dev': (sum((e - sum(self.error_history)/n)**2 for e in self.error_history) / n) ** 0.5,
            'count': n
        }


class DataGenerator:
    """Generate test data for pattern analysis."""
    
    @staticmethod
    def generate_normal(mean: float = 0.0, std: float = 1.0, size: int = 100) -> List[float]:
        """Generate normally distributed data."""
        try:
            return [random.gauss(mean, std) for _ in range(size)]
        except Exception as e:
            raise RuntimeError(f"Data generation failed: {e}")
    
    @staticmethod
    def generate_anomalous(mean: float = 0.0, std: float = 1.0, size: int = 100, anomaly_ratio: float = 0.1) -> List[float]:
        """Generate data with anomalies."""
        data = DataGenerator.generate_normal(mean, std, int(size * (1 - anomaly_ratio)))
        anomaly_count = size - len(data)
        anomalies = [random.gauss(mean, std * 5) for _ in range(anomaly_count)]
        data.extend(anomalies)
        random.shuffle(data)
        return data


class ErrorRateTracker:
    """Tracks error rates over time."""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.errors: List[Tuple[float, str]] = []  # (error_rate, timestamp)
    
    def add_error(self, error_rate: float) -> None:
        """Add error rate entry."""
        timestamp = datetime.now().isoformat()
        self.errors.append((error_rate, timestamp))
        
        if len(self.errors) > self.window_size:
            self.errors.pop(0)
    
    def get_current_rate(self) -> float:
        """Get current error rate."""
        if not self.errors:
            return 0.0
        return self.errors[-1][0]
    
    def get_average_rate(self) -> float:
        """Get average error rate."""
        if not self.errors:
            return 0.0
        return sum(e[0] for e in self.errors) / len(self.errors)
    
    def export_data(self) -> List[Dict[str, Any]]:
        """Export error history."""
        return [
            {'error_rate': e[0], 'timestamp': e[1]}
            for e in self.errors
        ]


class PatternVisualizer:
    """Visualize pattern detection results."""
    
    @staticmethod
    def format_result(result: PatternResult) -> str:
        """Format result as string."""
        status = "DETECTED" if result.detected else "CLEAR"
        return (
            f"┌─────────────────────────────────────────┐\n"
            f"│ Pattern ID: {result.pattern_id:<25} │\n"
            f"│ Status: {status:<30} │\n"
            f"│ Error Rate: {result.error_rate:.4f} ({result.error_rate*100:.2f}%)    │\n"
            f"│ Confidence: {result.confidence:.4f}              │\n"
            f"│ Timestamp: {result.timestamp:<25} │\n"
            f"└─────────────────────────────────────────┘"
        )
    
    @staticmethod
    def print_progress_bar(current: int, total: int, width: int = 50) -> None:
        """Print progress bar."""
        filled = int(width * current / total) if total > 0 else 0
        bar = '█' * filled + '░' * (width - filled)
        percentage = 100 * current / total if total > 0 else 0
        print(f"\r[{bar}] {percentage:.1f}% ({current}/{total})", end='', flush=True)


class CrossPatternAnalyzer:
    """Main analyzer class combining all components."""
    
    def __init__(self):
        self.detector = CrossPatternDetector(threshold=0.05)
        self.tracker = ErrorRateTracker(window_size=100)
        self.generator = DataGenerator()
        self.results: List[PatternResult] = []
    
    def run_single_analysis(self, data: List[float], label: str = "Test") -> PatternResult:
        """Run single pattern analysis."""
        try:
            result = self.detector.analyze_sequence(data)
            self.tracker.add_error(result.error_rate)
            self.results.append(result)
            
            print(f"\n[ {label} ]")
            print(PatternVisualizer.format_result(result))
            
            return result
            
        except Exception as e:
            print(f"Analysis failed for {label}: {e}")
            raise
    
    def run_batch_analysis(self, num_analyses: int = 10, batch_size: int = 100) -> List[PatternResult]:
        """Run batch pattern analyses."""
        print(f"\nRunning {num_analyses} batch analyses...")
        results = []
        
        for i in range(num_analyses):
            # Mix normal and anomalous data
            if random.random() < 0.3:
                data = self.generator.generate_anomalous(size=batch_size)
            else:
                data = self.generator.generate_normal(size=batch_size)
            
            result = self.run_single_analysis(data, f"Batch_{i+1:03d}")
            results.append(result)
            
            # Progress visualization
            PatternVisualizer.print_progress_bar(i + 1, num_analyses)
            time.sleep(0.01)  # Small delay for visual effect
        
        print()  # New line after progress bar
        return results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate analysis report."""
        real_error_rate = self.detector.calculate_real_error_rate()
        stats = self.detector.get_statistics()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_analyses': len(self.results),
            'patterns_detected': sum(1 for r in self.results if r.detected),
            'real_error_rate': real_error_rate,
            'real_error_rate_percent': f"{real_error_rate * 100:.2f}%",
            'statistics': stats,
            'current_tracker_rate': self.tracker.get_current_rate(),
            'average_tracker_rate': self.tracker.get_average_rate()
        }
        
        return report
    
    def print_report(self) -> None:
        """Print formatted report."""
        report = self.generate_report()
        
        print("\n" + "=" * 60)
        print("CROSS-PATTERN ANALYSIS REPORT")
        print("=" * 60)
        print(f"Generated: {report['timestamp']}")
        print("-" * 60)
        print(f"Total Analyses:    {report['total_analyses']}")
        print(f"Patterns Detected: {report['patterns_detected']}")
        print("-" * 60)
        print(f"📈 Real Error Rate: {report['real_error_rate_percent']}")
        print("-" * 60)
        
        stats = report['statistics']
        if stats:
            print("Statistical Summary:")
            print(f"  Mean Error Rate:  {stats.get('mean', 0):.4f}")
            print(f"  Median:           {stats.get('median', 0):.4f}")
            print(f"  Min:              {stats.get('min', 0):.4f}")
            print(f"  Max:              {stats.get('max', 0):.4f}")
            print(f"  Std Dev:          {stats.get('std_dev', 0):.4f}")
            print(f"  Sample Count:     {stats.get('count', 0)}")
        
        print("-" * 60)
        print(f"Current Tracker Rate:  {report['current_tracker_rate']:.4f}")
        print(f"Average Tracker Rate:  {report['average_tracker_rate']:.4f}")
        print("=" * 60)


def run_demonstration() -> None:
    """Run demonstration of cross-pattern analysis."""
    print("\n" + "=" * 60)
    print("CROSS-PATTERN DETECTION SYSTEM")
    print("=" * 60)
    print(f"Python Version: {sys.version.split()[0]}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    analyzer = CrossPatternAnalyzer()
    
    # Test 1: Normal data
    print("\n[Test 1] Normal Data Analysis")
    normal_data = DataGenerator.generate_normal(mean=50, std=10, size=100)
    analyzer.run_single_analysis(normal_data, "Normal Data")
    
    # Test 2: Anomalous data
    print("\n[Test 2] Anomalous Data Analysis")
    anomalous_data = DataGenerator.generate_anomalous(mean=50, std=10, size=100, anomaly_ratio=0.15)
    analyzer.run_single_analysis(anomalous_data, "Anomalous Data")
    
    # Test 3: Edge case - high variance
    print("\n[Test 3] High Variance Data")
    high_var_data = DataGenerator.generate_normal(mean=0, std=100, size=200)
    analyzer.run_single_analysis(high_var_data, "High Variance")
    
    # Batch analysis
    print("\n[Batch Analysis] Processing multiple samples...")
    batch_results = analyzer.run_batch_analysis(num_analyses=20, batch_size=100)
    
    # Final report
    analyzer.print_report()
    
    # Export results
    try:
        export_data = analyzer.tracker.export_data()
        print(f"\n[Export] {len(export_data)} error rate entries available for export")
    except Exception as e:
        print(f"\n[Warning] Export failed: {e}")


def run_custom_analysis(data: List[float], threshold: float = 0.05) -> PatternResult:
    """Run custom analysis on provided data."""
    try:
        detector = CrossPatternDetector(threshold=threshold)
        result = detector.analyze_sequence(data)
        return result
    except Exception as e:
        print(f"Custom analysis failed: {e}")
        raise


def main() -> int:
    """Main entry point."""
    try:
        # Set random seed for reproducibility
        random.seed(42)
        
        # Run demonstration
        run_demonstration()
        
        # Additional custom tests
        print("\n" + "=" * 60)
        print("ADDITIONAL TESTS")
        print("=" * 60)
        
        # Test edge cases
        test_cases = [
            ([], "Empty list"),
            ([1.0], "Single element"),
            ([0.1, 0.2, 0.3, 0.4, 0.5], "Small sequence"),
            ([i * 0.1 for i in range(100)], "Linear sequence"),
        ]
        
        for data, description in test_cases:
            try:
                result = run_custom_analysis(data)
                print(f"\n[{description}] Error Rate: {result.error_rate:.4f}")
            except Exception as e:
                print(f"\n[{description}] Failed: {e}")
        
        print("\n" + "=" * 60)
        print("DEMONSTRATION COMPLETE")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())