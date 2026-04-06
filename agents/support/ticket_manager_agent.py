#!/usr/bin/env python3
"""
Ticket Manager Agent - Support Operations
Manages support tickets with full CRUD operations.
Based on SOUL.md principles: Eigenverantwortung, efficiency, action over perfection.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "ticket_manager.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TicketManager")

DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
TICKETS_FILE = DATA_DIR / "tickets.json"

# Priority levels
PRIORITIES = ["low", "medium", "high", "critical"]
STATUSES = ["open", "in_progress", "pending", "resolved", "closed"]


def load_tickets() -> dict:
    """Load tickets from JSON file."""
    try:
        if TICKETS_FILE.exists():
            with open(TICKETS_FILE, 'r') as f:
                return json.load(f)
        return {"tickets": []}
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse tickets JSON: {e}")
        return {"tickets": []}
    except Exception as e:
        logger.error(f"Failed to load tickets: {e}")
        return {"tickets": []}


def save_tickets(data: dict) -> bool:
    """Save tickets to JSON file."""
    try:
        with open(TICKETS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save tickets: {e}")
        return False


def create_ticket(title: str, description: str, priority: str = "medium", 
                  customer: str = "unknown", category: str = "general") -> dict:
    """Create a new ticket."""
    data = load_tickets()
    ticket_id = len(data["tickets"]) + 1
    now = datetime.utcnow().isoformat()
    
    ticket = {
        "id": ticket_id,
        "title": title,
        "description": description,
        "priority": priority if priority in PRIORITIES else "medium",
        "status": "open",
        "customer": customer,
        "category": category,
        "created_at": now,
        "updated_at": now,
        "comments": [],
        "tags": []
    }
    
    data["tickets"].append(ticket)
    if save_tickets(data):
        logger.info(f"Created ticket #{ticket_id}: {title}")
        return ticket
    else:
        raise Exception("Failed to save ticket")


def list_tickets(status: Optional[str] = None, priority: Optional[str] = None,
                 customer: Optional[str] = None, limit: int = 50) -> list:
    """List tickets with optional filters."""
    data = load_tickets()
    tickets = data["tickets"]
    
    if status:
        tickets = [t for t in tickets if t["status"] == status]
    if priority:
        tickets = [t for t in tickets if t["priority"] == priority]
    if customer:
        tickets = [t for t in tickets if customer.lower() in t.get("customer", "").lower()]
    
    # Sort by priority and date
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    tickets.sort(key=lambda x: (priority_order.get(x["priority"], 2), x["created_at"]))
    
    return tickets[:limit]


def get_ticket(ticket_id: int) -> Optional[dict]:
    """Get a single ticket by ID."""
    data = load_tickets()
    for ticket in data["tickets"]:
        if ticket["id"] == ticket_id:
            return ticket
    return None


def update_ticket(ticket_id: int, **kwargs) -> Optional[dict]:
    """Update ticket fields."""
    data = load_tickets()
    for ticket in data["tickets"]:
        if ticket["id"] == ticket_id:
            for key, value in kwargs.items():
                if key in ["title", "description", "priority", "status", "customer", "category"]:
                    ticket[key] = value
            ticket["updated_at"] = datetime.utcnow().isoformat()
            if save_tickets(data):
                logger.info(f"Updated ticket #{ticket_id}")
                return ticket
            return None
    return None


def add_comment(ticket_id: int, comment: str, author: str = "system") -> Optional[dict]:
    """Add a comment to a ticket."""
    data = load_tickets()
    for ticket in data["tickets"]:
        if ticket["id"] == ticket_id:
            comment_obj = {
                "author": author,
                "text": comment,
                "timestamp": datetime.utcnow().isoformat()
            }
            ticket["comments"].append(comment_obj)
            ticket["updated_at"] = datetime.utcnow().isoformat()
            if save_tickets(data):
                logger.info(f"Added comment to ticket #{ticket_id}")
                return ticket
            return None
    return None


def delete_ticket(ticket_id: int) -> bool:
    """Delete a ticket."""
    data = load_tickets()
    original_len = len(data["tickets"])
    data["tickets"] = [t for t in data["tickets"] if t["id"] != ticket_id]
    
    if len(data["tickets"]) < original_len:
        if save_tickets(data):
            logger.info(f"Deleted ticket #{ticket_id}")
            return True
    return False


def get_stats() -> dict:
    """Get ticket statistics."""
    data = load_tickets()
    tickets = data["tickets"]
    
    stats = {
        "total": len(tickets),
        "by_status": {},
        "by_priority": {},
        "avg_comments": 0
    }
    
    for t in tickets:
        stats["by_status"][t["status"]] = stats["by_status"].get(t["status"], 0) + 1
        stats["by_priority"][t["priority"]] = stats["by_priority"].get(t["priority"], 0) + 1
    
    if tickets:
        total_comments = sum(len(t.get("comments", [])) for t in tickets)
        stats["avg_comments"] = round(total_comments / len(tickets), 1)
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Ticket Manager Agent - Manage support tickets efficiently",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create --title "Login issue" --desc "Cannot login" --priority high
  %(prog)s list --status open --priority high
  %(prog)s get --id 1
  %(prog)s update --id 1 --status resolved
  %(prog)s comment --id 1 --text "Issue fixed"
  %(prog)s delete --id 1
  %(prog)s stats
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new ticket")
    create_parser.add_argument("--title", "-t", required=True, help="Ticket title")
    create_parser.add_argument("--description", "-d", required=True, help="Ticket description")
    create_parser.add_argument("--priority", "-p", choices=PRIORITIES, default="medium", help="Priority level")
    create_parser.add_argument("--customer", "-c", default="unknown", help="Customer name/email")
    create_parser.add_argument("--category", "-g", default="general", help="Ticket category")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List tickets")
    list_parser.add_argument("--status", "-s", choices=STATUSES, help="Filter by status")
    list_parser.add_argument("--priority", "-p", choices=PRIORITIES, help="Filter by priority")
    list_parser.add_argument("--customer", "-c", help="Filter by customer")
    list_parser.add_argument("--limit", "-l", type=int, default=50, help="Limit results")
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get a ticket by ID")
    get_parser.add_argument("--id", "-i", type=int, required=True, help="Ticket ID")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update a ticket")
    update_parser.add_argument("--id", "-i", type=int, required=True, help="Ticket ID")
    update_parser.add_argument("--title", "-t", help="New title")
    update_parser.add_argument("--description", "-d", help="New description")
    update_parser.add_argument("--priority", "-p", choices=PRIORITIES, help="New priority")
    update_parser.add_argument("--status", "-s", choices=STATUSES, help="New status")
    update_parser.add_argument("--customer", "-c", help="New customer")
    update_parser.add_argument("--category", "-g", help="New category")
    
    # Comment command
    comment_parser = subparsers.add_parser("comment", help="Add comment to ticket")
    comment_parser.add_argument("--id", "-i", type=int, required=True, help="Ticket ID")
    comment_parser.add_argument("--text", "-t", required=True, help="Comment text")
    comment_parser.add_argument("--author", "-a", default="system", help="Comment author")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a ticket")
    delete_parser.add_argument("--id", "-i", type=int, required=True, help="Ticket ID")
    
    # Stats command
    subparsers.add_parser("stats", help="Show ticket statistics")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        if args.command == "create":
            ticket = create_ticket(
                title=args.title,
                description=args.description,
                priority=args.priority,
                customer=args.customer,
                category=args.category
            )
            print(f"✅ Created ticket #{ticket['id']}: {ticket['title']}")
            
        elif args.command == "list":
            tickets = list_tickets(
                status=args.status,
                priority=args.priority,
                customer=args.customer,
                limit=args.limit
            )
            if not tickets:
                print("No tickets found.")
            else:
                print(f"Found {len(tickets)} ticket(s):\n")
                for t in tickets:
                    print(f"  #{t['id']} | {t['priority']:8} | {t['status']:12} | {t['title'][:50]}")
            
        elif args.command == "get":
            ticket = get_ticket(args.id)
            if ticket:
                print(f"\nTicket #{ticket['id']}")
                print(f"  Title: {ticket['title']}")
                print(f"  Description: {ticket['description']}")
                print(f"  Priority: {ticket['priority']}")
                print(f"  Status: {ticket['status']}")
                print(f"  Customer: {ticket['customer']}")
                print(f"  Category: {ticket['category']}")
                print(f"  Created: {ticket['created_at']}")
                print(f"  Updated: {ticket['updated_at']}")
                print(f"  Comments: {len(ticket.get('comments', []))}")
            else:
                print(f"Ticket #{args.id} not found.")
                return 1
                
        elif args.command == "update":
            kwargs = {k: v for k, v in vars(args).items() if k not in ['command', 'id'] and v is not None}
            ticket = update_ticket(args.id, **kwargs)
            if ticket:
                print(f"✅ Updated ticket #{ticket['id']}")
            else:
                print(f"Ticket #{args.id} not found.")
                return 1
                
        elif args.command == "comment":
            ticket = add_comment(args.id, args.text, args.author)
            if ticket:
                print(f"✅ Added comment to ticket #{ticket['id']}")
            else:
                print(f"Ticket #{args.id} not found.")
                return 1
                
        elif args.command == "delete":
            if delete_ticket(args.id):
                print(f"✅ Deleted ticket #{args.id}")
            else:
                print(f"Ticket #{args.id} not found.")
                return 1
                
        elif args.command == "stats":
            stats = get_stats()
            print("\n📊 Ticket Statistics")
            print(f"  Total Tickets: {stats['total']}")
            print(f"  Avg Comments: {stats['avg_comments']}")
            print("  By Status:")
            for status, count in stats["by_status"].items():
                print(f"    {status}: {count}")
            print("  By Priority:")
            for priority, count in stats["by_priority"].items():
                print(f"    {priority}: {count}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Command failed: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
