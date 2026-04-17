#!/usr/bin/env python3
"""
Cross-Pattern Analysis Script
Analyzes patterns and calculates error rates.
"""

import sys
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from collections import Counter


@dataclass
class PatternResult:
    """Container for pattern analysis results."""
    pattern_id: str
    occurrences: int
    error_count: int
    error_rate: float
    status: str


class PatternAnalyzer:
    """Analyzes cross-pattern data and computes metrics."""

    def __init__(self):
        self.patterns: Dict[str, List[str]] = {}
        self.results: List[PatternResult] = []
        self.total_analyzed = 0
        self.total_errors = 0

    def load_patterns(self, data: List[str]) -> bool:
        """Load patterns from data list."""
        try:
            for item in data:
                if not isinstance(item, str):
                    raise TypeError(f"Expected string, got {type(item)}")
                parts = item.split(':')
                if len(parts) >= 2:
                    pattern_type = parts[0].strip()
                    pattern_data = ':'.join(parts[1:])
                    if pattern_type not in self.patterns:
                        self.patterns[pattern_type] = []
                    self.patterns[pattern_type].append(pattern_data)
            return True
        except Exception as e:
            print(f"Error loading patterns: {e}")
            return False

    def analyze_cross_pattern(self, pattern_list: List[str]) -> PatternResult:
        """Analyze a specific cross-pattern."""
        try:
            pattern_id = f"PATTERN_{len(self.results) + 1}"
            occurrences = len(pattern_list)
            errors = sum(1 for p in pattern_list if 'ERROR' in p.upper() or 'FAIL' in p.upper())
            error_rate = (errors / occurrences * 100) if occurrences > 0 else 0.0
            
            return PatternResult(
                pattern_id=pattern_id,
                occurrences=occurrences,
                error_count=errors,
                error_rate=round(error_rate, 2),
                status="OK" if error_rate < 5 else "WARNING"
            )
        except ZeroDivisionError:
            return PatternResult(pattern_id="ERROR", occurrences=0, error_count=0, error_rate=0.0, status="ERROR")
        except Exception as e:
            raise RuntimeError(f"Analysis failed: {e}")

    def process_all(self) -> List[PatternResult]:
        """Process all loaded patterns."""
        try:
            for pattern_type, pattern_data in self.patterns.items():
                result = self.analyze_cross_pattern(pattern_data)
                self.results.append(result)
                self.total_analyzed += result.occurrences
                self.total_errors += result.error_count
            return self.results
        except Exception as e:
            print(f"Error processing patterns: {e}")
            return []

    def get_summary(self) -> Dict[str, Any]:
        """Get analysis summary statistics."""
        try:
            total_rate = (self.total_errors / self.total_analyzed * 100) if self.total_analyzed > 0 else 0.0
            return {
                'total_patterns': len(self.results),
                'total_analyzed': self.total_analyzed,
                'total_errors': self.total_errors,
                'overall_error_rate': round(total_rate, 2),
                'warnings': sum(1 for r in self.results if r.status == "WARNING")
            }
        except Exception as e:
            return {'error': str(e)}


class DataValidator:
    """Validates input data for pattern analysis."""

    @staticmethod
    def validate_input(data: Any) -> bool:
        """Validate input data format."""
        try:
            if data is None:
                return False
            if isinstance(data, list) and len(data) == 0:
                return True
            if not isinstance(data, list):
                return False
            for item in data:
                if not isinstance(item, str):
                    return False
            return True
        except Exception:
            return False

    @staticmethod
    def sanitize_input(data: List[str]) -> List[str]:
        """Sanitize input data by removing invalid entries."""
        sanitized = []
        for item in data:
            try:
                clean = re.sub(r'[^\w\s:.-]', '', str(item))
                if clean.strip():
                    sanitized.append(clean.strip())
            except Exception:
                continue
        return sanitized


class ReportGenerator:
    """Generates analysis reports."""

    @staticmethod
    def generate_text_report(analyzer: PatternAnalyzer) -> str:
        """Generate a plain text report."""
        try:
            lines = []
            lines.append("=" * 50)
            lines.append("CROSS-PATTERN ANALYSIS REPORT")
            lines.append("=" * 50)
            lines.append("")
            
            summary = analyzer.get_summary()
            lines.append(f"Total Patterns Analyzed: {summary.get('total_patterns', 0)}")
            lines.append(f"Total Items Analyzed: {summary.get('total_analyzed', 0)}")
            lines.append(f"Total Errors Found: {summary.get('total_errors', 0)}")
            lines.append(f"Overall Error Rate: {summary.get('overall_error_rate', 0)}%")
            lines.append(f"Warnings: {summary.get('warnings', 0)}")
            lines.append("")
            
            for result in analyzer.results:
                lines.append(f"Pattern ID: {result.pattern_id}")
                lines.append(f"  Occurrences: {result.occurrences}")
                lines.append(f"  Errors: {result.error_count}")
                lines.append(f"  Error Rate: {result.error_rate}%")
                lines.append(f"  Status: {result.status}")
                lines.append("")
            
            lines.append("=" * 50)
            return "\n".join(lines)
        except Exception as e:
            return f"Error generating report: {e}"

    @staticmethod
    def generate_json_report(analyzer: PatternAnalyzer) -> str:
        """Generate a JSON-style report."""
        try:
            import json
            summary = analyzer.get_summary()
            results = [
                {
                    'pattern_id': r.pattern_id,
                    'occurrences': r.occurrences,
                    'error_count': r.error_count,
                    'error_rate': r.error_rate,
                    'status': r.status
                }
                for r in analyzer.results
            ]
            report = {
                'summary': summary,
                'results': results
            }
            return json.dumps(report, indent=2)
        except Exception as e:
            return f'{{"error": "{e}"}}'


