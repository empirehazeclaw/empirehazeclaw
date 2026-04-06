import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
import random

SMTP_PORT = 587
SMTP_PASS = os.getenv("SMTP_PASS", "")

FROM_EMAIL = "empirehazeclaw@gmail.com"
FROM_NAME = "Nico | EmpireHazeClaw"

# 15 neue Leads (IT, Marketing, Beratung, etc.)
LEADS = [
    {"name": " Weber Digital", "email": "info@weber-digital.de", "website": "weber-digital.de"},
    {"name": " Schmidt IT", "email": "kontakt@schmidt-itk.de", "website": "schmidt-itk.de"},
    {"name": " Meyer Solutions", "email": "info@meyer-solutions.de", "website": "meyer-solutions.de"},
    {"name": " Wagner Software", "email": "hello@wagner-software.de", "website": "wagner-software.de"},
    {"name": " Becker Tech", "email": "info@becker-tech.de", "website": "becker-tech.de"},
    {"name": " Hoffmann Consulting", "email": "kontakt@hoffmann-consult.de", "website": "hoffmann-consult.de"},
    {"name": " Schulz Agentur", "email": "info@schulz-agentur.de", "website": "schulz-agentur.de"},
    {"name": " Neumann Webdev", "email": "hello@neumann-webdev.de", "website": "neumann-webdev.de"},
    {"name": " Lange Marketing", "email": "info@lange-marketing.de", "website": "lange-marketing.de"},
    {"name": " Krüger IT Service", "email": "kontakt@krueger-it.de", "website": "krueger-it.de"},
    {"name": " Fischer Dev", "email": "info@fischer-dev.de", "website": "fischer-dev.de"},
    {"name": " Peters Digital", "email": "hello@peters-digital.de", "website": "peters-digital.de"},
    {"name": " Wolf Systems", "email": "info@wolf-systems.de", "website": "wolf-systems.de"},
    {"name": " Braun Solutions", "email": "kontakt@braun-solutions.de", "website": "braun-solutions.de"},
    {"name": " König Tech", "email": "info@koenig-tech.de", "website": "koenig-tech.de"},
]

def send_campaign():
    print(f"[{datetime.now().isoformat()}] 🚀 STARTE KALT-AKQUISE: MANAGED AI HOSTING")
    
    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        print("✅ SMTP Login erfolgreich")
    except Exception as e:
        print(f"❌ SMTP Fehler: {e}")
        return

    success_count = 0

    for lead in LEADS:
        # Saubere Firmenname
        firmenname = lead['name'].strip()
        
        msg = MIMEMultipart()
        msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg["To"] = lead["email"]
        msg["Subject"] = "Ihr persönlicher KI-Agent - 24/7 für Ihr Unternehmen 🚀"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <p>Hallo {firmenname},</p>
            
            <p>stellen Sie sich vor, Sie hätten einen Mitarbeiter, der <b>nie schläft, nie krank wird</b> und trotzdem alle Ihre E-Mails, Termine und Akquise-Aufgaben übernimmt.</p>
            
            <p>Genau das ist ab sofort möglich.</p>
            
            <p>Wir bieten <b>Managed AI Hosting</b> - wir hosten und konfigurieren autonome KI-Agenten für deutsche Unternehmen.</p>
            
            <p><b>Was unsere Lösung besonders macht:</b></p>
            <ul>
                <li>✅ 100% DSGVO-konform (Server in Deutschland)</li>
                <li>✅ Keine technischen Vorkenntnisse nötig</li>
                <li>✅ Ihre Daten bleiben bei Ihnen (Sie behalten die API-Keys)</li>
                <li>✅ Bereits ab 99€/Monat</li>
            </ul>
            
            <p>Ob für Support, Vertrieb oder Marketing - unsere KI-Agenten arbeiten für Sie.</p>
            
            <p>Mehr Infos gibt es hier: <br>
            👉 <a href="https://empirehazeclaw.store/managed-ai.html">Managed AI Hosting ansehen</a></p>
            
            <p>Falls Sie Interesse an einer kostenlosen Demo haben, einfach kurz antworten.</p>
            
            <p>Mit freundlichen Grüße,<br>
            Nico<br>
            <i>Founder, EmpireHazeClaw</i></p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_content, "html"))

        try:
            server.send_message(msg)
            print(f"  ✉️ Gesendet an: {lead['email']} ({lead['name']})")
            success_count += 1
        except Exception as e:
            print(f"  ❌ Fehler bei {lead['email']}: {e}")

    server.quit()
    print(f"✅ Kampagne abgeschlossen. {success_count}/{len(LEADS)} E-Mails erfolgreich versendet.")

if __name__ == "__main__":
    send_campaign()
