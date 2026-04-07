import os
import asyncio
import requests
from bs4 import BeautifulSoup
import re
from crawl4ai import AsyncWebCrawler
import json
import urllib.parse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import random
import os

STATE_FILE = '/home/clawbot/.openclaw/workspace/data/sales_funnel_state.json'
SMTP_PORT = 587
SMTP_PASS = os.getenv("SMTP_PASS", "")
FROM_EMAIL = "empirehazeclaw@gmail.com"
FROM_NAME = "Nico | EmpireHazeClaw"

KEYWORDS = [
    "IT-Agentur Softwareentwicklung Impressum",
    "KI Beratung Agentur Impressum",
    "Webdesign App Agentur Deutschland Impressum email",
    "SaaS Entwicklung Agentur Kontakt Impressum",
    "Digitalagentur Software Impressum"
]

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"contacted_emails": [], "keyword_index": 0}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

async def scrape_leads(keyword):
    print(f"🔍 Suche nach: {keyword}")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(keyword)}"
    
    try:
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        for a in soup.find_all('a'):
            url = a.get('href')
            if url and 'uddg=' in url:
                try:
                    actual_url = urllib.parse.unquote(url.split('uddg=')[1].split('&')[0])
                    if actual_url.startswith('http'):
                        links.append(actual_url)
                except: pass
        links = list(set(links))[:8] # Max 8 Seiten pro Run crawlen
    except Exception as e:
        print(f"Fehler bei Suche: {e}")
        return []

    agencies = []
    if links:
        async with AsyncWebCrawler() as crawler:
            for url in links:
                try:
                    site_result = await crawler.arun(url=url)
                    if site_result.success:
                        emails = set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', site_result.html))
                        valid_emails = [e.lower() for e in emails if not e.lower().endswith(('.png','.jpg','.gif','.css','.js','.woff2')) and 'example' not in e.lower() and 'sentry' not in e.lower()]
                        
                        if not valid_emails:
                            # Try Impressum
                            imp_url = url.rstrip('/') + '/impressum'
                            imp_res = await crawler.arun(url=imp_url)
                            if imp_res.success:
                                imp_emails = set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', imp_res.html))
                                valid_emails = [e.lower() for e in imp_emails if not e.lower().endswith(('.png','.jpg','.gif','.css','.js','.woff2'))]

                        if valid_emails:
                            chosen_email = valid_emails[0]
                            for e in valid_emails:
                                if any(p in e for p in ['info@', 'hallo@', 'kontakt@', 'hello@']):
                                    chosen_email = e; break
                            domain = urllib.parse.urlparse(url).netloc.replace('www.', '')
                            name = domain.split('.')[0].capitalize()
                            agencies.append({"name": name, "email": chosen_email, "website": url})
                except Exception as e:
                    pass
    return agencies

def send_emails(leads, state):
    if not leads:
        print("Keine Leads zum Anschreiben gefunden.")
        return
    
    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
    except Exception as e:
        print(f"SMTP Login Fehler: {e}")
        return

    sent_count = 0
    for lead in leads:
        email = lead['email']
        if email in state['contacted_emails']:
            continue # Skip duplicates
            
        name = lead['name'].split('-')[0].capitalize()
        
        msg = MIMEMultipart()
        msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg["To"] = email
        msg["Subject"] = "Zusammenarbeit / Reduzierung eurer LLM API-Kosten"
        
        html = f"""<html><body>
            <p>Hallo {name}-Team,</p>
            <p>ich habe mir gerade eure Website ({lead['website']}) angesehen. Da ihr im Bereich Software/Digitales unterwegs seid, integriert ihr wahrscheinlich auch immer mehr KI-Features für Kunden.</p>
            <p>Das Problem: Die API-Kosten (OpenAI/Anthropic) eskalieren oft unbemerkt, weil User dieselben Prompts stellen.</p>
            <p>Wir haben dafür eine <b>Prompt Cache API (Semantic Caching)</b> entwickelt. Sie speichert semantisch ähnliche Prompts für 24h, senkt die Latenz auf 50ms und spart bis zu 40% der LLM-Kosten. Einbindung dauert 10 Minuten.</p>
            <p>Alle Infos & Doku findet ihr hier: <a href="https://empirehazeclaw.store/prompt-cache.html">Prompt Cache API</a></p>
            <p>Lasst mich gerne wissen, wenn ihr Fragen habt oder einen Trial-Key zum Testen braucht!</p>
            <p>Viele Grüße,<br>Nico<br><i>EmpireHazeClaw</i></p>
        </body></html>"""
        
        msg.attach(MIMEText(html, "html"))
        
        try:
            server.send_message(msg)
            print(f"✉️ Gesendet an: {email}")
            state['contacted_emails'].append(email)
            sent_count += 1
            if sent_count >= 15: # Tageslimit pro Lauf sicherheitshalber kappen
                break
        except Exception as e:
            print(f"Fehler bei {email}: {e}")
            
    server.quit()
    print(f"✅ Auto-Outreach beendet. {sent_count} Mails gesendet.")

async def main():
    print(f"[{datetime.now().isoformat()}] 🚀 Starte Auto B2B Sales Funnel")
    state = load_state()
    
    idx = state.get('keyword_index', 0)
    keyword = KEYWORDS[idx % len(KEYWORDS)]
    
    # Keyword rotieren für nächsten Tag
    state['keyword_index'] = (idx + 1) % len(KEYWORDS)
    
    leads = await scrape_leads(keyword)
    print(f"Gefundene Leads: {len(leads)}")
    
    send_emails(leads, state)
    save_state(state)

if __name__ == "__main__":
    asyncio.run(main())
