#!/usr/bin/env python3
"""
Skills Inventory Agent
Tracks employee skills, certifications, and identifies gaps.
Reads: employees.json, skills_inventory.json
Writes: skills_inventory.json, output/skills-gap-<date>.txt
"""

import argparse
import json
import logging
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
AGENTS_DIR = SCRIPT_DIR.parent
WORKSPACE = SCRIPT_DIR.parent.parent.parent
DATA_DIR = WORKSPACE / "data" / "hr"
LOGS_DIR = WORKSPACE / "logs"
OUTPUT_DIR = WORKSPACE / "data" / "hr" / "output"

LOGS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "skills_inventory.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("SkillsInventory")


def load_json(path: Path) -> dict | list:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {} if "." not in path.name else []
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {path}: {e}")
        return {} if "." not in path.name else []


def save_json(path: Path, data: Any) -> bool:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Failed to save {path}: {e}")
        return False


SKILL_CATEGORIES = [
    "programming_languages",
    "frameworks",
    "cloud_platforms",
    "databases",
    "tools",
    "soft_skills",
    "certifications",
    "languages",
]


def get_default_skills_inventory() -> dict:
    return {
        "skills_taxonomy": {
            "programming_languages": ["Python", "JavaScript", "TypeScript", "Go", "Rust", "Java", "C++"],
            "frameworks": ["React", "Node.js", "Django", "FastAPI", "Vue.js", "Angular"],
            "cloud_platforms": ["AWS", "GCP", "Azure", "Heroku", "Vercel"],
            "databases": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "DynamoDB"],
            "tools": ["Git", "Docker", "Kubernetes", "Terraform", "Jenkins", "GitHub Actions"],
            "soft_skills": ["Communication", "Leadership", "Problem Solving", "Teamwork"],
            "certifications": ["AWS Solutions Architect", "PMP", "Google Cloud Certified"],
            "languages": ["English", "German", "Spanish", "French", "Chinese"],
        },
        "employee_skills": [],
    }


def cmd_add_skill(args) -> int:
    """Add a skill to an employee's inventory."""
    inventory_file = DATA_DIR / "skills_inventory.json"
    inventory = load_json(inventory_file) or get_default_skills_inventory()
    
    # Find or create employee entry
    emp_skills = None
    for es in inventory.get("employee_skills", []):
        if es.get("employee_id") == args.employee_id:
            emp_skills = es
            break
    
    if not emp_skills:
        emp_skills = {
            "employee_id": args.employee_id,
            "skills": {},
            "certifications": [],
            "languages": [],
            "updated_at": datetime.now().isoformat(),
        }
        inventory.setdefault("employee_skills", []).append(emp_skills)
    
    category = args.category
    if category not in emp_skills["skills"]:
        emp_skills["skills"][category] = []
    
    if args.skill not in emp_skills["skills"][category]:
        emp_skills["skills"][category].append(args.skill)
        emp_skills["updated_at"] = datetime.now().isoformat()
        save_json(inventory_file, inventory)
        print(f"✅ Added skill '{args.skill}' to {args.employee_id} ({category})")
        logger.info(f"Added skill {args.skill} to {args.employee_id}")
    else:
        print(f"⚠️  Skill '{args.skill}' already exists for {args.employee_id}")
    
    return 0


def cmd_remove_skill(args) -> int:
    """Remove a skill from an employee's inventory."""
    inventory_file = DATA_DIR / "skills_inventory.json"
    inventory = load_json(inventory_file) or get_default_skills_inventory()
    
    for es in inventory.get("employee_skills", []):
        if es.get("employee_id") == args.employee_id:
            category_skills = es.get("skills", {}).get(args.category, [])
            if args.skill in category_skills:
                category_skills.remove(args.skill)
                es["updated_at"] = datetime.now().isoformat()
                save_json(inventory_file, inventory)
                print(f"✅ Removed skill '{args.skill}' from {args.employee_id}")
                logger.info(f"Removed skill {args.skill} from {args.employee_id}")
                return 0
            else:
                print(f"⚠️  Skill '{args.skill}' not found in {args.category}")
                return 1
    
    logger.error(f"Employee not found: {args.employee_id}")
    return 1


