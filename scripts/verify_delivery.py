#!/usr/bin/env python3
"""
LINK VERIFIER - Pruft alle URLs vor dem Senden

Usage:
    python3 verify_delivery.py <file.md>
    python3 verify_delivery.py --check "https://example.com"
"""

import sys
import re
import requests
from pathlib import Path

TIMEOUT = 5
HEADERS = {'User-Agent': 'Mozilla/5.0'}

TAGS = {
    'verified': '[VERIFIED]',
    'unverified': '[UNVERIFIED]',
    'constructed': '[CONSTRUCTED-FALSCH]'
}

def extract_urls(text):
    url_pattern = r'https?://[^\s<>"\']+'
    return re.findall(url_pattern, text)

def check_url(url):
    try:
        r = requests.head(url, timeout=TIMEOUT, headers=HEADERS, allow_redirects=True)
        return (url, r.status_code, "OK" if r.status_code == 200 else f"HTTP {r.status_code}")
    except Exception as e:
        return (url, 0, str(e)[:30])

def verify_file(filepath):
    path = Path(filepath)
    if not path.exists():
        return {"error": f"File not found: {filepath}"}
    
    content = path.read_text()
    urls = extract_urls(content)
    
    if not urls:
        return {"urls": [], "verified": 0, "unverified": 0}
    
    results = []
    for url in urls:
        url, status, msg = check_url(url)
        results.append({"url": url, "status": status, "msg": msg})
    
    verified = sum(1 for r in results if r["status"] == 200)
    
    return {
        "file": filepath,
        "total_urls": len(urls),
        "verified": verified,
        "unverified": len(urls) - verified,
        "results": results
    }

def print_report(report):
    print("=" * 60)
    print("VERIFICATION REPORT")
    print("=" * 60)
    
    if "error" in report:
        print(f"ERROR: {report['error']}")
        return
    
    print(f"File: {report['file']}")
    print(f"Total URLs: {report['total_urls']}")
    print(f"VERIFIED: {report['verified']}")
    print(f"UNVERIFIED: {report['unverified']}")
    print("-" * 60)
    
    for r in report['results']:
        icon = "OK" if r['status'] == 200 else "FAIL"
        print(f"[{icon}] {r['status']} - {r['msg']}")
        print(f"     {r['url'][:70]}")
    
    print("=" * 60)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    if sys.argv[1] == "--check":
        url = sys.argv[2]
        url, status, msg = check_url(url)
        print(f"[{'OK' if status == 200 else 'FAIL'}] {status} - {msg}")
        print(f"URL: {url}")
    else:
        report = verify_file(sys.argv[1])
        print_report(report)