#!/usr/bin/env python3
"""
Escalation Manager Agent - Support Operations
Manages ticket escalation rules, workflows and notifications.
Based on SOUL.md principles: Eigenverantwortung, action over waiting.
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "escalation_manager.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("EscalationManager")

DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
ESCALATIONS_FILE = DATA_DIR / "escalations.json"
HISTORY_FILE = DATA_DIR / "escalation_history.json"

TICKETS_FILE = DATA_DIR / "tickets.json"

PRIORITY_LEVELS = {"low": 1, "medium": 2, "high": 3, "critical": 4}
ESCALATION_LEVELS = ["support", "senior", "manager", "director", "executive"]


def load_escalations() -> dict:
    """Load escalation rules."""
    try:
        if ESCALATIONS_FILE.exists():
            with open(ESCALATIONS_FILE, 'r') as f:
                return json.load(f)
        return {"rules": [], "settings": {"auto_escalate_hours": 24}}
    except Exception as e:
        logger.error(f"Failed to load escalations: {e}")
        return {"rules": [], "settings": {"auto_escalate_hours": 24}}


def save_escalations(data: dict) -> bool:
    """Save escalation rules."""
    try:
        with open(ESCALATIONS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save escalations: {e}")
        return False


def load_history() -> dict:
    """Load escalation history."""
    try:
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        return {"history": []}
    except Exception as e:
        return {"history": []}


def save_history(data: dict) -> bool:
    """Save escalation history."""
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        return False


def load_tickets() -> dict:
    """Load tickets for escalation checking."""
    try:
        if TICKETS_FILE.exists():
            with open(TICKETS_FILE, 'r') as f:
                return json.load(f)
        return {"tickets": []}
    except Exception as e:
        return {"tickets": []}


def create_rule(name: str, trigger_type: str, trigger_value: str,
                escalation_level: str, action: str, notify: bool = True) -> dict:
    """Create an escalation rule."""
    data = load_escalations()
    rule_id = len(data["rules"]) + 1

    if escalation_level not in ESCALATION_LEVELS:
        raise ValueError(f"Invalid escalation level. Must be one of: {ESCALATION_LEVELS}")

    rule = {
        "id": rule_id,
        "name": name,
        "trigger_type": trigger_type,  # priority, time, status, keyword
        "trigger_value": trigger_value,
        "escalation_level": escalation_level,
        "action": action,
        "notify": notify,
        "active": True,
        "created_at": datetime.utcnow().isoformat(),
        "triggered_count": 0
    }

    data["rules"].append(rule)
    if save_escalations(data):
        logger.info(f"Created escalation rule #{rule_id}: {name}")
        return rule
    raise Exception("Failed to save rule")


def check_escalations() -> List[Dict]:
    """Check all tickets for escalation triggers."""
    data = load_escalations()
    tickets_data = load_tickets()
    rules = [r for r in data.get("rules", []) if r.get("active", True)]
    
    triggered = []
    now = datetime.utcnow()
    
    for ticket in tickets_data.get("tickets", []):
        if ticket.get("status") in ["resolved", "closed"]:
            continue
        
        ticket_level = ticket.get("escalation_level", "support")
        ticket_level_idx = ESCALATION_LEVELS.index(ticket_level) if ticket_level in ESCALATION_LEVELS else 0
        
        for rule in rules:
            should_escalate = False
            
            if rule["trigger_type"] == "priority":
                priority_val = PRIORITY_LEVELS.get(ticket.get("priority", "low"), 1)
                trigger_val = PRIORITY_LEVELS.get(rule["trigger_value"], 0)
                should_escalate = priority_val >= trigger_val
                
            elif rule["trigger_type"] == "time":
                created = datetime.fromisoformat(ticket.get("created_at", now.isoformat()))
                hours_old = (now - created).total_seconds() / 3600
                try:
                    threshold_hours = float(rule["trigger_value"])
                    should_escalate = hours_old >= threshold_hours
                except ValueError:
                    pass
                
            elif rule["trigger_type"] == "status":
                should_escalate = ticket.get("status") == rule["trigger_value"]
                
            elif rule["trigger_type"] == "keyword":
                content = f"{ticket.get('title', '')} {ticket.get('description', '')}".lower()
                should_escalate = rule["trigger_value"].lower() in content
            
            if should_escalate:
                target_idx = ESCALATION_LEVELS.index(rule["escalation_level"])
                # Only escalate if target level is higher
                if target_idx > ticket_level_idx:
                    triggered.append({
                        "ticket_id": ticket["id"],
                        "ticket_title": ticket["title"],
                        "current_level": ticket_level,
                        "target_level": rule["escalation_level"],
                        "rule_id": rule["id"],
                        "rule_name": rule["name"],
                        "action": rule["action"],
                        "notify": rule.get("notify", True)
                    })
                    rule["triggered_count"] = rule.get("triggered_count", 0) + 1

    # Save updated trigger counts
    save_escalations(data)
    return triggered


def list_rules(active_only: bool = False, level: Optional[str] = None) -> List[Dict]:
    """List escalation rules."""
    data = load_escalations()
    rules = data.get("rules", [])
    
    if active_only:
        rules = [r for r in rules if r.get("active", True)]
    if level:
        rules = [r for r in rules if r.get("escalation_level") == level]
    
    rules.sort(key=lambda x: (x.get("triggered_count", 0), x["id"]), reverse=True)
    return rules


def update_rule(rule_id: int, **kwargs) -> Optional[Dict]:
    """Update an escalation rule."""
    data = load_escalations()
    for rule in data["rules"]:
        if rule["id"] == rule_id:
            for key, value in kwargs.items():
                if key in ["name", "trigger_type", "trigger_value", "escalation_level",
                          "action", "notify", "active"]:
                    rule[key] = value
            if save_escalations(data):
                logger.info(f"Updated escalation rule #{rule_id}")
                return rule
            return None
    return None


def delete_rule(rule_id: int) -> bool:
    """Delete an escalation rule."""
    data = load_escalations()
    original_len = len(data["rules"])
    data["rules"] = [r for r in data["rules"] if r["id"] != rule_id]
    
    if len(data["rules"]) < original_len:
        if save_escalations(data):
            logger.info(f"Deleted escalation rule #{rule_id}")
            return True
    return False


def get_history(ticket_id: Optional[int] = None, limit: int = 50) -> List[Dict]:
    """Get escalation history."""
    history = load_history().get("history", [])
    
    if ticket_id:
        history = [h for h in history if h.get("ticket_id") == ticket_id]
    
    return history[-limit:]


def get_stats() -> Dict:
    """Get escalation statistics."""
    data = load_escalations()
    history = load_history().get("history", [])
    
    stats = {
        "total_rules": len(data.get("rules", [])),
        "active_rules": len([r for r in data.get("rules", []) if r.get("active", True)]),
        "total_escalations": len(history),
        "by_level": {},
        "pending_checks": 0
    }
    
    for h in history:
        level = h.get("target_level", "unknown")
        stats["by_level"][level] = stats["by_level"].get(level, 0) + 1
    
    # Check for pending escalations
    triggered = check_escalations()
    stats["pending_checks"] = len(triggered)
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Escalation Manager Agent - Manage ticket escalation workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create --name "Critical Priority" --trigger priority --value critical --level senior --action "assign_senior"
  %(prog)s create --name "24h Old Ticket" --trigger time --value 24 --level manager --action "notify_manager"
  %(prog)s check
  %(prog)s list --active-only
  %(prog)s history --ticket-id 1
  %(prog)s update --id 1 --active false
  %(prog)s delete --id 1
  %(prog)s stats
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create
    create_parser = subparsers.add_parser("create", help="Create escalation rule")
    create_parser.add_argument("--name", "-n", required=True, help="Rule name")
    create_parser.add_argument("--trigger", "-t", required=True,
                               choices=["priority", "time", "status", "keyword"],
                               help="Trigger type")
    create_parser.add_argument("--value", "-v", required=True, help="Trigger value")
    create_parser.add_argument("--level", "-l", required=True, choices=ESCALATION_LEVELS,
                               help="Escalation level")
    create_parser.add_argument("--action", "-a", required=True, help="Action to take")
    create_parser.add_argument("--no-notify", action="store_true", help="Disable notification")

    # Check
    check_parser = subparsers.add_parser("check", help="Check tickets for escalations")

    # List
    list_parser = subparsers.add_parser("list", help="List escalation rules")
    list_parser.add_argument("--active-only", action="store_true", help="Show only active")
    list_parser.add_argument("--level", choices=ESCALATION_LEVELS, help="Filter by level")

    # Update
    update_parser = subparsers.add_parser("update", help="Update a rule")
    update_parser.add_argument("--id", "-i", type=int, required=True, help="Rule ID")
    update_parser.add_argument("--name", "-n", help="New name")
    update_parser.add_argument("--trigger", "-t", choices=["priority", "time", "status", "keyword"])
    update_parser.add_argument("--value", "-v", help="New value")
    update_parser.add_argument("--level", "-l", choices=ESCALATION_LEVELS, help="New level")
    update_parser.add_argument("--action", "-a", help="New action")
    update_parser.add_argument("--active", type=lambda x: x.lower() == "true", help="Active status")

    # Delete
    delete_parser = subparsers.add_parser("delete", help="Delete a rule")
    delete_parser.add_argument("--id", "-i", type=int, required=True, help="Rule ID")

    # History
    history_parser = subparsers.add_parser("history", help="Show escalation history")
    history_parser.add_argument("--ticket-id", type=int, help="Filter by ticket ID")
    history_parser.add_argument("--limit", type=int, default=50, help="Limit results")

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
                trigger_type=args.trigger,
                trigger_value=args.value,
                escalation_level=args.level,
                action=args.action,
                notify=not args.no_notify
            )
            print(f"✅ Created escalation rule #{rule['id']}: {rule['name']}")

        elif args.command == "check":
            print("🔍 Checking tickets for escalations...")
            triggered = check_escalations()
            if not triggered:
                print("✅ No escalations needed.")
            else:
                print(f"⚠️  Found {len(triggered)} potential escalation(s):\n")
                for t in triggered:
                    print(f"  Ticket #{t['ticket_id']}: {t['ticket_title'][:40]}")
                    print(f"    {t['current_level']} → {t['target_level']} (Rule: {t['rule_name']})")
                    print(f"    Action: {t['action']}")

        elif args.command == "list":
            rules = list_rules(
                active_only=args.active_only if hasattr(args, 'active_only') else False,
                level=args.level if hasattr(args, 'level') else None
            )
            if not rules:
                print("No escalation rules found.")
            else:
                print(f"Found {len(rules)} rule(s):\n")
                for r in rules:
                    status = "✅" if r.get("active", True) else "❌"
                    print(f"  {status} #{r['id']} | {r.get('escalation_level', '?'):10} | {r['name']}")
                    print(f"         Trigger: {r['trigger_type']}={r['trigger_value']}")
                    print(f"         Action: {r['action']} | Triggered: {r.get('triggered_count', 0)}")

        elif args.command == "update":
            kwargs = {k: v for k, v in vars(args).items()
                      if k not in ['command', 'id'] and v is not None}
            rule = update_rule(args.id, **kwargs)
            if rule:
                print(f"✅ Updated escalation rule #{rule['id']}")
            else:
                print(f"Rule #{args.id} not found.")
                return 1

        elif args.command == "delete":
            if delete_rule(args.id):
                print(f"✅ Deleted escalation rule #{args.id}")
            else:
                print(f"Rule #{args.id} not found.")
                return 1

        elif args.command == "history":
            history = get_history(
                ticket_id=args.ticket_id if hasattr(args, 'ticket_id') else None,
                limit=args.limit if hasattr(args, 'limit') else 50
            )
            if not history:
                print("No escalation history found.")
            else:
                print(f"Recent escalations:\n")
                for h in history:
                    print(f"  [{h.get('timestamp', '?')}] Ticket #{h.get('ticket_id')}")
                    print(f"    {h.get('from_level', '?')} → {h.get('to_level', '?')}")

        elif args.command == "stats":
            stats = get_stats()
            print("\n📊 Escalation Statistics")
            print(f"  Total Rules: {stats['total_rules']}")
            print(f"  Active Rules: {stats['active_rules']}")
            print(f"  Total Escalations: {stats['total_escalations']}")
            print(f"  Pending Checks: {stats['pending_checks']}")
            print("  By Level:")
            for level, count in stats["by_level"].items():
                print(f"    {level}: {count}")

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
