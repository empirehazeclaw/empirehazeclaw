#!/usr/bin/env python3
"""
Performance Review Agent
Manages employee performance reviews, goals, and feedback cycles.
Reads: employees.json, reviews.json, goals.json
Writes: reviews.json, goals.json, output/review-<employee>-<date>.txt
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
        logging.FileHandler(LOGS_DIR / "performance_review.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("PerformanceReview")


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


def rating_to_label(rating: int) -> str:
    labels = {
        1: "Needs Improvement",
        2: "Below Expectations",
        3: "Meets Expectations",
        4: "Exceeds Expectations",
        5: "Outstanding",
    }
    return labels.get(rating, f"Rating {rating}")


def cmd_create_review(args) -> int:
    """Create a new performance review."""
    reviews_file = DATA_DIR / "reviews.json"
    employees_file = DATA_DIR / "employees.json"
    
    reviews = load_json(reviews_file) or []
    employees = load_json(employees_file) or []
    
    employee = None
    for emp in employees:
        if emp.get("id") == args.employee_id or emp.get("email", "").lower() == args.employee_id.lower():
            employee = emp
            break
    
    review = {
        "id": f"rev_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "employee_id": employee["id"] if employee else args.employee_id,
        "employee_name": employee.get("name", "Unknown") if employee else args.employee_id,
        "review_type": args.review_type or "annual",
        "review_period": args.period or f"{datetime.now().year}",
        "status": "draft",
        "overall_rating": args.rating or 3,
        "strengths": args.strengths.split("|") if args.strengths else [],
        "areas_for_improvement": args.improvements.split("|") if args.improvements else [],
        "goals_achieved": args.goals_achieved.split("|") if args.goals_achieved else [],
        "feedback": args.feedback or "",
        "created_at": datetime.now().isoformat(),
        "created_by": args.reviewer or "HR",
    }
    
    reviews.append(review)
    save_json(reviews_file, reviews)
    
    print(f"✅ Created review: {review['id']}")
    print(f"   Employee: {review['employee_name']}")
    print(f"   Rating: {review['overall_rating']}/5 ({rating_to_label(review['overall_rating'])})")
    logger.info(f"Created review {review['id']} for {review['employee_name']}")
    return 0


def cmd_list_reviews(args) -> int:
    """List all reviews."""
    reviews_file = DATA_DIR / "reviews.json"
    reviews = load_json(reviews_file) or []
    
    if not reviews:
        print("No reviews found.")
        return 0
    
    status_icons = {"draft": "📝", "submitted": "📤", "acknowledged": "✅", "archived": "📦"}
    
    print(f"\n📊 Performance Reviews ({len(reviews)} total):")
    print("-" * 70)
    for r in reviews:
        icon = status_icons.get(r.get("status", "unknown"), "❓")
        rating = r.get("overall_rating", 0)
        print(f"  {icon} [{r['id']}] {r.get('employee_name', 'Unknown')}")
        print(f"       Type: {r.get('review_type', 'N/A')} | Period: {r.get('review_period', 'N/A')}")
        print(f"       Rating: {rating}/5 ({rating_to_label(rating)}) | Status: {r.get('status', 'unknown')}")
    print()
    return 0


def cmd_show_review(args) -> int:
    """Show details of a specific review."""
    reviews_file = DATA_DIR / "reviews.json"
    reviews = load_json(reviews_file) or []
    
    for r in reviews:
        if r.get("id") == args.review_id:
            print(f"\n📋 Review: {r['id']}")
            print("=" * 50)
            print(f"  Employee: {r.get('employee_name', 'Unknown')}")
            print(f"  Type: {r.get('review_type', 'N/A')}")
            print(f"  Period: {r.get('review_period', 'N/A')}")
            print(f"  Status: {r.get('status', 'unknown')}")
            print(f"  Overall Rating: {r.get('overall_rating', 0)}/5 ({rating_to_label(r.get('overall_rating', 0))})")
            print(f"  Created: {r.get('created_at', 'N/A')[:10]}")
            print(f"  Reviewer: {r.get('created_by', 'N/A')}")
            
            if r.get("strengths"):
                print("\n  Strengths:")
                for s in r["strengths"]:
                    print(f"    ✅ {s}")
            
            if r.get("areas_for_improvement"):
                print("\n  Areas for Improvement:")
                for a in r["areas_for_improvement"]:
                    print(f"    📝 {a}")
            
            if r.get("goals_achieved"):
                print("\n  Goals Achieved:")
                for g in r["goals_achieved"]:
                    print(f"    🎯 {g}")
            
            if r.get("feedback"):
                print(f"\n  Feedback:\n  {r['feedback']}")
            
            return 0
    
    logger.error(f"Review not found: {args.review_id}")
    return 1


def cmd_set_goal(args) -> int:
    """Set a goal for an employee."""
    goals_file = DATA_DIR / "goals.json"
    goals = load_json(goals_file) or []
    
    goal = {
        "id": f"goal_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "employee_id": args.employee_id,
        "title": args.title,
        "description": args.description or "",
        "category": args.category or "professional",
        "due_date": args.due_date or "",
        "status": "active",
        "progress": 0,
        "created_at": datetime.now().isoformat(),
    }
    
    goals.append(goal)
    save_json(goals_file, goals)
    
    print(f"✅ Created goal: {goal['id']}")
    print(f"   Title: {goal['title']}")
    print(f"   Employee: {goal['employee_id']}")
    logger.info(f"Created goal {goal['id']} for {goal['employee_id']}")
    return 0


def cmd_list_goals(args) -> int:
    """List goals, optionally filtered by employee."""
    goals_file = DATA_DIR / "goals.json"
    goals = load_json(goals_file) or []
    
    if args.employee_id:
        goals = [g for g in goals if g.get("employee_id") == args.employee_id]
    
    if not goals:
        print("No goals found.")
        return 0
    
    print(f"\n🎯 Goals ({len(goals)} total):")
    print("-" * 60)
    for g in goals:
        status_icon = "🟢" if g.get("status") == "active" else "🔵" if g.get("status") == "completed" else "⚪"
        print(f"  {status_icon} [{g['id']}] {g.get('title', 'Untitled')}")
        print(f"       Employee: {g.get('employee_id', 'N/A')} | Category: {g.get('category', 'N/A')}")
        print(f"       Progress: {g.get('progress', 0)}% | Due: {g.get('due_date', 'N/A')}")
    print()
    return 0


def cmd_update_progress(args) -> int:
    """Update goal progress."""
    goals_file = DATA_DIR / "goals.json"
    goals = load_json(goals_file) or []
    
    for g in goals:
        if g.get("id") == args.goal_id:
            g["progress"] = min(100, max(0, args.progress))
            if g["progress"] >= 100:
                g["status"] = "completed"
                g["completed_at"] = datetime.now().isoformat()
            save_json(goals_file, goals)
            print(f"✅ Updated goal {args.goal_id}: {args.progress}% complete")
            logger.info(f"Updated goal {args.goal_id} to {args.progress}%")
            return 0
    
    logger.error(f"Goal not found: {args.goal_id}")
    return 1


def cmd_export_review(args) -> int:
    """Export a review to a text file."""
    reviews_file = DATA_DIR / "reviews.json"
    reviews = load_json(reviews_file) or []
    
    for r in reviews:
        if r.get("id") == args.review_id:
            date_str = datetime.now().strftime("%Y%m%d")
            safe_name = r.get("employee_name", "unknown").lower().replace(" ", "-")
            output_file = OUTPUT_DIR / f"review-{safe_name}-{date_str}.txt"
            
            lines = []
            lines.append(f"PERFORMANCE REVIEW")
            lines.append("=" * 50)
            lines.append(f"Employee: {r.get('employee_name', 'Unknown')}")
            lines.append(f"Review ID: {r.get('id', 'N/A')}")
            lines.append(f"Type: {r.get('review_type', 'N/A')}")
            lines.append(f"Period: {r.get('review_period', 'N/A')}")
            lines.append(f"Date: {r.get('created_at', 'N/A')[:10]}")
            lines.append(f"Overall Rating: {r.get('overall_rating', 0)}/5 ({rating_to_label(r.get('overall_rating', 0))})")
            lines.append("")
            
            if r.get("strengths"):
                lines.append("STRENGTHS:")
                for s in r["strengths"]:
                    lines.append(f"  - {s}")
                lines.append("")
            
            if r.get("areas_for_improvement"):
                lines.append("AREAS FOR IMPROVEMENT:")
                for a in r["areas_for_improvement"]:
                    lines.append(f"  - {a}")
                lines.append("")
            
            if r.get("goals_achieved"):
                lines.append("GOALS ACHIEVED:")
                for g in r["goals_achieved"]:
                    lines.append(f"  - {g}")
                lines.append("")
            
            if r.get("feedback"):
                lines.append("FEEDBACK:")
                lines.append(r["feedback"])
                lines.append("")
            
            content = "\n".join(lines)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(content)
            print(f"\n✅ Exported to: {output_file}")
            return 0
    
    logger.error(f"Review not found: {args.review_id}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Performance Review Agent - Manage reviews and goals",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list-reviews                      List all reviews
  %(prog)s --create-review emp_123 --rating 4 --strengths "Fast learner|Team player"
  %(prog)s --show-review rev_20260327120000
  %(prog)s --export-review rev_20260327120000
  %(prog)s --set-goal emp_123 --title "Learn Python" --due-date 2026-06-01
  %(prog)s --list-goals emp_123
  %(prog)s --update-progress goal_123 --progress 50
        """,
    )
    
    parser.add_argument("--list-reviews", action="store_true", help="List all reviews")
    parser.add_argument("--create-review", dest="employee_id", help="Create review for employee ID")
    parser.add_argument("--review-id", dest="review_id", help="Review ID")
    parser.add_argument("--show-review", dest="review_id", help="Show review details")
    parser.add_argument("--export-review", dest="review_id", help="Export review to file")
    parser.add_argument("--rating", type=int, default=3, help="Overall rating (1-5)")
    parser.add_argument("--strengths", help="Strengths (pipe-separated)")
    parser.add_argument("--improvements", dest="improvements", help="Areas for improvement (pipe-separated)")
    parser.add_argument("--goals-achieved", dest="goals_achieved", help="Goals achieved (pipe-separated)")
    parser.add_argument("--feedback", help="General feedback text")
    parser.add_argument("--review-type", dest="review_type", default="annual", help="Review type")
    parser.add_argument("--period", help="Review period (e.g. 2025)")
    parser.add_argument("--reviewer", help="Reviewer name")
    parser.add_argument("--set-goal", dest="employee_id", help="Set goal for employee")
    parser.add_argument("--title", help="Goal title")
    parser.add_argument("--description", help="Goal description")
    parser.add_argument("--category", default="professional", help="Goal category")
    parser.add_argument("--due-date", dest="due_date", help="Due date (YYYY-MM-DD)")
    parser.add_argument("--list-goals", dest="employee_id", nargs="?", const="all", help="List goals")
    parser.add_argument("--update-progress", dest="goal_id", help="Update goal progress")
    parser.add_argument("--progress", type=int, help="Progress percentage (0-100)")
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        parser.print_help()
        return 0
    
    try:
        if args.list_reviews:
            return cmd_list_reviews(args)
        if "--create-review" in sys.argv and "--set-goal" not in sys.argv:
            return cmd_create_review(args)
        if "--show-review" in sys.argv:
            return cmd_show_review(args)
        if "--export-review" in sys.argv:
            return cmd_export_review(args)
        if "--set-goal" in sys.argv:
            if not args.title:
                logger.error("--title required for --set-goal")
                return 1
            return cmd_set_goal(args)
        if "--list-goals" in sys.argv:
            return cmd_list_goals(args)
        if "--update-progress" in sys.argv:
            if args.progress is None:
                logger.error("--progress required for --update-progress")
                return 1
            return cmd_update_progress(args)
        
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
