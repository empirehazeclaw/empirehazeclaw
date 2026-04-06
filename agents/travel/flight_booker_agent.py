#!/usr/bin/env python3
"""
Flight Booker Agent - Search and book flights
Part of the Travel Agent Suite
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Setup
BASE_DIR = Path(__file__).parent.parent.parent.parent
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data" / "travel"
SCRIPT_NAME = "flight_booker_agent"

LOGS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / f"{SCRIPT_NAME}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(SCRIPT_NAME)

DATA_FILE = DATA_DIR / "flights.json"
BOOKINGS_FILE = DATA_DIR / "flight_bookings.json"


def load_data(file_path: Path, default: dict = None) -> dict:
    """Load data from JSON file."""
    if default is None:
        default = {}
    try:
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading {file_path}: {e}")
    return default


def save_data(file_path: Path, data: dict) -> bool:
    """Save data to JSON file."""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except IOError as e:
        logger.error(f"Error saving to {file_path}: {e}")
        return False


def generate_sample_flights(origin: str, destination: str, departure_date: str, num_results: int = 5) -> list:
    """Generate sample flight data for demonstration."""
    flights = load_data(DATA_FILE)
    if not flights.get("sample_flights"):
        flights["sample_flights"] = [
            {"id": "FL001", "airline": "Lufthansa", "origin": "FRA", "destination": "JFK",
             "departure": "2026-04-01T08:00", "arrival": "2026-04-01T12:30", "price": 549.99, "seats": 42},
            {"id": "FL002", "airline": "United", "origin": "FRA", "destination": "JFK",
             "departure": "2026-04-01T14:00", "arrival": "2026-04-01T18:30", "price": 489.99, "seats": 18},
            {"id": "FL003", "airline": "Delta", "origin": "FRA", "destination": "JFK",
             "departure": "2026-04-01T19:00", "arrival": "2026-04-02T06:30", "price": 399.99, "seats": 156},
            {"id": "FL004", "airline": "Emirates", "origin": "FRA", "destination": "DXB",
             "departure": "2026-04-02T22:00", "arrival": "2026-04-03T07:00", "price": 299.99, "seats": 34},
            {"id": "FL005", "airline": "Swiss", "origin": "ZRH", "destination": "LHR",
             "departure": "2026-04-01T10:00", "arrival": "2026-04-01T11:15", "price": 129.99, "seats": 8},
        ]
        save_data(DATA_FILE, flights)
    return flights.get("sample_flights", [])


def search_flights(origin: str, destination: str, departure_date: Optional[str] = None) -> list:
    """Search for available flights."""
    logger.info(f"Searching flights: {origin} -> {destination}")
    all_flights = generate_sample_flights(origin, destination, departure_date or "")
    
    results = []
    for flight in all_flights:
        if flight["origin"].upper() == origin.upper() and flight["destination"].upper() == destination.upper():
            if flight["seats"] > 0:
                if departure_date:
                    if flight["departure"].startswith(departure_date):
                        results.append(flight)
                else:
                    results.append(flight)
    
    return results


def book_flight(flight_id: str, passenger_name: str, passenger_email: str) -> Optional[dict]:
    """Book a specific flight."""
    logger.info(f"Booking flight {flight_id} for {passenger_name}")
    all_flights = load_data(DATA_FILE)
    flights = all_flights.get("sample_flights", [])
    
    flight = None
    for f in flights:
        if f["id"] == flight_id:
            flight = f
            break
    
    if not flight:
        logger.error(f"Flight {flight_id} not found")
        return None
    
    if flight["seats"] <= 0:
        logger.error(f"No seats available on flight {flight_id}")
        return None
    
    # Create booking
    booking = {
        "booking_id": f"BK{int(datetime.now().timestamp())}",
        "flight_id": flight_id,
        "passenger_name": passenger_name,
        "passenger_email": passenger_email,
        "airline": flight["airline"],
        "origin": flight["origin"],
        "destination": flight["destination"],
        "departure": flight["departure"],
        "price": flight["price"],
        "status": "confirmed",
        "booked_at": datetime.now().isoformat()
    }
    
    # Load bookings
    bookings_data = load_data(BOOKINGS_FILE, {"bookings": []})
    bookings_data["bookings"].append(booking)
    save_data(BOOKINGS_FILE, bookings_data)
    
    # Decrease available seats
    for f in flights:
        if f["id"] == flight_id:
            f["seats"] -= 1
            break
    save_data(DATA_FILE, all_flights)
    
    logger.info(f"Booking confirmed: {booking['booking_id']}")
    return booking


def list_bookings(email: Optional[str] = None) -> list:
    """List all bookings, optionally filtered by email."""
    bookings_data = load_data(BOOKINGS_FILE, {"bookings": []})
    bookings = bookings_data.get("bookings", [])
    
    if email:
        bookings = [b for b in bookings if b.get("passenger_email", "").lower() == email.lower()]
    
    return bookings


def cancel_booking(booking_id: str) -> bool:
    """Cancel a booking and restore seat."""
    logger.info(f"Cancelling booking {booking_id}")
    bookings_data = load_data(BOOKINGS_FILE, {"bookings": []})
    flights_data = load_data(DATA_FILE)
    
    bookings = bookings_data.get("bookings", [])
    for i, booking in enumerate(bookings):
        if booking["booking_id"] == booking_id:
            booking["status"] = "cancelled"
            booking["cancelled_at"] = datetime.now().isoformat()
            
            # Restore seat
            flights = flights_data.get("sample_flights", [])
            for f in flights:
                if f["id"] == booking["flight_id"]:
                    f["seats"] += 1
                    break
            
            save_data(BOOKINGS_FILE, bookings_data)
            save_data(DATA_FILE, flights_data)
            logger.info(f"Booking {booking_id} cancelled")
            return True
    
    return False


def cmd_search(args):
    """Handle search command."""
    results = search_flights(args.origin, args.destination, args.date)
    if results:
        print(f"\n📋 Found {len(results)} flights: {args.origin} -> {args.destination}")
        for f in results:
            print(f"\n  ✈️  {f['airline']} | {f['id']}")
            print(f"      {f['departure']} -> {f['arrival']}")
            print(f"      💰 ${f['price']:.2f} | {f['seats']} seats available")
    else:
        print(f"\n❌ No flights found for {args.origin} -> {args.destination}")
        if args.date:
            print(f"   on {args.date}")
    return 0


def cmd_book(args):
    """Handle book command."""
    result = book_flight(args.flight_id, args.name, args.email)
    if result:
        print(f"\n✅ Booking Confirmed!")
        print(f"   Booking ID: {result['booking_id']}")
        print(f"   Flight: {result['airline']} {result['flight_id']}")
        print(f"   Route: {result['origin']} -> {result['destination']}")
        print(f"   Departure: {result['departure']}")
        print(f"   Passenger: {result['passenger_name']}")
        print(f"   Total: ${result['price']:.2f}")
        return 0
    else:
        print(f"\n❌ Booking failed. Check flight ID and availability.")
        return 1


def cmd_list(args):
    """Handle list command."""
    bookings = list_bookings(args.email)
    if bookings:
        print(f"\n📋 Your Bookings ({len(bookings)}):")
        for b in bookings:
            status_icon = "✅" if b["status"] == "confirmed" else "❌"
            print(f"\n  {status_icon} {b['booking_id']}")
            print(f"      {b['airline']} {b['flight_id']}: {b['origin']} -> {b['destination']}")
            print(f"      {b['departure']} | {b['passenger_name']}")
    else:
        msg = f"\n❌ No bookings found for {args.email}" if args.email else "\n❌ No bookings found"
        print(msg)
    return 0


def cmd_cancel(args):
    """Handle cancel command."""
    if cancel_booking(args.booking_id):
        print(f"\n✅ Booking {args.booking_id} cancelled successfully")
        return 0
    else:
        print(f"\n❌ Booking {args.booking_id} not found")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="✈️ Flight Booker Agent - Search and book flights",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s search --origin FRA --destination JFK
  %(prog)s search --origin FRA --destination JFK --date 2026-04-01
  %(prog)s book --flight-id FL001 --name "John Doe" --email john@example.com
  %(prog)s list --email john@example.com
  %(prog)s cancel --booking-id BK1234567890
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for flights")
    search_parser.add_argument("--origin", required=True, help="Origin airport code (e.g., FRA)")
    search_parser.add_argument("--destination", required=True, help="Destination airport code (e.g., JFK)")
    search_parser.add_argument("--date", help="Departure date (YYYY-MM-DD)")
    
    # Book command
    book_parser = subparsers.add_parser("book", help="Book a flight")
    book_parser.add_argument("--flight-id", required=True, help="Flight ID to book")
    book_parser.add_argument("--name", required=True, help="Passenger name")
    book_parser.add_argument("--email", required=True, help="Passenger email")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List bookings")
    list_parser.add_argument("--email", help="Filter by passenger email")
    
    # Cancel command
    cancel_parser = subparsers.add_parser("cancel", help="Cancel a booking")
    cancel_parser.add_argument("--booking-id", required=True, help="Booking ID to cancel")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    commands = {
        "search": cmd_search,
        "book": cmd_book,
        "list": cmd_list,
        "cancel": cmd_cancel
    }
    
    if args.command in commands:
        try:
            return commands[args.command](args)
        except Exception as e:
            logger.exception("Command failed")
            print(f"\n❌ Error: {e}")
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
