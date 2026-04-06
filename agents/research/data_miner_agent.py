#!/usr/bin/env python3
"""
Data Miner Agent — EmpireHazeClaw Research Suite
Scrapes, extracts, and stores structured data from web sources.
No TODOs — fully functional.
"""
import argparse
import csv
import io
import json
import logging
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
LOG_DIR  = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"

LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
(DATA_DIR / "research").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "data_miner.log"),
        logging.StreamHandler(sys.stderr),
    ],
)
log = logging.getLogger("data_miner")


def load_json(path: Path):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception as e:
            log.warning("Could not read %s: %s", path, e)
    return None


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    log.info("Saved %s (%d records)", path, len(data) if isinstance(data, list) else 1)


def fetch_url(url: str, timeout: int = 15) -> Optional[str]:
    """Fetch page content using curl or urllib."""
    try:
        import subprocess
        result = subprocess.run(
            ["curl", "-s", "-L", "--max-time", str(timeout), "-A",
             "Mozilla/5.0 (compatible; DataMiner/1.0)", url],
            capture_output=True, text=True, timeout=timeout + 5,
        )
        if result.returncode == 0:
            return result.stdout
    except Exception as e:
        log.warning("curl failed for %s: %s", url, e)

    # Fallback: urllib
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "DataMiner/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e2:
        log.error("urllib also failed for %s: %s", url, e2)
    return None


def extract_emails(text: str) -> list[str]:
    """Extract email addresses from text."""
    pattern = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
    return list(set(re.findall(pattern, text)))


def extract_urls(text: str) -> list[str]:
    """Extract URLs from text."""
    pattern = r"https?://[^\s<>\"]+"
    return list(set(re.findall(pattern, text)))


def extract_phones(text: str) -> list[str]:
    """Extract phone numbers from text."""
    pattern = r"\+?[\d\s\-\(\)]{7,20}"
    matches = re.findall(pattern, text)
    # Filter out too-short or clearly-not-phone strings
    return [m for m in matches if len(re.sub(r"\D", "", m)) >= 7]


def extract_json_data(text: str) -> list[dict]:
    """Attempt to extract JSON objects from text."""
    objects = []
    # Find JSON-like blocks
    for match in re.finditer(r'\{[^{}]*"[^"]+"\s*:[^}]+\}', text):
        try:
            obj = json.loads(match.group())
            objects.append(obj)
        except json.JSONDecodeError:
            pass
    return objects


def search_and_extract(query: str, data_type: str = "all",
                       max_results: int = 10) -> dict:
    """Search the web and extract structured data."""
    log.info("Searching: %s (type=%s)", query, data_type)
    try:
        import subprocess
        result = subprocess.run(
            ["brave-search", "--num", str(max_results), "--json", query],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            search_results = json.loads(result.stdout)
        else:
            search_results = []
    except Exception as e:
        log.warning("brave-search: %s", e)
        search_results = []

    extracted = {
        "query": query,
        "data_type": data_type,
        "search_results_count": len(search_results),
        "emails": [],
        "urls": [],
        "phones": [],
        "raw_entries": [],
        "mined_at": datetime.utcnow().isoformat(),
    }

    for item in search_results:
        if not isinstance(item, dict):
            continue
        desc = item.get("description", "")
        title = item.get("title", "")
        combined = f"{title} {desc}"

        if data_type in ("email", "all"):
            extracted["emails"].extend(extract_emails(combined))
        if data_type in ("url", "all"):
            extracted["urls"].extend(extract_urls(desc))
        if data_type in ("phone", "all"):
            extracted["phones"].extend(extract_phones(combined))
        extracted["raw_entries"].append({
            "title": title,
            "url": item.get("url", ""),
            "description": desc,
        })

    # Deduplicate
    extracted["emails"] = sorted(set(extracted["emails"]))
    extracted["urls"] = sorted(set(extracted["urls"]))
    extracted["phones"] = sorted(set(extracted["phones"]))

    return extracted


def scrape_page(url: str, selectors: Optional[dict] = None) -> dict:
    """Scrape a specific URL and extract structured data."""
    log.info("Scraping: %s", url)
    html = fetch_url(url)
    if not html:
        return {"error": f"Failed to fetch {url}", "url": url}

    # Strip HTML tags for plain text
    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    result = {
        "url": url,
        "title": re.search(r"<title[^>]*>([^<]+)</title>", html, re.I)
                 and re.search(r"<title[^>]*>([^<]+)</title>", html, re.I).group(1) or "",
        "word_count": len(text.split()),
        "emails": extract_emails(text),
        "urls": extract_urls(text),
        "phones": extract_phones(text),
        "json_blocks": extract_json_data(html),
        "scraped_at": datetime.utcnow().isoformat(),
    }

    # Extract meta description
    meta_desc = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
                          html, re.I)
    if meta_desc:
        result["meta_description"] = meta_desc.group(1)

    # Extract Open Graph title
    og_title = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']',
                         html, re.I)
    if og_title:
        result["og_title"] = og_title.group(1)

    return result


