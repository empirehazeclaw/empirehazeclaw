#!/usr/bin/env python3
"""
🍽️ RESTAURANT RESERVATION TRACKER
====================================
Track reservations, manage waitlist, send reminders.

Usage:
    python3 reservation_tracker.py --add "John Doe" --date 2026-04-01 --time 19:00 --guests 4
    python3 reservation_tracker.py --list --date 2026-04-01
    python3 reservation_tracker.py --remind --date tomorrow

Author: EmpireHazeClaw
Version: 1.0
"""

import json
import csv
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_FILE = DATA_DIR / "reservations.json"
ARCHIVE_FILE = DATA_DIR / "reservations_archive.json"

class ReservationTracker:
    def __init__(self):
        self.data_file = DATA_FILE
        self.archive_file = ARCHIVE_FILE
        self._ensure_data_dir()
        self._load_data()
    
    def _ensure_data_dir(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    def _load_data(self):
        """Load reservations from file"""
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {"reservations": [], "waitlist": []}
    
    def _save_data(self):
        """Save reservations to file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def _generate_id(self):
        """Generate unique reservation ID"""
        if not self.data['reservations']:
            return "RES-001"
        last_id = max([r['id'] for r in self.data['reservations']])
        num = int(last_id.split('-')[1]) + 1
        return f"RES-{num:03d}"
    
    def add_reservation(self, name, phone, email, date, time, guests, notes="", special=""):
        """Add new reservation"""
        reservation = {
            "id": self._generate_id(),
            "name": name,
            "phone": phone,
            "email": email,
            "date": date,
            "time": time,
            "guests": int(guests),
            "notes": notes,
            "special": special,  # birthday, anniversary, etc.
            "status": "confirmed",
            "created_at": datetime.now().isoformat(),
            "reminder_sent": False,
            "source": "manual"
        }
        self.data['reservations'].append(reservation)
        self._save_data()
        return reservation
    
    def list_reservations(self, date=None, status=None):
        """List reservations, optionally filtered"""
        reservations = self.data['reservations']
        
        if date:
            reservations = [r for r in reservations if r['date'] == date]
        
        if status:
            reservations = [r for r in reservations if r['status'] == status]
        
        # Sort by date and time
        reservations.sort(key=lambda x: (x['date'], x['time']))
        
        return reservations
    
    def get_today_reservations(self):
        """Get today's reservations"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.list_reservations(date=today)
    
    def get_tomorrow_reservations(self):
        """Get tomorrow's reservations"""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        return self.list_reservations(date=tomorrow)
    
    def update_reservation(self, res_id, **kwargs):
        """Update reservation fields"""
        for res in self.data['reservations']:
            if res['id'] == res_id:
                for key, value in kwargs.items():
                    if key in res:
                        res[key] = value
                res['updated_at'] = datetime.now().isoformat()
                self._save_data()
                return res
        return None
    
    def cancel_reservation(self, res_id, reason=""):
        """Cancel a reservation"""
        for res in self.data['reservations']:
            if res['id'] == res_id:
                res['status'] = 'cancelled'
                res['cancelled_at'] = datetime.now().isoformat()
                res['cancel_reason'] = reason
                self._save_data()
                return res
        return None
    
    def mark_noshow(self, res_id):
        """Mark reservation as no-show"""
        return self.update_reservation(res_id, status='noshow')
    
    def add_to_waitlist(self, name, phone, date, time, guests, priority=1):
        """Add party to waitlist"""
        waitlist_entry = {
            "id": f"WL-{len(self.data['waitlist']) + 1:03d}",
            "name": name,
            "phone": phone,
            "date": date,
            "time": time,
            "guests": int(guests),
            "priority": priority,
            "added_at": datetime.now().isoformat()
        }
        self.data['waitlist'].append(waitlist_entry)
        self._save_data()
        return waitlist_entry
    
    def get_waitlist(self, date=None):
        """Get waitlist, optionally filtered by date"""
        waitlist = self.data['waitlist']
        if date:
            waitlist = [w for w in waitlist if w['date'] == date]
        waitlist.sort(key=lambda x: (x['date'], x['time'], -x['priority']))
        return waitlist
    
    def remove_from_waitlist(self, wl_id):
        """Remove entry from waitlist"""
        self.data['waitlist'] = [w for w in self.data['waitlist'] if w['id'] != wl_id]
        self._save_data()
    
    def get_stats(self, days=30):
        """Get reservation statistics"""
        reservations = self.data['reservations']
        
        # Filter by date range
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        recent = [r for r in reservations if r['date'] >= cutoff]
        
        stats = {
            "total_reservations": len(recent),
            "confirmed": len([r for r in recent if r['status'] == 'confirmed']),
            "cancelled": len([r for r in recent if r['status'] == 'cancelled']),
            "noshow": len([r for r in recent if r['status'] == 'noshow']),
            "completed": len([r for r in recent if r['status'] == 'completed']),
            "total_guests": sum(r['guests'] for r in recent),
            "avg_party_size": sum(r['guests'] for r in recent) / len(recent) if recent else 0
        }
        
        stats['cancellation_rate'] = (stats['cancelled'] / stats['total_reservations'] * 100) if stats['total_reservations'] > 0 else 0
        stats['noshow_rate'] = (stats['noshow'] / stats['total_reservations'] * 100) if stats['total_reservations'] > 0 else 0
        
        return stats
    
    def export_to_csv(self, filename="reservations_export.csv"):
        """Export reservations to CSV"""
        reservations = self.list_reservations()
        
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'id', 'name', 'phone', 'email', 'date', 'time', 
                'guests', 'status', 'special', 'notes', 'created_at'
            ])
            writer.writeheader()
            writer.writerows(reservations)
        
        return filename
    
    def print_reservation(self, res):
        """Pretty print a reservation"""
        print(f"\n{'='*50}")
        print(f"  {res['id']} | {res['date']} {res['time']}")
        print(f"{'='*50}")
        print(f"  Name:    {res['name']}")
        print(f"  Phone:   {res['phone']}")
        print(f"  Email:   {res['email']}")
        print(f"  Guests:  {res['guests']}")
        print(f"  Status:  {res['status'].upper()}")
        if res.get('special'):
            print(f"  Special: {res['special']}")
        if res.get('notes'):
            print(f"  Notes:   {res['notes']}")
        print(f"{'='*50}\n")
    
    def daily_summary(self, date=None):
        """Print daily summary"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        reservations = self.list_reservations(date=date)
        
        print(f"\n📅 TAGESÜBERSICHT: {date}")
        print("="*60)
        print(f"Reservierungen: {len(reservations)}")
        print(f"Totale Gäste: {sum(r['guests'] for r in reservations)}")
        
        # Group by hour
        by_hour = {}
        for res in reservations:
            hour = res['time'].split(':')[0]
            if hour not in by_hour:
                by_hour[hour] = {"count": 0, "guests": 0}
            by_hour[hour]["count"] += 1
            by_hour[hour]["guests"] += res['guests']
        
        print("\nStündliche Verteilung:")
        for hour in sorted(by_hour.keys()):
            print(f"  {hour}:00 - {by_hour[hour]['count']} Reservierungen ({by_hour[hour]['guests']} Gäste)")
        
        # Special occasions
        specials = [r for r in reservations if r.get('special')]
        if specials:
            print(f"\nBesondere Anlässe: {len(specials)}")
            for res in specials:
                print(f"  - {res['name']}: {res['special']}")
        
        # Waitlist for this date
        waitlist = self.get_waitlist(date=date)
        if waitlist:
            print(f"\nWarteliste: {len(waitlist)}")
            for w in waitlist:
                print(f"  - {w['name']} ({w['guests']} Pers., {w['time']})")
        
        print("="*60)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Restaurant Reservation Tracker")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add reservation
    add_parser = subparsers.add_parser('add', help='Add new reservation')
    add_parser.add_argument('--name', required=True, help='Guest name')
    add_parser.add_argument('--phone', required=True, help='Phone number')
    add_parser.add_argument('--email', default='', help='Email address')
    add_parser.add_argument('--date', required=True, help='Date (YYYY-MM-DD)')
    add_parser.add_argument('--time', required=True, help='Time (HH:MM)')
    add_parser.add_argument('--guests', type=int, required=True, help='Number of guests')
    add_parser.add_argument('--special', default='', help='Special occasion')
    add_parser.add_argument('--notes', default='', help='Additional notes')
    
    # List reservations
    list_parser = subparsers.add_parser('list', help='List reservations')
    list_parser.add_argument('--date', help='Filter by date (YYYY-MM-DD)')
    list_parser.add_argument('--status', help='Filter by status')
    
    # Show daily summary
    summary_parser = subparsers.add_parser('summary', help='Daily summary')
    summary_parser.add_argument('--date', help='Date (YYYY-MM-DD), default: today')
    
    # Cancel
    cancel_parser = subparsers.add_parser('cancel', help='Cancel reservation')
    cancel_parser.add_argument('--id', required=True, help='Reservation ID')
    cancel_parser.add_argument('--reason', default='', help='Cancellation reason')
    
    # Stats
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    stats_parser.add_argument('--days', type=int, default=30, help='Days to analyze')
    
    # Waitlist
    waitlist_parser = subparsers.add_parser('waitlist', help='Manage waitlist')
    waitlist_parser.add_argument('--add', action='store_true', help='Add to waitlist')
    waitlist_parser.add_argument('--name', help='Guest name')
    waitlist_parser.add_argument('--phone', help='Phone number')
    waitlist_parser.add_argument('--date', help='Date (YYYY-MM-DD)')
    waitlist_parser.add_argument('--time', help='Time (HH:MM)')
    waitlist_parser.add_argument('--guests', type=int, help='Number of guests')
    
    # Export
    export_parser = subparsers.add_parser('export', help='Export to CSV')
    export_parser.add_argument('--filename', default='reservations_export.csv')
    
    args = parser.parse_args()
    
    tracker = ReservationTracker()
    
    if args.command == 'add':
        res = tracker.add_reservation(
            name=args.name,
            phone=args.phone,
            email=args.email,
            date=args.date,
            time=args.time,
            guests=args.guests,
            notes=args.notes,
            special=args.special
        )
        print(f"✅ Reservation added: {res['id']}")
        tracker.print_reservation(res)
    
    elif args.command == 'list':
        reservations = tracker.list_reservations(date=args.date, status=args.status)
        if not reservations:
            print("No reservations found.")
        else:
            for res in reservations:
                print(f"  {res['id']} | {res['date']} {res['time']} | {res['name']} | {res['guests']} Pers. | {res['status']}")
    
    elif args.command == 'summary':
        tracker.daily_summary(date=args.date)
    
    elif args.command == 'cancel':
        result = tracker.cancel_reservation(args.id, reason=args.reason)
        if result:
            print(f"✅ Reservation {args.id} cancelled.")
        else:
            print(f"❌ Reservation {args.id} not found.")
    
    elif args.command == 'stats':
        stats = tracker.get_stats(days=args.days)
        print(f"\n📊 STATISTIK (letzte {args.days} Tage)")
        print("="*40)
        print(f"  Gesamt Reservierungen: {stats['total_reservations']}")
        print(f"  Bestätigt: {stats['confirmed']}")
        print(f"  Storniert: {stats['cancelled']} ({stats['cancellation_rate']:.1f}%)")
        print(f"  No-Shows: {stats['noshow']} ({stats['noshow_rate']:.1f}%)")
        print(f"  Abgeschlossen: {stats['completed']}")
        print(f"  Totale Gäste: {stats['total_guests']}")
        print(f"  Ø Gruppengröße: {stats['avg_party_size']:.1f}")
        print("="*40)
    
    elif args.command == 'waitlist':
        if args.add:
            entry = tracker.add_to_waitlist(
                name=args.name,
                phone=args.phone,
                date=args.date,
                time=args.time,
                guests=args.guests
            )
            print(f"✅ Added to waitlist: {entry['id']}")
        else:
            waitlist = tracker.get_waitlist()
            if not waitlist:
                print("Waitlist is empty.")
            else:
                for w in waitlist:
                    print(f"  {w['id']} | {w['date']} {w['time']} | {w['name']} | {w['guests']} Pers.")
    
    elif args.command == 'export':
        filename = tracker.export_to_csv(args.filename)
        print(f"✅ Exported to {filename}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
