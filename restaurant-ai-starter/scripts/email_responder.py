#!/usr/bin/env python3
"""
📧 RESTAURANT EMAIL AUTORESPONDER
==================================
Automatic email responses for common restaurant inquiries.

Usage:
    python3 email_responder.py --test
    python3 email_responder.py --inquiry reservation --name "John" --date "2026-04-01"

Author: EmpireHazeClaw
Version: 1.0
"""

import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
CONFIG_FILE = Path(__file__).parent.parent / "data" / "email_config.json"

class RestaurantEmailResponder:
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self):
        """Load email configuration"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        
        # Default config
        return {
            "restaurant_name": "Ihr Restaurant",
            "from_email": "info@ihr-restaurant.de",
            "from_name": "Restaurant Team",
            "reply_to": "info@ihr-restaurant.de",
            "address": "Musterstraße 1, 12345 Musterstadt",
            "phone": "+49 123 456789",
            "opening_hours": {
                "monday": "11:00 - 22:00",
                "tuesday": "11:00 - 22:00",
                "wednesday": "11:00 - 22:00",
                "thursday": "11:00 - 22:00",
                "friday": "11:00 - 23:00",
                "saturday": "12:00 - 23:00",
                "sunday": "12:00 - 21:00"
            }
        }
    
    def get_opening_hours_text(self):
        """Format opening hours as text"""
        days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        day_keys = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        
        lines = []
        for day, key in zip(days, day_keys):
            lines.append(f"{day}: {self.config['opening_hours'].get(key, 'Geschlossen')}")
        return "\n".join(lines)
    
    def generate_reservation_response(self, name, date, time, guests, phone="", email=""):
        """Generate reservation confirmation email"""
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: white; padding: 30px; text-align: center;">
                <h1 style="margin: 0;">{self.config['restaurant_name']}</h1>
            </div>
            
            <div style="padding: 30px; background: #f9f9f9;">
                <h2 style="color: #333;">Hallo {name},</h2>
                
                <p>vielen Dank für Ihre Reservierungsanfrage! Wir freuen uns auf Ihren Besuch.</p>
                
                <div style="background: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h3 style="color: #00ff88; margin-top: 0;">📅 Ihre Reservierung</h3>
                    <p><strong>Datum:</strong> {date}</p>
                    <p><strong>Uhrzeit:</strong> {time}</p>
                    <p><strong>Personen:</strong> {guests}</p>
                </div>
                
                <div style="background: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h3 style="color: #333; margin-top: 0;">📍 So finden Sie uns</h3>
                    <p>{self.config['address']}</p>
                    <p><strong>Telefon:</strong> {self.config['phone']}</p>
                </div>
                
                <div style="background: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h3 style="color: #333; margin-top: 0;">🕐 Öffnungszeiten</h3>
                    <pre style="font-family: Arial, sans-serif;">{self.get_opening_hours_text()}</pre>
                </div>
                
                <p style="color: #666; font-size: 14px;">
                    <strong>Wichtige Hinweise:</strong><br>
                    • Bitte melden Sie sich bei Verspätungen telefonisch<br>
                    • Tischreservierungen halten wir 15 Minuten frei<br>
                    • Stornierung bis 24h vorher kostenfrei
                </p>
                
                <p>Bei Fragen sind wir gerne für Sie da!</p>
                
                <p>Beste Grüße,<br>
                Ihr {self.config['restaurant_name']} Team</p>
            </div>
            
            <div style="background: #333; color: #999; padding: 20px; text-align: center; font-size: 12px;">
                <p style="margin: 0;">{self.config['restaurant_name']} | {self.config['address']}</p>
            </div>
        </body>
        </html>
        """
        
        text = f"""
        Hallo {name},

        vielen Dank für Ihre Reservierungsanfrage!

        IHRE RESERVIERUNG:
        Datum: {date}
        Uhrzeit: {time}
        Personen: {guests}

        SO FINDEN SIE UNS:
        {self.config['address']}
        Telefon: {self.config['phone']}

        ÖFFNUNGSZEITEN:
        {self.get_opening_hours_text()}

        WICHTIGE HINWEISE:
        - Bitte melden Sie sich bei Verspätungen telefonisch
        - Tischreservierungen halten wir 15 Minuten frei
        - Stornierung bis 24h vorher kostenlos

        Bei Fragen sind wir gerne für Sie da!

        Beste Grüße,
        Ihr {self.config['restaurant_name']} Team
        """
        
        return html, text
    
    def generate_catering_response(self, name, email, phone, event_type, guests, date=""):
        """Generate catering inquiry response"""
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: white; padding: 30px; text-align: center;">
                <h1 style="margin: 0;">{self.config['restaurant_name']}</h1>
                <p style="margin: 10px 0 0;">Catering & Events</p>
            </div>
            
            <div style="padding: 30px; background: #f9f9f9;">
                <h2 style="color: #333;">Hallo {name},</h2>
                
                <p>vielen Dank für Ihr Interesse an unserem Catering-Service!</p>
                
                <p>Wir haben Ihre Anfrage erhalten:</p>
                
                <div style="background: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <p><strong>Event-Typ:</strong> {event_type}</p>
                    <p><strong>Personen:</strong> {guests}</p>
                    <p><strong>Datum:</strong> {date if date else 'Noch nicht确定'}</p>
                </div>
                
                <p>Ein Mitglied unseres Catering-Teams wird sich innerhalb von 24 Stunden bei Ihnen melden, um:</p>
                <ul>
                    <li>Ihre genauen Wünsche zu besprechen</li>
                    <li>Individuelles Angebot zu erstellen</li>
                    <li>eine Besichtigung unserer Räumlichkeiten zu vereinbaren</li>
                </ul>
                
                <p><strong>Kontaktdaten:</strong><br>
                Telefon: {self.config['phone']}<br>
                Email: {self.config['reply_to']}</p>
                
                <p>Beste Grüße,<br>
                Ihr {self.config['restaurant_name']} Team</p>
            </div>
        </body>
        </html>
        """
        
        return html, "Text version would go here"
    
    def generate_feedback_thanks(self, name):
        """Generate thank you for feedback"""
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: white; padding: 30px; text-align: center;">
                <h1 style="margin: 0;">{self.config['restaurant_name']}</h1>
            </div>
            
            <div style="padding: 30px; background: #f9f9f9;">
                <h2 style="color: #333;">Hallo {name},</h2>
                
                <p>vielen Dank, dass Sie sich die Zeit genommen haben, uns Feedback zu geben!</p>
                
                <p>Ihr Feedback ist uns sehr wichtig und hilft uns, unseren Service stetig zu verbessern.</p>
                
                <p>Wir würden uns freuen, Sie bald wieder bei uns begrüßen zu dürfen.</p>
                
                <p>Beste Grüße,<br>
                Ihr {self.config['restaurant_name']} Team</p>
            </div>
        </body>
        </html>
        """
        
        return html, None
    
    def generate_waitlist_confirmation(self, name, date, time, guests):
        """Generate waitlist confirmation"""
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: white; padding: 30px; text-align: center;">
                <h1 style="margin: 0;">{self.config['restaurant_name']}</h1>
            </div>
            
            <div style="padding: 30px; background: #f9f9f9;">
                <h2 style="color: #333;">Hallo {name},</h2>
                
                <p>Sie wurden auf unsere Warteliste gesetzt!</p>
                
                <div style="background: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <p><strong>Gewünschtes Datum:</strong> {date}</p>
                    <p><strong>Uhrzeit:</strong> {time}</p>
                    <p><strong>Personen:</strong> {guests}</p>
                </div>
                
                <p>Sobald ein Tisch verfügbar wird, werden wir Sie umgehend kontaktieren.</p>
                
                <p>Bitte haben Sie Verständnis, dass wir bei hoher Nachfrage nicht immer einen Tisch anbieten können.</p>
                
                <p>Beste Grüße,<br>
                Ihr {self.config['restaurant_name']} Team</p>
            </div>
        </body>
        </html>
        """
        
        return html, None
    
    def generate_birthday_reminder(self, name, birthday_date):
        """Generate birthday celebration reminder"""
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: white; padding: 30px; text-align: center;">
                <h1 style="margin: 0;">🎉 Happy Birthday!</h1>
            </div>
            
            <div style="padding: 30px; background: #f9f9f9;">
                <h2 style="color: #333;">Hallo {name},</h2>
                
                <p>wir wissen, dass bald Ihr Geburtstag ansteht ({birthday_date}), und möchten Sie herzlich einladen, diesen bei uns zu feiern!</p>
                
                <div style="background: white; padding: 20px; border-radius: 10px; margin: 20px 0; text-align: center;">
                    <h3 style="color: #00ff88; margin-top: 0;">🎁 Geburtstags-Überraschung</h3>
                    <p>Kommen Sie vorbei und erhalten Sie ein <strong>gratis Dessert</strong> zum Geburtstag!</p>
                </div>
                
                <p>Reservieren Sie jetzt und teilen Sie uns mit, dass Sie Ihren Geburtstag bei uns feiern möchten.</p>
                
                <p>Wir freuen uns auf Sie!</p>
                
                <p>Beste Grüße,<br>
                Ihr {self.config['restaurant_name']} Team</p>
            </div>
        </body>
        </html>
        """
        
        return html, None

