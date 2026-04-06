#!/usr/bin/env python3
"""
QR Code Generator Agent - Productivity Division
Generates QR codes for URLs, text, WiFi, vCards, and more.

Inspired by SOUL.md: CEO mindset, Ressourceneffizienz, Geschwindigkeit über Perfektion
"""

import argparse
import base64
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
DATA_DIR = WORKSPACE / "data" / "productivity"
QR_HISTORY_FILE = DATA_DIR / "qr_history.json"

# Ensure directories exist
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - QR-GENERATOR - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "qr_generator.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def load_history():
    """Load QR code generation history."""
    if not QR_HISTORY_FILE.exists():
        return {"history": [], "version": "1.0"}
    try:
        with open(QR_HISTORY_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse history file: {e}")
        return {"history": [], "version": "1.0"}


def save_history(data):
    """Save QR code generation history."""
    try:
        with open(QR_HISTORY_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        logger.error(f"Failed to save history: {e}")


def generate_qr(data, output_path=None, format='PNG', size=10, 
                error_correction='M', border=4, dark_color='000000', light_color='ffffff'):
    """Generate QR code using available libraries."""
    
    # Try qrcode library first
    try:
        import qrcode
        from qrcode.image import pil
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=getattr(qrcode.constants, f'ERROR_CORRECT_{error_correction}'),
            box_size=size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color=dark_color, back_color=light_color)
        
        if output_path:
            img.save(output_path)
            logger.info(f"Generated QR code: {output_path}")
            print(f"✅ QR code saved to: {output_path}")
        else:
            # Save to default location
            default_path = DATA_DIR / f"qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            img.save(default_path)
            logger.info(f"Generated QR code: {default_path}")
            print(f"✅ QR code saved to: {default_path}")
            output_path = default_path
        
        return str(output_path)
    
    except ImportError:
        # Fallback: try pillow with basic generation
        try:
            from PIL import Image, ImageDraw
            
            # Simple fallback for basic QR (won't be scannable without proper library)
            print("⚠️  qrcode library not found. Installing...")
            os.system("pip install qrcode[pil] -q")
            
            # Retry
            import qrcode
            from qrcode.image import pil
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=getattr(qrcode.constants, f'ERROR_CORRECT_{error_correction}'),
                box_size=size,
                border=border,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color=dark_color, back_color=light_color)
            
            if output_path:
                img.save(output_path)
            else:
                default_path = DATA_DIR / f"qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                img.save(default_path)
                output_path = default_path
            
            print(f"✅ QR code saved to: {output_path}")
            return str(output_path)
            
        except ImportError:
            logger.error("Failed to import qrcode library")
            print("❌ Error: qrcode library required. Install with: pip install qrcode[pil]")
            return None


def generate_url_qr(url, output_path=None, **kwargs):
    """Generate QR code for URL."""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return generate_qr(url, output_path, **kwargs)


def generate_text_qr(text, output_path=None, **kwargs):
    """Generate QR code for plain text."""
    return generate_qr(text, output_path, **kwargs)


def generate_wifi_qr(ssid, password, hidden=False, output_path=None, **kwargs):
    """Generate QR code for WiFi credentials."""
    auth_type = 'WPA' if password else 'nopass'
    hidden_str = 'H:true' if hidden else 'H:false'
    wifi_string = f"WIFI:T:{auth_type};S:{ssid};P:{password};{hidden_str};;"
    return generate_qr(wifi_string, output_path, **kwargs)


def generate_email_qr(email, subject=None, body=None, output_path=None, **kwargs):
    """Generate QR code for email."""
    mailto = f"mailto:{email}"
    if subject:
        mailto += f"?subject={subject}"
    if body:
        if subject:
            mailto += f"&body={body}"
        else:
            mailto += f"?body={body}"
    return generate_qr(mailto, output_path, **kwargs)


def generate_sms_qr(phone, message=None, output_path=None, **kwargs):
    """Generate QR code for SMS."""
    sms = f"smsto:{phone}"
    if message:
        sms += f":{message}"
    return generate_qr(sms, output_path, **kwargs)


def generate_vcard_qr(name, phone=None, email=None, organization=None, 
                      address=None, website=None, output_path=None, **kwargs):
    """Generate QR code for vCard."""
    vcard = "BEGIN:VCARD\nVERSION:3.0\n"
    vcard += f"FN:{name}\n"
    vcard += f"N:{name}\n"
    if phone:
        vcard += f"TEL:{phone}\n"
    if email:
        vcard += f"EMAIL:{email}\n"
    if organization:
        vcard += f"ORG:{organization}\n"
    if address:
        vcard += f"ADR:{address}\n"
    if website:
        vcard += f"URL:{website}\n"
    vcard += "END:VCARD"
    return generate_qr(vcard, output_path, **kwargs)


def generate_geo_qr(latitude, longitude, output_path=None, **kwargs):
    """Generate QR code for geo location."""
    geo_string = f"geo:{latitude},{longitude}"
    return generate_qr(geo_string, output_path, **kwargs)


