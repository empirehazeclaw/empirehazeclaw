#!/usr/bin/env python3
"""
Newsletter Automation
- Weekly newsletter with blog posts + product updates
- Scheduled for Sunday 10am
"""

import os
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
BLOG_DIR = WORKSPACE / "blog"
SUBSCRIBERS_FILE = WORKSPACE / "data" / "newsletter-subscribers.json"

def get_blog_posts():
    """Get recent blog posts"""
    posts = []
    if BLOG_DIR.exists():
        for f in sorted(BLOG_DIR.glob("*.md"), reverse=True)[:3]:
            posts.append({
                "title": f.stem.replace("-", " ").title(),
                "file": str(f)
            })
    return posts

def get_product_updates():
    """Get recent product changes"""
    updates = []
    
    # Check Stripe payments
    invoice_dir = WORKSPACE / "data" / "invoices"
    if invoice_dir.exists():
        recent = sorted(invoice_dir.glob("RE-*.json"), reverse=True)[:3]
        for f in recent:
            data = json.loads(f.read_text())
            updates.append(f"Neue Bestellung: {data.get('product', 'Service')} - {data.get('amount', 0)}€")
    
    return updates

def generate_newsletter():
    """Generate newsletter content"""
    posts = get_blog_posts()
    updates = get_product_updates()
    
    content = f"""📧 EmpireHazeClaw Newsletter - KW{datetime.now().isocalendar()[1]}

Hallo!

Will zu unserem wöchentlichen Update. Hier ist, was diese Woche passiert ist:

{'='*50}

📝 NEUE BLOG POSTS

"""
    
    if posts:
        for p in posts:
            content += f"- {p['title']}\n"
    else:
        content += "Keine neuen Blog Posts diese Woche.\n"
    
    content += """

{'='*50}

🛒 PRODUKT UPDATES

"""
    
    if updates:
        for u in updates:
            content += f"- {u}\n"
    else:
        content += "Keine neuen Bestellungen diese Woche.\n"
    
    content += f"""

{'='*50}

🚀 WAS KOMMT ALS NÄCHSTES?

- Mehr AI Agent Templates
- Verbesserte Dashboard Features  
- Neue Integrationen

{'='*50}

Bis bald!
Dein EmpireHazeClaw Team

---
🥚 EmpireHazeClaw - AI & Automation für jeden
📧 empirehazeclaw@gmail.com
🌐 empirehazeclaw.com
"""
    
    return content

def send_newsletter():
    """Send newsletter to all subscribers"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    content = generate_newsletter()
    
    # Get subscribers
    subscribers = []
    if SUBSCRIBERS_FILE.exists():
        data = json.loads(SUBSCRIBERS_FILE.read_text())
        subscribers = [s['email'] for s in data.get('subscribers', [])]
    
    if not subscribers:
        print("ℹ️ Keine Abonnenten für Newsletter")
        return
    
    msg = MIMEMultipart()
    msg['From'] = "EmpireHazeClaw Newsletter <empirehazeclaw@gmail.com>"
    msg['Subject'] = f"📧 EmpireHazeClaw Newsletter - KW{datetime.now().isocalendar()[1]}"
    msg.attach(MIMEText(content, 'plain'))
    
    try:
        server.starttls()
        
        for email in subscribers[:50]:  # Limit to 50 per batch
            msg['To'] = email
            server.sendmail("empirehazeclaw@gmail.com", email, msg.as_string())
        
        server.quit()
        print(f"✅ Newsletter gesendet an {len(subscribers)} Abonnenten")
    except Exception as e:
        print(f"❌ Failed to send newsletter: {e}")

if __name__ == "__main__":
    print(f"📧 Newsletter Generator - {datetime.now().strftime('%Y-%m-%d')}")
    print()
    content = generate_newsletter()
    print(content[:500])
    print("...")
    print()
    # Uncomment to send: send_newsletter()
