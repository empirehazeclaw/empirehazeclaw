#!/usr/bin/env python3
"""
Sales Enricher Agent
====================
Enriches prospect/lead data with additional information from various sources.
"""

import argparse
import json
import logging
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
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
        logging.FileHandler(LOG_DIR / "sales_enricher.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("SalesEnricher")


class EnrichmentData:
    """Represents enrichment data for a prospect."""
    
    def __init__(self, prospect_id: str, source: str):
        self.prospect_id = prospect_id
        self.source = source
        self.data = {}
        self.enriched_at = datetime.now().isoformat()
        self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        raw = f"{self.prospect_id}{self.source}{datetime.now().isoformat()}"
        return "enr_" + hashlib.md5(raw.encode()).hexdigest()[:10]
    
    def add_data(self, key: str, value):
        self.data[key] = value
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "prospect_id": self.prospect_id,
            "source": self.source,
            "data": self.data,
            "enriched_at": self.enriched_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'EnrichmentData':
        e = cls(data.get("prospect_id", ""), data.get("source", ""))
        e.data = data.get("data", {})
        e.id = data.get("id", e.id)
        e.enriched_at = data.get("enriched_at", datetime.now().isoformat())
        return e


class EnrichmentStore:
    """Manages enrichment data persistence."""
    
    def __init__(self, data_file: Optional[Path] = None):
        self.data_file = data_file or (DATA_DIR / "enrichments.json")
        self.enrichments = []
        self._load()
    
    def _load(self):
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.enrichments = [EnrichmentData.from_dict(e) for e in data.get("enrichments", [])]
                logger.info(f"Loaded {len(self.enrichments)} enrichment records")
            except Exception as e:
                logger.error(f"Failed to load enrichments: {e}")
                self.enrichments = []
        else:
            self.enrichments = []
    
    def _save(self):
        try:
            data = {
                "enrichments": [e.to_dict() for e in self.enrichments],
                "updated_at": datetime.now().isoformat()
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.enrichments)} enrichments")
        except Exception as e:
            logger.error(f"Failed to save enrichments: {e}")
            raise
    
    def add_enrichment(self, enrichment: EnrichmentData) -> bool:
        self.enrichments.append(enrichment)
        self._save()
        return True
    
    def get_enrichments_for(self, prospect_id: str) -> List[EnrichmentData]:
        return [e for e in self.enrichments if e.prospect_id == prospect_id]
    
    def get_stats(self) -> dict:
        by_source = {}
        for e in self.enrichments:
            by_source[e.source] = by_source.get(e.source, 0) + 1
        
        return {
            "total_enrichments": len(self.enrichments),
            "unique_prospects": len(set(e.prospect_id for e in self.enrichments)),
            "by_source": by_source
        }


