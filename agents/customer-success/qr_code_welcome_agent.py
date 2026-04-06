#!/usr/bin/env python3
"""
QR Code Welcome Agent
=====================
Manages new customer onboarding via QR codes. Creates welcome sequences,
tracks onboarding progress, and sends welcome messages.
"""

import argparse
import json
import sys
import logging
import uuid
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Setup logging FIRST
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - QR-WELCOME - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "qr_welcome.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# QR code import (optional)
try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    logger.warning("qrcode module not installed. QR generation disabled. Install with: pip install qrcode pillow")

# Data paths
DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data/customer-success")
DATA_DIR.mkdir(parents=True, exist_ok=True)
CUSTOMERS_FILE = DATA_DIR / "welcome_customers.json"
WELCOME_SEQUENCES_FILE = DATA_DIR / "welcome_sequences.json"
QR_CODES_FILE = DATA_DIR / "qr_codes.json"
QR_OUTPUT_DIR = DATA_DIR / "qr_codes"


def load_json(filepath: Path, default: dict = None) -> dict:
    """Load JSON file or return default."""
    if default is None:
        default = {}
    try:
        if filepath.exists():
            return json.loads(filepath.read_text())
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
    return default


def save_json(filepath: Path, data: dict) -> bool:
    """Save data to JSON file."""
    try:
        filepath.write_text(json.dumps(data, indent=2, default=str))
        return True
    except Exception as e:
        logger.error(f"Error saving {filepath}: {e}")
        return False


def init_data_files():
    """Initialize data files if they don't exist."""
    QR_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    if not CUSTOMERS_FILE.exists():
        save_json(CUSTOMERS_FILE, {"customers": []})
    
    if not WELCOME_SEQUENCES_FILE.exists():
        save_json(WELCOME_SEQUENCES_FILE, {
            "sequences": [
                {
                    "id": "default",
                    "name": "Default Welcome",
                    "steps": [
                        {"order": 1, "type": "email", "subject": "Welcome!", "delay_hours": 0},
                        {"order": 2, "type": "gift", "description": "10% discount code", "delay_hours": 24},
                        {"order": 3, "type": "followup", "subject": "How can we help?", "delay_hours": 72}
                    ],
                    "created_at": datetime.now().isoformat()
                }
            ]
        })
    
    if not QR_CODES_FILE.exists():
        save_json(QR_CODES_FILE, {"qr_codes": []})


def generate_qr_code(data: str, output_path: Path, name: str) -> bool:
    """Generate a QR code image."""
    if not QRCODE_AVAILABLE:
        logger.error("qrcode module not available")
        return False
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output_path)
        
        logger.info(f"Generated QR code: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to generate QR code: {e}")
        return False


