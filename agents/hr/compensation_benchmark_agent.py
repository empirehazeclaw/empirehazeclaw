#!/usr/bin/env python3
"""
Compensation Benchmark Agent
Manages salary bands, compensation benchmarks, and equity data.
Reads: compensation_data.json, employees.json
Writes: compensation_data.json, output/compensation-report-<date>.txt
"""

import argparse
import json
import logging
import sys
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
        logging.FileHandler(LOGS_DIR / "compensation_benchmark.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("CompensationBenchmark")


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


def get_default_compensation_data() -> dict:
    return {
        "salary_bands": [
            {
                "id": "sb_software_eng",
                "title_pattern": "Software Engineer",
                "level": "mid",
                "currency": "USD",
                "min_salary": 70000,
                "mid_salary": 85000,
                "max_salary": 105000,
                "bonus_target": 0.10,
                "equity_range": "0.01-0.05",
            },
            {
                "id": "sb_senior_eng",
                "title_pattern": "Senior Software Engineer",
                "level": "senior",
                "currency": "USD",
                "min_salary": 100000,
                "mid_salary": 125000,
                "max_salary": 155000,
                "bonus_target": 0.15,
                "equity_range": "0.05-0.15",
            },
            {
                "id": "sb_product_mgr",
                "title_pattern": "Product Manager",
                "level": "senior",
                "currency": "USD",
                "min_salary": 95000,
                "mid_salary": 115000,
                "max_salary": 140000,
                "bonus_target": 0.12,
                "equity_range": "0.03-0.10",
            },
            {
                "id": "sb_marketing_mgr",
                "title_pattern": "Marketing Manager",
                "level": "mid",
                "currency": "USD",
                "min_salary": 60000,
                "mid_salary": 75000,
                "max_salary": 90000,
                "bonus_target": 0.08,
                "equity_range": "0.01-0.03",
            },
        ],
        "market_benchmarks": {
            "2026": {
                "software_engineer_mid": {"min": 75000, "mid": 90000, "max": 110000, "source": "market_data"},
                "senior_engineer": {"min": 105000, "mid": 130000, "max": 160000, "source": "market_data"},
            }
        },
        "adjustments": [],
    }


def find_matching_band(title: str, bands: list) -> dict | None:
    """Find salary band matching a job title."""
    title_lower = title.lower()
    for band in bands:
        pattern = band.get("title_pattern", "").lower()
        if pattern in title_lower or title_lower in pattern:
            return band
    return bands[0] if bands else None


def cmd_list_bands(args) -> int:
    """List all salary bands."""
    data = load_json(DATA_DIR / "compensation_data.json")
    if not data:
        data = get_default_compensation_data()
    
    bands = data.get("salary_bands", [])
    
    if not bands:
        print("No salary bands defined.")
        return 0
    
    print(f"\n💰 SALARY BANDS ({len(bands)} total)")
    print("-" * 80)
    for band in bands:
        print(f"  [{band['id']}] {band['title_pattern']} ({band['level']})")
        print(f"       Range: {band['currency']} {band['min_salary']:,} - {band['max_salary']:,}")
        print(f"       Midpoint: {band['mid_salary']:,} | Bonus Target: {band['bonus_target']*100:.0f}%")
        print(f"       Equity: {band.get('equity_range', 'N/A')}")
    print()
    return 0


def cmd_add_band(args) -> int:
    """Add a new salary band."""
    data = load_json(DATA_DIR / "compensation_data.json")
    if not data:
        data = get_default_compensation_data()
    
    band = {
        "id": f"sb_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "title_pattern": args.title,
        "level": args.level or "mid",
        "currency": args.currency or "USD",
        "min_salary": args.min_salary,
        "mid_salary": args.mid_salary,
        "max_salary": args.max_salary,
        "bonus_target": (args.bonus_target or 10) / 100,
        "equity_range": args.equity or "0",
    }
    
    data.setdefault("salary_bands", []).append(band)
    save_json(DATA_DIR / "compensation_data.json", data)
    
    print(f"✅ Added salary band: {band['id']}")
    print(f"   Title: {band['title_pattern']}")
    print(f"   Range: {band['currency']} {band['min_salary']:,} - {band['max_salary']:,}")
    logger.info(f"Added salary band {band['id']}")
    return 0


def cmd_analyze(args) -> int:
    """Analyze compensation for an employee against bands."""
    employees = load_json(DATA_DIR / "employees.json") or []
    data = load_json(DATA_DIR / "compensation_data.json") or get_default_compensation_data()
    
    employee = None
    for emp in employees:
        if emp.get("id") == args.employee_id or emp.get("email", "").lower() == args.employee_id.lower():
            employee = emp
            break
    
    if not employee and not args.employee_id.startswith("emp_"):
        logger.error(f"Employee not found: {args.employee_id}")
        return 1
    
    title = args.title or employee.get("title", "Unknown") if employee else args.employee_id
    band = find_matching_band(title, data.get("salary_bands", []))
    current_salary = args.salary or employee.get("salary", 0) if employee else args.salary
    
    print(f"\n📊 COMPENSATION ANALYSIS")
    print("=" * 60)
    print(f"Employee: {employee.get('name', title) if employee else title}")
    print(f"Title: {title}")
    
    if band:
        print(f"\n💼 Matching Band: {band['title_pattern']} ({band['level']})")
        print(f"   Range: {band['currency']} {band['min_salary']:,} - {band['max_salary']:,}")
        print(f"   Midpoint: {band['mid_salary']:,}")
        
        if current_salary:
            pct_of_mid = (current_salary / band['mid_salary']) * 100 if band['mid_salary'] else 0
            pct_of_min = ((current_salary - band['min_salary']) / (band['max_salary'] - band['min_salary'])) * 100 if band['max_salary'] != band['min_salary'] else 50
            
            print(f"\n📈 Current Salary Analysis")
            print(f"   Current: {band['currency']} {current_salary:,}")
            print(f"   % of Midpoint: {pct_of_mid:.1f}%")
            print(f"   Position in Band: {pct_of_min:.1f}%")
            
            if current_salary < band['min_salary']:
                print(f"   ⚠️  BELOW minimum - consider increase")
            elif current_salary > band['max_salary']:
                print(f"   ⚠️  ABOVE maximum - validate level")
            else:
                print(f"   ✅ Within band")
    else:
        print("\n⚠️  No matching salary band found")
    
    print()
    return 0


def cmd_update_salary(args) -> int:
    """Update an employee's salary."""
    employees_file = DATA_DIR / "employees.json"
    employees = load_json(employees_file) or []
    
    for emp in employees:
        if emp.get("id") == args.employee_id or emp.get("email", "").lower() == args.employee_id.lower():
            old_salary = emp.get("salary", 0)
            emp["salary"] = args.salary
            emp["salary_updated_at"] = datetime.now().isoformat()
            save_json(employees_file, employees)
            print(f"✅ Updated salary for {emp['name']}")
            print(f"   Old: {old_salary} → New: {args.salary}")
            logger.info(f"Updated salary for {emp['id']}: {old_salary} → {args.salary}")
            return 0
    
    logger.error(f"Employee not found: {args.employee_id}")
    return 1


def cmd_export_report(args) -> int:
    """Export compensation report."""
    employees = load_json(DATA_DIR / "employees.json") or []
    data = load_json(DATA_DIR / "compensation_data.json") or get_default_compensation_data()
    
    date_str = datetime.now().strftime("%Y%m%d")
    output_file = OUTPUT_DIR / f"compensation-report-{date_str}.txt"
    
    lines = []
    lines.append("COMPENSATION REPORT")
    lines.append("=" * 60)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    
    lines.append("SALARY BANDS")
    lines.append("-" * 40)
    for band in data.get("salary_bands", []):
        lines.append(f"  {band['title_pattern']} ({band['level']})")
        lines.append(f"    Range: {band['currency']} {band['min_salary']:,} - {band['max_salary']:,}")
    lines.append("")
    
    lines.append("EMPLOYEE COMPENSATION")
    lines.append("-" * 40)
    for emp in employees:
        salary = emp.get("salary", 0)
        band = find_matching_band(emp.get("title", ""), data.get("salary_bands", []))
        status = "✅" if band and band["min_salary"] <= salary <= band["max_salary"] else "⚠️"
        lines.append(f"  {status} {emp.get('name', 'Unknown')}")
        lines.append(f"    Title: {emp.get('title', 'N/A')} | Salary: {salary}")
    
    content = "\n".join(lines)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(content)
    print(f"\n✅ Report exported to: {output_file}")
    logger.info(f"Exported compensation report")
    return 0


def cmd_init(args) -> int:
    """Initialize compensation data file."""
    comp_file = DATA_DIR / "compensation_data.json"
    
    if comp_file.exists():
        print(f"⚠️  {comp_file} already exists")
    else:
        save_json(comp_file, get_default_compensation_data())
        print(f"✅ Created: {comp_file}")
    
    logger.info("Initialized compensation data")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compensation Benchmark Agent - Manage salary bands and benchmarks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --init                           Initialize data
  %(prog)s --list-bands                     List all salary bands
  %(prog)s --add-band --title "Designer" --min 60000 --mid 75000 --max 95000
  %(prog)s --analyze emp_123                Analyze employee compensation
  %(prog)s --analyze emp_123 --salary 90000 Analyze with custom salary
  %(prog)s --update-salary emp_123 --salary 95000
  %(prog)s --export-report                  Export full report
        """,
    )
    
    parser.add_argument("--init", action="store_true", help="Initialize data files")
    parser.add_argument("--list-bands", action="store_true", help="List salary bands")
    parser.add_argument("--add-band", action="store_true", help="Add a new salary band")
    parser.add_argument("--title", help="Job title (for --add-band or --analyze)")
    parser.add_argument("--level", default="mid", help="Level (entry/mid/senior)")
    parser.add_argument("--currency", default="USD", help="Currency code")
    parser.add_argument("--min-salary", type=int, dest="min_salary", help="Minimum salary")
    parser.add_argument("--mid-salary", type=int, dest="mid_salary", help="Midpoint salary")
    parser.add_argument("--max-salary", type=int, dest="max_salary", help="Maximum salary")
    parser.add_argument("--bonus-target", type=float, dest="bonus_target", help="Bonus target %%")
    parser.add_argument("--equity", help="Equity range (e.g. 0.01-0.05)")
    parser.add_argument("--analyze", dest="employee_id", help="Analyze compensation")
    parser.add_argument("--salary", type=int, help="Current salary")
    parser.add_argument("--update-salary", dest="employee_id", help="Update employee salary")
    parser.add_argument("--export-report", action="store_true", help="Export report")
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        parser.print_help()
        print("\n💡 Quick start: %(prog)s --init && %(prog)s --list-bands")
        return 0
    
    try:
        if args.init:
            return cmd_init(args)
        if args.list_bands:
            return cmd_list_bands(args)
        if args.add_band:
            if not args.title or not args.min_salary or not args.mid_salary or not args.max_salary:
                logger.error("--title, --min-salary, --mid-salary, --max-salary required for --add-band")
                return 1
            return cmd_add_band(args)
        if "--analyze" in sys.argv and "--update-salary" not in sys.argv:
            return cmd_analyze(args)
        if "--update-salary" in sys.argv:
            if not args.salary:
                logger.error("--salary required for --update-salary")
                return 1
            return cmd_update_salary(args)
        if args.export_report:
            return cmd_export_report(args)
        
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
