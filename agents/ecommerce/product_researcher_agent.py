#!/usr/bin/env python3
"""
Product Researcher Agent - OpenClaw E-Commerce Suite
Researches products, niches, competition, and market demand.
Reads/Writes: /home/clawbot/.openclaw/workspace/data/products/research.json
"""

import argparse
import json
import logging
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "products"
DATA_FILE = DATA_DIR / "research.json"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "product_researcher.log"

LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ProductResearcher")


def load_research() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        initial = {"products": [], "niches": [], "last_updated": datetime.utcnow().isoformat()}
        save_research(initial)
        return initial
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        log.error(f"Failed to load research data: {e}")
        return {"products": [], "niches": [], "last_updated": datetime.utcnow().isoformat()}


def save_research(data: dict) -> None:
    data["last_updated"] = datetime.utcnow().isoformat()
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        log.error(f"Failed to save research data: {e}")


def generate_id(items: list) -> int:
    return max((i.get("id", 0) for i in items), default=0) + 1


def web_search(query: str, count: int = 5) -> list:
    """Simple web search using DuckDuckGo HTML."""
    url = f"https://duckduckgo.com/html/?q={urllib.request.quote(query)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        # Extract titles and snippets
        import re
        results = []
        items = re.findall(r'<a class="result__a"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>', html)
        snippets = re.findall(r'<a class="result__snippet"[^>]*>([^<]+)</a>', html)
        for i, (link, title) in enumerate(items[:count]):
            snippet = snippets[i] if i < len(snippets) else ""
            results.append({"title": title.strip(), "url": link, "snippet": snippet.strip()})
        return results
    except Exception as e:
        log.warning(f"Web search failed for '{query}': {e}")
        return []


def cmd_search(args) -> None:
    """Search for product/niche information."""
    print(f"🔍 Searching for: {args.query}\n")
    results = web_search(args.query, count=args.count)

    if not results:
        print("No results found. Try different keywords.")
        return

    print(f"📊 Search Results ({len(results)} found)\n{'─'*60}")
    for i, r in enumerate(results, 1):
        print(f"  {i}. {r['title']}")
        print(f"     {r['snippet'][:100]}...")
        print(f"     🔗 {r['url'][:80]}")
        print()
    return results


def cmd_add_product(args) -> None:
    """Add a product to research database."""
    data = load_research()
    product = {
        "id": generate_id(data["products"]),
        "name": args.name,
        "description": args.description or "",
        "niche": args.niche or "",
        "platform": args.platform or "",
        "estimated_price": args.price or 0,
        "demand_score": args.demand or 0,
        "competition_level": args.competition or "medium",
        "status": "researching",
        "sources": args.sources.split(",") if args.sources else [],
        "notes": args.notes or "",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "research_count": 0,
    }
    data["products"].append(product)
    save_research(data)
    log.info(f"Product added to research: {product['name']}")
    print(f"📦 Product #{product['id']} added: {product['name']}")
    if args.niche:
        print(f"   Niche: {args.niche} | Competition: {args.competition}")


def cmd_add_niche(args) -> None:
    """Add a niche to track."""
    data = load_research()
    niche = {
        "id": generate_id(data["niches"]),
        "name": args.name,
        "description": args.description or "",
        "market_size": args.market_size or "unknown",
        "growth_trend": args.growth or "stable",
        "top_platforms": args.platforms.split(",") if args.platforms else [],
        "key_products": [],
        "notes": args.notes or "",
        "created_at": datetime.utcnow().isoformat(),
    }
    data["niches"].append(niche)
    save_research(data)
    log.info(f"Niche added: {niche['name']}")
    print(f"🎯 Niche #{niche['id']} added: {niche['name']}")


