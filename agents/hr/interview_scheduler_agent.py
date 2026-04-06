#!/usr/bin/env python3
"""
Interview Scheduler Agent
Schedules and manages interview appointments between candidates and interviewers.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data/hr")
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "interview_scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

INTERVIEWS_FILE = DATA_DIR / "interviews.json"
INTERVIEWERS_FILE = DATA_DIR / "interviewers.json"
CANDIDATES_FILE = DATA_DIR / "candidates.json"


def load_json(path: Path, default: Any = None) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text())
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading {path}: {e}")
    return default if default is not None else {}


def save_json(path: Path, data: Any) -> bool:
    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        return True
    except IOError as e:
        logger.error(f"Error saving {path}: {e}")
        return False


def parse_datetime(dt_str: str) -> datetime:
    """Parse datetime from string, trying multiple formats."""
    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(dt_str.strip(), fmt)
        except ValueError:
            continue
    raise ValueError(f"Could not parse date: {dt_str}")


def format_datetime(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M")


def generate_time_slots(date: datetime, duration_min: int = 60) -> list[dict]:
    """Generate hourly time slots for a given date (9 AM - 5 PM)."""
    slots = []
    start_hour = 9
    end_hour = 17
    
    current = date.replace(hour=start_hour, minute=0, second=0, microsecond=0)
    end = date.replace(hour=end_hour, minute=0, second=0, microsecond=0)
    
    while current < end:
        slots.append({
            "start": current.isoformat(),
            "end": (current + timedelta(minutes=duration_min)).isoformat(),
            "available": True
        })
        current += timedelta(minutes=duration_min)
    
    return slots


def check_conflict(new_start: datetime, new_end: datetime, existing: list[dict]) -> bool:
    """Check if a time slot conflicts with existing interviews."""
    for interview in existing:
        if interview.get("status") in ["cancelled", "rejected"]:
            continue
        try:
            exist_start = parse_datetime(interview["scheduled_at"])
            exist_duration = interview.get("duration_min", 60)
            exist_end = exist_start + timedelta(minutes=exist_duration)
            
            if new_start < exist_end and new_end > exist_start:
                return True
        except (KeyError, ValueError):
            continue
    return False


def find_available_slot(candidates: list, interviewers: list, duration_min: int = 60) -> dict:
    """Find an available slot that works for all participants."""
    # Get date range: next 14 days
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    for day_offset in range(14):
        date = today + timedelta(days=day_offset)
        
        # Skip weekends
        if date.weekday() >= 5:
            continue
        
        # Generate slots for this day
        slots = generate_time_slots(date, duration_min)
        
        for slot in slots:
            slot_start = parse_datetime(slot["start"])
            slot_end = slot_start + timedelta(minutes=duration_min)
            
            # Check all calendars
            all_available = True
            for participant in candidates + interviewers:
                cal = participant.get("calendar", [])
                if check_conflict(slot_start, slot_end, cal):
                    all_available = False
                    break
            
            if all_available:
                return {
                    "date": date.strftime("%Y-%m-%d"),
                    "start_time": slot_start.strftime("%H:%M"),
                    "end_time": slot_end.strftime("%H:%M"),
                    "start_iso": slot_start.isoformat(),
                    "end_iso": slot_end.isoformat()
                }
    
    return None


def add_candidate(candidate_data: dict) -> bool:
    """Add a candidate to the database."""
    data = load_json(CANDIDATES_FILE, {"candidates": []})
    candidate_id = candidate_data.get("id", f"cand_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}")
    candidate_data["id"] = candidate_id
    candidate_data["created_at"] = datetime.utcnow().isoformat()
    candidate_data["calendar"] = candidate_data.get("calendar", [])
    data["candidates"].append(candidate_data)
    return save_json(CANDIDATES_FILE, data)


def add_interviewer(interviewer_data: dict) -> bool:
    """Add an interviewer to the database."""
    data = load_json(INTERVIEWERS_FILE, {"interviewers": []})
    interviewer_id = interviewer_data.get("id", f"inter_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}")
    interviewer_data["id"] = interviewer_id
    interviewer_data["created_at"] = datetime.utcnow().isoformat()
    interviewer_data["calendar"] = interviewer_data.get("calendar", [])
    data["interviewers"].append(interviewer_data)
    return save_json(INTERVIEWERS_FILE, data)


def schedule_interview(candidate_id: str, interviewer_ids: list, interview_type: str, 
                       duration_min: int = 60, notes: str = "") -> dict:
    """Schedule an interview between a candidate and interviewers."""
    candidates = load_json(CANDIDATES_FILE, {"candidates": []})["candidates"]
    interviewers = load_json(INTERVIEWERS_FILE, {"interviewers": []})["interviewers"]
    
    candidate = next((c for c in candidates if c.get("id") == candidate_id), None)
    if not candidate:
        logger.error(f"Candidate not found: {candidate_id}")
        return {"success": False, "error": f"Candidate not found: {candidate_id}"}
    
    selected_interviewers = [i for i in interviewers if i.get("id") in interviewer_ids]
    if not selected_interviewers:
        return {"success": False, "error": "No valid interviewers found"}
    
    # Find available slot
    slot = find_available_slot([candidate], selected_interviewers, duration_min)
    if not slot:
        return {"success": False, "error": "No available slots in the next 14 days"}
    
    # Create interview
    interview_id = f"int_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
    interview = {
        "id": interview_id,
        "candidate_id": candidate_id,
        "candidate_name": candidate.get("name", "Unknown"),
        "candidate_email": candidate.get("email", ""),
        "interviewer_ids": interviewer_ids,
        "interviewer_names": [i.get("name", "Unknown") for i in selected_interviewers],
        "interview_type": interview_type,
        "scheduled_at": slot["start_iso"],
        "duration_min": duration_min,
        "status": "scheduled",
        "notes": notes,
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Update calendars
    interviews = load_json(INTERVIEWS_FILE, {"interviews": []})
    interviews["interviews"].append(interview)
    save_json(INTERVIEWS_FILE, interviews)
    
    # Update candidate calendar
    candidate["calendar"] = candidate.get("calendar", [])
    candidate["calendar"].append(interview)
    save_json(CANDIDATES_FILE, {"candidates": candidates})
    
    # Update interviewer calendars
    for i, interviewer in enumerate(interviewers):
        if interviewer["id"] in interviewer_ids:
            interviewer["calendar"] = interviewer.get("calendar", [])
            interviewer["calendar"].append(interview)
    save_json(INTERVIEWERS_FILE, {"interviewers": interviewers})
    
    logger.info(f"Interview scheduled: {interview_id}")
    return {"success": True, "interview": interview, "slot": slot}


def cancel_interview(interview_id: str) -> bool:
    """Cancel an interview."""
    interviews = load_json(INTERVIEWS_FILE, {"interviews": []})["interviews"]
    
    for interview in interviews:
        if interview.get("id") == interview_id:
            interview["status"] = "cancelled"
            interview["cancelled_at"] = datetime.utcnow().isoformat()
            save_json(INTERVIEWS_FILE, {"interviews": interviews})
            
            # Remove from calendars
            candidates = load_json(CANDIDATES_FILE, {"candidates": []})["candidates"]
            for c in candidates:
                c["calendar"] = [i for i in c.get("calendar", []) if i.get("id") != interview_id]
            save_json(CANDIDATES_FILE, {"candidates": candidates})
            
            logger.info(f"Interview cancelled: {interview_id}")
            return True
    
    return False


def list_interviews(status: str = None, candidate_id: str = None) -> list[dict]:
    """List all interviews, optionally filtered."""
    interviews = load_json(INTERVIEWS_FILE, {"interviews": []})["interviews"]
    
    if status:
        interviews = [i for i in interviews if i.get("status") == status]
    if candidate_id:
        interviews = [i for i in interviews if i.get("candidate_id") == candidate_id]
    
    return sorted(interviews, key=lambda x: x.get("scheduled_at", ""))


def cmd_schedule(args):
    """Schedule a new interview."""
    if not args.candidate_id or not args.interviewers:
        print("Error: --candidate-id and --interviewers are required")
        sys.exit(1)
    
    interviewer_list = args.interviewers.split(",")
    duration = args.duration or 60
    
    result = schedule_interview(
        candidate_id=args.candidate_id,
        interviewer_ids=interviewer_list,
        interview_type=args.type or "general",
        duration_min=duration,
        notes=args.notes or ""
    )
    
    if result["success"]:
        print(f"\n✅ Interview scheduled successfully!")
        print(f"   ID: {result['interview']['id']}")
        print(f"   Date: {result['slot']['date']}")
        print(f"   Time: {result['slot']['start_time']} - {result['slot']['end_time']}")
        print(f"   Candidate: {result['interview']['candidate_name']}")
        print(f"   Interviewers: {', '.join(result['interview']['interviewer_names'])}")
        print(f"   Type: {result['interview']['interview_type']}")
    else:
        print(f"❌ Failed to schedule: {result.get('error')}")


def cmd_cancel(args):
    """Cancel an interview."""
    if cancel_interview(args.interview_id):
        print(f"✅ Interview {args.interview_id} cancelled")
    else:
        print(f"❌ Interview not found: {args.interview_id}")


def cmd_list(args):
    """List interviews."""
    interviews = list_interviews(status=args.status, candidate_id=args.candidate_id)
    
    if not interviews:
        print("No interviews found")
        return
    
    print(f"\n{'='*70}")
    print(f"INTERVIEWS: {len(interviews)}")
    if args.status:
        print(f"Status Filter: {args.status}")
    print(f"{'='*70}\n")
    
    for i in interviews:
        status_icon = {"scheduled": "📅", "completed": "✅", "cancelled": "❌", "no_show": "👻"}.get(i.get("status", ""), "❓")
        dt = parse_datetime(i["scheduled_at"])
        print(f"{status_icon} {i.get('id')}")
        print(f"   {dt.strftime('%Y-%m-%d %H:%M')} ({i.get('duration_min', 60)} min)")
        print(f"   Candidate: {i.get('candidate_name')} ({i.get('candidate_email')})")
        print(f"   Interviewers: {', '.join(i.get('interviewer_names', []))}")
        print(f"   Type: {i.get('interview_type', 'general')}")
        print(f"   Status: {i.get('status')}")
        if i.get("notes"):
            print(f"   Notes: {i['notes']}")
        print()


def cmd_add_candidate(args):
    """Add a candidate interactively."""
    print("\n--- Add Candidate ---")
    candidate = {}
    candidate["name"] = input("Candidate Name: ").strip()
    if not candidate["name"]:
        print("Name is required")
        return
    candidate["email"] = input("Email: ").strip()
    candidate["phone"] = input("Phone: ").strip()
    candidate["position"] = input("Position Applied: ").strip()
    candidate["notes"] = input("Notes: ").strip()
    candidate["calendar"] = []
    
    if add_candidate(candidate):
        print(f"✅ Candidate added successfully!")
    else:
        print("❌ Failed to add candidate")


def cmd_add_interviewer(args):
    """Add an interviewer interactively."""
    print("\n--- Add Interviewer ---")
    interviewer = {}
    interviewer["name"] = input("Interviewer Name: ").strip()
    if not interviewer["name"]:
        print("Name is required")
        return
    interviewer["email"] = input("Email: ").strip()
    interviewer["department"] = input("Department: ").strip()
    interviewer["role"] = input("Role/Title: ").strip()
    interviewer["calendar"] = []
    
    if add_interviewer(interviewer):
        print(f"✅ Interviewer added successfully!")
    else:
        print("❌ Failed to add interviewer")


def cmd_show_slots(args):
    """Show available time slots."""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    print(f"\n{'='*50}")
    print(f"AVAILABLE TIME SLOTS (Next 7 days)")
    print(f"{'='*50}\n")
    
    days_shown = 0
    for day_offset in range(7):
        date = today + timedelta(days=day_offset)
        if date.weekday() >= 5:
            continue
        
        slots = generate_time_slots(date, 60)
        print(f"📅 {date.strftime('%Y-%m-%d')} ({date.strftime('%A')})")
        for slot in slots:
            slot_dt = parse_datetime(slot["start"])
            print(f"   {slot_dt.strftime('%H:%M')} - {(slot_dt + timedelta(hours=1)).strftime('%H:%M')}")
        print()
        days_shown += 1
        
        if days_shown >= 5:
            break


def main():
    parser = argparse.ArgumentParser(
        description="Interview Scheduler Agent - Schedule and manage interviews",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --add-candidate
  %(prog)s --add-interviewer
  %(prog)s --schedule --candidate-id cand_001 --interviewers int_001,int_002
  %(prog)s --list
  %(prog)s --list --status scheduled
  %(prog)s --cancel --interview-id int_xxx
  %(prog)s --show-slots
        """
    )
    
    parser.add_argument("--schedule", action="store_true", help="Schedule a new interview")
    parser.add_argument("--candidate-id", type=str, help="Candidate ID")
    parser.add_argument("--interviewers", type=str, help="Comma-separated interviewer IDs")
    parser.add_argument("--type", type=str, help="Interview type (technical, hr, final)")
    parser.add_argument("--duration", type=int, help="Duration in minutes (default: 60)")
    parser.add_argument("--notes", type=str, help="Interview notes")
    
    parser.add_argument("--list", action="store_true", help="List all interviews")
    parser.add_argument("--status", type=str, choices=["scheduled", "completed", "cancelled", "no_show"],
                        help="Filter by status")
    parser.add_argument("--candidate-id-list", dest="candidate_id", type=str,
                        help="Filter by candidate ID")
    
    parser.add_argument("--cancel", action="store_true", help="Cancel an interview")
    parser.add_argument("--interview-id", type=str, help="Interview ID to cancel")
    
    parser.add_argument("--add-candidate", action="store_true", help="Add a new candidate")
    parser.add_argument("--add-interviewer", action="store_true", help="Add a new interviewer")
    
    parser.add_argument("--show-slots", action="store_true", help="Show available time slots")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.schedule:
        cmd_schedule(args)
    elif args.cancel:
        cmd_cancel(args)
    elif args.list:
        cmd_list(args)
    elif args.add_candidate:
        cmd_add_candidate(args)
    elif args.add_interviewer:
        cmd_add_interviewer(args)
    elif args.show_slots:
        cmd_show_slots(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
