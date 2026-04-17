#!/usr/bin/env python3
"""
Cross-Pattern Error Rate Analyzer
Analyzes patterns and tracks real error rates.
"""

import random
import time
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
import math


@dataclass
class Pattern:
    """Represents a pattern with various attributes."""
    pattern_id: str
    sequence: List[int]
    pattern_type: str
    weight: float = 1.0
    metadata: Dict = field(default_factory=dict)

    def __str__(self) -> str:
        return f"Pattern({self.pattern_id}, type={self.pattern_type}, seq={self.sequence})"


@dataclass
class ErrorRecord:
    """Records error information."""
    timestamp: datetime
    pattern_id: str
    error_type: str
    position: int
    severity: str
    details: str = ""


class CrossPatternAnalyzer:
    """Main analyzer for cross-pattern analysis."""

    def __init__(self, seed: Optional[int] = None):
        self.patterns: List[Pattern] = []
        self.error_records: List[ErrorRecord] = []
        self.error_counts: Dict[str, int] = {}
        self.total_analyses: int = 0
        self.current_error_rate: float = 0.0
        
        if seed is not None:
            random.seed(seed)

    def add_pattern(self, pattern: Pattern) -> None:
        """Add a pattern to the analyzer."""
        try:
            if not pattern.pattern_id:
                raise ValueError("Pattern ID cannot be empty")
            if not pattern.sequence:
                raise ValueError("Pattern sequence cannot be empty")
            
            self.patterns.append(pattern)
        except ValueError as e:
            print(f"Error adding pattern: {e}")
            raise

    def generate_random_pattern(self, length: int = 10) -> Pattern:
        """Generate a random pattern."""
        try:
            pattern_id = f"PAT_{random.randint(1000, 9999)}"
            sequence = [random.randint(0, 100) for _ in range(length)]
            pattern_type = random.choice(["TYPE_A", "TYPE_B", "TYPE_C", "TYPE_D"])
            
            return Pattern(
                pattern_id=pattern_id,
                sequence=sequence,
                pattern_type=pattern_type,
                weight=random.uniform(0.5, 2.0)
            )
        except Exception as e:
            print(f"Error generating pattern: {e}")
            raise

    def calculate_cross_pattern_distance(self, p1: Pattern, p2: Pattern) -> float:
        """Calculate distance between two patterns."""
        try:
            if len(p1.sequence) != len(p2.sequence):
                min_len = min(len(p1.sequence), len(p2.sequence))
                max_len = max(len(p1.sequence), len(p2.sequence))
                length_penalty = (max_len - min_len) / max_len * 10
            else:
                length_penalty = 0

            sum_squared_diff = 0
            for i in range(min(len(p1.sequence), len(p2.sequence))):
                diff = p1.sequence[i] - p2.sequence[i]
                sum_squared_diff += diff ** 2

            euclidean = math.sqrt(sum_squared_diff)
            return euclidean + length_penalty
        except Exception as e:
            print(f"Error calculating distance: {e}")
            return float('inf')

    def analyze_pattern(self, pattern: Pattern) -> Dict:
        """Perform detailed analysis of a pattern."""
        try:
            result = {
                "pattern_id": pattern.pattern_id,
                "mean": sum(pattern.sequence) / len(pattern.sequence),
                "std_dev": self._calculate_std_dev(pattern.sequence),
                "min": min(pattern.sequence),
                "max": max(pattern.sequence),
                "range": max(pattern.sequence) - min(pattern.sequence),
                "type": pattern.pattern_type,
                "valid": True
            }

            # Detect anomalies
            mean = result["mean"]
            anomalies = []
            for i, val in enumerate(pattern.sequence):
                if abs(val - mean) > 2 * result["std_dev"]:
                    anomalies.append({"position": i, "value": val})

            result["anomalies"] = anomalies
            return result
        except Exception as e:
            return {"pattern_id": pattern.pattern_id, "valid": False, "error": str(e)}

    def _calculate_std_dev(self, values: List[int]) -> float:
        """Calculate standard deviation."""
        try:
            if not values:
                return 0.0
            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
            return math.sqrt(variance)
        except Exception as e:
            print(f"Error calculating std dev: {e}")
            return 0.0

    def detect_cross_pattern_errors(self, pattern: Pattern) -> List[ErrorRecord]:
        """Detect errors in cross-pattern analysis."""
        errors = []
        try:
            mean = sum(pattern.sequence) / len(pattern.sequence)
            std_dev = self._calculate_std_dev(pattern.sequence)

            threshold_upper = mean + 2 * std_dev
            threshold_lower = mean - 2 * std_dev

            for i, value in enumerate(pattern.sequence):
                if value > threshold_upper or value < threshold_lower:
                    error = ErrorRecord(
                        timestamp=datetime.now(),
                        pattern_id=pattern.pattern_id,
                        error_type="THRESHOLD_VIOLATION",
                        position=i,
                        severity="MEDIUM",
                        details=f"Value {value} outside thresholds [{threshold_lower:.2f}, {threshold_upper:.2f}]"
                    )
                    errors.append(error)
                    self.error_records.append(error)

            return errors
        except Exception as e:
            print(f"Error detecting errors: {e}")
            return errors

    def update_error_rate(self) -> float:
        """Update and return the current error rate."""
        try:
            if self.total_analyses == 0:
                self.current_error_rate = 0.0
            else:
                total_errors = sum(self.error_counts.values())
                self.current_error_rate = total_errors / self.total_analyses * 100
            
            return self.current_error_rate
        except Exception as e:
            print(f"Error updating error rate: {e}")
            return 0.0

    def record_analysis(self, error_occurred: bool = False) -> None:
        """Record an analysis result."""
        try:
            self.total_analyses += 1
            if error_occurred:
                self.error_counts["analysis_errors"] = self.error_counts.get("analysis_errors", 0) + 1
            self.update_error_rate()
        except Exception as e:
            print(f"Error recording analysis: {e}")

    def run_batch_analysis(self, num_patterns: int = 50) -> Dict:
        """Run analysis on multiple patterns."""
        try:
            results = {
                "total_patterns": num_patterns,
                "patterns_analyzed": 0,
                "errors_detected": 0,
                "error_rate": 0.0,
                "analyses": []
            }

            for _ in range(num_patterns):
                pattern = self.generate_random_pattern(random.randint(5, 15))
                self.add_pattern(pattern)

                analysis = self.analyze_pattern(pattern)
                errors = self.detect_cross_pattern_errors(pattern)

                results["analyses"].append({
                    "pattern_id": pattern.pattern_id,
                    "analysis": analysis,
                    "error_count": len(errors)
                })

                results["patterns_analyzed"] += 1
                results["errors_detected"] += len(errors)
                
                self.record_analysis(error_occurred=(len(errors) > 0))

            results["error_rate"] = self.update_error_rate()
            return results
        except Exception as e:
            print(f"Error in batch analysis: {e}")
            return {"error": str(e)}

    def compare_patterns(self, p1_id: str, p2_id: str) -> Optional[float]:
        """Compare two patterns by ID."""
        try:
            p1 = next((p for p in self.patterns if p.pattern_id == p1_id), None)
            p2 = next((p for p in self.patterns if p.pattern_id == p2_id), None)

            if p1 is None or p2 is None:
                print(f"Pattern not found: {p1_id} or {p2_id}")
                return None

            return self.calculate_cross_pattern_distance(p1, p2)
        except Exception as e:
            print(f"Error comparing patterns: {e}")
            return None

    def get_statistics(self) -> Dict:
        """Get comprehensive statistics."""
        try:
            total_errors = sum(self.error_counts.values())
            return {
                "total_analyses": self.total_analyses,
                "total_errors": total_errors,
                "current_error_rate": self.current_error_rate,
                "patterns_stored": len(self.patterns),
                "error_records_count": len(self.error_records),
                "error_counts_by_type": dict(self.error_counts)
            }
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {"error": str(e)}

    def export_report(self, filename: str) -> bool:
        """Export analysis report to JSON file."""
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "statistics": self.get_statistics(),
                "patterns": [
                    {
                        "id": p.pattern_id,
                        "type": p.pattern_type,
                        "sequence": p.sequence,
                        "weight": p.weight
                    }
                    for p in self.patterns[:100]  # Limit to first 100
                ],
                "errors": [
                    {
                        "timestamp": e.timestamp.isoformat(),
                        "pattern_id": e.pattern_id,
                        "error_type": e.error_type,
                        "position": e.position,
                        "severity": e.severity
                    }
                    for e in self.error_records[:100]  # Limit to first 100
                ]
            }

            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error exporting report: {e}")
            return False

    def reset(self) -> None:
        """Reset all data."""
        try:
            self.patterns.clear()
            self.error_records.clear()
            self.error_counts.clear()
            self.total_analyses = 0
            self.current_error_rate = 0.0
        except Exception as e:
            print(f"Error resetting: {e}")


