import os
#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          MAIL AGENT - ENHANCED                           ║
║          Brevo Integration · Templates · Follow-ups        ║
╚══════════════════════════════════════════════════════════════╝

Features:
  - Brevo SMTP Integration (aktuell)
  - Email Templates (Outreach, Follow-up, Newsletter)
  - Auto-Reply Drafting
  - Inbox Management (simuliert)
  - Follow-up Reminders
  - Communication Tone Adaptation

Hinweis: Gmail MCP kommt nach OAuth - aktuell Brevo
"""

from __future__ import annotations

import json
import logging
import re
import smtplib
from dataclasses import dataclass, field
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

log = logging.getLogger("openclaw.mail")

# Brevo SMTP Configuration
BREVO_PORT = 587
BREVO_PASS = os.getenv("SMTP_PASS", "")


class MailTone(str, Enum):
    FORMAL = "formal"
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    ASSERTIVE = "assertive"
    APOLOGETIC = "apologetic"
    URGENT = "urgent"
    COLD_OUTREACH = "cold_outreach"


class MailPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MailAction(str, Enum):
    REPLY = "reply"
    NEW = "new"
    FORWARD = "forward"
    FOLLOW_UP = "follow_up"


@dataclass
class EmailSpec:
    """Spezifikation für eine E-Mail"""
    to: str
    subject: str
    tone: MailTone = MailTone.PROFESSIONAL
    action: MailAction = MailAction.NEW
    template: str = ""
    context: Dict = field(default_factory=dict)
    priority: MailPriority = MailPriority.MEDIUM


@dataclass
class EmailResult:
    """Ergebnis einer E-Mail Aktion"""
    success: bool
    message_id: str = ""
    error: Optional[str] = None
    preview: str = ""


class MailAgent:
    """
    Enhanced Mail Agent mit:
    - Brevo Integration
    - Templates
    - Auto-Reply
    - Follow-up Management
    """
    
    def __init__(self):
        self.templates = self.load_templates()
        self.sent_history = []
        
    def load_templates(self) -> Dict:
        """Lade E-Mail Templates"""
        return {
            # Outreach Templates
            "cold_outreach": {
                "subject": "{subject}",
                "body": """Sehr geehrte/r {name},

ich wende mich heute mit einem Angebot an Sie, das Ihre Geschäftsentwicklung voranbringen kann.

{value_proposition}

Ich biete:
• Lösung für Ihr Hauptproblem
• Schnelle Umsetzung
• Faire Preise

Hätten Sie 15 Minuten für einen kurzen Austausch?

Mit freundlichen Grüßen
{from_name}
{company}"""
            },
            
            "follow_up": {
                "subject": "Nachfrage: {subject}",
                "body": """Hallo {name},

vor einigen Tagen habe ich Ihnen geschrieben wegen {topic}.

Falls Sie Interesse haben, stehe ich gerne für Fragen zur Verfügung.

Falls nicht, keine Sorge - ich melde mich nicht wieder.

Beste Grüße
{from_name}"""
            },
            
            # Newsletter
            "newsletter": {
                "subject": "{subject}",
                "body": """Hallo {name},

Willkommen zu unserem Newsletter!

---

{content}

---

📧 Sie erhalten diese E-Mail, weil Sie sich angemeldet haben.
Abmeldung jederzeit möglich: {unsubscribe_link}

{company}
{website}"""
            },
            
            # Auto-Reply
            "auto_reply": {
                "subject": "Re: {subject}",
                "body": """Hallo {name},

vielen Dank für Ihre Nachricht.

Ich bin aktuell nicht erreichbar und melde mich ab dem {return_date} zurück.

In dringenden Fällen wenden Sie sich bitte an {alternative_contact}.

Mit freundlichen Grüßen
{from_name}"""
            },
            
            # Welcome
            "welcome": {
                "subject": "Willkommen bei {company}!",
                "body": """Hallo {name},

herzlich willkommen bei {company}!

Was Sie als Nächstes tun können:
1. Unser Produkt entdecken
2. Fragen stellen
3. Support kontaktieren

