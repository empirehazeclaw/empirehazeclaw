#!/usr/bin/env python3
"""
Sales Prospector Agent
======================
Finds and qualifies potential customers for sales pipeline.
Uses web search to identify prospects and qualify them based on criteria.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Setup paths
AGENT_DIR = Path(__file__).parent
WORKSPACE = AGENT_DIR.parent.parent
LOG_DIR = WORKSPACE / "logs"
DATA_DIR = AGENT_DIR.parent.parent / "data"

# Ensure directories exist
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "sales_prospector.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("SalesProspector")


class Prospect:
    """Represents a sales prospect."""
    
    def __init__(self, name: str, company: str, email: str = "", 
                 phone: str = "", title: str = "", industry: str = "",
                 company_size: str = "", website: str = "", 
                 linkedin: str = "", source: str = "", score: int = 0,
                 status: str = "new", notes: str = "", tags: list = None):
        self.name = name
        self.company = company
        self.email = email
        self.phone = phone
        self.title = title
        self.industry = industry
        self.company_size = company_size
        self.website = website
        self.linkedin = linkedin
        self.source = source
        self.score = score
        self.status = status
        self.notes = notes
        self.tags = tags or []
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique ID for prospect."""
        import hashlib
        raw = f"{self.name}{self.company}{datetime.now().isoformat()}"
        return hashlib.md5(raw.encode()).hexdigest()[:12]
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "company": self.company,
            "email": self.email,
            "phone": self.phone,
            "title": self.title,
            "industry": self.industry,
            "company_size": self.company_size,
            "website": self.website,
            "linkedin": self.linkedin,
            "source": self.source,
            "score": self.score,
            "status": self.status,
            "notes": self.notes,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Prospect':
        p = cls(
            name=data.get("name", ""),
            company=data.get("company", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            title=data.get("title", ""),
            industry=data.get("industry", ""),
            company_size=data.get("company_size", ""),
            website=data.get("website", ""),
            linkedin=data.get("linkedin", ""),
            source=data.get("source", ""),
            score=data.get("score", 0),
            status=data.get("status", "new"),
            notes=data.get("notes", ""),
            tags=data.get("tags", [])
        )
        if "id" in data:
            p.id = data["id"]
        if "created_at" in data:
            p.created_at = data["created_at"]
        p.updated_at = data.get("updated_at", datetime.now().isoformat())
        return p


class ProspectorStore:
    """Manages prospect data persistence."""
    
    def __init__(self, data_file: Optional[Path] = None):
        self.data_file = data_file or (DATA_DIR / "prospects.json")
        self.prospects = []
        self._load()
    
    def _load(self):
        """Load prospects from JSON file."""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.prospects = [Prospect.from_dict(p) for p in data.get("prospects", [])]
                logger.info(f"Loaded {len(self.prospects)} prospects from {self.data_file}")
            except Exception as e:
                logger.error(f"Failed to load prospects: {e}")
                self.prospects = []
        else:
            logger.info("No existing prospects file, starting fresh")
            self.prospects = []
    
    def _save(self):
        """Save prospects to JSON file."""
        try:
            data = {
                "prospects": [p.to_dict() for p in self.prospects],
                "updated_at": datetime.now().isoformat()
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.prospects)} prospects to {self.data_file}")
        except Exception as e:
            logger.error(f"Failed to save prospects: {e}")
            raise
    
    def add_prospect(self, prospect: Prospect) -> bool:
        """Add a new prospect."""
        # Check for duplicates
        for existing in self.prospects:
            if existing.email and prospect.email:
                if existing.email.lower() == prospect.email.lower():
                    logger.warning(f"Duplicate prospect found: {prospect.email}")
                    return False
        
        self.prospects.append(prospect)
        self._save()
        logger.info(f"Added prospect: {prospect.name} at {prospect.company}")
        return True
    
    def get_prospect(self, prospect_id: str) -> Optional[Prospect]:
        """Get prospect by ID."""
        for p in self.prospects:
            if p.id == prospect_id:
                return p
        return None
    
    def update_prospect(self, prospect_id: str, updates: dict) -> bool:
        """Update prospect fields."""
        for p in self.prospects:
            if p.id == prospect_id:
                for key, value in updates.items():
                    if hasattr(p, key):
                        setattr(p, key, value)
                p.updated_at = datetime.now().isoformat()
                self._save()
                logger.info(f"Updated prospect: {prospect_id}")
                return True
        return False
    
    def delete_prospect(self, prospect_id: str) -> bool:
        """Delete a prospect."""
        self.prospects = [p for p in self.prospects if p.id != prospect_id]
        self._save()
        logger.info(f"Deleted prospect: {prospect_id}")
        return True
    
    def list_prospects(self, status: Optional[str] = None, 
                       limit: int = 100) -> list:
        """List prospects, optionally filtered by status."""
        prospects = self.prospects
        if status:
            prospects = [p for p in prospects if p.status == status]
        return sorted(prospects, key=lambda x: x.score, reverse=True)[:limit]
    
    def get_stats(self) -> dict:
        """Get prospect statistics."""
        total = len(self.prospects)
        by_status = {}
        for p in self.prospects:
            by_status[p.status] = by_status.get(p.status, 0) + 1
        
        avg_score = sum(p.score for p in self.prospects) / total if total > 0 else 0
        
        return {
            "total": total,
            "by_status": by_status,
            "average_score": round(avg_score, 1),
            "top_industries": self._get_top_field("industry", 5),
            "top_sources": self._get_top_field("source", 5)
        }
    
    def _get_top_field(self, field: str, limit: int) -> list:
        """Get top values for a field."""
        counts = {}
        for p in self.prospects:
            val = getattr(p, field)
            if val:
                counts[val] = counts.get(val, 0) + 1
        return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:limit]


