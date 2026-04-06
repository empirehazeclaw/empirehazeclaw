#!/usr/bin/env python3
"""
Client Manager Agent - Freelance Division
Manages client relationships, contacts, and communication history.

Inspired by SOUL.md: CEO mindset, Eigenverantwortung, Transparenz
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
WORKSPACE = SCRIPT_DIR.parent.parent.parent
LOG_DIR = WORKSPACE / "logs"
DATA_DIR = WORKSPACE / "data" / "freelance"
CLIENTS_FILE = DATA_DIR / "clients.json"

# Ensure directories exist
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - CLIENT-MANAGER - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "client_manager.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def load_clients():
    """Load clients from JSON file."""
    if not CLIENTS_FILE.exists():
        return {"clients": [], "version": "1.0"}
    try:
        with open(CLIENTS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse clients file: {e}")
        return {"clients": [], "version": "1.0"}


def save_clients(data):
    """Save clients to JSON file."""
    try:
        with open(CLIENTS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved {len(data['clients'])} clients to {CLIENTS_FILE}")
    except IOError as e:
        logger.error(f"Failed to save clients: {e}")
        raise


def add_client(name, email, phone=None, company=None, notes=None):
    """Add a new client."""
    data = load_clients()
    
    # Check for duplicate email
    for client in data['clients']:
        if client['email'].lower() == email.lower():
            logger.warning(f"Client with email {email} already exists")
            print(f"⚠️  Client with email '{email}' already exists.")
            return False
    
    new_client = {
        "id": len(data['clients']) + 1,
        "name": name,
        "email": email,
        "phone": phone,
        "company": company,
        "notes": notes or "",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "status": "active",
        "projects": [],
        "total_revenue": 0.0,
        "interactions": []
    }
    
    data['clients'].append(new_client)
    save_clients(data)
    logger.info(f"Added new client: {name} ({email})")
    print(f"✅ Added client: {name} <{email}>")
    return True


def list_clients(status_filter=None):
    """List all clients."""
    data = load_clients()
    clients = data['clients']
    
    if status_filter:
        clients = [c for c in clients if c.get('status') == status_filter]
    
    if not clients:
        print("📭 No clients found.")
        return
    
    print(f"\n📋 Clients ({len(clients)} total):")
    print("-" * 80)
    for client in clients:
        status_emoji = "🟢" if client.get('status') == 'active' else "🔴"
        print(f"{status_emoji} [{client['id']}] {client['name']} - {client['email']}")
        if client.get('company'):
            print(f"   Company: {client['company']}")
        if client.get('total_revenue', 0) > 0:
            print(f"   Revenue: ${client['total_revenue']:.2f}")
        print()


def get_client(client_id):
    """Get a specific client by ID."""
    data = load_clients()
    for client in data['clients']:
        if client['id'] == client_id:
            return client
    return None


def show_client(client_id):
    """Display detailed client information."""
    client = get_client(client_id)
    if not client:
        print(f"❌ Client with ID {client_id} not found.")
        return
    
    print(f"\n👤 Client Details:")
    print("=" * 60)
    print(f"ID:         {client['id']}")
    print(f"Name:       {client['name']}")
    print(f"Email:      {client['email']}")
    print(f"Phone:      {client.get('phone', 'N/A')}")
    print(f"Company:    {client.get('company', 'N/A')}")
    print(f"Status:     {client.get('status', 'active')}")
    print(f"Created:    {client.get('created_at', 'N/A')}")
    print(f"Revenue:    ${client.get('total_revenue', 0):.2f}")
    print(f"Notes:      {client.get('notes', 'N/A')}")
    
    if client.get('projects'):
        print(f"\n📁 Projects ({len(client['projects'])}):")
        for proj in client['projects']:
            print(f"   - {proj}")
    
    if client.get('interactions'):
        print(f"\n💬 Recent Interactions ({len(client['interactions'])}):")
        for interaction in client['interactions'][-5:]:
            print(f"   [{interaction.get('date', 'N/A')}] {interaction.get('type', 'note')}: {interaction.get('note', '')[:50]}")


def update_client(client_id, **kwargs):
    """Update client information."""
    data = load_clients()
    
    for client in data['clients']:
        if client['id'] == client_id:
            for key, value in kwargs.items():
                if key in ['name', 'email', 'phone', 'company', 'notes', 'status']:
                    client[key] = value
            client['updated_at'] = datetime.now().isoformat()
            save_clients(data)
            logger.info(f"Updated client {client_id}: {kwargs}")
            print(f"✅ Updated client {client_id}")
            return True
    
    print(f"❌ Client with ID {client_id} not found.")
    return False


def delete_client(client_id):
    """Delete a client (soft delete by setting status to inactive)."""
    return update_client(client_id, status="inactive")


def add_interaction(client_id, interaction_type, note):
    """Add an interaction/note to a client."""
    data = load_clients()
    
    for client in data['clients']:
        if client['id'] == client_id:
            interaction = {
                "date": datetime.now().isoformat(),
                "type": interaction_type,
                "note": note
            }
            client.setdefault('interactions', []).append(interaction)
            client['updated_at'] = datetime.now().isoformat()
            save_clients(data)
            logger.info(f"Added {interaction_type} interaction to client {client_id}")
            print(f"✅ Added {interaction_type} interaction to client {client_id}")
            return True
    
    print(f"❌ Client with ID {client_id} not found.")
    return False


def link_project(client_id, project_name):
    """Link a project to a client."""
    data = load_clients()
    
    for client in data['clients']:
        if client['id'] == client_id:
            client.setdefault('projects', []).append(project_name)
            client['updated_at'] = datetime.now().isoformat()
            save_clients(data)
            logger.info(f"Linked project '{project_name}' to client {client_id}")
            print(f"✅ Linked project '{project_name}' to client {client['name']}")
            return True
    
    print(f"❌ Client with ID {client_id} not found.")
    return False


def update_revenue(client_id, amount):
    """Update client's total revenue."""
    data = load_clients()
    
    for client in data['clients']:
        if client['id'] == client_id:
            client['total_revenue'] = client.get('total_revenue', 0) + amount
            client['updated_at'] = datetime.now().isoformat()
            save_clients(data)
            logger.info(f"Updated revenue for client {client_id}: +${amount:.2f}")
            print(f"✅ Added ${amount:.2f} to client {client['name']}'s total revenue (now ${client['total_revenue']:.2f})")
            return True
    
    print(f"❌ Client with ID {client_id} not found.")
    return False


