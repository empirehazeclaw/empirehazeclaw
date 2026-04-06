#!/usr/bin/env python3
"""
Universal Business Crawler - Findet ALLE Unternehmen in Deutschland
Nicht nur IT, sondern: Handwerk, Medizin, Recht, Finance, Retail, etc.
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
import random
from datetime import datetime

# Branchen + Suchbegriffe
BRANCHEN = [
    "Handwerker",
    "Zahnarzt", 
    "Rechtsanwalt",
    "Steuerberater",
    "Immobilienmakler",
    "Fitnessstudio",
    "Restaurant",
    "Café",
    "Friseur",
    "Autowerkstatt",
    "Elektriker",
    "Maler",
    "Architekt",
    "Berater",
    "Marketing Agentur"
]

SEARCH_URL = "https://www.google.com/search"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def crawl_branchen():
    """Crawle Unternehmen nach Branche"""
    all_businesses = []
    
    for branche in BRANCHEN[:10]:  # Erste 10 Branchen
        print(f"🔍 Suche: {branche}...")
        
        # Local/Region Keywords für Deutschland
        keywords = [
            f"{branche} Deutschland",
            f"{branche} GmbH",
            f"{branche} Firma"
        ]
        
        for keyword in keywords[:2]:
            try:
                params = {"q": keyword, "num": 10}
                resp = requests.get(SEARCH_URL, params=params, headers=HEADERS, timeout=10)
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Extrahiere URLs
                for link in soup.find_all('a'):
                    href = link.get('href', '')
                    if 'http' in href and 'google' not in href:
                        # Versuche E-Mail zu finden
                        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', href)
                        
                        if email_match:
                            all_businesses.append({
                                "name": branche,
                                "email": email_match.group(),
                                "source": keyword,
                                "date": datetime.now().isoformat()
                            })
                
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                print(f"❌ Fehler: {e}")
                continue
    
    # Speichern
    with open('/home/clawbot/.openclaw/workspace/data/all_business_leads.json', 'w') as f:
        json.dump(all_businesses, f, indent=2)
    
    print(f"✅ {len(all_businesses)} Unternehmen gefunden!")
    return all_businesses

if __name__ == "__main__":
    crawl_branchen()
