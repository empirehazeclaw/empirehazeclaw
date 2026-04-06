#!/usr/bin/env python3
"""
SMS Agent - EmpireHazeClaw
Sends SMS messages via configured providers (Twilio, etc.).
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Paths
BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "communication"
LOGS_DIR = BASE_DIR / "logs"
CONFIG_FILE = DATA_DIR / "sms_configs.json"
SENT_FILE = DATA_DIR / "sms_sent.json"
LOG_FILE = LOGS_DIR / "sms_agent.log"

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
logger = logging.getLogger("SMSAgent")


def load_configs():
    """Load SMS provider configurations."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"providers": {}, "default": None}
    return {"providers": {}, "default": None}


def save_configs(data):
    """Save SMS provider configurations."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def load_sent():
    """Load sent SMS history."""
    if SENT_FILE.exists():
        try:
            with open(SENT_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"sent": []}
    return {"sent": []}


def save_sent(data):
    """Save sent SMS history."""
    with open(SENT_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def add_provider(name, provider_type, api_key, api_secret=None, from_number=None, **kwargs):
    """Add SMS provider configuration."""
    configs = load_configs()
    
    provider = {
        "type": provider_type,
        "api_key": api_key,
        "api_secret": api_secret,
        "from_number": from_number,
        "created_at": datetime.now().isoformat(),
        "last_used": None,
        "sent_count": 0,
        "settings": kwargs
    }
    
    configs["providers"][name] = provider
    
    # Set as default if first provider
    if configs["default"] is None:
        configs["default"] = name
    
    save_configs(configs)
    logger.info(f"Added SMS provider: {name} ({provider_type})")
    return provider


def remove_provider(name):
    """Remove SMS provider configuration."""
    configs = load_configs()
    if name in configs["providers"]:
        del configs["providers"][name]
        if configs["default"] == name:
            configs["default"] = list(configs["providers"].keys())[0] if configs["providers"] else None
        save_configs(configs)
        logger.info(f"Removed provider: {name}")
        return True
    return False


def set_default_provider(name):
    """Set default SMS provider."""
    configs = load_configs()
    if name in configs["providers"]:
        configs["default"] = name
        save_configs(configs)
        return True
    return False


def send_sms(provider_name, to_number, message, from_number=None):
    """Send SMS via provider."""
    configs = load_configs()
    
    # Use default provider if not specified
    if provider_name is None:
        provider_name = configs.get("default")
        if provider_name is None:
            raise ValueError("No SMS provider configured. Add a provider first.")
    
    if provider_name not in configs["providers"]:
        raise ValueError(f"Provider '{provider_name}' not found")
    
    provider = configs["providers"][provider_name]
    
    # Validate phone number
    to_number = validate_phone(to_number)
    if not to_number:
        raise ValueError(f"Invalid phone number: {to_number}")
    
    # Use from_number from provider if not specified
    if from_number is None:
        from_number = provider.get("from_number")
    
    # Send via appropriate provider
    try:
        if provider["type"].lower() == "twilio":
            result = send_twilio(provider, to_number, message, from_number)
        elif provider["type"].lower() == "vonage":
            result = send_vonage(provider, to_number, message)
        elif provider["type"].lower() == "messagebird":
            result = send_messagebird(provider, to_number, message)
        elif provider["type"].lower() == "mock":
            result = send_mock(provider, to_number, message, from_number)
        else:
            raise ValueError(f"Unknown provider type: {provider['type']}")
        
        # Record sent SMS
        sent_data = load_sent()
        sent_record = {
            "id": f"sms_{int(datetime.now().timestamp())}",
            "provider": provider_name,
            "to": to_number,
            "from": from_number,
            "message": message,
            "status": "sent",
            "sent_at": datetime.now().isoformat(),
            "result": result
        }
        sent_data["sent"].append(sent_record)
        
        # Keep only last 1000 records
        if len(sent_data["sent"]) > 1000:
            sent_data["sent"] = sent_data["sent"][-1000:]
        
        save_sent(sent_data)
        
        # Update provider stats
        provider["last_used"] = datetime.now().isoformat()
        provider["sent_count"] = provider.get("sent_count", 0) + 1
        save_configs(configs)
        
        logger.info(f"SMS sent via {provider_name} to {to_number}")
        return sent_record
        
    except Exception as e:
        logger.error(f"Failed to send SMS: {e}")
        raise


def validate_phone(phone):
    """Validate and normalize phone number."""
    # Remove spaces, dashes, parentheses
    phone = ''.join(c for c in phone if c.isdigit() or c == '+')
    
    # Ensure it starts with + and country code
    if not phone.startswith('+'):
        if len(phone) >= 10:
            phone = '+' + phone
        else:
            return None
    
    # Basic validation: should be reasonable length
    if len(phone) < 8 or len(phone) > 15:
        return None
    
    return phone


def send_twilio(provider, to_number, message, from_number):
    """Send SMS via Twilio."""
    try:
        from twilio.rest import Client
        
        client = Client(provider["api_key"], provider["api_secret"])
        
        msg = client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
        
        return {"sid": msg.sid, "status": str(msg.status)}
    except ImportError:
        logger.warning("Twilio library not installed, using mock send")
        return send_mock(provider, to_number, message, from_number)
    except Exception as e:
        raise Exception(f"Twilio error: {e}")


def send_vonage(provider, to_number, message):
    """Send SMS via Vonage."""
    try:
        import vonage
        
        client = vonage.Client(key=provider["api_key"], secret=provider["api_secret"])
        
        result = client.send_message({
            "from": provider.get("from_number", "EmpireHazeClaw"),
            "to": to_number.replace('+', ''),
            "text": message
        })
        
        return {"success": result["messages"][0]["status"] == "0"}
    except ImportError:
        raise Exception("Vonage library not installed")
    except Exception as e:
        raise Exception(f"Vonage error: {e}")


def send_messagebird(provider, to_number, message):
    """Send SMS via MessageBird."""
    try:
        import messagebird
        
        client = messagebird.Client(provider["api_key"])
        
        msg = client.message_create(
            provider.get("from_number", "EmpireHazeClaw"),
            to_number,
            message
        )
        
        return {"id": msg.id, "status": msg.status}
    except ImportError:
        raise Exception("MessageBird library not installed")
    except Exception as e:
        raise Exception(f"MessageBird error: {e}")


def send_mock(provider, to_number, message, from_number):
    """Mock send for testing without API."""
    logger.info(f"[MOCK] Sending SMS to {to_number} from {from_number}: {message[:50]}...")
    return {"mock": True, "status": "sent"}


def list_providers():
    """List all configured SMS providers."""
    configs = load_configs()
    return configs.get("providers", {}), configs.get("default")


def get_sent_history(limit=50):
    """Get SMS sent history."""
    sent_data = load_sent()
    return sent_data.get("sent", [])[-limit:]


def get_stats():
    """Get SMS statistics."""
    configs = load_configs()
    sent_data = load_sent()
    
    total_sent = sum(p.get("sent_count", 0) for p in configs.get("providers", {}).values())
    
    return {
        "total_sent": total_sent,
        "providers_count": len(configs.get("providers", {})),
        "default_provider": configs.get("default"),
        "history_count": len(sent_data.get("sent", []))
    }


def main():
    parser = argparse.ArgumentParser(
        description="SMS Agent - Send SMS messages via configured providers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add Twilio provider
  %(prog)s add --name twilio --type twilio --key YOUR_SID --secret YOUR_TOKEN --from +1234567890
  
  # Add mock provider for testing
  %(prog)s add --name mock --type mock --from +1234567890
  
  # Send SMS
  %(prog)s send --to +49123456789 --message "Hello from SMS Agent!"
  
  # Send via specific provider
  %(prog)s send --provider twilio --to +49123456789 --message "Hello!"
  
  # List providers
  %(prog)s providers
  
  # View sent history
  %(prog)s history
  
  # View stats
  %(prog)s stats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add provider command
    add_parser = subparsers.add_parser('add', help='Add SMS provider')
    add_parser.add_argument('--name', required=True, help='Provider name')
    add_parser.add_argument('--type', required=True, choices=['twilio', 'vonage', 'messagebird', 'mock'], help='Provider type')
    add_parser.add_argument('--key', '--api-key', dest='api_key', help='API Key (required for non-mock providers)')
    add_parser.add_argument('--secret', '--api-secret', dest='api_secret', help='API Secret')
    add_parser.add_argument('--from', dest='from_number', help='From phone number')
    
    # Remove provider command
    remove_parser = subparsers.add_parser('remove', help='Remove SMS provider')
    remove_parser.add_argument('--name', required=True, help='Provider name')
    
    # Set default command
    default_parser = subparsers.add_parser('default', help='Set default provider')
    default_parser.add_argument('--name', required=True, help='Provider name')
    
    # Send command
    send_parser = subparsers.add_parser('send', help='Send SMS')
    send_parser.add_argument('--to', required=True, help='Recipient phone number')
    send_parser.add_argument('--message', required=True, help='SMS message')
    send_parser.add_argument('--from', dest='from_number', help='From phone number')
    send_parser.add_argument('--provider', help='Provider name (uses default if not specified)')
    
    # Providers command
    subparsers.add_parser('providers', help='List SMS providers')
    
    # History command
    history_parser = subparsers.add_parser('history', help='View sent SMS history')
    history_parser.add_argument('--limit', type=int, default=50, help='Number of records')
    
    # Stats command
    subparsers.add_parser('stats', help='View SMS statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        if args.command == 'add':
            provider = add_provider(
                args.name, args.type, args.api_key,
                args.api_secret, args.from_number
            )
            print(f"✅ Added SMS provider '{args.name}' ({args.type})")
            return 0
        
        elif args.command == 'remove':
            if remove_provider(args.name):
                print(f"✅ Removed provider '{args.name}'")
                return 0
            else:
                print(f"❌ Provider '{args.name}' not found")
                return 1
        
        elif args.command == 'default':
            if set_default_provider(args.name):
                print(f"✅ Set default provider to '{args.name}'")
                return 0
            else:
                print(f"❌ Provider '{args.name}' not found")
                return 1
        
        elif args.command == 'send':
            result = send_sms(args.provider, args.to, args.message, args.from_number)
            print(f"✅ SMS sent to {args.to}")
            print(f"   Provider: {result['provider']}")
            print(f"   Status: {result['status']}")
            return 0
        
        elif args.command == 'providers':
            providers, default = list_providers()
            
            if not providers:
                print("No SMS providers configured.")
                print("Use: sms-agent add --name myprovider --type twilio --key KEY --secret SECRET")
                return 0
            
            print(f"\n📱 SMS Providers ({len(providers)}):")
            print("-" * 50)
            
            for name, prov in providers.items():
                default_marker = " (default)" if name == default else ""
                print(f"\n  [{name}]{default_marker}")
                print(f"    Type: {prov['type']}")
                print(f"    From: {prov.get('from_number', 'N/A')}")
                print(f"    Sent: {prov.get('sent_count', 0)}")
                print(f"    Last used: {prov.get('last_used', 'Never')}")
            return 0
        
        elif args.command == 'history':
            history = get_sent_history(args.limit)
            
            if not history:
                print("No SMS sent yet.")
                return 0
            
            print(f"\n📤 SMS History ({len(history)} records):")
            print("-" * 60)
            
            for record in history:
                print(f"\n  → {record['to']}")
                print(f"     Message: {record['message'][:40]}...")
                print(f"     Provider: {record['provider']} | Status: {record['status']}")
                print(f"     Sent: {record['sent_at']}")
            return 0
        
        elif args.command == 'stats':
            stats = get_stats()
            
            print(f"\n📊 SMS Statistics:")
            print(f"   Total sent: {stats['total_sent']}")
            print(f"   Providers: {stats['providers_count']}")
            print(f"   Default: {stats['default_provider'] or 'None'}")
            print(f"   History records: {stats['history_count']}")
            return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
