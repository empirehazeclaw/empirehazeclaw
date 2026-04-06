#!/usr/bin/env python3
"""
Supplier Scorecard Agent
========================
Track and score supplier performance based on delivery, quality, and cost.

Usage:
    python3 supplier_scorecard_agent.py --score --supplier <name>
    python3 supplier_scorecard_agent.py --add-delivery --supplier <name> --on-time <0|1> --quality <0-100>
    python3 supplier_scorecard_agent.py --report
    python3 supplier_scorecard_agent.py --list-suppliers
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "supplier_scorecard.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Data paths
DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data/agents/supply-chain")
DATA_DIR.mkdir(parents=True, exist_ok=True)
SUPPLIERS_FILE = DATA_DIR / "suppliers.json"
DELIVERIES_FILE = DATA_DIR / "deliveries.json"
SCORES_FILE = DATA_DIR / "supplier_scores.json"


def load_json(filepath: Path, default: dict = {}) -> dict:
    """Load JSON data from file."""
    try:
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return default
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
        return default


def save_json(filepath: Path, data: dict) -> bool:
    """Save JSON data to file."""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        logger.error(f"Error saving {filepath}: {e}")
        return False


def initialize_data():
    """Initialize sample data."""
    if not SUPPLIERS_FILE.exists():
        save_json(SUPPLIERS_FILE, {
            "suppliers": {
                "Acme Corp": {
                    "name": "Acme Corp",
                    "category": "Electronics",
                    "contact": "sales@acme.com",
                    "contract_start": "2024-01-15",
                    "active": True
                },
                "Global Parts Ltd": {
                    "name": "Global Parts Ltd",
                    "category": "Components",
                    "contact": "procurement@globalparts.com",
                    "contract_start": "2024-03-01",
                    "active": True
                },
                "FastShip Inc": {
                    "name": "FastShip Inc",
                    "category": "Logistics",
                    "contact": "orders@fastship.com",
                    "contract_start": "2024-06-01",
                    "active": True
                }
            },
            "last_updated": datetime.now().isoformat()
        })
        logger.info("Initialized suppliers data")
    
    if not DELIVERIES_FILE.exists():
        save_json(DELIVERIES_FILE, {"deliveries": []})
        logger.info("Initialized deliveries data")
    
    if not SCORES_FILE.exists():
        save_json(SCORES_FILE, {"scores": {}})
        logger.info("Initialized scores")


def calculate_score(supplier_name: str) -> dict:
    """Calculate performance score for a supplier."""
    deliveries = load_json(DELIVERIES_FILE)
    suppliers = load_json(SUPPLIERS_FILE)
    
    if supplier_name not in suppliers.get("suppliers", {}):
        raise ValueError(f"Supplier {supplier_name} not found")
    
    # Get all deliveries for this supplier
    supplier_deliveries = [d for d in deliveries.get("deliveries", []) if d["supplier"] == supplier_name]
    
    if not supplier_deliveries:
        return {
            "supplier": supplier_name,
            "score": 0,
            "grade": "N/A",
            "total_deliveries": 0,
            "on_time_rate": 0,
            "quality_score": 0,
            "cost_score": 0,
            "message": "No delivery data available"
        }
    
    # Calculate metrics
    total = len(supplier_deliveries)
    on_time = sum(1 for d in supplier_deliveries if d.get("on_time", 0) == 1)
    on_time_rate = (on_time / total) * 100 if total > 0 else 0
    
    quality_scores = [d.get("quality_score", 0) for d in supplier_deliveries if d.get("quality_score", 0) > 0]
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
    
    cost_scores = [d.get("cost_score", 0) for d in supplier_deliveries if d.get("cost_score", 0) > 0]
    avg_cost = sum(cost_scores) / len(cost_scores) if cost_scores else 0
    
    # Weighted score
    # On-time: 40%, Quality: 40%, Cost: 20%
    score = (on_time_rate * 0.4) + (avg_quality * 0.4) + (avg_cost * 0.2)
    
    # Determine grade
    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "F"
    
    return {
        "supplier": supplier_name,
        "score": round(score, 1),
        "grade": grade,
        "total_deliveries": total,
        "on_time_deliveries": on_time,
        "on_time_rate": round(on_time_rate, 1),
        "quality_score": round(avg_quality, 1),
        "cost_score": round(avg_cost, 1),
        "calculated": datetime.now().isoformat()
    }


def add_delivery(supplier: str, on_time: int, quality_score: int, 
                 cost_score: Optional[int] = None, notes: Optional[str] = None) -> bool:
    """Add a delivery record."""
    suppliers = load_json(SUPPLIERS_FILE)
    
    if supplier not in suppliers.get("suppliers", {}):
        logger.error(f"Supplier {supplier} not found")
        return False
    
    deliveries = load_json(DELIVERIES_FILE)
    
    # Default cost score if not provided
    if cost_score is None:
        cost_score = 100 if on_time else 50
    
    delivery = {
        "supplier": supplier,
        "on_time": on_time,
        "quality_score": quality_score,
        "cost_score": cost_score,
        "date": datetime.now().isoformat(),
        "notes": notes
    }
    
    deliveries["deliveries"].append(delivery)
    
    # Recalculate score
    score = calculate_score(supplier)
    
    # Save scores
    scores = load_json(SCORES_FILE)
    scores["scores"][supplier] = score
    scores["last_updated"] = datetime.now().isoformat()
    
    save_json(DELIVERIES_FILE, deliveries)
    save_json(SCORES_FILE, scores)
    
    logger.info(f"Added delivery for {supplier}, new score: {score['score']}")
    return True


def get_all_scores() -> dict:
    """Get scores for all suppliers."""
    suppliers = load_json(SUPPLIERS_FILE)
    scores = {}
    
    for name in suppliers.get("suppliers", {}):
        try:
            scores[name] = calculate_score(name)
        except Exception as e:
            logger.error(f"Error calculating score for {name}: {e}")
    
    return scores


def list_suppliers() -> List[dict]:
    """List all suppliers."""
    suppliers = load_json(SUPPLIERS_FILE)
    result = []
    
    for name, data in suppliers.get("suppliers", {}).items():
        result.append({
            "name": name,
            "category": data.get("category", "unknown"),
            "active": data.get("active", True),
            "contact": data.get("contact", "N/A")
        })
    
    return result


def generate_report() -> dict:
    """Generate full supplier scorecard report."""
    scores = get_all_scores()
    suppliers = load_json(SUPPLIERS_FILE)
    deliveries = load_json(DELIVERIES_FILE)
    
    # Sort by score
    sorted_scores = sorted(scores.values(), key=lambda x: x.get("score", 0), reverse=True)
    
    report = {
        "generated": datetime.now().isoformat(),
        "total_suppliers": len(scores),
        "total_deliveries": len(deliveries.get("deliveries", [])),
        "scores": sorted_scores,
        "summary": {
            "avg_score": round(sum(s.get("score", 0) for s in scores.values()) / len(scores), 1) if scores else 0,
            "grade_a": sum(1 for s in scores.values() if s.get("grade") == "A"),
            "grade_b": sum(1 for s in scores.values() if s.get("grade") == "B"),
            "grade_c": sum(1 for s in scores.values() if s.get("grade") == "C"),
            "grade_d": sum(1 for s in scores.values() if s.get("grade") == "D"),
            "grade_f": sum(1 for s in scores.values() if s.get("grade") == "F"),
        }
    }
    
    return report


def display_score(score: dict):
    """Display a score nicely."""
    grade_emoji = {"A": "🏆", "B": "🥈", "C": "🥉", "D": "⚠️", "F": "❌", "N/A": "❓"}
    emoji = grade_emoji.get(score.get("grade", "N/A"), "❓")
    
    print("\n" + "=" * 60)
    print(f"{emoji} SUPPLIER SCORECARD: {score['supplier']}")
    print("=" * 60)
    print(f"  Score:       {score.get('score', 'N/A')}/100 ({score.get('grade', 'N/A')})")
    print(f"  Deliveries:  {score.get('total_deliveries', 0)}")
    
    if score.get('total_deliveries', 0) > 0:
        print(f"  On-Time:     {score.get('on_time_rate', 0)}% ({score.get('on_time_deliveries', 0)}/{score.get('total_deliveries', 0)})")
        print(f"  Quality:     {score.get('quality_score', 0)}/100")
        print(f"  Cost:       {score.get('cost_score', 0)}/100")
    else:
        print(f"  {score.get('message', 'No data')}")
    print("=" * 60)


def display_report(report: dict):
    """Display the full report."""
    print("\n" + "=" * 70)
    print("📊 SUPPLIER SCORECARD REPORT")
    print("=" * 70)
    print(f"Generated: {report['generated']}")
    print(f"Total Suppliers: {report['total_suppliers']}")
    print(f"Total Deliveries: {report['total_deliveries']}")
    print(f"Average Score: {report['summary']['avg_score']}")
    print()
    
    print("Grade Distribution:")
    print(f"  🏆 A (90+): {report['summary']['grade_a']} suppliers")
    print(f"  🥈 B (80-89): {report['summary']['grade_b']} suppliers")
    print(f"  🥉 C (70-79): {report['summary']['grade_c']} suppliers")
    print(f"  ⚠️ D (60-69): {report['summary']['grade_d']} suppliers")
    print(f"  ❌ F (<60): {report['summary']['grade_f']} suppliers")
    
    print()
    print("-" * 70)
    print("SUPPLIER RANKINGS:")
    print("-" * 70)
    
    for i, score in enumerate(report['scores'], 1):
        grade_emoji = {"A": "🏆", "B": "🥈", "C": "🥉", "D": "⚠️", "F": "❌", "N/A": "❓"}
        emoji = grade_emoji.get(score.get("grade", "N/A"), "❓")
        print(f"{i}. {emoji} {score['supplier']}: {score.get('score', 0)}/100 ({score.get('grade', 'N/A')}) | "
              f"Deliveries: {score.get('total_deliveries', 0)} | "
              f"On-Time: {score.get('on_time_rate', 0)}%")
    
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Supplier Scorecard Agent - Track and score supplier performance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --score --supplier "Acme Corp"
  %(prog)s --add-delivery --supplier "Acme Corp" --on-time 1 --quality 95
  %(prog)s --add-delivery --supplier "Acme Corp" --on-time 0 --quality 70
  %(prog)s --list-suppliers
  %(prog)s --report
  %(prog)s --init
        """
    )
    
    parser.add_argument("--score", action="store_true", help="Get score for a supplier")
    parser.add_argument("--supplier", type=str, help="Supplier name")
    parser.add_argument("--add-delivery", action="store_true", help="Add a delivery record")
    parser.add_argument("--on-time", type=int, choices=[0, 1], help="Was delivery on time? (0=no, 1=yes)")
    parser.add_argument("--quality", type=int, help="Quality score (0-100)")
    parser.add_argument("--cost-score", type=int, help="Cost score (0-100, default based on on_time)")
    parser.add_argument("--notes", type=str, help="Optional notes about delivery")
    parser.add_argument("--list-suppliers", action="store_true", help="List all suppliers")
    parser.add_argument("--report", action="store_true", help="Generate full report")
    parser.add_argument("--init", action="store_true", help="Initialize sample data")
    
    args = parser.parse_args()
    
    try:
        initialize_data()
        
        if args.init:
            print("✅ Sample data initialized")
            return
        
        if args.list_suppliers:
            suppliers = list_suppliers()
            print("\n🏭 SUPPLIERS:")
            print("-" * 60)
            for s in suppliers:
                status = "✅" if s["active"] else "❌"
                print(f"  {status} {s['name']} | Category: {s['category']} | Contact: {s['contact']}")
            print("-" * 60)
            return
        
        if args.score:
            if not args.supplier:
                parser.error("--score requires --supplier")
            score = calculate_score(args.supplier)
            display_score(score)
            return
        
        if args.add_delivery:
            if not args.supplier or args.on_time is None or args.quality is None:
                parser.error("--add-delivery requires --supplier, --on-time, and --quality")
            if add_delivery(args.supplier, args.on_time, args.quality, args.cost_score, args.notes):
                print(f"✅ Delivery recorded for {args.supplier}")
                score = calculate_score(args.supplier)
                display_score(score)
            else:
                print(f"❌ Failed to record delivery")
                sys.exit(1)
            return
        
        if args.report:
            report = generate_report()
            display_report(report)
            return
        
        parser.print_help()
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Error: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