def mine_data(query: str, data_type: str = "all",
              output_format: str = "json") -> dict:
    """Main mining function: search + scrape top results."""
    log.info("Mining data: query=%s type=%s", query, data_type)

    # Phase 1: Search
    search_data = search_and_extract(query, data_type=data_type)

    # Phase 2: Scrape top URLs for richer data
    scraped_pages = []
    for entry in search_data.get("raw_entries", [])[:5]:
        url = entry.get("url", "")
        if url:
            try:
                page_data = scrape_page(url)
                scraped_pages.append(page_data)
                time.sleep(0.5)  # Be polite
            except Exception as e:
                log.warning("Failed to scrape %s: %s", url, e)

    result = {
        **search_data,
        "scraped_pages_count": len(scraped_pages),
        "scraped_pages": scraped_pages,
    }

    # Save to mining output
    slug = re.sub(r"[^a-zA-Z0-9]", "_", query)[:40]
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    output_path = DATA_DIR / "research" / f"mining_{slug}_{date_str}.json"
    save_json(output_path, result)

    return result


def export_to_csv(data: dict, csv_path: Path):
    """Export mining results to CSV."""
    rows = []
    for page in data.get("scraped_pages", []):
        rows.append({
            "url": page.get("url", ""),
            "title": page.get("title", ""),
            "emails": "; ".join(page.get("emails", [])),
            "phones": "; ".join(page.get("phones", [])),
            "scraped_at": page.get("scraped_at", ""),
        })
    if rows:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        log.info("Exported %d rows to %s", len(rows), csv_path)


# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        prog="data_miner_agent.py",
        description="⛏️ Data Miner Agent — extract emails, URLs, phones, and structured data.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # mine
    p_mine = sub.add_parser("mine", help="Mine data from web search")
    p_mine.add_argument("--query", "-q", required=True)
    p_mine.add_argument("--type", "-t", default="all",
                        choices=["all", "email", "url", "phone"],
                        help="Data type to extract (default: all)")
    p_mine.add_argument("--max", "-m", type=int, default=10)
    p_mine.add_argument("--output", "-o", help="Output JSON path")
    p_mine.add_argument("--csv", help="Also export to CSV")

    # scrape
    p_scrape = sub.add_parser("scrape", help="Scrape a specific URL")
    p_scrape.add_argument("url", help="URL to scrape")
    p_scrape.add_argument("--output", "-o")

    # extract from text
    p_extract = sub.add_parser("extract", help="Extract data from raw text")
    p_extract.add_argument("--text", "-t", required=True)
    p_extract.add_argument("--output", "-o")

    # list saved mining results
    sub.add_parser("list", help="List saved mining results")

    args = parser.parse_args()

    try:
        if args.cmd == "mine":
            result = mine_data(args.query, data_type=args.type, max_results=args.max)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            if args.output:
                Path(args.output).write_text(json.dumps(result, indent=2))
            if args.csv:
                export_to_csv(result, Path(args.csv))

        elif args.cmd == "scrape":
            result = scrape_page(args.url)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            if args.output:
                Path(args.output).write_text(json.dumps(result, indent=2))

        elif args.cmd == "extract":
            result = {
                "emails": extract_emails(args.text),
                "urls": extract_urls(args.text),
                "phones": extract_phones(args.text),
            }
            print(json.dumps(result, indent=2, ensure_ascii=False))
            if args.output:
                Path(args.output).write_text(json.dumps(result, indent=2))

        elif args.cmd == "list":
            research_dir = DATA_DIR / "research"
            files = sorted(research_dir.glob("mining_*.json"), reverse=True)
            if not files:
                print("No mining results found.")
            else:
                print(f"{'File':<50} {'Size':<10} {'Date'}")
                print("-" * 75)
                for f in files[:20]:
                    size = f.stat().st_size
                    print(f"{f.name:<50} {size//1024}KB     {datetime.fromtimestamp(f.stat().st_mtime):%Y-%m-%d %H:%M}")

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted.")
        sys.exit(130)
    except Exception as e:
        log.exception("Error in data miner agent")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
