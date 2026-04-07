#!/usr/bin/env python3
"""
🔒 SSL MANAGER
=============
Check and renew SSL certificates
"""

import subprocess
import os
from datetime import datetime, timedelta
from pathlib import Path

CERT_DIR = Path("/etc/letsencrypt/live")

def check_expiry():
    """Check SSL certificate expiry"""
    domains = ["empirehazeclaw.com", "empirehazeclaw.de", "empirehazeclaw.info", "empirehazeclaw.store"]
    
    results = []
    for domain in domains:
        cert_file = CERT_DIR / domain / "cert.pem"
        if cert_file.exists():
            # Get expiry date
            result = subprocess.run(
                ["openssl", "x509", "-enddate", "-noout", "-in", str(cert_file)],
                capture_output=True, text=True
            )
            results.append(f"{domain}: {result.stdout.strip()}")
        else:
            results.append(f"{domain}: No cert found")
    
    return results

def renew():
    """Renew certificates"""
    result = subprocess.run(["certbot", "renew", "--quiet"], capture_output=True, text=True)
    return result.returncode == 0

# CLI
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "renew":
        print("Renewing certificates...")
        print("✅ Renewed" if renew() else "❌ Failed")
    else:
        print("🔒 SSL Certificate Status:")
        for r in check_expiry():
            print(f"  {r}")
