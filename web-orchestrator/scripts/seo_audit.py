#!/usr/bin/env python3
"""
🔍 Web Orchestrator - Weekly SEO Audit
Analysiert alle 4 Domains auf SEO-Probleme
"""
import requests
import re
import json
from datetime import datetime

DOMAINS = [
    {"name": "de", "url": "https://empirehazeclaw.de", "lang": "de"},
    {"name": "com", "url": "https://empirehazeclaw.com", "lang": "en"},
    {"name": "info", "url": "https://empirehazeclaw.info", "lang": "de/en"},
    {"name": "store", "url": "https://empirehazeclaw.store", "lang": "de/en"},
]

REPORT_FILE = "/home/clawbot/.openclaw/workspace/web-orchestrator/monitoring/seo_audit_report.json"

def audit_domain(domain):
    """SEO Audit für eine Domain"""
    url = domain["url"]
    issues = []
    warnings = []
    passed = []
    
    try:
        html = requests.get(url, timeout=15, headers={"User-Agent": "SEO-AuditBot/1.0"}).text
        
        # Title Check
        title = re.search(r'<title[^>]*>([^<]+)</title>', html)
        if title:
            t = title.group(1).strip()
            if len(t) < 30:
                warnings.append(f"Title zu kurz ({len(t)} chars): {t[:50]}")
            elif len(t) > 60:
                warnings.append(f"Title zu lang ({len(t)} chars): {t[:50]}")
            else:
                passed.append(f"Title OK ({len(t)} chars)")
        else:
            issues.append("KEIN <title> gefunden!")
        
        # Meta Description
        desc = re.search(r'<meta name="description" content="([^"]+)"', html)
        if desc:
            d = desc.group(1)
            if len(d) < 120:
                warnings.append(f"Meta Description kurz ({len(d)} chars)")
            elif len(d) > 160:
                warnings.append(f"Meta Description lang ({len(d)} chars)")
            else:
                passed.append("Meta Description OK")
        else:
            issues.append("KEINE Meta Description!")
        
        # H1 Check
        h1 = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
        if h1:
            passed.append(f"H1 gefunden: {h1.group(1)[:30]}...")
        else:
            issues.append("KEIN <h1> gefunden!")
        
        # Multiple H1s
        h1s = re.findall(r'<h1[^>]*>([^<]+)</h1>', html)
        if len(h1s) > 1:
            warnings.append(f"Mehrere H1s gefunden ({len(h1s)})")
        
        # Image Alt Tags
        imgs = re.findall(r'<img[^>]*>', html)
        missing_alt = [img for img in imgs if 'alt=' not in img.lower()]
        if missing_alt:
            warnings.append(f"{len(missing_alt)} Bilder ohne Alt-Tag")
        else:
            passed.append(f"Alle {len(imgs)} Bilder haben Alt-Tags")
        
        # Script Count (performance)
        scripts = re.findall(r'<script[^>]*>', html)
        if len(scripts) > 5:
            warnings.append(f"Viele Scripts ({len(scripts)}) - Performance beachten")
        else:
            passed.append(f"Scripts OK ({len(scripts)})")
        
        # Favicon
        favicon = re.search(r'<link[^>]*rel="icon"[^>]*>', html) or re.search(r'<link[^>]*href="[^"]*favicon', html)
        if favicon:
            passed.append("Favicon vorhanden")
        else:
            warnings.append("KEIN Favicon gefunden")
        
        # Canonical
        canonical = re.search(r'<link[^>]*rel="canonical"[^>]*>', html)
        if canonical:
            passed.append("Canonical URL vorhanden")
        else:
            warnings.append("KEIN Canonical Tag")
        
        # OG Tags (for social)
        og_tags = ["og:title", "og:description", "og:image", "og:url"]
        missing_og = [t for t in og_tags if f'property="{t}"' not in html and f'name="{t}"' not in html]
        if missing_og:
            warnings.append(f"Fehlende OG Tags: {', '.join(missing_og)}")
        else:
            passed.append("Alle OG Tags vorhanden")
        
        return {
            "domain": domain["name"],
            "url": url,
            "lang": domain["lang"],
            "issues": issues,
            "warnings": warnings,
            "passed": passed,
            "score": max(0, 100 - len(issues) * 20 - len(warnings) * 5),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "domain": domain["name"],
            "url": url,
            "error": str(e),
            "issues": [f"ERROR: {e}"],
            "warnings": [],
            "passed": [],
            "score": 0,
            "timestamp": datetime.now().isoformat()
        }

def main():
    print("🔍 Web Orchestrator - Weekly SEO Audit")
    print("=" * 50)
    
    results = []
    for domain in DOMAINS:
        print(f"\nAuditing {domain['name']}.empirehazeclaw.{domain['name']}...")
        result = audit_domain(domain)
        results.append(result)
        
        print(f"  Score: {result['score']}/100")
        print(f"  Issues: {len(result['issues'])}")
        print(f"  Warnings: {len(result['warnings'])}")
        print(f"  Passed: {len(result['passed'])}")
    
    # Save report
    with open(REPORT_FILE, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "domains": results,
            "summary": {
                "avg_score": round(sum(r['score'] for r in results) / len(results), 1),
                "total_issues": sum(len(r['issues']) for r in results),
                "total_warnings": sum(len(r['warnings']) for r in results)
            }
        }, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 SEO AUDIT SUMMARY")
    print("=" * 50)
    
    for r in results:
        status = "🟢" if r['score'] >= 80 else "🟡" if r['score'] >= 50 else "🔴"
        print(f"{status} {r['domain']}: {r['score']}/100 ({len(r['issues'])} issues, {len(r['warnings'])} warnings)")
    
    avg = sum(r['score'] for r in results) / len(results)
    print(f"\n📈 Average Score: {avg}/100")
    
    # Alert if bad scores
    bad = [r for r in results if r['score'] < 50]
    if bad:
        print(f"\n⚠️ DOMAINS MIT AKTIONSPFLICHT:")
        for r in bad:
            print(f"  - {r['domain']}: {r['score']}/100")
            for issue in r['issues'][:3]:
                print(f"    ❌ {issue}")
    
    return 0 if avg >= 70 else 1

if __name__ == "__main__":
    exit(main())
