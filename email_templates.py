#!/usr/bin/env python3
"""Email Template Manager"""
import os

TEMPLATES = {
    "local_closer": "data/local-closer/offer_template.txt",
    "outreach": "data/outreach_template.txt",
    "followup": "data/followup_template.txt"
}

def list_templates():
    print("=== 📧 EMAIL TEMPLATES ===")
    for name, path in TEMPLATES.items():
        exists = "✅" if os.path.exists(path) else "❌"
        print(f"{exists} {name}: {path}")

def show_template(name):
    if name not in TEMPLATES:
        return f"❌ Not found: {name}"
    
    path = TEMPLATES[name]
    if not os.path.exists(path):
        return f"❌ Missing: {path}"
    
    with open(path) as f:
        return f.read()

if __name__ == "__main__":
    import sys
    list_templates()
