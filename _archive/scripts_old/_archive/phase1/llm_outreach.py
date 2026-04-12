#!/usr/bin/env python3
"""
📧 LLM-Powered Outreach - Skill
Erstellt wirklich personalisierte Emails mit echter KI

Nutzung: python3 scripts/llm_outreach.py --lead "Max Mustermann" --company "Restaurant Goldener Löwen" --industry gastro --email max@firma.de
"""
import smtplib
import os
import json
from email.mime.text import MIMEText
from datetime import datetime
import urllib.request
import urllib.error

CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "email": "empirehazeclaw@gmail.com",
    "app_password": "${GMAIL_APP_PASSWORD}"
}

# OpenAI API Key
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")

DATA_DIR = "/home/clawbot/.openclaw/workspace/data"
SENT_FILE = f"{DATA_DIR}/sent_llm_outreach.json"

# Industry Context für bessere Personalisierung
def template_fallback(lead_name, company, industry):
    """Fallback wenn LLM nicht verfügbar"""
    name = lead_name
    industry_key = get_industry_key(industry)
    ctx = INDUSTRY_CONTEXT.get(industry_key, INDUSTRY_CONTEXT['default'])
    
    pain = ctx['pain_points'][0] if ctx['pain_points'] else "Anfragen"
    benefit = ctx['benefits'][0] if ctx['benefits'] else "sofortige Antworten"
    testimonial = ctx['testimonial'] if ctx['testimonial'] else None
    
    body = f"""Sehr geehrte/r {name},

vielen Dank für Ihre Zeit.

Ich schreibe Ihnen, weil {pain} in Ihrem Unternehmen viel Zeit kosten.

Wir haben eine Lösung: Ein KI-Mitarbeiter, der {benefit} - 24/7, ohne Pause.

{f"Ein ähnliches Unternehmen berichtet: {testimonial}" if testimonial else ""}

Das beste: In nur 2 Wochen könnte das für Sie live sein.

Haben Sie 15 Minuten für einen kurzen Call diese Woche?

Viele Grüße
Nico

P.S. Falls jetzt nicht passt - einfach kurz antworten."""

    return {
        "subject": f"15-minütiger Call: KI für {company}?",
        "body": body,
        "industry": industry_key,
        "llm_used": False
    }


INDUSTRY_CONTEXT = {
    "gastro": {
        "pain_points": ["Reservierungen", "E-Mails beantworten", "Öffnungszeiten erklären", "No-Shows"],
        "benefits": ["Sofortige Antworten 24/7", "Automatisierte Terminbuchung", "Weniger No-Shows durch Erinnerungen"],
        "testimonial": "Restaurant 'Zum Goldenen Löwen': +40% Reservierungen, -60% No-Shows"
    },
    "zahnarzt": {
        "pain_points": ["Terminkoordination", "Patientenerinnerungen", "Erstkontakte"],
        "benefits": ["Automatische Terminerinnerungen", "Sofortige Antworten", "Weniger Ausfall"],
        "testimonial": "Zahnarztpraxis Dr. X: -70% Telefonate für Terminvereinbarung"
    },
    "werkstatt": {
        "pain_points": ["Angebote schreiben", "Terminvereinbarungen", "Kunden auf dem Laufenden halten"],
        "benefits": ["Automatisierte Angebotserstellung", "Status-Updates per KI", "Mehr Zeit für die Arbeit"],
        "testimonial": "KFZ Werkstatt Müller: 10 Stunden/Monat gespart"
    },
    "physio": {
        "pain_points": ["Terminbuchung", "Erstgespräche", "Erinnerungen"],
        "benefits": ["Online-Terminbuchung", "Automatisierte Erinnerungen", "Weniger Ausfall"],
        "testimonial": "Praxis am Park: -50% Ausfall durch automatische Erinnerungen"
    },
    "default": {
        "pain_points": ["Wiederkehrende Anfragen", "E-Mail Support", "Terminkoordination"],
        "benefits": ["24/7 Verfügbarkeit", "Sofortige Antworten", "Keine Wartezeit"],
        "testimonial": None
    }
}

def get_industry_key(industry):
    industry = industry.lower()
    if any(w in industry for w in ['restaurant', 'gastro', 'cafe', 'hotel', 'bar', 'bistro', 'imbiss']):
        return 'gastro'
    if any(w in industry for w in ['zahn', 'arzt', 'praxis', 'medizin', 'clinic']):
        return 'zahnarzt'
    if any(w in industry for w in ['werkstatt', 'kfz', 'auto', 'mechanic', 'service']):
        return 'werkstatt'
    if any(w in industry for w in ['physio', 'therap', 'reha', 'heil', 'fitness']):
        return 'physio'
    return 'default'