def create_sample_data() -> List[str]:
    """Create sample data for demonstration."""
    samples = [
        "CROSS-PATTERN:sample_data_001",
        "CROSS-PATTERN:sample_data_002",
        "CROSS-PATTERN:sample_data_003",
        "CROSS-PATTERN:ERROR_sample_004",
        "CROSS-PATTERN:sample_data_005",
        "CROSS-PATTERN:FAIL_sample_006",
        "CROSS-PATTERN:sample_data_007",
        "CROSS-PATTERN:sample_data_008",
        "CROSS-PATTERN:ERROR_sample_009",
        "CROSS-PATTERN:sample_data_010",
        "CROSS-PATTERN:sample_data_011",
        "CROSS-PATTERN:sample_data_012",
        "CROSS-PATTERN:sample_data_013",
        "CROSS-PATTERN:sample_data_014",
        "CROSS-PATTERN:sample_data_015",
        "CROSS-PATTERN:sample_data_016",
        "CROSS-PATTERN:sample_data_017",
        "CROSS-PATTERN:sample_data_018",
        "CROSS-PATTERN:sample_data_019",
        "CROSS-PATTERN:sample_data_020",
        "CROSS-PATTERN:sample_data_021",
        "CROSS-PATTERN:sample_data_022",
        "CROSS-PATTERN:sample_data_023",
        "CROSS-PATTERN:sample_data_024",
        "CROSS-PATTERN:sample_data_025",
        "CROSS-PATTERN:sample_data_026",
        "CROSS-PATTERN:sample_data_027",
        "CROSS-PATTERN:sample_data_028",
        "CROSS-PATTERN:sample_data_029",
        "CROSS-PATTERN:sample_data_030",
        "CROSS-PATTERN:sample_data_031",
        "CROSS-PATTERN:sample_data_032",
        "CROSS-PATTERN:sample_data_033",
        "CROSS-PATTERN:sample_data_034",
        "CROSS-PATTERN:sample_data_035",
        "CROSS-PATTERN:sample_data_036",
        "CROSS-PATTERN:sample_data_037",
        "CROSS-PATTERN:sample_data_038",
        "CROSS-PATTERN:sample_data_039",
        "CROSS-PATTERN:sample_data_040",
        "CROSS-PATTERN:sample_data_041",
        "CROSS-PATTERN:sample_data_042",
        "CROSS-PATTERN:sample_data_043",
        "CROSS-PATTERN:sample_data_044",
        "CROSS-PATTERN:sample_data_045",
        "CROSS-PATTERN:sample_data_046",
        "CROSS-PATTERN:sample_data_047",
        "CROSS-PATTERN:sample_data_048",
        "CROSS-PATTERN:sample_data_049",
        "CROSS-PATTERN:sample_data_050",
    ]
    return samples


def run_analysis(data: List[str], verbose: bool = True) -> bool:
    """Run the complete analysis pipeline."""
    try:
        if not DataValidator.validate_input(data):
            print("Error: Invalid input data format")
            return False

        sanitized = DataValidator.sanitize_input(data)
        
        analyzer = PatternAnalyzer()
        
        if not analyzer.load_patterns(sanitized):
            print("Error: Failed to load patterns")
            return False

        results = analyzer.process_all()
        
        if not results:
            print("Warning: No results generated")
            return False

        if verbose:
            report = ReportGenerator.generate_text_report(analyzer)
            print(report)

        summary = analyzer.get_summary()
        print(f"\n📈 Real Error Rate: {summary.get('overall_error_rate', 0)}%")
        
        return True

    except MemoryError:
        print("Error: Out of memory")
        return False
    except RecursionError:
        print("Error: Recursion limit exceeded")
        return False
    except Exception as e:
        print(f"Error during analysis: {e}")
        return False


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the script."""
    try:
        print("Starting Cross-Pattern Analysis...")
        print("")

        data = create_sample_data()
        
        success = run_analysis(data, verbose=True)
        
        if success:
            print("\nAnalysis completed successfully.")
            return 0
        else:
            print("\nAnalysis failed.")
            return 1

    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user.")
        return 130
    except SystemExit as e:
        return e.code if e.code else 0
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())