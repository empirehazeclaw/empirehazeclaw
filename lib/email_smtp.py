#!/usr/bin/env python3
"""
📧 Gmail SMTP Email Sender
Uses App Password instead of OAuth (simpler for servers)

Setup:
1. Enable 2FA on Google Account
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Set environment variables:
   export GMAIL_USER="empirehazeclaw@gmail.com"
   export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"

Usage:
    python3 email_smtp.py --to test@example.com --subject "Test" --body "Hello"
    python3 email_smtp.py --to test@example.com --subject "Test" --body "Hello" --attach file.pdf
"""

import os
import sys
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path

DEFAULT_FROM = "empirehazeclaw@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587  # TLS

def send_email(to_email, subject, body, from_email=None, app_password=None, html=False, attachments=None):
    """
    Send email via Gmail SMTP
    
    Args:
        to_email: Recipient email
        subject: Email subject
        body: Email body (plain text or HTML)
        from_email: Sender email (default: GMAIL_USER env)
        app_password: App password (default: GMAIL_APP_PASSWORD env)
        html: If True, body is HTML
        attachments: List of file paths to attach
    
    Returns:
        (success: bool, message: str)
    """
    from_email = from_email or os.environ.get("GMAIL_USER", DEFAULT_FROM)
    app_password = app_password or os.environ.get("GMAIL_APP_PASSWORD", "")
    
    if not app_password:
        return False, "GMAIL_APP_PASSWORD not set"
    
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        
        # Attach body
        content_type = "html" if html else "plain"
        msg.attach(MIMEText(body, content_type, "utf-8"))
        
        # Attach files
        if attachments:
            for filepath in attachments:
                path = Path(filepath)
                if not path.exists():
                    continue
                
                with open(path, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={path.name}"
                )
                msg.attach(part)
        
        # Connect and send
        context = ssl.create_default_context()
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(from_email, app_password)
            server.sendmail(from_email, to_email, msg.as_string())
        
        return True, "Email sent"
        
    except smtplib.SMTPAuthenticationError:
        return False, "Auth failed - check App Password"
    except smtplib.SMTPException as e:
        return False, f"SMTP error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def test_connection():
    """Test SMTP connection"""
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            return True, "Connection OK"
    except Exception as e:
        return False, str(e)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Send Email via Gmail SMTP")
    parser.add_argument("--to", required=True, help="Recipient email")
    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument("--body", required=True, help="Email body")
    parser.add_argument("--html", action="store_true", help="Body is HTML")
    parser.add_argument("--attach", nargs="*", help="Attachment files")
    parser.add_argument("--test", action="store_true", help="Test SMTP connection")
    
    args = parser.parse_args()
    
    if args.test:
        success, msg = test_connection()
        print(f"{'✅' if success else '❌'} {msg}")
        return
    
    success, msg = send_email(
        args.to,
        args.subject,
        args.body,
        html=args.html,
        attachments=args.attach
    )
    
    print(f"{'✅' if success else '❌'} {msg}")

if __name__ == "__main__":
    main()
