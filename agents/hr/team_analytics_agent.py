#!/usr/bin/env python3
"""
Team Analytics Agent
Analyzes team metrics, headcount, department distribution, and trends.
Reads: employees.json, reviews.json, onboarding_progress.json
Writes: analytics.json, output/team-report-<date>.txt
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
        logging.FileHandler(LOGS_DIR / "team_analytics.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("TeamAnalytics")


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


def calculate_analytics() -> dict:
    """Calculate all team analytics."""
    employees = load_json(DATA_DIR / "employees.json") or []
    reviews = load_json(DATA_DIR / "reviews.json") or []
    progress = load_json(DATA_DIR / "onboarding_progress.json") or []
    
    analytics = {
        "generated_at": datetime.now().isoformat(),
        "headcount": {
            "total": len(employees),
            "by_status": defaultdict(int),
            "by_department": defaultdict(int),
        },
        "onboarding": {
            "active": 0,
            "completed": 0,
        },
        "performance": {
            "total_reviews": len(reviews),
            "average_rating": 0,
            "rating_distribution": defaultdict(int),
        },
        "department_breakdown": [],
    }
    
    # Headcount by status and department
    for emp in employees:
        analytics["headcount"]["by_status"][emp.get("status", "unknown")] += 1
        analytics["headcount"]["by_department"][emp.get("department", "Unknown")] += 1
    
    # Onboarding status
    for p in progress:
        if p.get("status") == "in_progress":
            analytics["onboarding"]["active"] += 1
        elif p.get("status") == "completed":
            analytics["onboarding"]["completed"] += 1
    
    # Performance ratings
    ratings = [r.get("overall_rating", 0) for r in reviews if r.get("overall_rating")]
    if ratings:
        analytics["performance"]["average_rating"] = round(sum(ratings) / len(ratings), 2)
    for r in reviews:
        analytics["performance"]["rating_distribution"][r.get("overall_rating", 0)] += 1
    
    # Department breakdown
    for dept, count in analytics["headcount"]["by_department"].items():
        dept_emps = [e for e in employees if e.get("department") == dept]
        dept_reviews = [r for r in reviews if r.get("employee_id") in [e.get("id") for e in dept_emps]]
        dept_ratings = [r.get("overall_rating", 0) for r in dept_reviews if r.get("overall_rating")]
        
        analytics["department_breakdown"].append({
            "department": dept,
            "headcount": count,
            "avg_rating": round(sum(dept_ratings) / len(dept_ratings), 2) if dept_ratings else 0,
            "review_count": len(dept_reviews),
        })
    
    # Convert defaultdicts to regular dicts for JSON
    analytics["headcount"]["by_status"] = dict(analytics["headcount"]["by_status"])
    analytics["headcount"]["by_department"] = dict(analytics["headcount"]["by_department"])
    analytics["performance"]["rating_distribution"] = dict(analytics["performance"]["rating_distribution"])
    
    return analytics


def cmd_dashboard(args) -> int:
    """Show analytics dashboard."""
    analytics = calculate_analytics()
    
    print("\n📊 TEAM ANALYTICS DASHBOARD")
    print("=" * 50)
    print(f"Generated: {analytics['generated_at'][:19]}")
    print()
    
    print("👥 HEADCOUNT")
    print("-" * 30)
    hc = analytics["headcount"]
    print(f"  Total Employees: {hc['total']}")
    print("  By Status:")
    for status, count in hc["by_status"].items():
        print(f"    {status}: {count}")
    print("  By Department:")
    for dept, count in hc["by_department"].items():
        print(f"    {dept}: {count}")
    print()
    
    print("🔄 ONBOARDING")
    print("-" * 30)
    onb = analytics["onboarding"]
    print(f"  Active: {onb['active']}")
    print(f"  Completed: {onb['completed']}")
    print()
    
    print("📈 PERFORMANCE")
    print("-" * 30)
    perf = analytics["performance"]
    print(f"  Total Reviews: {perf['total_reviews']}")
    print(f"  Average Rating: {perf['average_rating']}/5")
    if perf["rating_distribution"]:
        print("  Rating Distribution:")
        for rating, count in sorted(perf["rating_distribution"].items()):
            bar = "█" * count
            print(f"    {rating}: {bar} ({count})")
    print()
    
    if analytics["department_breakdown"]:
        print("🏢 DEPARTMENT BREAKDOWN")
        print("-" * 30)
        for dept in sorted(analytics["department_breakdown"], key=lambda x: x["headcount"], reverse=True):
            print(f"  {dept['department']}: {dept['headcount']} employees, avg rating: {dept['avg_rating']}/5")
        print()
    
    return 0


def cmd_save(args) -> int:
    """Save analytics to JSON file."""
    analytics = calculate_analytics()
    
    date_str = datetime.now().strftime("%Y%m%d")
    output_file = DATA_DIR / f"analytics-{date_str}.json"
    
    save_json(output_file, analytics)
    
    # Also save latest
    save_json(DATA_DIR / "analytics_latest.json", analytics)
    
    print(f"✅ Analytics saved to: {output_file}")
    logger.info(f"Saved analytics snapshot")
    return 0


def cmd_export_report(args) -> int:
    """Export full team report to text file."""
    analytics = calculate_analytics()
    employees = load_json(DATA_DIR / "employees.json") or []
    reviews = load_json(DATA_DIR / "reviews.json") or []
    
    date_str = datetime.now().strftime("%Y%m%d")
    output_file = OUTPUT_DIR / f"team-report-{date_str}.txt"
    
    lines = []
    lines.append("TEAM REPORT")
    lines.append("=" * 60)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    
    lines.append("EXECUTIVE SUMMARY")
    lines.append("-" * 30)
    lines.append(f"Total Headcount: {analytics['headcount']['total']}")
    lines.append(f"Active Onboarding: {analytics['onboarding']['active']}")
    lines.append(f"Total Reviews: {analytics['performance']['total_reviews']}")
    lines.append(f"Average Rating: {analytics['performance']['average_rating']}/5")
    lines.append("")
    
    lines.append("HEADCOUNT BY DEPARTMENT")
    lines.append("-" * 30)
    for dept in sorted(analytics["department_breakdown"], key=lambda x: x["headcount"], reverse=True):
        lines.append(f"  {dept['department']}: {dept['headcount']}")
    lines.append("")
    
    lines.append("EMPLOYEE LIST")
    lines.append("-" * 30)
    for emp in employees:
        lines.append(f"  [{emp.get('id', 'N/A')}] {emp.get('name', 'Unknown')}")
        lines.append(f"    {emp.get('title', 'N/A')} | {emp.get('department', 'N/A')}")
        lines.append(f"    Status: {emp.get('status', 'N/A')} | Since: {emp.get('start_date', 'N/A')}")
    lines.append("")
    
    lines.append("PERFORMANCE REVIEW SUMMARY")
    lines.append("-" * 30)
    for r in reviews:
        lines.append(f"  [{r.get('id', 'N/A')}] {r.get('employee_name', 'Unknown')}")
        lines.append(f"    Rating: {r.get('overall_rating', 'N/A')}/5 | Period: {r.get('review_period', 'N/A')}")
        lines.append(f"    Status: {r.get('status', 'N/A')}")
    lines.append("")
    
    content = "\n".join(lines)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(content)
    print(f"\n✅ Report exported to: {output_file}")
    logger.info(f"Exported team report to {output_file}")
    return 0


def cmd_trends(args) -> int:
    """Show hiring/performance trends."""
    employees = load_json(DATA_DIR / "employees.json") or []
    
    # Group by month
    by_month = defaultdict(list)
    for emp in employees:
        start = emp.get("start_date", "")
        if start:
            month = start[:7]  # YYYY-MM
            by_month[month].append(emp)
    
    print("\n📈 HIRING TRENDS")
    print("=" * 40)
    print("Month      | Hires")
    print("-" * 40)
    
    for month in sorted(by_month.keys()):
        hires = by_month[month]
        bar = "█" * len(hires)
        print(f"{month} | {bar} ({len(hires)})")
    
    if not by_month:
        print("No hiring data available.")
    print()
    
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Team Analytics Agent - Analyze team metrics and trends",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --dashboard           Show analytics dashboard
  %(prog)s --save                 Save analytics to JSON
  %(prog)s --export-report        Export full team report
  %(prog)s --trends               Show hiring trends
        """,
    )
    
    parser.add_argument("--dashboard", action="store_true", help="Show analytics dashboard")
    parser.add_argument("--save", action="store_true", help="Save analytics snapshot")
    parser.add_argument("--export-report", action="store_true", help="Export full report")
    parser.add_argument("--trends", action="store_true", help="Show hiring trends")
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        parser.print_help()
        print("\n💡 Quick start: %(prog)s --dashboard")
        return 0
    
    try:
        if args.dashboard:
            return cmd_dashboard(args)
        if args.save:
            return cmd_save(args)
        if args.export_report:
            return cmd_export_report(args)
        if args.trends:
            return cmd_trends(args)
        
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
