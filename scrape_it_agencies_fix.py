import requests
from bs4 import BeautifulSoup
import asyncio
import re
from crawl4ai import AsyncWebCrawler
import json
import urllib.parse

async def main():
    print("🔍 Starte Crawler für IT-Agenturen...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    search_url = "https://html.duckduckgo.com/html/?q=IT-Agentur+Softwareentwicklung+Impressum"
    
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    links = []
    for a in soup.find_all('a'):
        url = a.get('href')
        if url and 'uddg=' in url:
            try:
                # Extrahiere die echte URL aus dem DuckDuckGo-Redirect
                actual_url = urllib.parse.unquote(url.split('uddg=')[1].split('&')[0])
                if actual_url.startswith('http'):
                    links.append(actual_url)
            except:
                pass
                
    links = list(set(links))[:5]
    print(f"Gefundene echte URLs: {len(links)}")
    for l in links: print(f" - {l}")
    
    agencies = []
    
    if links:
        async with AsyncWebCrawler() as crawler:
            for i, url in enumerate(links):
                print(f"\n[{i+1}/5] Crawle Website: {url}")
                try:
                    site_result = await crawler.arun(url=url)
                    
                    if site_result.success:
                        text = site_result.html
                        emails = set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text))
                        
                        valid_emails = []
                        for email in emails:
                            email = email.lower()
                            if not email.endswith(('.png', '.jpg', '.gif', '.svg', '.webp', '.js', '.css', '.woff2')):
                                if 'w3.org' not in email and 'schema.org' not in email and 'sentry' not in email and 'example' not in email:
                                    valid_emails.append(email)
                        
                        if not valid_emails:
                            # Versuche Impressum
                            impressum_url = url.rstrip('/') + '/impressum'
                            print(f"  -> Keine E-Mail auf Startseite. Versuche {impressum_url}")
                            imp_result = await crawler.arun(url=impressum_url)
                            if imp_result.success:
                                imp_emails = set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', imp_result.html))
                                for email in imp_emails:
                                    email = email.lower()
                                    if not email.endswith(('.png', '.jpg', '.gif', '.svg', '.webp', '.js', '.css')):
                                        if 'w3.org' not in email and 'schema.org' not in email and 'example' not in email:
                                            valid_emails.append(email)
                        
                        if valid_emails:
                            chosen_email = valid_emails[0]
                            for email in valid_emails:
                                if any(prefix in email for prefix in ['info@', 'hallo@', 'kontakt@', 'hello@', 'office@']):
                                    chosen_email = email
                                    break
                            
                            domain = urllib.parse.urlparse(url).netloc.replace('www.', '')
                            name = domain.split('.')[0].capitalize()
                            
                            print(f"✅ Gefunden: {name} -> {chosen_email}")
                            agencies.append({
                                "name": name,
                                "email": chosen_email,
                                "website": url
                            })
                        else:
                            print("❌ Keine E-Mail gefunden")
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
