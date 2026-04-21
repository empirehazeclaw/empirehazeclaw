#!/usr/bin/env python3
"""
Memory Sanitizer - Removes personal data, API keys, names, addresses
Usage: python3 sanitize_memory.py [--dry-run]
"""
import re
import json
import sys
from pathlib import Path

MEMORY_DIR = Path("/home/clawbot/.openclaw/workspace/ceo/memory")

# Patterns to redact
PATTERNS = [
    # API Keys (MiniMax, OpenRouter, Tavily, Stripe, etc.)
    (r'sk-[a-zA-Z0-9]{20,}', '[API_KEY_REDACTED]'),
    (r'tvly[a-zA-Z0-9]{20,}', '[API_KEY_REDACTED]'),
    (r'ghp_[a-zA-Z0-9]{20,}', '[API_KEY_REDACTED]'),
    (r'x0x[a-zA-Z0-9]{20,}', '[API_KEY_REDACTED]'),
    # Generic secrets
    (r'secret[_-]?key', '[SECRET_REDACTED]'),
    (r'api[_-]?key', '[API_KEY_REDACTED]'),
    (r'password', '[PASSWORD_REDACTED]'),
    (r'token', '[TOKEN_REDACTED]'),
    # Personal names - simple heuristic: capitalized word pairs
    # (handled separately below)
    # Addresses (German)
    (r'[A-Z][a-z]+ Stra.ße', '[ADDRESS_REDACTED]'),
    (r'[A-Z][a-z]+ Weg', '[ADDRESS_REDACTED]'),
    (r'[A-Z][a-z]+ Platz', '[ADDRESS_REDACTED]'),
    # Phone numbers
    (r'\+?[0-9]{10,}', '[PHONE_REDACTED]'),
    # Email
    (r'[a-zA-Z0-9_.]+@[a-zA-Z0-9_.]+\.[a-z]{2,}', '[EMAIL_REDACTED]'),
    # Telegram IDs
    (r'telegram:[0-9]+', 'telegram:[ID_REDACTED]'),
    (r'chat_id[=: ][0-9]+', '[CHAT_ID_REDACTED]'),
    # UUID patterns that look like user/session IDs
    (r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '[ID_REDACTED]'),
]

# Names to redact (from USER.md or known)
NAMES_TO_REDACT = ['Nico', 'ClawBot', 'Sir HazeClaw', 'Empire Haze Claw', 'HazeClaw']

def sanitize_text(text: str) -> str:
    """Apply all redaction patterns to text."""
    for pattern, replacement in PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def sanitize_file(filepath: Path, dry_run: bool = True) -> dict:
    """Sanitize a single file."""
    try:
        content = filepath.read_text()
        original = content
        
        # Apply pattern redactions
        content = sanitize_text(content)
        
        # Redact known names
        for name in NAMES_TO_REDACT:
            content = re.sub(rf'\b{re.escape(name)}\b', '[NAME_REDACTED]', content)
        
        if not dry_run and content != original:
            filepath.write_text(content)
        
        return {
            'file': str(filepath),
            'changed': content != original,
            'size': len(content)
        }
    except Exception as e:
        return {'file': str(filepath), 'error': str(e)}

def main():
    dry_run = '--dry-run' in sys.argv
    mode = 'DRY RUN' if dry_run else 'LIVE'
    
    print(f"=== Memory Sanitizer ({mode}) ===\n")
    
    files = list(MEMORY_DIR.rglob("*.md")) + list(MEMORY_DIR.rglob("*.json"))
    print(f"Scanning {len(files)} files...")
    
    results = []
    for f in files:
        if '.dreams' in str(f) or 'archive' in str(f):
            continue  # Skip dreams/archive for now
        r = sanitize_file(f, dry_run)
        results.append(r)
    
    changed = [r for r in results if r.get('changed')]
    print(f"\nFiles scanned: {len(results)}")
    print(f"Files to change: {len(changed)}")
    
    if changed:
        print(f"\nFiles that would be modified:")
        for r in changed[:10]:
            print(f"  - {r['file']}")
        if len(changed) > 10:
            print(f"  ... and {len(changed) - 10} more")
    
    if dry_run:
        print(f"\nRun without --dry-run to apply changes")
    else:
        print(f"\nSanitization complete!")

if __name__ == "__main__":
    main()
