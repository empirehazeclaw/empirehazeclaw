#!/usr/bin/env python3
"""
Notification Manager Agent - EmpireHazeClaw
Manages multi-channel notifications (Telegram, Email, Webhook, etc.).
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Paths
BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "communication"
LOGS_DIR = BASE_DIR / "logs"
CONFIG_FILE = DATA_DIR / "notification_configs.json"
HISTORY_FILE = DATA_DIR / "notification_history.json"
LOG_FILE = LOGS_DIR / "notification_manager.log"

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
logger = logging.getLogger("NotifMgr")


def load_configs():
    """Load notification channel configurations."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"channels": {}, "templates": {}}
    return {"channels": {}, "templates": {}}


def save_configs(data):
    """Save notification channel configurations."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def load_history():
    """Load notification history."""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"notifications": []}
    return {"notifications": []}


def save_history(data):
    """Save notification history."""
    with open(HISTORY_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def add_channel(name, channel_type, config):
    """Add a notification channel."""
    data = load_configs()
    
    channel = {
        "type": channel_type,
        "config": config,
        "created_at": datetime.now().isoformat(),
        "last_used": None,
        "sent_count": 0,
        "enabled": True
    }
    
    data["channels"][name] = channel
    save_configs(data)
    logger.info(f"Added notification channel: {name} ({channel_type})")
    return channel


def remove_channel(name):
    """Remove a notification channel."""
    data = load_configs()
    if name in data["channels"]:
        del data["channels"][name]
        save_configs(data)
        return True
    return False


def enable_channel(name, enabled=True):
    """Enable or disable a channel."""
    data = load_configs()
    if name in data["channels"]:
        data["channels"][name]["enabled"] = enabled
        save_configs(data)
        return True
    return False


def list_channels():
    """List all notification channels."""
    data = load_configs()
    return data.get("channels", {})


def add_template(name, template):
    """Add a notification template."""
    data = load_configs()
    
    tpl = {
        "name": name,
        "subject": template.get("subject", ""),
        "body": template.get("body", ""),
        "variables": template.get("variables", []),
        "created_at": datetime.now().isoformat()
    }
    
    data["templates"][name] = tpl
    save_configs(data)
    return tpl


def get_template(name):
    """Get a notification template."""
    data = load_configs()
    return data.get("templates", {}).get(name)


def list_templates():
    """List all notification templates."""
    data = load_configs()
    return data.get("templates", {})


def render_template(name, variables):
    """Render a template with variables."""
    tpl = get_template(name)
    if not tpl:
        raise ValueError(f"Template '{name}' not found")
    
    subject = tpl.get("subject", "")
    body = tpl.get("body", "")
    
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        subject = subject.replace(placeholder, str(value))
        body = body.replace(placeholder, str(value))
    
    return {"subject": subject, "body": body}


def send_notification(channel_name, message, subject=None, **kwargs):
    """Send a notification via specified channel."""
    data = load_configs()
    
    if channel_name not in data["channels"]:
        raise ValueError(f"Channel '{channel_name}' not found")
    
    channel = data["channels"][channel_name]
    
    if not channel.get("enabled", True):
        raise ValueError(f"Channel '{channel_name}' is disabled")
    
    channel_type = channel["type"]
    config = channel["config"]
    
    try:
        if channel_type == "telegram":
            result = send_telegram(config, message)
        elif channel_type == "email":
            result = send_email(config, subject or "Notification", message)
        elif channel_type == "webhook":
            result = send_webhook(config, message, **kwargs)
        elif channel_type == "discord":
            result = send_discord(config, message)
        elif channel_type == "slack":
            result = send_slack(config, message)
        else:
            raise ValueError(f"Unknown channel type: {channel_type}")
        
        # Record notification
        history = load_history()
        record = {
            "id": f"notif_{int(datetime.now().timestamp())}",
            "channel": channel_name,
            "type": channel_type,
            "subject": subject,
            "message": message,
            "status": "sent",
            "sent_at": datetime.now().isoformat(),
            "result": result
        }
        history["notifications"].append(record)
        
        # Keep last 1000 records
        if len(history["notifications"]) > 1000:
            history["notifications"] = history["notifications"][-1000:]
        
        save_history(history)
        
        # Update channel stats
        channel["last_used"] = datetime.now().isoformat()
        channel["sent_count"] = channel.get("sent_count", 0) + 1
        save_configs(data)
        
        logger.info(f"Notification sent via {channel_name}")
        return record
        
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        raise


def send_telegram(config, message):
    """Send notification via Telegram."""
    import requests
    
    bot_token = config.get("bot_token")
    chat_id = config.get("chat_id")
    
    if not bot_token or not chat_id:
        raise ValueError("Telegram config requires bot_token and chat_id")
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": config.get("parse_mode", "Markdown")
    }
    
    response = requests.post(url, json=payload, timeout=10)
    result = response.json()
    
    if not result.get("ok"):
        raise Exception(f"Telegram error: {result.get('description')}")
    
    return {"message_id": result["result"]["message_id"]}


def send_email(config, subject, message):
    """Send notification via Email."""
    import smtplib
    from email.mime.text import MIMEText
    
    smtp_host = config.get("smtp_host")
    smtp_port = config.get("smtp_port", 587)
    smtp_user = config.get("smtp_user")
    smtp_pass = config.get("smtp_pass")
    to_email = config.get("to_email")
    from_email = config.get("from_email", smtp_user)
    
    if not all([smtp_host, smtp_user, smtp_pass, to_email]):
        raise ValueError("Email config incomplete")
    
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    
    with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
        server.ehlo()
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
    
    return {"sent": True}


def send_webhook(config, message, **kwargs):
    """Send notification via Webhook."""
    import requests
    import urllib.parse
    
    webhook_url = config.get("url")
    
    if not webhook_url:
        raise ValueError("Webhook config requires url")
    
    # Support different formats
    format_type = config.get("format", "json")
    
    if format_type == "json":
        payload = {"message": message, **kwargs}
        headers = {"Content-Type": "application/json"}
        response = requests.post(webhook_url, json=payload, headers=headers, timeout=10)
    elif format_type == "form":
        payload = {"message": message, **kwargs}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(webhook_url, data=urllib.parse.urlencode(payload), headers=headers, timeout=10)
    elif format_type == "text":
        # Plain text POST
        response = requests.post(webhook_url, data=message.encode('utf-8'), timeout=10)
    else:
        raise ValueError(f"Unknown webhook format: {format_type}")
    
    return {"status_code": response.status_code}


def send_discord(config, message):
    """Send notification via Discord webhook."""
    import requests
    
    webhook_url = config.get("webhook_url")
    
    if not webhook_url:
        raise ValueError("Discord config requires webhook_url")
    
    payload = {
        "content": message,
        "username": config.get("username", "Notification Bot")
    }
    
    response = requests.post(webhook_url, json=payload, timeout=10)
    
    if response.status_code != 204 and response.status_code != 200:
        raise Exception(f"Discord webhook error: {response.status_code}")
    
    return {"sent": True}


def send_slack(config, message):
    """Send notification via Slack webhook."""
    import requests
    
    webhook_url = config.get("webhook_url")
    
    if not webhook_url:
        raise ValueError("Slack config requires webhook_url")
    
    payload = {
        "text": message,
        "channel": config.get("channel"),
        "username": config.get("username", "Notification Bot")
    }
    
    response = requests.post(webhook_url, json=payload, timeout=10)
    
    if response.status_code != 200:
        raise Exception(f"Slack webhook error: {response.status_code}")
    
    return {"sent": True}


def broadcast(message, subject=None, channels=None):
    """Broadcast notification to multiple channels."""
    if channels is None:
        data = load_configs()
        channels = [name for name, ch in data["channels"].items() if ch.get("enabled", True)]
    
    results = {}
    for channel in channels:
        try:
            result = send_notification(channel, message, subject)
            results[channel] = {"status": "sent", "result": result}
        except Exception as e:
            results[channel] = {"status": "failed", "error": str(e)}
    
    return results


def get_history(limit=100, channel=None):
    """Get notification history."""
    history = load_history()
    notifications = history.get("notifications", [])
    
    if channel:
        notifications = [n for n in notifications if n.get("channel") == channel]
    
    return notifications[-limit:]


def get_stats():
    """Get notification statistics."""
    data = load_configs()
    history = load_history()
    
    channel_stats = {}
    for name, ch in data.get("channels", {}).items():
        channel_stats[name] = {
            "type": ch["type"],
            "sent": ch.get("sent_count", 0),
            "last_used": ch.get("last_used"),
            "enabled": ch.get("enabled", True)
        }
    
    return {
        "total_channels": len(data.get("channels", {})),
        "total_sent": sum(ch.get("sent_count", 0) for ch in data.get("channels", {}).values()),
        "total_notifications": len(history.get("notifications", [])),
        "channel_stats": channel_stats
    }


def main():
    parser = argparse.ArgumentParser(
        description="Notification Manager Agent - Multi-channel notifications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add Telegram channel
  %(prog)s add-channel --name my-telegram --type telegram --bot-token TOKEN --chat-id CHATID
  
  # Add Discord webhook channel
  %(prog)s add-channel --name my-discord --type discord --webhook-url https://discord.com/api/webhooks/...
  
  # Add webhook channel
  %(prog)s add-channel --name my-webhook --type webhook --url https://example.com/hook --format json
  
  # Send notification
  %(prog)s send --channel my-telegram --message "Hello from Notification Agent!"
  
  # Broadcast to all channels
  %(prog)s broadcast --message "System Alert!"
  
  # List channels
  %(prog)s channels
  
  # View history
  %(prog)s history
  
  # View stats
  %(prog)s stats
  
  # Add template
  %(prog)s add-template --name alert --subject "Alert: {{title}}" --body "{{message}}"
  
  # Send using template
  %(prog)s send --channel my-telegram --template alert --vars title=Critical,message=System down
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add channel command
    add_ch_parser = subparsers.add_parser('add-channel', help='Add notification channel')
    add_ch_parser.add_argument('--name', required=True, help='Channel name')
    add_ch_parser.add_argument('--type', required=True, 
                               choices=['telegram', 'email', 'webhook', 'discord', 'slack'],
                               help='Channel type')
    # Telegram options
    add_ch_parser.add_argument('--bot-token', help='Telegram bot token')
    add_ch_parser.add_argument('--chat-id', help='Telegram chat ID')
    # Discord/Slack options
    add_ch_parser.add_argument('--webhook-url', help='Discord/Slack webhook URL')
    # Email options
    add_ch_parser.add_argument('--smtp-host', help='SMTP host')
    add_ch_parser.add_argument('--smtp-port', type=int, help='SMTP port')
    add_ch_parser.add_argument('--smtp-user', help='SMTP username')
    add_ch_parser.add_argument('--smtp-pass', help='SMTP password')
    add_ch_parser.add_argument('--to-email', help='Recipient email')
    add_ch_parser.add_argument('--from-email', help='From email')
    # Webhook options
    add_ch_parser.add_argument('--url', help='Webhook URL')
    add_ch_parser.add_argument('--format', choices=['json', 'form', 'text'], default='json', help='Webhook format')
    # Generic
    add_ch_parser.add_argument('--username', help='Display username for Discord/Slack')
    
    # Remove channel command
    remove_ch_parser = subparsers.add_parser('remove-channel', help='Remove notification channel')
    remove_ch_parser.add_argument('--name', required=True, help='Channel name')
    
    # Enable/disable channel
    toggle_parser = subparsers.add_parser('toggle-channel', help='Enable/disable channel')
    toggle_parser.add_argument('--name', required=True, help='Channel name')
    toggle_parser.add_argument('--on', action='store_true', help='Enable')
    toggle_parser.add_argument('--off', action='store_true', help='Disable')
    
    # Channels command
    subparsers.add_parser('channels', help='List notification channels')
    
    # Send command
    send_parser = subparsers.add_parser('send', help='Send notification')
    send_parser.add_argument('--channel', required=True, help='Channel name')
    send_parser.add_argument('--message', help='Message to send')
    send_parser.add_argument('--subject', help='Subject (for email)')
    send_parser.add_argument('--template', help='Template name to use')
    send_parser.add_argument('--vars', help='Variables as key=value pairs')
    
    # Broadcast command
    broadcast_parser = subparsers.add_parser('broadcast', help='Broadcast to all channels')
    broadcast_parser.add_argument('--message', required=True, help='Message to send')
    broadcast_parser.add_argument('--subject', help='Subject (for email)')
    broadcast_parser.add_argument('--channels', help='Comma-separated channel names (or all if not specified)')
    
    # History command
    history_parser = subparsers.add_parser('history', help='View notification history')
    history_parser.add_argument('--limit', type=int, default=50, help='Number of records')
    history_parser.add_argument('--channel', help='Filter by channel')
    
    # Stats command
    subparsers.add_parser('stats', help='View notification statistics')
    
    # Template commands
    add_tpl_parser = subparsers.add_parser('add-template', help='Add notification template')
    add_tpl_parser.add_argument('--name', required=True, help='Template name')
    add_tpl_parser.add_argument('--subject', help='Subject with {{variables}}')
    add_tpl_parser.add_argument('--body', required=True, help='Body with {{variables}}')
    
    subparsers.add_parser('templates', help='List notification templates')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        if args.command == 'add-channel':
            # Build config based on type
            if args.type == 'telegram':
                config = {"bot_token": args.bot_token, "chat_id": args.chat_id}
            elif args.type == 'email':
                config = {
                    "smtp_host": args.smtp_host,
                    "smtp_port": args.smtp_port or 587,
                    "smtp_user": args.smtp_user,
                    "smtp_pass": args.smtp_pass,
                    "to_email": args.to_email,
                    "from_email": args.from_email or args.smtp_user
                }
            elif args.type in ['discord', 'slack']:
                config = {"webhook_url": args.webhook_url, "username": args.username}
            elif args.type == 'webhook':
                config = {"url": args.url, "format": args.format}
            else:
                config = {}
            
            add_channel(args.name, args.type, config)
            print(f"✅ Added channel '{args.name}' ({args.type})")
            return 0
        
        elif args.command == 'remove-channel':
            if remove_channel(args.name):
                print(f"✅ Removed channel '{args.name}'")
                return 0
            else:
                print(f"❌ Channel '{args.name}' not found")
                return 1
        
        elif args.command == 'toggle-channel':
            enabled = not args.off
            if enable_channel(args.name, enabled):
                status = "enabled" if enabled else "disabled"
                print(f"✅ Channel '{args.name}' {status}")
                return 0
            else:
                print(f"❌ Channel '{args.name}' not found")
                return 1
        
        elif args.command == 'channels':
            channels = list_channels()
            if not channels:
                print("No notification channels configured.")
                print("Use: notification-manager add-channel --name mychan --type telegram ...")
                return 0
            
            print(f"\n📢 Notification Channels ({len(channels)}):")
            print("-" * 60)
            
            for name, ch in channels.items():
                status = "✅" if ch.get("enabled", True) else "❌"
                print(f"\n  {status} [{name}]")
                print(f"     Type: {ch['type']}")
                print(f"     Sent: {ch.get('sent_count', 0)}")
                print(f"     Last used: {ch.get('last_used', 'Never')}")
            return 0
        
        elif args.command == 'send':
            message = args.message
            
            if args.template:
                variables = {}
                if args.vars:
                    for pair in args.vars.split(','):
                        if '=' in pair:
                            key, value = pair.split('=', 1)
                            variables[key.strip()] = value.strip()
                
                rendered = render_template(args.template, variables)
                subject = rendered.get("subject") if args.subject is None else args.subject
                message = rendered.get("body")
            
            if not message:
                print("❌ No message provided (use --message or --template)")
                return 1
            
            result = send_notification(args.channel, message, args.subject)
            print(f"✅ Notification sent via {args.channel}")
            print(f"   Status: {result['status']}")
            return 0
        
        elif args.command == 'broadcast':
            channels = None
            if args.channels:
                channels = [c.strip() for c in args.channels.split(',')]
            
            results = broadcast(args.message, args.subject, channels)
            
            print(f"\n📢 Broadcast Results:")
            for channel, result in results.items():
                icon = "✅" if result["status"] == "sent" else "❌"
                print(f"   {icon} {channel}: {result['status']}")
            return 0
        
        elif args.command == 'history':
            history = get_history(args.limit, args.channel)
            
            if not history:
                print("No notifications sent yet.")
                return 0
            
            print(f"\n📜 Notification History ({len(history)} records):")
            print("-" * 70)
            
            for record in history[-args.limit:]:
                icon = "✅" if record["status"] == "sent" else "❌"
                print(f"\n  {icon} [{record['channel']}] {record['type']}")
                print(f"     Message: {record['message'][:50]}...")
                print(f"     Sent: {record['sent_at']}")
            return 0
        
        elif args.command == 'stats':
            stats = get_stats()
            
            print(f"\n📊 Notification Statistics:")
            print(f"   Total channels: {stats['total_channels']}")
            print(f"   Total sent: {stats['total_sent']}")
            print(f"   History records: {stats['total_notifications']}")
            
            if stats['channel_stats']:
                print(f"\n📢 Per-Channel Stats:")
                for name, ch_stats in stats['channel_stats'].items():
                    enabled = "✅" if ch_stats['enabled'] else "❌"
                    print(f"   {enabled} [{name}] ({ch_stats['type']}): {ch_stats['sent']} sent")
            return 0
        
        elif args.command == 'add-template':
            add_template(args.name, {"subject": args.subject or "", "body": args.body})
            print(f"✅ Added template '{args.name}'")
            return 0
        
        elif args.command == 'templates':
            templates = list_templates()
            if not templates:
                print("No templates configured.")
                return 0
            
            print(f"\n📝 Notification Templates ({len(templates)}):")
            for name, tpl in templates.items():
                print(f"   [{name}]")
                if tpl.get('subject'):
                    print(f"       Subject: {tpl['subject']}")
                print(f"       Body: {tpl['body'][:50]}...")
            return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
