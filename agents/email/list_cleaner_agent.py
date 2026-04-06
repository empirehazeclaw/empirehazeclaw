#!/usr/bin/env python3
"""
List Cleaner Agent - EmpireHazeClaw
Cleans and deduplicates email lists with various filtering options.
"""

import argparse
import json
import logging
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

# Paths
BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "emails"
LOGS_DIR = BASE_DIR / "logs"
CLEANED_FILE = DATA_DIR / "cleaned_lists.json"
LOG_FILE = LOGS_DIR / "list_cleaner.log"

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
logger = logging.getLogger("ListCleaner")


# Disposable email domains
DISPOSABLE_DOMAINS = {
    'tempmail.com', 'throwaway.com', 'mailinator.com', 'guerrillamail.com',
    '10minutemail.com', 'temp-mail.org', 'fakeinbox.com', 'trashmail.com',
    'maildrop.cc', 'getairmail.com', 'yopmail.com', 'sharklasers.com',
    'dispostable.com', 'mailnesia.com', 'tempr.email', 'discard.email',
    'mintemail.com', 'spamgourmet.com', 'mytrashmail.com', 'mailexpire.com'
}


def load_lists():
    """Load saved cleaned lists."""
    if CLEANED_FILE.exists():
        try:
            with open(CLEANED_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"lists": {}}
    return {"lists": {}}


