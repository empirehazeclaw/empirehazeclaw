#!/usr/bin/env python3
"""
SMTP Manager Agent - EmpireHazeClaw
Manages SMTP configurations and sends emails via configured servers.
"""

import argparse
import json
import logging
import os
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# Paths
BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "emails"
LOGS_DIR = BASE_DIR / "logs"
CONFIG_FILE = DATA_DIR / "smtp_configs.json"
LOG_FILE = LOGS_DIR / "smtp_manager.log"

# Ensure directories exist
LOGS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("SMTPMgr")


def load_configs():
    """Load SMTP configurations from JSON file."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error("Corrupted smtp_configs.json, creating new one")
            return {"configs": {}}
    return {"configs": {}}


def save_configs(data):
    """Save SMTP configurations to JSON file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def add_config(name, host, port, username, password, use_tls=True, from_email=None, from_name=None):
    """Add a new SMTP configuration."""
    configs = load_configs()
    
    config = {
        "host": host,
        "port": int(port),
        "username": username,
        "password": password,
        "use_tls": use_tls,
        "from_email": from_email or username,
        "from_name": from_name or username.split('@')[0] if '@' in username else username,
        "created_at": datetime.now().isoformat(),
        "last_used": None,
        "sent_count": 0
    }
    
    configs["configs"][name] = config
    save_configs(configs)
    logger.info(f"Added SMTP config: {name}")
    return config


def test_connection(name):
    """Test SMTP connection."""
    configs = load_configs()
    if name not in configs["configs"]:
        logger.error(f"Config '{name}' not found")
        return False
    
    cfg = configs["configs"][name]
    
    try:
        if cfg.get("use_tls", True):
            server = smtplib.SMTP(cfg["host"], cfg["port"], timeout=10)
            server.ehlo()
            server.starttls()
            server.ehlo()
        else:
            server = smtplib.SMTP(cfg["host"], cfg["port"], timeout=10)
        
        server.login(cfg["username"], cfg["password"])
        server.quit()
        logger.info(f"Connection test successful for: {name}")
        return True
    except Exception as e:
        logger.error(f"Connection test failed for {name}: {e}")
        return False


def send_email(config_name, to_email, subject, body, html_body=None):
    """Send an email using a configured SMTP server."""
    configs = load_configs()
    
    if config_name not in configs["configs"]:
        raise ValueError(f"Config '{config_name}' not found")
    
    cfg = configs["configs"][config_name]
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f"{cfg['from_name']} <{cfg['from_email']}>"
    msg['To'] = to_email
    
    # Attach plain text
    part1 = MIMEText(body, 'plain')
    msg.attach(part1)
    
    # Attach HTML if provided
    if html_body:
        part2 = MIMEText(html_body, 'html')
        msg.attach(part2)
    
    try:
        if cfg.get("use_tls", True):
            server = smtplib.SMTP(cfg["host"], cfg["port"], timeout=30)
            server.ehlo()
            server.starttls()
            server.ehlo()
        else:
            server = smtplib.SMTP(cfg["host"], cfg["port"], timeout=30)
        
        server.login(cfg["username"], cfg["password"])
        server.sendmail(cfg["from_email"], [to_email], msg.as_string())
        server.quit()
        
        # Update stats
        configs["configs"][config_name]["last_used"] = datetime.now().isoformat()
        configs["configs"][config_name]["sent_count"] = configs["configs"][config_name].get("sent_count", 0) + 1
        save_configs(configs)
        
        logger.info(f"Email sent via {config_name} to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise


def list_configs():
    """List all SMTP configurations."""
    configs = load_configs()
    return configs.get("configs", {})


def remove_config(name):
    """Remove an SMTP configuration."""
    configs = load_configs()
    if name in configs["configs"]:
        del configs["configs"][name]
        save_configs(configs)
        logger.info(f"Removed config: {name}")
        return True
    return False


def main():
    parser = argparse.ArgumentParser(
        description="SMTP Manager Agent - Manage SMTP configs and send emails",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add a new SMTP configuration
  %(prog)s add --name gmail --host smtp.gmail.com --port 587 --user user@gmail.com --pass 'password'
  
  # List all configurations
  %(prog)s list
  
  # Test a connection
  %(prog)s test --name gmail
  
  # Send an email
  %(prog)s send --config gmail --to recipient@example.com --subject "Hello" --body "Message"
  
  # Remove a configuration
  %(prog)s remove --name gmail
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add new SMTP configuration')
    add_parser.add_argument('--name', required=True, help='Config name')
    add_parser.add_argument('--host', required=True, help='SMTP host')
    add_parser.add_argument('--port', type=int, default=587, help='SMTP port (default: 587)')
    add_parser.add_argument('--user', '--username', dest='username', required=True, help='SMTP username')
    add_parser.add_argument('--pass', '--password', dest='password', required=True, help='SMTP password')
    add_parser.add_argument('--no-tls', action='store_true', help='Disable TLS')
    add_parser.add_argument('--from-email', help='From email address')
    add_parser.add_argument('--from-name', help='From name')
    
    # List command
    subparsers.add_parser('list', help='List all SMTP configurations')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test SMTP connection')
    test_parser.add_argument('--name', required=True, help='Config name to test')
    
    # Send command
    send_parser = subparsers.add_parser('send', help='Send email via SMTP')
    send_parser.add_argument('--config', '--name', dest='config', required=True, help='Config name')
    send_parser.add_argument('--to', required=True, help='Recipient email')
    send_parser.add_argument('--subject', required=True, help='Email subject')
    send_parser.add_argument('--body', required=True, help='Email body (plain text)')
    send_parser.add_argument('--html', help='Email body (HTML)')
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove SMTP configuration')
    remove_parser.add_argument('--name', required=True, help='Config name to remove')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        if args.command == 'add':
            config = add_config(
                args.name, args.host, args.port,
                args.username, args.password,
                use_tls=not args.no_tls,
                from_email=args.from_email,
                from_name=args.from_name
            )
            print(f"✅ Added SMTP config '{args.name}'")
            return 0
        
        elif args.command == 'list':
            configs = list_configs()
            if not configs:
                print("No SMTP configurations found.")
                return 0
            print(f"\n📧 SMTP Configurations ({len(configs)}):")
            print("-" * 60)
            for name, cfg in configs.items():
                print(f"\n  [{name}]")
                print(f"    Host: {cfg['host']}:{cfg['port']}")
                print(f"    User: {cfg['username']}")
                print(f"    TLS: {'Yes' if cfg.get('use_tls', True) else 'No'}")
                print(f"    From: {cfg.get('from_name', 'N/A')} <{cfg.get('from_email', 'N/A')}>")
                print(f"    Sent: {cfg.get('sent_count', 0)} emails")
                print(f"    Last used: {cfg.get('last_used', 'Never')}")
            print()
            return 0
        
        elif args.command == 'test':
            if test_connection(args.name):
                print(f"✅ Connection successful for '{args.name}'")
                return 0
            else:
                print(f"❌ Connection failed for '{args.name}'")
                return 1
        
        elif args.command == 'send':
            send_email(args.config, args.to, args.subject, args.body, args.html)
            print(f"✅ Email sent to {args.to}")
            return 0
        
        elif args.command == 'remove':
            if remove_config(args.name):
                print(f"✅ Removed config '{args.name}'")
                return 0
            else:
                print(f"❌ Config '{args.name}' not found")
                return 1
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
