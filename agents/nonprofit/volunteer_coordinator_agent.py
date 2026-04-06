#!/usr/bin/env python3
"""
Volunteer Coordinator Agent - Nonprofit Sector
Manages volunteer recruitment, scheduling, tracking, and communication.
"""

import argparse
import json
import logging
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List

LOG_DIR = Path(__file__).parent.parent.parent / "logs" / "nonprofit"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_DIR / "volunteer_coordinator.log"), logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("VolunteerCoordinatorAgent")


@dataclass
class Volunteer:
    id: str; name: str; email: str; phone: str = ""; skills: List[str] = None
    availability: str = ""; hours_committed: float = 0.0; hours_completed: float = 0.0
    start_date: str = ""; status: str = "active"; background_check: bool = False
    emergency_contact: str = ""; notes: str = ""; tags: List[str] = None
    created_at: str = ""; updated_at: str = ""

    def __post_init__(self):
        if self.skills is None: self.skills = []
        if self.tags is None: self.tags = []
        if not self.start_date: self.start_date = datetime.now().date().isoformat()
        if not self.created_at: self.created_at = datetime.now().isoformat()
        if not self.updated_at: self.updated_at = datetime.now().isoformat()


@dataclass
class Shift:
    id: str; volunteer_id: str; title: str; date: str; start_time: str; end_time: str
    location: str = ""; role: str = ""; status: str = "scheduled"
    hours_logged: float = 0.0; notes: str = ""; feedback: str = ""


@dataclass
class Event:
    id: str; name: str; date: str; description: str = ""; location: str = ""
    required_volunteers: int = 0; shifts: List[dict] = None; volunteer_ids: List[str] = None
    status: str = "planning"; notes: str = ""

    def __post_init__(self):
        if self.shifts is None: self.shifts = []
        if self.volunteer_ids is None: self.volunteer_ids = []


