#!/usr/bin/env python3
"""
Itinerary Planner Agent - Plan complete travel itineraries
Part of the Travel Agent Suite
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict

# Setup
BASE_DIR = Path(__file__).parent.parent.parent.parent
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data" / "travel"
SCRIPT_NAME = "itinerary_planner_agent"

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

DATA_FILE = DATA_DIR / "itineraries.json"
ACTIVITIES_FILE = DATA_DIR / "activities.json"


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


def generate_sample_activities() -> list:
    """Generate sample activities for different destinations."""
    activities = load_data(ACTIVITIES_FILE, {"activities": []})
    if not activities.get("activities"):
        activities["activities"] = [
            # New York
            {"id": "ACT001", "name": "Statue of Liberty Tour", "city": "New York", "country": "USA",
             "duration_hours": 4, "price": 25.00, "category": "sightseeing"},
            {"id": "ACT002", "name": "Central Park Walking Tour", "city": "New York", "country": "USA",
             "duration_hours": 2, "price": 0.00, "category": "nature"},
            {"id": "ACT003", "name": "Broadway Show", "city": "New York", "country": "USA",
             "duration_hours": 3, "price": 150.00, "category": "entertainment"},
            {"id": "ACT004", "name": "Metropolitan Museum of Art", "city": "New York", "country": "USA",
             "duration_hours": 3, "price": 25.00, "category": "culture"},
            # Miami
            {"id": "ACT005", "name": "South Beach Day Pass", "city": "Miami", "country": "USA",
             "duration_hours": 6, "price": 30.00, "category": "nature"},
            {"id": "ACT006", "name": "Everglades Airboat Tour", "city": "Miami", "country": "USA",
             "duration_hours": 4, "price": 60.00, "category": "adventure"},
            # Paris
            {"id": "ACT007", "name": "Eiffel Tower Visit", "city": "Paris", "country": "France",
             "duration_hours": 3, "price": 28.00, "category": "sightseeing"},
            {"id": "ACT008", "name": "Louvre Museum", "city": "Paris", "country": "France",
             "duration_hours": 4, "price": 17.00, "category": "culture"},
            {"id": "ACT009", "name": "Seine River Cruise", "city": "Paris", "country": "France",
             "duration_hours": 2, "price": 15.00, "category": "entertainment"},
            # London
            {"id": "ACT010", "name": "Tower of London", "city": "London", "country": "UK",
             "duration_hours": 3, "price": 30.00, "category": "culture"},
            {"id": "ACT011", "name": "British Museum", "city": "London", "country": "UK",
             "duration_hours": 3, "price": 0.00, "category": "culture"},
            {"id": "ACT012", "name": "West End Theatre", "city": "London", "country": "UK",
             "duration_hours": 3, "price": 80.00, "category": "entertainment"},
        ]
        save_data(ACTIVITIES_FILE, activities)
    return activities.get("activities", [])


def get_activities_for_destination(city: str, country: Optional[str] = None, 
                                   category: Optional[str] = None) -> list:
    """Get available activities for a destination."""
    all_activities = generate_sample_activities()
    results = []
    
    for act in all_activities:
        if act["city"].lower() == city.lower():
            if country and act["country"].lower() != country.lower():
                continue
            if category and act["category"].lower() != category.lower():
                continue
            results.append(act)
    
    return results


def plan_itinerary(trip_name: str, destination: str, country: str,
                   start_date: str, end_date: str,
                   selected_activities: List[str] = None,
                   trip_type: str = "mixed") -> dict:
    """Plan a complete trip itinerary."""
    logger.info(f"Planning itinerary: {trip_name} to {destination}")
    
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        total_days = (end - start).days
        if total_days <= 0:
            raise ValueError("End date must be after start date")
    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        return None
    
    # Get activities
    all_activities = get_activities_for_destination(destination, country)
    
    # If no specific activities selected, auto-select based on trip type
    if not selected_activities:
        selected_activities = [a["id"] for a in all_activities[:5]]
    
    # Build daily plan
    daily_plan = []
    current_date = start
    
    for day_num in range(total_days):
        day_activities = []
        day_start = current_date + timedelta(hours=9)  # Start activities at 9 AM
        
        for act_id in selected_activities:
            act = next((a for a in all_activities if a["id"] == act_id), None)
            if act:
                act_start = day_start + timedelta(hours=len(day_activities) * act["duration_hours"])
                if act_start.hour + act["duration_hours"] <= 21:  # Before 9 PM
                    day_activities.append({
                        "activity_id": act["id"],
                        "name": act["name"],
                        "start_time": act_start.strftime("%H:%M"),
                        "duration_hours": act["duration_hours"],
                        "price": act["price"],
                        "category": act["category"]
                    })
        
        day_plan = {
            "day": day_num + 1,
            "date": current_date.strftime("%Y-%m-%d"),
            "day_of_week": current_date.strftime("%A"),
            "activities": day_activities,
            "daily_cost": sum(a["price"] for a in day_activities)
        }
        daily_plan.append(day_plan)
        current_date += timedelta(days=1)
    
    # Calculate totals
    total_cost = sum(day["daily_cost"] for day in daily_plan)
    
    # Create itinerary
    itinerary = {
        "itinerary_id": f"ITN{int(datetime.now().timestamp())}",
        "name": trip_name,
        "destination": destination,
        "country": country,
        "start_date": start_date,
        "end_date": end_date,
        "total_days": total_days,
        "trip_type": trip_type,
        "daily_plan": daily_plan,
        "total_estimated_cost": round(total_cost, 2),
        "created_at": datetime.now().isoformat()
    }
    
    # Save itinerary
    itineraries_data = load_data(DATA_FILE, {"itineraries": []})
    itineraries_data["itineraries"].append(itinerary)
    save_data(DATA_FILE, itineraries_data)
    
    logger.info(f"Itinerary created: {itinerary['itinerary_id']}")
    return itinerary


def list_itineraries(destination: Optional[str] = None) -> list:
    """List all itineraries, optionally filtered by destination."""
    data = load_data(DATA_FILE, {"itineraries": []})
    itineraries = data.get("itineraries", [])
    
    if destination:
        itineraries = [i for i in itineraries 
                       if i.get("destination", "").lower() == destination.lower()]
    
    return itineraries


def get_itinerary(itinerary_id: str) -> Optional[dict]:
    """Get a specific itinerary by ID."""
    data = load_data(DATA_FILE, {"itineraries": []})
    for itn in data.get("itineraries", []):
        if itn["itinerary_id"] == itinerary_id:
            return itn
    return None


def delete_itinerary(itinerary_id: str) -> bool:
    """Delete an itinerary."""
    data = load_data(DATA_FILE, {"itineraries": []})
    itineraries = data.get("itineraries", [])
    
    for i, itn in enumerate(itineraries):
        if itn["itinerary_id"] == itinerary_id:
            itineraries.pop(i)
            save_data(DATA_FILE, {"itineraries": itineraries})
            logger.info(f"Itinerary {itinerary_id} deleted")
            return True
    
    return False


def format_itinerary(itinerary: dict, detailed: bool = False) -> str:
    """Format itinerary for display."""
    output = []
    output.append(f"\n🗓️  {itinerary['name']}")
    output.append(f"   📍 {itinerary['destination']}, {itinerary['country']}")
    output.append(f"   📅 {itinerary['start_date']} to {itinerary['end_date']} ({itinerary['total_days']} days)")
    output.append(f"   💰 Estimated Cost: ${itinerary['total_estimated_cost']:.2f}")
    
    if detailed:
        for day in itinerary.get("daily_plan", []):
            output.append(f"\n   ─── Day {day['day']} ({day['day_of_week']}, {day['date']}) ───")
            if day['activities']:
                for act in day['activities']:
                    output.append(f"      🕐 {act['start_time']} | {act['name']} ({act['duration_hours']}h)")
                    if act['price'] > 0:
                        output.append(f"         💰 ${act['price']:.2f}")
            else:
                output.append(f"      🌴 Free day")
            output.append(f"      📊 Day total: ${day['daily_cost']:.2f}")
    
    return "\n".join(output)


def cmd_plan(args):
    """Handle plan command."""
    activities = args.activities.split(",") if args.activities else None
    result = plan_itinerary(
        args.name, args.destination, args.country,
        args.start_date, args.end_date,
        selected_activities=activities,
        trip_type=args.trip_type
    )
    if result:
        print(format_itinerary(result, detailed=True))
        print(f"\n✅ Itinerary saved with ID: {result['itinerary_id']}")
        return 0
    else:
        print("\n❌ Failed to create itinerary. Check dates and destination.")
        return 1


def cmd_list(args):
    """Handle list command."""
    itineraries = list_itineraries(args.destination)
    if itineraries:
        print(f"\n📋 Your Itineraries ({len(itineraries)}):")
        for itn in itineraries:
            print(format_itinerary(itn))
    else:
        msg = f"\n❌ No itineraries found for {args.destination}" if args.destination else "\n❌ No itineraries found"
        print(msg)
    return 0


def cmd_show(args):
    """Handle show command."""
    itinerary = get_itinerary(args.itinerary_id)
    if itinerary:
        print(format_itinerary(itinerary, detailed=True))
        return 0
    else:
        print(f"\n❌ Itinerary {args.itinerary_id} not found")
        return 1


def cmd_activities(args):
    """Handle activities command."""
    activities = get_activities_for_destination(args.city, args.country, args.category)
    if activities:
        print(f"\n🎯 Available Activities in {args.city}:")
        for act in activities:
            price_str = f"${act['price']:.2f}" if act['price'] > 0 else "FREE"
            print(f"\n  📌 {act['name']}")
            print(f"      Category: {act['category']} | Duration: {act['duration_hours']}h | {price_str}")
    else:
        print(f"\n❌ No activities found for {args.city}")
    return 0


def cmd_delete(args):
    """Handle delete command."""
    if delete_itinerary(args.itinerary_id):
        print(f"\n✅ Itinerary {args.itinerary_id} deleted")
        return 0
    else:
        print(f"\n❌ Itinerary {args.itinerary_id} not found")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="🗓️ Itinerary Planner Agent - Plan complete travel itineraries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s plan --name "NYC Trip" --destination "New York" --country "USA" --start-date 2026-04-01 --end-date 2026-04-05
  %(prog)s plan --name "Paris Week" --destination "Paris" --country "France" --start-date 2026-05-01 --end-date 2026-05-07 --trip-type culture
  %(prog)s list
  %(prog)s list --destination "London"
  %(prog)s show --itinerary-id ITN1234567890
  %(prog)s activities --city "New York"
  %(prog)s activities --city "Paris" --category sightseeing
  %(prog)s delete --itinerary-id ITN1234567890
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Plan command
    plan_parser = subparsers.add_parser("plan", help="Create new itinerary")
    plan_parser.add_argument("--name", required=True, help="Trip name")
    plan_parser.add_argument("--destination", required=True, help="Destination city")
    plan_parser.add_argument("--country", required=True, help="Country")
    plan_parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    plan_parser.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    plan_parser.add_argument("--trip-type", default="mixed", choices=["sightseeing", "culture", "adventure", "mixed", "relaxation"],
                            help="Type of trip")
    plan_parser.add_argument("--activities", help="Comma-separated activity IDs")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List itineraries")
    list_parser.add_argument("--destination", help="Filter by destination")
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Show itinerary details")
    show_parser.add_argument("--itinerary-id", required=True, help="Itinerary ID")
    
    # Activities command
    act_parser = subparsers.add_parser("activities", help="List available activities")
    act_parser.add_argument("--city", required=True, help="City name")
    act_parser.add_argument("--country", help="Country name")
    act_parser.add_argument("--category", help="Activity category")
    
    # Delete command
    del_parser = subparsers.add_parser("delete", help="Delete an itinerary")
    del_parser.add_argument("--itinerary-id", required=True, help="Itinerary ID to delete")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    commands = {
        "plan": cmd_plan,
        "list": cmd_list,
        "show": cmd_show,
        "activities": cmd_activities,
        "delete": cmd_delete
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
