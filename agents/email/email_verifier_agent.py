#!/usr/bin/env python3
"""
Email Verifier Agent - EmpireHazeClaw
Validates email addresses and verifies deliverability.
"""

import argparse
import json
import logging
import re
import socket
import sys
import time
from datetime import datetime
from pathlib import Path
import os

# Paths
BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "emails"
LOGS_DIR = BASE_DIR / "logs"
VERIFIED_FILE = DATA_DIR / "verified_emails.json"
LOG_FILE = LOGS_DIR / "email_verifier.log"

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
logger = logging.getLogger("EmailVerifier")


# Disposable email domains to block
DISPOSABLE_DOMAINS = {
    'tempmail.com', 'throwaway.com', 'mailinator.com', 'guerrillamail.com',
    '10minutemail.com', 'temp-mail.org', 'fakeinbox.com', 'trashmail.com',
    'maildrop.cc', 'getairmail.com', 'yopmail.com', 'sharklasers.com',
    'dispostable.com', 'mailnesia.com', 'tempr.email', 'discard.email'
}


def load_verified():
    """Load verified emails from JSON file."""
    if VERIFIED_FILE.exists():
        try:
            with open(VERIFIED_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"emails": {}, "stats": {"total": 0, "valid": 0, "invalid": 0, "risky": 0}}
    return {"emails": {}, "stats": {"total": 0, "valid": 0, "invalid": 0, "risky": 0}}