class VolunteerCoordinator:
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent / "data" / "nonprofit"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.volunteers_file = self.data_dir / "volunteers.json"
        self.shifts_file = self.data_dir / "volunteer_shifts.json"
        self.events_file = self.data_dir / "volunteer_events.json"
        self.volunteers = self._load_json(self.volunteers_file, Volunteer)
        self.shifts = self._load_json(self.shifts_file, Shift)
        self.events = self._load_json(self.events_file, Event)

    def _load_json(self, filepath: Path, cls):
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    return {item['id']: cls(**item) for item in data}
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Error loading {filepath}: {e}")
        return {}

    def _save_json(self, filepath: Path, data: dict):
        try:
            with open(filepath, 'w') as f:
                json.dump([asdict(item) for item in data.values()], f, indent=2)
        except IOError as e:
            logger.error(f"Error saving {filepath}: {e}")

    def _save_volunteers(self): self._save_json(self.volunteers_file, self.volunteers)
    def _save_shifts(self): self._save_json(self.shifts_file, self.shifts)
    def _save_events(self): self._save_json(self.events_file, self.events)
    def generate_id(self, prefix: str) -> str: return f"{prefix}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def add_volunteer(self, name: str, email: str, phone: str = "", skills: List[str] = None,
                      availability: str = "", notes: str = "", tags: List[str] = None,
                      background_check: bool = False, emergency_contact: str = "") -> Volunteer:
        for v in self.volunteers.values():
            if v.email.lower() == email.lower(): return v
        volunteer = Volunteer(id=self.generate_id("vol"), name=name, email=email, phone=phone,
            skills=skills or [], availability=availability, notes=notes, tags=tags or [],
            background_check=background_check, emergency_contact=emergency_contact)
        self.volunteers[volunteer.id] = volunteer
        self._save_volunteers()
        logger.info(f"Added volunteer: {name}")
        return volunteer

    def get_volunteer(self, volunteer_id: str) -> Optional[Volunteer]: return self.volunteers.get(volunteer_id)
    def find_volunteer_by_email(self, email: str) -> Optional[Volunteer]:
        for v in self.volunteers.values():
            if v.email.lower() == email.lower(): return v
        return None

    def list_volunteers(self, status: str = None, skill: str = None) -> List[Volunteer]:
        result = list(self.volunteers.values())
        if status: result = [v for v in result if v.status == status]
        if skill: result = [v for v in result if skill.lower() in [s.lower() for s in v.skills]]
        result.sort(key=lambda x: x.name.lower())
        return result

    def update_volunteer(self, volunteer_id: str, **kwargs) -> Optional[Volunteer]:
        if volunteer_id not in self.volunteers: return None
        volunteer = self.volunteers[volunteer_id]
        for key, value in kwargs.items():
            if hasattr(volunteer, key) and key not in ['id', 'hours_completed']: setattr(volunteer, key, value)
        volunteer.updated_at = datetime.now().isoformat()
        self._save_volunteers()
        return volunteer

    def delete_volunteer(self, volunteer_id: str) -> bool:
        if volunteer_id not in self.volunteers: return False
        self.shifts = {k: v for k, v in self.shifts.items() if v.volunteer_id != volunteer_id}
        del self.volunteers[volunteer_id]
        self._save_volunteers(); self._save_shifts()
        return True

    def create_shift(self, volunteer_id: str, title: str, date: str, start_time: str,
                     end_time: str, location: str = "", role: str = "", notes: str = "") -> Optional[Shift]:
        if volunteer_id not in self.volunteers: return None
        shift = Shift(id=self.generate_id("shift"), volunteer_id=volunteer_id, title=title, date=date,
            start_time=start_time, end_time=end_time, location=location, role=role, notes=notes)
        self.shifts[shift.id] = shift
        self._save_shifts()
        logger.info(f"Created shift: {title} for {date}")
        return shift

    def complete_shift(self, shift_id: str, hours_logged: float = None, feedback: str = "") -> Optional[Shift]:
        if shift_id not in self.shifts: return None
        shift = self.shifts[shift_id]; shift.status = "completed"
        if hours_logged: shift.hours_logged = hours_logged
        if feedback: shift.feedback = feedback
        volunteer = self.volunteers.get(shift.volunteer_id)
        if volunteer: volunteer.hours_completed += shift.hours_logged
        self._save_shifts(); self._save_volunteers()
        return shift

    def cancel_shift(self, shift_id: str) -> Optional[Shift]:
        if shift_id not in self.shifts: return None
        self.shifts[shift_id].status = "cancelled"
        self._save_shifts()
        return self.shifts[shift_id]

    def get_volunteer_shifts(self, volunteer_id: str, status: str = None) -> List[Shift]:
        shifts = [s for s in self.shifts.values() if s.volunteer_id == volunteer_id]
        if status: shifts = [s for s in shifts if s.status == status]
        return sorted(shifts, key=lambda x: x.date)

    def get_upcoming_shifts(self, days: int = 7) -> List[tuple]:
        upcoming = []; cutoff = datetime.now() + timedelta(days=days)
        for shift in self.shifts.values():
            if shift.status != "scheduled": continue
            try:
                shift_date = datetime.fromisoformat(shift.date)
                if datetime.now() <= shift_date <= cutoff:
                    volunteer = self.volunteers.get(shift.volunteer_id)
                    upcoming.append((shift, volunteer.name if volunteer else "Unknown"))
            except ValueError: continue
        upcoming.sort(key=lambda x: x[0].date)
        return upcoming

    def create_event(self, name: str, date: str, description: str = "", location: str = "",
                     required_volunteers: int = 0, shifts: List[dict] = None, notes: str = "") -> Event:
        event = Event(id=self.generate_id("evt"), name=name, date=date, description=description,
            location=location, required_volunteers=required_volunteers, shifts=shifts or [], notes=notes)
        self.events[event.id] = event
        self._save_events()
        logger.info(f"Created event: {name}")
        return event

    def assign_volunteer_to_event(self, event_id: str, volunteer_id: str) -> bool:
        if event_id not in self.events or volunteer_id not in self.volunteers: return False
        event = self.events[event_id]
        if volunteer_id not in event.volunteer_ids: event.volunteer_ids.append(volunteer_id)
        self._save_events()
        return True

    def get_event_volunteers(self, event_id: str) -> List[Volunteer]:
        if event_id not in self.events: return []
        return [self.volunteers[vid] for vid in self.events[event_id].volunteer_ids if vid in self.volunteers]

    def list_events(self, status: str = None) -> List[Event]:
        events = list(self.events.values())
        if status: events = [e for e in events if e.status == status]
        events.sort(key=lambda x: x.date)
        return events

    def get_statistics(self) -> dict:
        active = len([v for v in self.volunteers.values() if v.status == "active"])
        total_hours = sum(v.hours_completed for v in self.volunteers.values())
        upcoming = self.get_upcoming_shifts(30)
        upcoming_events = [e for e in self.events.values() if e.status in ["planning", "open"]]
        return {
            "total_volunteers": len(self.volunteers), "active_volunteers": active,
            "inactive_volunteers": len(self.volunteers) - active,
            "total_hours_donated": total_hours,
            "background_checks_complete": len([v for v in self.volunteers.values() if v.background_check]),
            "upcoming_shifts": len(upcoming), "upcoming_events": len(upcoming_events),
            "total_events": len(self.events)
        }

    def generate_report(self, output_file: Path = None) -> str:
        stats = self.get_statistics()
        lines = ["=" * 60, "VOLUNTEER COORDINATION REPORT",
                 f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", "=" * 60, "",
                 "SUMMARY", "-" * 50,
                 f"Total Volunteers: {stats['total_volunteers']}",
                 f"Active: {stats['active_volunteers']}",
                 f"Inactive: {stats['inactive_volunteers']}",
                 f"Total Hours Donated: {stats['total_hours_donated']:.1f}",
                 f"Background Checks: {stats['background_checks_complete']}",
                 f"Upcoming Shifts (30 days): {stats['upcoming_shifts']}",
                 f"Upcoming Events: {stats['upcoming_events']}", "", "TOP VOLUNTEERS", "-" * 50]
        top = sorted(self.volunteers.values(), key=lambda v: v.hours_completed, reverse=True)[:5]
        for v in top:
            lines.append(f"{v.name}: {v.hours_completed:.1f} hours | {v.availability or 'N/A'}")
        text = "\n".join(lines)
        if output_file: output_file.write_text(text)
        return text


