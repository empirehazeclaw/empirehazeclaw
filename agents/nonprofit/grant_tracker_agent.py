#!/usr/bin/env python3
"""
Grant Tracker Agent - Nonprofit Sector
Tracks grant applications, deadlines, requirements, and reporting.
"""

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List

# Configure logging
LOG_DIR = Path(__file__).parent.parent.parent / "logs" / "nonprofit"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "grant_tracker.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("GrantTrackerAgent")


@dataclass
class Grant:
    id: str
    name: str
    funder: str
    amount: float
    deadline: str
    status: str = "identified"
    description: str = ""
    requirements: List[str] = None
    eligibility: str = ""
    website: str = ""
    contact_name: str = ""
    contact_email: str = ""
    application_url: str = ""
    notes: str = ""
    documents: List[str] = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if self.requirements is None:
            self.requirements = []
        if self.documents is None:
            self.documents = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()


@dataclass
class Milestone:
    id: str
    grant_id: str
    title: str
    due_date: str
    completed: bool = False
    completed_date: Optional[str] = None
    notes: str = ""


@dataclass
class Report:
    id: str
    grant_id: str
    report_type: str = "progress"
    due_date: str = ""
    submitted_date: Optional[str] = None
    status: str = "pending"
    notes: str = ""


class GrantTracker:
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent / "data" / "nonprofit"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.grants_file = self.data_dir / "grants.json"
        self.milestones_file = self.data_dir / "grant_milestones.json"
        self.reports_file = self.data_dir / "grant_reports.json"
        self.grants = self._load_grants()
        self.milestones = self._load_milestones()
        self.reports = self._load_reports()

    def _load_json(self, filepath: Path, cls):
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    return {item['id']: cls(**item) for item in data}
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Error loading {filepath}: {e}")
        return {}

    def _load_grants(self) -> dict:
        return self._load_json(self.grants_file, Grant)

    def _load_milestones(self) -> dict:
        return self._load_json(self.milestones_file, Milestone)

    def _load_reports(self) -> dict:
        return self._load_json(self.reports_file, Report)

    def _save_json(self, filepath: Path, data: dict):
        try:
            with open(filepath, 'w') as f:
                json.dump([asdict(item) for item in data.values()], f, indent=2)
        except IOError as e:
            logger.error(f"Error saving {filepath}: {e}")

    def _save_grants(self):
        self._save_json(self.grants_file, self.grants)

    def _save_milestones(self):
        self._save_json(self.milestones_file, self.milestones)

    def _save_reports(self):
        self._save_json(self.reports_file, self.reports)

    def generate_id(self, prefix: str) -> str:
        return f"{prefix}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def add_grant(self, name: str, funder: str, amount: float, deadline: str,
                  description: str = "", eligibility: str = "", website: str = "",
                  contact_name: str = "", contact_email: str = "",
                  application_url: str = "", notes: str = "",
                  requirements: List[str] = None, documents: List[str] = None) -> Grant:
        grant = Grant(
            id=self.generate_id("grant"),
            name=name, funder=funder, amount=amount, deadline=deadline,
            description=description, eligibility=eligibility, website=website,
            contact_name=contact_name, contact_email=contact_email,
            application_url=application_url, notes=notes,
            requirements=requirements or [], documents=documents or []
        )
        self.grants[grant.id] = grant
        self._save_grants()
        logger.info(f"Added grant: {name} from {funder}")
        return grant

    def update_grant_status(self, grant_id: str, status: str) -> Optional[Grant]:
        if grant_id not in self.grants:
            logger.error(f"Grant {grant_id} not found")
            return None
        self.grants[grant_id].status = status
        self.grants[grant_id].updated_at = datetime.now().isoformat()
        self._save_grants()
        logger.info(f"Updated grant {grant_id} status to {status}")
        return self.grants[grant_id]

    def get_grant(self, grant_id: str) -> Optional[Grant]:
        return self.grants.get(grant_id)

    def list_grants(self, status: str = None, sort_by: str = "deadline") -> List[Grant]:
        grants = list(self.grants.values())
        if status:
            grants = [g for g in grants if g.status == status]
        if sort_by == "amount":
            grants.sort(key=lambda x: x.amount, reverse=True)
        elif sort_by == "name":
            grants.sort(key=lambda x: x.name.lower())
        else:
            grants.sort(key=lambda x: x.deadline)
        return grants

    def get_upcoming_deadlines(self, days: int = 30) -> List[tuple]:
        upcoming = []
        cutoff = datetime.now() + timedelta(days=days)
        for grant in self.grants.values():
            try:
                deadline = datetime.fromisoformat(grant.deadline)
                if datetime.now() <= deadline <= cutoff:
                    days_left = (deadline - datetime.now()).days
                    upcoming.append((grant, days_left))
            except ValueError:
                continue
        upcoming.sort(key=lambda x: x[1])
        return upcoming

    def add_milestone(self, grant_id: str, title: str, due_date: str, notes: str = "") -> Optional[Milestone]:
        if grant_id not in self.grants:
            logger.error(f"Grant {grant_id} not found")
            return None
        milestone = Milestone(
            id=self.generate_id("ms"), grant_id=grant_id, title=title, due_date=due_date, notes=notes
        )
        self.milestones[milestone.id] = milestone
        self._save_milestones()
        logger.info(f"Added milestone: {title} for grant {grant_id}")
        return milestone

    def complete_milestone(self, milestone_id: str) -> Optional[Milestone]:
        if milestone_id not in self.milestones:
            logger.error(f"Milestone {milestone_id} not found")
            return None
        self.milestones[milestone_id].completed = True
        self.milestones[milestone_id].completed_date = datetime.now().isoformat()
        self._save_milestones()
        return self.milestones[milestone_id]

    def get_milestones(self, grant_id: str) -> List[Milestone]:
        return [m for m in self.milestones.values() if m.grant_id == grant_id]

    def add_report(self, grant_id: str, report_type: str, due_date: str, notes: str = "") -> Optional[Report]:
        if grant_id not in self.grants:
            logger.error(f"Grant {grant_id} not found")
            return None
        report = Report(id=self.generate_id("rpt"), grant_id=grant_id, report_type=report_type, due_date=due_date, notes=notes)
        self.reports[report.id] = report
        self._save_reports()
        logger.info(f"Added report: {report_type} for grant {grant_id}")
        return report

    def submit_report(self, report_id: str) -> Optional[Report]:
        if report_id not in self.reports:
            logger.error(f"Report {report_id} not found")
            return None
        self.reports[report_id].submitted_date = datetime.now().isoformat()
        self.reports[report_id].status = "submitted"
        self._save_reports()
        return self.reports[report_id]

    def get_reports(self, grant_id: str = None, status: str = None) -> List[Report]:
        reports = list(self.reports.values())
        if grant_id:
            reports = [r for r in reports if r.grant_id == grant_id]
        if status:
            reports = [r for r in reports if r.status == status]
        return reports

    def get_overdue_reports(self) -> List[tuple]:
        overdue = []
        for report in self.reports.values():
            if report.status in ["pending", "in_progress"]:
                try:
                    due = datetime.fromisoformat(report.due_date)
                    if due < datetime.now():
                        overdue.append((report, (datetime.now() - due).days))
                except ValueError:
                    continue
        return overdue

    def get_statistics(self) -> dict:
        total_amount = sum(g.amount for g in self.grants.values())
        submitted_amount = sum(g.amount for g in self.grants.values() if g.status == "submitted")
        awarded_amount = sum(g.amount for g in self.grants.values() if g.status == "awarded")
        status_counts = {}
        for g in self.grants.values():
            status_counts[g.status] = status_counts.get(g.status, 0) + 1
        pending_reports = len([r for r in self.reports.values() if r.status == "pending"])
        overdue_reports = len(self.get_overdue_reports())
        return {
            "total_grants": len(self.grants), "total_funding_tracked": total_amount,
            "submitted_amount": submitted_amount, "awarded_amount": awarded_amount,
            "pending_amount": total_amount - submitted_amount - awarded_amount,
            "status_distribution": status_counts, "pending_reports": pending_reports,
            "overdue_reports": overdue_reports, "upcoming_deadlines": len(self.get_upcoming_deadlines())
        }

    def generate_report(self, output_file: Path = None) -> str:
        stats = self.get_statistics()
        upcoming = self.get_upcoming_deadlines(60)
        overdue = self.get_overdue_reports()
        lines = [
            "=" * 70, "GRANT TRACKING REPORT", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", "=" * 70, "",
            "SUMMARY", "-" * 50,
            f"Total Grants Tracked: {stats['total_grants']}",
            f"Total Funding Tracked: ${stats['total_funding_tracked']:,.2f}",
            f"Awarded: ${stats['awarded_amount']:,.2f}",
            f"Submitted (Pending): ${stats['submitted_amount']:,.2f}",
            f"Available: ${stats['pending_amount']:,.2f}", "",
            "STATUS DISTRIBUTION", "-" * 50,
        ]
        for status, count in stats['status_distribution'].items():
            lines.append(f"  {status.capitalize()}: {count}")
        if upcoming:
            lines.extend(["", "UPCOMING DEADLINES (60 days)", "-" * 50])
            for grant, days in upcoming:
                lines.append(f"  [{days} days] {grant.name} | {grant.funder} | ${grant.amount:,.2f}")
                lines.append(f"           Deadline: {grant.deadline}")
        if overdue:
            lines.extend(["", "OVERDUE REPORTS", "-" * 50])
            for report, days in overdue:
                grant = self.grants.get(report.grant_id)
                gname = grant.name if grant else "Unknown"
                lines.append(f"  [{days} days overdue] {report.report_type} report for {gname}")
                lines.append(f"           Due: {report.due_date}")
        report_text = "\n".join(lines)
        if output_file:
            output_file.write_text(report_text)
        return report_text

    def delete_grant(self, grant_id: str) -> bool:
        if grant_id not in self.grants:
            return False
        # Remove related milestones and reports
        self.milestones = {k: v for k, v in self.milestones.items() if v.grant_id != grant_id}
        self.reports = {k: v for k, v in self.reports.items() if v.grant_id != grant_id}
        del self.grants[grant_id]
        self._save_grants()
        self._save_milestones()
        self._save_reports()
        return True