class Visualizer:
    """Visualization helper for pattern analysis."""

    @staticmethod
    def print_header(title: str) -> None:
        """Print formatted header."""
        print("\n" + "=" * 60)
        print(f" {title}")
        print("=" * 60)

    @staticmethod
    def print_progress(current: int, total: int, prefix: str = "Progress") -> None:
        """Print progress bar."""
        percentage = (current / total) * 100 if total > 0 else 0
        bar_length = 40
        filled = int(bar_length * current / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"\r{prefix}: |{bar}| {percentage:.1f}% ({current}/{total})", end="")

    @staticmethod
    def print_pattern_info(pattern: Pattern) -> None:
        """Print pattern information."""
        print(f"  ID: {pattern.pattern_id}")
        print(f"  Type: {pattern.pattern_type}")
        print(f"  Sequence: {pattern.sequence[:10]}{'...' if len(pattern.sequence) > 10 else ''}")
        print(f"  Weight: {pattern.weight:.2f}")


def run_demonstration() -> None:
    """Run a demonstration of the cross-pattern analyzer."""
    print("\n🚀 Starting Cross-Pattern Error Rate Analyzer\n")

    analyzer = CrossPatternAnalyzer(seed=42)
    visualizer = Visualizer()

    # Generate and analyze patterns
    visualizer.print_header("CROSS-PATTERN GENERATION")
    
    test_patterns = []
    for i in range(20):
        pattern = analyzer.generate_random_pattern(length=8)
        test_patterns.append(pattern)
        print(f"  Generated: {pattern.pattern_id} ({pattern.pattern_type})")

    # Add patterns to analyzer
    visualizer.print_header("ADDING PATTERNS TO ANALYZER")
    for pattern in test_patterns:
        try:
            analyzer.add_pattern(pattern)
            print(f"  ✓ Added {pattern.pattern_id}")
        except Exception as e:
            print(f"  ✗ Failed to add {pattern.pattern_id}: {e}")

    # Perform cross-pattern analysis
    visualizer.print_header("CROSS-PATTERN ANALYSIS")
    for i, pattern in enumerate(test_patterns[:5]):
        analysis = analyzer.analyze_pattern(pattern)
        print(f"\n  Pattern: {pattern.pattern_id}")
        print(f"    Mean: {analysis.get('mean', 'N/A'):.2f}")
        print(f"    Std Dev: {analysis.get('std_dev', 'N/A'):.2f}")
        print(f"    Anomalies: {len(analysis.get('anomalies', []))}")

        errors = analyzer.detect_cross_pattern_errors(pattern)
        print(f"    Errors detected: {len(errors)}")

        analyzer.record_analysis(error_occurred=(len(errors) > 0))

    # Run batch analysis
    visualizer.print_header("BATCH ANALYSIS")
    print("  Running batch analysis on 30 patterns...")
    batch_results = analyzer.run_batch_analysis(num_patterns=30)
    print(f"  ✓ Analyzed {batch_results['patterns_analyzed']} patterns")
    print(f"  ✓ Detected {batch_results['errors_detected']} errors")

    # Show error rate
    visualizer.print_header("ERROR RATE ANALYSIS")
    error_rate = analyzer.update_error_rate()
    print(f"\n  📈 Real Error Rate: {error_rate:.2f}%")

    # Statistics
    stats = analyzer.get_statistics()
    visualizer.print_header("STATISTICS")
    print(f"  Total Analyses: {stats['total_analyses']}")
    print(f"  Total Errors: {stats['total_errors']}")
    print(f"  Patterns Stored: {stats['patterns_stored']}")
    print(f"  Error Rate: {stats['current_error_rate']:.2f}%")

    # Cross-pattern comparisons
    visualizer.print_header("CROSS-PATTERN COMPARISONS")
    if len(analyzer.patterns) >= 2:
        p1 = analyzer.patterns[0]
        p2 = analyzer.patterns[1]
        distance = analyzer.calculate_cross_pattern_distance(p1, p2)
        print(f"  Distance between {p1.pattern_id} and {p2.pattern_id}: {distance:.2f}")

    # Export report
    visualizer.print_header("EXPORT REPORT")
    try:
        filename = "cross_pattern_report.json"
        success = analyzer.export_report(filename)
        if success:
            print(f"  ✓ Report exported to {filename}")
        else:
            print("  ✗ Failed to export report")
    except Exception as e:
        print(f"  ✗ Error exporting: {e}")

    visualizer.print_header("DEMONSTRATION COMPLETE")
    print("\n  ✅ All operations completed successfully!")
    print(f"  📊 Final Error Rate: {error_rate:.2f}%\n")


