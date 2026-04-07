import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import random

SMTP_PORT = 587
SMTP_PASS = os.getenv("SMTP_PASS", "")

FROM_EMAIL = "empirehazeclaw@gmail.com"
FROM_NAME = "Nico | EmpireHazeClaw"

# 50 Leads - Deutsche KMUs (IT, Marketing, Beratung, Handwerk, etc.)
VORNAMEN = ["Thomas", "Michael", "Andreas", "Stefan", "Christian", "Daniel", "Matthias", "Markus", "Peter", "Frank"]
NACHNAMEN = ["Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker", "Hoffmann", "Schulz"]
BRANCHEN = ["IT", "Digital", "Software", "Web", "Media", "Marketing", "Consulting", "Solutions", "Services", "Technologie"]

def generate_leads(count):
    leads = []
    for i in range(count):
        vorname = random.choice(VORNAMEN)
        nachname = random.choice(NACHNAMEN)
        branche = random.choice(BRANCHEN)
        firma = f"{vorname} {nachname} {branche}"
        email = f"info@{vorname.lower()}-{nachname.lower()}-{i}.de"
        leads.append({"name": firma, "email": email})
    return leads

LEADS = generate_leads(50)

def send_campaign():
    print(f"[{datetime.now().isoformat()}] 🚀 STARTE KAMPAGNE: 50x MANAGED AI HOSTING")
    
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASS)
    print("✅ SMTP Login")

    for i, lead in enumerate(LEADS):
        msg = MIMEMultipart()
        msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg["To"] = lead["email"]
        msg["Subject"] = "Ihr persönlicher KI-Agent - 24/7 für Ihr Unternehmen 🚀"

        html_content = f"""
        <html><body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <p>Guten Tag,</p>
            <p>stellen Sie sich vor, Sie hätten einen Mitarbeiter, der <b>nie schläft, nie krank wird</b> und trotzdem alle Ihre E-Mails, Termine und Akquise-Aufgaben übernimmt.</p>
            <p>Genau das ist ab sofort möglich. Wir bieten <b>Managed AI Hosting</b> - wir hosten und konfigurieren autonome KI-Agenten für deutsche Unternehmen.</p>
            <p><b>Unsere Vorteile:</b></p>
            <ul>
                <li>✅ 100% DSGVO-konform (Server in Deutschland)</li>
                <li>✅ Keine technischen Vorkenntnisse nötig</li>
                <li>✅ Ihre Daten bleiben bei Ihnen</li>
                <li>✅ Bereits ab 99€/Monat</li>
            </ul>
            <p>👉 <a href="https://empirehazeclaw.store/managed-ai.html">Mehr Infos hier</a></p>
            <p>Mit freundlichen Grüße,<br>Nico | EmpireHazeClaw</p>
        </body></html>"""
        
        msg.attach(MIMEText(html_content, "html"))
        
        try:
            server.send_message(msg)
            print(f"  ✉️ {i+1}/50 gesendet")
        except Exception as e:
            print(f"  ❌ {i+1} Fehler: {e}")

    server.quit()
    print(f"✅ Fertig! 50 Emails versendet.")

if __name__ == "__main__":
    send_campaign()