Wir freuen uns auf die Zusammenarbeit!

Beste Grüße
{from_name}"""
            },
            
            # Sales
            "sales_offer": {
                "subject": "Ihr persönliches Angebot: {offer_name}",
                "body": """Hallo {name},

basierend auf unserem Gespräch habe ich Ihnen ein individuelles Angebot erstellt:

{offer_details}

Preis: {price}
Gültig bis: {valid_until}

Fragen? Einfach antworten!

Beste Grüße
{from_name}"""
            }
        }
    
    def send_email(self, spec: EmailSpec) -> EmailResult:
        """
        Sende E-Mail via Brevo SMTP
        """
        log.info(f"📧 Sende E-Mail: {spec.to} | {spec.subject}")
        
        try:
            # Build email
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{spec.context.get('from_name', 'EmpireHazeClaw')} <noreply@empirehazeclaw.de>"
            msg['To'] = spec.to
            msg['Subject'] = spec.subject
            
            # Get template or use custom
            if spec.template and spec.template in self.templates:
                body = self.templates[spec.template]["body"]
            else:
                body = spec.context.get("body", "")
            
            # Apply tone
            body = self.apply_tone(body, spec.tone)
            
            # Fill placeholders
            body = self.fill_placeholders(body, spec.context)
            
            # Attach
            text_part = MIMEText(body, 'plain', 'utf-8')
            html_part = MIMEText(self.plain_to_html(body), 'html', 'utf-8')
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send via SMTP
            server = smtplib.SMTP(BREVO_SMTP, BREVO_PORT)
            server.starttls()
            server.login(BREVO_USER, BREVO_PASS)
            server.send_message(msg)
            server.quit()
            
            # Log
            message_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}@{spec.context.get('domain', 'empirehazeclaw.de')}"
            
            self.sent_history.append({
                "to": spec.to,
                "subject": spec.subject,
                "timestamp": datetime.now().isoformat(),
                "template": spec.template
            })
            
            log.info(f"✅ Email gesendet: {message_id}")
            
            return EmailResult(
                success=True,
                message_id=message_id,
                preview=body[:200]
            )
            
        except Exception as e:
            log.error(f"❌ Email Fehler: {e}")
            return EmailResult(
                success=False,
                error=str(e)
            )
    
    def apply_tone(self, body: str, tone: MailTone) -> str:
        """Passe Ton der E-Mail an"""
        
        tone_modifications = {
            MailTone.FORMAL: {
                "replace": [("Hallo", "Sehr geehrte/r"), ("Moin", "Guten Tag")]
            },
            MailTone.PROFESSIONAL: {
                "replace": []
            },
            MailTone.FRIENDLY: {
                "replace": [("Sehr geehrte", "Hallo"), ("Mit freundlichen Grüßen", "Viele Grüße")]
            },
            MailTone.ASSERTIVE: {
                "replace": [("vielleicht", "definitiv"), ("könnten", "können")]
            },
            MailTone.APOLOGETIC: {
                "prefix": "Entschuldigen Sie bitte die verspätete Antwort.\n\n"
            },
            MailTone.URGENT: {
                "prefix": "⚠️ WICHTIG / DRINGEND\n\n"
            }
        }
        
        modifications = tone_modifications.get(tone, {})
        
        # Apply replacements
        for old, new in modifications.get("replace", []):
            body = body.replace(old, new)
        
        # Apply prefix
        if "prefix" in modifications:
            body = modifications["prefix"] + body
        
        return body
    
    def fill_placeholders(self, body: str, context: Dict) -> str:
        """Fülle Template-Platzhalter"""
        
        defaults = {
            "name": "Herr/Frau",
            "from_name": "EmpireHazeClaw",
            "company": "EmpireHazeClaw",
            "website": "https://empirehazeclaw.de",
            "unsubscribe_link": "https://empirehazeclaw.de/unsubscribe",
            "return_date": (datetime.now() + timedelta(days=3)).strftime("%d.%m.%Y"),
            "alternative_contact": "support@empirehazeclaw.de",
            "domain": "empirehazeclaw.de"
        }
        
        # Merge with context
        values = {**defaults, **context}
        
        # Replace placeholders
        for key, value in values.items():
            placeholder = "{" + key + "}"
            body = body.replace(placeholder, str(value))
        
        return body
    
    def plain_to_html(self, text: str) -> str:
        """Konvertiere Plain Text zu HTML"""
        
        # Basic HTML conversion
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .footer {{ font-size: 12px; color: #666; margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        {text.replace('\n', '<br>').replace('---', '<hr>')}
    </div>
</body>
</html>
"""
        return html
    
    def create_outreach(self, lead: Dict, template: str = "cold_outreach") -> EmailResult:
        """Erstelle und sende Outreach E-Mail"""
        
        spec = EmailSpec(
            to=lead.get("email", ""),
            subject=f"Kurzinfo für {lead.get('company', 'Ihr Unternehmen')}",
            tone=MailTone.COLD_OUTREACH,
            action=MailAction.NEW,
            template=template,
            context={
                "name": lead.get("name", "Herr/Frau"),
                "company": lead.get("company", ""),
                "from_name": "Nick von EmpireHazeClaw",
                "value_proposition": lead.get("value_prop", "Ich zeige Ihnen, wie Sie mit KI Zeit und Geld sparen können.")
            }
        )
        
        return self.send_email(spec)
    
    def create_followup(self, original_email: Dict, days_later: int = 3) -> EmailResult:
        """Erstelle Follow-up E-Mail"""
        
        spec = EmailSpec(
            to=original_email.get("to", ""),
            subject=f"Nachfrage: {original_email.get('subject', '')}",
            tone=MailTone.PROFESSIONAL,
            action=MailAction.FOLLOW_UP,
            template="follow_up",
            context={
                "name": original_email.get("name", "Herr/Frau"),
                "topic": original_email.get("topic", "unser Angebot"),
                "from_name": original_email.get("from_name", "Nick")
            }
        )
        
        return self.send_email(spec)
    
    def create_newsletter(self, recipients: List[str], content: str, subject: str) -> Dict:
        """Sende Newsletter an mehrere Empfänger"""
        
        results = []
        
        for recipient in recipients:
            spec = EmailSpec(
                to=recipient,
                subject=subject,
                tone=MailTone.FRIENDLY,
                action=MailAction.NEW,
                template="newsletter",
                context={
                    "name": "Subscriber",
                    "content": content,
                    "from_name": "EmpireHazeClaw Team"
                }
            )
            
            result = self.send_email(spec)
            results.append({"to": recipient, "success": result.success})
        
        return {
            "total": len(recipients),
            "successful": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "results": results
        }
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """Gib E-Mail History zurück"""
        return self.sent_history[-limit:]
    
    def get_stats(self) -> Dict:
        """Gib Statistiken zurück"""
        return {
            "total_sent": len(self.sent_history),
            "by_template": self.count_by_template(),
            "last_sent": self.sent_history[-1]["timestamp"] if self.sent_history else None
        }
    
    def count_by_template(self) -> Dict:
        """Zähle nach Template"""
        counts = {}
        for entry in self.sent_history:
            template = entry.get("template", "custom")
            counts[template] = counts.get(template, 0) + 1
        return counts


async def main():
    """CLI Test"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Mail Agent")
    parser.add_argument("--to", default="test@example.com")
    parser.add_argument("--template", default="cold_outreach")
    parser.add_argument("--subject", default="Test Email")
    
    args = parser.parse_args()
    
    agent = MailAgent()
    
    # Test send
    spec = EmailSpec(
        to=args.to,
        subject=args.subject,
        template=args.template,
        context={
            "name": "Test",
            "company": "Test Company",
            "from_name": "Nick"
        }
    )
    
    result = agent.send_email(spec)
    
    print(f"\n📧 EMAIL RESULT")
    print(f"   Success: {result.success}")
    if result.message_id:
        print(f"   Message ID: {result.message_id}")
    if result.error:
        print(f"   Error: {result.error}")
    
    print(f"\n📊 STATS:")
    stats = agent.get_stats()
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