class SalesProspector:
    """Main prospector agent class."""
    
    # Qualification criteria weights
    INDUSTRY_SCORES = {
        "saas": 20, "software": 18, "technology": 15,
        "finance": 15, "healthcare": 12, "ecommerce": 10,
        "marketing": 8, "other": 5
    }
    
    COMPANY_SIZE_SCORES = {
        "enterprise": 25, "large": 20, "medium": 15,
        "small": 10, "startup": 8
    }
    
    TITLE_SCORES = {
        "ceo": 20, "cto": 18, "cfo": 15, "vp": 12,
        "director": 10, "manager": 8, "other": 5
    }
    
    def __init__(self):
        self.store = ProspectorStore()
        logger.info("SalesProspector initialized")
    
    def calculate_score(self, prospect: Prospect) -> int:
        """Calculate qualification score for prospect."""
        score = 0
        
        # Industry score
        industry_lower = prospect.industry.lower() if prospect.industry else ""
        for key, val in self.INDUSTRY_SCORES.items():
            if key in industry_lower:
                score += val
                break
        else:
            score += 5  # default
        
        # Company size score
        size_lower = prospect.company_size.lower() if prospect.company_size else ""
        for key, val in self.COMPANY_SIZE_SCORES.items():
            if key in size_lower:
                score += val
                break
        
        # Title score
        title_lower = prospect.title.lower() if prospect.title else ""
        for key, val in self.TITLE_SCORES.items():
            if key in title_lower:
                score += val
                break
        
        # Email validation bonus
        if prospect.email and "@" in prospect.email and "." in prospect.email:
            score += 5
        
        # Website bonus
        if prospect.website:
            score += 3
        
        # LinkedIn bonus
        if prospect.linkedin:
            score += 2
        
        return min(score, 100)  # Cap at 100
    
    def add_prospect_from_dict(self, data: dict) -> bool:
        """Add prospect from dictionary data."""
        try:
            prospect = Prospect(
                name=data.get("name", ""),
                company=data.get("company", ""),
                email=data.get("email", ""),
                phone=data.get("phone", ""),
                title=data.get("title", ""),
                industry=data.get("industry", ""),
                company_size=data.get("company_size", ""),
                website=data.get("website", ""),
                linkedin=data.get("linkedin", ""),
                source=data.get("source", "manual"),
                notes=data.get("notes", ""),
                tags=data.get("tags", [])
            )
            
            # Calculate score
            prospect.score = self.calculate_score(prospect)
            
            return self.store.add_prospect(prospect)
        except Exception as e:
            logger.error(f"Failed to add prospect: {e}")
            return False
    
    def qualify_prospect(self, prospect_id: str) -> Optional[dict]:
        """Qualify a prospect and update score."""
        prospect = self.store.get_prospect(prospect_id)
        if not prospect:
            logger.error(f"Prospect not found: {prospect_id}")
            return None
        
        # Recalculate score
        new_score = self.calculate_score(prospect)
        old_score = prospect.score
        
        self.store.update_prospect(prospect_id, {"score": new_score})
        
        # Determine qualification level
        if new_score >= 70:
            level = "hot"
        elif new_score >= 40:
            level = "warm"
        else:
            level = "cold"
        
        logger.info(f"Qualified {prospect.name}: {old_score} -> {new_score} ({level})")
        
        return {
            "prospect_id": prospect_id,
            "name": prospect.name,
            "old_score": old_score,
            "new_score": new_score,
            "level": level
        }
    
    def bulk_import(self, prospects_data: list) -> dict:
        """Bulk import prospects from list of dicts."""
        results = {"added": 0, "skipped": 0, "errors": 0}
        
        for data in prospects_data:
            if self.add_prospect_from_dict(data):
                results["added"] += 1
            else:
                results["skipped"] += 1
        
        return results


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Sales Prospector Agent - Find and qualify potential customers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --add '{"name": "John Doe", "company": "Acme Inc", "email": "john@acme.com", "title": "CEO", "industry": "saas"}'
  %(prog)s --list --status new --limit 10
  %(prog)s --qualify abc123
  %(prog)s --stats
  %(prog)s --import prospects.json
  %(prog)s --update abc123 --status contacted --score 75
  %(prog)s --delete abc123
        """
    )
    
    parser.add_argument("--add", type=str, help="Add prospect from JSON string")
    parser.add_argument("--list", action="store_true", help="List all prospects")
    parser.add_argument("--status", type=str, help="Filter by status (new/contacted/qualified/proposal/closed)")
    parser.add_argument("--limit", type=int, default=100, help="Limit number of prospects (default: 100)")
    parser.add_argument("--qualify", type=str, help="Qualify prospect by ID")
    parser.add_argument("--stats", action="store_true", help="Show prospect statistics")
    parser.add_argument("--import", dest="import_file", type=str, help="Import prospects from JSON file")
    parser.add_argument("--update", type=str, help="Update prospect by ID (use --set)")
    parser.add_argument("--set", type=str, help="JSON fields to update on prospect")
    parser.add_argument("--delete", type=str, help="Delete prospect by ID")
    parser.add_argument("--get", type=str, help="Get prospect details by ID")
    
    args = parser.parse_args()
    
    prospector = SalesProspector()
    
    try:
        if args.add:
            # Add single prospect
            data = json.loads(args.add)
            if prospector.add_prospect_from_dict(data):
                print(json.dumps({"success": True, "message": "Prospect added"}))
            else:
                print(json.dumps({"success": False, "message": "Failed to add prospect (duplicate?)"}))
        
        elif args.list:
            # List prospects
            prospects = prospector.store.list_prospects(status=args.status, limit=args.limit)
            output = [p.to_dict() for p in prospects]
            print(json.dumps({"count": len(output), "prospects": output}, indent=2))
        
        elif args.qualify:
            # Qualify prospect
            result = prospector.qualify_prospect(args.qualify)
            if result:
                print(json.dumps({"success": True, "result": result}))
            else:
                print(json.dumps({"success": False, "message": "Prospect not found"}))
        
        elif args.stats:
            # Show statistics
            stats = prospector.store.get_stats()
            print(json.dumps(stats, indent=2))
        
        elif args.import_file:
            # Import from file
            import_path = Path(args.import_file)
            if not import_path.exists():
                print(json.dumps({"success": False, "message": "File not found"}))
                sys.exit(1)
            
            with open(import_path, 'r') as f:
                data = json.load(f)
            
            prospects_data = data if isinstance(data, list) else data.get("prospects", [])
            results = prospector.bulk_import(prospects_data)
            print(json.dumps({"success": True, "results": results}))
        
        elif args.update:
            if not args.set:
                print(json.dumps({"success": False, "message": "--set required with --update"}))
                sys.exit(1)
            
            updates = json.loads(args.set)
            success = prospector.store.update_prospect(args.update, updates)
            print(json.dumps({"success": success}))
        
        elif args.delete:
            success = prospector.store.delete_prospect(args.delete)
            print(json.dumps({"success": success}))
        
        elif args.get:
            prospect = prospector.store.get_prospect(args.get)
            if prospect:
                print(json.dumps(prospect.to_dict(), indent=2))
            else:
                print(json.dumps({"success": False, "message": "Prospect not found"}))
        
        else:
            parser.print_help()
    
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        print(json.dumps({"success": False, "message": f"Invalid JSON: {e}"}))
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(json.dumps({"success": False, "message": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
