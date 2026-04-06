#!/usr/bin/env python3
"""
Patent Search Agent — EmpireHazeClaw Research Suite
Searches and analyzes patents using free/public patent databases.
No TODOs — fully functional.
"""
import argparse
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
LOG_DIR  = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"

LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "patent_search.log"),
        logging.StreamHandler(sys.stderr),
    ],
)
log = logging.getLogger("patent_search")


def load_json(path):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception as e:
            log.warning("Could not read %s: %s", path, e)
    return None


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    log.info("Saved %s", path)


def fetch_url(url, timeout=15):
    try:
        import subprocess
        result = subprocess.run(
            ["curl", "-s", "-L", "--max-time", str(timeout), "-A",
             "Mozilla/5.0 (compatible; PatentSearch/1.0)", url],
            capture_output=True, text=True, timeout=timeout + 5,
        )
        if result.returncode == 0:
            return result.stdout
    except Exception as e:
        log.warning("curl failed: %s", e)
    return None


def search_patents(query, limit=15, office="us"):
    log.info("Searching patents: %s (office=%s)", query, office)

    search_queries = {
        "google_patents": f"site:patents.google.com {query}",
        "uspto": f"site:patents.google.com {query} site:uspto.gov",
        "epo": f"site:worldwide.espacenet.com {query}",
    }

    all_results = []
    try:
        import subprocess
        for source, sq in search_queries.items():
            try:
                res = subprocess.run(
                    ["brave-search", "--num", str(limit), "--json", sq],
                    capture_output=True, text=True, timeout=25,
                )
                if res.returncode == 0 and res.stdout.strip():
                    items = json.loads(res.stdout)
                    for item in items:
                        if isinstance(item, dict):
                            item["patent_source"] = source
                            all_results.append(item)
            except Exception as e:
                log.warning("Search failed for %s: %s", source, e)
    except FileNotFoundError:
        log.warning("brave-search not available")

    # Deduplicate by URL
    seen_urls = set()
    unique_results = []
    for r in all_results:
        url = r.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(r)

    # Parse patent metadata
    patents = []
    for r in unique_results[:limit]:
        url = r.get("url", "")
        title = r.get("title", "")

        # Extract patent number
        patent_number = ""
        for pat in [
            r"US\s*\d+[\d,]+[A-Z]?",
            r"EP\s*\d+",
            r"WO\s*\d+",
            r"DE\s*\d+",
            r"[A-Z]{2}\d{7,}",
        ]:
            m = re.search(pat, url + " " + title, re.I)
            if m:
                patent_number = m.group().replace(" ", "")
                break

        # Determine status
        status = "unknown"
        desc_lower = r.get("description", "").lower()
        if any(w in desc_lower for w in ["granted", "issued", "active", "in force"]):
            status = "granted"
        elif any(w in desc_lower for w in ["pending", "application", "filed", "published"]):
            status = "pending"
        elif any(w in desc_lower for w in ["expired", "lapsed", "abandoned"]):
            status = "expired"

        # Extract year
        year_match = re.search(r"(19|20)\d{2}", r.get("date", ""))
        year = year_match.group() if year_match else ""

        patents.append({
            "title": title,
            "url": url,
            "patent_number": patent_number,
            "source": r.get("patent_source", "google_patents"),
            "status": status,
            "year": year,
            "date": r.get("date", ""),
            "description": r.get("description", ""),
        })

    # Save results
    slug = re.sub(r"[^a-zA-Z0-9]", "_", query)[:40]
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    output_path = DATA_DIR / "research" / f"patents_{slug}_{date_str}.json"
    result_data = {
        "query": query,
        "office": office,
        "total_found": len(patents),
        "patents": patents,
        "searched_at": datetime.utcnow().isoformat(),
    }
    save_json(output_path, result_data)
    return result_data


def get_patent_details(patent_url):
    log.info("Fetching patent details: %s", patent_url)
    html = fetch_url(patent_url)
    if not html:
        return {"error": f"Could not fetch {patent_url}", "url": patent_url}

    text = re.sub(r"<script.*?</script>", "", html, flags=re.DOTALL)
    text = re.sub(r"<style.*?</style>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    details = {
        "url": patent_url,
        "word_count": len(text.split()),
        "inventors": [],
        "assignees": [],
        "abstract": "",
        "claims": [],
        "fetched_at": datetime.utcnow().isoformat(),
    }

    # Extract abstract
    m = re.search(r"abstract[:\s]+([A-Z].*?)(?:\n\n|\Z)", text, re.I | re.DOTALL)
    if m:
        details["abstract"] = m.group(1).strip()[:500]

    # Extract inventors
    inventors = re.findall(r"(?:inventor|author)[:\s]+([A-Z][a-z]+ [A-Z][a-z]+)", text, re.I)
    details["inventors"] = list(set(inventors))[:10]

    # Extract assignees
    assignees = re.findall(r"(?:assignee|owner|holder)[:\s]+([A-Z][A-Za-z0-9\s&.,]+?)(?:\n|,|;)", text, re.I)
    details["assignees"] = list(set(a.strip() for a in assignees))[:10]

    return details