def main():
    parser = argparse.ArgumentParser(description="Volunteer Coordinator Agent - Manage volunteers and schedules")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    add_vol = subparsers.add_parser("add-volunteer", help="Add volunteer")
    add_vol.add_argument("--name", required=True); add_vol.add_argument("--email", required=True)
    add_vol.add_argument("--phone", default=""); add_vol.add_argument("--skills", nargs="*")
    add_vol.add_argument("--availability", default=""); add_vol.add_argument("--notes", default="")
    add_vol.add_argument("--tags", nargs="*"); add_vol.add_argument("--background-check", action="store_true")
    add_vol.add_argument("--emergency-contact", default="")

    list_vol = subparsers.add_parser("list-volunteers", help="List volunteers")
    list_vol.add_argument("--status"); list_vol.add_argument("--skill")

    get_vol = subparsers.add_parser("get-volunteer", help="Get volunteer details")
    get_vol.add_argument("--volunteer-id", required=True)

    update_vol = subparsers.add_parser("update-volunteer", help="Update volunteer")
    update_vol.add_argument("--volunteer-id", required=True)
    update_vol.add_argument("--name"); update_vol.add_argument("--phone")
    update_vol.add_argument("--availability"); update_vol.add_argument("--status")
    update_vol.add_argument("--notes"); update_vol.add_argument("--tags", nargs="*")

    delete_vol = subparsers.add_parser("delete-volunteer", help="Delete volunteer")
    delete_vol.add_argument("--volunteer-id", required=True)

    add_shift = subparsers.add_parser("add-shift", help="Create shift")
    add_shift.add_argument("--volunteer-id", required=True); add_shift.add_argument("--title", required=True)
    add_shift.add_argument("--date", required=True); add_shift.add_argument("--start-time", required=True)
    add_shift.add_argument("--end-time", required=True)
    add_shift.add_argument("--location", default=""); add_shift.add_argument("--role", default="")
    add_shift.add_argument("--notes", default="")

    complete = subparsers.add_parser("complete-shift", help="Complete shift")
    complete.add_argument("--shift-id", required=True)
    complete.add_argument("--hours", type=float, default=0); complete.add_argument("--feedback", default="")

    cancel_shift = subparsers.add_parser("cancel-shift", help="Cancel shift")
    cancel_shift.add_argument("--shift-id", required=True)

    shifts = subparsers.add_parser("shifts", help="Get volunteer shifts")
    shifts.add_argument("--volunteer-id", required=True); shifts.add_argument("--status")

    upcoming = subparsers.add_parser("upcoming", help="Show upcoming shifts")
    upcoming.add_argument("--days", type=int, default=7)

    add_evt = subparsers.add_parser("create-event", help="Create event")
    add_evt.add_argument("--name", required=True); add_evt.add_argument("--date", required=True)
    add_evt.add_argument("--description", default=""); add_evt.add_argument("--location", default="")
    add_evt.add_argument("--required-volunteers", type=int, default=0); add_evt.add_argument("--notes", default="")

    assign = subparsers.add_parser("assign-volunteer", help="Assign volunteer to event")
    assign.add_argument("--event-id", required=True); assign.add_argument("--volunteer-id", required=True)

    list_evts = subparsers.add_parser("list-events", help="List events")
    list_evts.add_argument("--status")

    evt_vol = subparsers.add_parser("event-volunteers", help="Get event volunteers")
    evt_vol.add_argument("--event-id", required=True)

    stats = subparsers.add_parser("stats", help="Get statistics")
    report = subparsers.add_parser("report", help="Generate report")
    report.add_argument("--output", type=Path)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    coord = VolunteerCoordinator()
    try:
        if args.command == "add-volunteer":
            v = coord.add_volunteer(args.name, args.email, args.phone, args.skills,
                args.availability, args.notes, args.tags, args.background_check, args.emergency_contact)
            print(f"✓ Volunteer added: {v.id}"); print(f"  {v.name} | {v.email}")

        elif args.command == "list-volunteers":
            vols = coord.list_volunteers(args.status, args.skill)
            if not vols: print("No volunteers found.")
            else:
                print(f"\n{'Name':<25} {'Email':<30} {'Hours':<8} {'Status':<10} {'Skills'}")
                print("-" * 90)
                for v in vols:
                    print(f"{v.name:<25} {v.email:<30} {v.hours_completed:<8.1f} {v.status:<10} {', '.join(v.skills[:3]) or 'N/A'}")

        elif args.command == "get-volunteer":
            v = coord.get_volunteer(args.volunteer_id)
            if not v: print(f"✗ Volunteer not found"); sys.exit(1)
            print(f"\n{'='*50}\nVOLUNTEER: {v.id}\n{'='*50}")
            print(f"Name: {v.name}\nEmail: {v.email}\nPhone: {v.phone or 'N/A'}")
            print(f"Status: {v.status}\nSkills: {', '.join(v.skills) or 'None'}")
            print(f"Availability: {v.availability or 'N/A'}\nHours Committed: {v.hours_committed:.1f}")
            print(f"Hours Completed: {v.hours_completed:.1f}\nBackground Check: {'Yes' if v.background_check else 'No'}")
            print(f"Emergency Contact: {v.emergency_contact or 'N/A'}\nTags: {', '.join(v.tags) or 'None'}")
            print(f"Notes: {v.notes or 'None'}\nStart Date: {v.start_date}")

        elif args.command == "update-volunteer":
            kwargs = {k: v for k, v in vars(args).items() if k not in ["command", "volunteer_id"] and v is not None}
            v = coord.update_volunteer(args.volunteer_id, **kwargs)
            if v: print(f"✓ Volunteer updated: {v.id}")
            else: print(f"✗ Volunteer not found"); sys.exit(1)

        elif args.command == "delete-volunteer":
            if coord.delete_volunteer(args.volunteer_id): print(f"✓ Volunteer deleted")
            else: print(f"✗ Volunteer not found"); sys.exit(1)

        elif args.command == "add-shift":
            s = coord.create_shift(args.volunteer_id, args.title, args.date, args.start_time,
                args.end_time, args.location, args.role, args.notes)
            if s: print(f"✓ Shift created: {s.id}"); print(f"  {s.title} | {s.date} {s.start_time}-{s.end_time}")
            else: print(f"✗ Failed"); sys.exit(1)

        elif args.command == "complete-shift":
            s = coord.complete_shift(args.shift_id, args.hours, args.feedback)
            if s: print(f"✓ Shift completed: {s.id}")
            else: print(f"✗ Shift not found"); sys.exit(1)

        elif args.command == "cancel-shift":
            s = coord.cancel_shift(args.shift_id)
            if s: print(f"✓ Shift cancelled: {s.id}")
            else: print(f"✗ Shift not found"); sys.exit(1)

        elif args.command == "shifts":
            shifts_list = coord.get_volunteer_shifts(args.volunteer_id, args.status)
            if not shifts_list: print("No shifts found.")
            else:
                print(f"\nShifts for: {args.volunteer_id}")
                print("-" * 70)
                for s in shifts_list:
                    print(f"{s.status.upper():<12} {s.date} {s.start_time}-{s.end_time} | {s.title}")

        elif args.command == "upcoming":
            up = coord.get_upcoming_shifts(args.days)
            if not up: print(f"No upcoming shifts in {args.days} days.")
            else:
                print(f"\nUpcoming Shifts ({args.days} days)")
                print("-" * 70)
                for shift, vname in up:
                    print(f"{shift.date} {shift.start_time}-{shift.end_time} | {shift.title}")
                    print(f"  Volunteer: {vname} | Location: {shift.location or 'N/A'}")

        elif args.command == "create-event":
            e = coord.create_event(args.name, args.date, args.description, args.location, args.required_volunteers, notes=args.notes)
            print(f"✓ Event created: {e.id}"); print(f"  {e.name} | {e.date}")

        elif args.command == "assign-volunteer":
            if coord.assign_volunteer_to_event(args.event_id, args.volunteer_id):
                print(f"✓ Volunteer assigned to event")
            else: print(f"✗ Failed"); sys.exit(1)

        elif args.command == "list-events":
            evts = coord.list_events(args.status)
            if not evts: print("No events found.")
            else:
                print(f"\n{'Name':<35} {'Date':<12} {'Volunteers':<12} {'Status'}")
                print("-" * 80)
                for e in evts:
                    print(f"{e.name:<35} {e.date:<12} {len(e.volunteer_ids):<12} {e.status}")

        elif args.command == "event-volunteers":
            vols = coord.get_event_volunteers(args.event_id)
            if not vols: print("No volunteers assigned.")
            else:
                print(f"\nVolunteers for Event: {args.event_id}")
                for v in vols: print(f"  - {v.name} ({v.email})")

        elif args.command == "stats":
            s = coord.get_statistics()
            print(f"\n{'='*50}\nVOLUNTEER STATISTICS\n{'='*50}")
            print(f"Total Volunteers: {s['total_volunteers']}")
            print(f"Active: {s['active_volunteers']} | Inactive: {s['inactive_volunteers']}")
            print(f"Total Hours Donated: {s['total_hours_donated']:.1f}")
            print(f"Background Checks: {s['background_checks_complete']}")
            print(f"Upcoming Shifts: {s['upcoming_shifts']}")
            print(f"Upcoming Events: {s['upcoming_events']}")

        elif args.command == "report":
            text = coord.generate_report(args.output)
            if args.output: print(f"✓ Report saved to {args.output}")
            else: print(text)

    except Exception as e:
        logger.exception(f"Error: {e}")
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
