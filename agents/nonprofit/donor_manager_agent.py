#!/usr/bin/env python3
"""
Donor Manager Agent - Nonprofit Sector
Manages donor relationships, tracks donations, and automates donor communication.
"""

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Configure logging
LOG_DIR = Path(__file__).parent.parent.parent / "logs" / "nonprofit"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "donor_manager.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("DonorManagerAgent")


@dataclass
class Donor:
    id: str
    name: str
    email: str
    phone: str = ""
    donation_total: float = 0.0
    donation_count: int = 0
    last_donation_date: Optional[str] = None
    first_donation_date: Optional[str] = None
    donor_tier: str = "Bronze"  # Bronze, Silver, Gold, Platinum
    notes: str = ""
    tags: list = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()
        self._update_tier()

    def _update_tier(self):
        """Update donor tier based on total donations."""
        if self.donation_total >= 10000:
            self.donor_tier = "Platinum"
        elif self.donation_total >= 5000:
            self.donor_tier = "Gold"
        elif self.donation_total >= 1000:
            self.donor_tier = "Silver"
        else:
            self.donor_tier = "Bronze"


@dataclass
class Donation:
    id: str
    donor_id: str
    amount: float
    date: str
    campaign: str = "General"
    payment_method: str = "Unknown"
    notes: str = ""
    recurring: bool = False
    receipt_sent: bool = False


