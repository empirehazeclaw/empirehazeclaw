import requests
from bs4 import BeautifulSoup
import asyncio
import re
from crawl4ai import AsyncWebCrawler
import json
import urllib.parse

async def main():
    print("🔍 Starte Web Crawler für IT-Agenturen...")
    
    # 1. Hole Suchergebnisse via DuckDuckGo HTML mit passendem User-Agent
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    search_url = "https://html.duckduckgo.com/html/?q=IT-Agentur+Softwareentwicklung+Impressum"
    
    try:
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []
        for a in soup.find_all('a', class_='result__snippet'):
            url = a.get('href')
            if url and "duckduckgo" not in url:
                links.append(url)
                
        # Alternative falls Struktur anders ist
        if not links:
            for a in soup.find_all('a', class_='result__url'):
                url = a.get('href')
                if url:
                    links.append(url)
                    
        # Alternative 3: Alle Links filtern
        if not links:
            for a in soup.find_all('a'):
                url = a.get('href')
                if url and url.startswith('//duckduckgo.com/l/?uddg='):
                    decoded_url = urllib.parse.unquote(url.split('uddg=')[1].split('&')[0])
                    links.append(decoded_url)
        
        links = list(set(links))[:5]
        print(f"Gefundene URLs: {len(links)}")
        for l in links: print(f" - {l}")
        
    except Exception as e:
        print(f"Fehler bei DDG Suche: {e}")
        return
        
    agencies = []
    
    # 2. Crawle die gefundenen URLs mit Crawl4AI
    if links:
        async with AsyncWebCrawler() as crawler:
            for i, url in enumerate(links):
                print(f"\n[{i+1}/5] Crawle Website: {url}")
                try:
                    # Hänge /impressum an die URL an, da dort meist die E-Mail steht
                    parsed_url = urllib.parse.urlparse(url)
                    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                    impressum_url = f"{base_url}/impressum"
                    
                    print(f"Versuche Impressum: {impressum_url}")
                    site_result = await crawler.arun(url=impressum_url)
                    
                    # Falls 404, versuche Startseite
                    if not site_result.success or len(site_result.html) < 500:
                        print("Fallback zur Startseite...")
                        site_result = await crawler.arun(url=url)
                    
                    if site_result.success:
                        text = site_result.html
                        # Extrahiere Emails
                        emails = set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text))
                        
                        valid_emails = []
                        for email in emails:
                            email = email.lower()
                            if not email.endswith(('.png', '.jpg', '.gif', '.svg', '.webp', '.js', '.css')):
                                if 'w3.org' not in email and 'schema.org' not in email and 'sentry' not in email:
                                    valid_emails.append(email)
                        
                        if valid_emails:
                            # Bevorzuge generische Adressen
                            chosen_email = valid_emails[0]
                            for email in valid_emails:
                                if any(prefix in email for prefix in ['info@', 'hallo@', 'kontakt@', 'hello@', 'office@']):
                                    chosen_email = email
                                    break
                            
                            domain = base_url.replace('https://', '').replace('http://', '').replace('www.', '')
                            name = domain.split('.')[0].capitalize()
                            
                            print(f"✅ Gefunden: {name} -> {chosen_email}")
                            agencies.append({
                                "name": name,
                                "email": chosen_email,
                                "website": base_url
                            })
                        else:
                            print("❌ Keine gültige E-Mail gefunden")
                    else:
                        print("❌ Crawl fehlgeschlagen")
                except Exception as e:
                    print(f"❌ Fehler: {str(e)}")
                    
        print("\n=== ZUSAMMENFASSUNG ECHTER LEADS ===")
        print(json.dumps(agencies, indent=2))
        
        with open('/home/clawbot/.openclaw/workspace/data/real_it_leads.json', 'w') as f:
            json.dump(agencies, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
