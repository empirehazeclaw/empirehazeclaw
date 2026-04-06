#!/usr/bin/env python3
"""
Demo Scheduler Agent
=====================
Schedules and manages product demos with potential customers.
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
import hashlib

AGENT_DIR = Path(__file__).parent
WORKSPACE = AGENT_DIR.parent.parent
LOG_DIR = WORKSPACE / "logs"
DATA_DIR = WORKSPACE / "data"

LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "demo_scheduler.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("DemoScheduler")


class Demo:
    """Represents a demo session."""
    
    DURATIONS = [15, 30, 45, 60, 90, 120]
    STATUSES = ["scheduled", "confirmed", "completed", "cancelled", "no_show"]
    
    def __init__(self, prospect_name: str, prospect_email: str,
                 company: str = "", title: str = "",
                 scheduled_time: str = "", duration: int = 30,
                 timezone: str = "UTC", product: str = "general",
                 meeting_link: str = "", notes: str = "",
                 reminder_sent: bool = False):
        self.id = self._generate_id()
        self.prospect_name = prospect_name
        self.prospect_email = prospect_email
        self.company = company
        self.title = title
        self.scheduled_time = scheduled_time
        self.duration = duration
        self.timezone = timezone
        self.product = product
        self.meeting_link = meeting_link
        self.notes = notes
        self.status = "scheduled"
        self.reminder_sent = reminder_sent
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.completed_at = None
        self.feedback = None
    
    def _generate_id(self) -> str:
        raw = f"{datetime.now().isoformat()}"
        return "demo_" + hashlib.md5(raw.encode()).hexdigest()[:10]
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "prospect_name": self.prospect_name,
            "prospect_email": self.prospect_email,
            "company": self.company,
            "title": self.title,
            "scheduled_time": self.scheduled_time,
            "duration": self.duration,
            "timezone": self.timezone,
            "product": self.product,
            "meeting_link": self.meeting_link,
            "notes": self.notes,
            "status": self.status,
            "reminder_sent": self.reminder_sent,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "feedback": self.feedback
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Demo':
        d = cls(
            prospect_name=data.get("prospect_name", ""),
            prospect_email=data.get("prospect_email", ""),
            company=data.get("company", ""),
            title=data.get("title", ""),
            scheduled_time=data.get("scheduled_time", ""),
            duration=data.get("duration", 30),
            timezone=data.get("timezone", "UTC"),
            product=data.get("product", "general"),
            meeting_link=data.get("meeting_link", ""),
            notes=data.get("notes", ""),
            reminder_sent=data.get("reminder_sent", False)
        )
        for key in ["id", "status", "created_at", "updated_at", "completed_at", "feedback"]:
            if key in data:
                setattr(d, key, data[key])
        return d
    
    def confirm(self):
        """Confirm the demo."""
        self.status = "confirmed"
        self.updated_at = datetime.now().isoformat()
        logger.info(f"Demo {self.id} confirmed")
    
    def complete(self, feedback: str = None):
        """Mark demo as completed."""
        self.status = "completed"
        self.completed_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.feedback = feedback
        logger.info(f"Demo {self.id} completed")
    
    def cancel(self):
        """Cancel the demo."""
        self.status = "cancelled"
        self.updated_at = datetime.now().isoformat()
        logger.info(f"Demo {self.id} cancelled")
    
    def mark_no_show(self):
        """Mark as no-show."""
        self.status = "no_show"
        self.updated_at = datetime.now().isoformat()
        logger.info(f"Demo {self.id} marked as no-show")
    
    def send_reminder(self):
        """Mark reminder as sent."""
        self.reminder_sent = True
        self.updated_at = datetime.now().isoformat()
        logger.info(f"Demo {self.id} reminder sent")
    
    def get_end_time(self) -> Optional[str]:
        """Calculate demo end time."""
        if not self.scheduled_time:
            return None
        try:
            start = datetime.fromisoformat(self.scheduled_time.replace("Z", "+00:00"))
            end = start + timedelta(minutes=self.duration)
            return end.isoformat()
        except:
            return None


class DemoStore:
    """Manages demo data persistence."""
    
    def __init__(self, data_file: Optional[Path] = None):
        self.data_file = data_file or (DATA_DIR / "demos.json")
        self.demos = []
        self._load()
    
    def _load(self):
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.demos = [Demo.from_dict(d) for d in data.get("demos", [])]
                logger.info(f"Loaded {len(self.demos)} demos")
            except Exception as e:
                logger.error(f"Failed to load demos: {e}")
                self.demos = []
        else:
            self.demos = []
    
    def _save(self):
        try:
            data = {
                "demos": [d.to_dict() for d in self.demos],
                "updated_at": datetime.now().isoformat()
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.demos)} demos")
        except Exception as e:
            logger.error(f"Failed to save demos: {e}")
            raise
    
    def add_demo(self, demo: Demo) -> bool:
        for existing in self.demos:
            if existing.id == demo.id:
                return False
        self.demos.append(demo)
        self._save()
        return True
    
    def get_demo(self, demo_id: str) -> Optional[Demo]:
        for d in self.demos:
            if d.id == demo_id:
                return d
        return None
    
    def update_demo(self, demo_id: str, updates: dict) -> bool:
        for d in self.demos:
            if d.id == demo_id:
                for key, value in updates.items():
                    if hasattr(d, key) and key not in ["id", "created_at"]:
                        setattr(d, key, value)
                d.updated_at = datetime.now().isoformat()
                self._save()
                return True
        return False
    
    def delete_demo(self, demo_id: str) -> bool:
        self.demos = [d for d in self.demos if d.id != demo_id]
        self._save()
        return True
    
    def list_demos(self, status: Optional[str] = None,
                   upcoming: bool = False) -> List[Demo]:
        demos = self.demos
        
        if status:
            demos = [d for d in demos if d.status == status]
        
        if upcoming:
            now = datetime.now()
            demos = [d for d in demos if d.status in ["scheduled", "confirmed"]]
            demos = [d for d in demos if d.scheduled_time and 
                     datetime.fromisoformat(d.scheduled_time.replace("Z", "+00:00")) > now]
        
        return sorted(demos, key=lambda x: x.scheduled_time or "")
    
    def get_upcoming_reminders(self, hours: int = 24) -> List[Demo]:
        """Get demos needing reminder within N hours."""
        now = datetime.now()
        cutoff = now + timedelta(hours=hours)
        
        reminders = []
        for d in self.demos:
            if d.status in ["scheduled", "confirmed"] and d.scheduled_time:
                try:
                    sched = datetime.fromisoformat(d.scheduled_time.replace("Z", "+00:00"))
                    if now < sched < cutoff and not d.reminder_sent:
                        reminders.append(d)
                except:
                    pass
        return reminders
    
    def get_stats(self) -> dict:
        """Get demo statistics."""
        total = len(self.demos)
        by_status = {}
        for d in self.demos:
            by_status[d.status] = by_status.get(d.status, 0) + 1
        
        completed = [d for d in self.demos if d.status == "completed"]
        no_show = [d for d in self.demos if d.status == "no_show"]
        show_rate = round(len(completed) / (len(completed) + len(no_show)) * 100, 1) if (completed or no_show) else 0
        
        return {
            "total_demos": total,
            "by_status": by_status,
            "completed": len(completed),
            "no_shows": len(no_show),
            "show_rate": show_rate,
            "upcoming_count": len([d for d in self.demos if d.status in ["scheduled", "confirmed"]])
        }


class DemoScheduler:
    """Main demo scheduler agent."""
    
    def __init__(self):
        self.store = DemoStore()
        logger.info("DemoScheduler initialized")
    
    def schedule_demo(self, data: dict) -> Optional[Demo]:
        """Schedule a new demo."""
        try:
            demo = Demo(
                prospect_name=data.get("prospect_name", ""),
                prospect_email=data.get("prospect_email", ""),
                company=data.get("company", ""),
                title=data.get("title", ""),
                scheduled_time=data.get("scheduled_time", ""),
                duration=data.get("duration", 30),
                timezone=data.get("timezone", "UTC"),
                product=data.get("product", "general"),
                meeting_link=data.get("meeting_link", ""),
                notes=data.get("notes", "")
            )
            
            if demo.scheduled_time:
                # Validate datetime format
                try:
                    datetime.fromisoformat(demo.scheduled_time.replace("Z", "+00:00"))
                except ValueError:
                    raise ValueError("Invalid datetime format for scheduled_time")
            
            self.store.add_demo(demo)
            logger.info(f"Scheduled demo for {demo.prospect_name} at {demo.company}")
            return demo
        except Exception as e:
            logger.error(f"Failed to schedule demo: {e}")
            return None
    
    def confirm_demo(self, demo_id: str) -> bool:
        demo = self.store.get_demo(demo_id)
        if not demo:
            return False
        demo.confirm()
        self.store._save()
        return True
    
    def cancel_demo(self, demo_id: str) -> bool:
        demo = self.store.get_demo(demo_id)
        if not demo:
            return False
        demo.cancel()
        self.store._save()
        return True
    
    def complete_demo(self, demo_id: str, feedback: str = None) -> bool:
        demo = self.store.get_demo(demo_id)
        if not demo:
            return False
        demo.complete(feedback)
        self.store._save()
        return True
    
    def mark_no_show(self, demo_id: str) -> bool:
        demo = self.store.get_demo(demo_id)
        if not demo:
            return False
        demo.mark_no_show()
        self.store._save()
        return True
    
    def reschedule_demo(self, demo_id: str, new_time: str) -> bool:
        demo = self.store.get_demo(demo_id)
        if not demo:
            return False
        
        try:
            datetime.fromisoformat(new_time.replace("Z", "+00:00"))
            demo.scheduled_time = new_time
            demo.updated_at = datetime.now().isoformat()
            self.store._save()
            logger.info(f"Rescheduled demo {demo_id} to {new_time}")
            return True
        except ValueError:
            logger.error(f"Invalid datetime format: {new_time}")
            return False
    
    def send_reminder(self, demo_id: str) -> dict:
        """Prepare reminder data for sending."""
        demo = self.store.get_demo(demo_id)
        if not demo:
            return {"success": False, "message": "Demo not found"}
        
        demo.send_reminder()
        self.store._save()
        
        return {
            "success": True,
            "reminder": {
                "to": demo.prospect_email,
                "subject": f"Reminder: Demo scheduled for {demo.company}",
                "body": self._generate_reminder_body(demo),
                "meeting_link": demo.meeting_link
            }
        }
    
    def _generate_reminder_body(self, demo: Demo) -> str:
        """Generate reminder email body."""
        return f"""Hi {demo.prospect_name},

