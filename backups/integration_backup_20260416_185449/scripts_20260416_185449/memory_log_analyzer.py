#!/usr/bin/env python3
"""
Memory & Log Analyzer for Agent Self-Improver

Extracts learning signals from:
- Daily memory files (memory/YYYY-MM-DD.md)
- Log files (logs/*.log, logs/*.json)
- Session corpora (.dreams/session-corpus/)

Usage:
    python3 memory_log_analyzer.py              # Full analysis
    python3 memory_log_analyzer.py --memory    # Memory only
    python3 memory_log_analyzer.py --logs      # Logs only
    python3 memory_log_analyzer.py --summary   # Quick summary
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "ceo" / "memory"
LOGS_DIR = WORKSPACE / "logs"
DREAMS_DIR = MEMORY_DIR / ".dreams"

# Key patterns to look for
SUCCESS_PATTERNS = [
    r'✅.*complete[d]?',
    r'passed|success|working',
    r'fixed|resolved|solved',
    r'improved|optimized|better',
    r'approved|confirmed|valid',
]

FAILURE_PATTERNS = [
    r'❌.*error',
    r'failed|broken|crashed',
    r'warning|alarm|alert',
    r'fixme|bug|issue',
    r'rejected|invalid|failed',
]

DECISION_PATTERNS = [
    r'decision:?\s*(.+)',
    r'chose|selected|decided',
    r'choosing between (.+) and (.+)',
    r'went with (.+)',
]


class MemoryLogAnalyzer:
    """Analyze memory files and logs for learning signals."""
    
    def __init__(self):
        self.memory_dir = MEMORY_DIR
        self.logs_dir = LOGS_DIR
        self.dreams_dir = DREAMS_DIR
    
    def extract_memory_signals(self, limit_days: int = 7) -> List[Dict]:
        """Extract signals from memory files."""
        signals = []
        
        if not self.memory_dir.exists():
            print(f"   ⚠️ Memory dir not found: {self.memory_dir}")
            return signals
        
        # Get memory files
        memory_files = sorted(self.memory_dir.glob("2026-*.md"))
        
        for mem_file in memory_files[-limit_days:]:
            try:
                with open(mem_file, 'r') as f:
                    content = f.read()
                
                # Extract date from filename
                date_str = mem_file.stem[:10]
                
                # Find success signals
                for pattern in SUCCESS_PATTERNS:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches[:5]:  # Limit per pattern
                        signals.append({
                            "source": "memory",
                            "date": date_str,
                            "type": "success",
                            "content": match[:200] if isinstance(match, str) else str(match)[:200],
                            "file": mem_file.name
                        })
                
                # Find failure signals
                for pattern in FAILURE_PATTERNS:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches[:3]:
                        signals.append({
                            "source": "memory",
                            "date": date_str,
                            "type": "failure",
                            "content": match[:200] if isinstance(match, str) else str(match)[:200],
                            "file": mem_file.name
                        })
                
                # Extract decisions (looking for key decisions)
                decision_lines = []
                for line in content.split('\n'):
                    if any(kw in line.lower() for kw in ['decision:', 'decided', 'chose', 'selected']):
                        decision_lines.append(line.strip()[:150])
                
                for dl in decision_lines[:5]:
                    signals.append({
                        "source": "memory",
                        "date": date_str,
                        "type": "decision",
                        "content": dl,
                        "file": mem_file.name
                    })
                    
            except Exception as e:
                print(f"   ❌ Error reading {mem_file}: {e}")
        
        return signals
    
    def extract_log_signals(self, limit_hours: int = 48) -> List[Dict]:
        """Extract signals from log files."""
        signals = []
        
        if not self.logs_dir.exists():
            print(f"   ⚠️ Logs dir not found: {self.logs_dir}")
            return signals
        
        cutoff_time = datetime.now() - timedelta(hours=limit_hours)
        
        # Process log files
        for log_file in self.logs_dir.glob("*.log"):
            try:
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mtime < cutoff_time:
                    continue
                
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                
                file_signals = {
                    "success_count": 0,
                    "failure_count": 0,
                    "errors": [],
                    "warnings": []
                }
                
                for line in lines[-500:]:  # Last 500 lines
                    line_lower = line.lower()
                    
                    if '✅' in line or 'passed' in line_lower or 'success' in line_lower:
                        file_signals["success_count"] += 1
                    if '❌' in line or 'error' in line_lower or 'failed' in line_lower:
                        file_signals["failure_count"] += 1
                        if 'error:' in line_lower:
                            file_signals["errors"].append(line.strip()[:100])
                    if 'warning' in line_lower or '⚠️' in line:
                        file_signals["warnings"].append(line.strip()[:100])
                
                if file_signals["success_count"] > 0 or file_signals["failure_count"] > 0:
                    signals.append({
                        "source": "log",
                        "file": log_file.name,
                        "type": "summary",
                        "success_count": file_signals["success_count"],
                        "failure_count": file_signals["failure_count"],
                        "sample_errors": file_signals["errors"][:3],
                        "sample_warnings": file_signals["warnings"][:3]
                    })
                    
            except Exception as e:
                print(f"   ❌ Error reading {log_file}: {e}")
        
        # Also check JSON logs
        for json_file in self.logs_dir.glob("*.json"):
            if json_file.stat().st_size > 100000:  # Skip large files
                continue
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    # Take last 50 entries
                    for entry in data[-50:]:
                        if isinstance(entry, dict):
                            entry_str = json.dumps(entry)
                            if 'error' in entry_str.lower() or 'failed' in entry_str.lower():
                                signals.append({
                                    "source": "json_log",
                                    "file": json_file.name,
                                    "type": "error_entry",
                                    "content": entry_str[:200]
                                })
            except:
                pass
        
        return signals
    
    def extract_session_insights(self) -> List[Dict]:
        """Extract insights from session corpus."""
        insights = []
        
        corpus_dir = self.dreams_dir / "session-corpus"
        if not corpus_dir.exists():
            return insights
        
        # Get recent session files
        session_files = sorted(corpus_dir.glob("2026-04-*.txt"))[-3:]
        
        for session_file in session_files:
            try:
                with open(session_file, 'r') as f:
                    content = f.read()
                
                # Look for repeated patterns
                lines = content.split('\n')
                line_counts = Counter(lines)
                
                # Find most repeated non-trivial lines
                repeated = []
                for line, count in line_counts.most_common(20):
                    line = line.strip()
                    if len(line) > 30 and count >= 2 and not line.startswith('['):
                        repeated.append({
                            "content": line[:150],
                            "count": count
                        })
                
                if repeated:
                    insights.append({
                        "source": "session_corpus",
                        "file": session_file.name,
                        "type": "repeated_patterns",
                        "patterns": repeated[:10]
                    })
                    
            except Exception as e:
                print(f"   ❌ Error reading {session_file}: {e}")
        
        return insights
    
    def analyze_and_store(self) -> Dict:
        """Run full analysis and return insights."""
        print("\n" + "="*60)
        print("🔍 MEMORY & LOG ANALYZER")
        print("="*60)
        
        # Memory signals
        print("\n📚 Analyzing memory files...")
        memory_signals = self.extract_memory_signals(limit_days=7)
        print(f"   Found {len(memory_signals)} memory signals")
        
        # Log signals
        print("\n📋 Analyzing log files...")
        log_signals = self.extract_log_signals(limit_hours=48)
        print(f"   Found {len(log_signals)} log signals")
        
        # Session insights
        print("\n💭 Analyzing session corpus...")
        session_insights = self.extract_session_insights()
        print(f"   Found {len(session_insights)} session insights")
        
        # Compile insights
        insights = {
            "timestamp": datetime.now().isoformat(),
            "memory_signals": memory_signals,
            "log_signals": log_signals,
            "session_insights": session_insights,
            "summary": {
                "total_memory_signals": len(memory_signals),
                "total_log_signals": len(log_signals),
                "total_session_insights": len(session_insights),
                "success_signals": len([s for s in memory_signals if s.get("type") == "success"]),
                "failure_signals": len([s for s in memory_signals if s.get("type") == "failure"]),
                "decisions": len([s for s in memory_signals if s.get("type") == "decision"])
            }
        }
        
        return insights
    
    def get_patterns_from_insights(self, insights: Dict) -> Tuple[List[Dict], List[Dict]]:
        """Convert insights into patterns and warnings for learning store."""
        patterns = []
        warnings = []
        
        # From memory signals
        for signal in insights.get("memory_signals", []):
            if signal.get("type") == "success":
                patterns.append({
                    "name": f"memory:{signal.get('content', '')[:40]}",
                    "context": signal.get("source"),
                    "description": signal.get("content", "")[:200],
                    "source": "memory_analysis"
                })
            elif signal.get("type") == "failure":
                warnings.append({
                    "pattern": f"memory:{signal.get('content', '')[:40]}",
                    "context": signal.get("source"),
                    "description": signal.get("content", "")[:200],
                    "source": "memory_analysis"
                })
        
        # From log signals
        for signal in insights.get("log_signals", []):
            if signal.get("failure_count", 0) > signal.get("success_count", 0):
                warnings.append({
                    "pattern": f"log:{signal.get('file', '')}",
                    "context": "log_analysis",
                    "description": f"{signal.get('failure_count')} failures vs {signal.get('success_count')} successes",
                    "source": "log_analysis"
                })
            elif signal.get("success_count", 0) > signal.get("failure_count", 0) * 2:
                patterns.append({
                    "name": f"log:{signal.get('file', '')}",
                    "context": "log_analysis",
                    "description": f"{signal.get('success_count')} successes (healthy)",
                    "source": "log_analysis"
                })
        
        return patterns, warnings


def main():
    """Main CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Memory & Log Analyzer for Agent Self-Improver")
    parser.add_argument("--memory", action="store_true", help="Memory only")
    parser.add_argument("--logs", action="store_true", help="Logs only")
    parser.add_argument("--summary", action="store_true", help="Quick summary")
    parser.add_argument("--output", metavar="FILE", help="Save output to JSON file")
    
    args = parser.parse_args()
    
    analyzer = MemoryLogAnalyzer()
    
    if args.memory:
        signals = analyzer.extract_memory_signals()
        print(json.dumps(signals, indent=2))
    elif args.logs:
        signals = analyzer.extract_log_signals()
        print(json.dumps(signals, indent=2))
    elif args.summary:
        insights = analyzer.analyze_and_store()
        print(json.dumps(insights["summary"], indent=2))
    else:
        insights = analyzer.analyze_and_store()
        
        # Get patterns and warnings
        patterns, warnings = analyzer.get_patterns_from_insights(insights)
        
        print(f"\n📊 SUMMARY:")
        print(f"   Memory signals: {insights['summary']['total_memory_signals']}")
        print(f"   Log signals: {insights['summary']['total_log_signals']}")
        print(f"   Session insights: {insights['summary']['total_session_insights']}")
        print(f"   Success signals: {insights['summary']['success_signals']}")
        print(f"   Failure signals: {insights['summary']['failure_signals']}")
        print(f"   Decisions: {insights['summary']['decisions']}")
        print(f"\n📝 Patterns extracted: {len(patterns)}")
        print(f"⚠️ Warnings extracted: {len(warnings)}")
        
        if args.output:
            output = {
                "insights": insights,
                "patterns": patterns,
                "warnings": warnings
            }
            with open(args.output, 'w') as f:
                json.dump(output, f, indent=2)
            print(f"   Saved to {args.output}")


if __name__ == "__main__":
    main()
