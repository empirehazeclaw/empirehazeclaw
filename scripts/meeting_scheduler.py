#!/usr/bin/env python3
"""
🦞 Meeting Scheduler - Books demo meetings automatically
When a lead responds, schedules a calendar slot
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = WORKSPACE / "data"
CALENDAR_FILE = DATA_DIR / "meetings.json"
RESPONSES_FILE = DATA_DIR / "responses.json"

# Available slots (can be customized)
AVAILABLE_SLOTS = [
    {"day": "Monday", "time": "10:00", "duration": 30},
    {"day": "Monday", "time": "14:00", "duration": 30},
    {"day": "Wednesday", "time": "10:00", "duration": 30},
    {"day": "Wednesday", "time": "14:00", "duration": 30},
    {"day": "Friday", "time": "10:00", "duration": 30},
    {"day": "Friday", "time": "14:00", "duration": 30},
]

class MeetingScheduler:
    def __init__(self):
        self.calendar_file = CALENDAR_FILE
        self.responses_file = RESPONSES_FILE
        self.meetings = self.load_meetings()
    
    def load_meetings(self) -> List[Dict]:
        """Load existing meetings"""
        if self.calendar_file.exists():
            with open(self.calendar_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_meetings(self):
        """Save meetings to file"""
        self.calendar_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.calendar_file, 'w') as f:
            json.dump(self.meetings, f, indent=2)
    
    def get_next_slot(self, preferred_day: Optional[str] = None) -> Optional[Dict]:
        """Get the next available slot"""
        now = datetime.now()
        
        # Simple slot selection - find next available day/time
        for meeting in self.meetings:
            if meeting.get("status") == "scheduled":
                return None  # No slots available
        
        # Return next available (simplified - just picks first slot)
        return AVAILABLE_SLOTS[0]
    
    def schedule_meeting(self, lead_email: str, lead_name: str, company: str, 
                        slot: Optional[Dict] = None, notes: str = "") -> Dict:
        """Schedule a meeting with a lead"""
        if slot is None:
            slot = self.get_next_slot()
        
        if slot is None:
            return {"success": False, "error": "No slots available"}
        
        meeting = {
            "id": f"meet_{len(self.meetings) + 1}",
            "lead_email": lead_email,
            "lead_name": lead_name,
            "company": company,
            "slot": slot,
            "notes": notes,
            "status": "scheduled",
            "created_at": datetime.now().isoformat(),
            "meeting_link": self.generate_meet_link(),
            "calendar_event": self.create_calendar_event(lead_email, lead_name, company, slot)
        }
        
        self.meetings.append(meeting)
        self.save_meetings()
        
        return {"success": True, "meeting": meeting}
    
    def generate_meet_link(self) -> str:
        """Generate a Google Meet or video link placeholder"""
        # In production, this would use Google Calendar API
        return f"https://meet.empirehazeclaw.de/{datetime.now().strftime('%Y%m%d%H%M')}"
    
    def create_calendar_event(self, email: str, name: str, company: str, slot: Dict) -> Dict:
        """Create calendar event data"""
        # Simplified - in production would use Google Calendar API
        return {
            "title": f"EmpireHazeClaw Demo - {company}",
            "description": f"Demo call with {name} from {company}\nEmail: {email}",
            "duration_minutes": slot.get("duration", 30)
        }
    
    def get_upcoming_meetings(self) -> List[Dict]:
        """Get all upcoming scheduled meetings"""
        return [m for m in self.meetings if m.get("status") == "scheduled"]
    
    def cancel_meeting(self, meeting_id: str) -> bool:
        """Cancel a meeting"""
        for meeting in self.meetings:
            if meeting.get("id") == meeting_id:
                meeting["status"] = "cancelled"
                self.save_meetings()
                return True
        return False
    
    def get_availability(self) -> Dict:
        """Get current availability"""
        scheduled = len([m for m in self.meetings if m.get("status") == "scheduled"])
        return {
            "total_slots": len(AVAILABLE_SLOTS),
            "scheduled": scheduled,
            "available": len(AVAILABLE_SLOTS) - scheduled,
            "next_slot": AVAILABLE_SLOTS[0] if scheduled < len(AVAILABLE_SLOTS) else None
        }
    
    def send_confirmation(self, meeting: Dict) -> bool:
        """Send meeting confirmation email"""
        # In production, would send via SMTP/GOG
        print(f"📧 Would send confirmation to {meeting['lead_email']}")
        print(f"   Meeting: {meeting['slot']['day']} at {meeting['slot']['time']}")
        print(f"   Link: {meeting['meeting_link']}")
        return True
    
    def run(self, command: str = "status", **kwargs):
        """Main CLI interface"""
        if command == "status":
            avail = self.get_availability()
            print(f"\n📅 Meeting Scheduler Status")
            print("=" * 40)
            print(f"Available Slots: {avail['available']}/{avail['total_slots']}")
            print(f"Scheduled: {avail['scheduled']}")
            if avail['next_slot']:
                print(f"Next Slot: {avail['next_slot']['day']} at {avail['next_slot']['time']}")
            
            upcoming = self.get_upcoming_meetings()
            if upcoming:
                print(f"\n📅 Upcoming Meetings:")
                for m in upcoming:
                    print(f"  - {m['lead_name']} ({m['company']}) - {m['slot']['day']} {m['slot']['time']}")
        
        elif command == "schedule":
            result = self.schedule_meeting(
                kwargs.get("email"),
                kwargs.get("name", "Unknown"),
                kwargs.get("company", "Unknown"),
                notes=kwargs.get("notes", "")
            )
            if result["success"]:
                print(f"✅ Meeting scheduled!")
                self.send_confirmation(result["meeting"])
            else:
                print(f"❌ {result.get('error')}")
        
        elif command == "list":
            upcoming = self.get_upcoming_meetings()
            if not upcoming:
                print("No upcoming meetings")
            else:
                for m in upcoming:
                    print(f"\n📅 {m['lead_name']} ({m['company']})")
                    print(f"   Email: {m['lead_email']}")
                    print(f"   When: {m['slot']['day']} at {m['slot']['time']}")
                    print(f"   Link: {m['meeting_link']}")

if __name__ == "__main__":
    import sys
    
    scheduler = MeetingScheduler()
    
    if len(sys.argv) < 2:
        scheduler.run("status")
    elif sys.argv[1] == "schedule" and len(sys.argv) >= 5:
        scheduler.run(
            "schedule",
            email=sys.argv[2],
            name=sys.argv[3],
            company=sys.argv[4]
        )
    elif sys.argv[1] == "list":
        scheduler.run("list")
    else:
        print("Usage:")
        print("  python3 meeting_scheduler.py              # Show status")
        print("  python3 meeting_scheduler.py list         # List meetings")
        print("  python3 meeting_scheduler.py schedule <email> <name> <company>")