def save_to_history(data_type, content, output_path, success=True):
    """Save generation to history."""
    history = load_history()
    entry = {
        "id": len(history['history']) + 1,
        "type": data_type,
        "content": content[:200],  # Truncate for storage
        "output": str(output_path),
        "success": success,
        "created_at": datetime.now().isoformat()
    }
    history['history'].append(entry)
    save_history(history)
    logger.info(f"Saved QR generation to history: {data_type}")


def show_history(limit=20):
    """Show QR code generation history."""
    history = load_history()
    entries = history['history'][-limit:]
    
    if not entries:
        print("📭 No QR codes generated yet.")
        return
    
    print(f"\n📋 Recent QR Codes ({len(entries)} of {len(history['history'])} total):")
    print("-" * 70)
    for entry in reversed(entries):
        status = "✅" if entry.get('success') else "❌"
        print(f"{status} [{entry['id']}] {entry['type']}")
        print(f"   Content: {entry.get('content', 'N/A')[:60]}...")
        print(f"   Saved: {entry['created_at'][:19]}")
        print()


def get_stats():
    """Show QR code generation statistics."""
    history = load_history()
    entries = history['history']
    
    total = len(entries)
    successful = len([e for e in entries if e.get('success')])
    
    type_counts = {}
    for entry in entries:
        t = entry.get('type', 'unknown')
        type_counts[t] = type_counts.get(t, 0) + 1
    
    print(f"\n📊 QR Code Statistics:")
    print("=" * 40)
    print(f"Total Generated:   {total}")
    print(f"Successful:       {successful} ✅")
    print(f"Failed:           {total - successful} ❌")
    if entries:
        print(f"\nBy Type:")
        for t, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            print(f"  📱 {t}: {count}")


