#!/usr/bin/env python3
"""
Voicemail Agent
==============
Manage voicemails: log, transcribe, summarize, and respond.

Usage:
    python3 voicemail_agent_agent.py --log --from-name <name> --from-number <phone> --message <text>
    python3 voicemail_agent_agent.py --list
    python3 voicemail_agent_agent.py --view <id>
    python3 voicemail_agent_agent.py --respond --id <id> --response <text>
    python3 voicemail_agent_agent.py --transcribe --id <id>
"""

import argparse
import json
import logging
import os
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
        logging.FileHandler(LOG_DIR / "voicemail_agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Data paths
DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data/agents/voice")
DATA_DIR.mkdir(parents=True, exist_ok=True)
VOICEMAILS_FILE = DATA_DIR / "voicemails.json"
RESPONSES_FILE = DATA_DIR / "voicemail_responses.json"
TEMPLATES_FILE = DATA_DIR / "voicemail_templates.json"


def load_json(filepath: Path, default: dict = {}) -> dict:
    """Load JSON data from file."""
    try:
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return default
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
        return default


def save_json(filepath: Path, data: dict) -> bool:
    """Save JSON data to file."""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        logger.error(f"Error saving {filepath}: {e}")
        return False


def initialize_data():
    """Initialize data files."""
    if not VOICEMAILS_FILE.exists():
        save_json(VOICEMAILS_FILE, {"voicemails": []})
        logger.info("Initialized voicemails data")
    
    if not RESPONSES_FILE.exists():
        save_json(RESPONSES_FILE, {"responses": []})
        logger.info("Initialized responses data")
    
    if not TEMPLATES_FILE.exists():
        templates = {
            "templates": [
                {
                    "id": "tmpl-001",
                    "name": "General Callback",
                    "text": "Hi, this is a callback regarding your recent message. Please call us back at your convenience.",
                    "active": True
                },
                {
                    "id": "tmpl-002",
                    "name": "Urgent Response",
                    "text": "Hi, this is an urgent callback. Please contact us immediately at your earliest convenience.",
                    "active": True
                },
                {
                    "id": "tmpl-003",
                    "name": "Thank You",
                    "text": "Hi, thank you for your message. We have received it and will follow up shortly.",
                    "active": True
                },
                {
                    "id": "tmpl-004",
                    "name": "Appointment Confirmation",
                    "text": "Hi, this is to confirm your upcoming appointment. We look forward to seeing you.",
                    "active": True
                }
            ],
            "last_updated": datetime.now().isoformat()
        }
        save_json(TEMPLATES_FILE, templates)
        logger.info("Initialized voicemail templates")


def get_next_voicemail_id() -> str:
    """Get next voicemail ID."""
    voicemails = load_json(VOICEMAILS_FILE)
    existing = voicemails.get("voicemails", [])
    
    if not existing:
        return "VM-001"
    
    max_id = 0
    for v in existing:
        try:
            num = int(v["id"].split("-")[1])
            if num > max_id:
                max_id = num
        except:
            pass
    
    return f"VM-{max_id + 1:03d}"


def log_voicemail(caller_name: str, caller_number: str, message: str,
                  priority: str = "normal", tags: Optional[List[str]] = None) -> Dict:
    """Log a new voicemail."""
    voicemails = load_json(VOICEMAILS_FILE)
    
    vm_id = get_next_voicemail_id()
    
    voicemail = {
        "id": vm_id,
        "caller_name": caller_name,
        "caller_number": caller_number,
        "message": message,
        "priority": priority,
        "tags": tags or [],
        "status": "new",
        "transcribed": False,
        "transcript": None,
        "responded": False,
        "response_id": None,
        "logged_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(days=30)).isoformat()
    }
    
    voicemails["voicemails"].append(voicemail)
    voicemails["last_updated"] = datetime.now().isoformat()
    
    save_json(VOICEMAILS_FILE, voicemails)
    
    logger.info(f"Logged voicemail {vm_id} from {caller_name}")
    return voicemail


def update_voicemail_status(vm_id: str, status: str) -> bool:
    """Update voicemail status."""
    voicemails = load_json(VOICEMAILS_FILE)
    
    for vm in voicemails.get("voicemails", []):
        if vm["id"] == vm_id:
            old_status = vm["status"]
            vm["status"] = status
            voicemails["last_updated"] = datetime.now().isoformat()
            save_json(VOICEMAILS_FILE, voicemails)
            logger.info(f"Updated voicemail {vm_id}: {old_status} -> {status}")
            return True
    
    return False


def add_response(vm_id: str, response_text: str, response_type: str = "callback") -> Dict:
    """Add a response to a voicemail."""
    responses = load_json(RESPONSES_FILE)
    voicemails = load_json(VOICEMAILS_FILE)
    
    response_id = f"RSP-{len(responses.get('responses', [])) + 1:03d}"
    
    response = {
        "id": response_id,
        "voicemail_id": vm_id,
        "response_text": response_text,
        "response_type": response_type,
        "created_at": datetime.now().isoformat()
    }
    
    responses["responses"].append(response)
    responses["last_updated"] = datetime.now().isoformat()
    
    # Update voicemail
    for vm in voicemails.get("voicemails", []):
        if vm["id"] == vm_id:
            vm["responded"] = True
            vm["response_id"] = response_id
            vm["status"] = "responded"
            break
    
    save_json(RESPONSES_FILE, responses)
    save_json(VOICEMAILS_FILE, voicemails)
    
    logger.info(f"Added response {response_id} to voicemail {vm_id}")
    return response


def list_voicemails(status_filter: Optional[str] = None, 
                    priority_filter: Optional[str] = None) -> List[Dict]:
    """List voicemails with optional filters."""
    voicemails = load_json(VOICEMAILS_FILE)
    result = voicemails.get("voicemails", [])
    
    if status_filter:
        result = [v for v in result if v["status"] == status_filter]
    
    if priority_filter:
        result = [v for v in result if v["priority"] == priority_filter]
    
    # Sort by priority then by date
    priority_order = {"urgent": 0, "high": 1, "normal": 2, "low": 3}
    result.sort(key=lambda x: (priority_order.get(x["priority"], 2), x["logged_at"]), reverse=True)
    
    return result


def get_voicemail(vm_id: str) -> Optional[Dict]:
    """Get a specific voicemail by ID."""
    voicemails = load_json(VOICEMAILS_FILE)
    
    for vm in voicemails.get("voicemails", []):
        if vm["id"] == vm_id:
            return vm
    
    return None


def get_response(response_id: str) -> Optional[Dict]:
    """Get a response by ID."""
    responses = load_json(RESPONSES_FILE)
    
    for r in responses.get("responses", []):
        if r["id"] == response_id:
            return r
    
    return None


def get_templates() -> List[Dict]:
    """Get all active templates."""
    templates = load_json(TEMPLATES_FILE)
    return [t for t in templates.get("templates", []) if t.get("active", True)]


def display_voicemail(vm: Dict):
    """Display a voicemail nicely."""
    status_emoji = {
        "new": "📩",
        "in_progress": "🔄",
        "responded": "✅",
        "archived": "📁"
    }
    priority_emoji = {
        "urgent": "🔴",
        "high": "🟠",
        "normal": "🟡",
        "low": "⚪"
    }
    
    emoji = status_emoji.get(vm["status"], "❓")
    priority = priority_emoji.get(vm["priority"], "⚪")
    
    print("\n" + "=" * 70)
    print(f"{emoji} VOICEMAIL: {vm['id']} {priority} {vm['priority'].upper()}")
    print("=" * 70)
    print(f"  From:       {vm['caller_name']}")
    print(f"  Number:     {vm['caller_number']}")
    print(f"  Status:     {vm['status'].upper().replace('_', ' ')}")
    print(f"  Logged:     {vm['logged_at'][:19].replace('T', ' ')}")
    print(f"  Expires:    {vm['expires_at'][:10]}")
    
    if vm.get("tags"):
        print(f"  Tags:       {', '.join(vm['tags'])}")
    
    print()
    print("-" * 70)
    print("MESSAGE:")
    print("-" * 70)
    print(f"  {vm['message']}")
    print("-" * 70)
    
    if vm.get("transcribed") and vm.get("transcript"):
        print()
        print("📝 TRANSCRIPT:")
        print(f"  {vm['transcript']}")
    
    if vm.get("responded"):
        print()
        print("✅ RESPONDED:")
        response = get_response(vm["response_id"])
        if response:
            print(f"  [{response['created_at'][:19].replace('T', ' ')}]")
            print(f"  {response['response_text']}")
    
    print("=" * 70)


def display_voicemails(voicemails: List[Dict]):
    """Display a list of voicemails."""
    if not voicemails:
        print("\nNo voicemails found.")
        return
    
    print("\n" + "=" * 80)
    print("📩 VOICEMAILS")
    print("=" * 80)
    
    status_emoji = {"new": "📩", "in_progress": "🔄", "responded": "✅", "archived": "📁"}
    priority_emoji = {"urgent": "🔴", "high": "🟠", "normal": "🟡", "low": "⚪"}
    
    for vm in voicemails:
        status = status_emoji.get(vm["status"], "❓")
        priority = priority_emoji.get(vm["priority"], "⚪")
        
        msg_preview = vm["message"][:40] + "..." if len(vm["message"]) > 40 else vm["message"]
        responded = "✅" if vm.get("responded") else "⏳"
        
        print(f"{status} {vm['id']} | {priority} {vm['priority']:7} | {responded} | "
              f"{vm['caller_name'][:15]:15} | {msg_preview}")
    
    print("=" * 80)
    print(f"Total: {len(voicemails)} voicemails")


def main():
    valid_statuses = ["new", "in_progress", "responded", "archived"]
    valid_priorities = ["urgent", "high", "normal", "low"]
    
    parser = argparse.ArgumentParser(
        description="Voicemail Agent - Manage voicemails: log, transcribe, summarize, and respond",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --log --from-name "John Doe" --from-number "+1234567890" --message "Call me back"
  %(prog)s --log --from-name "Jane" --from-number "+1987654321" --message "Urgent issue" --priority urgent
  %(prog)s --list
  %(prog)s --list --status new --priority urgent
  %(prog)s --view VM-001
  %(prog)s --respond --id VM-001 --response "I will call you back shortly"
  %(prog)s --templates
  %(prog)s --init
        """
    )
    
    parser.add_argument("--log", action="store_true", help="Log a new voicemail")
    parser.add_argument("--from-name", dest="from_name", type=str, help="Caller name")
    parser.add_argument("--from-number", dest="from_number", type=str, help="Caller phone number")
    parser.add_argument("--message", type=str, help="Voicemail message")
    parser.add_argument("--priority", type=str, choices=valid_priorities, default="normal", help="Priority level")
    parser.add_argument("--tags", type=str, nargs="+", help="Tags for the voicemail")
    parser.add_argument("--list", action="store_true", help="List all voicemails")
    parser.add_argument("--status", type=str, choices=valid_statuses, help="Filter by status")
    parser.add_argument("--priority-filter", dest="priority_filter", type=str, choices=valid_priorities, help="Filter by priority")
    parser.add_argument("--view", type=str, help="View a specific voicemail by ID")
    parser.add_argument("--respond", action="store_true", help="Add a response to a voicemail")
    parser.add_argument("--id", type=str, help="Voicemail ID for response/view")
    parser.add_argument("--response", type=str, help="Response text")
    parser.add_argument("--response-type", dest="response_type", type=str, 
                        choices=["callback", "sms", "email"], default="callback", help="Response type")
    parser.add_argument("--templates", action="store_true", help="List response templates")
    parser.add_argument("--init", action="store_true", help="Initialize sample data")
    
    args = parser.parse_args()
    
    try:
        initialize_data()
        
        if args.init:
            print("✅ Sample data initialized")
            return
        
        if args.log:
            if not args.from_name or not args.from_number or not args.message:
                parser.error("--log requires --from-name, --from-number, and --message")
            
            voicemail = log_voicemail(
                args.from_name, 
                args.from_number, 
                args.message,
                args.priority,
                args.tags
            )
            print(f"\n✅ Voicemail logged: {voicemail['id']}")
            display_voicemail(voicemail)
            return
        
        if args.list:
            voicemails = list_voicemails(args.status, args.priority_filter)
            display_voicemails(voicemails)
            return
        
        if args.view:
            vm = get_voicemail(args.view)
            if vm:
                display_voicemail(vm)
            else:
                print(f"\n❌ Voicemail not found: {args.view}")
                sys.exit(1)
            return
        
        if args.respond:
            if not args.id or not args.response:
                parser.error("--respond requires --id and --response")
            
            vm = get_voicemail(args.id)
            if not vm:
                print(f"\n❌ Voicemail not found: {args.id}")
                sys.exit(1)
            
            response = add_response(args.id, args.response, args.response_type)
            print(f"\n✅ Response added: {response['id']}")
            
            # Show updated voicemail
            vm = get_voicemail(args.id)
            display_voicemail(vm)
            return
        
        if args.templates:
            templates = get_templates()
            print("\n📋 RESPONSE TEMPLATES:")
            print("-" * 60)
            for t in templates:
                print(f"  {t['id']}: {t['name']}")
                print(f"    {t['text'][:70]}...")
                print()
            return
        
        parser.print_help()
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Error: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
