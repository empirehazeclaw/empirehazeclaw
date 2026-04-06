#!/usr/bin/env python3
"""
Ecommerce Product Researcher Agent - OpenClaw Ecommerce Division
Researches products: market analysis, competition, trends, profit potential
Persona: CEO-mode - find winning products fast, validate before building
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

AGENT_NAME = "ProductResearcher"
BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "product_research"
LOG_DIR = BASE_DIR / "logs"
RESEARCH_FILE = DATA_DIR / "research.json"
NICHES_FILE = DATA_DIR / "niches.json"
TRENDS_FILE = DATA_DIR / "trends.json"
COMPETITORS_FILE = DATA_DIR / "competitors.json"

def setup_logging(verbose: bool = False) -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"product_researcher_{datetime.now():%Y%m%d}.log"
    level = logging.DEBUG if verbose else logging.INFO
    logger = logging.getLogger(AGENT_NAME)
    logger.setLevel(level)
    if logger.handlers:
        logger.handlers.clear()
    fh = logging.FileHandler(log_file)
    fh.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh.setFormatter(fmt)
    ch.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

logger = setup_logging()

def load_json(path: Path, default: dict | list) -> dict | list:
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return default

def save_json(path: Path, data: dict | list) -> bool:
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except IOError as e:
        logger.error(f"Failed to save: {e}")
        return False

def init_data():
    if not RESEARCH_FILE.exists():
        save_json(RESEARCH_FILE, {"products": []})
    if not NICHES_FILE.exists():
        save_json(NICHES_FILE, {"niches": []})
    if not TRENDS_FILE.exists():
        save_json(TRENDS_FILE, {"trends": []})
    if not COMPETITORS_FILE.exists():
        save_json(COMPETITORS_FILE, {"competitors": []})
    logger.info("Product researcher initialized")

def calculate_validation_score(product: dict) -> float:
    score = 0
    signals = product.get("validation_signals", {})
    if signals.get("reddit"): score += 25
    if signals.get("trends"): score += 25
    if signals.get("competition"): score += 25
    if signals.get("outreach"): score += 25
    return min(score, 100)

def validate_product(product: dict) -> dict:
    score = calculate_validation_score(product)
    product["validation_score"] = score
    product["validation_status"] = "strong" if score >= 75 else "moderate" if score >= 50 else "weak"
    return product

def cmd_niche_add(args) -> int:
    data = load_json(NICHES_FILE, {"niches": []})
    niche = {
        "id": f"NICHE_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "name": args.name,
        "description": args.description or "",
        "keywords": [k.strip() for k in args.keywords.split(",")] if args.keywords else [],
        "competition_level": args.competition or "medium",
        "market_size": args.market_size or "unknown",
        "trending": args.trending,
        "seasonal": args.seasonal,
        "platforms": [p.strip() for p in args.platforms.split(",")] if args.platforms else ["amazon","etsy","shopify"],
        "added_at": datetime.now().isoformat(),
        "niche_score": 50
    }
    niche_score = 50
    if niche["competition_level"] == "low": niche_score += 30
    elif niche["competition_level"] == "high": niche_score -= 20
    niche_score += len(niche["keywords"]) * 5
    if niche["trending"]: niche_score += 15
    niche["niche_score"] = min(niche_score, 100)
    data["niches"].append(niche)
    save_json(NICHES_FILE, data)
    print(f"✅ Niche '{niche['name']}' added (Score: {niche['niche_score']}/100)")
    return 0

def cmd_niche_list(args) -> int:
    data = load_json(NICHES_FILE, {"niches": []})
    niches = data.get("niches", [])
    if not niches:
        print("📊 No niches tracked. Add: product-researcher niche add --name '...'")
        return 0
    print(f"\n📊 Tracked Niches ({len(niches)}):")
    for n in sorted(niches, key=lambda x: x.get("niche_score", 0), reverse=True):
        t = "📈" if n.get("trending") else "📉"
        s = "❄️" if n.get("seasonal") else "  "
        print(f"  {t}{s} [{n['id']}] {n['name']} - Score: {n.get('niche_score',0)}/100 | Competition: {n.get('competition_level')}")
    return 0

def cmd_product_add(args) -> int:
    data = load_json(RESEARCH_FILE, {"products": []})
    product = {
        "id": f"PROD_R_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "name": args.name,
        "description": args.description or "",
        "category": args.category or "general",
        "supplier_cost": args.cost,
        "selling_price": args.price,
        "marketplace": args.marketplace or "amazon",
        "niche": args.niche or "",
        "validation_signals": {
            "reddit": args.signal_reddit,
            "trends": args.signal_trends,
            "competition": args.signal_competition,
            "outreach": args.signal_outreach
        },
        "created_at": datetime.now().isoformat()
    }
    product = validate_product(product)
    data["products"].append(product)
    save_json(RESEARCH_FILE, data)
    score = product["validation_score"]
    status = "🟢 Strong" if score >= 75 else "🟡 Moderate" if score >= 50 else "🔴 Weak"
    profit = (product["selling_price"] - product["supplier_cost"]) / max(product["supplier_cost"], 0.01) * 100
    print(f"✅ Product '{product['name']}' added")
    print(f"   Validation: {status} ({score}/100)")
    print(f"   Est. Profit Margin: {profit:.1f}%")
    return 0

def cmd_product_list(args) -> int:
    data = load_json(RESEARCH_FILE, {"products": []})
    products = data.get("products", [])
    if args.status:
        products = [p for p in products if p.get("validation_status") == args.status]
    if args.niche:
        products = [p for p in products if args.niche.lower() in p.get("niche", "").lower()]
    if args.min_margin:
        products = [p for p in products if (
            (p.get("selling_price", 0) - p.get("supplier_cost", 0)) / max(p.get("supplier_cost", 1), 0.01) * 100 >= args.min_margin
        )]
    if not products:
        print("📦 No products match your filters")
        return 0
    print(f"\n📦 Products ({len(products)} results):")
    for p in sorted(products, key=lambda x: x.get("validation_score", 0), reverse=True):
        score = p.get("validation_score", 0)
        icon = "🟢" if score >= 75 else "🟡" if score >= 50 else "🔴"
        margin = (p.get("selling_price", 0) - p.get("supplier_cost", 0)) / max(p.get("supplier_cost", 1), 0.01) * 100
        print(f"  {icon} [{p['id']}] {p.get('name')}")
        print(f"     Validation: {score}/100 | Margin: {margin:.1f}% | Cost: ${p.get('supplier_cost',0):.2f} | Sell: ${p.get('selling_price',0):.2f}")
    return 0

def cmd_product_validate(args) -> int:
    data = load_json(RESEARCH_FILE, {"products": []})
    valid_signals = ["reddit", "trends", "competition", "outreach"]
    if args.signal not in valid_signals:
        print(f"❌ Invalid signal. Choose: {', '.join(valid_signals)}")
        return 1
    for p in data["products"]:
        if p["id"] == args.product_id:
            p["validation_signals"][args.signal] = True
            p = validate_product(p)
            save_json(RESEARCH_FILE, data)
            print(f"✅ {p['id']} - New score: {p['validation_score']}/100 ({p['validation_status']})")
            return 0
    print(f"❌ Product not found: {args.product_id}")
    return 1

def cmd_product_score(args) -> int:
    data = load_json(RESEARCH_FILE, {"products": []})
    products = data.get("products", [])
    if not products:
        print("📦 No products to score")
        return 0
    scored = []
    for p in products:
        margin = (p.get("selling_price", 0) - p.get("supplier_cost", 0)) / max(p.get("supplier_cost", 1), 0.01)
        profit_score = min(margin * 25, 50)
        val_score = p.get("validation_score", 0) * 0.5
        p["composite_score"] = round(profit_score + val_score, 1)
        scored.append(p)
    scored.sort(key=lambda x: x["composite_score"], reverse=True)
    print(f"\n🏆 Product Rankings:")
    print(f"  {'Rank':<5} {'Product':<30} {'Score':<10} {'Validation':<12} {'Margin'}")
    print("-" * 80)
    for i, p in enumerate(scored, 1):
        margin = (p.get("selling_price", 0) - p.get("supplier_cost", 0)) / max(p.get("supplier_cost", 1), 0.01) * 100
        print(f"  {i:<5} {p['name'][:28]:<30} {p['composite_score']:<10.1f} {p.get('validation_score',0):<12} {margin:.1f}%")
    save_json(RESEARCH_FILE, data)
    return 0

def cmd_trends(args) -> int:
    data = load_json(TRENDS_FILE, {"trends": []})
    if args.add:
        trend = {
            "id": f"TREND_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "name": args.add,
            "category": args.category or "general",
            "direction": args.direction or "up",
            "platforms": [p.strip() for p in args.platforms.split(",")] if args.platforms else ["amazon"],
            "added_at": datetime.now().isoformat()
        }
        data["trends"].append(trend)
        save_json(TRENDS_FILE, data)
        print(f"✅ Trend '{trend['name']}' added ({trend['direction']})")
        return 0
    if not data.get("trends"):
        print("📈 No trends. Add: product-researcher trends add <name>")
        return 0
    print(f"\n📈 Trends ({len(data['trends'])}):")
    for t in data["trends"]:
        icon = "📈" if t.get("direction") == "up" else "📉"
        print(f"  {icon} {t['name']} ({t.get('category')})")
    return 0

def cmd_competitor(args) -> int:
    data = load_json(COMPETITORS_FILE, {"competitors": []})
    if args.add:
        comp = {
            "id": f"COMP_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "name": args.add,
            "platform": args.platform or "amazon",
            "products": [p.strip() for p in args.products.split(",")] if args.products else [],
            "strength": args.strength or "medium",
            "website": args.website or "",
            "notes": args.notes or "",
            "added_at": datetime.now().isoformat()
        }
        data["competitors"].append(comp)
        save_json(COMPETITORS_FILE, data)
        print(f"✅ Competitor '{comp['name']}' added")
        return 0
    if not data.get("competitors"):
        print("🏢 No competitors tracked")
        return 0
    print(f"\n🏢 Competitors ({len(data['competitors'])}):")
    for c in data["competitors"]:
        print(f"  [{c['platform']}] {c['name']} - {c.get('strength')} strength")
    return 0

def cmd_report(args) -> int:
    research = load_json(RESEARCH_FILE, {"products": []})
    niches = load_json(NICHES_FILE, {"niches": []})
    trends = load_json(TRENDS_FILE, {"trends": []})
    competitors = load_json(COMPETITORS_FILE, {"competitors": []})
    products = research.get("products", [])
    strong = [p for p in products if p.get("validation_score", 0) >= 75]
    moderate = [p for p in products if 50 <= p.get("validation_score", 0) < 75]
    print(f"""
