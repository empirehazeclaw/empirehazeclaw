#!/usr/bin/env python3
"""
Job Posting Generator Agent
Generates professional job postings from templates and company data.
Reads: company.json, job_templates.json
Writes: job_postings.json, output/<title>-<date>.txt
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
AGENTS_DIR = SCRIPT_DIR.parent
WORKSPACE = SCRIPT_DIR.parent.parent.parent
DATA_DIR = WORKSPACE / "data" / "hr"
LOGS_DIR = WORKSPACE / "logs"
OUTPUT_DIR = WORKSPACE / "data" / "hr" / "output"

# Ensure dirs exist
LOGS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "job_posting_generator.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("JobPostingGenerator")


def load_json(path: Path) -> dict | list:
    """Load JSON file, return empty dict/list on error."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"File not found: {path}")
        return {} if "." not in path.name else []
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {path}: {e}")
        return {} if "." not in path.name else []


def save_json(path: Path, data: Any) -> bool:
    """Save data to JSON file."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Failed to save {path}: {e}")
        return False


def get_default_company() -> dict:
    """Return default company data if none exists."""
    return {
        "name": "OpenClaw Company",
        "industry": "Technology",
        "size": "11-50",
        "culture": "Fast-paced, innovative, remote-friendly",
        "benefits": ["Flexible hours", "Remote work", "Learning budget"],
        "website": "https://example.com",
        "contact_email": "hr@example.com",
    }


def get_default_templates() -> list:
    """Return default job templates."""
    return [
        {
            "id": "software_engineer",
            "title": "Software Engineer",
            "department": "Engineering",
            "seniority": "Mid-Level",
            "description": "We are looking for a skilled Software Engineer to join our growing team.",
            "responsibilities": [
                "Design and implement scalable software solutions",
                "Collaborate with cross-functional teams",
                "Write clean, maintainable code",
                "Participate in code reviews",
            ],
            "requirements": [
                "3+ years of software development experience",
                "Proficiency in Python, JavaScript, or similar",
                "Experience with cloud platforms",
                "Strong problem-solving skills",
            ],
            "nice_to_have": [
                "Open source contributions",
                "Experience with containers and CI/CD",
            ],
            "salary_range": {"min": 60000, "max": 90000, "currency": "USD"},
        },
        {
            "id": "product_manager",
            "title": "Product Manager",
            "department": "Product",
            "seniority": "Senior",
            "description": "Lead product strategy and roadmap for our core platform.",
            "responsibilities": [
                "Define product vision and roadmap",
                "Gather and prioritize requirements",
                "Work closely with engineering and design",
                "Analyze metrics and iterate",
            ],
            "requirements": [
                "5+ years of product management experience",
                "Strong analytical skills",
                "Excellent communication",
                "Technical background preferred",
            ],
            "nice_to_have": ["Experience with SaaS products", "MBA degree"],
            "salary_range": {"min": 90000, "max": 130000, "currency": "USD"},
        },
        {
            "id": "marketing_manager",
            "title": "Marketing Manager",
            "department": "Marketing",
            "seniority": "Mid-Senior",
            "description": "Drive growth through digital marketing campaigns and content strategy.",
            "responsibilities": [
                "Plan and execute marketing campaigns",
                "Manage social media presence",
                "Create content marketing strategy",
                "Track and report on KPIs",
            ],
            "requirements": [
                "4+ years of marketing experience",
                "Experience with SEO/SEM",
                "Strong writing skills",
                "Data-driven approach",
            ],
            "nice_to_have": ["HubSpot/Mailchimp experience", "B2B SaaS experience"],
            "salary_range": {"min": 55000, "max": 80000, "currency": "USD"},
        },
    ]


def generate_posting(template: dict, company: dict, custom_fields: dict = None) -> str:
    """Generate a full job posting from template and company data."""
    custom = custom_fields or {}
    
    title = custom.get("title", template.get("title", "Unknown Position"))
    department = custom.get("department", template.get("department", "General"))
    seniority = custom.get("seniority", template.get("seniority", ""))
    salary = template.get("salary_range", {})
    
    posting_parts = []
    posting_parts.append(f"# {title}")
    posting_parts.append(f"**Department:** {department}")
    if seniority:
        posting_parts.append(f"**Level:** {seniority}")
    posting_parts.append("")
    posting_parts.append(f"*{template.get('description', '')}*")
    posting_parts.append("")
    posting_parts.append("## About Us")
    posting_parts.append(f"We are {company.get('name', 'our company')}, a {company.get('industry', 'technology')} company.")
    posting_parts.append(f"Company size: {company.get('size', '11-50 employees')}.")
    posting_parts.append(f"Culture: {company.get('culture', 'innovative and collaborative')}.")
    posting_parts.append("")
    
    if company.get("benefits"):
        posting_parts.append("## Benefits")
        for benefit in company["benefits"]:
            posting_parts.append(f"- {benefit}")
        posting_parts.append("")
    
    posting_parts.append("## What You'll Do")
    for resp in template.get("responsibilities", []):
        posting_parts.append(f"- {resp}")
    posting_parts.append("")
    
    posting_parts.append("## Requirements")
    for req in template.get("requirements", []):
        posting_parts.append(f"- {req}")
    posting_parts.append("")
    
    if template.get("nice_to_have"):
        posting_parts.append("## Nice to Have")
        for item in template["nice_to_have"]:
            posting_parts.append(f"- {item}")
        posting_parts.append("")
    
    if salary.get("min") and salary.get("max"):
        posting_parts.append(f"## Compensation")
        posting_parts.append(f"Range: {salary['currency']} {salary['min']:,} - {salary['max']:,}")
        posting_parts.append("")
    
    posting_parts.append("## How to Apply")
    posting_parts.append(f"Apply by sending your CV to: {company.get('contact_email', 'hr@company.com')}")
    posting_parts.append(f"Or visit: {company.get('website', 'https://example.com/careers')}")
    posting_parts.append("")
    posting_parts.append(f"*Posted: {datetime.now().strftime('%Y-%m-%d')}*")
    
    return "\n".join(posting_parts)


def list_templates(templates: list) -> None:
    """List available job templates."""
    print("\n📋 Available Job Templates:")
    print("-" * 50)
    for t in templates:
        print(f"  [{t['id']}] {t['title']} ({t['department']}) - {t['seniority']}")
    print()


def cmd_generate(args) -> int:
    """Generate a job posting."""
    company_file = DATA_DIR / "company.json"
    templates_file = DATA_DIR / "job_templates.json"
    
    company = load_json(company_file) or get_default_company()
    templates = load_json(templates_file) or get_default_templates()
    
    if not templates:
        logger.error("No templates available")
        return 1
    
    # Find matching template
    template = None
    if args.template_id:
        for t in templates:
            if t["id"] == args.template_id:
                template = t
                break
        if not template:
            logger.error(f"Template '{args.template_id}' not found")
            list_templates(templates)
            return 1
    else:
        template = templates[0]
    
    # Custom fields from args
    custom = {}
    if args.title:
        custom["title"] = args.title
    if args.department:
        custom["department"] = args.department
    
    # Generate posting
    posting = generate_posting(template, company, custom)
    
    # Save to file
    date_str = datetime.now().strftime("%Y%m%d")
    safe_title = (args.title or template["title"]).lower().replace(" ", "-")
    output_file = OUTPUT_DIR / f"{safe_title}-{date_str}.txt"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(posting)
    
    # Save to postings registry
    postings_file = DATA_DIR / "job_postings.json"
    postings = load_json(postings_file) or []
    
    entry = {
        "id": f"{safe_title}-{date_str}",
        "template_id": template["id"],
        "title": args.title or template["title"],
        "created_at": datetime.now().isoformat(),
        "file": str(output_file),
        "status": "draft",
    }
    postings.append(entry)
    save_json(postings_file, postings)
    
    # Print to stdout
    print(posting)
    print(f"\n✅ Saved to: {output_file}")
    logger.info(f"Generated job posting: {entry['id']}")
    return 0


def cmd_list(args) -> int:
    """List all job postings."""
    postings_file = DATA_DIR / "job_postings.json"
    postings = load_json(postings_file) or []
    
    if not postings:
        print("No job postings found.")
        return 0
    
    print(f"\n📋 Job Postings ({len(postings)} total):")
    print("-" * 60)
    for p in postings:
        status_icon = "✅" if p.get("status") == "published" else "📝"
        print(f"  {status_icon} [{p['id']}] {p['title']}")
        print(f"       Created: {p.get('created_at', 'unknown')[:10]}")
        print(f"       Status: {p.get('status', 'unknown')}")
    print()
    return 0


def cmd_publish(args) -> int:
    """Publish a job posting."""
    postings_file = DATA_DIR / "job_postings.json"
    postings = load_json(postings_file) or []
    
    posting_id = args.posting_id
    for p in postings:
        if p["id"] == posting_id:
            p["status"] = "published"
            p["published_at"] = datetime.now().isoformat()
            save_json(postings_file, postings)
            print(f"✅ Published: {p['title']}")
            logger.info(f"Published posting: {posting_id}")
            return 0
    
    logger.error(f"Posting not found: {posting_id}")
    return 1


def cmd_init(args) -> int:
    """Initialize HR data files with defaults."""
    company_file = DATA_DIR / "company.json"
    templates_file = DATA_DIR / "job_templates.json"
    
    if company_file.exists():
        print(f"⚠️  {company_file} already exists, skipping")
    else:
        save_json(company_file, get_default_company())
        print(f"✅ Created: {company_file}")
    
    if templates_file.exists():
        print(f"⚠️  {templates_file} already exists, skipping")
    else:
        save_json(templates_file, get_default_templates())
        print(f"✅ Created: {templates_file}")
    
    logger.info("Initialized HR data files")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Job Posting Generator - Create professional job postings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --init                    Initialize data files
  %(prog)s --list                    List all postings
  %(prog)s --generate                Generate from first template
  %(prog)s --generate --template-id software_engineer
  %(prog)s --generate --title "Senior Python Developer" --department Engineering
  %(prog)s --publish my-posting-20260327
        """,
    )
    
    parser.add_argument("--init", action="store_true", help="Initialize data files with defaults")
    parser.add_argument("--list", action="store_true", help="List all job postings")
    parser.add_argument("--generate", action="store_true", help="Generate a new job posting")
    parser.add_argument("--template-id", help="Template ID to use")
    parser.add_argument("--title", help="Custom job title")
    parser.add_argument("--department", help="Custom department")
    parser.add_argument("--publish", dest="posting_id", help="Publish a posting by ID")
    
    args = parser.parse_args()
    
    # Default action: show help if no args
    if len(sys.argv) == 1:
        parser.print_help()
        print("\n💡 Quick start: %(prog)s --init && %(prog)s --generate")
        return 0
    
    try:
        if args.init:
            return cmd_init(args)
        if args.list:
            return cmd_list(args)
        if args.generate:
            return cmd_generate(args)
        if args.posting_id:
            return cmd_publish(args)
        
        parser.print_help()
        return 0
    except KeyboardInterrupt:
        print("\n⚠️  Cancelled")
        return 130
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
