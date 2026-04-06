#!/usr/bin/env python3
"""
Hotel Booker Agent - Search and book hotels
Part of the Travel Agent Suite
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Setup
BASE_DIR = Path(__file__).parent.parent.parent.parent
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data" / "travel"
SCRIPT_NAME = "hotel_booker_agent"

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

DATA_FILE = DATA_DIR / "hotels.json"
BOOKINGS_FILE = DATA_DIR / "hotel_bookings.json"


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


def generate_sample_hotels() -> list:
    """Generate sample hotel data."""
    hotels = load_data(DATA_FILE)
    if not hotels.get("sample_hotels"):
        hotels["sample_hotels"] = [
            {"id": "HTL001", "name": "Grand Plaza Hotel", "city": "New York", "country": "USA",
             "stars": 5, "price_per_night": 299.99, "rooms_available": 12,
             "amenities": ["WiFi", "Pool", "Spa", "Gym", "Restaurant"]},
            {"id": "HTL002", "name": "Comfort Inn Central", "city": "New York", "country": "USA",
             "stars": 3, "price_per_night": 129.99, "rooms_available": 25,
             "amenities": ["WiFi", "Breakfast", "Parking"]},
            {"id": "HTL003", "name": "Budget Stay", "city": "New York", "country": "USA",
             "stars": 2, "price_per_night": 69.99, "rooms_available": 8,
             "amenities": ["WiFi"]},
            {"id": "HTL004", "name": "Seaside Resort", "city": "Miami", "country": "USA",
             "stars": 4, "price_per_night": 189.99, "rooms_available": 5,
             "amenities": ["WiFi", "Pool", "Beach Access", "Bar"]},
            {"id": "HTL005", "name": "Alpine Lodge", "city": "Zurich", "country": "Switzerland",
             "stars": 4, "price_per_night": 249.99, "rooms_available": 15,
             "amenities": ["WiFi", "Ski Storage", "Fireplace", "Restaurant"]},
        ]
        save_data(DATA_FILE, hotels)
    return hotels.get("sample_hotels", [])


def search_hotels(city: str, country: Optional[str] = None, min_stars: int = 0) -> list:
    """Search for available hotels."""
    logger.info(f"Searching hotels in {city}, {country or 'any'}")
    all_hotels = generate_sample_hotels()
    
    results = []
    for hotel in all_hotels:
        if hotel["city"].lower() == city.lower():
            if country and hotel["country"].lower() != country.lower():
                continue
            if hotel["stars"] >= min_stars and hotel["rooms_available"] > 0:
                results.append(hotel)
    
    return sorted(results, key=lambda x: x["price_per_night"])


def book_hotel(hotel_id: str, guest_name: str, guest_email: str,
               check_in: str, check_out: str, guests: int = 1) -> Optional[dict]:
    """Book a hotel room."""
    logger.info(f"Booking hotel {hotel_id} for {guest_name}")
    all_hotels = load_data(DATA_FILE)
    hotels = all_hotels.get("sample_hotels", [])
    
    hotel = None
    for h in hotels:
        if h["id"] == hotel_id:
            hotel = h
            break
    
    if not hotel:
        logger.error(f"Hotel {hotel_id} not found")
        return None
    
    if hotel["rooms_available"] <= 0:
        logger.error(f"No rooms available at {hotel['name']}")
        return None
    
    # Calculate nights
    try:
        check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
        nights = (check_out_date - check_in_date).days
        if nights <= 0:
            logger.error("Check-out must be after check-in")
            return None
    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        return None
    
    total_price = hotel["price_per_night"] * nights
    
    # Create booking
    booking = {
        "booking_id": f"HBK{int(datetime.now().timestamp())}",
        "hotel_id": hotel_id,
        "hotel_name": hotel["name"],
        "guest_name": guest_name,
        "guest_email": guest_email,
        "city": hotel["city"],
        "country": hotel["country"],
        "check_in": check_in,
        "check_out": check_out,
        "nights": nights,
        "guests": guests,
        "price_per_night": hotel["price_per_night"],
        "total_price": round(total_price, 2),
        "status": "confirmed",
        "booked_at": datetime.now().isoformat()
    }
    
    # Load bookings
    bookings_data = load_data(BOOKINGS_FILE, {"bookings": []})
    bookings_data["bookings"].append(booking)
    save_data(BOOKINGS_FILE, bookings_data)
    
    # Decrease available rooms
    for h in hotels:
        if h["id"] == hotel_id:
            h["rooms_available"] -= 1
            break
    save_data(DATA_FILE, all_hotels)
    
    logger.info(f"Booking confirmed: {booking['booking_id']}")
    return booking


def list_bookings(email: Optional[str] = None) -> list:
    """List all bookings, optionally filtered by email."""
    bookings_data = load_data(BOOKINGS_FILE, {"bookings": []})
    bookings = bookings_data.get("bookings", [])
    
    if email:
        bookings = [b for b in bookings if b.get("guest_email", "").lower() == email.lower()]
    
    return bookings


def cancel_booking(booking_id: str) -> bool:
    """Cancel a booking and restore room."""
    logger.info(f"Cancelling booking {booking_id}")
    bookings_data = load_data(BOOKINGS_FILE, {"bookings": []})
    hotels_data = load_data(DATA_FILE)
    
    bookings = bookings_data.get("bookings", [])
    for i, booking in enumerate(bookings):
        if booking["booking_id"] == booking_id:
            booking["status"] = "cancelled"
            booking["cancelled_at"] = datetime.now().isoformat()
            
            # Restore room
            hotels = hotels_data.get("sample_hotels", [])
            for h in hotels:
                if h["id"] == booking["hotel_id"]:
                    h["rooms_available"] += 1
                    break
            
            save_data(BOOKINGS_FILE, bookings_data)
            save_data(DATA_FILE, hotels_data)
            logger.info(f"Booking {booking_id} cancelled")
            return True
    
    return False


def cmd_search(args):
    """Handle search command."""
    results = search_hotels(args.city, args.country, args.min_stars)
    if results:
        print(f"\n🏨 Found {len(results)} hotels in {args.city}:")
        for h in results:
            stars = "⭐" * h["stars"]
            print(f"\n  🏨 {h['name']} {stars}")
            print(f"      {h['country']} | {h['rooms_available']} rooms available")
            print(f"      💰 ${h['price_per_night']:.2f}/night")
            print(f"      Amenities: {', '.join(h['amenities'])}")
    else:
        print(f"\n❌ No hotels found in {args.city}")
    return 0


def cmd_book(args):
    """Handle book command."""
    result = book_hotel(args.hotel_id, args.name, args.email, args.check_in, args.check_out, args.guests)
    if result:
        print(f"\n✅ Booking Confirmed!")
        print(f"   Booking ID: {result['booking_id']}")
        print(f"   Hotel: {result['hotel_name']}")
        print(f"   Location: {result['city']}, {result['country']}")
        print(f"   Check-in: {result['check_in']}")
        print(f"   Check-out: {result['check_out']} ({result['nights']} nights)")
        print(f"   Guest: {result['guest_name']} ({result['guests']} guest(s))")
        print(f"   Total: ${result['total_price']:.2f}")
        return 0
    else:
        print(f"\n❌ Booking failed. Check hotel ID and availability.")
        return 1


def cmd_list(args):
    """Handle list command."""
    bookings = list_bookings(args.email)
    if bookings:
        print(f"\n📋 Your Hotel Bookings ({len(bookings)}):")
        for b in bookings:
            status_icon = "✅" if b["status"] == "confirmed" else "❌"
            print(f"\n  {status_icon} {b['booking_id']}")
            print(f"      {b['hotel_name']} - {b['city']}")
            print(f"      {b['check_in']} to {b['check_out']} ({b['nights']} nights)")
            print(f"      {b['guest_name']} | ${b['total_price']:.2f}")
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
        description="🏨 Hotel Booker Agent - Search and book hotels",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s search --city "New York"
  %(prog)s search --city "New York" --min-stars 4
  %(prog)s book --hotel-id HTL001 --name "Jane Doe" --email jane@example.com --check-in 2026-04-01 --check-out 2026-04-05
  %(prog)s list --email jane@example.com
  %(prog)s cancel --booking-id HBK1234567890
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for hotels")
    search_parser.add_argument("--city", required=True, help="City name")
    search_parser.add_argument("--country", help="Country name")
    search_parser.add_argument("--min-stars", type=int, default=0, help="Minimum star rating")
    
    # Book command
    book_parser = subparsers.add_parser("book", help="Book a hotel")
    book_parser.add_argument("--hotel-id", required=True, help="Hotel ID to book")
    book_parser.add_argument("--name", required=True, help="Guest name")
    book_parser.add_argument("--email", required=True, help="Guest email")
    book_parser.add_argument("--check-in", required=True, help="Check-in date (YYYY-MM-DD)")
    book_parser.add_argument("--check-out", required=True, help="Check-out date (YYYY-MM-DD)")
    book_parser.add_argument("--guests", type=int, default=1, help="Number of guests")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List bookings")
    list_parser.add_argument("--email", help="Filter by guest email")
    
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
