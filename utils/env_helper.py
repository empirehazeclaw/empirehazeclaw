#!/usr/bin/env python3
"""Central Environment Helper - Load all credentials"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load from multiple sources
env_paths = [
    Path.home() / ".openclaw" / ".env",
    Path.home() / ".env",
    Path(__file__).parent.parent / ".env"
]

for p in env_paths:
    if p.exists():
        load_dotenv(p)
        print(f"Loaded: {p}")

# Export common credentials
SMTP_PASS = os.getenv("SMTP_PASS", "")
