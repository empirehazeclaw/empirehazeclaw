#!/usr/bin/env python3
"""
Lead Generator for EmpireHazeClaw
Finds German businesses (KMUs) that could benefit from AI agents
"""
import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import re
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data")
LEADS_FILE = DATA_DIR / "crm_leads.csv"

# Target industries for AI agent services
INDUSTRIES = {
    "gastro": ["Restaurant", "Café", "Bistro", "Gastronomie", "Imbiss", "Bar"],
    "gesundheit": ["Zahnarzt", "Arzt", "Physiotherapie", "Praxis", "Heilpraktiker", "Apotheke"],
    "service": ["KFZ", "Werkstatt", "Autohaus", "Friseur", "Salon"],
    "handwerk": ["Heizung", "Sanitär", "Elektro", "Dachdecker", "Maler", "Tischler"],
    "retail": ["Einzelhandel", "Shop", "Boutique", "Mode"],
    "hotel": ["Hotel", "Pension", "Ferienwohnung"]
}

def search_google(query, limit=10):
    """Search using Tavily API (we have this key)"""
    try:
        Tavily_API = "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"
        response = requests.post(
            "https://api.tavily.com/search",
            json={"query": query, "max_results": limit},
            headers={"Authorization": f"Bearer {Tavily_API}"},
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get("results", [])
    except Exception as e:
        print(f"Tavily error: {e}")
    return []

def extract_emails_from_website(url):
    """Try to find contact email on website"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(url, headers=headers, timeout=10, verify=False)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Look for email links
        emails = re.findall(r'[\w.-]+@[\w.-]+\.\w+', resp.text)
        emails = [e for e in emails if not e.startswith('noreply') and not e.startswith('info@web.')]
        
        # Look for contact page
        contact_links = [a['href'] for a in soup.find_all('a', href=True) 
                        if 'contact' in a['href'].lower() or 'kontakt' in a['href'].lower()]
        
        return list(set(emails))[:3], contact_links[:3]
    except:
        return [], []

def search_business_type(business_type, location="Deutschland", limit=20):
    """Search for businesses of a specific type"""
    query = f"{business_type} {location} -site:google.com -site:linkedin.com"
    results = search_google(query, limit)
    
    leads = []
    for r in results:
        url = r.get('url', '')
        title = r.get('title', '')
        
        # Skip if no URL
        if not url or 'google' in url or 'linkedin' in url:
            continue
        
        # Extract email
        emails, _ = extract_emails_from_website(url)
        email = emails[0] if emails else ""
        
        # Determine industry
        industry = "unknown"
        for ind, keywords in INDUSTRIES.items():
            if any(k.lower() in title.lower() for k in keywords):
                industry = ind
                break
        
        leads.append({
            "company": title,
            "email": email,
            "website": url,
            "industry": industry,
            "source": "lead_generator"
        })
        
        time.sleep(1)  # Rate limiting
    
    return leads

def add_to_csv(leads, csv_file):
    """Add leads to CSV"""
    file_exists = csv_file.exists()
    
    with open(csv_file, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['company', 'email', 'website', 'industry', 'source'])
        if not file_exists:
            writer.writeheader()
        writer.writerows(leads)
    
    return len(leads)

def main():
    print(f"[{datetime.now()}] Starting lead generation...")
    
    all_leads = []
    
    # Search for each business type
    for industry, keywords in INDUSTRIES.items():
        for keyword in keywords[:2]:  # Limit to 2 keywords per industry
            print(f"  Searching: {keyword}...")
            leads = search_business_type(keyword, limit=15)
            all_leads.extend(leads)
            print(f"    Found {len(leads)} leads")
            time.sleep(2)
    
    # Remove duplicates by email
    seen_emails = set()
    unique_leads = []
    for lead in all_leads:
        email = lead.get('email', '')
        if email and email not in seen_emails:
            seen_emails.add(email)
            unique_leads.append(lead)
    
    # Save to CSV
    if unique_leads:
        count = add_to_csv(unique_leads, LEADS_FILE)
        print(f"\n✅ Added {count} new leads to {LEADS_FILE}")
    else:
        print("\n❌ No new leads found")
    
    print(f"Total leads now: {sum(1 for _ in open(LEADS_FILE)) - 1}")

if __name__ == "__main__":
    main()
