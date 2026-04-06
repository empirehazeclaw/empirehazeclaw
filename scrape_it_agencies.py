import asyncio
import re
from crawl4ai import AsyncWebCrawler
from bs4 import BeautifulSoup
import json

async def main():
    print("🔍 Starte Web Crawler (Crawl4AI) für IT-Agenturen...")
    
    search_url = "https://html.duckduckgo.com/html/?q=IT+Agentur+Softwareentwicklung+Impressum"
    
    agencies = []
    
    async with AsyncWebCrawler() as crawler:
        print(f"Crawle Suchergebnisse: {search_url}")
        result = await crawler.arun(url=search_url)
        
        if result.success:
            soup = BeautifulSoup(result.html, 'html.parser')
            links = []
            for a in soup.find_all('a', class_='result__url'):
                url = a.get('href')
                if url and "http" in url and "duckduckgo" not in url:
                    links.append(url)
            
            # Limitiere auf die ersten 5 Ergebnisse um Zeit zu sparen
            links = list(set(links))[:5]
            print(f"Gefundene URLs: {links}")
            
            for url in links:
                try:
                    print(f"\nCrawle Website: {url}")
                    site_result = await crawler.arun(url=url)
                    if site_result.success:
                        # Extrahiere Emails via Regex
                        emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', site_result.markdown)
                        
                        # Filtere sinnlose Emails
                        valid_emails = []
                        for email in emails:
                            email = email.lower()
                            if not email.endswith(('.png', '.jpg', '.gif', '.webp', '.svg', 'sentry.io')):
                                valid_emails.append(email)
                        
                        if valid_emails:
                            agency_email = valid_emails[0]
                            # Versuche den Namen aus der URL abzuleiten
                            domain = url.split('//')[-1].split('/')[0].replace('www.', '')
                            name = domain.split('.')[0].capitalize()
                            
                            print(f"✅ Gefunden: {name} -> {agency_email}")
                            agencies.append({
                                "name": name,
                                "email": agency_email,
                                "website": url
                            })
                        else:
                            print(f"❌ Keine E-Mail gefunden auf {url}")
                except Exception as e:
                    print(f"❌ Fehler bei {url}: {str(e)}")
        else:
            print("❌ Fehler beim Suchmaschinen-Crawl")
    
    print("\n=== ZUSAMMENFASSUNG ===")
    print(json.dumps(agencies, indent=2))
    
    # Speichere die Leads
    with open('/home/clawbot/.openclaw/workspace/data/real_it_leads.json', 'w') as f:
        json.dump(agencies, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
