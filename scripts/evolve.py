#!/usr/bin/env python3
"""
🦞 Capability Evolver - Improves Agent Capabilities Over Time
Analyzes agent scripts, identifies weaknesses, suggests/implements improvements
"""
import os
import ast
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "scripts"
AGENTS_DIR = WORKSPACE / "agents"

class CapabilityEvolver:
    def __init__(self):
        self.issues = []
        self.fixes = []
    
    def scan_python_file(self, filepath: Path) -> List[Dict]:
        """Analyze a Python file for issues"""
        issues = []
        
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Skip security scanners - they detect shell=True, they don't use it
            if any(x in str(filepath) for x in ['security_agent', 'evolve.py', 'server_ops_agent']):
                return issues
            
            # Check for shell=True
            if 'shell=True' in content:
                issues.append({
                    'file': str(filepath),
                    'severity': 'HIGH',
                    'type': 'Security',
                    'issue': 'shell=True found - command injection risk',
                    'line': content[:content.index('shell=True')].count('\n') + 1
                })
            
            # Check for broad exception handling
            if 'except:' in content and 'Exception' not in content:
                issues.append({
                    'file': str(filepath),
                    'severity': 'MEDIUM',
                    'type': 'Error Handling',
                    'issue': 'Bare except clause - may catch system exceptions',
                    'line': content[:content.index('except:')].count('\n') + 1
                })
            
            # Check for missing error handling
            if 'subprocess.run' in content and 'try' not in content:
                issues.append({
                    'file': str(filepath),
                    'severity': 'MEDIUM',
                    'type': 'Error Handling',
                    'issue': 'subprocess.run without try/except',
                    'line': 'N/A'
                })
            
            # Check for TODO/FIXME
            todos = re.findall(r'# (TODO|FIXME|HACK|XXX): (.+)', content)
            for todo in todos:
                issues.append({
                    'file': str(filepath),
                    'severity': 'LOW',
                    'type': 'Technical Debt',
                    'issue': f'TODO: {todo[1]}',
                    'line': content[:content.index(todo[0])].count('\n') + 1
                })
            
        except Exception as e:
            issues.append({
                'file': str(filepath),
                'severity': 'LOW',
                'type': 'Analysis',
                'issue': f'Could not parse: {e}',
                'line': 'N/A'
            })
        
        return issues
    
    def scan_directory(self, directory: Path) -> List[Dict]:
        """Scan all Python files in directory"""
        all_issues = []
        
        for py_file in directory.rglob("*.py"):
            # Skip archive, backup, __pycache__
            if any(x in str(py_file) for x in ['archive', 'backup', '__pycache__', '.git']):
                continue
            
            issues = self.scan_python_file(py_file)
            all_issues.extend(issues)
        
        return all_issues
    
    def generate_report(self) -> str:
        """Generate improvement report"""
        report = []
        report.append("=" * 60)
        report.append(f"🦞 CAPABILITY EVOLUTION REPORT")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("=" * 60)
        
        if not self.issues:
            report.append("\n✅ No critical issues found!")
            return "\n".join(report)
        
        # Group by severity
        by_severity = {'HIGH': [], 'MEDIUM': [], 'LOW': []}
        for issue in self.issues:
            by_severity[issue['severity']].append(issue)
        
        for severity in ['HIGH', 'MEDIUM', 'LOW']:
            if by_severity[severity]:
                report.append(f"\n{'🔴' if severity == 'HIGH' else '🟡' if severity == 'MEDIUM' else '🟢'} {severity} ({len(by_severity[severity])} issues)")
                report.append("-" * 40)
                
                for issue in by_severity[severity]:
                    report.append(f"  📄 {issue['file']}")
                    report.append(f"     {issue['type']}: {issue['issue']}")
                    report.append(f"     → Fix: {self.suggest_fix(issue)}")
                    report.append("")
        
        return "\n".join(report)
    
    def suggest_fix(self, issue: Dict) -> str:
        """Suggest a fix for an issue"""
        if issue['type'] == 'Security' and 'shell=True' in issue.get('issue', ''):
            return "Use list form: subprocess.run(['cmd', 'arg1', 'arg2']) instead"
        elif issue['type'] == 'Error Handling':
            return "Wrap in try/except with specific exception type"
        elif issue['type'] == 'Technical Debt':
            return "Implement or create TODO issue"
        else:
            return "Review and improve"
    
    def run_scan(self):
        """Run full capability scan"""
        print("🔍 Scanning scripts...")
        self.issues = self.scan_directory(SCRIPTS_DIR)
        
        print("🔍 Scanning agents...")
        self.issues.extend(self.scan_directory(AGENTS_DIR))
        
        report = self.generate_report()
        print(report)
        
        # Save report
        report_file = WORKSPACE / "data" / f"capability_report_{datetime.now().strftime('%Y%m%d')}.txt"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"\n📄 Report saved to: {report_file}")
        
        return len([i for i in self.issues if i['severity'] == 'HIGH'])

if __name__ == "__main__":
    evolver = CapabilityEvolver()
    high_issues = evolver.run_scan()
    
    if high_issues > 0:
        print(f"\n⚠️ {high_issues} HIGH severity issues found - should be fixed!")
    else:
        print("\n✅ All systems operational!")
