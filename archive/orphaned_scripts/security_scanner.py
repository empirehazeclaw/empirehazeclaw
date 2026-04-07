#!/usr/bin/env python3
"""
Basic Security Scanner - Code Injection & Prompt Injection Detection
"""
import re
import sys

def scan_code_injection(code):
    """Detect potential code injection vulnerabilities"""
    patterns = [
        (r'exec\s*\(', 'Code Injection: exec()'),
        (r'eval\s*\(', 'Code Injection: eval()'),
        (r'system\s*\(', 'Code Injection: system()'),
        (r'shell_exec\s*\(', 'Code Injection: shell_exec()'),
        (r'\$\{.*\}', 'Code Injection: Variable interpolation'),
        (r'SQL.*\$\w+', 'SQL Injection risk'),
    ]
    
    issues = []
    for pattern, msg in patterns:
        if re.search(pattern, code, re.IGNORECASE):
            issues.append(msg)
    
    return issues

def scan_prompt_injection(prompt):
    """Detect potential prompt injection attempts"""
    patterns = [
        (r'ignore\s+previous', 'Prompt Injection: Ignore'),
        (r'disregard\s+instructions', 'Prompt Injection: Disregard'),
        (r'system\s*:', 'Prompt Injection: System Override'),
        (r'you\s+are\s+now', 'Prompt Injection: Role Override'),
        (r'forget\s+everything', 'Prompt Injection: Forget'),
    ]
    
    issues = []
    for pattern, msg in patterns:
        if re.search(pattern, prompt, re.IGNORECASE):
            issues.append(msg)
    
    return issues

def scan_xss(content):
    """Detect potential XSS vulnerabilities"""
    patterns = [
        (r'innerHTML\s*=', 'XSS: innerHTML'),
        (r'document\.write', 'XSS: document.write'),
        (r'<script', 'XSS: Script tag'),
        (r'on\w+\s*=', 'XSS: Event handler'),
    ]
    
    issues = []
    for pattern, msg in patterns:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(msg)
    
    return issues

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 security_scanner.py <type> <filepath>")
        print("Types: code, prompt, xss")
        sys.exit(1)
    
    type = sys.argv[1]
    filepath = sys.argv[2]
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    if type == 'code':
        issues = scan_code_injection(content)
    elif type == 'prompt':
        issues = scan_prompt_injection(content)
    elif type == 'xss':
        issues = scan_xss(content)
    else:
        print("Unknown type")
        sys.exit(1)
    
    if issues:
        print("⚠️ ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ No issues found")
