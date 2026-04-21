#!/usr/bin/env python3
"""Sanitize all CEO workspace files - remove personal data"""
import re
from pathlib import Path

CEO_DIR = Path("/home/clawbot/.openclaw/workspace/ceo")

PATTERNS = [
    (r'sk-[a-zA-Z0-9]{20,}', '[API_KEY_REDACTED]'),
    (r'tvly[a-zA-Z0-9]{20,}', '[API_KEY_REDACTED]'),
    (r'ghp_[a-zA-Z0-9]{20,}', '[API_KEY_REDACTED]'),
    (r'x0x[a-zA-Z0-9]{20,}', '[API_KEY_REDACTED]'),
    (r'\+?[0-9]{10,}', '[PHONE_REDACTED]'),
    (r'[a-zA-Z0-9_.]+@[a-zA-Z0-9_.]+\.[a-z]{2,}', '[EMAIL_REDACTED]'),
    (r'telegram:5392634979', 'telegram:[USER_ID]'),
    (r'5392634979', '[USER_ID]'),
    (r'Nico\b', '[HUMAN_NAME]'),
    (r'\bClawBot\b', '[AGENT_NAME]'),
    (r'\bSir HazeClaw\b', '[AGENT_NAME]'),
    (r'Empire Haze Claw', '[ORG_NAME]'),
    # German addresses
    (r'[A-Z][a-z]+ Stra.ße', '[ADDRESS_REDACTED]'),
    (r'[A-Z][a-z]+ Weg', '[ADDRESS_REDACTED]'),
    (r'[A-Z][a-z]+ Platz', '[ADDRESS_REDACTED]'),
    (r'[A-Z][a-z]+ Str\.', '[ADDRESS_REDACTED]'),
    (r'[0-9]{5}', '[POSTAL_CODE]'),
]

def sanitize_file(filepath):
    try:
        content = filepath.read_text()
        original = content
        for pattern, replacement in PATTERNS:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        if content != original:
            filepath.write_text(content)
            return True
    except Exception as e:
        print(f"Error on {filepath}: {e}")
    return False

files = [
    CEO_DIR / "AGENTS.md",
    CEO_DIR / "SOUL.md", 
    CEO_DIR / "HEARTBEAT.md",
    CEO_DIR / "TOOLS.md",
    CEO_DIR / "BOOTSTRAP.md",
]

count = 0
for f in files:
    if f.exists():
        if sanitize_file(f):
            count += 1
            print(f"Sanitized: {f.name}")

print(f"\nDone. {count} files sanitized.")