This is a reminder about your upcoming product demo.

Details:
- Company: {demo.company}
- Date/Time: {demo.scheduled_time} ({demo.timezone})
- Duration: {demo.duration} minutes
- Product: {demo.product}

{demo.meeting_link and f"Meeting Link: {demo.meeting_link}" or ""}

Please let us know if you need to reschedule.

Best regards,
The Sales Team
"""


def main():
    parser = argparse.ArgumentParser(
        description="Demo Scheduler Agent - Schedule and manage product demos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --schedule '{"prospect_name": "John Doe", "prospect_email": "john@acme.com", "company": "Acme Inc", "scheduled_time": "2026-04-01T10:00:00Z", "duration": 30, "product": "saas-platform"}'
  %(prog)s --list
  %(prog)s --list --status scheduled
  %(prog)s --list --upcoming
  %(prog)s --confirm demo_abc123
  %(prog)s --cancel demo_abc123
  %(prog)s --complete demo_abc123 --feedback "Great demo, interested in enterprise plan"
  %(prog)s --no-show demo_abc123
  %(prog)s --reschedule demo_abc123 --time "2026-04-02T14:00:00Z"
  %(prog)s --reminder demo_abc123
  %(prog)s --get demo_abc123
  %(prog)s --stats
  %(prog)s --delete demo_abc123
        """
    )
    
    parser.add_argument("--schedule", type=str, help="Schedule demo from JSON")
    parser.add_argument("--list", action="store_true", help="List all demos")
    parser.add_argument("--status", type=str, help="Filter by status")
    parser.add_argument("--upcoming", action="store_true", help="Show only upcoming demos")
    parser.add_argument("--confirm", type=str, help="Confirm demo by ID")
    parser.add_argument("--cancel", type=str, help="Cancel demo by ID")
    parser.add_argument("--complete", type=str, help="Complete demo by ID")
    parser.add_argument("--feedback", type=str, default="", help="Feedback after demo")
    parser.add_argument("--no-show", dest="no_show", type=str, help="Mark demo as no-show")
    parser.add_argument("--reschedule", type=str, help="Reschedule demo by ID")
    parser.add_argument("--time", type=str, help="New time for reschedule")
    parser.add_argument("--reminder", type=str, help="Send reminder for demo (returns email data)")
    parser.add_argument("--get", type=str, help="Get demo by ID")
    parser.add_argument("--stats", action="store_true", help="Show demo statistics")
    parser.add_argument("--delete", type=str, help="Delete demo by ID")
    
    args = parser.parse_args()
    scheduler = DemoScheduler()
    
    try:
        if args.schedule:
            data = json.loads(args.schedule)
            demo = scheduler.schedule_demo(data)
            if demo:
                print(json.dumps({"success": True, "demo": demo.to_dict()}))
            else:
                print(json.dumps({"success": False, "message": "Failed to schedule demo"}))
        
        elif args.list:
            demos = scheduler.store.list_demos(status=args.status, upcoming=args.upcoming)
            output = [d.to_dict() for d in demos]
            print(json.dumps({"count": len(output), "demos": output}, indent=2))
        
        elif args.confirm:
            if scheduler.confirm_demo(args.confirm):
                demo = scheduler.store.get_demo(args.confirm)
                print(json.dumps({"success": True, "demo": demo.to_dict()}))
            else:
                print(json.dumps({"success": False, "message": "Demo not found"}))
        
        elif args.cancel:
            if scheduler.cancel_demo(args.cancel):
                print(json.dumps({"success": True, "message": "Demo cancelled"}))
            else:
                print(json.dumps({"success": False, "message": "Demo not found"}))
        
        elif args.complete:
            if scheduler.complete_demo(args.complete, args.feedback):
                demo = scheduler.store.get_demo(args.complete)
                print(json.dumps({"success": True, "demo": demo.to_dict()}))
            else:
                print(json.dumps({"success": False, "message": "Demo not found"}))
        
        elif args.no_show:
            if scheduler.mark_no_show(args.no_show):
                print(json.dumps({"success": True, "message": "Demo marked as no-show"}))
            else:
                print(json.dumps({"success": False, "message": "Demo not found"}))
        
        elif args.reschedule:
            if not args.time:
                print(json.dumps({"success": False, "message": "--time required for reschedule"}))
                sys.exit(1)
            if scheduler.reschedule_demo(args.reschedule, args.time):
                demo = scheduler.store.get_demo(args.reschedule)
                print(json.dumps({"success": True, "demo": demo.to_dict()}))
            else:
                print(json.dumps({"success": False, "message": "Failed to reschedule"}))
        
        elif args.reminder:
            result = scheduler.send_reminder(args.reminder)
            print(json.dumps(result, indent=2))
        
        elif args.get:
            demo = scheduler.store.get_demo(args.get)
            if demo:
                print(json.dumps(demo.to_dict(), indent=2))
            else:
                print(json.dumps({"success": False, "message": "Demo not found"}))
        
        elif args.stats:
            stats = scheduler.store.get_stats()
            print(json.dumps(stats, indent=2))
        
        elif args.delete:
            success = scheduler.store.delete_demo(args.delete)
            print(json.dumps({"success": success}))
        
        else:
            parser.print_help()
    
    except json.JSONDecodeError as e:
        print(json.dumps({"success": False, "message": f"Invalid JSON: {e}"}))
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        print(json.dumps({"success": False, "message": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
