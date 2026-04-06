#!/usr/bin/env python3
"""
Auto Responder Agent - Support Operations
Manages auto-response rules and templates for customer support.
Based on SOUL.md principles: fast response, efficiency, no waiting.
"""

import argparse
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "auto_responder.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AutoResponder")

DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
RESPONSES_FILE = DATA_DIR / "auto_responses.json"
LOGS_FILE = DATA_DIR / "auto_responder_logs.json"

CHANNELS = ["email", "telegram", "chat", "api"]


def load_responses() -> dict:
    """Load auto-response rules."""
    try:
        if RESPONSES_FILE.exists():
            with open(RESPONSES_FILE, 'r') as f:
                return json.load(f)
        return {"rules": [], "templates": []}
    except Exception as e:
        logger.error(f"Failed to load responses: {e}")
        return {"rules": [], "templates": []}


def save_responses(data: dict) -> bool:
    """Save auto-response rules."""
    try:
        with open(RESPONSES_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save responses: {e}")
        return False


def load_logs() -> dict:
    """Load response logs."""
    try:
        if LOGS_FILE.exists():
            with open(LOGS_FILE, 'r') as f:
                return json.load(f)
        return {"logs": []}
    except Exception as e:
        return {"logs": []}


def save_logs(data: dict) -> bool:
    """Save response logs."""
    try:
        with open(LOGS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        return False


def create_rule(name: str, match_pattern: str, response: str,
                channel: str = "email", priority: int = 5,
                active: bool = True, case_sensitive: bool = False) -> dict:
    """Create an auto-response rule."""
    data = load_responses()
    rule_id = len(data["rules"]) + 1

    # Validate regex
    try:
        re.compile(match_pattern)
    except re.error as e:
        raise ValueError(f"Invalid regex pattern: {e}")

    rule = {
        "id": rule_id,
        "name": name,
        "match_pattern": match_pattern,
        "response": response,
        "channel": channel if channel in CHANNELS else "email",
        "priority": max(1, min(10, priority)),
        "active": active,
        "case_sensitive": case_sensitive,
        "created_at": datetime.utcnow().isoformat(),
        "trigger_count": 0
    }

    data["rules"].append(rule)
    if save_responses(data):
        logger.info(f"Created rule #{rule_id}: {name}")
        return rule
    raise Exception("Failed to save rule")


def match_rule(message: str, channel: str = "email") -> Optional[Dict]:
    """Find first matching rule for a message."""
    data = load_responses()

    # Get active rules, sorted by priority
    active_rules = [r for r in data["rules"] if r.get("active", True)]
    active_rules.sort(key=lambda x: x.get("priority", 5), reverse=True)

    for rule in active_rules:
        if rule.get("channel") and rule["channel"] != channel:
            continue

        pattern = rule["match_pattern"]
        if not rule.get("case_sensitive", False):
            pattern = pattern.lower()
            message_check = message.lower()
        else:
            message_check = message

        try:
            if re.search(pattern, message_check):
                # Increment trigger count
                rule["trigger_count"] = rule.get("trigger_count", 0) + 1
                save_responses(data)

                # Log the match
                logs = load_logs()
                logs["logs"].append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "rule_id": rule["id"],
                    "rule_name": rule["name"],
                    "channel": channel,
                    "matched": True
                })
                # Keep only last 1000 logs
                logs["logs"] = logs["logs"][-1000:]
                save_logs(logs)

                return rule
        except re.error:
            continue

    return None


def test_response(message: str, channel: str = "email") -> Dict:
    """Test what response would be triggered for a message."""
    matched_rule = match_rule(message, channel)

    result = {
        "matched": matched_rule is not None,
        "message": message,
        "channel": channel
    }

    if matched_rule:
        result["rule_id"] = matched_rule["id"]
        result["rule_name"] = matched_rule["name"]
        result["response"] = matched_rule["response"]
        result["priority"] = matched_rule.get("priority", 5)
    else:
        result["response"] = None
        result["suggestion"] = "No matching rule found. Consider creating one."

    return result


