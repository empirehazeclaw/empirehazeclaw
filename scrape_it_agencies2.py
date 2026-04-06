import asyncio
import re
from duckduckgo_search import DDGS
from crawl4ai import AsyncWebCrawler
import json

async def main():
    print("🔍 Starte Web Crawler (Crawl4AI + DDGS) für IT-Agenturen...")
    
    agencies = []
    
    with DDGS() as ddgs:
        results = list(ddgs.text('"IT Agentur" OR "Softwareentwicklung" "Impressum" "email" site:.de', max_results=10))
    
    if not results:
        print("Keine Suchergebnisse gefunden.")
        return
        
    links = [r['href'] for r in results]
    print(f"Gefundene URLs: {len(links)}")
    
    async with AsyncWebCrawler() as crawler:
        for i, url in enumerate(links[:5]):
            print(f"\n[{i+1}/5] Crawle Website: {url}")
            try:
                # Crawle die Website
                site_result = await crawler.arun(url=url)
                
                if site_result.success:
                    # Extrahiere Emails aus dem rohen HTML + Markdown
                    text = site_result.markdown + site_result.html
                    emails = set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text))
                    
                    valid_emails = []
                    for email in emails:
                        email = email.lower()
                        # Filtere Bilder, Sentry, React-Sachen und Typo3 raus
                        if not email.endswith(('.png', '.jpg', '.gif', '.svg', '.webp', '.js', '.css', 'sentry.io', 'example.com')):
                            if 'w3.org' not in email and 'schema.org' not in email:
                                valid_emails.append(email)
                    
                    if valid_emails:
                        # Bevorzuge info@, hallo@ oder kontakt@
                        chosen_email = valid_emails[0]
                        for email in valid_emails:
                            if any(prefix in email for prefix in ['info@', 'hallo@', 'kontakt@', 'hello@']):
                                chosen_email = email
                                break
                        
                        domain = url.split('//')[-1].split('/')[0].replace('www.', '')
                        name = domain.split('.')[0].capitalize()
                        
                        print(f"✅ Gefunden: {name} -> {chosen_email}")
                        agencies.append({
                            "name": name,
                            "email": chosen_email,
                            "website": url
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