def send_email(to_email, subject, html_body, text_body=None):
    """Send email via SMTP"""
    # This is a placeholder - integrate with your actual email sending solution
    print(f"📧 Sending email to: {to_email}")
    print(f"   Subject: {subject}")
    print(f"   HTML: {len(html_body)} chars")
    return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Restaurant Email Autoresponder")
    parser.add_argument('--test', action='store_true', help='Send test email')
    parser.add_argument('--inquiry', choices=['reservation', 'catering', 'feedback', 'waitlist'], 
                        help='Type of inquiry')
    parser.add_argument('--name', default="Test Gast", help='Guest name')
    parser.add_argument('--email', default="test@example.com", help='Email address')
    parser.add_argument('--date', default="2026-04-01", help='Date')
    parser.add_argument('--time', default="19:00", help='Time')
    parser.add_argument('--guests', type=int, default=2, help='Number of guests')
    parser.add_argument('--phone', default="", help='Phone number')
    
    args = parser.parse_args()
    
    responder = RestaurantEmailResponder()
    
    if args.inquiry == 'reservation':
        html, text = responder.generate_reservation_response(
            name=args.name,
            date=args.date,
            time=args.time,
            guests=args.guests,
            phone=args.phone,
            email=args.email
        )
        send_email(args.email, "Reservierungsbestätigung", html, text)
        print("✅ Reservation response generated!")
    
    elif args.inquiry == 'catering':
        html, text = responder.generate_catering_response(
            name=args.name,
            email=args.email,
            phone=args.phone,
            event_type="Firmenevent",
            guests=args.guests,
            date=args.date
        )
        send_email(args.email, "Catering-Anfrage erhalten", html, text)
        print("✅ Catering response generated!")
    
    elif args.inquiry == 'waitlist':
        html, text = responder.generate_waitlist_confirmation(
            name=args.name,
            date=args.date,
            time=args.time,
            guests=args.guests
        )
        send_email(args.email, "Wartelisten-Bestätigung", html, text)
        print("✅ Waitlist confirmation generated!")
    
    elif args.test:
        html, text = responder.generate_reservation_response(
            name="Test Gast",
            date="2026-04-01",
            time="19:00",
            guests=4
        )
        print("✅ Test email generated successfully!")
        print(f"\nPreview ({len(html)} chars):")
        print(html[:500] + "...")

if __name__ == "__main__":
    main()