def list_rules(channel: Optional[str] = None, active_only: bool = False) -> List[Dict]:
    """List all rules with optional filters."""
    data = load_responses()
    rules = data["rules"]

    if channel:
        rules = [r for r in rules if r.get("channel") == channel]
    if active_only:
        rules = [r for r in rules if r.get("active", True)]

    rules.sort(key=lambda x: (x.get("priority", 5), x["id"]), reverse=True)
    return rules


def update_rule(rule_id: int, **kwargs) -> Optional[Dict]:
    """Update a rule."""
    data = load_responses()
    for rule in data["rules"]:
        if rule["id"] == rule_id:
            for key, value in kwargs.items():
                if key in ["name", "match_pattern", "response", "channel",
                          "priority", "active", "case_sensitive"]:
                    if key == "match_pattern":
                        try:
                            re.compile(value)
                        except re.error as e:
                            raise ValueError(f"Invalid regex: {e}")
                    rule[key] = value
            if save_responses(data):
                logger.info(f"Updated rule #{rule_id}")
                return rule
            return None
    return None


def delete_rule(rule_id: int) -> bool:
    """Delete a rule."""
    data = load_responses()
    original_len = len(data["rules"])
    data["rules"] = [r for r in data["rules"] if r["id"] != rule_id]

    if len(data["rules"]) < original_len:
        if save_responses(data):
            logger.info(f"Deleted rule #{rule_id}")
            return True
    return False


def toggle_rule(rule_id: int) -> Optional[Dict]:
    """Toggle rule active status."""
    data = load_responses()
    for rule in data["rules"]:
        if rule["id"] == rule_id:
            rule["active"] = not rule.get("active", True)
            if save_responses(data):
                logger.info(f"Toggled rule #{rule_id} to {'active' if rule['active'] else 'inactive'}")
                return rule
            return None
    return None