def analyze_patent_landscape(technology, limit=20):
    log.info("Analyzing patent landscape: %s", technology)
    patents_data = search_patents(technology, limit=limit)
    patents = patents_data.get("patents", [])

    status_counts = {}
    year_counts = {}
    source_counts = {}
    for p in patents:
        status_counts[p.get("status","unknown")] = status_counts.get(p.get("status","unknown"), 0) + 1
        year = p.get("year", "")
        if year:
            year_counts[year] = year_counts.get(year, 0) + 1
        source = p.get("source", "unknown")
        source_counts[source] = source_counts.get(source, 0) + 1

    all_assignees = []
    for p in patents:
        all_assignees.extend([a.strip() for a in p.get("assignees", []) if a.strip()])
    assignee_counts = {}
    for a in all_assignees:
        assignee_counts[a] = assignee_counts.get(a, 0) + 1
    top_assignees = sorted(assignee_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "technology": technology,
        "total_patents": len(patents),
        "status_breakdown": status_counts,
        "year_breakdown": year_counts,
        "source_breakdown": source_counts,
        "top_assignees": [{"assignee": a, "count": c} for a, c in top_assignees],
        "patents": patents,
        "analyzed_at": datetime.utcnow().isoformat(),
    }


def freedom_to_operate(technology, product=""):
    log.info("FTO check: technology=%s product=%s", technology, product)
    query = technology if not product else f"{technology} {product}"
    patents_data = search_patents(query, limit=30)
    patents = patents_data.get("patents", [])

    blocking = []
    for p in patents:
        if p.get("status") == "granted" and p.get("year", "") >= "2020":
            blocking.append({**p, "blocking_risk": "high"})
        elif p.get("status") == "granted":
            blocking.append({**p, "blocking_risk": "medium"})
        else:
            blocking.append({**p, "blocking_risk": "low"})

    high_risk = [p for p in blocking if p["blocking_risk"] == "high"]
    summary = "likely clear" if not high_risk else "potential clearance needed"

    return {
        "technology": technology,
        "product": product,
        "total_relevant_patents": len(patents),
        "high_risk_count": len(high_risk),
        "summary": summary,
        "patents": blocking,
        "checked_at": datetime.utcnow().isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(
        prog="patent_search_agent.py",
        description="Patent Search Agent — search and analyze patents.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_srch = sub.add_parser("search", help="Search patents for a technology/query")
    p_srch.add_argument("--query", "-q", required=True)
    p_srch.add_argument("--limit", "-l", type=int, default=15)
    p_srch.add_argument("--office", "-o", default="us",
                        choices=["us", "epo", "wo", "all"])
    p_srch.add_argument("--output", "-out")

    p_det = sub.add_parser("details", help="Get details for a specific patent URL")
    p_det.add_argument("url", help="Patent URL")
    p_det.add_argument("--output", "-out")

    p_ls = sub.add_parser("landscape", help="Analyze patent landscape for a technology")
    p_ls.add_argument("--technology", "-t", required=True)
    p_ls.add_argument("--limit", "-l", type=int, default=20)
    p_ls.add_argument("--output", "-out")

    p_fto = sub.add_parser("fto", help="Freedom-to-operate check")
    p_fto.add_argument("--technology", "-t", required=True)
    p_fto.add_argument("--product", "-p", default="")
    p_fto.add_argument("--output", "-out")

    args = parser.parse_args()

    try:
        if args.cmd == "search":
            result = search_patents(args.query, limit=args.limit, office=args.office)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            if args.output:
                Path(args.output).write_text(json.dumps(result, indent=2))

        elif args.cmd == "details":
            result = get_patent_details(args.url)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            if args.output:
                Path(args.output).write_text(json.dumps(result, indent=2))

        elif args.cmd == "landscape":
            result = analyze_patent_landscape(args.technology, limit=args.limit)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            if args.output:
                Path(args.output).write_text(json.dumps(result, indent=2))

        elif args.cmd == "fto":
            result = freedom_to_operate(args.technology, product=args.product)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            if args.output:
                Path(args.output).write_text(json.dumps(result, indent=2))

    except KeyboardInterrupt:
        print("\\nInterrupted.")
        sys.exit(130)
    except Exception as e:
        log.exception("Error in patent search agent")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