def cmd_show_employee(args) -> int:
    """Show skills for an employee."""
    inventory_file = DATA_DIR / "skills_inventory.json"
    inventory = load_json(inventory_file) or get_default_skills_inventory()
    
    for es in inventory.get("employee_skills", []):
        if es.get("employee_id") == args.employee_id:
            print(f"\n🛠️  Skills for {args.employee_id}")
            print("=" * 50)
            skills = es.get("skills", {})
            for category, skill_list in skills.items():
                if skill_list:
                    print(f"\n  {category.replace('_', ' ').title()}:")
                    for skill in skill_list:
                        print(f"    - {skill}")
            return 0
    
    logger.error(f"Employee skills not found: {args.employee_id}")
    return 1


def cmd_list_all(args) -> int:
    """List all skills in the taxonomy."""
    inventory_file = DATA_DIR / "skills_inventory.json"
    inventory = load_json(inventory_file) or get_default_skills_inventory()
    
    taxonomy = inventory.get("skills_taxonomy", {})
    
    print(f"\n📋 SKILLS TAXONOMY")
    print("=" * 50)
    for category in SKILL_CATEGORIES:
        skills = taxonomy.get(category, [])
        if skills:
            print(f"\n  {category.replace('_', ' ').title()}:")
            for skill in skills:
                print(f"    - {skill}")
    print()
    return 0


def cmd_search(args) -> int:
    """Search for employees with a specific skill."""
    inventory_file = DATA_DIR / "skills_inventory.json"
    inventory = load_json(inventory_file) or get_default_skills_inventory()
    
    search_term = args.skill.lower()
    matches = []
    
    for es in inventory.get("employee_skills", []):
        for category, skills in es.get("skills", {}).items():
            for skill in skills:
                if search_term in skill.lower():
                    matches.append((es.get("employee_id"), category, skill))
    
    if matches:
        print(f"\n🔍 Employees with '{args.skill}' ({len(matches)} found):")
        print("-" * 50)
        for emp_id, category, skill in matches:
            print(f"  [{emp_id}] {skill} ({category})")
    else:
        print(f"No employees found with skill: {args.skill}")
    print()
    return 0


def cmd_gap_analysis(args) -> int:
    """Analyze skills gaps against required skills."""
    inventory_file = DATA_DIR / "skills_inventory.json"
    inventory = load_json(inventory_file) or get_default_skills_inventory()
    
    taxonomy = inventory.get("skills_taxonomy", {})
    
    print(f"\n📊 SKILLS GAP ANALYSIS")
    print("=" * 60)
    
    # Count skill occurrences across all employees
    skill_counts = defaultdict(int)
    total_employees = len(inventory.get("employee_skills", []))
    
    if total_employees == 0:
        print("No employees in skills inventory.")
        return 0
    
    for es in inventory.get("employee_skills", []):
        for category, skills in es.get("skills", {}).items():
            for skill in skills:
                skill_counts[(category, skill)] += 1
    
    print(f"Total Employees: {total_employees}")
    print()
    
    # Show skills coverage
    print("SKILLS COVERAGE:")
    print("-" * 60)
    for category in SKILL_CATEGORIES:
        skills = taxonomy.get(category, [])
        if skills:
            print(f"\n  {category.replace('_', ' ').title()}:")
            for skill in skills:
                count = skill_counts.get((category, skill), 0)
                pct = (count / total_employees) * 100
                bar_len = int(pct / 10)
                bar = "█" * bar_len + "░" * (10 - bar_len)
                coverage = "high" if pct >= 75 else "medium" if pct >= 40 else "low"
                icon = "🟢" if coverage == "high" else "🟡" if coverage == "medium" else "🔴"
                print(f"    {icon} {skill}: {bar} {pct:.0f}% ({count}/{total_employees})")
    
    print()
    return 0