def get_stats() -> Dict:
    """Get auto-responder statistics."""
    data = load_responses()
    logs = load_logs()

    stats = {
        "total_rules": len(data.get("rules", [])),
        "active_rules": len([r for r in data.get("rules", []) if r.get("active", True)]),
        "total_triggers": sum(r.get("trigger_count", 0) for r in data.get("rules", [])),
        "recent_triggers": len([l for l in logs.get("logs", [])
                               if datetime.fromisoformat(l["timestamp"].replace("Z", "+00:00")) >
                                  datetime.utcnow().replace(hour=0, minute=0, second=0)])
    }
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Auto Responder Agent - Manage automated response rules",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create --name "Password Reset" --pattern "password|reset" --response "To reset..."
  %(prog)s test --message "I forgot my password"
  %(prog)s list --channel telegram --active-only
  %(prog)s update --id 1 --active false
  %(prog)s toggle --id 1
  %(prog)s delete --id 1
  %(prog)s stats
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create
    create_parser = subparsers.add_parser("create", help="Create a new rule")
    create_parser.add_argument("--name", "-n", required=True, help="Rule name")
    create_parser.add_argument("--pattern", "-p", required=True, help="Match regex pattern")
    create_parser.add_argument("--response", "-r", required=True, help="Response text")
    create_parser.add_argument("--channel", "-c", choices=CHANNELS, default="email", help="Channel")
    create_parser.add_argument("--priority", type=int, default=5, help="Priority (1-10)")
    create_parser.add_argument("--case-sensitive", action="store_true", help="Case sensitive match")

    # Test
    test_parser = subparsers.add_parser("test", help="Test a message against rules")
    test_parser.add_argument("--message", "-m", required=True, help="Test message")
    test_parser.add_argument("--channel", "-c", choices=CHANNELS, default="email", help="Channel")

    # List
    list_parser = subparsers.add_parser("list", help="List rules")
    list_parser.add_argument("--channel", "-c", choices=CHANNELS, help="Filter by channel")
    list_parser.add_argument("--active-only", action="store_true", help="Show only active rules")

    # Update
    update_parser = subparsers.add_parser("update", help="Update a rule")
    update_parser.add_argument("--id", "-i", type=int, required=True, help="Rule ID")
    update_parser.add_argument("--name", "-n", help="New name")
    update_parser.add_argument("--pattern", "-p", help="New pattern")
    update_parser.add_argument("--response", "-r", help="New response")
    update_parser.add_argument("--channel", "-c", choices=CHANNELS, help="New channel")
    update_parser.add_argument("--priority", type=int, help="New priority")
    update_parser.add_argument("--active", type=lambda x: x.lower() == "true", help="Active status")

    # Toggle
    toggle_parser = subparsers.add_parser("toggle", help="Toggle rule active status")
    toggle_parser.add_argument("--id", "-i", type=int, required=True, help="Rule ID")

    # Delete
    delete_parser = subparsers.add_parser("delete", help="Delete a rule")
    delete_parser.add_argument("--id", "-i", type=int, required=True, help="Rule ID")

    # Stats
    subparsers.add_parser("stats", help="Show statistics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    try:
        if args.command == "create":
            rule = create_rule(
                name=args.name,
                match_pattern=args.pattern,
                response=args.response,
                channel=args.channel,
                priority=args.priority,
                case_sensitive=args.case_sensitive
            )
            print(f"✅ Created rule #{rule['id']}: {rule['name']}")

        elif args.command == "test":
            result = test_response(args.message, args.channel)
            if result["matched"]:
                print(f"✅ Matched rule #{result['rule_id']}: {result['rule_name']}")
                print(f"   Priority: {result['priority']}")
                print(f"   Response: {result['response'][:100]}{'...' if len(result['response']) > 100 else ''}")
            else:
                print(f"❌ No matching rule for: {args.message}")
                print(f"   Suggestion: {result.get('suggestion', '')}")

        elif args.command == "list":
            rules = list_rules(channel=args.channel if 'channel' in args else None,
                              active_only=args.active_only if hasattr(args, 'active_only') else False)
            if not rules:
                print("No rules found.")
            else:
                print(f"Found {len(rules)} rule(s):\n")
                for r in rules:
                    status = "✅" if r.get("active", True) else "❌"
                    print(f"  {status} #{r['id']} | P{r.get('priority', 5)} | {r.get('channel', 'email'):8} | {r['name'][:40]}")
                    print(f"         Pattern: {r['match_pattern'][:50]}")
                    print(f"         Triggered: {r.get('trigger_count', 0)} times")

        elif args.command == "update":
            kwargs = {k: v for k, v in vars(args).items()
                      if k not in ['command', 'id'] and v is not None}
            rule = update_rule(args.id, **kwargs)
            if rule:
                print(f"✅ Updated rule #{rule['id']}")
            else:
                print(f"Rule #{args.id} not found.")
                return 1

        elif args.command == "toggle":
            rule = toggle_rule(args.id)
            if rule:
                status = "activated" if rule["active"] else "deactivated"
                print(f"✅ Rule #{rule['id']} {status}")
            else:
                print(f"Rule #{args.id} not found.")
                return 1

        elif args.command == "delete":
            if delete_rule(args.id):
                print(f"✅ Deleted rule #{args.id}")
            else:
                print(f"Rule #{args.id} not found.")
                return 1

        elif args.command == "stats":
            stats = get_stats()
            print("\n📊 Auto Responder Statistics")
            print(f"  Total Rules: {stats['total_rules']}")
            print(f"  Active Rules: {stats['active_rules']}")
            print(f"  Total Triggers: {stats['total_triggers']}")
            print(f"  Triggers Today: {stats['recent_triggers']}")

        return 0

    except ValueError as e:
        print(f"❌ Validation Error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Command failed: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