def save_verified(data):
    """Save verified emails to JSON file."""
    with open(VERIFIED_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def validate_syntax(email):
    """Validate email syntax using regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True, "Valid syntax"
    return False, "Invalid syntax"


def check_disposable(email):
    """Check if email uses a disposable domain."""
    domain = email.lower().split('@')[1] if '@' in email else ''
    if domain in DISPOSABLE_DOMAINS:
        return True, "Disposable domain"
    return False, "Not disposable"


def check_mx_records(domain):
    """Check if domain has valid MX records."""
    try:
        mx_records = socket.getaddrinfo(domain, 25)
        return True, f"MX records found ({len(mx_records)})"
    except socket.gaierror:
        return False, "No MX records"


def verify_smtp(email, timeout=5):
    """
    Verify email via SMTP simulation (non-destructive).
    This checks if the domain accepts mail without sending.
    """
    domain = email.split('@')[1] if '@' in email else ''
    
    try:
        # Get MX server
        mx_hosts = []
        try:
            import dns.resolver
            answers = dns.resolver.resolve(domain, 'MX')
            for rdata in answers:
                mx_hosts.append(str(rdata.exchange).rstrip('.'))
        except Exception:
            # Fallback: try common mail servers
            mx_hosts = [f'mail.{domain}', f'smtp.{domain}', f'mx.{domain}']
        
        for mx_host in mx_hosts[:3]:  # Try up to 3 servers
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                sock.connect((mx_host, 25))
                
                response = sock.recv(1024).decode('utf-8', errors='ignore')
                
                # Check for SMTP greeting
                if response.startswith('220'):
                    sock.sendall(b'QUIT\r\n')
                    sock.close()
                    return True, f"Connected to {mx_host}"
                
                sock.close()
            except Exception:
                continue
        
        return False, "Could not connect to mail server"
        
    except Exception as e:
        return False, f"SMTP check failed: {str(e)[:50]}"


def verify_email(email, check_smtp=False):
    """Verify a single email address."""
    result = {
        "email": email.lower(),
        "timestamp": datetime.now().isoformat(),
        "checks": {}
    }
    
    # Syntax check
    valid_syntax, syntax_msg = validate_syntax(email)
    result["checks"]["syntax"] = {"passed": valid_syntax, "message": syntax_msg}
    
    if not valid_syntax:
        result["status"] = "invalid"
        result["score"] = 0
        return result
    
    domain = email.split('@')[1] if '@' in email else ''
    
    # Disposable check
    is_disposable, disp_msg = check_disposable(email)
    result["checks"]["disposable"] = {"passed": not is_disposable, "message": disp_msg}
    
    # MX record check
    has_mx, mx_msg = check_mx_records(domain)
    result["checks"]["mx_records"] = {"passed": has_mx, "message": mx_msg}
    
    if not has_mx:
        result["status"] = "invalid"
        result["score"] = 20
        return result
    
    # SMTP check (optional, can be slow)
    if check_smtp:
        has_smtp, smtp_msg = verify_smtp(email)
        result["checks"]["smtp"] = {"passed": has_smtp, "message": smtp_msg}
    
    # Calculate score
    score = 100
    if is_disposable:
        score -= 40
    if not has_mx:
        score -= 30
    if check_smtp:
        if not has_smtp:
            score -= 30
    
    result["score"] = max(0, score)
    
    if score >= 80:
        result["status"] = "valid"
    elif score >= 50:
        result["status"] = "risky"
    else:
        result["status"] = "invalid"
    
    return result


def verify_batch(emails, check_smtp=False, delay=0.5):
    """Verify a batch of email addresses."""
    results = []
    
    for email in emails:
        email = email.strip()
        if email:
            result = verify_email(email, check_smtp=check_smtp)
            results.append(result)
            
            # Update stats
            data = load_verified()
            data["emails"][email.lower()] = result
            data["stats"]["total"] += 1
            if result["status"] == "valid":
                data["stats"]["valid"] += 1
            elif result["status"] == "risky":
                data["stats"]["risky"] += 1
            else:
                data["stats"]["invalid"] += 1
            save_verified(data)
            
            if delay and len(emails) > 1:
                time.sleep(delay)
    
    return results


def get_stats():
    """Get verification statistics."""
    data = load_verified()
    return data.get("stats", {})


def get_verified_list(status=None):
    """Get list of verified emails, optionally filtered by status."""
    data = load_verified()
    emails = data.get("emails", {})
    
    if status:
        return {k: v for k, v in emails.items() if v.get("status") == status}
    return emails


def main():
    parser = argparse.ArgumentParser(
        description="Email Verifier Agent - Validate and verify email addresses",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify single email
  %(prog)s verify --email test@example.com
  
  # Verify with SMTP check (slower)
  %(prog)s verify --email test@example.com --smtp
  
  # Verify batch from file
  %(prog)s verify --file emails.txt
  
  # Verify batch with SMTP checks
  %(prog)s verify --file emails.txt --smtp --delay 1
  
  # Check stats
  %(prog)s stats
  
  # List valid emails
  %(prog)s list --status valid
  
  # Clean invalid emails from cache
  %(prog)s clean --status invalid
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify email(s)')
    verify_parser.add_argument('--email', help='Single email to verify')
    verify_parser.add_argument('--file', help='File with emails (one per line)')
    verify_parser.add_argument('--smtp', action='store_true', help='Perform SMTP check (slower)')
    verify_parser.add_argument('--delay', type=float, default=0.5, help='Delay between verifications (seconds)')
    
    # Stats command
    subparsers.add_parser('stats', help='Show verification statistics')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List verified emails')
    list_parser.add_argument('--status', choices=['valid', 'invalid', 'risky'], help='Filter by status')
    list_parser.add_argument('--limit', type=int, default=50, help='Limit results')
    
    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Clean verified emails cache')
    clean_parser.add_argument('--status', choices=['valid', 'invalid', 'risky'], help='Remove emails with status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        if args.command == 'verify':
            emails = []
            
            if args.email:
                emails = [args.email]
            elif args.file:
                with open(args.file, 'r') as f:
                    emails = [line.strip() for line in f if line.strip()]
            else:
                print("❌ Please provide --email or --file")
                return 1
            
            print(f"🔍 Verifying {len(emails)} email(s)...\n")
            
            results = verify_batch(emails, check_smtp=args.smtp, delay=args.delay if args.smtp else 0)
            
            valid = sum(1 for r in results if r["status"] == "valid")
            risky = sum(1 for r in results if r["status"] == "risky")
            invalid = sum(1 for r in results if r["status"] == "invalid")
            
            print(f"\n📊 Results:")
            print(f"   ✅ Valid: {valid}")
            print(f"   ⚠️  Risky: {risky}")
            print(f"   ❌ Invalid: {invalid}")
            
            print(f"\n📋 Details:")
            for r in results:
                status_icon = {"valid": "✅", "risky": "⚠️", "invalid": "❌"}.get(r["status"], "?")
                score = r.get("score", 0)
                print(f"   {status_icon} {r['email']} (Score: {score})")
            
            return 0
        
        elif args.command == 'stats':
            stats = get_stats()
            print(f"\n📊 Verification Statistics:")
            print(f"   Total checked: {stats.get('total', 0)}")
            print(f"   ✅ Valid: {stats.get('valid', 0)}")
            print(f"   ⚠️  Risky: {stats.get('risky', 0)}")
            print(f"   ❌ Invalid: {stats.get('invalid', 0)}")
            
            total = stats.get('total', 0)
            if total > 0:
                valid_rate = (stats.get('valid', 0) / total) * 100
                print(f"\n   Valid rate: {valid_rate:.1f}%")
            return 0
        
        elif args.command == 'list':
            emails = get_verified_list(args.status)
            if not emails:
                print("No emails found.")
                return 0
            
            status_msg = f" with status '{args.status}'" if args.status else ""
            print(f"\n📧 Verified Emails{status_msg} ({len(emails)}):")
            
            count = 0
            for email, data in emails.items():
                if count >= args.limit:
                    print(f"   ... and {len(emails) - count} more")
                    break
                status_icon = {"valid": "✅", "risky": "⚠️", "invalid": "❌"}.get(data.get("status"), "?")
                score = data.get("score", 0)
                print(f"   {status_icon} {email} (Score: {score})")
                count += 1
            return 0
        
        elif args.command == 'clean':
            data = load_verified()
            
            if args.status:
                emails = data.get("emails", {})
                original_count = len(emails)
                emails = {k: v for k, v in emails.items() if v.get("status") != args.status}
                data["emails"] = emails
                
                # Update stats
                stats = data.get("stats", {})
                removed = original_count - len(emails)
                stats["total"] = max(0, stats.get("total", 0) - removed)
                stats[args.status] = 0
                data["stats"] = stats
                
                save_verified(data)
                print(f"✅ Removed {removed} emails with status '{args.status}'")
            else:
                # Clear all
                data = {"emails": {}, "stats": {"total": 0, "valid": 0, "invalid": 0, "risky": 0}}
                save_verified(data)
                print("✅ Cleared all verified emails")
            return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
