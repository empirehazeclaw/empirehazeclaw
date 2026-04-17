#!/usr/bin/env python3
"""
CROSS-PATTERN Monitor
A pattern detection and error rate monitoring system.
"""

import random
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from collections import deque


@dataclass
class Pattern:
    """Represents a detected pattern."""
    pattern_id: str
    pattern_type: str
    data: List[Any]
    timestamp: datetime = field(default_factory=datetime.now)
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorRecord:
    """Records error occurrences."""
    error_type: str
    message: str
    timestamp: datetime
    severity: str = "medium"


class CrossPatternDetector:
    """Detects cross-patterns in data streams."""
    
    def __init__(self, buffer_size: int = 100):
        self.pattern_buffer: deque = deque(maxlen=buffer_size)
        self.error_log: List[ErrorRecord] = []
        self.total_requests: int = 0
        self.error_count: int = 0
        self.patterns_detected: int = 0
        self._running: bool = False
    
    def add_pattern(self, pattern: Pattern) -> bool:
        """Add a pattern to the buffer."""
        try:
            self.pattern_buffer.append(pattern)
            self.patterns_detected += 1
            return True
        except Exception as e:
            self._log_error("PatternAddError", str(e), "low")
            return False
    
    def _log_error(self, error_type: str, message: str, severity: str) -> None:
        """Log an error with details."""
        try:
            record = ErrorRecord(
                error_type=error_type,
                message=message,
                timestamp=datetime.now(),
                severity=severity
            )
            self.error_log.append(record)
            self.error_count += 1
            print(f"[ERROR] {error_type}: {message}")
        except Exception:
            pass
    
    def calculate_error_rate(self) -> float:
        """Calculate current error rate percentage."""
        try:
            if self.total_requests == 0:
                return 0.0
            return (self.error_count / self.total_requests) * 100
        except Exception as e:
            self._log_error("CalculationError", str(e), "medium")
            return 0.0
    
    def analyze_cross_patterns(self) -> List[Dict[str, Any]]:
        """Analyze patterns for cross-pattern detection."""
        try:
            results = []
            patterns_list = list(self.pattern_buffer)
            
            for i, pattern in enumerate(patterns_list):
                cross_matches = []
                
                for j, other in enumerate(patterns_list):
                    if i != j and self._is_cross_match(pattern, other):
                        cross_matches.append(other.pattern_id)
                
                results.append({
                    'pattern_id': pattern.pattern_id,
                    'cross_matches': len(cross_matches),
                    'match_ids': cross_matches[:5],
                    'confidence': pattern.confidence
                })
            
            return results
        except Exception as e:
            self._log_error("AnalysisError", str(e), "high")
            return []
    
    def _is_cross_match(self, p1: Pattern, p2: Pattern) -> bool:
        """Check if two patterns match cross-pattern criteria."""
        try:
            if p1.pattern_type != p2.pattern_type:
                return False
            
            time_diff = abs(
                (p1.timestamp - p2.timestamp).total_seconds()
            )
            
            return time_diff < 60 and len(p1.data) > 0 and len(p2.data) > 0
        except Exception:
            return False
    
    def generate_sample_data(self, count: int = 5) -> List[Pattern]:
        """Generate sample patterns for testing."""
        patterns = []
        try:
            types = ["A", "B", "C", "D"]
            for i in range(count):
                pattern = Pattern(
                    pattern_id=f"P{i:04d}",
                    pattern_type=random.choice(types),
                    data=[random.randint(0, 100) for _ in range(5)],
                    timestamp=datetime.now(),
                    confidence=random.uniform(0.5, 1.0)
                )
                patterns.append(pattern)
            return patterns
        except Exception as e:
            self._log_error("DataGenError", str(e), "medium")
            return []
    
    def process_stream(self, duration: int = 10) -> Dict[str, Any]:
        """Process data stream for specified duration."""
        self._running = True
        start_time = time.time()
        processed = 0
        
        try:
            while self._running and (time.time() - start_time) < duration:
                self.total_requests += 1
                
                sample = self.generate_sample_data(random.randint(1, 3))
                for pattern in sample:
                    if self.add_pattern(pattern):
                        processed += 1
                
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            self._running = False
        except Exception as e:
            self._log_error("StreamError", str(e), "high")
        finally:
            self._running = False
        
        return self._get_stats(processed)
    
    def _get_stats(self, processed: int) -> Dict[str, Any]:
        """Get current statistics."""
        try:
            return {
                'total_requests': self.total_requests,
                'patterns_processed': processed,
                'patterns_detected': self.patterns_detected,
                'error_count': self.error_count,
                'error_rate': round(self.calculate_error_rate(), 2),
                'buffer_size': len(self.pattern_buffer)
            }
        except Exception:
            return {}


