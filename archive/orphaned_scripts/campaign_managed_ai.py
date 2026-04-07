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

# Wir nutzen unsere IT-Agenturen-Leads von vorhin als Test-Pilot für das Hosting!
with open('/home/clawbot/.openclaw/workspace/data/real_it_leads.json', 'r') as f:
    IT_AGENCIES = json.load(f)

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

    for agency in IT_AGENCIES:
        name = agency['name']
        if '-' in name: name = name.split('-')[0].capitalize()
        if name.lower() == 'pt': name = 'PT Software Team'
        
        msg = MIMEMultipart()
        msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg["To"] = agency["email"]
        msg["Subject"] = "DSGVO-konformes Hosting für eure KI-Agenten (Server in DE) 🇩🇪"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <p>Hallo {name},</p>
            <p>ich habe mir euer Portfolio ({agency['website']}) angesehen und gesehen, dass ihr im Bereich digitale Lösungen für Kunden stark aufgestellt seid.</p>
            <p>Aktuell sprechen alle über autonome KI-Agenten (OpenClaw etc.), aber viele Agenturen und Mittelständler zögern bei der Einführung. Der Grund: <b>Sicherheitsbedenken, US-Server und fehlendes Linux-Know-How.</b></p>
            <p>Wir haben genau dafür eine Lösung gebaut: <b>Managed AI Agent Hosting in Deutschland.</b></p>
            <ul>
                <li>🛡️ <b>100% DSGVO-Konform:</b> Eure Agenten laufen auf dedizierten Servern bei Hetzner (Nürnberg/Falkenstein).</li>
                <li>🔒 <b>Sandboxed:</b> Voll isolierte Container-Umgebungen. Keine Hacker-Gefahr für das Host-System.</li>
                <li>🔑 <b>All-Inclusive oder BYOK:</b> Ihr könnt eure eigenen API-Keys mitbringen oder wir übernehmen das komplette Token-Abrechnungs-Chaos.</li>
            </ul>
            <p>Ihr könnt euch auf die Workflows eurer Kunden konzentrieren, wir machen das Server-Setup im Hintergrund.</p>
            <p>Schaut euch das Setup gerne hier an:<br>
            👉 <a href="https://empirehazeclaw.store/managed-ai.html">Managed AI Hosting (DE)</a></p>
            <p>Hättet ihr diese Woche 15 Minuten Zeit für einen kurzen Setup-Call (via Zoom), um zu schauen, wie wir eure internen Workflows oder Kundenprojekte damit absichern können?</p>
            <p>Beste Grüße,<br>
            Nico<br>
            <i>Founder, EmpireHazeClaw</i></p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_content, "html"))

        try:
            server.send_message(msg)
            print(f"  ✉️ B2B Pitch gesendet an: {agency['email']} ({agency['name']})")
            success_count += 1
        except Exception as e:
            print(f"  ❌ Fehler bei {agency['email']}: {e}")

    server.quit()
    print(f"✅ Kampagne abgeschlossen. {success_count}/{len(IT_AGENCIES)} ECHTE E-Mails erfolgreich versendet.")

if __name__ == "__main__":
    send_campaign()
