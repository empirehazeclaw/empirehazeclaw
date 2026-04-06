#!/usr/bin/env python3
"""
Proposal Generator Agent
========================
Generates sales proposals and quotes for potential customers.
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
OUTPUT_DIR = WORKSPACE / "proposals"

LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "proposal_generator.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ProposalGenerator")


class LineItem:
    """Represents a line item in a proposal."""
    
    def __init__(self, description: str, quantity: int, unit_price: float,
                 discount: float = 0, tax_rate: float = 0):
        self.description = description
        self.quantity = quantity
        self.unit_price = unit_price
        self.discount = discount
        self.tax_rate = tax_rate
    
    @property
    def subtotal(self) -> float:
        return self.quantity * self.unit_price
    
    @property
    def discount_amount(self) -> float:
        return self.subtotal * (self.discount / 100)
    
    @property
    def tax_amount(self) -> float:
        return (self.subtotal - self.discount_amount) * (self.tax_rate / 100)
    
    @property
    def total(self) -> float:
        return self.subtotal - self.discount_amount + self.tax_amount
    
    def to_dict(self) -> dict:
        return {
            "description": self.description,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "discount": self.discount,
            "tax_rate": self.tax_rate,
            "subtotal": self.subtotal,
            "discount_amount": self.discount_amount,
            "tax_amount": self.tax_amount,
            "total": self.total
        }


class Proposal:
    """Represents a sales proposal."""
    
    CURRENCIES = ["USD", "EUR", "GBP"]
    STATUSES = ["draft", "sent", "viewed", "accepted", "rejected", "expired"]
    
    def __init__(self, prospect_name: str, prospect_email: str,
                 company: str = "", title: str = "",
                 items: List[dict] = None, currency: str = "USD",
                 valid_days: int = 30, notes: str = "",
                 payment_terms: str = "Net 30", delivery: str = ""):
        self.id = self._generate_id()
        self.prospect_name = prospect_name
        self.prospect_email = prospect_email
        self.company = company
        self.title = title
        self.items = [LineItem(**i) if isinstance(i, dict) else i for i in (items or [])]
        self.currency = currency
        self.valid_days = valid_days
        self.notes = notes
        self.payment_terms = payment_terms
        self.delivery = delivery
        self.status = "draft"
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.sent_at = None
        self.viewed_at = None
        self.accepted_at = None
        self.rejected_at = None
    
    def _generate_id(self) -> str:
        raw = f"{datetime.now().isoformat()}"
        return "prop_" + hashlib.md5(raw.encode()).hexdigest()[:10]
    
    @property
    def subtotal(self) -> float:
        return sum(item.subtotal for item in self.items)
    
    @property
    def total_discount(self) -> float:
        return sum(item.discount_amount for item in self.items)
    
    @property
    def total_tax(self) -> float:
        return sum(item.tax_amount for item in self.items)
    
    @property
    def total(self) -> float:
        return sum(item.total for item in self.items)
    
    @property
    def valid_until(self) -> str:
        try:
            created = datetime.fromisoformat(self.created_at)
            return (created + timedelta(days=self.valid_days)).isoformat()
        except:
            return ""
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "prospect_name": self.prospect_name,
            "prospect_email": self.prospect_email,
            "company": self.company,
            "title": self.title,
            "items": [item.to_dict() if isinstance(item, LineItem) else item for item in self.items],
            "currency": self.currency,
            "subtotal": self.subtotal,
            "total_discount": self.total_discount,
            "total_tax": self.total_tax,
            "total": self.total,
            "valid_days": self.valid_days,
            "valid_until": self.valid_until,
            "notes": self.notes,
            "payment_terms": self.payment_terms,
            "delivery": self.delivery,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "sent_at": self.sent_at,
            "viewed_at": self.viewed_at,
            "accepted_at": self.accepted_at,
            "rejected_at": self.rejected_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Proposal':
        # Filter out computed fields from items dict before passing to LineItem
        computed_fields = {"subtotal", "discount_amount", "tax_amount", "total"}
        items = []
        for i in data.get("items", []):
            if isinstance(i, dict):
                filtered = {k: v for k, v in i.items() if k not in computed_fields}
                items.append(LineItem(**filtered))
            else:
                items.append(i)
        p = cls(
            prospect_name=data.get("prospect_name", ""),
            prospect_email=data.get("prospect_email", ""),
            company=data.get("company", ""),
            title=data.get("title", ""),
            items=items,
            currency=data.get("currency", "USD"),
            valid_days=data.get("valid_days", 30),
            notes=data.get("notes", ""),
            payment_terms=data.get("payment_terms", "Net 30"),
            delivery=data.get("delivery", "")
        )
        for key in ["id", "status", "created_at", "updated_at", "sent_at", "viewed_at", "accepted_at", "rejected_at"]:
            if key in data:
                setattr(p, key, data[key])
        return p
    
    def send(self):
        self.status = "sent"
        self.sent_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        logger.info(f"Proposal {self.id} sent")
    
    def mark_viewed(self):
        self.status = "viewed"
        self.viewed_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        logger.info(f"Proposal {self.id} viewed")
    
    def accept(self):
        self.status = "accepted"
        self.accepted_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        logger.info(f"Proposal {self.id} accepted")
    
    def reject(self):
        self.status = "rejected"
        self.rejected_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        logger.info(f"Proposal {self.id} rejected")
    
    def generate_text(self) -> str:
        """Generate plain text proposal."""
        currency_symbol = {"USD": "$", "EUR": "€", "GBP": "£"}.get(self.currency, "$")
        
        lines = [
            "=" * 60,
            "SALES PROPOSAL",
            "=" * 60,
            "",
            f"Proposal #: {self.id}",
            f"Date: {self.created_at[:10]}",
            f"Valid Until: {self.valid_until[:10]}",
            "",
            "-" * 40,
            "TO:",
            f"  {self.prospect_name}",
            f"  {self.company}",
            f"  {self.prospect_email}",
            "",
            "-" * 40,
            "PROPOSAL DETAILS:",
            f"  {self.title}",
            "",
            "-" * 40,
            "LINE ITEMS:",
            ""
        ]
        
        for i, item in enumerate(self.items, 1):
            lines.append(f"  {i}. {item.description}")
            lines.append(f"     Qty: {item.quantity} x {currency_symbol}{item.unit_price:.2f}")
            if item.discount > 0:
                lines.append(f"     Discount: {item.discount}%")
            lines.append(f"     Total: {currency_symbol}{item.total:.2f}")
            lines.append("")
        
        lines.extend([
            "-" * 40,
            "SUMMARY:",
            f"  Subtotal:    {currency_symbol}{self.subtotal:.2f}",
            f"  Discounts:   -{currency_symbol}{self.total_discount:.2f}",
            f"  Tax:          {currency_symbol}{self.total_tax:.2f}",
            f"  {'=' * 30}",
            f"  TOTAL:        {currency_symbol}{self.total:.2f}",
            "",
            "-" * 40,
            "TERMS:",
            f"  Payment Terms: {self.payment_terms}",
            f"  Delivery: {self.delivery or 'Per agreement'}",
            "",
            f"  {self.notes}",
            "",
            "=" * 60,
            f"Status: {self.status.upper()}",
            "=" * 60
        ])
        
        return "\n".join(lines)


class ProposalStore:
    """Manages proposal data persistence."""
    
    def __init__(self, data_file: Optional[Path] = None):
        self.data_file = data_file or (DATA_DIR / "proposals.json")
        self.proposals = []
        self._load()
    
    def _load(self):
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.proposals = [Proposal.from_dict(p) for p in data.get("proposals", [])]
                logger.info(f"Loaded {len(self.proposals)} proposals")
            except Exception as e:
                logger.error(f"Failed to load proposals: {e}")
                self.proposals = []
        else:
            self.proposals = []
    
    def _save(self):
        try:
            data = {
                "proposals": [p.to_dict() for p in self.proposals],
                "updated_at": datetime.now().isoformat()
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.proposals)} proposals")
        except Exception as e:
            logger.error(f"Failed to save proposals: {e}")
            raise
    
    def add_proposal(self, proposal: Proposal) -> bool:
        for existing in self.proposals:
            if existing.id == proposal.id:
                return False
        self.proposals.append(proposal)
        self._save()
        return True
    
    def get_proposal(self, proposal_id: str) -> Optional[Proposal]:
        for p in self.proposals:
            if p.id == proposal_id:
                return p
        return None
    
    def update_proposal(self, proposal_id: str, updates: dict) -> bool:
        for p in self.proposals:
            if p.id == proposal_id:
                for key, value in updates.items():
                    if hasattr(p, key) and key not in ["id", "created_at"]:
                        setattr(p, key, value)
                p.updated_at = datetime.now().isoformat()
                self._save()
                return True
        return False
    
    def delete_proposal(self, proposal_id: str) -> bool:
        self.proposals = [p for p in self.proposals if p.id != proposal_id]
        self._save()
        return True
    
    def list_proposals(self, status: Optional[str] = None) -> List[Proposal]:
        proposals = self.proposals
        if status:
            proposals = [p for p in proposals if p.status == status]
        return sorted(proposals, key=lambda x: x.created_at, reverse=True)
    
    def get_stats(self) -> dict:
        total = len(self.proposals)
        by_status = {}
        total_value = 0
        for p in self.proposals:
            by_status[p.status] = by_status.get(p.status, 0) + 1
            total_value += p.total
        
        accepted_value = sum(p.total for p in self.proposals if p.status == "accepted")
        avg_proposal = total_value / total if total else 0
        
        return {
            "total_proposals": total,
            "by_status": by_status,
            "total_value": total_value,
            "accepted_value": accepted_value,
            "average_proposal_value": round(avg_proposal, 2),
            "conversion_rate": round(by_status.get("accepted", 0) / total * 100, 1) if total else 0
        }


class ProposalGenerator:
    """Main proposal generator agent."""
    
    def __init__(self):
        self.store = ProposalStore()
        logger.info("ProposalGenerator initialized")
    
    def create_proposal(self, data: dict) -> Optional[Proposal]:
        """Create proposal from dictionary."""
        try:
            proposal = Proposal(
                prospect_name=data.get("prospect_name", ""),
                prospect_email=data.get("prospect_email", ""),
                company=data.get("company", ""),
                title=data.get("title", ""),
                items=data.get("items", []),
                currency=data.get("currency", "USD"),
                valid_days=data.get("valid_days", 30),
                notes=data.get("notes", ""),
                payment_terms=data.get("payment_terms", "Net 30"),
                delivery=data.get("delivery", "")
            )
            self.store.add_proposal(proposal)
            logger.info(f"Created proposal {proposal.id} for {proposal.company}")
            return proposal
        except Exception as e:
            logger.error(f"Failed to create proposal: {e}")
            return None
    
    def send_proposal(self, proposal_id: str) -> bool:
        proposal = self.store.get_proposal(proposal_id)
        if not proposal:
            return False
        proposal.send()
        self.store._save()
        return True
    
    def accept_proposal(self, proposal_id: str) -> bool:
        proposal = self.store.get_proposal(proposal_id)
        if not proposal:
            return False
        proposal.accept()
        self.store._save()
        return True
    
    def reject_proposal(self, proposal_id: str) -> bool:
        proposal = self.store.get_proposal(proposal_id)
        if not proposal:
            return False
        proposal.reject()
        self.store._save()
        return True
    
    def mark_viewed(self, proposal_id: str) -> bool:
        proposal = self.store.get_proposal(proposal_id)
        if not proposal:
            return False
        proposal.mark_viewed()
        self.store._save()
        return True
    
    def export_text(self, proposal_id: str, output_file: Path = None) -> Optional[str]:
        """Export proposal as text file."""
        proposal = self.store.get_proposal(proposal_id)
        if not proposal:
            return None
        
        text = proposal.generate_text()
        
        if output_file:
            output_file.write_text(text)
            logger.info(f"Exported proposal to {output_file}")
        elif output_file is None:
            # Save to default location
            out_path = OUTPUT_DIR / f"{proposal_id}.txt"
            out_path.write_text(text)
            logger.info(f"Exported proposal to {out_path}")
            return str(out_path)
        
        return text
    
    def generate_summary(self, proposal_id: str) -> Optional[dict]:
        """Generate proposal summary for email."""
        proposal = self.store.get_proposal(proposal_id)
        if not proposal:
            return None
        
        currency_symbol = {"USD": "$", "EUR": "€", "GBP": "£"}.get(proposal.currency, "$")
        
        return {
            "proposal_id": proposal.id,
            "to": proposal.prospect_email,
            "subject": f"Proposal: {proposal.title}",
            "summary": f"""Proposal for {proposal.company}