def cmd_dashboard(args) -> int:
    """Show welcome program dashboard."""
    logger.info("Showing welcome dashboard...")
    
    customers = load_json(CUSTOMERS_FILE)
    sequences = load_json(WELCOME_SEQUENCES_FILE)
    qr_codes = load_json(QR_CODES_FILE)
    
    all_customers = customers.get('customers', [])
    welcomed = len([c for c in all_customers if c.get('onboarding_complete', False)])
    pending = len([c for c in all_customers if not c.get('onboarding_complete', False)])
    
    # Calculate completion rate
    completion_rate = (welcomed / len(all_customers) * 100) if all_customers else 0
    
    print("\n" + "="*60)
    print("🎫 QR CODE WELCOME DASHBOARD")
    print("="*60)
    print(f"📅 Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("-"*60)
    
    print("\n👥 CUSTOMERS")
    print(f"   Total Onboarded: {len(all_customers)}")
    print(f"   Completed: {welcomed}")
    print(f"   Pending: {pending}")
    print(f"   Completion Rate: {completion_rate:.1f}%")
    
    print("\n📋 WELCOME SEQUENCES")
    print(f"   Total: {len(sequences.get('sequences', []))}")
    for seq in sequences.get('sequences', [])[:3]:
        print(f"      📋 {seq.get('name', 'Untitled')} ({len(seq.get('steps', []))} steps)")
    
    print("\n📱 QR CODES")
    print(f"   Total Generated: {len(qr_codes.get('qr_codes', []))}")
    
    # Recent signups
    if all_customers:
        recent = sorted(all_customers, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
        print("\n📅 RECENT SIGNUPS:")
        for c in recent:
            status = "✅" if c.get('onboarding_complete') else "⏳"
            print(f"   {status} {c.get('name', 'Unknown')} ({c.get('email', '?')})")
    
    print("\n" + "="*60)
    return 0


def cmd_generate_qr(args) -> int:
    """Generate a new QR code."""
    logger.info(f"Generating QR code: {args.name}")
    
    qr_codes = load_json(QR_CODES_FILE)
    
    # Create unique ID
    qr_id = str(uuid.uuid4())[:8]
    
    # Generate destination URL
    base_url = args.url.rstrip('/')
    destination = f"{base_url}?ref={qr_id}&welcome={args.sequence or 'default'}"
    
    # Generate filename
    filename = f"{args.name.replace(' ', '_').lower()}_{qr_id}.png"
    filepath = QR_OUTPUT_DIR / filename
    
    # Generate QR code
    if generate_qr_code(destination, filepath, args.name):
        qr_entry = {
            "id": qr_id,
            "name": args.name,
            "destination": destination,
            "sequence": args.sequence or "default",
            "filename": filename,
            "path": str(filepath),
            "created_at": datetime.now().isoformat(),
            "scans": 0,
            "usage": "new_customer"
        }
        
        qr_codes['qr_codes'].append(qr_entry)
        save_json(QR_CODES_FILE, qr_codes)
        
        print(f"✅ QR Code generated!")
        print(f"   ID: {qr_id}")
        print(f"   Name: {args.name}")
        print(f"   Destination: {destination}")
        print(f"   Saved to: {filepath}")
        return 0
    else:
        print(f"❌ Failed to generate QR code")
        return 1


def cmd_list_qr_codes(args) -> int:
    """List all QR codes."""
    logger.info("Listing QR codes...")
    
    qr_codes = load_json(QR_CODES_FILE)
    all_codes = qr_codes.get('qr_codes', [])
    
    if not all_codes:
        print("No QR codes generated yet.")
        return 0
    
    print(f"\n📱 QR Codes ({len(all_codes)}):")
    print("-"*70)
    for code in sorted(all_codes, key=lambda x: x.get('created_at', ''), reverse=True):
        print(f"   🆔 {code.get('id')} | {code.get('name', 'Untitled')}")
        print(f"      Sequence: {code.get('sequence', 'default')} | Scans: {code.get('scans', 0)}")
        print(f"      Created: {code.get('created_at', '')[:10]}")
    
    return 0


def cmd_register_customer(args) -> int:
    """Register a new customer from QR scan."""
    logger.info(f"Registering customer: {args.email}")
    
    customers = load_json(CUSTOMERS_FILE)
    sequences = load_json(WELCOME_SEQUENCES_FILE)
    
    # Check if customer already exists
    for c in customers.get('customers', []):
        if c.get('email') == args.email:
            print(f"⚠️  Customer {args.email} already registered.")
            print(f"   Onboarding: {'✅ Complete' if c.get('onboarding_complete') else '⏳ Pending'}")
            return 0
    
    # Get sequence steps
    sequence_id = args.sequence or "default"
    sequence = None
    for s in sequences.get('sequences', []):
        if s.get('id') == sequence_id:
            sequence = s
            break
    
    if not sequence:
        # Use default sequence
        for s in sequences.get('sequences', []):
            if s.get('id') == "default":
                sequence = s
                break
    
    customer = {
        "id": str(uuid.uuid4())[:8],
        "name": args.name or args.email.split('@')[0],
        "email": args.email,
        "qr_code_id": args.qr_ref,
        "sequence_id": sequence_id,
        "onboarding_complete": False,
        "welcome_sent": False,
        "steps_completed": [],
        "created_at": datetime.now().isoformat(),
        "source": args.source or "qr_code",
        "notes": args.notes or ""
    }
    
    customers['customers'].append(customer)
    save_json(CUSTOMERS_FILE, customers)
    
    # Update QR scan count
    if args.qr_ref:
        qr_codes = load_json(QR_CODES_FILE)
        for qr in qr_codes.get('qr_codes', []):
            if qr.get('id') == args.qr_ref:
                qr['scans'] = qr.get('scans', 0) + 1
                save_json(QR_CODES_FILE, qr_codes)
                break
    
    print(f"✅ Customer registered: {args.email}")
    print(f"   Welcome Sequence: {sequence_id}")
    print(f"   Next: Welcome email will be sent")
    
    return 0


def cmd_list_customers(args) -> int:
    """List customers with optional filters."""
    logger.info("Listing customers...")
    
    customers = load_json(CUSTOMERS_FILE)
    all_customers = customers.get('customers', [])
    
    if args.status == 'completed':
        all_customers = [c for c in all_customers if c.get('onboarding_complete', False)]
    elif args.status == 'pending':
        all_customers = [c for c in all_customers if not c.get('onboarding_complete', False)]
    
    if args.sequence:
        all_customers = [c for c in all_customers if c.get('sequence_id') == args.sequence]
    
    if not all_customers:
        print("No customers found.")
        return 0
    
    print(f"\n👥 Customers ({len(all_customers)}):")
    print("-"*70)
    for cust in sorted(all_customers, key=lambda x: x.get('created_at', ''), reverse=True):
        status = "✅" if cust.get('onboarding_complete') else "⏳"
        print(f"   {status} {cust.get('name', 'Unknown')} | {cust.get('email', '?')}")
        print(f"       Sequence: {cust.get('sequence_id', 'default')} | Source: {cust.get('source', '?')}")
    
    return 0


def cmd_complete_onboarding(args) -> int:
    """Mark a customer's onboarding as complete."""
    logger.info(f"Completing onboarding for customer: {args.customer_id}")
    
    customers = load_json(CUSTOMERS_FILE)
    
    for cust in customers.get('customers', []):
        if cust.get('id') == args.customer_id or cust.get('email') == args.customer_id:
            cust['onboarding_complete'] = True
            cust['completed_at'] = datetime.now().isoformat()
            
            # Mark all sequence steps as completed
            cust['steps_completed'] = ['welcome_email', 'discount_given', 'followup_sent']
            
            save_json(CUSTOMERS_FILE, customers)
            print(f"✅ Onboarding completed for {cust.get('name', cust.get('email', 'Unknown'))}!")
            return 0
    
    print(f"❌ Customer {args.customer_id} not found.")
    return 1


def cmd_create_sequence(args) -> int:
    """Create a new welcome sequence."""
    logger.info(f"Creating welcome sequence: {args.name}")
    
    sequences = load_json(WELCOME_SEQUENCES_FILE)
    
    seq_id = args.name.lower().replace(' ', '-')[:20]
    
    # Parse steps
    steps = []
    if args.steps:
        step_list = args.steps.split(',')
        for i, step in enumerate(step_list, 1):
            steps.append({
                "order": i,
                "type": step.strip(),
                "delay_hours": (i - 1) * 24
            })
    
    sequence = {
        "id": seq_id,
        "name": args.name,
        "description": args.description or "",
        "steps": steps,
        "created_at": datetime.now().isoformat()
    }
    
    sequences['sequences'].append(sequence)
    save_json(WELCOME_SEQUENCES_FILE, sequences)
    
    print(f"✅ Welcome sequence created: {args.name} (ID: {seq_id})")
    return 0


def cmd_list_sequences(args) -> int:
    """List all welcome sequences."""
    logger.info("Listing sequences...")
    
    sequences = load_json(WELCOME_SEQUENCES_FILE)
    all_seqs = sequences.get('sequences', [])
    
    if not all_seqs:
        print("No welcome sequences created.")
        return 0
    
    print(f"\n📋 Welcome Sequences ({len(all_seqs)}):")
    print("-"*70)
    for seq in all_seqs:
        print(f"   📋 {seq.get('name', 'Untitled')} (ID: {seq.get('id', '?')})")
        print(f"       Steps: {len(seq.get('steps', []))}")
        if seq.get('description'):
            print(f"       {seq.get('description')}")
    
    return 0


def cmd_stats(args) -> int:
    """Show onboarding statistics."""
    logger.info("Calculating onboarding stats...")
    
    customers = load_json(CUSTOMERS_FILE)
    qr_codes = load_json(QR_CODES_FILE)
    sequences = load_json(WELCOME_SEQUENCES_FILE)
    
    all_customers = customers.get('customers', [])
    all_qr = qr_codes.get('qr_codes', [])
    
    total_customers = len(all_customers)
    completed = len([c for c in all_customers if c.get('onboarding_complete', False)])
    pending = total_customers - completed
    
    total_scans = sum(q.get('scans', 0) for q in all_qr)
    conversion_rate = (total_customers / total_scans * 100) if total_scans > 0 else 0
    
    # Calculate average onboarding time
    onboarding_times = []
    for c in all_customers:
        if c.get('completed_at') and c.get('created_at'):
            created = datetime.fromisoformat(c['created_at'])
            completed_date = datetime.fromisoformat(c['completed_at'])
            hours = (completed_date - created).total_seconds() / 3600
            onboarding_times.append(hours)
    
    avg_onboarding = sum(onboarding_times) / len(onboarding_times) if onboarding_times else 0
    
    print("\n" + "="*60)
    print("📊 ONBOARDING STATISTICS")
    print("="*60)
    print(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("-"*60)
    
    print("\n👥 CUSTOMERS")
    print(f"   Total Registered: {total_customers}")
    print(f"   Completed: {completed} ({completed/total_customers*100:.1f}% if total > 0 else 0%)")
    print(f"   Pending: {pending}")
    print(f"   Avg Onboarding Time: {avg_onboarding:.1f} hours")
    
    print("\n📱 QR CODE PERFORMANCE")
    print(f"   Total QR Codes: {len(all_qr)}")
    print(f"   Total Scans: {total_scans}")
    print(f"   Scan-to-Register Rate: {conversion_rate:.1f}%")
    
    print("\n📋 SEQUENCES")
    print(f"   Total Sequences: {len(sequences.get('sequences', []))}")
    
    print("\n" + "="*60)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="🎫 QR Code Welcome Agent - Customer Onboarding",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s dashboard                    Show welcome program dashboard
  %(prog)s generate-qr --name "Shop" --url https://empirehazeclaw.com/welcome
  %(prog)s list-qr-codes
  %(prog)s register --email customer@example.com --name "John" --qr-ref abc123
  %(prog)s list-customers --status pending
  %(prog)s complete-onboarding --customer-id abc12345
  %(prog)s create-sequence --name "Premium" --steps "email,gift,followup"
  %(prog)s list-sequences
  %(prog)s stats                        Show onboarding statistics
        """
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Dashboard
    subparsers.add_parser('dashboard', help='Show welcome program dashboard')
    
    # QR code commands
    qr_parser = subparsers.add_parser('generate-qr', help='Generate a new QR code')
    qr_parser.add_argument('--name', required=True, help='QR code name')
    qr_parser.add_argument('--url', required=True, help='Destination URL')
    qr_parser.add_argument('--sequence', help='Welcome sequence ID')
    
    subparsers.add_parser('list-qr-codes', help='List all QR codes')
    
    # Customer commands
    reg_parser = subparsers.add_parser('register', help='Register a new customer')
    reg_parser.add_argument('--email', required=True, help='Customer email')
    reg_parser.add_argument('--name', help='Customer name')
    reg_parser.add_argument('--qr-ref', help='QR code reference ID')
    reg_parser.add_argument('--sequence', help='Welcome sequence ID')
    reg_parser.add_argument('--source', help='Customer source')
    reg_parser.add_argument('--notes', help='Notes')
    
    list_cust_parser = subparsers.add_parser('list-customers', help='List customers')
    list_cust_parser.add_argument('--status', choices=['pending', 'completed'])
    list_cust_parser.add_argument('--sequence', help='Filter by sequence ID')
    
    complete_parser = subparsers.add_parser('complete-onboarding', help='Mark onboarding complete')
    complete_parser.add_argument('--customer-id', required=True, help='Customer ID or email')
    
    # Sequence commands
    seq_parser = subparsers.add_parser('create-sequence', help='Create welcome sequence')
    seq_parser.add_argument('--name', required=True, help='Sequence name')
    seq_parser.add_argument('--description', help='Description')
    seq_parser.add_argument('--steps', help='Comma-separated step types')
    
    subparsers.add_parser('list-sequences', help='List all sequences')
    
    # Stats command
    subparsers.add_parser('stats', help='Show onboarding statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize data files
    init_data_files()
    
    # Route to command handler
    commands = {
        'dashboard': cmd_dashboard,
        'generate-qr': cmd_generate_qr,
        'list-qr-codes': cmd_list_qr_codes,
        'register': cmd_register_customer,
        'list-customers': cmd_list_customers,
        'complete-onboarding': cmd_complete_onboarding,
        'create-sequence': cmd_create_sequence,
        'list-sequences': cmd_list_sequences,
        'stats': cmd_stats
    }
    
    try:
        return commands[args.command](args)
    except Exception as e:
        logger.error(f"Command failed: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
