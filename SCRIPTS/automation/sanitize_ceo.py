#!/usr/bin/env python3
import re
from pathlib import Path

CEO_DIR = Path("/home/clawbot/.openclaw/workspace/ceo")

GENERAL_PATTERNS = [
    (r'sk-[a-zA-Z0-9]{20,}', '[API_KEY_REDACTED]'),
    (r'tvly[a-zA-Z0-9]{20,}', '[API_KEY_REDACTED]'),
    (r'ghp_[a-zA-Z0-9]{20,}', '[API_KEY_REDACTED]'),
    (r'\+?[0-9]{10,}', '[PHONE_REDACTED]'),
    (r'[a-zA-Z0-9_.]+@[a-zA-Z0-9_.]+\.[a-z]{2,}', '[EMAIL_REDACTED]'),
]

USER_REPLACEMENTS = [
    (r'\*\*Name:\*\* Nico', '**Name:** [USER_NAME]'),
    (r'\*\*What to call them:\*\* Nico', '**What to call them:** [HUMAN]'),
    (r'telegram:5392634979', 'telegram:[USER_ID]'),
]

def sanitize_file(filepath, replacements):
    content = filepath.read_text()
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    filepath.write_text(content)

sanitize_file(CEO_DIR / "USER.md", USER_REPLACEMENTS + GENERAL_PATTERNS)
sanitize_file(CEO_DIR / "MEMORY.md", GENERAL_PATTERNS)
sanitize_file(CEO_DIR / "IDENTITY.md", GENERAL_PATTERNS)

print("CEO files sanitized")
