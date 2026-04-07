#!/usr/bin/env python3
"""
Input Sanitizer - Security Module for OpenClaw
Bereinigt und validiert alle User-Inputs bevor sie an AI-Modelle oder Scripts gehen.
"""

import re
import html
from urllib.parse import urlparse
from typing import Tuple, List, Optional

class InputSanitizer:
    """Bereinigt User-Inputs für maximale Sicherheit"""
    
    # 🚨 Gefährliche Patterns die geblockt werden
    BLOCKED_PATTERNS = [
        # Command Injection
        r'rm\s+-rf\s+/',
        r'curl\s+.*\|\s*sh',
        r'wget\s+.*\|\s*sh',
        r':\(\)\{',  # Fork bomb
        r'sudo\s+',
        r'chmod\s+777',
        r'chown\s+',
        
        # Prompt Injection / Jailbreak
        r'ignore\s+(previous|all|above)\s+instructions',
        r'deny\s+(your|the)\s+(programming|system)',
        r'forget\s+(everything|all|your)',
        r'new\s+system\s+(prompt|message|instruction)',
        r'direct\s+mode',
        r'DAN\s+',
        r'jailbreak',
        r'roleplay\s+as\s+(?!.*helper)',
        r'you\s+are\s+now\s+(?!.*helpful)',
        
        # XSS / HTML Injection
        r'<script[^>]*>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe',
        r'<object',
        r'<embed',
        
        # SQL Injection
        r"'\s*OR\s+'1'\s*=\s*'1",
        r'UNION\s+SELECT',
        r'--\s*$',
        
        # Path Traversal
        r'\.\./',
        r'\.\.\\',
        r'/etc/passwd',
        r'C:\\Windows',
    ]
    
    # ⚠️ WarnPatterns - werden nur markiert, nicht geblockt
    WARNING_PATTERNS = [
        r'delete\s+all',
        r'format\s+disk',
        r'drop\s+table',
        r'truncate',
        r'shutdown',
        r'reboot',
        r'kill\s+-9',
        r'chmod\s+600',
    ]
    
    def __init__(self):
        self.blocked_regex = [re.compile(p, re.IGNORECASE) for p in self.BLOCKED_PATTERNS]
        self.warning_regex = [re.compile(p, re.IGNORECASE) for p in self.WARNING_PATTERNS]
        
    def sanitize(self, text: str, max_length: int = 10000) -> Tuple[bool, str, List[str]]:
        """
        Bereinigt einen Input.
        
        Returns:
            (is_safe, sanitized_text, warnings)
        """
        if not text:
            return True, "", []
        
        warnings = []
        
        # 1. Length Check
        if len(text) > max_length:
            text = text[:max_length]
            warnings.append(f"Text wurde auf {max_length} Zeichen gekürzt")
        
        # 2. HTML Entity Encoding (XSS Prevention)
        text = html.escape(text)
        
        # 3. Blocked Patterns Check
        for pattern in self.blocked_regex:
            if pattern.search(text):
                return False, "", [f"BLOCKED: Gefährliches Pattern gefunden"]
        
        # 4. Warning Patterns Check
        for pattern in self.warning_regex:
            match = pattern.search(text)
            if match:
                warnings.append(f"⚠️ Achtung: Potenziell riskantes Pattern '{match.group()}'")
        
        # 5. URL Validation
        urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text)
        for url in urls:
            if not self.is_safe_url(url):
                return False, "", [f"BLOCKED: Unsichere URL {url}"]
        
        return True, text, warnings
    
    def is_safe_url(self, url: str) -> bool:
        """Prüft ob eine URL sicher ist"""
        try:
            parsed = urlparse(url)
            
            # Block dangerous protocols
            if parsed.scheme not in ('http', 'https'):
                return False
            
            # Block dangerous domains
            blocked_domains = [
                'localhost', '127.0.0.1', '0.0.0.0',
                '.tk', '.ml', '.ga', '.cf', '.gq',  # Free domains often used for phishing
            ]
            
            if any(d in parsed.netloc.lower() for d in blocked_domains):
                return False
                
            return True
        except:
            return False
    
    def sanitize_filename(self, filename: str) -> str:
        """Bereinigt einen Dateinamen"""
        # Remove path traversal
        filename = filename.replace('../', '').replace('..\\', '')
        
        # Remove dangerous characters
        filename = re.sub(r'[^\w\s.-]', '', filename)
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:255-len(ext)] + '.' + ext if ext else name[:255]
        
        return filename
    
    def sanitize_command(self, command: str) -> Tuple[bool, str]:
        """Bereinigt einen Shell-Befehl"""
        # Block dangerous commands
        dangerous = ['rm -rf', 'dd if=', 'mkfs', '> /dev/sd', 'chmod 777']
        
        for cmd in dangerous:
            if cmd in command.lower():
                return False, ""
        
        return True, command


def main():
    """CLI Interface für Testing"""
    import sys
    
    sanitizer = InputSanitizer()
    
    if len(sys.argv) > 1:
        # Test mode
        test_input = ' '.join(sys.argv[1:])
        is_safe, result, warnings = sanitizer.sanitize(test_input)
        
        print(f"Input: {test_input}")
        print(f"Safe: {is_safe}")
        print(f"Result: {result}")
        print(f"Warnings: {warnings}")
    else:
        # Interactive mode
        print("🛡️ Input Sanitizer - Test Mode")
        print("-" * 40)
        
        while True:
            user_input = input("\n✏️ Input (q=quit): ")
            if user_input.lower() == 'q':
                break
                
            is_safe, result, warnings = sanitizer.sanitize(user_input)
            
            if is_safe:
                print(f"✅ Safe!")
                if warnings:
                    for w in warnings:
                        print(f"  {w}")
            else:
                print(f"❌ BLOCKED!")
                for w in warnings:
                    print(f"  {w}")


if __name__ == "__main__":
    main()
