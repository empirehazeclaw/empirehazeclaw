#!/usr/bin/env python3
"""
Testimonial Collector Agent — Collect, manage, and format customer testimonials
Version: 1.0
Usage: python3 testimonial_collector_agent.py --task <task> [options]
"""

import argparse
import json
import logging
import sys
import os
import re
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

# Logging Setup
LOG_DIR = "/home/clawbot/.openclaw/workspace/logs"
DATA_DIR = "/home/clawbot/.openclaw/workspace/data"
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [TESTIMONIAL] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "testimonial_collector.log")),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


class TestimonialCollectorAgent:
    """Collect, manage, format, and analyze customer testimonials."""

    TESTIMONIAL_DATA_FILE = os.path.join(DATA_DIR, "testimonials.json")
    PENDING_DATA_FILE = os.path.join(DATA_DIR, "pending_testimonials.json")

    def __init__(self):
        self.log = log
        self._ensure_data_files()

    def _ensure_data_files(self):
        """Ensure data files exist."""
        if not os.path.exists(self.TESTIMONIAL_DATA_FILE):
            with open(self.TESTIMONIAL_DATA_FILE, 'w') as f:
                json.dump({"testimonials": [], "metadata": {"last_updated": datetime.now().isoformat()}}, f)

        if not os.path.exists(self.PENDING_DATA_FILE):
            with open(self.PENDING_DATA_FILE, 'w') as f:
                json.dump({"pending": [], "metadata": {"last_updated": datetime.now().isoformat()}}, f)

    def add_testimonial(self, quote: str, author: str, role: str = None,
                       company: str = None, rating: int = None,
                       source: str = "direct", tags: List[str] = None) -> Dict[str, Any]:
        """Add a new verified testimonial."""

        testimonial = {
            "id": str(uuid.uuid4())[:8],
            "quote": quote,
            "author": author,
            "role": role,
            "company": company,
            "rating": rating,
            "source": source,
            "tags": tags or [],
            "status": "verified",
            "created_at": datetime.now().isoformat(),
            "use_cases": []
        }

        # Load existing
        data = self._load_testimonials()
        data["testimonials"].append(testimonial)
        data["metadata"]["last_updated"] = datetime.now().isoformat()
        data["metadata"]["total_count"] = len(data["testimonials"])

        # Save
        self._save_testimonials(data)

        self.log.info(f"Added testimonial from {author}")
        return testimonial

    def add_pending_testimonial(self, quote: str, author: str = None,
                               source: str = "unknown") -> Dict[str, Any]:
        """Add a testimonial pending verification."""

        pending = {
            "id": str(uuid.uuid4())[:8],
            "quote": quote,
            "author": author,
            "source": source,
            "created_at": datetime.now().isoformat(),
            "verified": False
        }

        # Load existing
        data = self._load_pending()
        data["pending"].append(pending)
        data["metadata"]["last_updated"] = datetime.now().isoformat()

        self._save_pending(data)

        self.log.info(f"Added pending testimonial: {pending['id']}")
        return pending

    def verify_testimonial(self, testimonial_id: str, author_info: Dict[str, str] = None) -> Dict[str, Any]:
        """Verify a pending testimonial and add to collection."""

        # Load pending
        pending_data = self._load_pending()
        pending = None
        for p in pending_data["pending"]:
            if p["id"] == testimonial_id:
                pending = p
                break

        if not pending:
            raise ValueError(f"Pending testimonial {testimonial_id} not found")

        # Remove from pending
        pending_data["pending"] = [p for p in pending_data["pending"] if p["id"] != testimonial_id]
        self._save_pending(pending_data)

        # Add to verified
        testimonial = {
            "id": testimonial_id,
            "quote": pending["quote"],
            "author": author_info.get("name", pending.get("author")) if author_info else pending.get("author"),
            "role": author_info.get("role") if author_info else None,
            "company": author_info.get("company") if author_info else None,
            "source": pending.get("source", "unknown"),
            "tags": [],
            "status": "verified",
            "created_at": pending.get("created_at"),
            "verified_at": datetime.now().isoformat()
        }

        data = self._load_testimonials()
        data["testimonials"].append(testimonial)
        self._save_testimonials(data)

        self.log.info(f"Verified testimonial {testimonial_id}")
        return testimonial

    def get_testimonials(self, filter_tags: List[str] = None,
                         min_rating: int = None,
                         status: str = "verified") -> List[Dict[str, Any]]:
        """Get testimonials with optional filtering."""

        if status == "pending":
            data = self._load_pending()
            return data["pending"]
        else:
            data = self._load_testimonials()
            testimonials = data["testimonials"]

            # Apply filters
            if filter_tags:
                testimonials = [t for t in testimonials
                               if any(tag in t.get("tags", []) for tag in filter_tags)]

            if min_rating:
                testimonials = [t for t in testimonials
                               if t.get("rating", 0) >= min_rating]

            return testimonials

    def format_for_website(self, testimonials: List[Dict] = None) -> str:
        """Format testimonials for website display."""

        if not testimonials:
            testimonials = self.get_testimonials()

        html = '<div class="testimonials">\n'

        for t in testimonials:
            stars = "⭐" * t.get("rating", 5) if t.get("rating") else ""
            author_info = f"{t.get('author', 'Customer')}"
            if t.get("role") or t.get("company"):
                author_info += f", {t.get('role', '')} {t.get('company', '')}".strip()

            html += f"""
    <blockquote class="testimonial">
        <p>"{t['quote']}"</p>
        <footer>
            <cite>{author_info}</cite>
            {stars}
        </footer>
    </blockquote>
"""

        html += '</div>'
        return html

    def format_for_social(self, testimonial: Dict) -> str:
        """Format testimonial for social media."""

        quote = testimonial.get("quote", "")
        author = testimonial.get("author", "Customer")
        company = testimonial.get("company", "")

        return f'''
"{quote}"

— {author}{f" from {company}" if company else ""}
'''

    def generate_request_email(self, customer_name: str, customer_email: str,
                             product_name: str = "our product") -> Dict[str, str]:
        """Generate a testimonial request email."""

        subject = f"Share your experience with {product_name}"

        body = f"""Hi {customer_name},

I hope this message finds you well.

We've been working hard to improve {product_name}, and we'd love to hear about your experience. Your feedback helps us serve you better and helps other customers make informed decisions.

If you have a few minutes, we'd really appreciate it if you could share your thoughts:
- What did you like most?
- How has it helped your work?
- Any suggestions for improvement?

Of course, if you'd prefer not to respond, we completely understand.

Thank you for being a valued customer!

Best regards,
The Team
"""

        return {
            "to": customer_email,
            "subject": subject,
            "body": body
        }

    def analyze_sentiment(self, testimonials: List[Dict] = None) -> Dict[str, Any]:
        """Analyze sentiment of testimonials."""

        if not testimonials:
            testimonials = self.get_testimonials()

        positive_words = ["great", "excellent", "amazing", "love", "helpful", "easy", "best", "fantastic", "wonderful"]
        negative_words = ["bad", "terrible", "awful", "hate", "difficult", "poor", "frustrating", "disappointing"]
        neutral_words = ["okay", "fine", "decent", "average", "ok"]

        stats = {
            "total": len(testimonials),
            "positive": 0,
            "negative": 0,
            "neutral": 0,
            "average_rating": 0
        }

        for t in testimonials:
            quote_lower = t.get("quote", "").lower()
            pos = sum(1 for w in positive_words if w in quote_lower)
            neg = sum(1 for w in negative_words if w in quote_lower)

            if pos > neg:
                stats["positive"] += 1
            elif neg > pos:
                stats["negative"] += 1
            else:
                stats["neutral"] += 1

        ratings = [t.get("rating", 0) for t in testimonials if t.get("rating")]
        if ratings:
            stats["average_rating"] = sum(ratings) / len(ratings)

        return stats

    def get_stats(self) -> Dict[str, Any]:
        """Get overall testimonial statistics."""

        data = self._load_testimonials()
        pending_data = self._load_pending()

        testimonials = data["testimonials"]
        ratings = [t.get("rating") for t in testimonials if t.get("rating")]

        return {
            "total_testimonials": len(testimonials),
            "pending_testimonials": len(pending_data["pending"]),
            "verified": len([t for t in testimonials if t.get("status") == "verified"]),
            "average_rating": sum(ratings) / len(ratings) if ratings else 0,
            "by_source": self._count_by_field(testimonials, "source"),
            "by_tag": self._count_by_field(testimonials, "tags")
        }

    def _count_by_field(self, items: List[Dict], field: str) -> Dict[str, int]:
        """Count items by a specific field."""

        counts = {}
        for item in items:
            if field == "tags":
                for tag in item.get(field, []):
                    counts[tag] = counts.get(tag, 0) + 1
            else:
                val = item.get(field, "unknown")
                counts[val] = counts.get(val, 0) + 1
        return counts

    def _load_testimonials(self) -> Dict:
        """Load testimonials from file."""
        try:
            with open(self.TESTIMONIAL_DATA_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"testimonials": [], "metadata": {}}

    def _save_testimonials(self, data: Dict):
        """Save testimonials to file."""
        with open(self.TESTIMONIAL_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def _load_pending(self) -> Dict:
        """Load pending testimonials from file."""
        try:
            with open(self.PENDING_DATA_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"pending": [], "metadata": {}}

    def _save_pending(self, data: Dict):
        """Save pending testimonials to file."""
        with open(self.PENDING_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Testimonial Collector Agent — Manage customer testimonials",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add a new testimonial
  python3 testimonial_collector_agent.py --task add --quote "Great product!" \\
    --author "John Doe" --company "Acme Inc" --rating 5

  # List all testimonials
  python3 testimonial_collector_agent.py --task list

  # Get pending testimonials
  python3 testimonial_collector_agent.py --task list --status pending

  # Verify a testimonial
  python3 testimonial_collector_agent.py --task verify --id abc123 \\
    --author-name "John Doe" --author-company "Acme"

  # Format for website
  python3 testimonial_collector_agent.py --task website-format --output ./testimonials.html

  # Generate request email
  python3 testimonial_collector_agent.py --task request-email \\
    --customer-name "Jane" --customer-email "jane@example.com"

  # Analyze sentiment
  python3 testimonial_collector_agent.py --task analyze

  # Get stats
  python3 testimonial_collector_agent.py --task stats
        """
    )

    parser.add_argument("--task", required=True,
                        choices=["add", "add-pending", "verify", "list", "website-format",
                               "social-format", "request-email", "analyze", "stats"],
                        help="Task to perform")
    parser.add_argument("--quote", help="Testimonial quote text")
    parser.add_argument("--author", help="Author name")
    parser.add_argument("--author-name", help="Author name (for verification)")
    parser.add_argument("--author-company", help="Author company (for verification)")
    parser.add_argument("--author-role", help="Author role (for verification)")
    parser.add_argument("--company", help="Company name")
    parser.add_argument("--rating", type=int, choices=[1, 2, 3, 4, 5], help="Star rating (1-5)")
    parser.add_argument("--source", default="direct", help="Source of testimonial")
    parser.add_argument("--tags", help="Comma-separated tags")
    parser.add_argument("--id", help="Testimonial ID")
    parser.add_argument("--status", default="verified", choices=["verified", "pending"])
    parser.add_argument("--filter-tags", help="Comma-separated tags to filter by")
    parser.add_argument("--min-rating", type=int, choices=[1, 2, 3, 4, 5], help="Minimum rating")
    parser.add_argument("--customer-name", help="Customer name (for email)")
    parser.add_argument("--customer-email", help="Customer email (for email)")
    parser.add_argument("--product-name", default="our product", help="Product name")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    agent = TestimonialCollectorAgent()

    try:
        result = None

        if args.task == "add":
            if not args.quote or not args.author:
                raise ValueError("--quote and --author required")

            tags = args.tags.split(",") if args.tags else None
            result = agent.add_testimonial(
                quote=args.quote,
                author=args.author,
                role=args.author_role,
                company=args.company,
                rating=args.rating,
                source=args.source,
                tags=tags
            )

        elif args.task == "add-pending":
            if not args.quote:
                raise ValueError("--quote required")

            result = agent.add_pending_testimonial(
                quote=args.quote,
                author=args.author,
                source=args.source
            )

        elif args.task == "verify":
            if not args.id:
                raise ValueError("--id required")

            author_info = {}
            if args.author_name:
                author_info["name"] = args.author_name
            if args.author_company:
                author_info["company"] = args.author_company
            if args.author_role:
                author_info["role"] = args.author_role

            result = agent.verify_testimonial(args.id, author_info if author_info else None)

        elif args.task == "list":
            filter_tags = args.filter_tags.split(",") if args.filter_tags else None
            result = {"testimonials": agent.get_testimonials(filter_tags, args.min_rating, args.status)}

        elif args.task == "website-format":
            filter_tags = args.filter_tags.split(",") if args.filter_tags else None
            testimonials = agent.get_testimonials(filter_tags, args.min_rating)
            result = {"html": agent.format_for_website(testimonials)}

        elif args.task == "social-format":
            filter_tags = args.filter_tags.split(",") if args.filter_tags else None
            testimonials = agent.get_testimonials(filter_tags, args.min_rating)
            formatted = [agent.format_for_social(t) for t in testimonials]
            result = {"formatted": formatted}

        elif args.task == "request-email":
            if not args.customer_name or not args.customer_email:
                raise ValueError("--customer-name and --customer-email required")

            result = agent.generate_request_email(
                customer_name=args.customer_name,
                customer_email=args.customer_email,
                product_name=args.product_name
            )

        elif args.task == "analyze":
            result = agent.analyze_sentiment()

        elif args.task == "stats":
            result = agent.get_stats()

        if result:
            if args.output:
                with open(args.output, 'w') as f:
                    if "html" in result:
                        f.write(result["html"])
                    else:
                        json.dump(result, f, indent=2)
                log.info(f"Output saved to {args.output}")
            else:
                print(json.dumps(result, indent=2))
            log.info("Task completed successfully")

    except FileNotFoundError as e:
        log.error(f"File not found: {e}")
        sys.exit(1)
    except ValueError as e:
        log.error(f"Validation error: {e}")
        sys.exit(1)
    except Exception as e:
        log.error(f"Task failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