def main():
    parser = argparse.ArgumentParser(description="Grant Tracker Agent - Track grant opportunities and deadlines")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    add = subparsers.add_parser("add", help="Add a grant")
    add.add_argument("--name", required=True)
    add.add_argument("--funder", required=True)
    add.add_argument("--amount", type=float, required=True)
    add.add_argument("--deadline", required=True)
    add.add_argument("--description", default="")
    add.add_argument("--eligibility", default="")
    add.add_argument("--website", default="")
    add.add_argument("--contact-name", default="")
    add.add_argument("--contact-email", default="")
    add.add_argument("--application-url", default="")
    add.add_argument("--notes", default="")
    add.add_argument("--requirements", nargs="*")
    add.add_argument("--documents", nargs="*")

    status = subparsers.add_parser("set-status", help="Update grant status")
    status.add_argument("--grant-id", required=True)
    status.add_argument("--status", required=True, choices=["identified", "preparing", "submitted", "awarded", "rejected", "closed"])

    list_gr = subparsers.add_parser("list", help="List grants")
    list_gr.add_argument("--status", choices=["identified", "preparing", "submitted", "awarded", "rejected", "closed"])
    list_gr.add_argument("--sort", choices=["deadline", "amount", "name"], default="deadline")

    get = subparsers.add_parser("get", help="Get grant details")
    get.add_argument("--grant-id", required=True)

    deadlines = subparsers.add_parser("deadlines", help="Show upcoming deadlines")
    deadlines.add_argument("--days", type=int, default=30)

    add_ms = subparsers.add_parser("add-milestone", help="Add milestone")
    add_ms.add_argument("--grant-id", required=True)
    add_ms.add_argument("--title", required=True)
    add_ms.add_argument("--due-date", required=True)
    add_ms.add_argument("--notes", default="")

    complete_ms = subparsers.add_parser("complete-milestone", help="Complete milestone")
    complete_ms.add_argument("--milestone-id", required=True)

    milestones = subparsers.add_parser("milestones", help="List milestones")
    milestones.add_argument("--grant-id", required=True)

    add_rpt = subparsers.add_parser("add-report", help="Add report requirement")
    add_rpt.add_argument("--grant-id", required=True)
    add_rpt.add_argument("--type", required=True, choices=["progress", "final", "financial"])
    add_rpt.add_argument("--due-date", required=True)
    add_rpt.add_argument("--notes", default="")

    submit_rpt = subparsers.add_parser("submit-report", help="Submit report")
    submit_rpt.add_argument("--report-id", required=True)

    reports = subparsers.add_parser("reports", help="List reports")
    reports.add_argument("--grant-id")
    reports.add_argument("--status")

    stats = subparsers.add_parser("stats", help="Get statistics")
    report_gen = subparsers.add_parser("report", help="Generate report")
    report_gen.add_argument("--output", type=Path)

    delete = subparsers.add_parser("delete", help="Delete grant")
    delete.add_argument("--grant-id", required=True)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    tracker = GrantTracker()
    try:
        if args.command == "add":
            g = tracker.add_grant(args.name, args.funder, args.amount, args.deadline,
                                  args.description, args.eligibility, args.website,
                                  args.contact_name, args.contact_email, args.application_url,
                                  args.notes, args.requirements, args.documents)
            print(f"✓ Grant added: {g.id}")
            print(f"  {g.name} from {g.funder}")
            print(f"  Amount: ${g.amount:,.2f} | Deadline: {g.deadline}")

        elif args.command == "set-status":
            g = tracker.update_grant_status(args.grant_id, args.status)
            if g:
                print(f"✓ Status updated: {g.id} → {g.status}")
            else:
                print(f"✗ Grant not found")
                sys.exit(1)

        elif args.command == "list":
            grants = tracker.list_grants(args.status, args.sort)
            if not grants:
                print("No grants found.")
            else:
                print(f"\n{'Name':<35} {'Funder':<20} {'Amount':<12} {'Deadline':<12} {'Status'}")
                print("-" * 100)
                for g in grants:
                    print(f"{g.name:<35} {g.funder:<20} ${g.amount:<11,.0f} {g.deadline:<12} {g.status}")

        elif args.command == "get":
            g = tracker.get_grant(args.grant_id)
            if not g:
                print(f"✗ Grant not found: {args.grant_id}")
                sys.exit(1)
            print(f"\n{'='*60}")
            print(f"GRANT: {g.id}")
            print(f"{'='*60}")
            print(f"Name: {g.name}")
            print(f"Funder: {g.funder}")
            print(f"Amount: ${g.amount:,.2f}")
            print(f"Deadline: {g.deadline}")
            print(f"Status: {g.status}")
            print(f"Description: {g.description or 'N/A'}")
            print(f"Eligibility: {g.eligibility or 'N/A'}")
            print(f"Website: {g.website or 'N/A'}")
            print(f"Contact: {g.contact_name} ({g.contact_email})" if g.contact_email else "Contact: N/A")
            print(f"Application URL: {g.application_url or 'N/A'}")
            print(f"Requirements: {', '.join(g.requirements) or 'None'}")
            print(f"Documents: {', '.join(g.documents) or 'None'}")
            print(f"Notes: {g.notes or 'None'}")

        elif args.command == "deadlines":
            upcoming = tracker.get_upcoming_deadlines(args.days)
            if not upcoming:
                print(f"No deadlines in the next {args.days} days.")
            else:
                print(f"\nUpcoming Deadlines ({args.days} days)")
                print("-" * 70)
                for grant, days in upcoming:
                    print(f"[{days} days] {grant.name}")
                    print(f"           {grant.funder} | ${grant.amount:,.2f}")
                    print(f"           Deadline: {grant.deadline}")
                    print()

        elif args.command == "add-milestone":
            m = tracker.add_milestone(args.grant_id, args.title, args.due_date, args.notes)
            if m:
                print(f"✓ Milestone added: {m.id}")
                print(f"  {m.title} | Due: {m.due_date}")
            else:
                print(f"✗ Failed to add milestone")
                sys.exit(1)

        elif args.command == "complete-milestone":
            m = tracker.complete_milestone(args.milestone_id)
            if m:
                print(f"✓ Milestone completed: {m.id}")
            else:
                print(f"✗ Milestone not found")
                sys.exit(1)

        elif args.command == "milestones":
            milestones = tracker.get_milestones(args.grant_id)
            if not milestones:
                print("No milestones found.")
            else:
                print(f"\nMilestones for Grant: {args.grant_id}")
                print("-" * 60)
                for m in milestones:
                    status = "✓" if m.completed else "○"
                    print(f"{status} {m.title} | Due: {m.due_date}")
                    if m.completed:
                        print(f"   Completed: {m.completed_date}")

        elif args.command == "add-report":
            r = tracker.add_report(args.grant_id, args.type, args.due_date, args.notes)
            if r:
                print(f"✓ Report added: {r.id}")
                print(f"  Type: {r.report_type} | Due: {r.due_date}")
            else:
                print(f"✗ Failed to add report")
                sys.exit(1)

        elif args.command == "submit-report":
            r = tracker.submit_report(args.report_id)
            if r:
                print(f"✓ Report submitted: {r.id}")
            else:
                print(f"✗ Report not found")
                sys.exit(1)

        elif args.command == "reports":
            reports_list = tracker.get_reports(args.grant_id, args.status)
            if not reports_list:
                print("No reports found.")
            else:
                print(f"\nReports")
                print("-" * 70)
                for r in reports_list:
                    print(f"{r.id} | {r.report_type} | Due: {r.due_date} | Status: {r.status}")

        elif args.command == "stats":
            stats_data = tracker.get_statistics()
            print(f"\n{'='*50}")
            print("GRANT STATISTICS")
            print(f"{'='*50}")
            print(f"Total Grants: {stats_data['total_grants']}")
            print(f"Total Funding Tracked: ${stats_data['total_funding_tracked']:,.2f}")
            print(f"Awarded: ${stats_data['awarded_amount']:,.2f}")
            print(f"Submitted: ${stats_data['submitted_amount']:,.2f}")
            print(f"Pending: ${stats_data['pending_amount']:,.2f}")
            print(f"\nStatus Distribution:")
            for s, c in stats_data['status_distribution'].items():
                print(f"  {s.capitalize()}: {c}")
            print(f"\nPending Reports: {stats_data['pending_reports']}")
            print(f"Overdue Reports: {stats_data['overdue_reports']}")
            print(f"Upcoming Deadlines: {stats_data['upcoming_deadlines']}")

        elif args.command == "report":
            output = tracker.generate_report(args.output)
            if args.output:
                print(f"✓ Report saved to {args.output}")
            else:
                print(output)

        elif args.command == "delete":
            if tracker.delete_grant(args.grant_id):
                print(f"✓ Grant deleted: {args.grant_id}")
            else:
                print(f"✗ Grant not found")
                sys.exit(1)

    except Exception as e:
        logger.exception(f"Error: {e}")
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