def save_lists(data):
    """Save cleaned lists."""
    with open(CLEANED_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def normalize_email(email):
    """Normalize email address (lowercase, strip whitespace)."""
    email = email.lower().strip()
    # Remove display names
    if '<' in email:
        email = email.split('<')[1].split('>')[0]
    return email


def validate_syntax(email):
    """Validate email syntax."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_disposable(email):
    """Check if email uses disposable domain."""
    domain = email.split('@')[1] if '@' in email else ''
    return domain.lower() in DISPOSABLE_DOMAINS


def is_role_email(email):
    """Check if email is a role-based address (info@, support@, etc.)."""
    role_prefixes = {'info', 'support', 'admin', 'sales', 'marketing', 'noreply', 
                     'no-reply', 'hello', 'contact', 'webmaster', 'postmaster', 'abuse'}
    local = email.split('@')[0] if '@' in email else ''
    return local.lower() in role_prefixes


def remove_duplicates(emails):
    """Remove duplicate emails (case-insensitive)."""
    seen = set()
    unique = []
    duplicates = []
    
    for email in emails:
        normalized = normalize_email(email)
        if normalized not in seen:
            seen.add(normalized)
            unique.append(normalized)
        else:
            duplicates.append(email)
    
    return unique, duplicates


def clean_list(emails, remove_disposable=True, remove_invalid=True, 
                remove_duplicates_flag=True, remove_role=True, min_length=0):
    """Clean an email list with various filters."""
    original_count = len(emails)
    
    # Normalize all emails
    emails = [normalize_email(e) for e in emails if e.strip()]
    
    results = {
        "original": emails.copy(),
        "cleaned": [],
        "removed": {
            "duplicates": [],
            "invalid": [],
            "disposable": [],
            "role_based": [],
            "too_short": []
        },
        "stats": {}
    }
    
    seen = set()
    
    for email in emails:
        # Skip if already seen (duplicate)
        if email in seen:
            results["removed"]["duplicates"].append(email)
            continue
        seen.add(email)
        
        # Check if valid syntax
        if remove_invalid and not validate_syntax(email):
            results["removed"]["invalid"].append(email)
            continue
        
        # Check disposable
        if remove_disposable and is_disposable(email):
            results["removed"]["disposable"].append(email)
            continue
        
        # Check role-based
        if remove_role and is_role_email(email):
            results["removed"]["role_based"].append(email)
            continue
        
        # Check min length
        if min_length > 0 and len(email.split('@')[0]) < min_length:
            results["removed"]["too_short"].append(email)
            continue
        
        results["cleaned"].append(email)
    
    # Calculate stats
    results["stats"] = {
        "original_count": original_count,
        "cleaned_count": len(results["cleaned"]),
        "removed_count": original_count - len(results["cleaned"]),
        "duplicate_count": len(results["removed"]["duplicates"]),
        "invalid_count": len(results["removed"]["invalid"]),
        "disposable_count": len(results["removed"]["disposable"]),
        "role_count": len(results["removed"]["role_based"]),
        "retention_rate": round(len(results["cleaned"]) / original_count * 100, 1) if original_count > 0 else 0
    }
    
    return results


def analyze_list(emails):
    """Analyze an email list without cleaning."""
    emails = [normalize_email(e) for e in emails if e.strip()]
    
    domains = Counter()
    tlds = Counter()
    local_parts = Counter()
    
    for email in emails:
        if '@' in email:
            local, domain = email.split('@')
            domains[domain] += 1
            tlds[domain.split('.')[-1]] += 1
            local_parts[local] += 1
    
    # Find potential duplicates
    duplicates = {k: v for k, v in Counter(emails).items() if v > 1}
    
    # Find disposable usage
    disposable = [e for e in emails if is_disposable(e)]
    
    # Find role-based
    roles = [e for e in emails if is_role_email(e)]
    
    # Find invalid
    invalid = [e for e in emails if not validate_syntax(e)]
    
    return {
        "total": len(emails),
        "unique": len(set(emails)),
        "duplicate_count": sum(v - 1 for v in duplicates.values()),
        "domains": dict(domains.most_common(20)),
        "tlds": dict(tlds.most_common(10)),
        "disposable_count": len(disposable),
        "disposable_list": disposable[:20],
        "role_count": len(roles),
        "role_list": roles[:20],
        "invalid_count": len(invalid),
        "invalid_list": invalid[:20]
    }


def save_cleaned_list(name, emails, results):
    """Save a cleaned list to storage."""
    data = load_lists()
    
    data["lists"][name] = {
        "name": name,
        "emails": emails,
        "created_at": datetime.now().isoformat(),
        "stats": results["stats"],
        "original_count": results["stats"]["original_count"]
    }
    
    save_lists(data)
    logger.info(f"Saved cleaned list: {name} with {len(emails)} emails")
    return data["lists"][name]


def get_saved_lists():
    """Get all saved cleaned lists."""
    data = load_lists()
    return data.get("lists", {})


def delete_list(name):
    """Delete a saved list."""
    data = load_lists()
    if name in data["lists"]:
        del data["lists"][name]
        save_lists(data)
        return True
    return False


def export_list(name, filepath, format='txt'):
    """Export a saved list to file."""
    data = load_lists()
    
    if name not in data["lists"]:
        raise ValueError(f"List '{name}' not found")
    
    emails = data["lists"][name]["emails"]
    
    if format == 'txt':
        with open(filepath, 'w') as f:
            f.write('\n'.join(emails))
    elif format == 'json':
        with open(filepath, 'w') as f:
            json.dump({"emails": emails, "count": len(emails)}, f, indent=2)
    elif format == 'csv':
        with open(filepath, 'w') as f:
            f.write("email\n")
            for email in emails:
                f.write(f"{email}\n")
    
    return filepath


def main():
    parser = argparse.ArgumentParser(
        description="List Cleaner Agent - Clean, deduplicate, and analyze email lists",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Clean an email list
  %(prog)s clean --input emails.txt --output cleaned.txt
  
  # Analyze without cleaning
  %(prog)s analyze --file emails.txt
  
  # Clean with specific options
  %(prog)s clean --input emails.txt --keep-disposable --keep-role --keep-duplicates --output cleaned.txt
  
  # Save cleaned list to storage
  %(prog)s save --name mylist --file emails.txt
  
  # List saved lists
  %(prog)s lists
  
  # Export saved list
  %(prog)s export --name mylist --file cleaned.csv --format csv
  
  # Delete saved list
  %(prog)s delete --name mylist
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Clean email list')
    clean_parser.add_argument('--input', '--file', required=True, help='Input file')
    clean_parser.add_argument('--output', '-o', help='Output file (optional)')
    clean_parser.add_argument('--keep-disposable', action='store_true', help='Keep disposable emails')
    clean_parser.add_argument('--keep-invalid', action='store_true', help='Keep invalid emails')
    clean_parser.add_argument('--keep-duplicates', action='store_true', help='Keep duplicates')
    clean_parser.add_argument('--keep-role', action='store_true', help='Keep role-based emails')
    clean_parser.add_argument('--save', help='Save to storage with name')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze email list without cleaning')
    analyze_parser.add_argument('--file', '--input', required=True, help='Input file')
    
    # Save command
    save_parser = subparsers.add_parser('save', help='Save cleaned list to storage')
    save_parser.add_argument('--name', required=True, help='List name')
    save_parser.add_argument('--file', required=True, help='Input file')
    save_parser.add_argument('--clean', action='store_true', help='Clean before saving')
    
    # Lists command
    subparsers.add_parser('lists', help='List saved cleaned lists')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export saved list')
    export_parser.add_argument('--name', required=True, help='List name')
    export_parser.add_argument('--file', required=True, help='Output file path')
    export_parser.add_argument('--format', choices=['txt', 'json', 'csv'], default='txt', help='Output format')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete saved list')
    delete_parser.add_argument('--name', required=True, help='List name to delete')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        if args.command == 'clean':
            # Load emails from file
            with open(args.input, 'r') as f:
                emails = [line.strip() for line in f if line.strip()]
            
            print(f"📋 Loaded {len(emails)} emails from {args.input}")
            
            # Clean
            results = clean_list(
                emails,
                remove_disposable=not args.keep_disposable,
                remove_invalid=not args.keep_invalid,
                remove_duplicates_flag=not args.keep_duplicates,
                remove_role=not args.keep_role
            )
            
            print(f"\n🧹 Cleaning Results:")
            print(f"   Original: {results['stats']['original_count']}")
            print(f"   Cleaned: {results['stats']['cleaned_count']}")
            print(f"   Removed: {results['stats']['removed_count']}")
            print(f"\n   📊 Removed breakdown:")
            print(f"      Duplicates: {results['stats']['duplicate_count']}")
            print(f"      Invalid: {results['stats']['invalid_count']}")
            print(f"      Disposable: {results['stats']['disposable_count']}")
            print(f"      Role-based: {results['stats']['role_count']}")
            print(f"\n   ✅ Retention rate: {results['stats']['retention_rate']}%")
            
            # Output
            if args.output:
                with open(args.output, 'w') as f:
                    f.write('\n'.join(results['cleaned']))
                print(f"\n💾 Saved to: {args.output}")
            
            if args.save:
                save_cleaned_list(args.save, results['cleaned'], results)
                print(f"💾 Saved to storage as: {args.save}")
            
            return 0
        
        elif args.command == 'analyze':
            with open(args.file, 'r') as f:
                emails = [line.strip() for line in f if line.strip()]
            
            print(f"📊 Analyzing {len(emails)} emails from {args.file}...\n")
            
            analysis = analyze_list(emails)
            
            print(f"📈 List Analysis:")
            print(f"   Total emails: {analysis['total']}")
            print(f"   Unique emails: {analysis['unique']}")
            print(f"   Duplicates: {analysis['duplicate_count']}")
            print(f"\n🚫 Issues found:")
            print(f"   Invalid syntax: {analysis['invalid_count']}")
            print(f"   Disposable domains: {analysis['disposable_count']}")
            print(f"   Role-based accounts: {analysis['role_count']}")
            
            if analysis['domains']:
                print(f"\n📧 Top Domains:")
                for domain, count in list(analysis['domains'].items())[:5]:
                    print(f"   {domain}: {count}")
            
            if analysis['tlds']:
                print(f"\n🌐 Top TLDs:")
                for tld, count in analysis['tlds'].items():
                    print(f"   .{tld}: {count}")
            
            if analysis['disposable_list']:
                print(f"\n⚠️  Disposable domains (sample):")
                for email in analysis['disposable_list'][:5]:
                    print(f"   {email}")
            
            return 0
        
        elif args.command == 'save':
            with open(args.file, 'r') as f:
                emails = [line.strip() for line in f if line.strip()]
            
            if args.clean:
                results = clean_list(emails)
                emails = results['cleaned']
                print(f"✅ Cleaned list: {len(emails)} emails")
            else:
                print(f"📋 Saving {len(emails)} emails")
            
            # Create a simple result object
            class SimpleResults:
                stats = {"original_count": len(emails), "cleaned_count": len(emails), 
                        "removed_count": 0, "duplicate_count": 0, "invalid_count": 0,
                        "disposable_count": 0, "role_count": 0, "retention_rate": 100}
            
            save_cleaned_list(args.name, emails, SimpleResults())
            print(f"✅ Saved list as '{args.name}'")
            return 0
        
        elif args.command == 'lists':
            lists = get_saved_lists()
            
            if not lists:
                print("No saved lists.")
                return 0
            
            print(f"\n📁 Saved Lists ({len(lists)}):")
            for name, data in lists.items():
                print(f"   [{name}]")
                print(f"       Emails: {len(data['emails'])}")
                print(f"       Saved: {data['created_at']}")
            return 0
        
        elif args.command == 'export':
            path = export_list(args.name, args.file, args.format)
            print(f"✅ Exported to: {path}")
            return 0
        
        elif args.command == 'delete':
            if delete_list(args.name):
                print(f"✅ Deleted list '{args.name}'")
                return 0
            else:
                print(f"❌ List '{args.name}' not found")
                return 1
        
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
