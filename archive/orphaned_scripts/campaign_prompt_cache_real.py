import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
import os

SMTP_PORT = 587
SMTP_PASS = os.getenv("SMTP_PASS", "")

FROM_EMAIL = "empirehazeclaw@gmail.com"
FROM_NAME = "Nico | EmpireHazeClaw"

with open('/home/clawbot/.openclaw/workspace/data/real_it_leads.json', 'r') as f:
    IT_AGENCIES = json.load(f)

def send_campaign():
    print(f"[{datetime.now().isoformat()}] 🚀 STARTE KALT-AKQUISE: ECHTE LEADS via Crawl4AI")
    
    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        print("✅ SMTP Login erfolgreich")
    except Exception as e:
        print(f"❌ SMTP Fehler: {e}")
        return

    success_count = 0

    for agency in IT_AGENCIES:
        # Extrahiere einen vernünftigen Namen (keine langen Bindestriche)
        name = agency['name']
        if '-' in name: name = name.split('-')[0].capitalize()
        if name.lower() == 'pt': name = 'PT Software Team'
        
        msg = MIMEMultipart()
        msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg["To"] = agency["email"]
        msg["Subject"] = "40% geringere LLM API Kosten für eure KI-Projekte 🚀"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <p>Hallo {name},</p>
            <p>ich bin auf eure Website ({agency['website']}) gestoßen und habe gesehen, dass ihr Softwarelösungen entwickelt. Da aktuell fast jedes Kundenprojekt KI integriert, explodieren oft die Rechnungen für OpenAI oder Anthropic API-Calls.</p>
            <p>Ich habe eine <b>Prompt Cache API (Semantic Caching)</b> entwickelt. Sie speichert semantisch ähnliche Prompts zwischen, reduziert eure API-Aufrufe um bis zu 40% und drückt die Latenz für den Endnutzer auf unter 50ms.</p>
            <p>Es ist ein simples Plug-and-Play Setup (nur ein Endpoint), das euch und euren Kunden direkt bares Geld spart.</p>
            <p>Vielleicht spannend für eure aktuellen Projekte?<br>
            Alle technischen Infos & Code-Beispiele gibt es hier: <br>
            👉 <a href="https://empirehazeclaw.store/prompt-cache.html">Prompt Cache API ansehen</a></p>
            <p>Lasst mich gerne wissen, wenn ihr Fragen zur Architektur habt!</p>
            <p>Beste Grüße,<br>
            Nico<br>
            <i>Founder, EmpireHazeClaw</i></p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_content, "html"))

        try:
            server.send_message(msg)
            print(f"  ✉️ Gesendet an: {agency['email']} ({agency['name']})")
            success_count += 1
        except Exception as e:
            print(f"  ❌ Fehler bei {agency['email']}: {e}")

    server.quit()
    print(f"✅ Kampagne abgeschlossen. {success_count}/{len(IT_AGENCIES)} ECHTE E-Mails erfolgreich versendet.")

if __name__ == "__main__":
    send_campaign()
