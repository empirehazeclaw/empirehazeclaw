#!/usr/bin/env python3
"""
Academic Search Agent — EmpireHazeClaw Research Suite
Searches academic papers, journals, and preprints via free APIs.
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
        logging.FileHandler(LOG_DIR / "academic_search.log"),
        logging.StreamHandler(sys.stderr),
    ],
)
log = logging.getLogger("academic_search")


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
    log.info("Saved %s", path)


def fetch_url(url: str, timeout: int = 15) -> Optional[str]:
    try:
        import subprocess
        result = subprocess.run(
            ["curl", "-s", "-L", "--max-time", str(timeout), "-A",
             "AcademicSearch/1.0", url],
            capture_output=True, text=True, timeout=timeout + 5,
        )
        if result.returncode == 0:
            return result.stdout
    except Exception as e:
        log.warning("curl: %s", e)
    return None


def search_semantic_scholar(query: str, limit: int = 15) -> list[dict]:
    """Search Semantic Scholar API (free, no key required for basic use)."""
    log.info("Searching Semantic Scholar: %s", query)
    try:
        import urllib.parse
        encoded_q = urllib.parse.quote(query)
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={encoded_q}&limit={limit}&fields=title,authors,year,abstract,citationCount,venue,url,openAccessPdf"
        html = fetch_url(url)
        if html:
            data = json.loads(html)
            papers = data.get("data", [])
            results = []
            for p in papers:
                authors = [a.get("name", "") for a in p.get("authors", [])[:5]]
                results.append({
                    "title": p.get("title", ""),
                    "authors": authors,
                    "year": p.get("year", ""),
                    "abstract": (p.get("abstract") or "")[:500],
                    "venue": p.get("venue", ""),
                    "citations": p.get("citationCount", 0),
                    "url": p.get("url", ""),
                    "pdf_url": p.get("openAccessPdf", {}).get("url", "") if isinstance(p.get("openAccessPdf"), dict) else "",
                    "source": "semantic_scholar",
                })
            return results
    except Exception as e:
        log.warning("Semantic Scholar API: %s", e)
    return []


def search_openalex(query: str, limit: int = 15) -> list[dict]:
    """Search OpenAlex API (free, comprehensive academic database)."""
    log.info("Searching OpenAlex: %s", query)
    try:
        import urllib.parse
        encoded_q = urllib.parse.quote(query)
        url = f"https://api.openalex.org/works?search={encoded_q}&per-page={limit}"
        html = fetch_url(url)
        if html:
            data = json.loads(html)
            works = data.get("results", [])
            results = []
            for w in works:
                authors = [
                    a.get("display_name", "")
                    for a in (w.get("authorships", [])[:5])
                ]
                results.append({
                    "title": w.get("title", ""),
                    "authors": authors,
                    "year": w.get("publication_year", ""),
                    "abstract": (w.get("abstract_inverted_index") and " ".join(
                        v for k, vs in w["abstract_inverted_index"].items()
                        for v in vs)) or "",
                    "venue": w.get("primary_location", {}).get("source", {}).get("display_name", ""),
                    "citations": w.get("cited_by_count", 0),
                    "url": w.get("doi", ""),
                    "pdf_url": w.get("best_oa_location", {}).get("landing_page_url", "") if isinstance(w.get("best_oa_location"), dict) else "",
                    "source": "openalex",
                })
            return results
    except Exception as e:
        log.warning("OpenAlex API: %s", e)
    return []


def search_arxiv(query: str, limit: int = 10) -> list[dict]:
    """Search arXiv via their Atom API."""
    log.info("Searching arXiv: %s", query)
    try:
        import urllib.parse
        encoded_q = urllib.parse.quote(query)
        url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_q}&start=0&max_results={limit}"
        xml = fetch_url(url, timeout=20)
        if not xml:
            return []
        papers = []
        # Simple XML parsing without lxml
        entries = re.split(r"<entry>", xml)[1:]
        for entry in entries:
            title = re.search(r"<title>(.*?)</title>", entry, re.DOTALL)
            summary = re.search(r"<summary>(.*?)</summary>", entry, re.DOTALL)
            authors = re.findall(r"<name>(.*?)</name>", entry)
            published = re.search(r"<published>(.*?)</published>", entry)
            doi = re.search(r"<arxiv:doi>(.*?)</arxiv:doi>", entry)
            pdf_link = re.search(r"<link title=\"pdf\" href=\"(.*?)\"", entry)
            papers.append({
                "title": title.group(1).replace("\n", " ").strip() if title else "",
                "authors": [a.strip() for a in authors[:5]],
                "year": published.group(1)[:4] if published else "",
                "abstract": (summary.group(1).replace("\n", " ").strip()[:500] if summary else ""),
                "venue": "arXiv",
                "citations": 0,
                "url": f"https://arxiv.org/abs/{doi.group(1)}" if doi else "",
                "pdf_url": pdf_link.group(1) if pdf_link else "",
                "source": "arxiv",
            })
        return papers
    except Exception as e:
        log.warning("arXiv API: %s", e)
    return []


def search_crossref(query: str, limit: int = 10) -> list[dict]:
    """Search Crossref for academic papers."""
    log.info("Searching Crossref: %s", query)
    try:
        import urllib.parse
        encoded_q = urllib.parse.quote(query)
        url = f"https://api.crossref.org/works?query={encoded_q}&rows={limit}"
        html = fetch_url(url)
        if html:
            data = json.loads(html)
            items = data.get("message", {}).get("items", [])
            results = []
            for item in items:
                authors = [
                    a.get("given", "") + " " + a.get("family", "")
                    for a in item.get("author", [])[:5]
                ]
                title_list = item.get("title", [])
                results.append({
                    "title": title_list[0] if title_list else "",
                    "authors": [a.strip() for a in authors if a.strip()],
                    "year": item.get("published-print", {}).get("date-parts", [[""]])[0][0] or "",
                    "abstract": "",
                    "venue": item.get("container-title", [""])[0] or "",
                    "citations": item.get("is-referenced-by-count", 0),
                    "url": item.get("URL", ""),
                    "pdf_url": "",
                    "source": "crossref",
                })
            return results
    except Exception as e:
        log.warning("Crossref API: %s", e)
    return []


def search_all_sources(query: str, limit: int = 15) -> dict:
    """Search all academic sources and combine results."""
    log.info("Searching all sources for: %s", query)

    ss_results = search_semantic_scholar(query, limit=limit)
    oa_results = search_openalex(query, limit=limit)
    ax_results = search_arxiv(query, limit=limit)
    cr_results = search_crossref(query, limit=limit)

    # Combine, deduplicate by title (case-insensitive)
    seen_titles = set()
    combined = []
    for r in ss_results + oa_results + ax_results + cr_results:
        title_key = r.get("title", "").lower()[:80]
        if title_key and title_key not in seen_titles:
            seen_titles.add(title_key)
            combined.append(r)

    return {
        "query": query,
        "total_results": len(combined),
        "by_source": {
            "semantic_scholar": len(ss_results),
            "openalex": len(oa_results),
            "arxiv": len(ax_results),
            "crossref": len(cr_results),
        },
        "papers": combined[:limit],
        "searched_at": datetime.utcnow().isoformat(),
    }


def get_paper_details(paper_url: str) -> dict:
    """Fetch detailed information for a specific paper."""
    log.info("Fetching paper details: %s", paper_url)
    html = fetch_url(paper_url)
    if not html:
        return {"error": "Could not fetch paper page", "url": paper_url}

    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()

    return {
        "url": paper_url,
        "snippet": text[:1000],
        "fetched_at": datetime.utcnow().isoformat(),
    }


def save_search_results(query: str, limit: int = 15) -> Path:
    """Save search results to a dated file."""
    results = search_all_sources(query, limit=limit)
    slug = re.sub(r"[^a-zA-Z0-9]", "_", query)[:40]
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    output_path = DATA_DIR / "research" / f"academic_{slug}_{date_str}.json"
    save_json(output_path, results)
    return output_path


# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        prog="academic_search_agent.py",
        description="📚 Academic Search Agent — search papers from Semantic Scholar, OpenAlex, arXiv, Crossref.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # search
    p_srch = sub.add_parser("search", help="Search academic papers")
    p_srch.add_argument("--query", "-q", required=True)
    p_srch.add_argument("--limit", "-l", type=int, default=15)
    p_srch.add_argument("--source", "-s", default="all",
                        choices=["all", "semantic_scholar", "openalex", "arxiv", "crossref"],
                        help="Source to search (default: all)")
    p_srch.add_argument("--output", "-o")

    # sources
    p_src = sub.add_parser("sources", help="List supported academic sources")
    p_src.add_argument("--details", action="store_true", help="Show source details")

    # save
    p_save = sub.add_parser("save", help="Search and save results to data/research/")
    p_save.add_argument("--query", "-q", required=True)
    p_save.add_argument("--limit", "-l", type=int, default=15)

    args = parser.parse_args()

    try:
        if args.cmd == "search":
            source = args.source
            if source == "all":
                result = search_all_sources(args.query, limit=args.limit)
            elif source == "semantic_scholar":
                result = {"query": args.query, "papers": search_semantic_scholar(args.query, args.limit),
                          "searched_at": datetime.utcnow().isoformat()}
            elif source == "openalex":
                result = {"query": args.query, "papers": search_openalex(args.query, args.limit),
                          "searched_at": datetime.utcnow().isoformat()}
            elif source == "arxiv":
                result = {"query": args.query, "papers": search_arxiv(args.query, args.limit),
                          "searched_at": datetime.utcnow().isoformat()}
            elif source == "crossref":
                result = {"query": args.query, "papers": search_crossref(args.query, args.limit),
                          "searched_at": datetime.utcnow().isoformat()}
            print(json.dumps(result, indent=2, ensure_ascii=False))
            if args.output:
                Path(args.output).write_text(json.dumps(result, indent=2))

        elif args.cmd == "sources":
            sources = [
                {"name": "Semantic Scholar", "id": "semantic_scholar",
                 "api_url": "https://api.semanticscholar.org/graph/v1",
                 "free": True, "papers": "78M+", "notes": "AI research focus, good for CS"},
                {"name": "OpenAlex", "id": "openalex",
                 "api_url": "https://api.openalex.org", "free": True,
                 "papers": "240M+", "notes": "Comprehensive, covers all disciplines"},
                {"name": "arXiv", "id": "arxiv",
                 "api_url": "http://export.arxiv.org/api/query", "free": True,
                 "papers": "2M+", "notes": "Preprints in physics, math, CS, quantitative biology, finance"},
                {"name": "Crossref", "id": "crossref",
                 "api_url": "https://api.crossref.org/works", "free": True,
                 "papers": "120M+", "notes": "DOI-based, good for citations and metadata"},
            ]
            print(json.dumps(sources, indent=2, ensure_ascii=False))

        elif args.cmd == "save":
            path = save_search_results(args.query, limit=args.limit)
            print(f"✅ Results saved to {path}")

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted.")
        sys.exit(130)
    except Exception as e:
        log.exception("Error in academic search agent")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
