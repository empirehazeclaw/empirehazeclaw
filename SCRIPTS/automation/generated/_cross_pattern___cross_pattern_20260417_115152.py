#!/usr/bin/env python3
"""
Error Rate Pattern Analysis Script
Analyzes cross-patterns in error rates and provides detailed reporting.
"""

import random
import time
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class ErrorLevel(Enum):
    """Error severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class ErrorRecord:
    """Represents a single error record."""
    timestamp: str
    error_rate: float
    pattern_id: str
    severity: str
    description: str
    source: str


class CrossPatternAnalyzer:
    """Analyzes cross-patterns in error rates."""
    
    def __init__(self, threshold: float = 2.0):
        self.threshold = threshold
        self.records: List[ErrorRecord] = []
        self.patterns: Dict[str, int] = {}
        self.alerts: List[str] = []
    
    def generate_sample_data(self, count: int = 100) -> List[float]:
        """Generate sample error rate data."""
        data = []
        for _ in range(count):
            rate = random.gauss(2.0, 0.5)
            rate = max(0.1, min(rate, 5.0))
            data.append(rate)
        return data
    
    def detect_cross_patterns(self, data: List[float]) -> List[Dict]:
        """Detect cross-patterns in error rate data."""
        patterns = []
        for i in range(len(data) - 2):
            pattern = []
            for j in range(3):
                if i + j < len(data):
                    pattern.append(data[i + j])
            
            if len(pattern) == 3:
                is_cross_pattern = (
                    pattern[0] > self.threshold and
                    pattern[1] > self.threshold and
                    pattern[2] > self.threshold
                )
                patterns.append({
                    'start_index': i,
                    'pattern': pattern,
                    'is_cross_pattern': is_cross_pattern,
                    'avg_rate': sum(pattern) / len(pattern)
                })
        return patterns
    
    def analyze_trends(self, data: List[float]) -> Dict:
        """Analyze trends in error rate data."""
        if not data:
            return {}
        
        return {
            'mean': sum(data) / len(data),
            'max': max(data),
            'min': min(data),
            'count': len(data),
            'above_threshold': sum(1 for x in data if x > self.threshold),
            'cross_pattern_count': len([p for p in self.detect_cross_patterns(data) if p['is_cross_pattern']])
        }
    
    def add_record(self, record: ErrorRecord):
        """Add an error record."""
        self.records.append(record)
        if record.pattern_id not in self.patterns:
            self.patterns[record.pattern_id] = 0
        self.patterns[record.pattern_id] += 1
        
        if record.error_rate > self.threshold:
            self.alerts.append(f"[CROSS-PATTERN] Alert: Error rate {record.error_rate:.2f}% at {record.timestamp}")
    
    def generate_report(self) -> str:
        """Generate a detailed analysis report."""
        report = []
        report.append("=" * 60)
        report.append("CROSS-PATTERN ERROR RATE ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Records: {len(self.records)}")
        report.append(f"Cross-Pattern Alerts: {len(self.alerts)}")
        report.append(f"Threshold: {self.threshold}%")
        report.append("-" * 60)
        
        if self.alerts:
            report.append("\n📈 DETECTED CROSS-PATTERNS:")
            for i, alert in enumerate(self.alerts[:10], 1):
                report.append(f"  {i}. {alert}")
        
        if self.patterns:
            report.append("\n📊 Pattern Distribution:")
            for pattern_id, count in sorted(self.patterns.items(), key=lambda x: x[1], reverse=True)[:5]:
                report.append(f"  {pattern_id}: {count} occurrences")
        
        return "\n".join(report)


class DataSimulator:
    """Simulates error data for testing."""
    
    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        self.sources = ['API', 'Database', 'Cache', 'Worker', 'Queue', 'Gateway']
        self.patterns = ['ALPHA', 'BETA', 'GAMMA', 'DELTA', 'EPSILON']
    
    def generate_record(self) -> ErrorRecord:
        """Generate a random error record."""
        timestamp = datetime.now().isoformat()
        error_rate = round(random.gauss(2.21, 0.8), 2)
        error_rate = max(0.01, min(error_rate, 10.0))
        
        severity = random.choice([e.value for e in ErrorLevel])
        pattern_id = random.choice(self.patterns)
        source = random.choice(self.sources)
        
        descriptions = [
            f"Connection timeout in {source}",
            f"Rate limit exceeded for {pattern_id}",
            f"Failed health check: {source}",
            f"Memory threshold exceeded",
            f"Request queue full",
            f"Authentication failure"
        ]
        description = random.choice(descriptions)
        
        return ErrorRecord(
            timestamp=timestamp,
            error_rate=error_rate,
            pattern_id=pattern_id,
            severity=severity,
            description=description,
            source=source
        )
    
    def generate_batch(self, count: int) -> List[ErrorRecord]:
        """Generate a batch of error records."""
        return [self.generate_record() for _ in range(count)]


class Visualizer:
    """Visualizes error rate patterns."""
    
    @staticmethod
    def create_histogram(data: List[float], bins: int = 10) -> str:
        """Create a simple text-based histogram."""
        if not data:
            return "No data to display"
        
        min_val = min(data)
        max_val = max(data)
        bin_width = (max_val - min_val) / bins if bins > 0 else 1
        
        histogram = ["\n📊 Error Rate Distribution:"]
        histogram.append("-" * 40)
        
        counts = [0] * bins
        for value in data:
            bin_index = min(int((value - min_val) / bin_width), bins - 1)
            counts[bin_index] += 1
        
        max_count = max(counts) if counts else 1
        for i, count in enumerate(counts):
            bin_start = min_val + i * bin_width
            bin_end = bin_start + bin_width
            bar_length = int((count / max_count) * 20)
            bar = "█" * bar_length
            histogram.append(f"  {bin_start:5.2f} - {bin_end:5.2f} | {bar} ({count})")
        
        histogram.append("-" * 40)
        return "\n".join(histogram)
    
    @staticmethod
    def create_trend_indicator(current: float, previous: float) -> str:
        """Create a trend indicator."""
        diff = current - previous
        if abs(diff) < 0.1:
            return "➡️  STABLE"
        elif diff > 0:
            return f"📈 UP ({diff:+.2f}%)"
        else:
            return f"📉 DOWN ({diff:+.2f}%)"


class ErrorRateMonitor:
    """Main monitoring class for error rates."""
    
    def __init__(self, name: str = "ErrorRateMonitor"):
        self.name = name
        self.analyzer = CrossPatternAnalyzer(threshold=2.0)
        self.simulator = DataSimulator()
        self.history: List[ErrorRecord] = []
        self.running = False
    
    def start_monitoring(self, duration: int = 10, interval: float = 1.0):
        """Start monitoring error rates."""
        self.running = True
        start_time = time.time()
        
        print(f"\n🔄 Starting {self.name}...")
        print(f"   Duration: {duration}s, Interval: {interval}s\n")
        
        iteration = 0
        while self.running and (time.time() - start_time) < duration:
            try:
                record = self.simulator.generate_record()
                self.analyzer.add_record(record)
                self.history.append(record)
                
                iteration += 1
                if iteration % 5 == 0:
                    current_rate = record.error_rate
                    avg_rate = sum(r.error_rate for r in self.history[-10:]) / min(10, len(self.history))
                    trend = Visualizer.create_trend_indicator(current_rate, avg_rate)
                    
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"Rate: {current_rate:5.2f}% | "
                          f"Pattern: {record.pattern_id} | "
                          f"Status: {record.severity} | "
                          f"Trend: {trend}")
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("\n⚠️  Monitoring interrupted by user")
                break
            except Exception as e:
                print(f"❌ Error during monitoring: {e}")
                continue
        
        self.running = False
        print(f"\n✅ Monitoring stopped. Collected {len(self.history)} records.")
    
    def generate_detailed_report(self) -> str:
        """Generate a detailed monitoring report."""
        if not self.history:
            return "No data collected yet."
        
        report_lines = []
        report_lines.append("\n" + "=" * 70)
        report_lines.append("                    DETAILED MONITORING REPORT")
        report_lines.append("=" * 70)
        
        rates = [r.error_rate for r in self.history]
        report_lines.append(f"\n⏱️  Monitoring Duration: {len(self.history)} iterations")
        report_lines.append(f"📈 Real Error Rate: {sum(rates)/len(rates):.2f}%")
        
        trends = self.analyzer.analyze_trends(rates)
        report_lines.append(f"\n📊 Statistics:")
        report_lines.append(f"   • Mean Error Rate: {trends.get('mean', 0):.2f}%")
        report_lines.append(f"   • Maximum: {trends.get('max', 0):.2f}%")
        report_lines.append(f"   • Minimum: {trends.get('min', 0):.2f}%")
        report_lines.append(f"   • Samples Above Threshold: {trends.get('above_threshold', 0)}")
        report_lines.append(f"   • Cross-Pattern Count: {trends.get('cross_pattern_count', 0)}")
        
        report_lines.append(Visualizer.create_histogram(rates))
        
        report_lines.append("\n" + self.analyzer.generate_report())
        
        report_lines.append("\n" + "=" * 70)
        report_lines.append("                         END OF REPORT")
        report_lines.append("=" * 70)
        
        return "\n".join(report_lines)
    
    def export_data(self, filename: str) -> bool:
        """Export collected data to JSON file."""
        try:
            data = [asdict(record) for record in self.history]
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✅ Data exported to {filename}")
            return True
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False


class Configuration:
    """Configuration manager."""
    
    DEFAULT_CONFIG = {
        'monitoring_duration': 10,
        'interval': 1.0,
        'error_threshold': 2.0,
        'seed': None,
        'export_file': 'error_rates.json'
    }
    
    @classmethod
    def load_from_dict(cls, config: Dict) -> Dict:
        """Merge custom config with defaults."""
        result = cls.DEFAULT_CONFIG.copy()
        result.update(config)
        return result


def run_demo():
    """Run a demonstration of the error rate monitoring system."""
    print("\n" + "🎯" * 30)
    print("CROSS-PATTERN ERROR RATE MONITORING SYSTEM - DEMO")
    print("🎯" * 30)
    
    try:
        config = Configuration.load_from_dict({
            'monitoring_duration': 8,
            'interval': 0.8,
            'seed': 42
        })
        
        monitor = ErrorRateMonitor("CrossPatternMonitor")
        monitor.analyzer.threshold = config['error_threshold']
        
        monitor.simulator = DataSimulator(seed=config['seed'])
        
        monitor.start_monitoring(
            duration=config['monitoring_duration'],
            interval=config['interval']
        )
        
        print(monitor.generate_detailed_report())
        
        if len(monitor.history) >= 20:
            save = input("\n💾 Export data to JSON? (y/n): ").strip().lower()
            if save == 'y':
                monitor.export_data(config['export_file'])
        
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        raise


def run_tests():
    """Run unit tests."""
    print("\n🧪 Running tests...")
    
    tests_passed = 0
    tests_failed = 0
    
    try:
        # Test CrossPatternAnalyzer
        analyzer = CrossPatternAnalyzer(threshold=2.0)
        test_data = [2.5, 2.3, 2.1, 1.5, 2.4, 2.6, 2.2]
        patterns = analyzer.detect_cross_patterns(test_data)
        cross_patterns = [p for p in patterns if p['is_cross_pattern']]
        assert len(cross_patterns) > 0, "Should detect cross patterns"
        tests_passed += 1
        print("  ✓ CrossPatternAnalyzer test passed")
        
        # Test DataSimulator
        simulator = DataSimulator(seed=123)
        record = simulator.generate_record()
        assert isinstance(record, ErrorRecord)
        assert 0 < record.error_rate < 15
        tests_passed += 1
        print("  ✓ DataSimulator test passed")
        
        # Test ErrorRateMonitor
        monitor = ErrorRateMonitor("TestMonitor")
        assert monitor.name == "TestMonitor"
        assert len(monitor.history) == 0
        tests_passed += 1
        print("  ✓ ErrorRateMonitor test passed")
        
        # Test trends analysis
        trends = analyzer.analyze_trends(test_data)
        assert 'mean' in trends
        assert trends['mean'] > 0
        tests_passed += 1
        print("  ✓ Trends analysis test passed")
        
        # Test Visualizer
        histogram = Visualizer.create_histogram([1.0, 2.0, 3.0, 2.5, 2.2])
        assert "Error Rate Distribution" in histogram
        tests_passed += 1
        print("  ✓ Visualizer test passed")
        
        # Test configuration
        config = Configuration.load_from_dict({'seed': 999})
        assert config['seed'] == 999
        assert config['monitoring_duration'] == 10
        tests_passed += 1
        print("  ✓ Configuration test passed")
        
    except AssertionError as e:
        tests_failed += 1
        print(f"  ✗ Test failed: {e}")
    except Exception as e:
        tests_failed += 1
        print(f"  ✗ Test error: {e}")
    
    print(f"\n📋 Test Results: {tests_passed} passed, {tests_failed} failed")
    return tests_failed == 0


def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("  ERROR RATE CROSS-PATTERN ANALYSIS SYSTEM")
    print("=" * 60)
    print(f"  Python Version: {__import__('sys').version.split()[0]}")
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        mode = input("\nSelect mode:\n  1. Run Demo\n  2. Run Tests\n  3. Interactive Monitoring\n\nEnter choice (1/2/3): ").strip()
        
        if mode == '1':
            run_demo()
        elif mode == '2':
            success = run_tests()
            if success:
                print("\n✅ All tests passed!")
            else:
                print("\n❌ Some tests failed!")
        elif mode == '3':
            monitor = ErrorRateMonitor("InteractiveMonitor")
            duration = int(input("Enter monitoring duration (seconds): ") or "10")
            monitor.start_monitoring(duration=duration)
            print(monitor.generate_detailed_report())
        else:
            print("Invalid choice, running demo by default...")
            run_demo()
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Exiting...")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        return 1
    
    print("\n" + "=" * 60)
    print("  PROGRAM COMPLETED")
    print("=" * 60 + "\n")
    return 0


if __name__ == "__main__":
    exit(main())