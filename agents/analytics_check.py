#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          ANALYTICS CHECKER                              ║
║          Website Analytics Monitoring                   ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import json
import logging
import subprocess
from datetime import datetime

log = logging.getLogger("openclaw.analytics")

# Google Analytics
GA_MEASUREMENT_ID = os.environ.get("GA_MEASUREMENT_ID", "")
GA_API_SECRET = os.environ.get("GA_API_SECRET", "")

# Simple Analytics (Plausible alternative)
PLAUSIBLE_API = os.environ.get("PLAUSIBLE_API", "")
SITE_URL = "empirehazeclaw.com"


class AnalyticsChecker:
    """Checkt Website Analytics"""
    
    def __init__(self):
        self.data = {}
        
    async def check_all(self) -> dict:
        """Prüfe alle Analytics"""
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "websites": {},
            "summary": {}
        }
        
        # Check each site
        sites = [
            "empirehazeclaw.com",
            "empirehazeclaw.de", 
            "empirehazeclaw.store",
            "empirehazeclaw.info"
        ]
        
        for site in sites:
            results["websites"][site] = await self.check_site(site)
        
        # Summary
        results["summary"] = {
            "total_sites": len(sites),
            "all_online": all(r.get("online") for r in results["websites"].values())
        }
        
        return results
    
    async def check_site(self, site: str) -> dict:
        """Prüfe einzelne Website"""
        
        # Check if site is online (curl)
        try:
            result = subprocess.run(
                ["curl", "-sf", "-o", "/dev/null", "-w", "%{http_code}", 
                f"https://{site}"],
                capture_output=True,
                timeout=10
            )
            online = result.returncode == 0 and result.stdout.decode().strip() == "200"
            
            return {
                "online": online,
                "http_code": result.stdout.decode().strip() if result.returncode == 0 else "error",
                "checked_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            log.error(f"Fehler bei {site}: {e}")
            return {"online": False, "error": str(e)}
    
    def format_report(self, results: dict) -> str:
        """Formatiere Report"""
        
        report = f"""
📊 ANALYTICS REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M')}
{'='*50}

"""
        
        for site, data in results["websites"].items():
            status = "✅" if data.get("online") else "❌"
            code = data.get("http_code", "N/A")
            report += f"{status} {site}: {code}\n"
        
        report += f"""
{'='*50}
Summary: {results['summary']['total_sites']} Sites, Alle online: {'Ja' if results['summary']['all_online'] else 'Nein'}
"""
        
        return report


async def main():
    checker = AnalyticsChecker()
    
    print("🔍 Prüfe Analytics...")
    
    results = await checker.check_all()
    
    # Print report
    report = checker.format_report(results)
    print(report)
    
    # Save to log
    log_file = "/home/clawbot/.openclaw/workspace/logs/analytics.log"
    with open(log_file, "a") as f:
        f.write(report + "\n")
    
    return results


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