def main():
    parser = argparse.ArgumentParser(
        description="QR Code Generator Agent - Create QR codes for any data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s url "https://example.com" -o qr.png
  %(prog)s url "https://empirehazeclaw.store" --size 15
  %(prog)s text "Hello, World!"
  %(prog)s wifi "MyNetwork" "password123" --hidden
  %(prog)s email "contact@example.com" --subject "Hello" --body "Message"
  %(prog)s sms "+1234567890" --message "Call me"
  %(prog)s vcard "John Doe" --phone "+1234567890" --email john@example.com --org "Acme Inc"
  %(prog)s geo "40.7128" "-74.0060"
  %(prog)s history
  %(prog)s stats

QR Code Options:
  --output, -o     Output file path
  --size           Box size (default: 10)
  --border         Border size (default: 4)
  --error          Error correction: L, M, Q, H (default: M)
  --dark           Dark color hex (default: 000000)
  --light          Light color hex (default: ffffff)
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # URL QR
    url_parser = subparsers.add_parser('url', help='Generate QR for URL')
    url_parser.add_argument('url', help='URL address')
    url_parser.add_argument('--output', '-o', help='Output file path')
    url_parser.add_argument('--size', '-s', type=int, default=10, help='Box size')
    url_parser.add_argument('--border', '-b', type=int, default=4, help='Border size')
    url_parser.add_argument('--error', '-e', default='M', choices=['L', 'M', 'Q', 'H'],
                           help='Error correction level')
    url_parser.add_argument('--dark', default='000000', help='Dark color hex')
    url_parser.add_argument('--light', default='ffffff', help='Light color hex')
    
    # Text QR
    text_parser = subparsers.add_parser('text', help='Generate QR for plain text')
    text_parser.add_argument('text', help='Text content')
    text_parser.add_argument('--output', '-o', help='Output file path')
    text_parser.add_argument('--size', '-s', type=int, default=10)
    text_parser.add_argument('--border', '-b', type=int, default=4)
    text_parser.add_argument('--error', '-e', default='M', choices=['L', 'M', 'Q', 'H'])
    text_parser.add_argument('--dark', default='000000')
    text_parser.add_argument('--light', default='ffffff')
    
    # WiFi QR
    wifi_parser = subparsers.add_parser('wifi', help='Generate QR for WiFi')
    wifi_parser.add_argument('ssid', help='WiFi network name')
    wifi_parser.add_argument('--password', '-p', help='WiFi password')
    wifi_parser.add_argument('--hidden', action='store_true', help='Hidden network')
    wifi_parser.add_argument('--output', '-o', help='Output file path')
    wifi_parser.add_argument('--size', '-s', type=int, default=10)
    wifi_parser.add_argument('--border', '-b', type=int, default=4)
    wifi_parser.add_argument('--error', '-e', default='M', choices=['L', 'M', 'Q', 'H'])
    wifi_parser.add_argument('--dark', default='000000')
    wifi_parser.add_argument('--light', default='ffffff')
    
    # Email QR
    email_parser = subparsers.add_parser('email', help='Generate QR for email')
    email_parser.add_argument('email', help='Email address')
    email_parser.add_argument('--subject', help='Email subject')
    email_parser.add_argument('--body', help='Email body')
    email_parser.add_argument('--output', '-o', help='Output file path')
    email_parser.add_argument('--size', '-s', type=int, default=10)
    email_parser.add_argument('--border', '-b', type=int, default=4)
    email_parser.add_argument('--error', '-e', default='M', choices=['L', 'M', 'Q', 'H'])
    email_parser.add_argument('--dark', default='000000')
    email_parser.add_argument('--light', default='ffffff')
    
    # SMS QR
    sms_parser = subparsers.add_parser('sms', help='Generate QR for SMS')
    sms_parser.add_argument('phone', help='Phone number')
    sms_parser.add_argument('--message', '-m', help='SMS message')
    sms_parser.add_argument('--output', '-o', help='Output file path')
    sms_parser.add_argument('--size', '-s', type=int, default=10)
    sms_parser.add_argument('--border', '-b', type=int, default=4)
    sms_parser.add_argument('--error', '-e', default='M', choices=['L', 'M', 'Q', 'H'])
    sms_parser.add_argument('--dark', default='000000')
    sms_parser.add_argument('--light', default='ffffff')
    
    # vCard QR
    vcard_parser = subparsers.add_parser('vcard', help='Generate QR for vCard')
    vcard_parser.add_argument('name', help='Full name')
    vcard_parser.add_argument('--phone', help='Phone number')
    vcard_parser.add_argument('--email', help='Email address')
    vcard_parser.add_argument('--org', help='Organization')
    vcard_parser.add_argument('--address', help='Address')
    vcard_parser.add_argument('--website', help='Website URL')
    vcard_parser.add_argument('--output', '-o', help='Output file path')
    vcard_parser.add_argument('--size', '-s', type=int, default=10)
    vcard_parser.add_argument('--border', '-b', type=int, default=4)
    vcard_parser.add_argument('--error', '-e', default='M', choices=['L', 'M', 'Q', 'H'])
    vcard_parser.add_argument('--dark', default='000000')
    vcard_parser.add_argument('--light', default='ffffff')
    
    # Geo QR
    geo_parser = subparsers.add_parser('geo', help='Generate QR for geo location')
    geo_parser.add_argument('latitude', help='Latitude')
    geo_parser.add_argument('longitude', help='Longitude')
    geo_parser.add_argument('--output', '-o', help='Output file path')
    geo_parser.add_argument('--size', '-s', type=int, default=10)
    geo_parser.add_argument('--border', '-b', type=int, default=4)
    geo_parser.add_argument('--error', '-e', default='M', choices=['L', 'M', 'Q', 'H'])
    geo_parser.add_argument('--dark', default='000000')
    geo_parser.add_argument('--light', default='ffffff')
    
    # History
    subparsers.add_parser('history', help='Show generation history')
    
    # Stats
    subparsers.add_parser('stats', help='Show statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        kwargs = {
            'size': args.size if hasattr(args, 'size') else 10,
            'border': args.border if hasattr(args, 'border') else 4,
            'error_correction': args.error if hasattr(args, 'error') else 'M',
            'dark_color': args.dark if hasattr(args, 'dark') else '000000',
            'light_color': args.light if hasattr(args, 'light') else 'ffffff'
        }
        output_path = args.output if hasattr(args, 'output') else None
        
        if args.command == 'url':
            result = generate_url_qr(args.url, output_path, **kwargs)
            if result:
                save_to_history('url', args.url, result)
        
        elif args.command == 'text':
            result = generate_text_qr(args.text, output_path, **kwargs)
            if result:
                save_to_history('text', args.text, result)
        
        elif args.command == 'wifi':
            result = generate_wifi_qr(args.ssid, args.password, args.hidden, output_path, **kwargs)
            if result:
                content = f"WIFI:{args.ssid}"
                save_to_history('wifi', content, result)
        
        elif args.command == 'email':
            result = generate_email_qr(args.email, args.subject, args.body, output_path, **kwargs)
            if result:
                content = f"mailto:{args.email}"
                save_to_history('email', content, result)
        
        elif args.command == 'sms':
            result = generate_sms_qr(args.phone, args.message, output_path, **kwargs)
            if result:
                content = f"smsto:{args.phone}"
                save_to_history('sms', content, result)
        
        elif args.command == 'vcard':
            result = generate_vcard_qr(args.name, args.phone, args.email, args.org, 
                                       args.address, args.website, output_path, **kwargs)
            if result:
                save_to_history('vcard', args.name, result)
        
        elif args.command == 'geo':
            result = generate_geo_qr(args.latitude, args.longitude, output_path, **kwargs)
            if result:
                content = f"geo:{args.latitude},{args.longitude}"
                save_to_history('geo', content, result)
        
        elif args.command == 'history':
            show_history()
        
        elif args.command == 'stats':
            get_stats()
    
    except Exception as e:
        logger.error(f"Error generating QR code: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
