#!/usr/bin/env python3
import os
from os import getenv
"""Outreach Agent - Uses environment variables for credentials"""
import os

# Load from environment (secure!)
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_PASS = os.getenv("SMTP_PASS", "")  # Must be set in environment!

# ... rest of the agent
print(f"✅ Outreach Agent using SMTP: {SMTP_HOST}")
print(f"   User: {SMTP_USER}")
print("   Password: [FROM ENV]")