def generate_personalized_email(lead_name, company, industry, email):
    """Generiere personalisierte Email mit LLM"""
    
    industry_key = get_industry_key(industry)
    ctx = INDUSTRY_CONTEXT.get(industry_key, INDUSTRY_CONTEXT['default'])
    
    # Fallback function with closure
    def fallback():
        ctx_fb = INDUSTRY_CONTEXT.get(industry_key, INDUSTRY_CONTEXT['default'])
        pain = ctx_fb['pain_points'][0] if ctx_fb['pain_points'] else "Anfragen"
        benefit = ctx_fb['benefits'][0] if ctx_fb['benefits'] else "sofortige Antworten"
        testimonial = ctx_fb.get('testimonial')
        
        body_fb = f"""Sehr geehrte/r {lead_name},

vielen Dank für Ihre Zeit.

Ich schreibe Ihnen, weil {pain} in Ihrem Unternehmen viel Zeit kosten.

Wir haben eine Lösung: Ein KI-Mitarbeiter, der {benefit} - 24/7, ohne Pause.

{f"Ein ähnliches Unternehmen berichtet: {testimonial}" if testimonial else ""}

Das beste: In nur 2 Wochen könnte das für Sie live sein.

Haben Sie 15 Minuten für einen kurzen Call diese Woche?

Viele Grüße
Nico

P.S. Falls jetzt nicht passt - einfach kurz antworten."""

        return {
            "subject": f"15-minütiger Call: KI für {company}?",
            "body": body_fb,
            "industry": industry_key,
            "llm_used": False
        }
    
    # System Prompt
    system_prompt = f"""Du bist ein erfahrener B2B Sales Copywriter für EmpireHazeClaw.

帝国HazeClaw verkauft "KI-Mitarbeiter" an deutsche Kleinunternehmen:
- Monatliche Kosten: €99-199
- Nutzen: 24/7 E-Mail-Support, Terminbuchung, Kundenanfragen
- Zielgruppe: Lokale KMUs (Restaurants, Praxen, Werkstätten)
- Tone: Freundlich-professionell, kurz, direkt

Regeln:
- Schreibe auf Deutsch
- Maximale Länge: 150 Wörter
--personalisiert auf den Lead
- Nenne konkreten Nutzen
- Inkludiere Social Proof wenn vorhanden
- Call-to-Action: 15-minütiger Call

Schreibe eine Email die:
1. Den Lead beim Namen nennt
2. EIN konkretes Problem seiner Branche anspricht
3. Eine konkrete Lösung bietet
4. Social Proof nutzt
5. Mit einem klaren CTA endet"""

    user_prompt = f"""Schreibe eine Email an:

Name: {lead_name}
Unternehmen: {company}
Branche: {industry}
Email: {email}

Kontext für Branche '{industry_key}':
- Typische Probleme: {', '.join(ctx['pain_points'])}
- Nutzen: {', '.join(ctx['benefits'])}
{f"- Testimonial: {ctx['testimonial']}" if ctx['testimonial'] else ""}

Schreibe nur die Email (Subject + Body), keine Erklärungen."""

    try:
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.8
        }
        
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {OPENAI_KEY}",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            content = result["choices"][0]["message"]["content"]
            
            # Parse Subject und Body
            lines = content.strip().split("\n")
            subject = ""
            body_lines = []
            in_body = False
            
            for line in lines:
                if line.startswith("Subject:") or line.startswith("Betreff:"):
                    subject = line.split(":", 1)[1].strip()
                    in_body = True
                elif in_body or (line and not subject):
                    body_lines.append(line)
            
            if not subject and body_lines:
                # Fallback: erste nicht-leere Zeile als Betreff
                for i, line in enumerate(body_lines):
                    if line.strip() and len(line.strip()) > 5:
                        subject = f"Email für {company}"
                        break
            
            body = "\n".join(body_lines).strip()
            
            return {
                "subject": subject or f"15-minütiger Call: KI für {company}",
                "body": body,
                "industry": industry_key,
                "llm_used": True
            }
            
    except Exception as e:
        print(f"LLM Error: {e}")
        # Fallback to template-based
        print("🔄 Using template fallback...")
        return fallback()

def send_email(to_email, subject, body):
    """Sende Email"""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = CONFIG["email"]
    msg["To"] = to_email
    
    try:
        with smtplib.SMTP(CONFIG["smtp_server"], CONFIG["smtp_port"]) as server:
            server.starttls()
            server.login(CONFIG["email"], CONFIG["app_password"])
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False

def main():
    import sys
    
    if len(sys.argv) < 2:
        # Interactive mode
        print("📧 LLM-Powered Outreach Generator")
        print("=" * 50)
        print("Usage:")
        print("  python3 llm_outreach.py --name 'Max' --company 'Restaurant Gold' --industry gastro --email max@firma.de [--send]")
        return 0
    
    # Parse arguments
    args = {}
    for arg in sys.argv[1:]:
        if "=" in arg:
            k, v = arg.split("=", 1)
            args[k.replace("--", "")] = v
    
    name = args.get("name", "Kunde")
    company = args.get("company", "Unternehmen")
    industry = args.get("industry", "business")
    email = args.get("email", "")
    
    if not email:
        print("❌ --email is required")
        return 1
    
    print(f"📧 LLM-Powered Outreach")
    print(f"   Lead: {name}")
    print(f"   Company: {company}")
    print(f"   Industry: {industry}")
    print()
    print("🤖 Generiere personalisierte Email mit KI...")
    
    result = generate_personalized_email(name, company, industry, email)
    
    if not result:
        print("❌ LLM generation failed")
        return 1
    
    print(f"\n📬 EMAIL GENERATED:")
    print(f"   Subject: {result['subject']}")
    print(f"   Industry: {result['industry']}")
    print()
    print(result['body'][:500])
    
    if "--send" in args:
        print("\n📤 Senden...")
        if send_email(email, result['subject'], result['body']):
            print(f"✅ Gesendet an {email}")
            # Log
            sent = []
            if os.path.exists(SENT_FILE):
                with open(SENT_FILE) as f:
                    sent = json.load(f)
            sent.append({"email": email, "company": company, "date": datetime.now().isoformat()})
            with open(SENT_FILE, 'w') as f:
                json.dump(sent[-100:], f, indent=2)
        else:
            print(f"❌ Senden fehlgeschlagen")
    
    return 0

if __name__ == "__main__":
    exit(main())