def get_stats():
    """Show client statistics."""
    data = load_clients()
    clients = data['clients']
    
    active = len([c for c in clients if c.get('status') == 'active'])
    inactive = len([c for c in clients if c.get('status') == 'inactive'])
    total_revenue = sum(c.get('total_revenue', 0) for c in clients)
    
    print(f"\n📊 Client Statistics:")
    print("=" * 40)
    print(f"Total Clients:  {len(clients)}")
    print(f"Active:         {active} 🟢")
    print(f"Inactive:       {inactive} 🔴")
    print(f"Total Revenue:  ${total_revenue:.2f}")
    
    if clients:
        avg_revenue = total_revenue / len(clients)
        print(f"Avg per Client: ${avg_revenue:.2f}")


def main():
    parser = argparse.ArgumentParser(
        description="Client Manager Agent - Manage your freelance clients",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s add "John Doe" john@example.com --company "Acme Inc"
  %(prog)s list
  %(prog)s list --status active
  %(prog)s show 1
  %(prog)s update 1 --name "John Smith" --status active
  %(prog)s interact 1 email "Sent follow-up about project"
  %(prog)s project 1 "Website Redesign"
  %(prog)s revenue 1 500.00
  %(prog)s stats
  %(prog)s delete 1
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add client
    add_parser = subparsers.add_parser('add', help='Add a new client')
    add_parser.add_argument('name', help='Client name')
    add_parser.add_argument('email', help='Client email')
    add_parser.add_argument('--phone', '-p', help='Phone number')
    add_parser.add_argument('--company', '-c', help='Company name')
    add_parser.add_argument('--notes', '-n', help='Additional notes')
    
    # List clients
    list_parser = subparsers.add_parser('list', help='List all clients')
    list_parser.add_argument('--status', '-s', choices=['active', 'inactive'], 
                            help='Filter by status')
    
    # Show client
    show_parser = subparsers.add_parser('show', help='Show client details')
    show_parser.add_argument('client_id', type=int, help='Client ID')
    
    # Update client
    update_parser = subparsers.add_parser('update', help='Update client')
    update_parser.add_argument('client_id', type=int, help='Client ID')
    update_parser.add_argument('--name', help='New name')
    update_parser.add_argument('--email', help='New email')
    update_parser.add_argument('--phone', help='New phone')
    update_parser.add_argument('--company', help='New company')
    update_parser.add_argument('--notes', help='New notes')
    update_parser.add_argument('--status', choices=['active', 'inactive'], help='Status')
    
    # Delete client (soft delete)
    delete_parser = subparsers.add_parser('delete', help='Deactivate a client')
    delete_parser.add_argument('client_id', type=int, help='Client ID')
    
    # Add interaction
    interact_parser = subparsers.add_parser('interact', help='Add client interaction')
    interact_parser.add_argument('client_id', type=int, help='Client ID')
    interact_parser.add_argument('type', choices=['email', 'call', 'meeting', 'note'],
                                help='Interaction type')
    interact_parser.add_argument('note', help='Interaction note')
    
    # Link project
    project_parser = subparsers.add_parser('project', help='Link project to client')
    project_parser.add_argument('client_id', type=int, help='Client ID')
    project_parser.add_argument('name', help='Project name')
    
    # Update revenue
    revenue_parser = subparsers.add_parser('revenue', help='Add to client revenue')
    revenue_parser.add_argument('client_id', type=int, help='Client ID')
    revenue_parser.add_argument('amount', type=float, help='Amount to add')
    
    # Stats
    subparsers.add_parser('stats', help='Show client statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'add':
            add_client(args.name, args.email, args.phone, args.company, args.notes)
        elif args.command == 'list':
            list_clients(args.status)
        elif args.command == 'show':
            show_client(args.client_id)
        elif args.command == 'update':
            kwargs = {k: v for k, v in vars(args).items() 
                     if k not in ['command', 'client_id'] and v is not None}
            if kwargs:
                update_client(args.client_id, **kwargs)
            else:
                print("❌ No updates specified. Use --name, --email, etc.")
        elif args.command == 'delete':
            delete_client(args.client_id)
        elif args.command == 'interact':
            add_interaction(args.client_id, args.type, args.note)
        elif args.command == 'project':
            link_project(args.client_id, args.name)
        elif args.command == 'revenue':
            update_revenue(args.client_id, args.amount)
        elif args.command == 'stats':
            get_stats()
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
