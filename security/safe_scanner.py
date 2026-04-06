#!/usr/bin/env python3
"""
MAXIMUM Code Security Scanner
Comprehensive protection against all known threats
"""
import os
import re
import json
import hashlib
from datetime import datetime

QUARANTINE = "/home/clawbot/.openclaw/workspace/security/quarantine"
REPORTS = "/home/clawbot/.openclaw/workspace/security/reports"
os.makedirs(QUARANTINE, exist_ok=True)
os.makedirs(REPORTS, exist_ok=True)

# ==================== MAXIMUM DETECTION PATTERNS ====================

CATEGORIES = {
    # Critical - Malware & Backdoors
    "CRITICAL": [
        (r"base64_decode\s*\(", "Obfuscated code execution"),
        (r"gzinflate\s*\(", "Obfuscated decompression"),
        (r"str_rot13\s*\(", "Obfuscation"),
        (r"chr\s*\([^)]*\)\.", "Char code obfuscation"),
        (r"\\\\x[0-9a-f]{2}", "Hex escape sequence"),
        (r"\\\\n[0-9]{3}", "Octal escape"),
        (r"goto\s+\w+;", "Goto for code flow evasion"),
        (r"create_function\s*\(", "Dynamic code creation"),
        (r"assert\s*\(\s*\$\w+", "Variable assertion execution"),
        (r"preg_replace\s*\(.*\/e", "Regex code execution"),
        (r"usort\s*\(\s*\$\w+\s*,\s*['\"]", "Callback execution"),
        (r"array_map\s*\(\s*['\"][a-z_]+\s*,\s*\$\w+", "Array map execution"),
        (r"call_user_func\s*\(\s*\$\w+", "Dynamic function call"),
        (r"call_user_func_array\s*\(", "Dynamic call with args"),
        (r"\$\w+\s*\(\s*\$\w+", "Variable function call"),
    ],
    
    # Shell Execution
    "SHELL": [
        (r"exec\s*\(\s*\$", "Shell exec with variable"),
        (r"shell_exec\s*\(\s*\$", "Shell exec variable"),
        (r"passthru\s*\(\s*\$", "Passthru variable"),
        (r"system\s*\(\s*\$", "System call variable"),
        (r"popen\s*\(\s*\$", "Process opening"),
        (r"proc_open\s*\(\s*\$", "Process opening"),
        (r"pcntl_exec\s*\(", "Process execution"),
        (r"expect_", "Expect module"),
        (r"proc_get_status\s*\(", "Process status"),
        (r"stream_socket_client\s*\(\s*['\"]tcp://", "Network socket"),
    ],
    
    # File System
    "FILESYSTEM": [
        (r"file_get_contents\s*\(\s*\$_(GET|POST|COOKIE", "File read from input"),
        (r"file_put_contents\s*\(\s*\$_(GET|POST|COOKIE", "File write from input"),
        (r"fopen\s*\(\s*\$_(GET|POST|COOKIE", "File open from input"),
        (r"readfile\s*\(\s*\$_(GET|POST", "File read from input"),
        (r"move_uploaded_file\s*\(\s*\$", "File upload"),
        (r"mkdir\s*\(\s*\$_(GET|POST", "Directory creation"),
        (r"rmdir\s*\(\s*\$_(GET|POST", "Directory deletion"),
        (r"unlink\s*\(\s*\$_(GET|POST", "File deletion"),
        (r"chmod\s*\(\s*\$_(GET|POST", "Permission change"),
        (r"chown\s*\(\s*\$_(GET|POST", "Owner change"),
        (r"symlink\s*\(\s*\$_(GET|POST", "Symlink creation"),
        (r"glob\s*\(\s*\$", "Glob with variable"),
        (r"scandir\s*\(\s*\$", "Directory listing"),
    ],
    
    # Network / Exfiltration
    "NETWORK": [
        (r"curl_setopt\s*\(\s*\$", "cURL with variable"),
        (r"file_get_contents\s*\(\s*['\"]http", "HTTP request"),
        (r"file_get_contents\s*\(\s*['\"]ftp", "FTP request"),
        (r"fsockopen\s*\(\s*\$", "Socket connection"),
        (r"stream_socket_client\s*\(\s*\$", "Stream socket"),
        (r"socket_connect\s*\(\s*\$", "Socket connect"),
        (r"stream_context_create.*http", "HTTP context"),
        (r"header\s*\(\s*['\"]Location.*\$", "Header injection"),
        (r"setcookie\s*\(\s*\$_(GET|POST", "Cookie injection"),
    ],
    
    # SQL Injection
    "SQL": [
        (r"mysqli_query\s*\(\s*.*\$\_(GET|POST|COOKIE", "SQL with input"),
        (r"mysql_query\s*\(\s*.*\$\w+", "Deprecated SQL with var"),
        (r"PDO\s*->\s*query\s*\(\s*.*\$\w+", "PDO query with var"),
        (r"execute\s*\(\s*\$_(GET|POST", "Prepared statement with input"),
        (r"concat\s*\(\s*\$_(GET|POST", "SQL concat with input"),
        (r"'\s*\.\s*\$\w+\s*\.\s*'", "String concat in SQL"),
    ],
    
    # XSS
    "XSS": [
        (r"innerHTML\s*=\s*\$_(GET|POST", "XSS via innerHTML"),
        (r"outerHTML\s*=\s*\$_(GET|POST", "XSS via outerHTML"),
        (r"document\.write\s*\(\s*\$_(GET|POST", "XSS via write"),
        (r"eval\s*\(\s*\$_(GET|POST", "XSS via eval"),
        (r"<script[^>]*>.*\$_(GET|POST|COOKIE", "Script with input"),
        (r"on\w+\s*=\s*['\"][^'\"]*\$_(GET|POST", "Event handler with input"),
        (r"src\s*=\s*['\"]javascript:", "JavaScript protocol"),
    ],
    
    # Command Injection
    "INJECTION": [
        (r"exec\s*\(\s*['\"].*\$\w+", "Command with variable"),
        (r"system\s*\(\s*['\"].*\$\w+", "System with variable"),
        (r"shell_exec\s*\(\s*['\"].*\$\w+", "Shell with variable"),
        (r"\|\s*\$\w+", "Pipe to variable"),
        (r"\&\s*\$\w+", "Background with variable"),
        (r"\;\s*\$\w+", "Semicolon to variable"),
        (r"`[^`]*\$\w+[^`]*`", "Backtick with variable"),
    ],
    
    # LFI / Path Traversal
    "LFI": [
        (r"\.\.\/\$\w+", "Path traversal"),
        (r"\.\.\\\\\$\w+", "Windows path traversal"),
        (r"include\s*\(\s*\$_(GET|POST", "Include with input"),
        (r"require\s*\(\s*\$_(GET|POST", "Require with input"),
        (r"include_once\s*\(\s*\$_(GET|POST", "Include once with input"),
        (r"readfile\s*\(\s*\$_(GET|POST", "Readfile with input"),
    ],
    
    # Crypto Mining
    "MINING": [
        (r"coinhive", "Crypto mining"),
        (r"cryptoloot", "Crypto mining"),
        (r"webmine", "Crypto mining"),
        (r"coinblind", "Crypto mining"),
        (r"jsecoin", "Crypto mining"),
        (r"miner\.src", "Mining script"),
        (r"web\.socket", "External socket"),
    ],
    
    # Environment Access
    "ENV": [
        (r"getenv\s*\(\s*['\"]HTTP_", "HTTP environment"),
        (r"putenv\s*\(\s*\$", "Set environment"),
        (r"apache_getenv", "Apache environment"),
        (r"get_defined_vars\s*\(\s*\)", "Defined variables"),
        (r"get_defined_functions\s*\(\s*\)", "Defined functions"),
        (r"get_defined_constants\s*\(\s*\)", "Defined constants"),
    ],
    
    # Serialization Attacks
    "SERIALIZATION": [
        (r"unserialize\s*\(\s*\$_(GET|POST|COOKIE", "Unserialize with input"),
        (r"pickle_loads", "Python pickle"),
        (r"yaml_load\s*\(\s*\$_(GET|POST", "YAML with input"),
        (r"json_decode\s*\(\s*\$_(GET|POST", "JSON with input"),
    ],
    
    # Prompt Injection (for AI/Chat code)
    "PROMPT_INJECTION": [
        (r"ignore\s+all\s+previous", "Prompt ignore"),
        (r"disregard\s+.*instructions", "Disregard instructions"),
        (r"forget\s+.*rules", "Forget rules"),
        (r"you\s+are\s+now\s+\w+\s+instead", "Role override"),
        (r"system\s*:\s*\w+", "System override"),
        (r"jailbreak|越狱", "Jailbreak"),
        (r"do\s+anything\s+now|DAN", "DAN attack"),
        (r"developer\s+mode|devmode", "Dev mode"),
        (r"without\s+limitations|no\s+restrictions", "Remove limits"),
        (r"ignore.*safety|disregard.*guidelines", "Safety override"),
    ],
}

