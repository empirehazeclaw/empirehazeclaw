#!/usr/bin/env python3
"""
Email Scheduler Agent - EmpireHazeClaw
Schedules and manages email campaigns with timing control.
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
try:
    from croniter import croniter
    CRONITER_AVAILABLE = True
except ImportError:
    CRONITER_AVAILABLE = False
    croniter = None

# Paths
BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "emails"
LOGS_DIR = BASE_DIR / "logs"
SCHEDULE_FILE = DATA_DIR / "email_schedule.json"
QUEUE_FILE = DATA_DIR / "email_queue.json"
LOG_FILE = LOGS_DIR / "email_scheduler.log"

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
logger = logging.getLogger("EmailScheduler")


def load_schedule():
    """Load scheduled emails from JSON file."""
    if SCHEDULE_FILE.exists():
        try:
            with open(SCHEDULE_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"schedules": {}, "sequences": {}}
    return {"schedules": {}, "sequences": {}}


def save_schedule(data):
    """Save scheduled emails to JSON file."""
    with open(SCHEDULE_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def load_queue():
    """Load email queue from JSON file."""
    if QUEUE_FILE.exists():
        try:
            with open(QUEUE_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"queue": [], "history": []}
    return {"queue": [], "history": []}


def save_queue(data):
    """Save email queue to JSON file."""
    with open(QUEUE_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def schedule_email(name, template, recipients, send_at, smtp_config=None, timezone="UTC"):
    """Schedule a single email or campaign."""
    data = load_schedule()
    
    # Parse send_at datetime
    if isinstance(send_at, str):
        try:
            # Try ISO format
            send_dt = datetime.fromisoformat(send_at.replace('Z', '+00:00'))
        except ValueError:
            # Try cron format
            if CRONITER_AVAILABLE and croniter.is_valid(send_at):
                iter = croniter(send_at, datetime.now())
                send_dt = iter.get_next(datetime)
            elif CRONITER_AVAILABLE:
                raise ValueError(f"Invalid send_at format: {send_at}")
            else:
                # Fallback to ISO without cron
                raise ValueError(f"Invalid ISO format (croniter not installed): {send_at}")
    
    schedule = {
        "name": name,
        "template": template,
        "recipients": recipients if isinstance(recipients, list) else [recipients],
        "smtp_config": smtp_config,
        "send_at": send_dt.isoformat(),
        "timezone": timezone,
        "status": "scheduled",
        "created_at": datetime.now().isoformat(),
        "sent_count": 0,
        "failed_count": 0,
        "type": "single"
    }
    
    data["schedules"][name] = schedule
    save_schedule(data)
    logger.info(f"Scheduled email: {name} for {send_dt}")
    return schedule


def schedule_sequence(name, template, recipients, interval_hours=24, smtp_config=None, start_date=None):
    """Schedule an email sequence (drip campaign)."""
    data = load_schedule()
    
    if start_date is None:
        start_date = datetime.now().isoformat()
    
    sequence = {
        "name": name,
        "template": template,
        "recipients": recipients if isinstance(recipients, list) else [recipients],
        "smtp_config": smtp_config,
        "interval_hours": interval_hours,
        "start_date": start_date,
        "status": "scheduled",
        "created_at": datetime.now().isoformat(),
        "sent_count": 0,
        "failed_count": 0,
        "type": "sequence"
    }
    
    data["sequences"][name] = sequence
    save_schedule(data)
    logger.info(f"Scheduled sequence: {name} with interval {interval_hours}h")
    return sequence


def cancel_scheduled(name):
    """Cancel a scheduled email or sequence."""
    data = load_schedule()
    
    if name in data["schedules"]:
        data["schedules"][name]["status"] = "cancelled"
        save_schedule(data)
        logger.info(f"Cancelled schedule: {name}")
        return True
    
    if name in data["sequences"]:
        data["sequences"][name]["status"] = "cancelled"
        save_schedule(data)
        logger.info(f"Cancelled sequence: {name}")
        return True
    
    return False


def add_to_queue(campaign_name, recipient, subject, body, smtp_config=None, priority=5):
    """Add an email to the sending queue."""
    queue_data = load_queue()
    
    item = {
        "id": f"{campaign_name}_{recipient}_{int(time.time())}",
        "campaign": campaign_name,
        "recipient": recipient,
        "subject": subject,
        "body": body,
        "smtp_config": smtp_config,
        "priority": priority,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "attempts": 0
    }
    
    queue_data["queue"].append(item)
    queue_data["queue"].sort(key=lambda x: x["priority"], reverse=True)
    save_queue(queue_data)
    
    return item


def get_queue():
    """Get current email queue."""
    queue_data = load_queue()
    return queue_data.get("queue", [])


def process_queue(limit=10):
    """Process pending emails from queue (returns items to send)."""
    queue_data = load_queue()
    
    pending = [item for item in queue_data["queue"] if item["status"] == "pending"]
    to_process = pending[:limit]
    
    for item in to_process:
        item["status"] = "processing"
        item["started_at"] = datetime.now().isoformat()
    
    save_queue(queue_data)
    return to_process


def mark_sent(queue_id):
    """Mark a queued email as sent."""
    queue_data = load_queue()
    
    for item in queue_data["queue"]:
        if item["id"] == queue_id:
            item["status"] = "sent"
            item["sent_at"] = datetime.now().isoformat()
            
            # Add to history
            queue_data.setdefault("history", []).append({
                "id": item["id"],
                "recipient": item["recipient"],
                "campaign": item["campaign"],
                "sent_at": item["sent_at"]
            })
            
            # Update campaign stats
            data = load_schedule()
            if item["campaign"] in data["schedules"]:
                data["schedules"][item["campaign"]]["sent_count"] += 1
            if item["campaign"] in data["sequences"]:
                data["sequences"][item["campaign"]]["sent_count"] += 1
            save_schedule(data)
            
            break
    
    # Remove from queue
    queue_data["queue"] = [item for item in queue_data["queue"] if item["id"] != queue_id]
    save_queue(queue_data)


def mark_failed(queue_id, error):
    """Mark a queued email as failed."""
    queue_data = load_queue()
    
    for item in queue_data["queue"]:
        if item["id"] == queue_id:
            item["attempts"] += 1
            if item["attempts"] >= 3:
                item["status"] = "failed"
                item["error"] = error
            else:
                item["status"] = "pending"  # Retry
            break
    
    save_queue(queue_data)


def list_schedules(status=None):
    """List all scheduled emails and sequences."""
    data = load_schedule()
    
    results = {"schedules": {}, "sequences": {}}
    
    if status:
        results["schedules"] = {k: v for k, v in data.get("schedules", {}).items() 
                                if v.get("status") == status}
        results["sequences"] = {k: v for k, v in data.get("sequences", {}).items() 
                                if v.get("status") == status}
    else:
        results["schedules"] = data.get("schedules", {})
        results["sequences"] = data.get("sequences", {})
    
    return results


def get_next_send():
    """Get the next scheduled email to be sent."""
    data = load_schedule()
    upcoming = []
    
    now = datetime.now()
    
    for name, sched in data.get("schedules", {}).items():
        if sched.get("status") == "scheduled":
            send_at = datetime.fromisoformat(sched["send_at"])
            upcoming.append({
                "name": name,
                "type": "single",
                "send_at": send_at,
                "recipients_count": len(sched.get("recipients", []))
            })
    
    for name, seq in data.get("sequences", {}).items():
        if seq.get("status") == "scheduled":
            start_date = datetime.fromisoformat(seq["start_date"])
            upcoming.append({
                "name": name,
                "type": "sequence",
                "start_date": start_date,
                "interval_hours": seq.get("interval_hours", 24),
                "recipients_count": len(seq.get("recipients", []))
            })
    
    # Sort by send time
    upcoming.sort(key=lambda x: x.get("send_at") or x.get("start_date"))
    
    return upcoming


def main():
    parser = argparse.ArgumentParser(
        description="Email Scheduler Agent - Schedule and manage email campaigns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Schedule a single email
  %(prog)s schedule --name launch --template welcome --recipients file:contacts.txt --at "2026-03-28T10:00"
  
  # Schedule a drip sequence (emails every 24 hours)
  %(prog)s sequence --name nurture --template followup --recipients leads.json --interval 24
  
  # List all scheduled emails
  %(prog)s list
  
  # List upcoming sends
  %(prog)s upcoming
  
  # Cancel a scheduled email
  %(prog)s cancel --name launch
  
  # Show queue status
  %(prog)s queue
  
  # Add email to queue manually
  %(prog)s enqueue --campaign test --recipient user@example.com --subject "Hello" --body "Message"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Schedule command
    sched_parser = subparsers.add_parser('schedule', help='Schedule a single email')
    sched_parser.add_argument('--name', required=True, help='Schedule name')
    sched_parser.add_argument('--template', required=True, help='Template name to use')
    sched_parser.add_argument('--recipients', required=True, help='Recipients (email or @file)')
    sched_parser.add_argument('--at', required=True, help='Send time (ISO format or cron)')
    sched_parser.add_argument('--smtp', help='SMTP config name')
    sched_parser.add_argument('--timezone', default='UTC', help='Timezone')
    
    # Sequence command
    seq_parser = subparsers.add_parser('sequence', help='Schedule email sequence (drip)')
    seq_parser.add_argument('--name', required=True, help='Sequence name')
    seq_parser.add_argument('--template', required=True, help='Template name')
    seq_parser.add_argument('--recipients', required=True, help='Recipients file or email')
    seq_parser.add_argument('--interval', type=int, default=24, help='Hours between emails')
    seq_parser.add_argument('--smtp', help='SMTP config name')
    seq_parser.add_argument('--start', help='Start date (ISO format)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List scheduled emails')
    list_parser.add_argument('--status', choices=['scheduled', 'sent', 'cancelled'], help='Filter by status')
    
    # Upcoming command
    subparsers.add_parser('upcoming', help='Show upcoming scheduled emails')
    
    # Cancel command
    cancel_parser = subparsers.add_parser('cancel', help='Cancel scheduled email')
    cancel_parser.add_argument('--name', required=True, help='Name of schedule to cancel')
    
    # Queue commands
    queue_parser = subparsers.add_parser('queue', help='Show email queue')
    queue_parser.add_argument('--status', choices=['pending', 'processing', 'sent', 'failed'])
    
    # Enqueue command
    enqueue_parser = subparsers.add_parser('enqueue', help='Add email to queue')
    enqueue_parser.add_argument('--campaign', required=True, help='Campaign name')
    enqueue_parser.add_argument('--recipient', required=True, help='Recipient email')
    enqueue_parser.add_argument('--subject', required=True, help='Email subject')
    enqueue_parser.add_argument('--body', required=True, help='Email body')
    enqueue_parser.add_argument('--smtp', help='SMTP config')
    enqueue_parser.add_argument('--priority', type=int, default=5, help='Priority (1-10)')
    
    # Process command (for cron/scheduler)
    subparsers.add_parser('process', help='Process queue (for automated runs)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        if args.command == 'schedule':
            # Parse recipients
            recipients = args.recipients
            if recipients.startswith('file:'):
                with open(recipients[5:], 'r') as f:
                    recipients = [line.strip() for line in f if '@' in line]
            elif ',' in recipients:
                recipients = [r.strip() for r in recipients.split(',')]
            else:
                recipients = [recipients]
            
            schedule = schedule_email(
                args.name, args.template, recipients,
                args.at, args.smtp, args.timezone
            )
            print(f"✅ Scheduled email '{args.name}' for {schedule['send_at']}")
            print(f"   Recipients: {len(recipients)}")
            return 0
        
        elif args.command == 'sequence':
            recipients = args.recipients
            if recipients.startswith('file:'):
                with open(recipients[5:], 'r') as f:
                    recipients = [line.strip() for line in f if '@' in line]
            elif ',' in recipients:
                recipients = [r.strip() for r in recipients.split(',')]
            else:
                recipients = [recipients]
            
            sequence = schedule_sequence(
                args.name, args.template, recipients,
                args.interval, args.smtp, args.start
            )
            print(f"✅ Scheduled sequence '{args.name}'")
            print(f"   Interval: every {sequence['interval_hours']} hours")
            print(f"   Recipients: {len(recipients)}")
            return 0
        
        elif args.command == 'list':
            results = list_schedules(args.status)
            
            print(f"\n📅 Scheduled Emails & Sequences:")
            print("=" * 60)
            
            if results["schedules"]:
                print(f"\n📧 Single Emails ({len(results['schedules'])}):")
                for name, sched in results["schedules"].items():
                    status_icon = {"scheduled": "⏰", "sent": "✅", "cancelled": "❌"}.get(sched.get("status"), "?")
                    print(f"   {status_icon} [{name}]")
                    print(f"       Template: {sched['template']}")
                    print(f"       Send at: {sched['send_at']}")
                    print(f"       Recipients: {len(sched.get('recipients', []))}")
            
            if results["sequences"]:
                print(f"\n📋 Sequences ({len(results['sequences'])}):")
                for name, seq in results["sequences"].items():
                    status_icon = {"scheduled": "⏰", "sent": "✅", "cancelled": "❌"}.get(seq.get("status"), "?")
                    print(f"   {status_icon} [{name}]")
                    print(f"       Template: {seq['template']}")
                    print(f"       Interval: {seq['interval_hours']}h")
                    print(f"       Start: {seq['start_date']}")
            return 0
        
        elif args.command == 'upcoming':
            upcoming = get_next_send()
            
            if not upcoming:
                print("No upcoming scheduled emails.")
                return 0
            
            print(f"\n⏰ Upcoming Emails ({len(upcoming)}):")
            print("-" * 60)
            
            for item in upcoming[:10]:
                send_time = item.get("send_at") or item.get("start_date")
                print(f"   [{item['name']}] ({item['type']})")
                print(f"       Time: {send_time}")
                print(f"       Recipients: {item['recipients_count']}")
                if item.get('interval_hours'):
                    print(f"       Interval: {item['interval_hours']}h")
            return 0
        
        elif args.command == 'cancel':
            if cancel_scheduled(args.name):
                print(f"✅ Cancelled '{args.name}'")
                return 0
            else:
                print(f"❌ Schedule '{args.name}' not found")
                return 1
        
        elif args.command == 'queue':
            queue = get_queue()
            
            if args.status:
                queue = [item for item in queue if item.get("status") == args.status]
            
            if not queue:
                print("Queue is empty.")
                return 0
            
            print(f"\n📬 Email Queue ({len(queue)} items):")
            for item in queue[:20]:
                status_icon = {
                    "pending": "⏳",
                    "processing": "🔄",
                    "sent": "✅",
                    "failed": "❌"
                }.get(item.get("status"), "?")
                
                print(f"   {status_icon} [{item['campaign']}] -> {item['recipient']}")
                print(f"       Subject: {item['subject'][:40]}...")
                print(f"       Priority: {item['priority']} | Attempts: {item.get('attempts', 0)}")
            return 0
        
        elif args.command == 'enqueue':
            item = add_to_queue(args.campaign, args.recipient, args.subject, args.body, args.smtp, args.priority)
            print(f"✅ Added to queue: {item['id']}")
            print(f"   Recipient: {args.recipient}")
            print(f"   Priority: {args.priority}")
            return 0
        
        elif args.command == 'process':
            items = process_queue(limit=10)
            if items:
                print(f"📤 Processing {len(items)} queued emails...")
                for item in items:
                    print(f"   → {item['recipient']}: {item['subject'][:30]}...")
                return 0
            else:
                print("📭 Queue is empty")
                return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
