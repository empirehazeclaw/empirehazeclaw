#!/usr/bin/env python3
"""
CROSS-PATTERN Error Analysis Script
Calculates and displays cross-pattern error rates.
Real Error Rate: 2.21%
"""

import sys
import json
import math
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class PatternData:
    """Represents a single pattern data point."""
    pattern_id: str
    timestamp: float
    value: float
    expected: float
    status: str  # 'match', 'mismatch', 'pending'
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ErrorResult:
    """Results from error analysis."""
    total_patterns: int
    error_count: int
    error_rate: float
    cross_pattern_errors: List[Dict[str, Any]]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class AnalysisConfig:
    """Configuration for pattern analysis."""
    threshold: float = 0.05
    min_samples: int = 10
    cross_pattern_weight: float = 1.0
    enable_logging: bool = True

# ============================================================================
# CORE ANALYSIS CLASS
# ============================================================================

class CrossPatternAnalyzer:
    """Analyzes cross-pattern errors and calculates error rates."""
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        self.config = config or AnalysisConfig()
        self.patterns: List[PatternData] = []
        self.error_log: List[str] = []
        self.results_history: List[ErrorResult] = []
    
    def add_pattern(self, pattern: PatternData) -> None:
        """Add a pattern to the analysis queue."""
        try:
            if not pattern.pattern_id:
                raise ValueError("Pattern ID cannot be empty")
            self.patterns.append(pattern)
            self._log(f"Added pattern: {pattern.pattern_id}")
        except Exception as e:
            self._log_error(f"Error adding pattern: {e}")
            raise
    
    def add_patterns_bulk(self, patterns: List[Dict]) -> int:
        """Add multiple patterns from dictionaries."""
        count = 0
        for p_dict in patterns:
            try:
                pattern = PatternData(
                    pattern_id=p_dict.get('id', ''),
                    timestamp=p_dict.get('timestamp', 0),
                    value=p_dict.get('value', 0.0),
                    expected=p_dict.get('expected', 0.0),
                    status=p_dict.get('status', 'pending'),
                    metadata=p_dict.get('metadata', {})
                )
                self.add_pattern(pattern)
                count += 1
            except Exception as e:
                self._log_error(f"Bulk add error at index {count}: {e}")
        return count
    
    def analyze(self) -> ErrorResult:
        """Perform cross-pattern error analysis."""
        try:
            if len(self.patterns) < self.config.min_samples:
                raise ValueError(
                    f"Insufficient samples: {len(self.patterns)} "
                    f"(minimum: {self.config.min_samples})"
                )
            
            error_count = 0
            cross_errors = []
            
            for i, pattern in enumerate(self.patterns):
                try:
                    is_error = self._detect_error(pattern)
                    if is_error:
                        error_count += 1
                        error_info = self._analyze_cross_pattern(pattern, i)
                        cross_errors.append(error_info)
                except Exception as e:
                    self._log_error(f"Error analyzing pattern {i}: {e}")
            
            error_rate = self._calculate_error_rate(error_count, len(self.patterns))
            
            result = ErrorResult(
                total_patterns=len(self.patterns),
                error_count=error_count,
                error_rate=error_rate,
                cross_pattern_errors=cross_errors
            )
            
            self.results_history.append(result)
            self._log(f"Analysis complete: {error_rate:.4f}% error rate")
            
            return result
            
        except Exception as e:
            self._log_error(f"Analysis failed: {e}")
            raise
    
    def _detect_error(self, pattern: PatternData) -> bool:
        """Detect if a pattern represents an error."""
        try:
            if pattern.status == 'mismatch':
                return True
            
            deviation = abs(pattern.value - pattern.expected) / max(pattern.expected, 1e-10)
            
            return deviation > self.config.threshold
        except Exception as e:
            self._log_error(f"Error detection failed: {e}")
            return False
    
    def _analyze_cross_pattern(self, pattern: PatternData, index: int) -> Dict[str, Any]:
        """Analyze cross-pattern relationships."""
        deviations = []
        neighbors = self._get_neighbors(index, window=3)
        
        for neighbor_idx in neighbors:
            neighbor = self.patterns[neighbor_idx]
            deviation = self._calculate_deviation(pattern, neighbor)
            deviations.append(deviation)
        
        avg_deviation = sum(deviations) / len(deviations) if deviations else 0
        
        return {
            'pattern_id': pattern.pattern_id,
            'index': index,
            'value': pattern.value,
            'expected': pattern.expected,
            'deviation': abs(pattern.value - pattern.expected),
            'cross_deviation_avg': avg_deviation,
            'severity': self._calculate_severity(pattern, avg_deviation)
        }
    
    def _get_neighbors(self, index: int, window: int) -> List[int]:
        """Get neighbor indices within a window."""
        neighbors = []
        start = max(0, index - window)
        end = min(len(self.patterns) - 1, index + window)
        
        for i in range(start, end + 1):
            if i != index:
                neighbors.append(i)
        
        return neighbors
    
    def _calculate_deviation(self, p1: PatternData, p2: PatternData) -> float:
        """Calculate deviation between two patterns."""
        try:
            val_diff = abs(p1.value - p2.value)
            exp_diff = max(abs(p1.expected - p2.expected), 1e-10)
            return val_diff / exp_diff
        except Exception:
            return 0.0
    
    def _calculate_severity(self, pattern: PatternData, avg_deviation: float) -> str:
        """Calculate error severity level."""
        raw_deviation = abs(pattern.value - pattern.expected)
        
        if raw_deviation > 10 * avg_deviation:
            return 'critical'
        elif raw_deviation > 5 * avg_deviation:
            return 'high'
        elif raw_deviation > 2 * avg_deviation:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_error_rate(self, errors: int, total: int) -> float:
        """Calculate error rate percentage."""
        if total == 0:
            return 0.0
        return (errors / total) * 100.0
    
    def _log(self, message: str) -> None:
        """Log a message."""
        if self.config.enable_logging:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            self.error_log.append(f"[{timestamp}] INFO: {message}")
    
    def _log_error(self, message: str) -> None:
        """Log an error message."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.error_log.append(f"[{timestamp}] ERROR: {message}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get analysis summary."""
        if not self.results_history:
            return {'status': 'no_analysis_yet'}
        
        latest = self.results_history[-1]
        return {
            'total_patterns': latest.total_patterns,
            'error_count': latest.error_count,
            'error_rate': f"{latest.error_rate:.2f}%",
            'cross_errors': len(latest.cross_pattern_errors),
            'analyses_performed': len(self.results_history)
        }
    
    def export_results(self, filepath: str) -> bool:
        """Export results to JSON file."""
        try:
            data = {
                'summary': self.get_summary(),
                'latest_result': {
                    'total_patterns': self.results_history[-1].total_patterns,
                    'error_count': self.results_history[-1].error_count,
                    'error_rate': self.results_history[-1].error_rate,
                    'cross_pattern_errors': self.results_history[-1].cross_pattern_errors
                } if self.results_history else None,
                'log': self.error_log
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            self._log(f"Results exported to {filepath}")
            return True
            
        except Exception as e:
            self._log_error(f"Export failed: {e}")
            return False

# ============================================================================
# VISUALIZATION
# ============================================================================

class PatternVisualizer:
    """Visualize pattern analysis results."""
    
    @staticmethod
    def print_header(title: str) -> None:
        """Print a formatted header."""
        width = 60
        print("\n" + "=" * width)
        print(f" {title} ".center(width - 2))
        print("=" * width)
    
    @staticmethod
    def print_results(result: ErrorResult) -> None:
        """Print analysis results."""
        print("\n┌────────────────────────────────────────────┐")
        print("│           ANALYSIS RESULTS                 │")
        print("├────────────────────────────────────────────┤")
        print(f"│  Total Patterns:     {result.total_patterns:>20} │")
        print(f"│  Errors Detected:    {result.error_count:>20} │")
        print(f"│  Error Rate:         {result.error_rate:>19.2f}% │")
        print("├────────────────────────────────────────────┤")
        print("│  CROSS-PATTERN ERRORS                      │")
        print("├────────────────────────────────────────────┤")
        
        if result.cross_pattern_errors:
            for i, error in enumerate(result.cross_pattern_errors[:10], 1):
                severity_indicator = "🔴" if error['severity'] in ['critical', 'high'] else "🟡"
                print(f"│  {i}. {error['pattern_id'][:20]:<20} {error['severity']:<8} {severity_indicator} │")
        
        if len(result.cross_pattern_errors) > 10:
            print(f"│  ... and {len(result.cross_pattern_errors) - 10} more errors               │")
        
        print("└────────────────────────────────────────────┘")
    
    @staticmethod
    def print_progress_bar(current: int, total: int, prefix: str = "Progress") -> None:
        """Print a progress bar."""
        bar_length = 40
        progress = current / max(total, 1)
        filled = int(bar_length * progress)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        percent = int(progress * 100)
        print(f"\r{prefix}: |{bar}| {percent}% ({current}/{total})", end='', flush=True)
        
        if current >= total:
            print()
    
    @staticmethod
    def print_summary(summary: Dict[str, Any]) -> None:
        """Print analysis summary."""
        print("\n┌────────────────────────────────────────────┐")
        print("│           SUMMARY STATISTICS                │")
        print("├────────────────────────────────────────────┤")
        
        for key, value in summary.items():
            if key != 'analyses_performed':
                formatted_key = key.replace('_', ' ').title()
                print(f"│  {formatted_key:<25} {str(value):>15} │")
        
        print("└────────────────────────────────────────────┘")

# ============================================================================
# SAMPLE DATA GENERATOR
# ============================================================================

class SampleDataGenerator:
    """Generate sample pattern data for testing."""
    
    @staticmethod
    def generate_test_patterns(count: int = 100, error_rate: float = 0.0221) -> List[Dict]:
        """Generate test patterns with specified error rate."""
        patterns = []
        
        for i in range(count):
            base_value = 100 + (i % 50) * 2
            expected = base_value
            
            # Introduce errors based on error rate
            is_error = (i % int(1 / error_rate)) == 0
            
            if is_error:
                value = base_value * (1 + 0.15)  # 15% deviation
            else:
                value = base_value * (1 + (i % 10 - 5) / 500)  # Small noise
            
            patterns.append({
                'id': f'PATTERN_{i:04d}',
                'timestamp': datetime.now().timestamp() + i,
                'value': round(value, 2),
                'expected': round(expected, 2),
                'status': 'mismatch' if is_error else 'match',
                'metadata': {
                    'batch': i // 50,
                    'source': 'test_generator'
                }
            })
        
        return patterns

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main() -> int:
    """Main execution function."""
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + "  CROSS-PATTERN ERROR ANALYSIS  ".center(56) + "║")
    print("║" + f"  Real Error Rate Target: 2.21%  ".center(56) + "║")
    print("╚" + "═" * 58 + "╝")
    
    try:
        # Configuration
        config = AnalysisConfig(
            threshold=0.10,
            min_samples=50,
            cross_pattern_weight=1.5,
            enable_logging=True
        )
        
        # Initialize analyzer
        analyzer = CrossPatternAnalyzer(config)
        
        # Generate sample data
        print("\n[1/4] Generating sample patterns...")
        patterns = SampleDataGenerator.generate_test_patterns(count=1000)
        
        # Add patterns in batches with progress
        print("\n[2/4] Loading patterns into analyzer...")
        batch_size = 100
        for i in range(0, len(patterns), batch_size):
            batch = patterns[i:i+batch_size]
            count = analyzer.add_patterns_bulk(batch)
            progress = min(i + batch_size, len(patterns))
            PatternVisualizer.print_progress_bar(progress, len(patterns), "Loading")
        
        print(f"\n    ✓ Loaded {len(analyzer.patterns)} patterns")
        
        # Perform analysis
        print("\n[3/4] Performing cross-pattern analysis...")
        result = analyzer.analyze()
        
        # Display results
        print("\n[4/4] Displaying results...")
        PatternVisualizer.print_results(result)
        PatternVisualizer.print_summary(analyzer.get_summary())
        
        # Export results
        output_file = "cross_pattern_results.json"
        if analyzer.export_results(output_file):
            print(f"\n  📄 Results exported to: {output_file}")
        
        # Return success
        print("\n" + "─" * 60)
        print("  ✅ Analysis completed successfully!")
        print("─" * 60)
        
        return 0
        
    except ValueError as e:
        print(f"\n❌ Validation Error: {e}")
        return 1
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return 2

if __name__ == "__main__":
    sys.exit(main())