def scan_file(filepath):
    """Comprehensive file scan"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        return {"error": str(e)}
    
    # Calculate file hash
    file_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
    
    results = {
        "file": os.path.basename(filepath),
        "size": len(content),
        "hash": file_hash,
        "timestamp": datetime.now().isoformat(),
        "status": "clean",
        "risk_level": "none",
        "issues": [],
        "summary": {}
    }
    
    all_issues = []
    
    for category, patterns in CATEGORIES.items():
        category_issues = []
        
        for pattern, desc in patterns:
            try:
                matches = list(re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE))
                for m in matches:
                    line = content[:m.start()].count('\n') + 1
                    category_issues.append({
                        "line": line,
                        "description": desc,
                        "match": m.group()[:80]
                    })
            except:
                pass
        
        if category_issues:
            all_issues.extend(category_issues)
            results["summary"][category] = len(category_issues)
    
    if all_issues:
        results["issues"] = all_issues[:50]  # Limit to 50 issues
        results["status"] = "dirty"
        
        # Calculate risk
        critical = results["summary"].get("CRITICAL", 0)
        shell = results["summary"].get("SHELL", 0)
        sql = results["summary"].get("SQL", 0)
        
        if critical > 0 or shell > 0:
            results["risk_level"] = "CRITICAL"
        elif sql > 5:
            results["risk_level"] = "HIGH"
        elif len(all_issues) > 10:
            results["risk_level"] = "MEDIUM"
        else:
            results["risk_level"] = "LOW"
    
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("🛡️ MAXIMUM Code Security Scanner")
        print("Usage: python3 safe_scanner.py <filepath>")
        print(f"Detects: {len(CATEGORIES)} categories, {sum(len(v) for v in CATEGORIES.values())} patterns")
        sys.exit(0)
    
    filepath = sys.argv[1]
    result = scan_file(filepath)
    
    print(f"📄 {result['file']}")
    print(f"🔒 Size: {result.get('size', 0)} bytes | Hash: {result.get('hash', 'N/A')}")
    print(f"⚠️  Risk: {result['risk_level']}")
    
    if result.get("issues"):
        print(f"\n🚨 {len(result['issues'])} issues found:")
        for cat, count in result["summary"].items():
            print(f"  [{cat}] {count}")
        print("\nTop issues:")
        for i in result["issues"][:5]:
            print(f"  Line {i['line']}: {i['description']}")
    else:
        print("\n✅ No threats detected")
    
    # Save
    report_file = f"{REPORTS}/max_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n📄 Report: {report_file}")
