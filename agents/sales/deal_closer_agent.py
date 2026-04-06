#!/usr/bin/env python3
"""
Deal Closer Agent
==================
Manages deal pipeline, tracks deal progress, and helps close deals.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
import hashlib

# Setup paths
AGENT_DIR = Path(__file__).parent
WORKSPACE = AGENT_DIR.parent.parent
LOG_DIR = WORKSPACE / "logs"
DATA_DIR = AGENT_DIR.parent.parent / "data"

LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "deal_closer.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("DealCloser")


class Deal:
    """Represents a sales deal."""
    
    STAGES = ["discovery", "qualification", "proposal", "negotiation", "closing", "won", "lost"]
    
    def __init__(self, title: str, value: float, prospect_id: str,
                 company: str = "", contact_name: str = "", contact_email: str = "",
                 stage: str = "discovery", probability: int = 10,
                 expected_close: str = "", notes: str = "",
                 discount: float = 0, owner: str = "system"):
        self.id = self._generate_id(title, company)
        self.title = title
        self.value = value
        self.prospect_id = prospect_id
        self.company = company
        self.contact_name = contact_name
        self.contact_email = contact_email
        self.stage = stage
        self.probability = probability
        self.expected_close = expected_close
        self.notes = notes
        self.discount = discount
        self.owner = owner
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.closed_at = None
        self.stage_history = [{"stage": stage, "timestamp": datetime.now().isoformat()}]
    
    def _generate_id(self, title: str, company: str) -> str:
        raw = f"{title}{company}{datetime.now().isoformat()}"
        return hashlib.md5(raw.encode()).hexdigest()[:12]
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "value": self.value,
            "prospect_id": self.prospect_id,
            "company": self.company,
            "contact_name": self.contact_name,
            "contact_email": self.contact_email,
            "stage": self.stage,
            "probability": self.probability,
            "expected_close": self.expected_close,
            "notes": self.notes,
            "discount": self.discount,
            "owner": self.owner,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "closed_at": self.closed_at,
            "stage_history": self.stage_history
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Deal':
        d = cls(
            title=data.get("title", ""),
            value=data.get("value", 0),
            prospect_id=data.get("prospect_id", ""),
            company=data.get("company", ""),
            contact_name=data.get("contact_name", ""),
            contact_email=data.get("contact_email", ""),
            stage=data.get("stage", "discovery"),
            probability=data.get("probability", 10),
            expected_close=data.get("expected_close", ""),
            notes=data.get("notes", ""),
            discount=data.get("discount", 0),
            owner=data.get("owner", "system")
        )
        for key in ["id", "created_at", "updated_at", "closed_at", "stage_history"]:
            if key in data:
                setattr(d, key, data[key])
        return d
    
    def move_stage(self, new_stage: str) -> bool:
        """Move deal to new stage."""
        if new_stage not in self.STAGES:
            logger.error(f"Invalid stage: {new_stage}")
            return False
        
        old_stage = self.stage
        self.stage = new_stage
        self.updated_at = datetime.now().isoformat()
        
        # Update probability based on stage
        stage_probs = {
            "discovery": 10, "qualification": 25, "proposal": 50,
            "negotiation": 75, "closing": 90, "won": 100, "lost": 0
        }
        self.probability = stage_probs.get(new_stage, self.probability)
        
        # Record stage history
        self.stage_history.append({
            "stage": new_stage,
            "timestamp": datetime.now().isoformat(),
            "from_stage": old_stage
        })
        
        # Set closed date if terminal stage
        if new_stage in ["won", "lost"]:
            self.closed_at = datetime.now().isoformat()
        
        logger.info(f"Deal {self.id} moved: {old_stage} -> {new_stage}")
        return True
    
    def get_weighted_value(self) -> float:
        """Get probability-weighted deal value."""
        return self.value * (self.probability / 100)
    
    def apply_discount(self, discount_percent: float) -> float:
        """Apply discount and return new value."""
        if not 0 <= discount_percent <= 100:
            raise ValueError("Discount must be between 0 and 100")
        
        self.discount = discount_percent
        self.value = self.value * (1 - discount_percent / 100)
        self.updated_at = datetime.now().isoformat()
        return self.value


class DealStore:
    """Manages deal data persistence."""
    
    def __init__(self, data_file: Optional[Path] = None):
        self.data_file = data_file or (DATA_DIR / "deals.json")
        self.deals = []
        self._load()
    
    def _load(self):
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.deals = [Deal.from_dict(d) for d in data.get("deals", [])]
                logger.info(f"Loaded {len(self.deals)} deals")
            except Exception as e:
                logger.error(f"Failed to load deals: {e}")
                self.deals = []
        else:
            self.deals = []
    
    def _save(self):
        try:
            data = {
                "deals": [d.to_dict() for d in self.deals],
                "updated_at": datetime.now().isoformat()
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.deals)} deals")
        except Exception as e:
            logger.error(f"Failed to save deals: {e}")
            raise
    
    def add_deal(self, deal: Deal) -> bool:
        """Add new deal."""
        for existing in self.deals:
            if existing.id == deal.id:
                logger.warning(f"Deal already exists: {deal.id}")
                return False
        
        self.deals.append(deal)
        self._save()
        logger.info(f"Added deal: {deal.title} ({deal.id})")
        return True
    
    def get_deal(self, deal_id: str) -> Optional[Deal]:
        for d in self.deals:
            if d.id == deal_id:
                return d
        return None
    
    def update_deal(self, deal_id: str, updates: dict) -> bool:
        for d in self.deals:
            if d.id == deal_id:
                for key, value in updates.items():
                    if hasattr(d, key) and key not in ["id", "created_at"]:
                        if key == "stage" and value != d.stage:
                            d.move_stage(value)
                        else:
                            setattr(d, key, value)
                d.updated_at = datetime.now().isoformat()
                self._save()
                return True
        return False
    
    def delete_deal(self, deal_id: str) -> bool:
        self.deals = [d for d in self.deals if d.id != deal_id]
        self._save()
        return True
    
    def list_deals(self, stage: Optional[str] = None, 
                   include_closed: bool = True) -> List[Deal]:
        deals = self.deals
        
        if stage:
            deals = [d for d in deals if d.stage == stage]
        elif not include_closed:
            deals = [d for d in deals if d.stage not in ["won", "lost"]]
        
        return sorted(deals, key=lambda x: x.value, reverse=True)
    
    def get_stats(self) -> dict:
        """Get deal pipeline statistics."""
        active = [d for d in self.deals if d.stage not in ["won", "lost"]]
        won = [d for d in self.deals if d.stage == "won"]
        lost = [d for d in self.deals if d.stage == "lost"]
        
        pipeline_value = sum(d.value for d in active)
        weighted_value = sum(d.get_weighted_value() for d in active)
        won_value = sum(d.value for d in won)
        
        by_stage = {}
        for d in self.deals:
            by_stage[d.stage] = by_stage.get(d.stage, 0) + 1
        
        return {
            "total_deals": len(self.deals),
            "active_deals": len(active),
            "won_deals": len(won),
            "lost_deals": len(lost),
            "pipeline_value": pipeline_value,
            "weighted_value": weighted_value,
            "won_value": won_value,
            "win_rate": round(len(won) / len(self.deals) * 100, 1) if self.deals else 0,
            "by_stage": by_stage,
            "avg_deal_size": round(pipeline_value / len(active), 2) if active else 0
        }
    
    def get_forecast(self, days: int = 30) -> dict:
        """Get deal forecast for next N days."""
        forecast_date = datetime.now() + timedelta(days=days)
        forecast_deals = []
        
        for d in self.deals:
            if d.stage not in ["won", "lost"] and d.expected_close:
                try:
                    close_date = datetime.fromisoformat(d.expected_close)
                    if close_date <= forecast_date:
                        forecast_deals.append(d)
                except:
                    pass
        
        total_value = sum(d.value for d in forecast_deals)
        weighted_value = sum(d.get_weighted_value() for d in forecast_deals)
        
        return {
            "forecast_days": days,
            "deal_count": len(forecast_deals),
            "total_value": total_value,
            "weighted_value": weighted_value,
            "deals": [d.to_dict() for d in forecast_deals]
        }


class DealCloser:
    """Main deal closer agent."""
    
    def __init__(self):
        self.store = DealStore()
        logger.info("DealCloser initialized")
    
    def create_deal(self, data: dict) -> Optional[Deal]:
        """Create deal from dictionary."""
        try:
            deal = Deal(
                title=data.get("title", ""),
                value=float(data.get("value", 0)),
                prospect_id=data.get("prospect_id", ""),
                company=data.get("company", ""),
                contact_name=data.get("contact_name", ""),
                contact_email=data.get("contact_email", ""),
                stage=data.get("stage", "discovery"),
                probability=int(data.get("probability", 10)),
                expected_close=data.get("expected_close", ""),
                notes=data.get("notes", ""),
                owner=data.get("owner", "system")
            )
            self.store.add_deal(deal)
            return deal
        except Exception as e:
            logger.error(f"Failed to create deal: {e}")
            return None
    
    def advance_deal(self, deal_id: str, notes: str = "") -> bool:
        """Advance deal to next stage."""
        deal = self.store.get_deal(deal_id)
        if not deal:
            logger.error(f"Deal not found: {deal_id}")
            return False
        
        stage_order = Deal.STAGES[:-2]  # Exclude won/lost
        if deal.stage in stage_order:
            current_idx = stage_order.index(deal.stage)
            next_stage = stage_order[current_idx + 1]
            
            if notes:
                deal.notes = (deal.notes + "\n" + notes).strip()
            
            return deal.move_stage(next_stage)
        
        logger.warning(f"Cannot advance deal in stage: {deal.stage}")
        return False
    
    def close_deal(self, deal_id: str, won: bool, notes: str = "") -> bool:
        """Close deal as won or lost."""
        deal = self.store.get_deal(deal_id)
        if not deal:
            return False
        
        new_stage = "won" if won else "lost"
        
        if notes:
            deal.notes = (deal.notes + "\n" + notes).strip()
        
        return deal.move_stage(new_stage)
    
    def apply_discount(self, deal_id: str, discount_percent: float) -> Optional[float]:
        """Apply discount to deal."""
        deal = self.store.get_deal(deal_id)
        if not deal:
            return None
        
        try:
            return deal.apply_discount(discount_percent)
        except ValueError as e:
            logger.error(f"Discount error: {e}")
            return None


def main():
    parser = argparse.ArgumentParser(
        description="Deal Closer Agent - Manage sales deals and close pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --create '{"title": "Acme Enterprise Deal", "value": 50000, "company": "Acme Inc", "contact_email": "buyer@acme.com", "expected_close": "2026-04-15"}'
  %(prog)s --list
  %(prog)s --list --stage negotiation
  %(prog)s --advance abc123 --notes "Sent revised proposal"
  %(prog)s --close abc123 --won --notes "Signed contract!"
  %(prog)s --close abc123 --lost --notes "Went with competitor"
  %(prog)s --discount abc123 15
  %(prog)s --stats
  %(prog)s --forecast --days 30
  %(prog)s --get abc123
  %(prog)s --delete abc123
        """
    )
    
    parser.add_argument("--create", type=str, help="Create deal from JSON")
    parser.add_argument("--list", action="store_true", help="List all deals")
    parser.add_argument("--stage", type=str, help="Filter by stage")
    parser.add_argument("--advance", type=str, help="Advance deal to next stage")
    parser.add_argument("--notes", type=str, default="", help="Notes for stage change")
    parser.add_argument("--close", type=str, help="Close deal by ID")
    parser.add_argument("--won", action="store_true", help="Close as won")
    parser.add_argument("--lost", action="store_true", help="Close as lost")
    parser.add_argument("--discount", type=float, help="Apply discount %% to deal")
    parser.add_argument("--stats", action="store_true", help="Show pipeline statistics")
    parser.add_argument("--forecast", action="store_true", help="Show deal forecast")
    parser.add_argument("--days", type=int, default=30, help="Forecast days (default: 30)")
    parser.add_argument("--get", type=str, help="Get deal by ID")
    parser.add_argument("--delete", type=str, help="Delete deal by ID")
    
    args = parser.parse_args()
    closer = DealCloser()
    
    try:
        if args.create:
            data = json.loads(args.create)
            deal = closer.create_deal(data)
            if deal:
                print(json.dumps({"success": True, "deal_id": deal.id, "deal": deal.to_dict()}))
            else:
                print(json.dumps({"success": False, "message": "Failed to create deal"}))
        
        elif args.list:
            deals = closer.store.list_deals(stage=args.stage)
            output = [d.to_dict() for d in deals]
            print(json.dumps({"count": len(output), "deals": output}, indent=2))
        
        elif args.advance:
            if closer.advance_deal(args.advance, args.notes):
                deal = closer.store.get_deal(args.advance)
                print(json.dumps({"success": True, "deal": deal.to_dict()}))
            else:
                print(json.dumps({"success": False, "message": "Failed to advance deal"}))
        
        elif args.close:
            if args.won and args.lost:
                print(json.dumps({"success": False, "message": "Choose --won or --lost, not both"}))
                sys.exit(1)
            
            won = args.won if args.won else False
            if closer.close_deal(args.close, won, args.notes):
                deal = closer.store.get_deal(args.close)
                print(json.dumps({"success": True, "deal": deal.to_dict()}))
            else:
                print(json.dumps({"success": False, "message": "Failed to close deal"}))
        
        elif args.discount:
            if not args.close:
                print(json.dumps({"success": False, "message": "--close required with --discount"}))
                sys.exit(1)
            
            new_value = closer.apply_discount(args.close, args.discount)
            if new_value is not None:
                print(json.dumps({"success": True, "new_value": new_value}))
            else:
                print(json.dumps({"success": False, "message": "Failed to apply discount"}))
        
        elif args.stats:
            stats = closer.store.get_stats()
            print(json.dumps(stats, indent=2))
        
        elif args.forecast:
            forecast = closer.store.get_forecast(days=args.days)
            print(json.dumps(forecast, indent=2))
        
        elif args.get:
            deal = closer.store.get_deal(args.get)
            if deal:
                print(json.dumps(deal.to_dict(), indent=2))
            else:
                print(json.dumps({"success": False, "message": "Deal not found"}))
        
        elif args.delete:
            success = closer.store.delete_deal(args.delete)
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
