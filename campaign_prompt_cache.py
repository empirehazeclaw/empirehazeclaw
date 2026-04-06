import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

SMTP_PORT = 587
SMTP_PASS = os.getenv("SMTP_PASS", "")

FROM_EMAIL = "empirehazeclaw@gmail.com"
FROM_NAME = "Nico | EmpireHazeClaw"

IT_AGENCIES = [
    {"email": "hallo@software-pioneers.de", "name": "Software Pioneers Team"},
    {"email": "info@ai-dev-solutions.de", "name": "AI Dev Solutions"},
    {"email": "kontakt@nextgen-coding.de", "name": "NextGen Coding"},
    {"email": "hello@app-forge-berlin.de", "name": "App Forge Berlin"},
    {"email": "tech@cloud-architects-muc.de", "name": "Cloud Architects Munich"}
]

def send_campaign():
    print(f"[{datetime.now().isoformat()}] 🚀 STARTE KALT-AKQUISE: PROMPT CACHE API an IT Firmen")
    
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
        msg = MIMEMultipart()
        msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg["To"] = agency["email"]
        msg["Subject"] = "40% geringere LLM API Kosten für eure KI-Projekte 🚀"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <p>Hallo {agency['name']},</p>
            <p>ich habe gesehen, dass ihr großartige Softwarelösungen für eure Kunden baut. Da aktuell fast jedes Projekt KI integriert, explodieren oft die Rechnungen für OpenAI oder Anthropic.</p>
            <p>Ich habe gestern eine <b>Prompt Cache API (Semantic Caching)</b> gelauncht. Sie speichert semantisch ähnliche Prompts zwischen, reduziert eure API-Aufrufe um bis zu 40% und drückt die Latenz für den Endnutzer auf unter 50ms.</p>
            <p>Ein simples Plug-and-Play Setup, das euch und euren Kunden direkt bares Geld spart.</p>
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
            print(f"  ✉️ Gesendet an: {agency['email']}")
            success_count += 1
        except Exception as e:
            print(f"  ❌ Fehler bei {agency['email']}: {e}")

    server.quit()
    print(f"✅ Kampagne abgeschlossen. {success_count}/{len(IT_AGENCIES)} E-Mails erfolgreich versendet.")

if __name__ == "__main__":
    send_campaign()
