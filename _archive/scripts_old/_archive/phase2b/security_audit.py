#!/usr/bin/env python3
"""
Sir HazeClaw Security Audit
Prüft auf Sicherheitsrisiken.
"""

import re
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")

# Patterns to check
SUSPICIOUS_PATTERNS = [
    (r'exec\s*\(', 'exec() usage - potential code injection'),
    (r'eval\s*\(', 'eval() usage - potential code injection'),
    (r'subprocess.*shell\s*=\s*True', 'shell=True - potential command injection'),
    (r'os\.system\s*\(', 'os.system() - potential command injection'),
    (r'__import__\s*\(', '__import__() - dynamic import risk'),
    (r'\bcompile\s*\([^)]+\bfile\b', 'compile() - dynamic code risk'),
]

def scan_script(script_path):
    """Scannt ein Script auf verdächtige Patterns."""
    # Skip this script itself to avoid false positives
    if script_path.name == 'security_audit.py':
        return []
    
    try:
        content = script_path.read_text()
    except:
        return []
    
    issues = []
    for pattern, desc in SUSPICIOUS_PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            issues.append((desc, len(matches)))
    
    return issues

def generate_report():
    """Generiert Security Report."""
    scripts_dir = WORKSPACE / "scripts"
    
    results = []
    high_risk = []
    medium_risk = []
    
    for script in sorted(scripts_dir.glob("*.py")):
        if script.name.startswith('_'):
            continue
        
        issues = scan_script(script)
        if issues:
            for desc, count in issues:
                if 'exec' in desc or 'eval' in desc:
                    high_risk.append((script.name, desc, count))
                else:
                    medium_risk.append((script.name, desc, count))
    
    lines = []
    lines.append("🔒 **SECURITY AUDIT REPORT**")
    lines.append(f"_Generated: Security Scan_")
    lines.append("")
    
    # High Risk
    lines.append("**🔴 HIGH RISK ISSUES:**")
    if high_risk:
        for script, desc, count in high_risk:
            lines.append(f"  - `{script}`: {desc} ({count}x)")
    else:
        lines.append("  ✅ No high risk issues found")
    lines.append("")
    
    # Medium Risk
    lines.append("**🟡 MEDIUM RISK ISSUES:**")
    if medium_risk:
        for script, desc, count in medium_risk:
            lines.append(f"  - `{script}`: {desc} ({count}x)")
    else:
        lines.append("  ✅ No medium risk issues found")
    lines.append("")
    
    # Total
    total = len(high_risk) + len(medium_risk)
    lines.append(f"**Total Issues:** {total}")
    
    return "\n".join(lines)

if __name__ == "__main__":
    print(generate_report())
