#!/usr/bin/env python3
"""Quick System Status"""
import subprocess
import os
from datetime import datetime

def check_service(name, port):
    """Check if service is running"""
    result = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", 
                             f"http://localhost:{port}/"], capture_output=True, text=True)
    return "✅" if result.stdout == "200" else "❌"

print(f"=== 📊 SYSTEM STATUS ({datetime.now().strftime('%H:%M')}) ===")
print("")

# Check services
services = [
    ("AI Chatbot", 8896),
    ("Lead Generator", 8895),
    ("Trading Bot", 8001),
    ("SEO Tool", 8898),
    ("Dashboard", 8890)
]

for name, port in services:
    status = check_service(name, port)
    print(f"{status} {name}: {port}")

print("")
print("📧 Email: Check .env")
print("💰 Stripe: Check config")