class DonorManager:
    """Manages donor database and operations."""

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent / "data" / "nonprofit"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.donors_file = self.data_dir / "donors.json"
        self.donations_file = self.data_dir / "donations.json"
        self.donors = self._load_donors()
        self.donations = self._load_donations()

    def _load_donors(self) -> dict:
        """Load donors from JSON file."""
        if self.donors_file.exists():
            try:
                with open(self.donors_file, 'r') as f:
                    data = json.load(f)
                    return {d['id']: Donor(**d) for d in data}
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Error loading donors: {e}")
        return {}

    def _load_donations(self) -> dict:
        """Load donations from JSON file."""
        if self.donations_file.exists():
            try:
                with open(self.donations_file, 'r') as f:
                    return {d['id']: Donation(**d) for d in json.load(f)}
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Error loading donations: {e}")
        return {}

    def _save_donors(self):
        """Save donors to JSON file."""
        try:
            with open(self.donors_file, 'w') as f:
                json.dump([asdict(d) for d in self.donors.values()], f, indent=2)
            logger.info(f"Saved {len(self.donors)} donors")
        except IOError as e:
            logger.error(f"Error saving donors: {e}")

    def _save_donations(self):
        """Save donations to JSON file."""
        try:
            with open(self.donations_file, 'w') as f:
                json.dump([asdict(d) for d in self.donations.values()], f, indent=2)
            logger.info(f"Saved {len(self.donations)} donations")
        except IOError as e:
            logger.error(f"Error saving donations: {e}")

    def generate_id(self, prefix: str) -> str:
        """Generate unique ID."""
        return f"{prefix}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self.donors) + 1}"

    def add_donor(self, name: str, email: str, phone: str = "", notes: str = "", tags: list = None) -> Donor:
        """Add a new donor."""
        # Check for existing donor with same email
        for donor in self.donors.values():
            if donor.email.lower() == email.lower():
                logger.warning(f"Donor with email {email} already exists")
                return donor

        donor = Donor(
            id=self.generate_id("donor"),
            name=name,
            email=email,
            phone=phone,
            notes=notes,
            tags=tags or []
        )
        self.donors[donor.id] = donor
        self._save_donors()
        logger.info(f"Added donor: {name} ({email})")
        return donor

    def add_donation(self, donor_id: str, amount: float, campaign: str = "General",
                     payment_method: str = "Unknown", notes: str = "", recurring: bool = False) -> Optional[Donation]:
        """Record a new donation."""
        if donor_id not in self.donors:
            logger.error(f"Donor {donor_id} not found")
            return None

        donation = Donation(
            id=self.generate_id("don"),
            donor_id=donor_id,
            amount=amount,
            date=datetime.now().isoformat(),
            campaign=campaign,
            payment_method=payment_method,
            notes=notes,
            recurring=recurring
        )
        self.donations[donation.id] = donation

        # Update donor stats
        donor = self.donors[donor_id]
        donor.donation_total += amount
        donor.donation_count += 1
        donor.last_donation_date = donation.date
        if not donor.first_donation_date:
            donor.first_donation_date = donation.date
        donor.updated_at = datetime.now().isoformat()
        donor._update_tier()

        self._save_donations()
        self._save_donors()
        logger.info(f"Recorded donation: ${amount:.2f} from {donor.name}")
        return donation

    def get_donor(self, donor_id: str) -> Optional[Donor]:
        """Get donor by ID."""
        return self.donors.get(donor_id)

    def find_donor_by_email(self, email: str) -> Optional[Donor]:
        """Find donor by email."""
        for donor in self.donors.values():
            if donor.email.lower() == email.lower():
                return donor
        return None

    def list_donors(self, tier: str = None, sort_by: str = "name") -> list:
        """List all donors, optionally filtered by tier."""
        donors = list(self.donors.values())
        if tier:
            donors = [d for d in donors if d.donor_tier == tier]
        if sort_by == "total":
            donors.sort(key=lambda x: x.donation_total, reverse=True)
        elif sort_by == "recent":
            donors.sort(key=lambda x: x.last_donation_date or "", reverse=True)
        else:
            donors.sort(key=lambda x: x.name.lower())
        return donors

    def get_statistics(self) -> dict:
        """Get overall donation statistics."""
        total_donations = sum(donation.amount for donation in self.donations.values())
        avg_donation = total_donations / len(self.donors) if self.donors else 0

        # Count by tier
        tier_counts = {"Bronze": 0, "Silver": 0, "Gold": 0, "Platinum": 0}
        for donor in self.donors.values():
            tier_counts[donor.donor_tier] += 1

        # Recent donations (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_total = 0
        for donation in self.donations.values():
            if datetime.fromisoformat(donation.date) > thirty_days_ago:
                recent_total += donation.amount

        # Monthly average
        months_active = 1
        if self.donations:
            dates = [datetime.fromisoformat(d.date) for d in self.donations.values()]
            date_range = (max(dates) - min(dates)).days / 30 if len(dates) > 1 else 1
            months_active = max(1, date_range)

        return {
            "total_donors": len(self.donors),
            "total_donations": len(self.donations),
            "total_amount": total_donations,
            "average_donation": avg_donation,
            "monthly_average": total_donations / months_active,
            "donations_last_30_days": recent_total,
            "tier_distribution": tier_counts
        }

    def generate_donor_report(self, output_file: Path = None) -> str:
        """Generate a donor report."""
        stats = self.get_statistics()
        report_lines = [
            "=" * 60,
            "DONOR MANAGEMENT REPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "=" * 60,
            "",
            "SUMMARY",
            "-" * 40,
            f"Total Donors: {stats['total_donors']}",
            f"Total Donations: {stats['total_donations']}",
            f"Total Amount Raised: ${stats['total_amount']:,.2f}",
            f"Average Donation: ${stats['average_donation']:.2f}",
            f"Monthly Average: ${stats['monthly_average']:.2f}",
            f"Last 30 Days: ${stats['donations_last_30_days']:,.2f}",
            "",
            "DONOR TIERS",
            "-" * 40,
        ]
        for tier, count in stats['tier_distribution'].items():
            report_lines.append(f"  {tier}: {count} donors")

        report_lines.extend([
            "",
            "TOP DONORS",
            "-" * 40,
        ])

        top_donors = sorted(self.donors.values(), key=lambda x: x.donation_total, reverse=True)[:10]
        for i, donor in enumerate(top_donors, 1):
            report_lines.append(f"{i}. {donor.name}")
            report_lines.append(f"   ${donor.donation_total:,.2f} ({donor.donation_count} donations)")
            report_lines.append(f"   {donor.donor_tier} Tier | {donor.email}")

        report = "\n".join(report_lines)

        if output_file:
            output_file.write_text(report)
            logger.info(f"Report saved to {output_file}")

        return report

    def export_csv(self, output_file: Path) -> bool:
        """Export donors to CSV."""
        try:
            import csv
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Total Donations',
                                'Donation Count', 'Tier', 'Last Donation', 'Tags'])
                for donor in self.donors.values():
                    writer.writerow([
                        donor.id, donor.name, donor.email, donor.phone,
                        donor.donation_total, donor.donation_count, donor.donor_tier,
                        donor.last_donation_date or 'Never', ','.join(donor.tags)
                    ])
            logger.info(f"Exported {len(self.donors)} donors to {output_file}")
            return True
        except IOError as e:
            logger.error(f"Error exporting CSV: {e}")
            return False

    def update_donor(self, donor_id: str, **kwargs) -> Optional[Donor]:
        """Update donor information."""
        if donor_id not in self.donors:
            logger.error(f"Donor {donor_id} not found")
            return None

        donor = self.donors[donor_id]
        for key, value in kwargs.items():
            if hasattr(donor, key) and key not in ['id', 'donation_total', 'donation_count']:
                setattr(donor, key, value)
        donor.updated_at = datetime.now().isoformat()
        self._save_donors()
        logger.info(f"Updated donor: {donor_id}")
        return donor

    def delete_donor(self, donor_id: str) -> bool:
        """Delete a donor and their donations."""
        if donor_id not in self.donors:
            logger.error(f"Donor {donor_id} not found")
            return False

        # Remove associated donations
        donations_to_remove = [d_id for d in self.donations.values() if d.donor_id == donor_id]
        for d_id in donations_to_remove:
            del self.donations[d_id]

        del self.donors[donor_id]
        self._save_donors()
        self._save_donations()
        logger.info(f"Deleted donor: {donor_id}")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Donor Manager Agent - Manage nonprofit donor relationships",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s add-donor --name "John Doe" --email john@example.com
  %(prog)s add-donation --donor-id donor_xxx --amount 500 --campaign "Spring Fundraiser"
  %(prog)s list --tier Gold
  %(prog)s stats
  %(prog)s report --output donor_report.txt
  %(prog)s export --output donors.csv
  %(prog)s find --email john@example.com
  %(prog)s update --donor-id donor_xxx --phone "+1234567890"
  %(prog)s delete --donor-id donor_xxx
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Add Donor
    add_parser = subparsers.add_parser("add-donor", help="Add a new donor")
    add_parser.add_argument("--name", required=True, help="Donor name")
    add_parser.add_argument("--email", required=True, help="Donor email")
    add_parser.add_argument("--phone", default="", help="Donor phone")
    add_parser.add_argument("--notes", default="", help="Notes")
    add_parser.add_argument("--tags", nargs="*", help="Tags")

    # Add Donation
    don_parser = subparsers.add_parser("add-donation", help="Record a donation")
    don_parser.add_argument("--donor-id", required=True, help="Donor ID")
    don_parser.add_argument("--amount", type=float, required=True, help="Donation amount")
    don_parser.add_argument("--campaign", default="General", help="Campaign name")
    don_parser.add_argument("--payment-method", default="Unknown", help="Payment method")
    don_parser.add_argument("--notes", default="", help="Notes")
    don_parser.add_argument("--recurring", action="store_true", help="Recurring donation")

    # List Donors
    list_parser = subparsers.add_parser("list", help="List all donors")
    list_parser.add_argument("--tier", choices=["Bronze", "Silver", "Gold", "Platinum"], help="Filter by tier")
    list_parser.add_argument("--sort", choices=["name", "total", "recent"], default="name", help="Sort by")

    # Get Donor
    get_parser = subparsers.add_parser("get", help="Get donor details")
    get_parser.add_argument("--donor-id", required=True, help="Donor ID")

    # Find Donor
    find_parser = subparsers.add_parser("find", help="Find donor by email")
    find_parser.add_argument("--email", required=True, help="Email address")

    # Statistics
    subparsers.add_parser("stats", help="Get donation statistics")

    # Report
    report_parser = subparsers.add_parser("report", help="Generate donor report")
    report_parser.add_argument("--output", type=Path, help="Output file path")

    # Export
    export_parser = subparsers.add_parser("export", help="Export donors to CSV")
    export_parser.add_argument("--output", type=Path, required=True, help="Output CSV file path")

    # Update Donor
    update_parser = subparsers.add_parser("update", help="Update donor")
    update_parser.add_argument("--donor-id", required=True, help="Donor ID")
    update_parser.add_argument("--name", help="New name")
    update_parser.add_argument("--email", help="New email")
    update_parser.add_argument("--phone", help="New phone")
    update_parser.add_argument("--notes", help="New notes")
    update_parser.add_argument("--tags", nargs="*", help="New tags")

    # Delete Donor
    delete_parser = subparsers.add_parser("delete", help="Delete donor")
    delete_parser.add_argument("--donor-id", required=True, help="Donor ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    manager = DonorManager()

    try:
        if args.command == "add-donor":
            donor = manager.add_donor(args.name, args.email, args.phone, args.notes, args.tags)
            print(f"✓ Donor added: {donor.id}")
            print(f"  Name: {donor.name}")
            print(f"  Email: {donor.email}")
            print(f"  Tier: {donor.donor_tier}")

        elif args.command == "add-donation":
            donation = manager.add_donation(
                args.donor_id, args.amount, args.campaign,
                args.payment_method, args.notes, args.recurring
            )
            if donation:
                print(f"✓ Donation recorded: {donation.id}")
                print(f"  Amount: ${args.amount:.2f}")
                print(f"  Campaign: {args.campaign}")
            else:
                print(f"✗ Failed to record donation")
                sys.exit(1)

        elif args.command == "list":
            donors = manager.list_donors(args.tier, args.sort)
            if not donors:
                print("No donors found.")
            else:
                print(f"\n{'Name':<25} {'Email':<30} {'Tier':<10} {'Total':<12} {'Donations'}")
                print("-" * 90)
                for d in donors:
                    print(f"{d.name:<25} {d.email:<30} {d.donor_tier:<10} ${d.donation_total:<11,.2f} {d.donation_count}")

        elif args.command == "get":
            donor = manager.get_donor(args.donor_id)
            if donor:
                print(f"\n{'='*50}")
                print(f"DONOR DETAILS: {donor.id}")
                print(f"{'='*50}")
                print(f"Name: {donor.name}")
                print(f"Email: {donor.email}")
                print(f"Phone: {donor.phone}")
                print(f"Tier: {donor.donor_tier}")
                print(f"Total Donations: ${donor.donation_total:,.2f}")
                print(f"Donation Count: {donor.donation_count}")
                print(f"First Donation: {donor.first_donation_date or 'N/A'}")
                print(f"Last Donation: {donor.last_donation_date or 'N/A'}")
                print(f"Tags: {', '.join(donor.tags) or 'None'}")
                print(f"Notes: {donor.notes or 'None'}")
                print(f"Created: {donor.created_at}")
                print(f"Updated: {donor.updated_at}")
            else:
                print(f"✗ Donor not found: {args.donor_id}")
                sys.exit(1)

        elif args.command == "find":
            donor = manager.find_donor_by_email(args.email)
            if donor:
                print(f"✓ Found donor: {donor.id}")
                print(f"  Name: {donor.name}")
                print(f"  Email: {donor.email}")
                print(f"  Tier: {donor.donor_tier}")
                print(f"  Total: ${donor.donation_total:,.2f}")
            else:
                print(f"✗ No donor found with email: {args.email}")
                sys.exit(1)

        elif args.command == "stats":
            stats = manager.get_statistics()
            print(f"\n{'='*50}")
            print("DONATION STATISTICS")
            print(f"{'='*50}")
            print(f"Total Donors: {stats['total_donors']}")
            print(f"Total Donations: {stats['total_donations']}")
            print(f"Total Amount: ${stats['total_amount']:,.2f}")
            print(f"Average Donation: ${stats['average_donation']:.2f}")
            print(f"Monthly Average: ${stats['monthly_average']:.2f}")
            print(f"Last 30 Days: ${stats['donations_last_30_days']:,.2f}")
            print("\nTier Distribution:")
            for tier, count in stats['tier_distribution'].items():
                print(f"  {tier}: {count}")

        elif args.command == "report":
            report = manager.generate_donor_report(args.output)
            if args.output:
                print(f"✓ Report saved to {args.output}")
            else:
                print(report)

        elif args.command == "export":
            if manager.export_csv(args.output):
                print(f"✓ Exported {len(manager.donors)} donors to {args.output}")
            else:
                print("✗ Export failed")
                sys.exit(1)

        elif args.command == "update":
            kwargs = {k: v for k, v in vars(args).items() if k != "command" and k != "donor_id" and v is not None}
            donor = manager.update_donor(args.donor_id, **kwargs)
            if donor:
                print(f"✓ Donor updated: {donor.id}")
            else:
                print(f"✗ Update failed")
                sys.exit(1)

        elif args.command == "delete":
            if manager.delete_donor(args.donor_id):
                print(f"✓ Donor deleted: {args.donor_id}")
            else:
                print(f"✗ Delete failed")
                sys.exit(1)

    except Exception as e:
        logger.exception(f"Error executing command: {e}")
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
