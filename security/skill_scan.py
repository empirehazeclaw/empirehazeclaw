#!/usr/bin/env python3
"""
Skill Security Scanner — ClawHub Vetting Process
Scans skill directories for malicious patterns before installation
"""

import sys
import os
import re
from pathlib import Path

MALICIOUS_PATTERNS = [
    # Environment theft
    (r"os\.environ\.get\(['\"]", "ENV_READ", "CRITICAL", "Reading environment variables"),
    (r"process\.env\(['\"]", "ENV_READ", "CRITICAL", "Reading process environment"),
    (r"\.getenv\(['\"]", "ENV_READ", "HIGH", "Getting environment variables"),
    (r"dotenv\.config\(\)", "ENV_READ", "MEDIUM", "Loading dotenv (may expose secrets)"),
    
    # Exec injection
    (r"exec\s*\(\s*(?:user|input|param)", "EXEC_INJECTION", "CRITICAL", "exec with user input"),
    (r"eval\s*\([^)]*(?:user|input|param)", "EXEC_INJECTION", "CRITICAL", "eval with user input"),
    (r"subprocess.*shell\s*=\s*True", "EXEC_INJECTION", "CRITICAL", "subprocess shell=True"),
    (r"\$(?:\{?\()?.*(?:user|input|param)", "EXEC_INJECTION", "HIGH", "Command injection via $()"),
    (r"\`(?:\{?)?.*(?:user|input|param)", "EXEC_INJECTION", "HIGH", "Command injection via backticks"),
    
    # Data exfiltration
    (r"fetch\s*\(\s*['\"]http", "DATA_EXFIL", "HIGH", "HTTP fetch (potential exfil)"),
    (r"requests\.get.*(?:user|input|param)", "DATA_EXFIL", "HIGH", "requests.get with user input"),
    (r"http.*exfil", "DATA_EXFIL", "CRITICAL", "HTTP exfiltration detected"),
    (r"curl.*\|", "DATA_EXFIL", "CRITICAL", "curl pipe (potential exfil)"),
    (r"wget.*(?:user|input)", "DATA_EXFIL", "HIGH", "wget with user input"),
    
    # Network scanning
    (r"socket\.connect", "NETWORK", "MEDIUM", "Socket connection"),
    (r"net\.createServer", "NETWORK", "MEDIUM", "Creating network server"),
    
    # File theft
    (r"fs\.readFile.*(?:credential|secret|key|\.env)", "FILE_THEFT", "CRITICAL", "Reading credential files"),
    (r"readFileSync.*(?:credential|secret|key|\.env)", "FILE_THEFT", "CRITICAL", "Reading credential files"),
    (r"cat\s+(?:/|\$HOME).*\.env", "FILE_THEFT", "CRITICAL", "Reading .env via cat"),
    
    # Suspicious patterns
    (r"child_process\.execFile", "EXEC_INJECTION", "HIGH", "execFile usage"),
    (r"require\s*\(\s*['\"].*['\"]\s*\+", "DYNAMIC_REQUIRE", "HIGH", "Dynamic require with concat"),
]

BLOCKED_PACKAGE_PATTERNS = [
    r"^env-stealer", r"^dotenv-grab", r"^secrets-", r"^api-key-",
    r"^token-", r"^creds-", r"^key-", r"^shell-", r"^exec-",
    r"^bash-", r"^code-", r"^eval-", r"^remote-", r"^system-",
    r"stealer$", r"grab$", r"injector$", r"exfiltrat", r"exfil$",
]


def scan_file(filepath, content):
    """Scan a single file for malicious patterns"""
    findings = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        for pattern, pattern_id, severity, description in MALICIOUS_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                findings.append({
                    'file': filepath,
                    'line': i,
                    'pattern_id': pattern_id,
                    'severity': severity,
                    'description': description,
                    'content': line.strip()[:100]
                })
    
    return findings


def scan_directory(directory):
    """Recursively scan directory for malicious patterns"""
    all_findings = []
    
    for root, dirs, files in os.walk(directory):
        # Skip node_modules and hidden dirs
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git'] and not d.startswith('.')]
        
        for file in files:
            if file.endswith(('.js', '.ts', '.py', '.sh', '.bash')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    findings = scan_file(filepath, content)
                    all_findings.extend(findings)
                except Exception as e:
                    pass  # Skip unreadable files
    
    return all_findings


def check_package_blocklist(pkg_name):
    """Check if package is on blocklist"""
    for pattern in BLOCKED_PACKAGE_PATTERNS:
        if re.match(pattern, pkg_name, re.IGNORECASE):
            return True, pattern
    return False, None


def main():
    if len(sys.argv) < 2:
        print("Usage: skill_scan.py <skill_directory|package_name>")
        print("       skill_scan.py --check-package <name>")
        sys.exit(1)
    
    if sys.argv[1] == '--check-package':
        pkg_name = sys.argv[2] if len(sys.argv) > 2 else ''
        blocked, pattern = check_package_blocklist(pkg_name)
        if blocked:
            print(f"🚨 BLOCKED: {pkg_name} matches blocked pattern: {pattern}")
            sys.exit(1)
        else:
            print(f"✅ {pkg_name} not on blocklist")
            sys.exit(0)
    
    target = sys.argv[1]
    
    if os.path.isdir(target):
        print(f"🔍 Scanning skill directory: {target}")
        findings = scan_directory(target)
        
        if findings:
            print(f"\n🚨 FOUND {len(findings)} SECURITY ISSUES:")
            for f in findings:
                print(f"  [{f['severity']}] {f['file']}:{f['line']}")
                print(f"      {f['description']}")
                print(f"      -> {f['content']}")
            sys.exit(1)
        else:
            print("✅ No malicious patterns detected")
            sys.exit(0)
    else:
        print(f"❌ Not a directory: {target}")
        sys.exit(1)


if __name__ == "__main__":
    main()