Total Value: {currency_symbol}{proposal.total:.2f}
Valid Until: {proposal.valid_until[:10]}
Status: {proposal.status}"""
        }


def main():
    parser = argparse.ArgumentParser(
        description="Proposal Generator Agent - Create and manage sales proposals",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --create '{"prospect_name": "John Doe", "prospect_email": "john@acme.com", "company": "Acme Inc", "title": "Enterprise License", "items": [{"description": "SaaS License (100 users)", "quantity": 1, "unit_price": 5000}]}'
  %(prog)s --list
  %(prog)s --list --status draft
  %(prog)s --get prop_abc123
  %(prog)s --send prop_abc123
  %(prog)s --accept prop_abc123
  %(prog)s --reject prop_abc123
  %(prog)s --viewed prop_abc123
  %(prog)s --export prop_abc123
  %(prog)s --text prop_abc123
  %(prog)s --stats
  %(prog)s --delete prop_abc123
        """
    )
    
    parser.add_argument("--create", type=str, help="Create proposal from JSON")
    parser.add_argument("--list", action="store_true", help="List all proposals")
    parser.add_argument("--status", type=str, help="Filter by status")
    parser.add_argument("--get", type=str, help="Get proposal by ID")
    parser.add_argument("--send", type=str, help="Mark proposal as sent")
    parser.add_argument("--accept", type=str, help="Mark proposal as accepted")
    parser.add_argument("--reject", type=str, help="Mark proposal as rejected")
    parser.add_argument("--viewed", type=str, help="Mark proposal as viewed")
    parser.add_argument("--export", type=str, help="Export proposal to file")
    parser.add_argument("--text", type=str, help="Generate text representation")
    parser.add_argument("--summary", type=str, help="Generate summary for email")
    parser.add_argument("--stats", action="store_true", help="Show proposal statistics")
    parser.add_argument("--delete", type=str, help="Delete proposal by ID")
    
    args = parser.parse_args()
    generator = ProposalGenerator()
    
    try:
        if args.create:
            data = json.loads(args.create)
            proposal = generator.create_proposal(data)
            if proposal:
                print(json.dumps({"success": True, "proposal": proposal.to_dict()}))
            else:
                print(json.dumps({"success": False, "message": "Failed to create proposal"}))
        
        elif args.list:
            proposals = generator.store.list_proposals(status=args.status)
            output = [p.to_dict() for p in proposals]
            print(json.dumps({"count": len(output), "proposals": output}, indent=2))
        
        elif args.get:
            proposal = generator.store.get_proposal(args.get)
            if proposal:
                print(json.dumps(proposal.to_dict(), indent=2))
            else:
                print(json.dumps({"success": False, "message": "Proposal not found"}))
        
        elif args.send:
            if generator.send_proposal(args.send):
                print(json.dumps({"success": True, "message": "Proposal marked as sent"}))
            else:
                print(json.dumps({"success": False, "message": "Proposal not found"}))
        
        elif args.accept:
            if generator.accept_proposal(args.accept):
                print(json.dumps({"success": True, "message": "Proposal accepted"}))
            else:
                print(json.dumps({"success": False, "message": "Proposal not found"}))
        
        elif args.reject:
            if generator.reject_proposal(args.reject):
                print(json.dumps({"success": True, "message": "Proposal rejected"}))
            else:
                print(json.dumps({"success": False, "message": "Proposal not found"}))
        
        elif args.viewed:
            if generator.mark_viewed(args.viewed):
                print(json.dumps({"success": True, "message": "Proposal marked as viewed"}))
            else:
                print(json.dumps({"success": False, "message": "Proposal not found"}))
        
        elif args.export:
            path = generator.export_proposal(args.export)
            if path:
                print(json.dumps({"success": True, "path": path}))
            else:
                print(json.dumps({"success": False, "message": "Proposal not found"}))
        
        elif args.text:
            text = generator.export_text(args.text)
            if text:
                print(text)
            else:
                print(json.dumps({"success": False, "message": "Proposal not found"}))
        
        elif args.summary:
            summary = generator.generate_summary(args.summary)
            if summary:
                print(json.dumps(summary, indent=2))
            else:
                print(json.dumps({"success": False, "message": "Proposal not found"}))
        
        elif args.stats:
            stats = generator.store.get_stats()
            print(json.dumps(stats, indent=2))
        
        elif args.delete:
            success = generator.store.delete_proposal(args.delete)
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