def run_error_simulation() -> None:
    """Run error rate simulation."""
    print("\n🎲 Running Error Rate Simulation\n")

    analyzer = CrossPatternAnalyzer(seed=123)

    iterations = 100
    for i in range(iterations):
        pattern = analyzer.generate_random_pattern(length=10)
        analyzer.add_pattern(pattern)

        errors = analyzer.detect_cross_pattern_errors(pattern)
        analyzer.record_analysis(error_occurred=(len(errors) > 0 and random.random() < 0.7))

        if (i + 1) % 20 == 0:
            error_rate = analyzer.update_error_rate()
            print(f"  Iteration {i + 1}: Error Rate = {error_rate:.2f}%")

    final_rate = analyzer.update_error_rate()
    print(f"\n  📈 Real Error Rate: {final_rate:.2f}%")
    print(f"  📊 Total Patterns: {len(analyzer.patterns)}")
    print(f"  📋 Total Errors Recorded: {len(analyzer.error_records)}\n")


def main():
    """Main entry point."""
    try:
        print("\n" + "=" * 60)
        print("  CROSS-PATTERN ERROR RATE ANALYZER")
        print("  Python 3 Compatible Version")
        print("=" * 60)

        run_demonstration()
        run_error_simulation()

        print("=" * 60)
        print("  ✅ Program completed successfully!")
        print("=" * 60 + "\n")

    except KeyboardInterrupt:
        print("\n\n  ⚠️  Operation cancelled by user\n")
    except Exception as e:
        print(f"\n  ❌ Unexpected error: {e}\n")
        raise


if __name__ == "__main__":
    main()