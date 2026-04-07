#!/usr/bin/env python3
"""
🎯 Quick Outreach Dashboard Generator
Creates a standalone HTML dashboard with real data from crm_leads.csv
"""
import csv
import json
from pathlib import Path
import os

DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data")
LEADS_FILE = DATA_DIR / "crm_leads.csv"
BOUNCED_FILE = DATA_DIR / "bounced_leads.json"
CONTACTED_FILE = DATA_DIR / "leads_contacted.json"

def get_data():
    leads = []
    
    # Load from CSV
    if LEADS_FILE.exists():
        with open(LEADS_FILE) as f:
            reader = csv.DictReader(f)
            leads = list(reader)
    
    # Load bounced
    bounced = set()
    if BOUNCED_FILE.exists():
        with open(BOUNCED_FILE) as f:
            bounced = {b["email"] for b in json.load(f)}
    
    # Load contacted (list of dicts)
    contacted = set()
    if CONTACTED_FILE.exists():
        with open(CONTACTED_FILE) as f:
            contacted_data = json.load(f)
            contacted = {c["email"] for c in contacted_data if "email" in c}
    
    return leads, bounced, contacted

def generate_dashboard(leads, bounced, contacted):
    total = len(leads)
    bounced_count = len(bounced)
    contacted_count = len(contacted)
    pending = total - contacted_count - bounced_count
    
    # Industry breakdown
    industries = {}
    for lead in leads:
        ind = lead.get("industry", "unknown")
        industries[ind] = industries.get(ind, 0) + 1
    
    # City breakdown
    cities = {}
    for lead in leads:
        city = lead.get("city", "unknown")
        cities[city] = cities.get(city, 0) + 1
    
    industry_html = "".join([f'<div class="stat-row"><span>{k}</span><span>{v}</span></div>' for k, v in sorted(industries.items(), key=lambda x: -x[1])[:5]])
    city_html = "".join([f'<div class="stat-row"><span>{k}</span><span>{v}</span></div>' for k, v in sorted(cities.items(), key=lambda x: -x[1])[:5]])
    
    # Recent leads
    recent = leads[:10]
    recent_html = ""
    for lead in recent:
        email = lead.get("email", "")
        company = lead.get("company", "Unknown")
        status = "✅ contacted" if email in contacted else ("❌ bounced" if email in bounced else "⏳ pending")
        recent_html += f'<div class="lead-row"><span class="lead-company">{company}</span><span class="lead-status">{status}</span></div>'
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎯 Outreach Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Inter', system-ui, -apple-system, sans-serif; 
            background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 2rem;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        h1 {{ font-size: 1.8rem; color: #fff; }}
        .badge {{ 
            background: linear-gradient(135deg, #667eea, #764ba2);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.85rem;
        }}
        
        .funnel {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .funnel-stage {{
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.2s, border-color 0.2s;
        }}
        .funnel-stage:hover {{
            transform: translateY(-4px);
            border-color: #667eea;
        }}
        .funnel-stage.active {{
            border-color: #00ff88;
            box-shadow: 0 0 20px rgba(0,255,136,0.2);
        }}
        .stage-num {{
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .stage-label {{ color: #888; font-size: 0.85rem; margin-top: 0.5rem; }}
        
        .grid {{ 
            display: grid; 
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
        }}
        .card {{
            background: rgba(255,255,255,0.03);
            border-radius: 16px;
            padding: 1.5rem;
            border: 1px solid rgba(255,255,255,0.08);
        }}
        .card-title {{
            font-size: 1rem;
            color: #888;
            margin-bottom: 1rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .stat-row {{
            display: flex;
            justify-content: space-between;
            padding: 0.75rem 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        .stat-row:last-child {{ border-bottom: none; }}
        
        .lead-row {{
            display: flex;
            justify-content: space-between;
            padding: 0.6rem 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        .lead-company {{ color: #fff; }}
        .lead-status {{ font-size: 0.85rem; color: #888; }}
        
        .actions {{
            display: flex;
            gap: 1rem;
            margin-top: 2rem;
        }}
        .btn {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 0.8rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: opacity 0.2s;
        }}
        .btn:hover {{ opacity: 0.9; }}
        .btn-secondary {{
            background: rgba(255,255,255,0.1);
        }}
        
        @media (max-width: 768px) {{
            .funnel {{ grid-template-columns: 1fr; }}
            .grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎯 Outreach Dashboard</h1>
            <span class="badge">📅 {os.popen('date +%Y-%m-%d').read().strip()}</span>
        </header>
        
        <!-- Funnel -->
        <div class="funnel">
            <div class="funnel-stage">
                <div class="stage-num">{total}</div>
                <div class="stage-label">📥 Total Leads</div>
            </div>
            <div class="funnel-stage">
                <div class="stage-num">{contacted_count}</div>
                <div class="stage-label">📤 Contacted</div>
            </div>
            <div class="funnel-stage active">
                <div class="stage-num">0</div>
                <div class="stage-label">💬 Replied</div>
            </div>
            <div class="funnel-stage">
                <div class="stage-num">0</div>
                <div class="stage-label">📅 Meetings</div>
            </div>
            <div class="funnel-stage">
                <div class="stage-num">0</div>
                <div class="stage-label">💰 Customers</div>
            </div>
        </div>
        
        <!-- Stats Grid -->
        <div class="grid">
            <div class="card">
                <div class="card-title">📊 By Industry</div>
                {industry_html}
            </div>
            <div class="card">
                <div class="card-title">🌍 By City</div>
                {city_html}
            </div>
        </div>
        
        <!-- Recent Leads -->
        <div class="card" style="margin-top: 1.5rem;">
            <div class="card-title">📋 Recent Leads</div>
            {recent_html}
        </div>
        
        <!-- Actions -->
        <div class="actions">
            <button class="btn" onclick="location.href='gog_outreach_enhanced.py'">📤 Send Outreach</button>
            <button class="btn btn-secondary" onclick="location.href='lead_crawler_v2.py'">🔍 Find New Leads</button>
            <button class="btn btn-secondary" onclick="location.href='crm_leads.csv'">📁 View CSV</button>
        </div>
    </div>
</body>
</html>'''
    
    return html

def main():
    leads, bounced, contacted = get_data()
    html = generate_dashboard(leads, bounced, contacted)
    
    out_file = DATA_DIR / "outreach_dashboard.html"
    with open(out_file, "w") as f:
        f.write(html)
    
    print(f"✅ Dashboard erstellt: {out_file}")
    print(f"   Leads: {len(leads)}")
    print(f"   Contacted: {len(contacted)}")
    print(f"   Bounced: {len(bounced)}")

if __name__ == "__main__":
    main()