class PatternMonitor:
    """Monitors and displays pattern statistics."""
    
    def __init__(self, detector: CrossPatternDetector):
        self.detector = detector
        self.history: List[Dict[str, Any]] = []
    
    def display_stats(self, stats: Dict[str, Any]) -> None:
        """Display statistics in formatted output."""
        try:
            print("\n" + "=" * 50)
            print("CROSS-PATTERN Monitor Statistics")
            print("=" * 50)
            print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Total Requests: {stats.get('total_requests', 0)}")
            print(f"Patterns Processed: {stats.get('patterns_processed', 0)}")
            print(f"Patterns Detected: {stats.get('patterns_detected', 0)}")
            print(f"Errors: {stats.get('error_count', 0)}")
            print(f"Error Rate: {stats.get('error_rate', 0.0)}%")
            print(f"Buffer Size: {stats.get('buffer_size', 0)}")
            print("=" * 50)
        except Exception as e:
            print(f"Display error: {e}")
    
    def run_monitoring_cycle(self, cycles: int = 5) -> None:
        """Run monitoring cycles."""
        try:
            for i in range(cycles):
                print(f"\n>>> Monitoring Cycle {i + 1}/{cycles}")
                
                sample_data = self.detector.generate_sample_data(3)
                for pattern in sample_data:
                    self.detector.add_pattern(pattern)
                
                self.detector.total_requests += len(sample_data)
                
                stats = {
                    'total_requests': self.detector.total_requests,
                    'patterns_processed': sum(1 for _ in sample_data),
                    'patterns_detected': self.detector.patterns_detected,
                    'error_count': self.detector.error_count,
                    'error_rate': self.detector.calculate_error_rate(),
                    'buffer_size': len(self.detector.pattern_buffer)
                }
                
                self.history.append(stats.copy())
                self.display_stats(stats)
                
                cross_results = self.detector.analyze_cross_patterns()
                if cross_results:
                    print(f"\nCross-pattern matches found: {len(cross_results)}")
                
                time.sleep(1)
                
        except Exception as e:
            print(f"Monitoring cycle error: {e}")
    
    def generate_report(self) -> str:
        """Generate monitoring report."""
        try:
            report_lines = [
                "=" * 60,
                "CROSS-PATTERN MONITORING REPORT",
                "=" * 60,
                f"Generated: {datetime.now().isoformat()}",
                f"Total Cycles: {len(self.history)}",
            ]
            
            if self.history:
                error_rates = [h.get('error_rate', 0) for h in self.history]
                avg_error_rate = sum(error_rates) / len(error_rates)
                report_lines.append(f"Average Error Rate: {avg_error_rate:.2f}%")
                report_lines.append(f"Peak Error Rate: {max(error_rates):.2f}%")
            
            report_lines.append("=" * 60)
            return "\n".join(report_lines)
        except Exception as e:
            return f"Report generation error: {e}"


def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration parameters."""
    try:
        required_keys = ['buffer_size', 'monitoring_enabled']
        for key in required_keys:
            if key not in config:
                return False
        
        if not isinstance(config['buffer_size'], int):
            return False
        
        if config['buffer_size'] < 1 or config['buffer_size'] > 1000:
            return False
        
        return True
    except Exception:
        return False


def main():
    """Main execution function."""
    try:
        print("Initializing CROSS-PATTERN Detection System...")
        
        config = {
            'buffer_size': 100,
            'monitoring_enabled': True
        }
        
        if not validate_config(config):
            print("Invalid configuration. Using defaults.")
            config['buffer_size'] = 100
        
        detector = CrossPatternDetector(buffer_size=config['buffer_size'])
        monitor = PatternMonitor(detector)
        
        print("Starting pattern detection...")
        
        sample_patterns = detector.generate_sample_data(5)
        for pattern in sample_patterns:
            detector.add_pattern(pattern)
        
        monitor.run_monitoring_cycle(cycles=3)
        
        stats = detector.process_stream(duration=3)
        monitor.display_stats(stats)
        
        print("\n" + monitor.generate_report())
        
        print("\nCross-pattern Analysis Results:")
        results = detector.analyze_cross_patterns()
        for result in results[:5]:
            print(f"  Pattern {result['pattern_id']}: "
                  f"{result['cross_matches']} cross-matches")
        
        print("\nSystem completed successfully.")
        
    except Exception as e:
        print(f"Main execution error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())