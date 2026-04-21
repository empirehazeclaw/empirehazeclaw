#!/usr/bin/env python3
"""
Phase 6.1.1: Session Context Analyzer
======================================
Analysiert den aktuellen Session-Kontext auf Token-Verschwendung.

Was es macht:
1. Sammelt Session-Metriken (Token-Verbrauch, Message-Count, etc.)
2. Identifiziert ineffiziente Patterns
3. Schlägt Pruning-Strategien vor
4. Reportet an KG

Usage:
    python3 session_context_analyzer.py [--verbose] [--fix]
"""

import json
import sys
import os
from datetime import datetime, timedelta
from collections import Counter
import re

# Paths
WORKSPACE = os.environ.get('WORKSPACE', '/home/clawbot/.openclaw/workspace/ceo')
KG_DIR = f"{WORKSPACE}/memory/kg"
MEMORY_DIR = f"{WORKSPACE}/memory"
SCRIPTS_DIR = f"{WORKSPACE}/scripts"

class SessionContextAnalyzer:
    def __init__(self):
        self.session_metrics = {
            'timestamp': datetime.now().isoformat(),
            'analyzer_version': '1.0.0',
            'phase': '6.1.1'
        }
        self.issues = []
        self.recommendations = []
        
    def run_full_analysis(self):
        """Main analysis pipeline."""
        print("🔍 Session Context Analyzer — Phase 6.1.1")
        print("=" * 50)
        
        # 1. Analyze session history size
        session_size = self.analyze_session_size()
        
        # 2. Check for token waste patterns
        token_waste = self.identify_token_waste()
        
        # 3. Analyze message patterns
        msg_patterns = self.analyze_message_patterns()
        
        # 4. Check context relevance
        relevance = self.check_context_relevance()
        
        # 5. Generate recommendations
        self.generate_recommendations()
        
        # 6. Output report
        self.print_report()
        
        # 7. Save to KG if possible
        self.save_to_kg()
        
        return self.session_metrics
    
    def analyze_session_size(self):
        """Analyze how big the session context is."""
        metrics = {}
        
        # Check recent memory files for session data
        memory_dir = f"{WORKSPACE}/memory"
        if os.path.exists(memory_dir):
            files = os.listdir(memory_dir)
            md_files = [f for f in files if f.endswith('.md') and f.startswith('2')]
            
            # Get file sizes
            total_size = 0
            for f in md_files:
                path = os.path.join(memory_dir, f)
                if os.path.isfile(path):
                    total_size += os.path.getsize(path)
            
            metrics['total_memory_files'] = len(md_files)
            metrics['total_memory_size_kb'] = total_size / 1024
            metrics['estimated_tokens'] = (total_size * 4) // 3  # rough estimate
        
        # Check session history if available
        session_file = f"{WORKSPACE}/.openclaw/sessions/current/session.json"
        if os.path.exists(session_file):
            size = os.path.getsize(session_file)
            metrics['session_file_size_kb'] = size / 1024
            metrics['session_tokens_estimate'] = (size * 4) // 3
        else:
            # Try alternate paths
            alt_paths = [
                f"{WORKSPACE}/.openclaw/sessions/session.json",
                f"{WORKSPACE}/.openclaw/session.json"
            ]
            for path in alt_paths:
                if os.path.exists(path):
                    size = os.path.getsize(path)
                    metrics['session_file_size_kb'] = size / 1024
                    metrics['session_tokens_estimate'] = (size * 4) // 3
                    break
        
        self.session_metrics['session_size'] = metrics
        
        # Check thresholds
        size_kb = metrics.get('session_file_size_kb', 0)
        if size_kb > 500:
            self.issues.append({
                'type': 'session_size',
                'severity': 'HIGH',
                'message': f'Session File sehr groß: {size_kb:.1f}KB (threshold: 500KB)',
                'suggestion': 'Context Pruning erforderlich'
            })
        elif size_kb > 200:
            self.issues.append({
                'type': 'session_size',
                'severity': 'MED',
                'message': f'Session File groß: {size_kb:.1f}KB (threshold: 200KB)',
                'suggestion': 'Baldige Session-Rotation empfohlen'
            })
        
        return metrics
    
    def identify_token_waste(self):
        """Identify patterns that waste tokens."""
        waste_patterns = []
        
        # Common token waste patterns:
        # 1. Repetitive status checks
        # 2. Long error traces repeated
        # 3. Repeated tool outputs
        # 4. Long system prompts repeated
        
        # Check memory/short_term/current.md for session patterns
        current_md = f"{WORKSPACE}/memory/short_term/current.md"
        if os.path.exists(current_md):
            try:
                with open(current_md, 'r') as f:
                    content = f.read()
                
                # Look for repetitive patterns
                lines = content.split('\n')
                if len(lines) > 100:
                    # Check for repeated status sections
                    status_count = content.count('## Status')
                    if status_count > 5:
                        waste_patterns.append({
                            'pattern': 'multiple_status_sections',
                            'severity': 'MED',
                            'description': f'{status_count} Status-Sektionen gefunden (Redundanz)',
                            'tokens_wasted': '~500-2000'
                        })
                        
            except Exception as e:
                print(f"Warning: Could not read current.md: {e}")
        
        # Check for log spam
        log_patterns = [
            (r'\[INFO\].*\[INFO\].*\[INFO\]', 'Repeated INFO logs'),
            (r'.*HEARTBEAT_OK.*HEARTBEAT_OK', 'Repeated heartbeat checks'),
            (r'Cron.*Cron.*Cron', 'Repeated cron status'),
        ]
        
        # Estimate token waste
        total_waste = sum(int(w.get('tokens_wasted', '0').replace('~', '').split('-')[0]) 
                         for w in waste_patterns if w.get('tokens_wasted'))
        
        self.session_metrics['token_waste'] = {
            'patterns': waste_patterns,
            'estimated_total': total_waste
        }
        
        return waste_patterns
    
    def analyze_message_patterns(self):
        """Analyze message patterns in the session."""
        patterns = {
            'total_messages': 0,
            'avg_message_length': 0,
            'long_messages': 0,
            'short_messages': 0,
            'tool_calls': 0,
            'replies': 0
        }
        
        # Check short_term files for message data
        short_term_dir = f"{WORKSPACE}/memory/short_term"
        if os.path.exists(short_term_dir):
            for f in os.listdir(short_term_dir):
                if f.endswith('.md'):
                    path = os.path.join(short_term_dir, f)
                    try:
                        with open(path, 'r') as fh:
                            content = fh.read()
                            # Very rough estimation
                            patterns['total_messages'] += content.count('\n##') // 2
                    except:
                        pass
        
        self.session_metrics['message_patterns'] = patterns
        return patterns
    
    def check_context_relevance(self):
        """Check how relevant the current context is."""
        relevance = {
            'score': 0.0,  # 0-1
            'factors': [],
            'oldest_fact_age_days': 0
        }
        
        # Check how old the facts in long_term are
        long_term_facts = f"{WORKSPACE}/memory/long_term/facts.md"
        if os.path.exists(long_term_facts):
            try:
                with open(long_term_facts, 'r') as f:
                    content = f.read()
                
                # Look for dates
                date_matches = re.findall(r'(\d{4}-\d{2}-\d{2})', content)
                if date_matches:
                    oldest = min(date_matches)
                    # Parse and calculate age
                    try:
                        dt = datetime.strptime(oldest, '%Y-%m-%d')
                        age = (datetime.now() - dt).days
                        relevance['oldest_fact_age_days'] = age
                        relevance['factors'].append(f'Oldest fact: {age} days old')
                    except:
                        pass
            except:
                pass
        
        # Estimate relevance score based on issues found
        issue_count = len(self.issues)
        if issue_count == 0:
            relevance['score'] = 0.9
        elif issue_count <= 2:
            relevance['score'] = 0.7
        elif issue_count <= 5:
            relevance['score'] = 0.5
        else:
            relevance['score'] = 0.3
        
        self.session_metrics['context_relevance'] = relevance
        return relevance
    
    def generate_recommendations(self):
        """Generate actionable recommendations based on analysis."""
        
        # Based on issues found
        if any(i['type'] == 'session_size' and i['severity'] == 'HIGH' 
               for i in self.issues):
            self.recommendations.append({
                'priority': 'P1',
                'action': 'session_rotation',
                'description': 'Session-Rotation sofort durchführen',
                'expected_tokens_saved': '30-50%'
            })
        
        # Token waste recommendations
        waste = self.session_metrics.get('token_waste', {})
        if waste.get('estimated_total', 0) > 100:
            self.recommendations.append({
                'priority': 'P2',
                'action': 'prune_repetitive_content',
                'description': 'Repetitive Status-Sektionen komprimieren',
                'expected_tokens_saved': '~500-2000'
            })
        
        # Context relevance recommendations
        rel = self.session_metrics.get('context_relevance', {})
        if rel.get('score', 1.0) < 0.7:
            self.recommendations.append({
                'priority': 'P2',
                'action': 'context_cleanup',
                'description': 'Relevantere Informationen priorisieren',
                'expected_tokens_saved': '~1000-3000'
            })
        
        # Always add these baseline recommendations
        self.recommendations.append({
            'priority': 'P3',
            'action': 'enable_auto_pruning',
            'description': 'Automatisiertes Context Pruning aktivieren',
            'expected_tokens_saved': '10-20%/session'
        })
        
        self.session_metrics['recommendations'] = self.recommendations
    
    def print_report(self):
        """Print a formatted report."""
        print("\n📊 SESSION CONTEXT ANALYSIS REPORT")
        print("-" * 50)
        
        # Session Size
        size = self.session_metrics.get('session_size', {})
        if size:
            print(f"\n📦 Session Size:")
            print(f"   Memory Files: {size.get('total_memory_files', 'N/A')}")
            print(f"   Memory Size: {size.get('total_memory_size_kb', 0):.1f} KB")
            print(f"   Session File: {size.get('session_file_size_kb', 0):.1f} KB")
            print(f"   Est. Tokens: {size.get('session_tokens_estimate', 0):,}")
        
        # Token Waste
        waste = self.session_metrics.get('token_waste', {})
        patterns = waste.get('patterns', [])
        if patterns:
            print(f"\n⚠️ Token Waste Patterns ({len(patterns)} found):")
            for p in patterns:
                print(f"   [{p.get('severity', '?')}] {p.get('description', 'Unknown')}")
                print(f"           Tokens: ~{p.get('tokens_wasted', '?')}")
        else:
            print(f"\n✅ No significant token waste patterns found")
        
        # Context Relevance
        rel = self.session_metrics.get('context_relevance', {})
        print(f"\n🎯 Context Relevance: {rel.get('score', 0)*100:.0f}%")
        for factor in rel.get('factors', []):
            print(f"   - {factor}")
        
        # Issues
        if self.issues:
            print(f"\n🚨 Issues Found ({len(self.issues)}):")
            for i in self.issues:
                print(f"   [{i.get('severity', '?')}] {i.get('message', 'Unknown')}")
                print(f"           → {i.get('suggestion', '')}")
        
        # Recommendations
        if self.recommendations:
            print(f"\n💡 Recommendations ({len(self.recommendations)}):")
            for r in self.recommendations:
                print(f"   [{r.get('priority', '?')}] {r.get('description', 'Unknown')}")
                print(f"           Expected savings: {r.get('expected_tokens_saved', '?')}")
        
        print("\n" + "=" * 50)
        
    def save_to_kg(self):
        """Save analysis results to KG."""
        # Create a KG entry for this analysis
        kg_entry = {
            'type': 'session_analysis',
            'timestamp': self.session_metrics['timestamp'],
            'version': self.session_metrics['analyzer_version'],
            'phase': self.session_metrics['phase'],
            'session_size_kb': self.session_metrics.get('session_size', {}).get('session_file_size_kb', 0),
            'token_waste_estimate': self.session_metrics.get('token_waste', {}).get('estimated_total', 0),
            'context_relevance_score': self.session_metrics.get('context_relevance', {}).get('score', 0),
            'issues_count': len(self.issues),
            'recommendations_count': len(self.recommendations)
        }
        
        # Save to a JSON file for later KG sync
        output_file = f"{WORKSPACE}/memory/short_term/session_analysis_latest.json"
        try:
            with open(output_file, 'w') as f:
                json.dump(kg_entry, f, indent=2)
            print(f"\n💾 Analysis saved to: {output_file}")
        except Exception as e:
            print(f"\n⚠️ Could not save to KG: {e}")


def main():
    analyzer = SessionContextAnalyzer()
    
    # Check for --fix flag
    if '--fix' in sys.argv:
        print("⚠️ Fix mode requested but not yet implemented")
        print("   (Session rotation requires careful handling)")
    
    # Run analysis
    metrics = analyzer.run_full_analysis()
    
    # Exit with appropriate code
    issue_count = len(metrics.get('issues', []))
    if issue_count > 3:
        sys.exit(1)  # High issue count
    elif issue_count > 0:
        sys.exit(2)  # Some issues
    else:
        sys.exit(0)  # Clean


if __name__ == '__main__':
    main()