def cmd_export_gaps(args) -> int:
    """Export skills gap report to file."""
    inventory_file = DATA_DIR / "skills_inventory.json"
    inventory = load_json(inventory_file) or get_default_skills_inventory()
    taxonomy = inventory.get("skills_taxonomy", {})
    
    date_str = datetime.now().strftime("%Y%m%d")
    output_file = OUTPUT_DIR / f"skills-gap-{date_str}.txt"
    
    total_employees = len(inventory.get("employee_skills", []))
    skill_counts = defaultdict(int)
    
    for es in inventory.get("employee_skills", []):
        for category, skills in es.get("skills", {}).items():
            for skill in skills:
                skill_counts[(category, skill)] += 1
    
    lines = []
    lines.append("SKILLS GAP ANALYSIS REPORT")
    lines.append("=" * 60)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Total Employees: {total_employees}")
    lines.append("")
    
    for category in SKILL_CATEGORIES:
        skills = taxonomy.get(category, [])
        if skills:
            lines.append(f"\n{category.replace('_', ' ').title()}:")
            for skill in skills:
                count = skill_counts.get((category, skill), 0)
                pct = (count / total_employees * 100) if total_employees else 0
                lines.append(f"  {skill}: {pct:.0f}% coverage ({count}/{total_employees})")
    
    content = "\n".join(lines)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(content)
    print(f"\n✅ Exported to: {output_file}")
    logger.info(f"Exported skills gap report")
    return 0


def cmd_init(args) -> int:
    """Initialize skills inventory."""
    inventory_file = DATA_DIR / "skills_inventory.json"
    
    if inventory_file.exists():
        print(f"⚠️  {inventory_file} already exists")
    else:
        save_json(inventory_file, get_default_skills_inventory())
        print(f"✅ Created: {inventory_file}")
    
    logger.info("Initialized skills inventory")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Skills Inventory Agent - Track and analyze employee skills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --init                           Initialize data
  %(prog)s --list-all                       List all skills in taxonomy
  %(prog)s --add-skill emp_123 --category programming_languages --skill Python
  %(prog)s --remove-skill emp_123 --category languages --skill German
  %(prog)s --show-employee emp_123         Show employee's skills
  %(prog)s --search Python                  Search employees with Python
  %(prog)s --gap-analysis                   Show skills coverage
  %(prog)s --export-gaps                    Export gap report to file
        """,
    )
    
    parser.add_argument("--init", action="store_true", help="Initialize data files")
    parser.add_argument("--list-all", action="store_true", help="List all skills in taxonomy")
    parser.add_argument("--add-skill", action="store_true", help="Add skill to employee")
    parser.add_argument("--remove-skill", action="store_true", help="Remove skill from employee")
    parser.add_argument("--employee-id", dest="employee_id", help="Employee ID")
    parser.add_argument("--category", help="Skill category")
    parser.add_argument("--skill", help="Skill name")
    parser.add_argument("--show-employee", dest="employee_id", help="Show employee skills")
    parser.add_argument("--search", help="Search for employees with skill")
    parser.add_argument("--gap-analysis", action="store_true", help="Run gap analysis")
    parser.add_argument("--export-gaps", action="store_true", help="Export gap report")
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        parser.print_help()
        print("\n💡 Quick start: %(prog)s --init && %(prog)s --list-all")
        return 0
    
    try:
        if args.init:
            return cmd_init(args)
        if args.list_all:
            return cmd_list_all(args)
        if args.add_skill:
            if not args.employee_id or not args.category or not args.skill:
                logger.error("--employee-id, --category, and --skill required for --add-skill")
                return 1
            if args.category not in SKILL_CATEGORIES:
                logger.error(f"Invalid category. Valid: {', '.join(SKILL_CATEGORIES)}")
                return 1
            return cmd_add_skill(args)
        if args.remove_skill:
            if not args.employee_id or not args.category or not args.skill:
                logger.error("--employee-id, --category, and --skill required for --remove-skill")
                return 1
            return cmd_remove_skill(args)
        if "--show-employee" in sys.argv:
            emp_id = getattr(args, 'employee_id', None)
            if emp_id:
                args.employee_id = emp_id
                return cmd_show_employee(args)
        if args.search:
            return cmd_search(args)
        if args.gap_analysis:
            return cmd_gap_analysis(args)
        if args.export_gaps:
            return cmd_export_gaps(args)
        
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