def cmd_list_products(args) -> None:
    """List researched products."""
    data = load_research()
    products = data["products"]

    if args.niche:
        products = [p for p in products if p.get("niche", "").lower() == args.niche.lower()]
    if args.status:
        products = [p for p in products if p.get("status") == args.status]
    if args.min_demand:
        products = [p for p in products if p.get("demand_score", 0) >= args.min_demand]

    if not products:
        print("📦 No products found matching filters.")
        return

    products.sort(key=lambda p: p.get("demand_score", 0), reverse=True)
    print(f"\n📦 Products ({len(products)} found)\n{'─'*70}")
    for p in products:
        icon = {"researching": "🔍", "validated": "✅", "rejected": "❌", "launched": "🚀"}.get(p.get("status"), "📌")
        demand = p.get("demand_score", 0)
        demand_bar = "🔥" * (demand // 3) + "☆" * (3 - demand // 3) if demand else "—"
        print(f"  {icon} #{p['id']:3d} | {p['name'][:35]:<35} | {p.get('niche','?'):<20} | {demand_bar}")
        print(f"         Price: ${p.get('estimated_price', 0):.2f} | Competition: {p.get('competition_level','?')}")
    print()


def cmd_list_niches(args) -> None:
    """List tracked niches."""
    data = load_research()
    niches = data.get("niches", [])
    if not niches:
        print("🎯 No niches tracked yet.")
        return
    print(f"\n🎯 Tracked Niches ({len(niches)})\n{'─'*60}")
    for n in niches:
        growth_icon = {"growing": "📈", "stable": "➡️", "declining": "📉"}.get(n.get("growth_trend", "stable"), "➡️")
        print(f"  {growth_icon} #{n['id']:3d} | {n['name']} | {n.get('market_size','?')} | {n.get('growth_trend')}")
        if n.get("top_platforms"):
            print(f"         Platforms: {', '.join(n['top_platforms'])}")
    print()


def cmd_validate(args) -> None:
    """Validate a product idea with web research."""
    data = load_research()
    product = None
    for p in data["products"]:
        if p["id"] == args.product_id:
            product = p
            break

    if not product:
        print(f"❌ Product #{args.product_id} not found.")
        return

    print(f"🔍 Validating: {product['name']}\n")

    # Search for demand signals
    queries = [
        f"{product['name']} buy",
        f"{product['name']} review",
        f"{product.get('niche', '')} trends 2026",
    ]
    all_results = []
    for q in queries:
        print(f"  Searching: {q}")
        results = web_search(q, count=5)
        all_results.extend(results)
        import time
        time.sleep(0.5)

    product["research_count"] = product.get("research_count", 0) + 1
    product["last_research"] = datetime.utcnow().isoformat()
    product["research_summary"] = f"Found {len(all_results)} related results"
    product["updated_at"] = datetime.utcnow().isoformat()

    if len(all_results) >= 5:
        product["status"] = "validated"
        print(f"\n✅ Product #{product['id']} VALIDATED — strong market signals found!")
    elif len(all_results) >= 2:
        product["status"] = "researching"
        print(f"\n🟡 Product #{product['id']} needs more research — some signals found.")
    else:
        product["status"] = "rejected"
        print(f"\n❌ Product #{product['id']} REJECTED — insufficient market signals.")

    save_research(data)

    print(f"\n📊 Research Summary:")
    print(f"  Results found: {len(all_results)}")
    print(f"  Status: {product['status']}")


def cmd_delete(args) -> None:
    """Delete a product from research."""
    data = load_research()
    t = args.type
    original = len(data.get(t + "s" if t[-1] != "s" else t, []))
    items = data.get(t + "s" if t[-1] != "s" else t, [])
    items = [x for x in items if x.get("id") != args.item_id]
    if len(items) < original:
        data[t + "s" if t[-1] != "s" else t] = items
        save_research(data)
        print(f"🗑️  {t.capitalize()} #{args.item_id} deleted.")
    else:
        print(f"❌ {t.capitalize()} #{args.item_id} not found.")


def main():
    parser = argparse.ArgumentParser(
        prog="product-researcher",
        description="📦 Product Researcher Agent — research products, niches, and market demand",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  product-researcher search "print on demand mugs" --count 10
  product-researcher add-product "Custom Coffee Mug" --niche pod --price 24.99 --competition low
  product-researcher list-products --niche pod --min-demand 5
  product-researcher add-niche "AI tools" --growth growing --platforms Etsy,Shopify
  product-researcher list-niches
  product-researcher validate 3
  product-researcher delete product 5
        """,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search", help="Search for product/niche information online")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--count", type=int, default=5, help="Number of results")

    p_add_prod = sub.add_parser("add-product", help="Add a product to research database")
    p_add_prod.add_argument("name", help="Product name")
    p_add_prod.add_argument("-d", "--description", default="", help="Description")
    p_add_prod.add_argument("--niche", default="", help="Niche name")
    p_add_prod.add_argument("--platform", default="", help="Platform (Etsy, Shopify, etc.)")
    p_add_prod.add_argument("--price", type=float, help="Estimated price")
    p_add_prod.add_argument("--demand", type=int, default=5, help="Demand score 1-10")
    p_add_prod.add_argument("--competition", choices=["low", "medium", "high"], default="medium")
    p_add_prod.add_argument("--sources", default="", help="Comma-separated source URLs")
    p_add_prod.add_argument("--notes", default="", help="Notes")

    p_add_niche = sub.add_parser("add-niche", help="Add a niche to track")
    p_add_niche.add_argument("name", help="Niche name")
    p_add_niche.add_argument("-d", "--description", default="", help="Description")
    p_add_niche.add_argument("--market-size", dest="market_size", default="unknown", help="Market size estimate")
    p_add_niche.add_argument("--growth", choices=["growing", "stable", "declining"], default="stable")
    p_add_niche.add_argument("--platforms", default="", help="Comma-separated platforms")
    p_add_niche.add_argument("--notes", default="", help="Notes")

    p_list_prod = sub.add_parser("list-products", help="List researched products")
    p_list_prod.add_argument("--niche", help="Filter by niche")
    p_list_prod.add_argument("--status", choices=["researching", "validated", "rejected", "launched"])
    p_list_prod.add_argument("--min-demand", type=int, help="Minimum demand score")

    sub.add_parser("list-niches", help="List tracked niches")

    p_val = sub.add_parser("validate", help="Validate a product with web research")
    p_val.add_argument("product_id", type=int, help="Product ID to validate")

    p_del = sub.add_parser("delete", help="Delete a product or niche")
    p_del.add_argument("type", choices=["product", "niche"], help="Type to delete")
    p_del.add_argument("item_id", type=int, help="Item ID to delete")

    args = parser.parse_args()
    try:
        if args.command == "search":
            cmd_search(args)
        elif args.command == "add-product":
            cmd_add_product(args)
        elif args.command == "add-niche":
            cmd_add_niche(args)
        elif args.command == "list-products":
            cmd_list_products(args)
        elif args.command == "list-niches":
            cmd_list_niches(args)
        elif args.command == "validate":
            cmd_validate(args)
        elif args.command == "delete":
            cmd_delete(args)
    except Exception as e:
        log.error(f"Command '{args.command}' failed: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