╔══════════════════════════════════════════════════════╗
║           📊 PRODUCT RESEARCH REPORT                 ║
║              {datetime.now().strftime('%Y-%m-%d %H:%M'):<36} ║
╚══════════════════════════════════════════════════════╝

📈 OVERVIEW
  Products Researched: {len(products)}
  Strong (75+):       {len(strong)} 🟢
  Moderate (50-74):   {len(moderate)} 🟡

📊 NICHES: {len(niches.get('niches', []))}
📈 TRENDS: {len(trends.get('trends', []))}
🏢 COMPETITORS: {len(competitors.get('competitors', []))}

🏆 TOP 5 PRODUCTS:
""")
    for i, p in enumerate(sorted(products, key=lambda x: x.get("validation_score", 0), reverse=True)[:5], 1):
        margin = (p.get("selling_price", 0) - p.get("supplier_cost", 0)) / max(p.get("supplier_cost", 1), 0.01) * 100
        print(f"  {i}. {p.get('name')} - Score: {p.get('validation_score')}/100 | Margin: {margin:.1f}%")
    print()
    return 0

def main():
    parser = argparse.ArgumentParser(description="🔍 Ecommerce Product Researcher")
    sub = parser.add_subparsers(dest="command", required=True)
    
    niche_p = sub.add_parser("niche", help="Manage niches")
    niche_sub = niche_p.add_subparsers(dest="action")
    na = niche_sub.add_parser("add", help="Add niche")
    na.add_argument("--name", required=True); na.add_argument("--description")
    na.add_argument("--keywords"); na.add_argument("--competition", choices=["low","medium","high"], default="medium")
    na.add_argument("--market-size"); na.add_argument("--trending", action="store_true")
    na.add_argument("--seasonal", action="store_true"); na.add_argument("--platforms")
    na.set_defaults(func=cmd_niche_add)
    niche_sub.add_parser("list", help="List niches").set_defaults(func=cmd_niche_list)
    
    prod_p = sub.add_parser("product", help="Research products")
    prod_sub = prod_p.add_subparsers(dest="action")
    pa = prod_sub.add_parser("add", help="Add product")
    pa.add_argument("--name", required=True); pa.add_argument("--description")
    pa.add_argument("--category"); pa.add_argument("--cost", type=float, required=True)
    pa.add_argument("--price", type=float, required=True)
    pa.add_argument("--marketplace", default="amazon"); pa.add_argument("--niche")
    pa.add_argument("--signal-reddit", action="store_true")
    pa.add_argument("--signal-trends", action="store_true")
    pa.add_argument("--signal-competition", action="store_true")
    pa.add_argument("--signal-outreach", action="store_true")
    pa.set_defaults(func=cmd_product_add)
    pl = prod_sub.add_parser("list", help="List products")
    pl.add_argument("--status", choices=["strong","moderate","weak"])
    pl.add_argument("--niche"); pl.add_argument("--min-margin", type=float)
    pl.set_defaults(func=cmd_product_list)
    pv = prod_sub.add_parser("validate", help="Add validation signal")
    pv.add_argument("--product-id", required=True); pv.add_argument("--signal", required=True, choices=["reddit","trends","competition","outreach"])
    pv.set_defaults(func=cmd_product_validate)
    prod_sub.add_parser("score", help="Rank products").set_defaults(func=cmd_product_score)
    
    t_p = sub.add_parser("trends", help="Track trends")
    t_p.add_argument("--add", help="Trend name"); t_p.add_argument("--category")
    t_p.add_argument("--direction", choices=["up","down"]); t_p.add_argument("--platforms")
    t_p.set_defaults(func=cmd_trends)
    
    c_p = sub.add_parser("competitor", help="Track competitors")
    c_p.add_argument("--add", help="Competitor name"); c_p.add_argument("--platform")
    c_p.add_argument("--products", help="Comma-separated products"); c_p.add_argument("--strength", choices=["low","medium","high"])
    c_p.add_argument("--website"); c_p.add_argument("--notes")
    c_p.set_defaults(func=cmd_competitor)
    
    sub.add_parser("report", help="Generate research report").set_defaults(func=cmd_report)
    
    args = parser.parse_args()
    init_data()
    try:
        return args.func(args)
    except Exception as e:
        logger.exception("Error")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