class SalesEnricher:
    """Main sales enricher agent."""
    
    # Common email patterns to extract company/role info
    TITLE_PATTERNS = [
        (r'ceo|chief executive', 'Executive'),
        (r'cto|chief technology', 'Technical Executive'),
        (r'cfo|chief finance', 'Finance Executive'),
        (r'vp|vice president', 'VP'),
        (r'director', 'Director'),
        (r'manager', 'Manager'),
        (r'engineer|developer', 'Technical'),
        (r'sales|account', 'Sales'),
        (r'marketing', 'Marketing'),
        (r'founder|co-founder', 'Founder'),
    ]
    
    INDUSTRY_KEYWORDS = {
        "saas": ["saas", "software as a service", "cloud"],
        "fintech": ["fintech", "financial", "payment", "banking"],
        "healthcare": ["health", "medical", "pharma", "biotech"],
        "ecommerce": ["e-commerce", "ecommerce", "online retail"],
        "marketing": ["marketing", "advertising", "agency"],
        "technology": ["technology", "tech", "software"],
        "consulting": ["consulting", "advisory"],
        "education": ["education", "edtech", "learning"],
    }
    
    def __init__(self):
        self.store = EnrichmentStore()
        logger.info("SalesEnricher initialized")
    
    def enrich_from_email(self, email: str) -> dict:
        """Extract information from email address."""
        result = {
            "email": email,
            "domain": "",
            "username": "",
            "possible_company": "",
            "inferred_industry": ""
        }
        
        if not email or "@" not in email:
            return result
        
        try:
            username, domain = email.rsplit("@", 1)
            result["domain"] = domain
            result["username"] = username
            
            # Extract company from common email patterns
            # e.g., john@acme-corp.com -> acme-corp
            company_match = re.match(r'^([a-zA-Z0-9]+)', domain.split(".")[0])
            if company_match:
                result["possible_company"] = company_match.group(1).title()
            
            # Infer industry from domain
            domain_lower = domain.lower()
            for industry, keywords in self.INDUSTRY_KEYWORDS.items():
                for kw in keywords:
                    if kw in domain_lower:
                        result["inferred_industry"] = industry
                        break
        
        except Exception as e:
            logger.error(f"Failed to parse email: {e}")
        
        return result
    
    def enrich_from_name(self, name: str) -> dict:
        """Extract information from name."""
        result = {
            "name": name,
            "first_name": "",
            "last_name": "",
            "inferred_title": ""
        }
        
        if not name:
            return result
        
        parts = name.strip().split()
        if parts:
            result["first_name"] = parts[0]
            result["last_name"] = " ".join(parts[1:]) if len(parts) > 1 else ""
        
        # Infer title from name patterns (very basic)
        name_lower = name.lower()
        for pattern, title in self.TITLE_PATTERNS:
            if re.search(pattern, name_lower):
                result["inferred_title"] = title
                break
        
        return result
    
    def enrich_from_company(self, company: str) -> dict:
        """Enrich company information."""
        result = {
            "company": company,
            "size_estimate": "unknown",
            "industry_estimate": "",
            "b2b_indicator": False
        }
        
        if not company:
            return result
        
        company_lower = company.lower()
        
        # Company size indicators
        size_keywords = {
            "enterprise": ["enterprise", "global", "international", "corporation", "inc"],
            "large": ["llc", "ltd", "limited", "holdings"],
            "medium": ["gmbh", "ag"],
            "small": ["ug", "startup", "io"]
        }
        
        for size, keywords in size_keywords.items():
            if any(kw in company_lower for kw in keywords):
                result["size_estimate"] = size
                break
        
        # Industry detection
        for industry, keywords in self.INDUSTRY_KEYWORDS.items():
            if any(kw in company_lower for kw in keywords):
                result["industry_estimate"] = industry
                break
        
        # B2B indicator
        result["b2b_indicator"] = any(kw in company_lower for kw in 
            ["inc", "llc", "ltd", "gmbh", "ag", "corp", "co", "company"])
        
        return result
    
    def enrich_from_linkedin(self, linkedin_url: str) -> dict:
        """Parse LinkedIn URL for information."""
        result = {
            "linkedin_url": linkedin_url,
            "linkedin_id": "",
            "profile_type": "personal"
        }
        
        if not linkedin_url:
            return result
        
        try:
            # Extract LinkedIn ID from URL
            # Pattern: linkedin.com/in/ID or linkedin.com/company/ID
            match = re.search(r'linkedin\.com/(?:in|company)/([^/?]+)', linkedin_url)
            if match:
                result["linkedin_id"] = match.group(1)
                if "/company/" in linkedin_url:
                    result["profile_type"] = "company"
                elif "/school/" in linkedin_url:
                    result["profile_type"] = "school"
        except Exception as e:
            logger.error(f"Failed to parse LinkedIn URL: {e}")
        
        return result
    
    def enrich_company_from_domain(self, domain: str) -> dict:
        """Enrich company data from domain."""
        result = {
            "domain": domain,
            "company_name": "",
            "industry": "",
            "description": "",
            "employee_range": ""
        }
        
        if not domain:
            return result
        
        # Clean domain
        domain = domain.lower().replace("https://", "").replace("http://", "").replace("www.", "")
        result["domain"] = domain
        
        # Extract company name from domain
        company = domain.split(".")[0]
        # Remove common prefixes
        for prefix in ["admin", "mail", "web", "ftp", "cpanel", "ns", "ns1", "smtp"]:
            if company.startswith(prefix + "."):
                company = company.split(".", 1)[1]
        result["company_name"] = company.title().replace("-", " ").replace("_", " ")
        
        # Try to infer industry from domain
        for industry, keywords in self.INDUSTRY_KEYWORDS.items():
            if any(kw in domain for kw in keywords):
                result["industry"] = industry
                break
        
        return result
    
    def phone_parse(self, phone: str) -> dict:
        """Parse and validate phone number."""
        result = {
            "original": phone,
            "formatted": "",
            "country_code": "",
            "valid": False
        }
        
        if not phone:
            return result
        
        # Remove non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Basic validation - at least 10 digits
        digits = re.sub(r'\D', '', cleaned)
        if len(digits) >= 10:
            result["valid"] = True
            result["formatted"] = cleaned
            if cleaned.startswith("+"):
                result["country_code"] = digits[:digits.index(digits[1])+1] if len(digits) > 10 else ""
        
        return result
    
    def validate_email(self, email: str) -> dict:
        """Validate email address."""
        result = {
            "email": email,
            "valid": False,
            "reason": ""
        }
        
        if not email:
            result["reason"] = "empty"
            return result
        
        # Basic pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            result["valid"] = True
            
            # Check for disposable email domains
            disposable = ["mailinator", "tempmail", "throwaway", "guerrillamail", "10minutemail"]
            domain = email.split("@")[1].lower()
            if any(d in domain for d in disposable):
                result["valid"] = False
                result["reason"] = "disposable_domain"
        else:
            result["reason"] = "invalid_format"
        
        return result
    
    def merge_enrichment(self, prospect_id: str, data: dict, source: str = "manual") -> bool:
        """Merge enrichment data for a prospect."""
        try:
            enrichment = EnrichmentData(prospect_id, source)
            
            for key, value in data.items():
                enrichment.add_data(key, value)
            
            return self.store.add_enrichment(enrichment)
        except Exception as e:
            logger.error(f"Failed to merge enrichment: {e}")
            return False
    
    def get_enriched_data(self, prospect_id: str) -> dict:
        """Get all enrichment data for a prospect."""
        enrichments = self.store.get_enrichments_for(prospect_id)
        merged = {}
        for e in enrichments:
            merged.update(e.data)
            merged["sources"] = merged.get("sources", []) + [e.source]
        return merged
    
    def bulk_enrich(self, prospects: List[dict]) -> dict:
        """Bulk enrich a list of prospects."""
        results = {"enriched": 0, "failed": 0, "data": []}
        
        for p in prospects:
            try:
                prospect_id = p.get("id", "")
                email = p.get("email", "")
                name = p.get("name", "")
                company = p.get("company", "")
                linkedin = p.get("linkedin", "")
                phone = p.get("phone", "")
                
                enriched = {}
                
                if email:
                    enriched.update(self.enrich_from_email(email))
                    enriched.update(self.validate_email(email))
                
                if name:
                    enriched.update(self.enrich_from_name(name))
                
                if company:
                    enriched.update(self.enrich_from_company(company))
                
                if linkedin:
                    enriched.update(self.enrich_from_linkedin(linkedin))
                
                if phone:
                    enriched.update(self.phone_parse(phone))
                
                if enriched and prospect_id:
                    self.merge_enrichment(prospect_id, enriched)
                    results["enriched"] += 1
                    results["data"].append({"prospect_id": prospect_id, "enriched": enriched})
                else:
                    results["failed"] += 1
                    
            except Exception as e:
                logger.error(f"Failed to enrich prospect: {e}")
                results["failed"] += 1
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description="Sales Enricher Agent - Enrich prospect data with additional information",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --enrich-email "john@acme-corp.com"
  %(prog)s --enrich-name "John Doe"
  %(prog)s --enrich-company "Acme Corporation Inc"
  %(prog)s --enrich-linkedin "https://linkedin.com/in/johndoe"
  %(prog)s --validate-email "john@acme.com"
  %(prog)s --parse-phone "+1-555-123-4567"
  %(prog)s --domain-info "acme-corp.com"
  %(prog)s --merge "prospect123" '{"email": "john@acme.com", "company": "Acme", "source": "web"}'
  %(prog)s --get-enrichment "prospect123"
  %(prog)s --bulk-enrich prospects.json
  %(prog)s --stats
        """
    )
    
    parser.add_argument("--enrich-email", type=str, help="Enrich from email address")
    parser.add_argument("--enrich-name", type=str, help="Enrich from name")
    parser.add_argument("--enrich-company", type=str, help="Enrich from company name")
    parser.add_argument("--enrich-linkedin", type=str, help="Enrich from LinkedIn URL")
    parser.add_argument("--validate-email", type=str, help="Validate email address")
    parser.add_argument("--parse-phone", type=str, help="Parse phone number")
    parser.add_argument("--domain-info", type=str, help="Get info from domain")
    parser.add_argument("--merge", type=str, help="Merge enrichment for prospect ID")
    parser.add_argument("--source-data", type=str, help="JSON data for merge")
    parser.add_argument("--get-enrichment", type=str, help="Get enrichment data for prospect")
    parser.add_argument("--bulk-enrich", type=str, help="Bulk enrich from JSON file")
    parser.add_argument("--stats", action="store_true", help="Show enrichment statistics")
    
    args = parser.parse_args()
    enricher = SalesEnricher()
    
    try:
        if args.enrich_email:
            result = enricher.enrich_from_email(args.enrich_email)
            print(json.dumps(result, indent=2))
        
        elif args.enrich_name:
            result = enricher.enrich_from_name(args.enrich_name)
            print(json.dumps(result, indent=2))
        
        elif args.enrich_company:
            result = enricher.enrich_from_company(args.enrich_company)
            print(json.dumps(result, indent=2))
        
        elif args.enrich_linkedin:
            result = enricher.enrich_from_linkedin(args.enrich_linkedin)
            print(json.dumps(result, indent=2))
        
        elif args.validate_email:
            result = enricher.validate_email(args.validate_email)
            print(json.dumps(result, indent=2))
        
        elif args.parse_phone:
            result = enricher.phone_parse(args.parse_phone)
            print(json.dumps(result, indent=2))
        
        elif args.domain_info:
            result = enricher.enrich_company_from_domain(args.domain_info)
            print(json.dumps(result, indent=2))
        
        elif args.merge:
            if not args.source_data:
                print(json.dumps({"success": False, "message": "--source-data required with --merge"}))
                sys.exit(1)
            
            data = json.loads(args.source_data)
            success = enricher.merge_enrichment(args.merge, data)
            print(json.dumps({"success": success}))
        
        elif args.get_enrichment:
            result = enricher.get_enriched_data(args.get_enrichment)
            print(json.dumps(result, indent=2))
        
        elif args.bulk_enrich:
            path = Path(args.bulk_enrich)
            if not path.exists():
                print(json.dumps({"success": False, "message": "File not found"}))
                sys.exit(1)
            
            with open(path, 'r') as f:
                data = json.load(f)
            
            prospects = data if isinstance(data, list) else data.get("prospects", [])
            results = enricher.bulk_enrich(prospects)
            print(json.dumps({"success": True, "results": results}, indent=2))
        
        elif args.stats:
            stats = enricher.store.get_stats()
            print(json.dumps(stats, indent=2))
        
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
